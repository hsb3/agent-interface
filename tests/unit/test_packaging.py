# Adapted from google/elephant-goldfish-model tests/unit/test_packaging.py (Apache-2.0); modified.
"""Runtime packages hold exactly the shipped files, safely and reproducibly."""

import json
from pathlib import Path
import re
import runpy
import shutil
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACK = runpy.run_path(str(ROOT / "scripts/pack_plugin.py"))
build = PACK["build"]
NAME = json.loads((ROOT / "plugin.json").read_text())["name"]
SKILL = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))[0]
SOURCE_ITEMS = ("plugin.json", "LICENSE", "README.md", "AGENTS.md", "skills", "agents", "resources",
                "docs", "assets", "evals", "openspec", ".claude-plugin", ".codex-plugin", ".agents")


@pytest.fixture
def source(tmp_path: Path) -> Path:
    root = tmp_path / "source"
    root.mkdir()
    for name in SOURCE_ITEMS:
        if (ROOT / name).is_dir():
            shutil.copytree(ROOT / name, root / name,
                            ignore=shutil.ignore_patterns("__pycache__", "results"))
        elif (ROOT / name).exists():
            shutil.copyfile(ROOT / name, root / name)
    return root


def contents(folder: Path) -> dict[str, bytes]:
    return {p.relative_to(folder).as_posix(): p.read_bytes()
            for p in folder.rglob("*") if p.is_file()}


@pytest.mark.parametrize("target", ["claude", "openai"])
def test_runtime_is_complete_reproducible_and_lean(
    source: Path, tmp_path: Path, target: str,
) -> None:
    for name in ("tests/secret.txt", ".github/workflows/a.yml", "hooks/run.sh",
                 "assets/private.txt", "docs/designs/idea.md", "bin/gate", "openspec/specs/x/spec.md",
                 f"skills/{SKILL}/references/.env", f"skills/{SKILL}/scripts/.DS_Store"):
        file = source / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("must not ship")
    nested = source / f"skills/{SKILL}/references/nested/deep.md"
    nested.parent.mkdir(parents=True)
    nested.write_text("# Deep\n")
    script = source / f"skills/{SKILL}/scripts/run.sh"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text("#!/bin/sh\n")
    script.chmod(0o755)
    first, archive = build(source, target, tmp_path / "first")
    _, repeated = build(source, target, tmp_path / "second")
    assert archive.read_bytes() == repeated.read_bytes()
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        names = set(bundle.namelist())
        skills = {p.parent.name for p in source.glob("skills/*/SKILL.md")}
        assert {n.split("/")[1] for n in names if n.endswith("/SKILL.md")} == skills
        for image in re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', bundle.read("README.md").decode()):
            assert image in names, f"Unbundled README image: {image}"
        assert not any(n.startswith(("tests/", ".github/", ".agents/", "evals/", "bin/",
                                     "docs/designs/", "hooks/", "distributions/", "openspec/"))
                       or n.endswith("marketplace.json") for n in names)
        assert not names & {"AGENTS.md", "docs/testing.md", "docs/development.md", "assets/private.txt"}
        assert (".claude-plugin/plugin.json" in names) == (target == "claude")
        has_adapters = any(source.glob(".claude-plugin/agents/*.md"))
        assert any(n.startswith(".claude-plugin/agents/") for n in names) == (
            target == "claude" and has_adapters)
        assert (".codex-plugin/plugin.json" in names) == (target == "openai")
        for info in bundle.infolist():
            assert info.date_time == (1980, 1, 1, 0, 0, 0)
            executable = (source / info.filename).stat().st_mode & 0o111
            assert info.external_attr >> 16 == (0o100755 if executable else 0o100644)
            assert bundle.read(info) == (first / info.filename).read_bytes()
        assert f"skills/{SKILL}/references/nested/deep.md" in names
        assert bundle.getinfo(f"skills/{SKILL}/scripts/run.sh").external_attr >> 16 == 0o100755
        assert not any(Path(n).name in (".env", ".DS_Store") for n in names)
    check_links = runpy.run_path(str(ROOT / "tests/unit/test_link_integrity.py"))[
        "test_relative_markdown_links_resolve_on_disk"]
    check_links(first)


@pytest.mark.parametrize("directory", [False, True])
def test_rejects_symlinked_runtime_paths(source: Path, tmp_path: Path, directory: bool) -> None:
    victim = source / ("docs" if directory else "assets/icon.svg")
    outside = tmp_path / "outside"
    shutil.move(str(victim), outside)
    victim.symlink_to(outside, target_is_directory=directory)
    with pytest.raises(ValueError, match="Symlink"):
        build(source, "openai", tmp_path / "output")


@pytest.mark.parametrize("reference", ["../escape.svg", "/tmp/icon.svg", "./assets/missing.svg"])
def test_rejects_escaping_or_missing_manifest_assets(
    source: Path, tmp_path: Path, reference: str,
) -> None:
    path = source / "plugin.json"
    manifest = json.loads(path.read_text())
    manifest["extensions"]["com.openai"]["interface"]["logo"] = reference
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="Unbundled"):
        build(source, "openai", tmp_path / "output")


def test_refuses_hooks_and_overwrites(source: Path, tmp_path: Path) -> None:
    output = tmp_path / "output"
    build(source, "claude", output)
    with pytest.raises(ValueError, match="already exists"):
        build(source, "claude", output)
    path = source / ".claude-plugin/plugin.json"
    manifest = json.loads(path.read_text())
    manifest["hooks"] = {"PreToolUse": []}
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="hooks"):
        build(source, "claude", tmp_path / "other")


@pytest.mark.parametrize("field", ["apps", "mcpServers"])
def test_refuses_unbundled_services(source: Path, tmp_path: Path, field: str) -> None:
    path = source / "plugin.json"
    manifest = json.loads(path.read_text())
    manifest["extensions"]["com.openai"][field] = "./missing.json"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="dependencies"):
        build(source, "openai", tmp_path / "output")


@pytest.mark.parametrize("target", ["claude", "openai"])
@pytest.mark.parametrize("missing", [
    "skills", f"skills/{SKILL}/SKILL.md", f"skills/{SKILL}/agents/openai.yaml",
    f"skills/{SKILL}/assets/icon.svg", "LICENSE", "resources/README.md", "docs/claude.md", "docs/codex.md", "assets/icon.svg",
])
def test_incomplete_source_fails_before_output(
    source: Path, tmp_path: Path, target: str, missing: str,
) -> None:
    path = source / missing
    if path.is_dir():
        shutil.rmtree(path)
        path.mkdir()
    else:
        path.unlink()
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="Missing required file"):
        build(source, target, output)
    assert not output.exists()


@pytest.mark.parametrize("target", ["claude", "openai"])
@pytest.mark.parametrize("suffix", ["", ".zip"])
def test_rejects_dangling_output_symlinks(
    source: Path, tmp_path: Path, target: str, suffix: str,
) -> None:
    output = tmp_path / "output"
    output.mkdir()
    outside = tmp_path / "outside"
    link = output / f"{NAME}-{target}{suffix}"
    link.symlink_to(outside, target_is_directory=not suffix)
    with pytest.raises(ValueError, match="already exists"):
        build(source, target, output)
    assert not outside.exists()
    assert list(output.iterdir()) == [link]


@pytest.mark.parametrize("target", ["claude", "openai"])
def test_published_runtime_is_current(tmp_path: Path, target: str) -> None:
    """Marketplaces install distributions/<target>; it must equal a fresh build."""
    generated, _ = build(ROOT, target, tmp_path)
    published = ROOT / "distributions" / target
    assert contents(published) == contents(generated), (
        "Run python3 scripts/pack_plugin.py --sync")
