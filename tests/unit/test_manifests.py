# Adapted from google/elephant-goldfish-model tests/unit/test_harnesses.py (Apache-2.0); modified.
"""Portable, host and marketplace manifests agree and point at bundled files."""

import re
from xml.etree import ElementTree

import pytest
import yaml

from helpers import ROOT, frontmatter, read_json

SCHEMA_URL = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
NAME_RE = r"(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?"
HOST_MANIFESTS = (".claude-plugin/plugin.json", ".codex-plugin/plugin.json")
MARKETPLACES = {
    ".claude-plugin/marketplace.json": "distributions/claude",
    ".agents/plugins/marketplace.json": "distributions/openai",
}


def adapters() -> list:
    return sorted((ROOT / ".claude-plugin/agents").glob("*.md"))


def test_portable_manifest_schema() -> None:
    manifest = read_json("plugin.json")
    assert manifest["$schema"] == SCHEMA_URL
    assert re.fullmatch(NAME_RE, manifest["name"])
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"])


@pytest.mark.parametrize("path", HOST_MANIFESTS)
def test_host_metadata_matches_portable(path: str) -> None:
    canonical = read_json("plugin.json")
    manifest = read_json(path)
    for field in ("name", "version", "description"):
        assert manifest[field] == canonical[field], f"{path}: {field} drift"
    for field in ("author", "homepage", "repository", "license"):
        if field in manifest or field in canonical:
            assert manifest.get(field) == canonical.get(field), f"{path}: {field} drift"


def test_openai_listing_limits_and_assets() -> None:
    extension = read_json("plugin.json")["extensions"]["com.openai"]
    codex = read_json(".codex-plugin/plugin.json")
    assert extension["interface"] == codex["interface"], "OpenAI interface drift"
    assert (ROOT / codex["skills"]).resolve() == ROOT / "skills"
    interface = extension["interface"]
    assert interface["developerName"] == read_json("plugin.json")["author"]["name"]
    for field, limit in (("displayName", 30), ("shortDescription", 30),
                         ("longDescription", 4000), ("developerName", 80)):
        assert 0 < len(interface[field]) <= limit, field
    assert len(interface["capabilities"]) <= 20
    assert all(0 < len(item) <= 120 for item in interface["capabilities"])
    for field in ("composerIcon", "logo"):
        asset = (ROOT / interface[field]).resolve()
        assert asset.is_relative_to(ROOT / "assets") and asset.is_file(), field
        svg = ElementTree.parse(asset).getroot()
        assert float(svg.attrib["width"]) == float(svg.attrib["height"]) >= 48


def test_claude_and_codex_listing_fields_agree() -> None:
    interface = read_json("plugin.json")["extensions"]["com.openai"]["interface"]
    claude = read_json(".claude-plugin/plugin.json")
    codex_catalog = read_json(".agents/plugins/marketplace.json")
    assert claude["displayName"] == interface["displayName"]
    assert codex_catalog["interface"]["displayName"] == interface["displayName"]
    assert codex_catalog["plugins"][0]["category"] == interface["category"]
    for claude_key, openai_key in (("supportUrl", "supportURL"),
                                   ("privacyPolicyUrl", "privacyPolicyURL")):
        assert claude.get(claude_key) == interface.get(openai_key), claude_key


@pytest.mark.parametrize("path,source", MARKETPLACES.items())
def test_marketplace_points_at_generated_runtime(path: str, source: str) -> None:
    canonical = read_json("plugin.json")
    marketplace = read_json(path)
    assert marketplace["name"] == canonical["name"]
    assert len(marketplace["plugins"]) == 1
    entry = marketplace["plugins"][0]
    assert entry["name"] == canonical["name"]
    target = entry["source"] if isinstance(entry["source"], str) else entry["source"]["path"]
    assert (ROOT / target).resolve() == ROOT / source
    if "description" in entry:
        assert entry["description"] == canonical["description"]


def test_skill_picker_metadata(discovered_skills: list) -> None:
    for skill in discovered_skills:
        interface = yaml.safe_load((skill / "agents/openai.yaml").read_text())["interface"]
        assert interface["display_name"]
        assert 25 <= len(interface["short_description"]) <= 64, skill.name
        for field in ("icon_small", "icon_large"):
            svg = ElementTree.parse(skill / interface[field]).getroot()
            assert svg.get("viewBox") == "0 0 24 24", f"{skill.name}: {field}"
            assert svg.findtext("{http://www.w3.org/2000/svg}title"), f"{skill.name}: {field}"


def test_claude_adapters_are_registered_and_resolve() -> None:
    listed = read_json(".claude-plugin/plugin.json").get("agents", [])
    assert sorted(listed) == [f"./{p.relative_to(ROOT).as_posix()}" for p in adapters()]
    assert not any(entry.startswith("./agents/") for entry in listed), (
        "Register Claude adapters, not shared personas")


def test_every_persona_has_claude_adapter() -> None:
    missing = sorted({p.name for p in (ROOT / "agents").glob("*.md")}
                     - {p.name for p in adapters()})
    assert not missing, f"Add .claude-plugin/agents/ adapters for: {missing}"


@pytest.mark.parametrize("adapter", adapters(), ids=lambda p: p.stem)
def test_claude_adapter_wraps_its_persona(adapter) -> None:
    config = frontmatter(adapter)
    assert isinstance(config.get("tools"), list), "Adapters declare an explicit tool list"
    assert config["model"] == "inherit"
    assert "memory" not in config
    persona = ROOT / "agents" / adapter.name
    assert persona.is_file(), f"No shared persona for {adapter.name}"
    assert f"${{CLAUDE_PLUGIN_ROOT}}/agents/{adapter.name}" in adapter.read_text()
    canonical = frontmatter(persona)
    assert canonical["name"] == config["name"]
    assert "tools" not in canonical and "omitClaudeMd" not in canonical, (
        "Keep Claude-only fields in the adapter")
    if set(config["tools"]) <= {"Read", "Grep", "Glob"}:
        assert config.get("omitClaudeMd") is True, "Read-only reviewers start without CLAUDE.md"


def test_no_hooks_or_services_in_runtime_manifests() -> None:
    for path in ("plugin.json",) + HOST_MANIFESTS:
        manifest = read_json(path)
        openai = manifest.get("extensions", {}).get("com.openai", {})
        for metadata in (manifest, openai):
            assert not any(metadata.get(k) for k in ("hooks", "mcpServers", "mcp", "apps")), path
    assert not (ROOT / "hooks/hooks.json").exists()


def test_bundled_prompt_paths_resolve() -> None:
    prompts = list((ROOT / "skills").glob("*/SKILL.md")) + list((ROOT / "agents").glob("*.md"))
    prompts += list((ROOT / ".claude-plugin/agents").glob("*.md"))
    for prompt in prompts:
        text = prompt.read_text(encoding="utf-8")
        for target in re.findall(r"`(?:\$\{CLAUDE_PLUGIN_ROOT\}/)?((?:agents|docs|resources|skills)/[^`\s]+)`", text):
            assert (ROOT / target).is_file(), f"{prompt}: missing {target}"
        for target in re.findall(r"`(references/[^`\s]+)`", text):
            assert (prompt.parent / target).is_file(), f"{prompt}: missing {target}"
