#!/usr/bin/env python3
"""Check a CLI command tree against the noun-verb naming standard: tree.py check <tree.json>."""
import json
import os
from pathlib import Path
import sys

VOCAB = Path(__file__).resolve().parent.parent / "references" / "cli-naming.json"
KINDS = ("command", "alias", "stub")
VIOLATIONS = {"synonym", "verb-first", "underscore-in-noun", "long-form", "noun-is-verb",
              "depth", "mixed-shape", "collision"}
RULES = {
    "synonym": "approved-verbs", "unlisted-verb": "approved-verbs",
    "confirm-synonym": "confirm-only-synonyms", "plural": "noun-singular",
    "long-form": "noun-full-word", "underscore-in-noun": "noun-hyphenated",
    "noun-is-verb": "noun-not-verb", "mixed-shape": "tree-noun-verb", "depth": "tree-depth",
    "verb-first": "mcp-noun-verb", "verb-not-last": "mcp-noun-verb", "ambiguous": "mcp-noun-verb",
    "no-noun": "mcp-noun-verb", "collision": "collisions", "incomplete-tree": "complete-tree",
}


class InvalidTree(Exception):
    pass


def need(ok, message):
    if not ok:
        raise InvalidTree(message)


def is_words(value):
    return isinstance(value, list) and all(isinstance(w, str) and w.split() == [w] for w in value)


def load_tree(name):
    try:
        t = json.loads(Path(name).read_text(encoding="utf-8"))
    except (OSError, ValueError, RecursionError) as e:
        raise InvalidTree(f"cannot read {name}: {e}")
    need(isinstance(t, dict), "the tree must be a JSON object")
    need(isinstance(t.get("cli"), str), "cli must be a string")
    sources = t.get("sources")
    need(isinstance(sources, list) and all(
        isinstance(s, dict) and s.get("kind") in ("catalog", "source") and isinstance(s.get("ref"), str)
        for s in sources), "sources must be a list of {kind: catalog|source, ref: string}")
    need(isinstance(t.get("complete"), bool), "complete must be a boolean")
    need(isinstance(t.get("commands"), list), "commands must be a list")
    need(is_words(t.get("local_verbs", [])), "local_verbs must be a list of words")
    refs = {s["ref"] for s in sources}
    for i, c in enumerate(t["commands"]):
        where = f"commands[{i}]"
        need(isinstance(c, dict), f"{where} must be an object")
        for key in ("path", "mcp_name", "kind", "source"):
            need(key in c, f"{where} is missing {key}")
        need(c["path"] is None or (is_words(c["path"]) and c["path"]),
             f"{where}.path must be null or a non-empty list of words")
        m = c["mcp_name"]
        need(m is None or (isinstance(m, str) and all(m.split("_"))),
             f"{where}.mcp_name must be null or words joined by single underscores")
        need(c["path"] is not None or m is not None, f"{where} needs a path or an mcp_name")
        need(c["kind"] in KINDS, f"{where}.kind must be one of {', '.join(KINDS)}")
        need(isinstance(c["source"], str) and c["source"] in refs,
             f"{where}.source must be one of the sources[].ref values")
        if c["kind"] != "command":
            need(is_words(c.get("renamed_to")) and c["renamed_to"],
                 f"{where} of kind {c['kind']} needs a non-empty renamed_to list")
    return t


def check(t, v):
    verbs, syn, confirm = set(v["verbs"]), v["synonyms"], v["confirm_synonyms"]
    long_to_short = {full: short for short, full in v["short_forms"].items()}
    exceptions, roots = set(v["plural_exceptions"]), set(v["root_commands"])
    local = set(t.get("local_verbs", []))
    findings, proposals, leaves = [], [], []

    def add(code, path, message, source, suggest=None, owner=None):
        f = {"code": code, "severity": "violation" if code in VIOLATIONS else "advisory",
             "path": path, "message": message, "suggest": suggest, "rule": RULES[code],
             "source": source}
        findings.append(f)
        if suggest is not None:
            proposals.append((f, owner))

    def verb_fix(verb):
        if verb in verbs or verb in local:
            return None, verb
        if verb in syn:
            return "synonym", syn[verb]
        if verb in confirm:
            return "confirm-synonym", verb
        return "unlisted-verb", verb

    def verb_note(code, verb):
        if code == "confirm-synonym":
            return f"{verb} may mean {confirm[verb]}; the owner decides"
        return f"{verb} is not an approved verb"

    def is_verb(word):
        return word in verbs or word in local or word in syn or word in confirm

    for i, c in enumerate(t["commands"]):
        if c["kind"] != "command":
            continue
        src, p, m = c["source"], c["path"], c["mcp_name"]
        if p and p[0] not in roots:
            name = " ".join(p)
            if len(p) > 2:
                add("depth", name, "paths deeper than noun verb are not allowed", src)
            else:
                leaves.append((name, len(p), src))
                verb = p[-1]
                code, new_verb = verb_fix(verb)
                renames = []
                if code == "synonym":
                    renames.append(("synonym", f"{verb} is a synonym of {new_verb}"))
                elif code:
                    add(code, name, verb_note(code, verb), src)
                words = [new_verb]
                if len(p) == 2:
                    noun = p[0].replace("_", "-")
                    if noun != p[0]:
                        renames.append(("underscore-in-noun", "multi-word nouns are hyphenated"))
                    if noun.endswith("s") and noun not in exceptions:
                        add("plural", name, f"{noun} looks plural; nouns are singular", src)
                    if noun in verbs:
                        add("noun-is-verb", name, f"{noun} is an approved verb, not a noun", src)
                    if noun in long_to_short:
                        noun = long_to_short[noun]
                        renames.append(("long-form", f"use the short form {noun}"))
                    words.insert(0, noun)
                for code, message in renames:
                    add(code, name, message, src, " ".join(words), i)
        if m is not None:
            w = m.split("_")
            if len(w) == 1:
                add("no-noun", m, "MCP names are noun_verb", src)
            elif any(is_verb(x) for x in w[1:-1]):
                add("verb-not-last", m, "a middle word is a verb", src)
            elif is_verb(w[-1]) and not is_verb(w[0]):
                code, new_verb = verb_fix(w[-1])
                if code == "synonym":
                    add(code, m, f"{w[-1]} is a synonym of {new_verb}", src,
                        "_".join(w[:-1] + [new_verb]), i)
                elif code:
                    add(code, m, verb_note(code, w[-1]), src)
            elif is_verb(w[0]) and not is_verb(w[-1]):
                code, new_verb = verb_fix(w[0])
                noun = w[1:]
                if noun[-1].endswith("s") and noun[-1] not in exceptions:
                    noun[-1] = noun[-1][:-1]
                suggest = "_".join(noun + [new_verb])
                if code == "confirm-synonym":
                    add(code, m, verb_note(code, w[0]), src)
                    suggest = None
                add("verb-first", m, "MCP names put the noun first", src, suggest, i)
            else:
                add("ambiguous", m, "cannot tell the noun from the verb", src)

    if {n for _, n, _ in leaves} == {1, 2}:
        for name, n, src in leaves:
            if n == 1:
                add("mixed-shape", name, "flat leaf in a CLI that also has noun verb leaves", src)

    holders = {}
    for i, c in enumerate(t["commands"]):
        for name in filter(None, (" ".join(c["path"] or []), c["mcp_name"])):
            holders.setdefault(name, set()).add(i)
    by_target = {}
    for f, i in proposals:
        by_target.setdefault(f["suggest"], []).append((f, i))
    for target, props in by_target.items():
        if len(holders.get(target, set()) | {i for _, i in props}) > 1:
            for f, _ in props:
                f["suggest"] = None
            dropped = ", ".join(dict.fromkeys(f["path"] for f, _ in props))
            taken = ", which is already a command" if target in holders else ""
            add("collision", target, f"{dropped} would be renamed to {target}{taken}", None)

    if not t["complete"]:
        refs = ", ".join(s["ref"] for s in t["sources"])
        add("incomplete-tree", "", f"the tree may miss commands; sources read: {refs}", None)

    findings.sort(key=lambda f: (f["path"], f["code"]))
    return {"schema_version": 1, "ok": not any(f["code"] in VIOLATIONS for f in findings),
            "standard_version": v["version"], "data": findings}


def fail(code, message):
    print(json.dumps({"ok": False, "error": {"code": code, "message": message}}), file=sys.stderr)
    return 2


def main(argv):
    try:
        if len(argv) != 2 or argv[0] != "check":
            return fail("usage", "usage: tree.py check <tree.json>")
        t = load_tree(argv[1])
        env = check(t, json.loads(VOCAB.read_text(encoding="utf-8")))
        sys.stdout.write(json.dumps(env, indent=2) + "\n")
        sys.stdout.flush()
    except InvalidTree as e:
        return fail("invalid-tree", str(e))
    except Exception as e:
        # A dead stdout would fail again in the shutdown flush and print "Exception ignored".
        os.dup2(os.open(os.devnull, os.O_WRONLY), 1)
        return fail("internal-error", f"{type(e).__name__}: {e}")
    return 0 if env["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
