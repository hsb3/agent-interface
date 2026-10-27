"""Every OpenSpec scenario names an existing eval case, and every eval case is traced to one."""

from pathlib import Path
import re

from helpers import ROOT

SCENARIO = re.compile(r"^#### Scenario: .+?(?=^#{1,4} |\Z)", re.M | re.S)
EVAL = re.compile(r"^- \*\*EVAL\*\* (evals/[^\s]+?)/?$", re.M)


def spec_files() -> list[Path]:
    specs = list((ROOT / "openspec/specs").glob("**/*.md"))
    return specs + [p for p in (ROOT / "openspec/changes").glob("*/specs/**/*.md")
                    if "archive" not in p.relative_to(ROOT / "openspec/changes").parts]


def test_scenarios_name_existing_eval_cases() -> None:
    files = spec_files()
    assert files, "No specs under openspec/specs or openspec/changes"
    for spec in files:
        for scenario in SCENARIO.findall(spec.read_text(encoding="utf-8")):
            evals = EVAL.findall(scenario)
            title = scenario.splitlines()[0]
            assert len(evals) == 1, f"{spec}: {title} needs exactly one EVAL line"
            assert (ROOT / evals[0] / "prompt.md").is_file(), f"{spec}: {title}: missing {evals[0]}"


def test_every_eval_case_is_traced_to_a_scenario() -> None:
    traced = {e.rstrip("/") for spec in spec_files() for e in EVAL.findall(spec.read_text())}
    for prompt in (ROOT / "evals").glob("*/*/prompt.md"):
        case = prompt.parent.relative_to(ROOT).as_posix()
        assert case in traced, f"{case} is not named by any spec scenario"
