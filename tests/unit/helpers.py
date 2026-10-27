"""Small readers shared by the unit tests."""

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]


def read_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"No leading frontmatter in {path}")
    data = yaml.safe_load(text.split("---", 2)[1])
    if not isinstance(data, dict):
        raise ValueError(f"Frontmatter in {path} is not a mapping")
    return data
