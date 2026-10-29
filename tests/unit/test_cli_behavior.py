"""Checks on the CLI behavior standard, its deviation schema and `behavior.py`."""

from collections import Counter
import copy
from functools import cache
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

from helpers import ROOT, frontmatter

SKILL = ROOT / "skills/cli-behavior"
STANDARD = SKILL / "references/cli-behavior.json"
SCHEMA = SKILL / "references/deviation.schema.json"
RULES_MD = SKILL / "references/cli-behavior.md"
SCRIPT = SKILL / "scripts/behavior.py"
TREE_SCRIPT = ROOT / "skills/menu-design/scripts/tree.py"
VOCAB = ROOT / "resources/cli-naming.json"
EVALS = ROOT / "evals/cli-behavior"
STATUSES = ("pass", "fail", "unknown", "not_applicable", "deviation")
# The scripts exit as the standard's code table says.
EXIT = {c: e["exit"] for c, e in json.loads(STANDARD.read_text(encoding="utf-8"))["error_codes"].items()}

# design.md "The standard": the tables this file must hold, in order.
KINDS = {"list": "read", "get": "read", "search": "read", "check": "read",
         "create": "write", "update": "write", "delete": "write", "sync": "write",
         "import": "write", "export": "write", "run": "write", "stop": "write",
         "start": "long-running"}
RULES = {
    "json-flag": ("all", "misread"),
    "envelope": ("all", "misread"),
    "stdout-data-only": ("all", "misread"),
    "error-object": ("all", "misread"),
    "exit-status": ("all", "misread"),
    "no-prompt": ("all", "hang"),
    "confirm-flag": ({"verbs": ["delete"]}, "hang"),
    "paged-list": ({"verbs": ["list", "search"]}, "data"),
    "dry-run": ({"kinds": ["write"]}, "data"),
    "idempotent-write": ({"kinds": ["write"]}, "data"),
    "operation-handle": ({"kinds": ["long-running"]}, "data"),
    "secret-input": ("all", "data"),
}
CODES = {
    "INVALID_ARGUMENT": (False, 2), "CONFIRMATION_REQUIRED": (False, 2), "NOT_FOUND": (False, 1),
    "CONFLICT": ("command", 1), "UNAUTHENTICATED": (False, 1), "PERMISSION_DENIED": (False, 1),
    "RATE_LIMITED": (True, 1), "UNAVAILABLE": ("command", 1), "TIMEOUT": ("command", 1),
    "INTERNAL": (False, 1),
}
NO_PROMPT_TEST = ("run `<command>` with stdin closed and a required argument missing: "
                  "it exits 2 with `INVALID_ARGUMENT` and does not wait")
PAGED_TEST = ("read 250 records with `<command> --limit 20`: every record appears once, "
              "and the last page has `has_more: false`")


@cache
def std():
    return json.loads(STANDARD.read_text(encoding="utf-8"))


@cache
def vocab():
    return json.loads(VOCAB.read_text(encoding="utf-8"))


# The standard


def test_every_verb_has_a_kind():
    kinds = std()["kinds"]
    assert kinds == KINDS
    assert set(kinds) == set(vocab()["verbs"])
    for word, verb in {**vocab()["synonyms"], **vocab()["confirm_synonyms"]}.items():
        assert verb in kinds, word


def valid_applies_to(a):
    if a == "all":
        return True
    if not (isinstance(a, dict) and len(a) == 1):
        return False
    (key, values), = a.items()
    allowed = {"kinds": set(KINDS.values()), "verbs": set(vocab()["verbs"])}.get(key)
    return allowed is not None and isinstance(values, list) and values and set(values) <= allowed


def test_rules_are_well_formed():
    s = std()
    assert s["version"] == 1
    assert s["severities"] == ["data", "hang", "misread"]
    assert [r["id"] for r in s["rules"]] == list(RULES)
    for r in s["rules"]:
        assert (r["applies_to"], r["severity"]) == RULES[r["id"]], r["id"]
        assert r["severity"] in s["severities"]
        assert valid_applies_to(r["applies_to"]), r["id"]
        assert isinstance(r["form"], str) and r["form"]
        assert r["tests"] and all("<command>" in t for t in r["tests"]), r["id"]


def test_spec_required_rule_tests():
    tests = {r["id"]: r["tests"] for r in std()["rules"]}
    assert NO_PROMPT_TEST in tests["no-prompt"]
    assert PAGED_TEST in tests["paged-list"]


def test_error_codes_paging_and_examples():
    s = std()
    assert {c: (e["retryable"], e["exit"]) for c, e in s["error_codes"].items()} == CODES
    assert list(s["error_codes"]) == list(CODES)
    assert all(isinstance(e["when"], str) and e["when"] for e in s["error_codes"].values())
    assert all(valid_applies_to(e["applies_to"]) for e in s["error_codes"].values())
    assert (s["paging"]["limit"], s["paging"]["max"]) == (20, 100)
    assert s["envelope"]["success"] == ["schema_version", "ok", "data"]
    assert s["envelope"]["failure"] == ["schema_version", "ok", "error"]
    assert s["error_object"] == ["code", "message", "retryable", "next_action"]
    assert set(s["idempotency"]["key_verbs"]) == {"create", "import", "run"}
    assert set(s["idempotency"]["end_state_verbs"]) == {"update", "delete", "sync", "stop", "export"}
    ok, bad = s["example_success"], s["example_failure"]
    assert list(ok) == s["envelope"]["success"] and ok["ok"] is True and ok["schema_version"] == 1
    assert list(bad) == s["envelope"]["failure"] and bad["ok"] is False
    assert list(bad["error"]) == s["error_object"]
    assert bad["error"]["code"] in CODES and bad["error"]["next_action"]
    assert bad["error"]["retryable"] is CODES[bad["error"]["code"]][0]


@pytest.mark.skipif(not RULES_MD.exists(), reason="cli-behavior.md is written in phase 3")
def test_every_rule_has_a_heading():
    headings = re.findall(r"^## (.+)$", RULES_MD.read_text(encoding="utf-8"), re.M)
    for r in std()["rules"]:
        assert r["id"] in headings, r["id"]


def test_deviation_schema():
    s = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert s["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert set(s["required"]) == {"standard_version", "deviations"}
    entry = s["$defs"]["deviation"]
    assert s["properties"]["deviations"]["items"] == {"$ref": "#/$defs/deviation"}
    assert entry["required"] == ["command", "rule", "proposed_form", "task", "harm", "evidence",
                                 "agent_cost", "work", "status"]
    props = entry["properties"]
    assert props["status"]["enum"] == ["proposed", "accepted", "declined"]
    assert props["evidence"]["minItems"] == 1
    assert props["work"]["required"] == ["standard", "deviation"]
    assert props["decided"]["required"] == ["on", "by"]
    assert entry["if"]["properties"]["status"]["const"] == "proposed"
    assert entry["else"]["required"] == ["decided"]


# Running the script


def run(*args, script=SCRIPT):
    p = subprocess.run([sys.executable, str(script), *map(str, args)],
                       capture_output=True, text=True, timeout=30)
    return p.returncode, p.stdout, p.stderr


def ok(code, out, err):
    assert code == 0, out + err
    assert err == ""
    env = json.loads(out)
    assert set(env) == {"schema_version", "ok", "data"}
    assert env["schema_version"] == 1 and env["ok"] is True
    return env["data"]


def assert_error(code, out, err, error_code):
    assert code == EXIT[error_code], out + err
    assert err == ""
    body = json.loads(out)
    assert set(body) == {"schema_version", "ok", "error"}
    assert body["schema_version"] == 1 and body["ok"] is False
    e = body["error"]
    assert set(e) == {"code", "message", "retryable", "next_action"}
    assert e["code"] == error_code and e["retryable"] is False
    assert isinstance(e["message"], str) and e["message"]
    assert isinstance(e["next_action"], str) and e["next_action"]
    return e["message"]


def problems(code, out, err):
    data = ok(code, out, err)
    assert set(data) == {"standard_version", "problems"} and data["problems"], data
    return data["problems"]


def entry(path, kind="command", mcp=None, renamed_to=None):
    c = {"path": path.split() if path else None, "mcp_name": mcp, "kind": kind, "source": "tool.py"}
    if renamed_to:
        c["renamed_to"] = renamed_to.split()
    return c


def make_tree(cli, *paths, extra=()):
    return {"cli": cli, "sources": [{"kind": "source", "ref": "tool.py"}], "complete": True,
            "commands": [entry(p) for p in paths] + list(extra)}


SKIPPED = [entry("item ls", kind="alias", renamed_to="tool item list"),
           entry("item all", kind="stub", renamed_to="tool item list"),
           entry(None, mcp="item_export"), entry("help"), entry("version"),
           entry("completion zsh")]
# designs-behavior-contract has no fixture tree; this is the tracker its prompt describes.
TRACKER = make_tree("tracker", "issue list", "issue create", "issue delete")


def write_tree(tmp_path, tree):
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    f = docs / "cli-tree.json"
    f.write_text(json.dumps(tree), encoding="utf-8")
    return f


def contract(tmp_path, tree):
    f = write_tree(tmp_path, tree)
    data = ok(*run("contract", "create", f))
    assert data == {"path": str(f.parent / "cli-contract.md")}
    return (f.parent / "cli-contract.md").read_text(encoding="utf-8")


def section(text, heading):
    level = len(heading.split()[0])
    m = re.search(rf"^{re.escape(heading)}\n(.*?)(?=^#{{1,{level}}} |\Z)", text, re.M | re.S)
    assert m, heading
    return m.group(1)


# contract create


def test_contract_is_deterministic(tmp_path):
    first = contract(tmp_path / "a", TRACKER)
    assert contract(tmp_path / "a", TRACKER) == first
    assert contract(tmp_path / "b", TRACKER) == first


def test_contract_covers_covered_commands_only(tmp_path):
    t = make_tree("tool", "item list", "item tail", "tag rm", extra=SKIPPED)
    text = contract(tmp_path, t)
    headings = re.findall(r"^### (.+)$", section(text, "## Commands"), re.M)
    assert headings == ["item list", "item tail", "tag rm"]
    assert re.findall(r"^### (.+)$", section(text, "## Tests"), re.M) == headings
    for skipped in ("item ls", "item all", "item_export", "tool help", "tool version", "completion"):
        assert skipped not in text, skipped


def test_contract_per_command_details(tmp_path):
    t = make_tree("tool", "item list", "item create", "item delete", "job start", "item tail", "tag rm")
    text = contract(tmp_path, t)

    def details(path):
        s = section(text, f"### {path}")
        return {k: v for k, v in re.findall(r"^- (Kind|Flags|Rules|Error codes): (.*)$", s, re.M)}

    d = details("item list")
    assert d["Kind"] == "read"
    assert d["Flags"] == "`--json`, `--limit`, `--cursor`"
    assert "`paged-list`" in d["Rules"] and "`dry-run`" not in d["Rules"]
    assert "CONFIRMATION_REQUIRED" not in d["Error codes"] and "CONFLICT" not in d["Error codes"]
    d = details("item create")
    assert d["Kind"] == "write"
    assert d["Flags"] == "`--json`, `--dry-run`, `--idempotency-key`"
    assert "`CONFLICT`" in d["Error codes"]
    d = details("item delete")
    assert d["Flags"] == "`--json`, `--yes`, `--dry-run`"
    assert "`CONFIRMATION_REQUIRED`" in d["Error codes"]
    d = details("job start")
    assert d["Kind"] == "long-running" and d["Flags"] == "`--json`"
    assert "`operation-handle`" in d["Rules"]
    # An unlisted verb is write, the strictest kind; a synonym takes its verb's kind and rules.
    d = details("item tail")
    assert d["Kind"] == "write" and "`--idempotency-key`" in d["Flags"]
    assert details("tag rm") == details("item delete")


def test_contract_holds_the_spec_tests(tmp_path):
    text = contract(tmp_path, TRACKER)
    tests = section(text, "## Tests")
    assert NO_PROMPT_TEST.replace("<command>", "tracker issue list") in tests
    assert PAGED_TEST.replace("<command>", "tracker issue list") in tests
    assert "<command>" not in text


def test_contract_states_each_rule_form(tmp_path):
    # The spec asks the contract to say how a repeated create or delete is made safe.
    rules = section(contract(tmp_path, TRACKER), "## Rules")
    for r in std()["rules"]:
        if r["id"] != "operation-handle":
            assert f"- `{r['id']}`: {r['form']}" in rules, r["id"]
    assert "operation-handle" not in rules


def test_contract_same_answer_for_unrelated_clis(tmp_path):
    a = contract(tmp_path / "a", TRACKER)
    b = contract(tmp_path / "b", make_tree("vault", "secret search", "backup import", "tag rm",
                                           "job start", "backup export"))
    shared = lambda t: t[t.index("## Envelope"):t.index("## Tests")]
    assert shared(a) == shared(b)
    flags = lambda t: set(re.findall(r"`(--[a-z-]+)`", "\n".join(re.findall(r"^- Flags: .*$", t, re.M))))
    assert flags(a) == flags(b) == {"--json", "--limit", "--cursor", "--yes", "--dry-run",
                                    "--idempotency-key"}
    for code in CODES:
        assert f"`{code}`" in shared(a)


def test_contract_dry_run_writes_nothing(tmp_path):
    f = write_tree(tmp_path, TRACKER)
    data = ok(*run("contract", "create", f, "--dry-run"))
    assert set(data) == {"path", "contract"}
    assert data["path"] == str(f.parent / "cli-contract.md")
    assert sorted(p.name for p in f.parent.iterdir()) == ["cli-tree.json"]
    assert data["contract"] == contract(tmp_path, TRACKER)


def test_contract_idempotency_key(tmp_path):
    f = write_tree(tmp_path, TRACKER)
    out = f.parent / "cli-contract.md"
    first = ok(*run("contract", "create", f, "--idempotency-key", "k1"))
    assert first == {"path": str(out)}
    text = out.read_text(encoding="utf-8")
    # The same key and tree returns the first result and leaves the file as it was.
    assert ok(*run("contract", "create", f, "--idempotency-key", "k1")) == first
    assert out.read_text(encoding="utf-8") == text
    # The same key with a changed tree is a conflict and changes nothing.
    write_tree(tmp_path, make_tree("tracker", "issue list"))
    message = assert_error(*run("contract", "create", f, "--idempotency-key", "k1"), "CONFLICT")
    assert "k1" in message
    assert out.read_text(encoding="utf-8") == text
    # A new key writes the changed tree's contract.
    ok(*run("contract", "create", f, "--idempotency-key", "k2"))
    assert "### issue create" not in out.read_text(encoding="utf-8")


def from_tree_fixture():
    text = (EVALS / "designs-contract-from-tree/prompt.md").read_text(encoding="utf-8")
    return json.loads(re.search(r"```json\n(.*?)```", text, re.S).group(1))


CONTRACT_CASES = {"designs-behavior-contract": lambda: TRACKER,
                  "designs-contract-from-tree": from_tree_fixture}
CONTENT_GRADERS = [(case, g) for case in CONTRACT_CASES
                   for g in sorted((EVALS / case / "graders").glob("*.md"))
                   if frontmatter(g).get("target") == {"source": "file", "path": "docs/cli-contract.md"}]


def test_each_contract_case_has_content_graders():
    assert {case for case, _ in CONTENT_GRADERS} == set(CONTRACT_CASES)


@pytest.mark.parametrize("case, grader", CONTENT_GRADERS,
                         ids=[f"{c}/{g.stem}" for c, g in CONTENT_GRADERS])
def test_contract_meets_eval_grader(tmp_path, case, grader):
    fm = frontmatter(grader)
    assert fm["type"] == "regex"
    found = re.search(fm["pattern"], contract(tmp_path, CONTRACT_CASES[case]())) is not None
    assert found is (fm.get("match", "contains") != "not_contains")


# result check

CHECK_PATHS = ["item list", "item get", "item create", "item delete", "job start"]
CHECK_TREE = make_tree("tool", *CHECK_PATHS, extra=SKIPPED)
FIELDS = {
    "pass": {"evidence": ["tool.py:3"]},
    "fail": {"evidence": ["tool.py:5", "tool.py:40"], "task": "read every item", "fix": "add the flag",
             "test": "run the command with the flag"},
    "unknown": {"test": "run the command with stdin closed"},
    "not_applicable": {"reason": "outside the rule's applies_to"},
    "deviation": {"evidence": ["tool.py:7"]},
}
OVERRIDES = {
    ("paged-list", "item list"): "fail",
    ("confirm-flag", "item delete"): "fail",
    ("envelope", "item list"): "fail",
    ("exit-status", "item list"): "fail",
    ("json-flag", "item get"): "fail",
    ("error-object", "item create"): "unknown",
    ("stdout-data-only", "item get"): "deviation",
    ("operation-handle", "job start"): "not_applicable",
}
# Severity, then the tree's command order, then the rules table's order.
FINDING_ORDER = [("paged-list", ["item list"]), ("confirm-flag", ["item delete"]),
                 ("envelope", ["item list"]), ("exit-status", ["item list"]),
                 ("json-flag", ["item get"])]


def deviation(command, rule, status, decided=True):
    e = {"command": command, "rule": rule, "proposed_form": "prints a table",
         "task": "count items in the nightly script", "harm": "the script parses the table",
         "evidence": ["scripts/count.sh:3"], "agent_cost": "an agent parses a table",
         "work": {"standard": "move the script to --json", "deviation": "none"}, "status": status}
    if decided:
        e["decided"] = {"on": "2026-10-21", "by": "Dana Reyes"}
    return e


REGISTER = {"standard_version": 1, "deviations": [
    deviation("item get", "stdout-data-only", "accepted"),
    deviation("item delete", "dry-run", "proposed", decided=False),
    deviation("item create", "json-flag", "declined"),
]}


def applies(rule, path, kinds):
    verb = path.split()[-1]
    kind = kinds.get(path) or std()["kinds"].get(verb, "write")
    a = rule["applies_to"]
    return a == "all" or kind in a.get("kinds", ()) or verb in a.get("verbs", ())


def build_results(paths=CHECK_PATHS, overrides=OVERRIDES, kinds=None):
    results = []
    for rule in std()["rules"]:
        groups = {}
        for p in paths:
            status = overrides.get((rule["id"], p)) or (
                "pass" if applies(rule, p, kinds or {}) else "not_applicable")
            groups.setdefault(status, []).append(p)
        for status, commands in groups.items():
            results.append({"commands": commands, "rule": rule["id"], "status": status,
                            **copy.deepcopy(FIELDS[status])})
    return {"standard_version": 1, "results": results}


def find(results, rule, status):
    return next(r for r in results["results"] if r["rule"] == rule and r["status"] == status)


def repo(tmp_path, results, register=REGISTER, tree=CHECK_TREE):
    (tmp_path / "tool.py").write_text("".join(f"line {i}\n" for i in range(1, 41)), encoding="utf-8")
    f = write_tree(tmp_path, tree).parent / "cli-behavior.json"
    f.write_text(json.dumps(results), encoding="utf-8")
    if register is not None:
        (f.parent / "cli-behavior-deviations.json").write_text(json.dumps(register), encoding="utf-8")
    return f


def test_result_check_accepts_a_valid_file(tmp_path):
    results = build_results()
    data = ok(*run("result", "check", repo(tmp_path, results)))
    assert set(data) == {"standard_version", "counts", "findings", "problems"}
    assert data["standard_version"] == 1 and data["problems"] == []
    counts = Counter(r["status"] for r in results["results"])
    assert data["counts"] == {s: counts[s] for s in STATUSES}
    # Only the deviation result counts; the proposed and declined entries do not.
    assert data["counts"]["deviation"] == 1
    assert [(f["rule"], f["commands"]) for f in data["findings"]] == FINDING_ORDER
    for f in data["findings"]:
        assert f["status"] == "fail" and f["severity"] == RULES[f["rule"]][1]


def test_result_check_without_a_register(tmp_path):
    overrides = {k: v for k, v in OVERRIDES.items() if v != "deviation"}
    data = ok(*run("result", "check", repo(tmp_path, build_results(overrides=overrides), register=None)))
    assert data["counts"]["deviation"] == 0


def test_result_check_rejects_an_empty_register(tmp_path):
    overrides = {k: v for k, v in OVERRIDES.items() if v != "deviation"}
    f = repo(tmp_path, build_results(overrides=overrides), register={})
    assert any("deviations list" in p for p in problems(*run("result", "check", f)))


def extract_files(case, tmp_path):
    text = (EVALS / case / "prompt.md").read_text(encoding="utf-8")
    for name, body in re.findall(r"^`([^`\n]+)`:\n\n```\w*\n(.*?)^```$", text, re.M | re.S):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(body, encoding="utf-8")


def test_result_check_accepts_the_deviation_eval_fixture(tmp_path):
    extract_files("accepts-deviation-on-instruction", tmp_path)
    data = ok(*run("result", "check", tmp_path / "docs/cli-behavior.json"))
    # The fixture plan's own line: 2 pass, 8 fail, 0 unknown, 6 not applicable, 0 deviation.
    assert data["counts"] == {"pass": 2, "fail": 8, "unknown": 0, "not_applicable": 6, "deviation": 0}
    assert [f["severity"] for f in data["findings"]] == sorted(
        (f["severity"] for f in data["findings"]), key=["data", "hang", "misread"].index)


def tail_results(overrides=None):
    # honors-accepted-deviation: item tail is an unlisted verb whose handler only reads.
    results = build_results(["item get", "item tail"],
                            {("stdout-data-only", "item tail"): "deviation", **(overrides or {})},
                            {"item tail": "read"})
    find(results, "json-flag", "pass")["command_kind"] = "read"
    return results


def test_result_check_accepts_an_accepted_deviation(tmp_path):
    extract_files("honors-accepted-deviation", tmp_path)
    f = tmp_path / "docs/cli-behavior.json"
    f.write_text(json.dumps(tail_results()), encoding="utf-8")
    data = ok(*run("result", "check", f))
    assert data["counts"]["deviation"] == 1 and data["findings"] == []


def test_command_kind_sets_an_unlisted_verbs_rules(tmp_path):
    extract_files("honors-accepted-deviation", tmp_path)
    f = tmp_path / "docs/cli-behavior.json"
    f.write_text(json.dumps(tail_results({("dry-run", "item tail"): "pass"})), encoding="utf-8")
    assert any("dry-run: item tail is outside the rule" in p for p in problems(*run("result", "check", f)))


def drop(results, rule, status, command):
    find(results, rule, status)["commands"].remove(command)


def set_status(results, rule, status, new):
    r = find(results, rule, status)
    r["status"] = new
    r.update(copy.deepcopy(FIELDS[new]))


# Each mutation of the valid fixture and a line its problem message must hold.
MUTATIONS = {
    "command left uncovered": (lambda res, reg: drop(res, "no-prompt", "pass", "item get"),
                               "no-prompt: item get has no result"),
    "status outside applies_to": (lambda res, reg: set_status(res, "confirm-flag", "not_applicable", "pass"),
                                  "confirm-flag: item list is outside the rule"),
    "missing field for status": (lambda res, reg: find(res, "paged-list", "fail").pop("fix"),
                                 "(paged-list, fail) is missing fix"),
    "unknown missing test": (lambda res, reg: find(res, "error-object", "unknown").pop("test"),
                             "(error-object, unknown) is missing test"),
    "evidence not path:line": (lambda res, reg: find(res, "exit-status", "pass").update(evidence=["tool.py"]),
                               "'tool.py' is not path:line"),
    "evidence past end of file": (
        lambda res, reg: find(res, "envelope", "pass").update(evidence=["tool.py:41"]),
        "'tool.py:41': tool.py has 40 lines"),
    "evidence outside the repository": (
        lambda res, reg: find(res, "dry-run", "pass").update(evidence=["/etc/hosts:1"]),
        "'/etc/hosts:1' is not repository-relative"),
    "result names an unknown rule": (
        lambda res, reg: res["results"].append({"commands": ["item get"], "rule": "no-such-result-rule",
                                                "status": "not_applicable", "reason": "x"}),
        "'no-such-result-rule' is not a rule in the standard"),
    "result names an uncovered command": (
        lambda res, reg: find(res, "secret-input", "pass")["commands"].append("item all"),
        "'item all' is not a covered command in the tree"),
    "deviation with no accepted entry": (
        lambda res, reg: reg["deviations"][0].update(status="proposed"),
        "item get stdout-data-only is a deviation with no accepted entry"),
    "register entry missing a field": (lambda res, reg: reg["deviations"][1].pop("harm"),
                                       "deviations[1] is missing harm"),
    "decided entry without decided": (lambda res, reg: reg["deviations"][2].pop("decided"),
                                      "deviations[2] is missing decided"),
    "register entry with an unknown rule": (
        lambda res, reg: reg["deviations"].append(deviation("item get", "no-such-entry-rule", "proposed")),
        "'no-such-entry-rule' is not a rule in the standard"),
    "register entry with an uncovered command": (
        lambda res, reg: reg["deviations"].append(deviation("item frob", "json-flag", "proposed")),
        "'item frob' is not a covered command in the tree"),
    "register entry with a bad status": (
        lambda res, reg: reg["deviations"].append(deviation("job start", "json-flag", "maybe")),
        "status 'maybe' is not one of proposed, accepted, declined"),
}


@pytest.mark.parametrize("name", list(MUTATIONS))
def test_result_check_rejects(tmp_path, name):
    mutate, expected = MUTATIONS[name]
    results, register = build_results(), copy.deepcopy(REGISTER)
    mutate(results, register)
    found = problems(*run("result", "check", repo(tmp_path, results, register)))
    assert any(expected in p for p in found), found


def test_result_check_reports_every_problem_at_once(tmp_path):
    results, register = build_results(), copy.deepcopy(REGISTER)
    for mutate, _ in MUTATIONS.values():
        mutate(results, register)
    found = problems(*run("result", "check", repo(tmp_path, results, register)))
    for _, expected in MUTATIONS.values():
        assert any(expected in p for p in found), expected


# Failures


BAD_INPUT = {
    "tree not JSON": ("contract", "{not json"),
    "tree not an object": ("contract", "[]"),
    "tree without cli": ("contract", json.dumps({"commands": []})),
    "tree with a bad path": ("contract", json.dumps(make_tree("t", extra=[dict(entry("a b"), path=[])]))),
    "results not JSON": ("result", "{not json"),
    "results without results": ("result", json.dumps({"standard_version": 1})),
    "results of another version": ("result", json.dumps({"standard_version": 2, "results": []})),
}


@pytest.mark.parametrize("name", list(BAD_INPUT))
def test_bad_input_exits_2(tmp_path, name):
    command, content = BAD_INPUT[name]
    docs = tmp_path / "docs"
    docs.mkdir()
    if command == "contract":
        f = docs / "cli-tree.json"
        argv = ("contract", "create", f)
    else:
        write_tree(tmp_path, CHECK_TREE)
        f = docs / "cli-behavior.json"
        argv = ("result", "check", f)
    f.write_text(content, encoding="utf-8")
    assert_error(*run(*argv), "INVALID_ARGUMENT")


def test_missing_files_exit_2(tmp_path):
    assert_error(*run("contract", "create", tmp_path / "absent.json"), "INVALID_ARGUMENT")
    assert_error(*run("result", "check", tmp_path / "absent.json"), "INVALID_ARGUMENT")
    f = tmp_path / "cli-behavior.json"
    f.write_text(json.dumps(build_results()), encoding="utf-8")
    assert "cli-tree.json" in assert_error(*run("result", "check", f), "INVALID_ARGUMENT")
    write_tree(tmp_path, CHECK_TREE)
    f = repo(tmp_path, build_results(), register=None)
    (f.parent / "cli-behavior-deviations.json").write_text("{nope", encoding="utf-8")
    assert "cli-behavior-deviations.json" in assert_error(*run("result", "check", f), "INVALID_ARGUMENT")


USAGE = [[], ["contract"], ["contract", "create"], ["contract", "create", "a.json", "b.json"],
         ["contract", "create", "--dry-run"], ["contract", "create", "a.json", "--idempotency-key"],
         ["contract", "create", "a.json", "--idempotency-key", "k", "--idempotency-key", "k"],
         ["contract", "create", "a.json", "--dry-run", "--dry-run"],
         ["contract", "check", "a.json"], ["result", "check"],
         ["result", "check", "a.json", "--dry-run"], ["result", "create", "a.json"], ["tree", "check", "a"]]


@pytest.mark.parametrize("argv", USAGE, ids=[" ".join(a) or "none" for a in USAGE])
def test_usage_error_exits_2(argv):
    assert_error(*run(*argv), "INVALID_ARGUMENT")


@pytest.mark.parametrize("script, argv, code", [
    (SCRIPT, ["contract"], "INVALID_ARGUMENT"),
    (SCRIPT, ["result", "check", "/nonexistent/cli-behavior.json"], "INVALID_ARGUMENT"),
    (TREE_SCRIPT, ["lint"], "INVALID_ARGUMENT"),
    (TREE_SCRIPT, ["check", "/nonexistent/cli-tree.json"], "INVALID_ARGUMENT"),
], ids=["behavior usage", "behavior input", "tree usage", "tree input"])
def test_both_scripts_fail_with_one_envelope_on_stdout(script, argv, code):
    assert_error(*run(*argv, script=script), code)


def test_internal_error_exits_1(tmp_path):
    # A broken vocabulary three folders above a copy of the script is a fault in the script's inputs.
    scripts = tmp_path / "skills/cli-behavior/scripts"
    scripts.mkdir(parents=True)
    shutil.copytree(SKILL / "references", tmp_path / "skills/cli-behavior/references")
    (tmp_path / "resources").mkdir()
    (tmp_path / "resources/cli-naming.json").write_text('{"version": 1}', encoding="utf-8")
    script = Path(shutil.copy(SCRIPT, scripts / "behavior.py"))
    f = write_tree(tmp_path, TRACKER)
    assert_error(*run("contract", "create", f, script=script), "INTERNAL")


def test_closed_stdout_exits_1(tmp_path):
    f = write_tree(tmp_path, make_tree("tool", *(f"n{i} create" for i in range(2000))))
    p = subprocess.Popen([sys.executable, str(SCRIPT), "contract", "create", str(f), "--dry-run"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p.stdout.close()
    err = p.stderr.read()
    assert p.wait(timeout=30) == 1
    assert err == ""


@pytest.mark.skipif(not Path("/usr/bin/python3").exists(), reason="no system Python")
def test_runs_on_the_system_python(tmp_path):
    f = repo(tmp_path, build_results())
    for argv in (["contract", "create", f.parent / "cli-tree.json"], ["result", "check", f]):
        p = subprocess.run(["/usr/bin/python3", str(SCRIPT), *map(str, argv)],
                           capture_output=True, text=True, timeout=30)
        assert p.returncode == 0, p.stdout + p.stderr
