"""Shared fixtures: the repository root and discovered skills."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def discovered_skills() -> list[Path]:
    skills = sorted(p for p in (ROOT / "skills").iterdir()
                    if p.is_dir() and not p.name.startswith((".", "_")))
    assert skills, "No skills discovered"
    return skills
