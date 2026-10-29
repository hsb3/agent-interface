"""Checks on the CLI naming vocabulary and the `tree.py check` command."""

from collections import Counter
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from helpers import ROOT

SKILL = ROOT / "skills/menu-design"
VOCAB = ROOT / "resources/cli-naming.json"
SCRIPT = SKILL / "scripts/tree.py"

# vocabulary.md "Severities", and the rule id each code reports.
CODES = {
    "synonym": ("violation", "approved-verbs"),
    "verb-first": ("violation", "mcp-noun-verb"),
    "underscore-in-noun": ("violation", "noun-hyphenated"),
    "long-form": ("violation", "noun-full-word"),
    "noun-is-verb": ("violation", "noun-not-verb"),
    "depth": ("violation", "tree-depth"),
    "mixed-shape": ("violation", "tree-noun-verb"),
    "collision": ("violation", "collisions"),
    "confirm-synonym": ("advisory", "confirm-only-synonyms"),
    "unlisted-verb": ("advisory", "approved-verbs"),
    "ambiguous": ("advisory", "mcp-noun-verb"),
    "verb-not-last": ("advisory", "mcp-noun-verb"),
    "no-noun": ("advisory", "mcp-noun-verb"),
    "plural": ("advisory", "noun-singular"),
    "incomplete-tree": ("advisory", "complete-tree"),
}


def no_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    assert len(keys) == len(set(keys)), [k for k, n in Counter(keys).items() if n > 1]
    return dict(pairs)


def test_vocabulary_is_consistent():
    # json.loads keeps only the last of two equal keys, so a repeat inside one map needs the hook.
    data = json.loads(VOCAB.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)
    verbs = set(data["verbs"])
    maps = (data["synonyms"], data["confirm_synonyms"])
    words = [w for m in maps for w in m]
    assert not [w for w, n in Counter(words).items() if n > 1]
    for word in words:
        assert word not in verbs, word
        assert word not in data["root_commands"], word
    for m in maps:
        for word, verb in m.items():
            assert verb in verbs, (word, verb)


def cmd(path=None, mcp=None, kind="command", source="cli.py", renamed_to=None):
    c = {"path": path.split() if path else None, "mcp_name": mcp, "kind": kind, "source": source}
    if renamed_to is not None:
        c["renamed_to"] = renamed_to.split()
    return c


def tree(*commands, **top):
    t = {"cli": "tool", "sources": [{"kind": "source", "ref": "cli.py"}],
         "complete": True, "commands": list(commands)}
    t.update(top)
    return t


def run(tmp_path, content, script=SCRIPT):
    f = tmp_path / "cli-tree.json"
    f.write_text(content if isinstance(content, str) else json.dumps(content), encoding="utf-8")
    p = subprocess.run([sys.executable, str(script), "check", str(f)],
                       capture_output=True, text=True, timeout=30)
    return p.returncode, p.stdout, p.stderr


def check(tmp_path, t):
    code, out, err = run(tmp_path, t)
    assert code == 0, out + err
    env = json.loads(out)
    assert env["ok"] is True
    return env["data"]["findings"]


# vocabulary.md "Classifying MCP names", every example.
MCP_TABLE = [
    ("slugify", [("no-noun", None)]),
    ("issue_list_all", [("verb-not-last", None)]),
    ("issue_list", []),
    ("work_item_list", []),
    ("list_notes", [("verb-first", "note_list")]),
    ("check_run", [("ambiguous", None)]),
    ("random_id", [("ambiguous", None)]),
]


@pytest.mark.parametrize("name, expected", MCP_TABLE)
def test_mcp_name_classification(tmp_path, name, expected):
    findings = check(tmp_path, tree(cmd(mcp=name)))
    assert [(f["code"], f["suggest"]) for f in findings] == expected
    assert all(f["path"] == name for f in findings)


SRC2 = [{"kind": "catalog", "ref": "toolkit.json"}, {"kind": "source", "ref": "cli.py"}]

# (tree, 1 when it has a violation else 0, findings as (code, path, suggest) in output order)
ROWS = {
    "clean": (tree(cmd("issue list", "issue_list"), cmd("issue create")), 0, []),
    "advisory only": (tree(cmd("report frobnicate"), cmd("issue list")), 0,
                      [("unlisted-verb", "report frobnicate", None)]),
    "empty commands": (tree(), 0, []),
    "synonym": (tree(cmd("label ls"), cmd("issue list")), 1,
                [("synonym", "label ls", "label list")]),
    "synonym in mcp name": (tree(cmd(mcp="issue_ls")), 1, [("synonym", "issue_ls", "issue_list")]),
    "verb-first": (tree(cmd(mcp="list_notes")), 1, [("verb-first", "list_notes", "note_list")]),
    "verb-first keeps plural exception": (tree(cmd(mcp="list_status")), 1,
                                          [("verb-first", "list_status", "status_list")]),
    "verb-first with automatic synonym": (tree(cmd(mcp="ls_notes")), 1,
                                          [("verb-first", "ls_notes", "note_list")]),
    "verb-first with confirm-only synonym": (tree(cmd(mcp="show_notes")), 1,
                                             [("confirm-synonym", "show_notes", None),
                                              ("verb-first", "show_notes", None)]),
    "underscore-in-noun": (tree(cmd("work_item list")), 1,
                           [("underscore-in-noun", "work_item list", "work-item list")]),
    "long-form": (tree(cmd("repository list")), 1, [("long-form", "repository list", "repo list")]),
    "noun-is-verb": (tree(cmd("run list")), 1, [("noun-is-verb", "run list", None)]),
    "noun-is-verb whole noun only": (tree(cmd("sync-state get")), 0, []),
    "depth": (tree(cmd("issue label list")), 1, [("depth", "issue label list", None)]),
    "depth is not classified further": (tree(cmd("issues ls all")), 1, [("depth", "issues ls all", None)]),
    "mixed-shape": (tree(cmd("list"), cmd("get"), cmd("issue get")), 1,
                    [("mixed-shape", "get", None), ("mixed-shape", "list", None)]),
    "flat one-noun cli": (tree(cmd("list"), cmd("get"), cmd("create")), 0, []),
    "mixed-shape ignores depth and skipped": (
        tree(cmd("list"), cmd("issue label list"), cmd("help topic"), cmd("issue get", kind="stub",
                                                                         renamed_to="tool issue list")),
        1, [("depth", "issue label list", None)]),
    "confirm-synonym": (tree(cmd("config set")), 0, [("confirm-synonym", "config set", None)]),
    "unlisted-verb": (tree(cmd("report frobnicate")), 0, [("unlisted-verb", "report frobnicate", None)]),
    "ambiguous": (tree(cmd(mcp="check_run")), 0, [("ambiguous", "check_run", None)]),
    "verb-not-last": (tree(cmd(mcp="issue_list_all")), 0, [("verb-not-last", "issue_list_all", None)]),
    "no-noun": (tree(cmd(mcp="slugify")), 0, [("no-noun", "slugify", None)]),
    "plural": (tree(cmd("issues list")), 0, [("plural", "issues list", None)]),
    "plural exception": (tree(cmd("status get")), 0, []),
    "mcp nouns are not noun-checked": (tree(cmd(mcp="notes_list"), cmd(mcp="repository_list")), 0, []),
    "incomplete-tree": (tree(cmd("issue list"), sources=SRC2, complete=False), 0,
                        [("incomplete-tree", "", None)]),
    "stubs and aliases skipped": (
        tree(cmd("issue list"), cmd("issue ls", kind="stub", renamed_to="tool issue list"),
             cmd("issue all", mcp="list_issues", kind="alias", renamed_to="tool issue list")),
        0, []),
    "root commands skipped": (
        tree(cmd("help"), cmd("version"), cmd("serve"), cmd("completion zsh"), cmd("init ls"),
             cmd("doctor"), cmd("update"), cmd("issue list")),
        0, []),
    "local_verbs honored": (
        tree(cmd("text encode", "text_encode"), cmd("config set"), cmd(mcp="encode_labels"),
             local_verbs=["encode", "set"]),
        1, [("verb-first", "encode_labels", "label_encode")]),
    "several renames propose the fully fixed name": (
        tree(cmd("work_item ls")), 1,
        [("synonym", "work_item ls", "work-item list"),
         ("underscore-in-noun", "work_item ls", "work-item list")]),
    "collision between proposals": (
        tree(cmd("issue ls"), cmd("issue all"), cmd("issue get")), 1,
        [("synonym", "issue all", None), ("collision", "issue list", None), ("synonym", "issue ls", None)]),
    "collision with an existing command": (
        tree(cmd("issue ls"), cmd("issue list")), 1,
        [("collision", "issue list", None), ("synonym", "issue ls", None)]),
    "collision with a stub": (
        tree(cmd("label ls"), cmd("label list", kind="stub", renamed_to="tool label get")), 1,
        [("collision", "label list", None), ("synonym", "label ls", None)]),
    "collision with an mcp name": (
        tree(cmd(mcp="list_notes"), cmd(mcp="note_list")), 1,
        [("verb-first", "list_notes", None), ("collision", "note_list", None)]),
}


@pytest.mark.parametrize("name", list(ROWS))
def test_tree_findings(tmp_path, name):
    # A completed check exits 0 even with violations; callers read the findings.
    t, has_violation, expected = ROWS[name]
    findings = check(tmp_path, t)
    assert [(f["code"], f["path"], f["suggest"]) for f in findings] == expected
    assert any(f["severity"] == "violation" for f in findings) is (has_violation == 1)


def test_every_severity_code_has_a_row():
    codes = {c for _, _, rows in ROWS.values() for c, _, _ in rows}
    assert codes == set(CODES)


def test_findings_carry_the_contract_fields(tmp_path):
    t = tree(*(c for r in ROWS.values() for c in r[0]["commands"]),
             local_verbs=["encode"], complete=False)
    code, out, _ = run(tmp_path, t)
    env = json.loads(out)
    assert code == 0
    assert set(env) == {"schema_version", "ok", "data"}
    assert env["schema_version"] == 1 and env["ok"] is True
    assert set(env["data"]) == {"standard_version", "findings"}
    assert env["data"]["standard_version"] == json.loads(VOCAB.read_text())["version"]
    findings = env["data"]["findings"]
    assert findings == sorted(findings, key=lambda f: (f["path"], f["code"]))
    for f in findings:
        assert set(f) == {"code", "severity", "path", "message", "suggest", "rule", "source"}
        assert (f["severity"], f["rule"]) == CODES[f["code"]], f
        assert isinstance(f["message"], str) and f["message"]
        whole_tree = f["code"] in ("incomplete-tree", "collision")
        assert f["source"] == (None if whole_tree else "cli.py"), f


def test_finding_sources_and_messages(tmp_path):
    t = tree(cmd("issue ls"), cmd("issue all", source="toolkit.json"), sources=SRC2, complete=False)
    by_path = {f["path"]: f for f in check(tmp_path, t)}
    assert by_path["issue ls"]["source"] == "cli.py"
    assert by_path["issue all"]["source"] == "toolkit.json"
    assert "toolkit.json" in by_path[""]["message"] and "cli.py" in by_path[""]["message"]
    assert "issue ls" in by_path["issue list"]["message"] and "issue all" in by_path["issue list"]["message"]


def missing(field, top=True):
    t = tree(cmd("issue list"))
    del (t if top else t["commands"][0])[field]
    return t


INVALID = {
    "not JSON": "{not json",
    "not an object": "[]",
    "missing cli": missing("cli"),
    "missing sources": missing("sources"),
    "missing complete": missing("complete"),
    "missing commands": missing("commands"),
    "missing path": missing("path", top=False),
    "missing mcp_name": missing("mcp_name", top=False),
    "missing kind": missing("kind", top=False),
    "missing source": missing("source", top=False),
    "unknown kind": tree(cmd("issue list", kind="hidden")),
    "unknown source kind": tree(sources=[{"kind": "web", "ref": "cli.py"}]),
    "source not in sources": tree(cmd("issue list", source="other.py")),
    "stub without renamed_to": tree(cmd("issue ls", kind="stub")),
    "alias without renamed_to": tree(cmd("issue ls", kind="alias")),
    "neither path nor mcp_name": tree(cmd()),
    "empty path": tree({"path": [], "mcp_name": None, "kind": "command", "source": "cli.py"}),
    "path not a list of words": tree({"path": "issue list", "mcp_name": None, "kind": "command",
                                      "source": "cli.py"}),
    "complete not a boolean": tree(complete="yes"),
    "local_verbs not a list": tree(local_verbs="encode"),
    "source not a string": tree(cmd("issue list", source=["cli.py"])),
    "empty renamed_to": tree(dict(cmd("issue ls", kind="stub"), renamed_to=[])),
    "empty path word": tree(dict(cmd(), path=["", "list"])),
    "path word with a space": tree(dict(cmd(), path=["issue list"])),
    "empty mcp_name": tree(cmd(mcp="")),
    "mcp_name with an empty word": tree(cmd(mcp="issue__list")),
    "mcp_name with a leading underscore": tree(cmd(mcp="_list")),
    "deeply nested JSON": "[" * 100000 + "]" * 100000,
}


EXIT = {"INVALID_ARGUMENT": 2, "INTERNAL": 1}


def assert_error(code, out, err, error_code):
    assert code == EXIT[error_code]
    assert err == ""
    body = json.loads(out)
    assert set(body) == {"schema_version", "ok", "error"}
    assert body["schema_version"] == 1 and body["ok"] is False
    e = body["error"]
    assert set(e) == {"code", "message", "retryable", "next_action"}
    assert e["code"] == error_code and e["retryable"] is False
    assert isinstance(e["message"], str) and e["message"]
    assert isinstance(e["next_action"], str) and e["next_action"]


@pytest.mark.parametrize("name", list(INVALID))
def test_invalid_tree_exits_2(tmp_path, name):
    assert_error(*run(tmp_path, INVALID[name]), "INVALID_ARGUMENT")


def test_unreadable_tree_exits_2(tmp_path):
    p = subprocess.run([sys.executable, str(SCRIPT), "check", str(tmp_path / "absent.json")],
                       capture_output=True, text=True, timeout=30)
    assert_error(p.returncode, p.stdout, p.stderr, "INVALID_ARGUMENT")


@pytest.mark.parametrize("argv", [[], ["lint", "x.json"], ["check"], ["check", "a.json", "b.json"]])
def test_usage_error_exits_2(argv):
    p = subprocess.run([sys.executable, str(SCRIPT), *argv], capture_output=True, text=True, timeout=30)
    assert_error(p.returncode, p.stdout, p.stderr, "INVALID_ARGUMENT")


def test_closed_stdout_exits_1(tmp_path):
    f = tmp_path / "cli-tree.json"
    f.write_text(json.dumps(tree(*(cmd(f"n{i} ls") for i in range(2000)))), encoding="utf-8")
    p = subprocess.Popen([sys.executable, str(SCRIPT), "check", str(f)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p.stdout.close()
    # The envelope cannot reach a closed stdout; the exit status still says INTERNAL.
    err = p.stderr.read()
    assert p.wait(timeout=30) == 1
    assert err == ""


@pytest.mark.skipif(not Path("/usr/bin/python3").exists(), reason="no system Python")
def test_runs_on_the_system_python(tmp_path):
    f = tmp_path / "cli-tree.json"
    f.write_text(json.dumps(ROWS["synonym"][0]), encoding="utf-8")
    p = subprocess.run(["/usr/bin/python3", str(SCRIPT), "check", str(f)],
                       capture_output=True, text=True, timeout=30)
    assert p.returncode == 0, p.stdout + p.stderr
    assert json.loads(p.stdout)["data"]["findings"][0]["suggest"] == "label list"


def test_internal_error_exits_1(tmp_path):
    # A broken vocabulary three folders above a copy of the script is a fault in the check, not in the tree.
    (tmp_path / "skills/menu-design/scripts").mkdir(parents=True)
    (tmp_path / "resources").mkdir()
    script = Path(shutil.copy(SCRIPT, tmp_path / "skills/menu-design/scripts/tree.py"))
    (tmp_path / "resources/cli-naming.json").write_text('{"version": 1}', encoding="utf-8")
    assert_error(*run(tmp_path, tree(cmd("issue list")), script=script), "INTERNAL")
