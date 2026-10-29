#!/usr/bin/env python3
"""Write a CLI's behavior contract, or check a behavior results file, against the cli-behavior standard.

behavior.py contract create <tree.json> [--dry-run] [--idempotency-key <key>]
behavior.py result check <results.json>
"""
from collections import Counter
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve()
VOCAB = HERE.parents[3] / "resources" / "cli-naming.json"
STANDARD = HERE.parents[1] / "references" / "cli-behavior.json"
SCHEMA = HERE.parents[1] / "references" / "deviation.schema.json"
ENTRY_KINDS = ("command", "alias", "stub")
UNLISTED_KIND = "write"  # the strictest kind, for a verb the standard does not list
STATUS_FIELDS = {"pass": ("evidence",), "fail": ("evidence", "task", "fix", "test"),
                 "unknown": ("test",), "not_applicable": ("reason",), "deviation": ("evidence",)}
ENTRY_TEXT = ("command", "rule", "proposed_form", "task", "harm", "agent_cost")
TREE, REGISTER, CONTRACT = "cli-tree.json", "cli-behavior-deviations.json", "cli-contract.md"
USAGE = ("usage: behavior.py contract create <tree.json> [--dry-run] [--idempotency-key <key>]"
         " | behavior.py result check <results.json>")
KEY_LINE = re.compile(r"<!-- idempotency-key: (.*) tree-sha256: ([0-9a-f]{64}) -->\n\Z")


class Invalid(Exception):
    pass


class Conflict(Exception):
    pass


def need(ok, message):
    if not ok:
        raise Invalid(message)


def bundled(path):
    # A broken bundled file is a fault in the script, so it is not wrapped as Invalid.
    return json.loads(path.read_text(encoding="utf-8"))


def read_input(path, what):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError, RecursionError) as e:
        raise Invalid(f"cannot read {what} {path}: {e}")


def is_text(value):
    return isinstance(value, str) and bool(value.strip())


def is_words(value):
    return isinstance(value, list) and bool(value) and all(
        isinstance(w, str) and w.split() == [w] for w in value)


def load_tree(path):
    t = read_input(path, "tree")
    need(isinstance(t, dict), f"{path}: the tree must be a JSON object")
    need(is_text(t.get("cli")), f"{path}: cli must be a non-empty string")
    need(isinstance(t.get("commands"), list), f"{path}: commands must be a list")
    for i, c in enumerate(t["commands"]):
        where = f"{path}: commands[{i}]"
        need(isinstance(c, dict), f"{where} must be an object")
        need(c.get("kind") in ENTRY_KINDS, f"{where}.kind must be one of {', '.join(ENTRY_KINDS)}")
        need(c.get("path") is None or is_words(c["path"]),
             f"{where}.path must be null or a non-empty list of words")
    return t


def covered(tree, vocab):
    roots = set(vocab["root_commands"])
    return list(dict.fromkeys(" ".join(c["path"]) for c in tree["commands"]
                              if c["kind"] == "command" and c["path"] and c["path"][0] not in roots))


def base_verb(path, vocab):
    verb = path.split()[-1]
    return vocab["synonyms"].get(verb) or vocab["confirm_synonyms"].get(verb) or verb


def applies(applies_to, verb, kind):
    return applies_to == "all" or kind in applies_to.get("kinds", ()) or verb in applies_to.get("verbs", ())


def ticks(items):
    return ", ".join(f"`{x}`" for x in items)


def render_contract(tree, std, vocab):
    cli, idem = tree["cli"], std["idempotency"]
    commands = []
    for path in covered(tree, vocab):
        verb = base_verb(path, vocab)
        kind = std["kinds"].get(verb, UNLISTED_KIND)
        rules = [r for r in std["rules"] if applies(r["applies_to"], verb, kind)]
        flags = [f for r in rules for f in r.get("flags", [])]
        if any(r["id"] == "idempotent-write" for r in rules) and verb not in idem["end_state_verbs"]:
            flags.append(idem["flag"])
        codes = [c for c, e in std["error_codes"].items() if applies(e["applies_to"], verb, kind)]
        commands.append((path, kind, flags, rules, codes))

    paging = std["paging"]
    out = [f"# Behavior contract: {cli}", "",
           f"Written by `behavior.py contract create` from `{TREE}` and the cli-behavior standard, "
           f"version {std['version']}. Change the tree and run it again rather than editing this file.",
           "", "## Commands", ""]
    for path, kind, flags, rules, codes in commands:
        out += [f"### {path}", "", f"- Kind: {kind}", f"- Flags: {ticks(flags)}",
                f"- Rules: {ticks(r['id'] for r in rules)}", f"- Error codes: {ticks(codes)}", ""]
    used = {r["id"] for _, _, _, rules, _ in commands for r in rules}
    out += ["## Rules", ""] + [f"- `{r['id']}`: {r['form']}" for r in std["rules"] if r["id"] in used]
    out += ["", "## Envelope", "",
            "With `--json`, stdout holds exactly one JSON document; progress, logs and warnings go to stderr.",
            "",
            f"- Success: {ticks(std['envelope']['success'])}, with `\"ok\": true`.",
            f"- Failure: {ticks(std['envelope']['failure'])}, with `\"ok\": false`.",
            f"- A list's `data` is an array, and the envelope adds `page`: {ticks(paging['page'])}. "
            f"`--limit` defaults to {paging['limit']} and is at most {paging['max']}; "
            "`--cursor` takes the previous page's `next_cursor`.",
            "", "## Error object", "",
            f"- Fields: {ticks(std['error_object'])}.",
            "- `retryable` is fixed per code. Where the table says \"set by the command\", it is `true` only "
            "when repeating the command is safe: it is a read, its write gives the same end state when "
            f"repeated, or the caller supplied `{idem['flag']}`.",
            "- `next_action` names what the caller should do next and is never empty.",
            "", "## Error codes", "",
            "| Code | `retryable` | Exit status | When |", "|---|---|---|---|"]
    for code, e in std["error_codes"].items():
        retry = "set by the command" if e["retryable"] == "command" else f"`{json.dumps(e['retryable'])}`"
        out.append(f"| `{code}` | {retry} | {e['exit']} | {e['when']} |")
    out += ["", "## Examples", "", "Success:", "", "```json", json.dumps(std["example_success"], indent=2),
            "```", "", "Failure:", "", "```json", json.dumps(std["example_failure"], indent=2), "```",
            "", "## Tests", ""]
    for path, _, _, rules, _ in commands:
        out += [f"### {path}", ""]
        out += [f"- `{r['id']}`: {t.replace('<command>', f'{cli} {path}')}" for r in rules for t in r["tests"]]
        out.append("")
    return "\n".join(out)


def evidence_problem(item, root):
    m = re.fullmatch(r"(.+):([1-9][0-9]*)", item) if isinstance(item, str) else None
    if not m:
        return f"{item!r} is not path:line"
    rel, line = m.group(1), int(m.group(2))
    target = (root / rel).resolve()
    if Path(rel).is_absolute() or root not in target.parents:
        return f"{item!r} is not repository-relative"
    try:
        lines = len(target.read_bytes().splitlines())
    except OSError as e:
        return f"{item!r}: cannot read {rel}: {e.strerror}"
    return None if line <= lines else f"{item!r}: {rel} has {lines} lines"


def check_register(reg, schema, std, commands, rules):
    if not isinstance(reg, dict) or not isinstance(reg.get("deviations"), list):
        return [f"{REGISTER} must be an object with a deviations list"], set()
    problems = [f"{REGISTER} is missing {f}" for f in schema["required"] if f not in reg]
    if "standard_version" in reg and reg["standard_version"] != std["version"]:
        problems.append(f"{REGISTER}: standard_version must be {std['version']}")
    spec = schema["$defs"]["deviation"]
    props = spec["properties"]
    statuses, open_status = props["status"]["enum"], spec["if"]["properties"]["status"]["const"]
    accepted, seen = set(), set()
    for j, e in enumerate(reg["deviations"]):
        where = f"deviations[{j}]"
        if not isinstance(e, dict):
            problems.append(f"{where} must be an object")
            continue
        status = e.get("status")
        required = spec["required"] + (spec["else"]["required"] if status != open_status else [])
        problems += [f"{where} is missing {f}" for f in required if f not in e]
        problems += [f"{where}.{f} must be a non-empty string" for f in ENTRY_TEXT if f in e and not is_text(e[f])]
        if "status" in e and (not isinstance(status, str) or status not in statuses):
            problems.append(f"{where}.status {status!r} is not one of {', '.join(statuses)}")
        if "evidence" in e and not (isinstance(e["evidence"], list) and e["evidence"]
                                    and all(is_text(x) for x in e["evidence"])):
            problems.append(f"{where}.evidence must be a non-empty list of strings")
        if "work" in e and not (isinstance(e["work"], dict)
                                and all(is_text(e["work"].get(f)) for f in props["work"]["required"])):
            problems.append(f"{where}.work must hold {' and '.join(props['work']['required'])} as text")
        if "decided" in e:
            d = e["decided"]
            if not (isinstance(d, dict) and all(f in d for f in props["decided"]["required"])
                    and is_text(d.get("by")) and is_iso_date(d.get("on"))):
                problems.append(f"{where}.decided must be {{on: an ISO date, by: who decided}}")
        command, rule = e.get("command"), e.get("rule")
        if is_text(command) and command not in commands:
            problems.append(f"{where}.command {command!r} is not a covered command in the tree")
        if is_text(rule) and rule not in rules:
            problems.append(f"{where}.rule {rule!r} is not a rule in the standard")
        if not (is_text(command) and is_text(rule)):
            continue
        if (command, rule) in seen:
            problems.append(f"{where} repeats the entry for {command} {rule}")
        seen.add((command, rule))
        if status == "accepted":
            accepted.add((command, rule))
    return problems, accepted


def is_iso_date(value):
    try:
        datetime.date.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False


def check_results(path):
    std, vocab, schema = bundled(STANDARD), bundled(VOCAB), bundled(SCHEMA)
    path = Path(path)
    data = read_input(path, "results")
    need(isinstance(data, dict) and isinstance(data.get("results"), list),
         f"{path}: must be an object with a results list")
    need(type(data.get("standard_version")) is int and data["standard_version"] == std["version"],
         f"{path}: standard_version must be {std['version']}")
    tree = load_tree(path.parent / TREE)
    register_file = path.parent / REGISTER
    register = read_input(register_file, "register") if register_file.exists() else None
    root = path.resolve().parent.parent
    commands = covered(tree, vocab)
    rules = {r["id"]: r for r in std["rules"]}
    kind_names = set(std["kinds"].values())
    problems, accepted = (check_register(register, schema, std, commands, rules)
                          if register is not None else ([], set()))

    usable, read_kinds = [], {}
    for i, r in enumerate(data["results"]):
        where = f"results[{i}]"
        if not isinstance(r, dict):
            problems.append(f"{where} must be an object")
            continue
        cmds, rule, status = r.get("commands"), r.get("rule"), r.get("status")
        if not (isinstance(cmds, list) and cmds and all(isinstance(c, str) for c in cmds)):
            problems.append(f"{where}.commands must be a non-empty list of command paths")
            cmds = []
        problems += [f"{where}.commands: {c!r} is not a covered command in the tree"
                     for c in cmds if c not in commands]
        rule = rule if isinstance(rule, str) else repr(rule)
        status = status if isinstance(status, str) else repr(status)
        if rule not in rules:
            problems.append(f"{where}.rule {rule!r} is not a rule in the standard")
        if status not in STATUS_FIELDS:
            problems.append(f"{where}.status {status!r} is not one of {', '.join(STATUS_FIELDS)}")
        for f in STATUS_FIELDS.get(status, ()):
            if f not in r:
                problems.append(f"{where} ({rule}, {status}) is missing {f}")
            elif f != "evidence" and not is_text(r[f]):
                problems.append(f"{where}.{f} must be a non-empty string")
        if "evidence" in r:
            ev = r["evidence"]
            if not (isinstance(ev, list) and ev):
                problems.append(f"{where}.evidence must be a non-empty list of path:line strings")
            else:
                problems += [f"{where}.evidence {p}" for p in (evidence_problem(x, root) for x in ev) if p]
        if "command_kind" in r:
            if r["command_kind"] not in kind_names:
                problems.append(f"{where}.command_kind must be one of {', '.join(sorted(kind_names))}")
            elif "evidence" not in r:
                problems.append(f"{where} has command_kind but no evidence citing the handler")
            else:
                for c in cmds:
                    if read_kinds.setdefault(c, r["command_kind"]) != r["command_kind"]:
                        problems.append(f"{where}: {c} has two command_kind values")
        cmds = [c for c in cmds if c in commands]
        if status == "deviation":
            problems += [f"{where}: {c} {rule} is a deviation with no accepted entry in {REGISTER}"
                         for c in cmds if (c, rule) not in accepted]
        if rule in rules:
            usable.append((rules[rule], status, cmds))

    def kind_of(c):
        verb = base_verb(c, vocab)
        return std["kinds"].get(verb) or read_kinds.get(c) or UNLISTED_KIND

    for rule in rules.values():
        seen = {c for r, _, cmds in usable if r is rule for c in cmds}
        problems += [f"{rule['id']}: {c} has no result" for c in commands if c not in seen]
    for rule, status, cmds in usable:
        problems += [f"{rule['id']}: {c} is outside the rule's applies_to, so its only status is not_applicable"
                     for c in cmds if status != "not_applicable"
                     and not applies(rule["applies_to"], base_verb(c, vocab), kind_of(c))]
    if problems:
        return {"standard_version": std["version"], "problems": list(dict.fromkeys(problems))}

    order = {c: i for i, c in enumerate(commands)}
    rule_order = {r: i for i, r in enumerate(rules)}
    severity = {s: i for i, s in enumerate(std["severities"])}
    findings = [dict(r, severity=rules[r["rule"]]["severity"]) for r in data["results"] if r["status"] == "fail"]
    findings.sort(key=lambda f: (severity[f["severity"]], min(order[c] for c in f["commands"]),
                                 rule_order[f["rule"]]))
    counts = Counter(r["status"] for r in data["results"])
    return {"standard_version": std["version"], "counts": {s: counts[s] for s in STATUS_FIELDS},
            "findings": findings, "problems": []}


def create_contract(name, dry_run, key):
    text = render_contract(load_tree(name), bundled(STANDARD), bundled(VOCAB))
    out = Path(name).parent / CONTRACT
    if key is not None:
        # The key and the tree's hash are kept in the contract itself, so a repeat needs no other file.
        digest = hashlib.sha256(Path(name).read_bytes()).hexdigest()
        first = KEY_LINE.search(out.read_text(encoding="utf-8")) if out.exists() else None
        if first and json.loads(first.group(1)) == key:
            if first.group(2) != digest:
                raise Conflict(f"idempotency key {key!r} was used with a different {TREE}")
            return {"path": str(out)}
        text += f"\n<!-- idempotency-key: {json.dumps(key)} tree-sha256: {digest} -->\n"
    if dry_run:
        return {"path": str(out), "contract": text}
    out.write_text(text, encoding="utf-8")
    return {"path": str(out)}


def contract_args(args):
    """Return (tree, dry_run, key) for contract create's arguments, or None on a usage error."""
    names, dry_run, key = [], False, None
    rest = iter(args)
    for a in rest:
        if a == "--dry-run" and not dry_run:
            dry_run = True
        elif a == "--idempotency-key" and key is None:
            key = next(rest, "")
            if not key.strip() or key.startswith("-"):
                return None
        elif a.startswith("-"):
            return None
        else:
            names.append(a)
    return (names[0], dry_run, key) if len(names) == 1 else None


EXIT = {"INVALID_ARGUMENT": 2, "CONFLICT": 1, "INTERNAL": 1}


def fail(code, message, next_action):
    error = {"code": code, "message": message, "retryable": False, "next_action": next_action}
    sys.stdout.write(json.dumps({"schema_version": 1, "ok": False, "error": error}) + "\n")
    return EXIT[code]


def main(argv):
    try:
        data = None
        if argv[:2] == ["contract", "create"] and (parsed := contract_args(argv[2:])):
            data = create_contract(*parsed)
        elif argv[:2] == ["result", "check"] and len(argv) == 3 and not argv[2].startswith("-"):
            data = check_results(argv[2])
        if data is None:
            return fail("INVALID_ARGUMENT", USAGE, "run behavior.py with one of the two usage forms")
        sys.stdout.write(json.dumps({"schema_version": 1, "ok": True, "data": data}, indent=2) + "\n")
        sys.stdout.flush()
    except Invalid as e:
        return fail("INVALID_ARGUMENT", str(e), "fix the problems in the named file and run the command again")
    except Conflict as e:
        return fail("CONFLICT", str(e), "run it again with a new --idempotency-key")
    except Exception as e:
        try:
            code = fail("INTERNAL", f"{type(e).__name__}: {e}", "report this error; do not retry")
            sys.stdout.flush()
            return code
        except OSError:
            # A dead stdout would fail again in the shutdown flush and print "Exception ignored".
            os.dup2(os.open(os.devnull, os.O_WRONLY), 1)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
