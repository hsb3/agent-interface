#!/usr/bin/env python3
# Adapted from google/elephant-goldfish-model scripts/pack_plugin.py (Apache-2.0); modified.
"""Build runtime folders and reproducible ZIPs without development files."""

import argparse
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

SHARED = (
    "plugin.json", "LICENSE", "README.md",
    "skills/*/SKILL.md", "skills/*/agents/openai.yaml",
    "skills/*/assets/*.svg", "skills/*/assets/*.png",
    "skills/*/references/**/*", "skills/*/scripts/**/*",
    "agents/*.md", "resources/**/*", "docs/*.md", "docs/assets/*.svg", "docs/assets/*.png",
    "assets/*.svg", "assets/*.png",
)
DEV_DOCS = {Path("docs/development.md"), Path("docs/testing.md")}
HOST = {
    "claude": (".claude-plugin/plugin.json", ".claude-plugin/icon.png",
               ".claude-plugin/agents/*.md"),
    "openai": (".codex-plugin/plugin.json",),
}
REQUIRED_SHARED = ("plugin.json", "LICENSE", "README.md", "assets/icon.svg", "resources/README.md",
                   "docs/claude.md", "docs/codex.md")
REQUIRED_PER_SKILL = ("SKILL.md", "agents/openai.yaml", "assets/icon.svg")
DISTRIBUTIONS = "distributions"


def build(root: Path, target: str, output: Path) -> tuple[Path, Path]:
    """Write a new runtime folder and ZIP; refuse unsafe inputs or overwrites."""
    root = root.resolve()
    name = json.loads((root / "plugin.json").read_text())["name"]
    folder = output.resolve() / f"{name}-{target}"
    archive = folder.with_suffix(".zip")
    if any(path.exists() or path.is_symlink() for path in (folder, archive)):
        raise ValueError("Output folder or ZIP already exists")
    if folder == root or root.is_relative_to(folder):
        raise ValueError("Output must not contain the source tree")
    files = set()
    for pattern in SHARED + HOST[target]:
        for path in root.glob(pattern):
            relative = path.relative_to(root)
            if any((root / Path(*relative.parts[:i])).is_symlink()
                   for i in range(1, len(relative.parts) + 1)):
                raise ValueError(f"Symlink in runtime path: {relative}")
            if not path.resolve().is_relative_to(root):
                raise ValueError(f"Path outside source: {relative}")
            hidden = any(part.startswith(".") for part in relative.parts[1:])
            if path.is_file() and not hidden and "__pycache__" not in relative.parts \
                    and relative not in DEV_DOCS:
                files.add(relative)
    skills = sorted(p.name for p in (root / "skills").glob("*")
                    if p.is_dir() and not p.name.startswith((".", "_")))
    required = REQUIRED_SHARED + (HOST[target][0],) + tuple(
        f"skills/{skill}/{item}" for skill in skills for item in REQUIRED_PER_SKILL)
    if not skills:
        raise ValueError("Missing required file: skills/*/SKILL.md")
    for required_name in required:
        if Path(required_name) not in files:
            raise ValueError(f"Missing required file: {required_name}")
    manifest = json.loads((root / HOST[target][0]).read_text())
    portable = json.loads((root / "plugin.json").read_text())
    openai = portable.get("extensions", {}).get("com.openai", {})
    if manifest.get("hooks") or portable.get("hooks") or openai.get("hooks"):
        raise ValueError("Runtime packages cannot contain hooks")
    for metadata in (manifest, portable, openai):
        if any(metadata.get(key) for key in ("mcpServers", "mcp", "apps")):
            raise ValueError("This runtime builder does not package MCP or app dependencies")
    references = list(manifest.get("agents", []))
    if target == "openai":
        interface = openai.get("interface") or manifest.get("interface", {})
        references += [interface[key] for key in ("composerIcon", "logo") if key in interface]
    elif "icon" in manifest:
        references.append(manifest["icon"])
    for reference in references:
        path = Path(reference)
        if path.is_absolute() or ".." in path.parts or path not in files:
            raise ValueError(f"Unbundled manifest reference: {reference}")
    output.mkdir(parents=True, exist_ok=True)
    folder.mkdir()
    with tempfile.TemporaryDirectory(prefix=".pack-", dir=output) as temporary:
        staged = Path(temporary) / archive.name
        with zipfile.ZipFile(staged, "x", zipfile.ZIP_DEFLATED) as bundle:
            for relative in sorted(files):
                data = (root / relative).read_bytes()
                # Keep the execute bit so bundled scripts still run after install.
                mode = 0o755 if (root / relative).stat().st_mode & 0o111 else 0o644
                destination = folder / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                destination.chmod(mode)
                info = zipfile.ZipInfo(relative.as_posix(), (1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (0o100000 | mode) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                bundle.writestr(info, data)
        # Linking the finished ZIP claims the final name without following a dangling symlink.
        archive.hardlink_to(staged)
    return folder, archive


def sync(root: Path) -> None:
    """Replace every checked-in distributions/<target> with a fresh build."""
    with tempfile.TemporaryDirectory() as temporary:
        # Build every target before replacing any, so a failure leaves distributions untouched.
        built = {target: build(root, target, Path(temporary))[0] for target in HOST}
        for target, folder in built.items():
            published = root / DISTRIBUTIONS / target
            if published.exists():
                shutil.rmtree(published)
            shutil.copytree(folder, published)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=HOST)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--sync", action="store_true",
                        help="Regenerate distributions/claude and distributions/openai")
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    if args.sync:
        sync(source)
        print(f"Synced {source / DISTRIBUTIONS}")
    elif args.target and args.output:
        runtime, bundle = build(source, args.target, args.output)
        print(f"Runtime: {runtime}\nZIP: {bundle}")
    else:
        parser.error("use --sync, or --target with --output")
