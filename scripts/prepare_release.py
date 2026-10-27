#!/usr/bin/env python3
# Adapted from google/elephant-goldfish-model scripts/prepare_release.py (Apache-2.0); modified.
"""Build versioned runtime archives and a checksum manifest for a draft release."""

import argparse
import hashlib
import json
from pathlib import Path
import re

from pack_plugin import HOST, build

MANIFESTS = ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json")


def version_for_tag(root: Path, tag: str) -> str:
    """Return the tag's version after checking every shipped manifest agrees with it."""
    if not re.fullmatch(r"v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", tag):
        raise ValueError("Tag must be vMAJOR.MINOR.PATCH without leading zeroes")
    version = tag[1:]
    for relative in MANIFESTS:
        manifest = json.loads((root / relative).read_text(encoding="utf-8"))
        if manifest.get("version") != version:
            raise ValueError(f"{relative}: version must match {tag}")
    return version


def prepare(root: Path, tag: str, output: Path, commit: str) -> None:
    """Write archives, SHA256SUMS and draft notes into a new directory.

    `commit` is the caller's declaration of source identity; only the release
    workflow verifies it against the tag.
    """
    version = version_for_tag(root, tag)
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Source commit must be a full Git SHA")
    portable = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
    name = portable["name"]
    slug = portable.get("repository", "").removeprefix("https://github.com/")
    output.mkdir(parents=True, exist_ok=False)
    checksums = []
    for target in HOST:
        _, archive = build(root, target, output / "build")
        destination = output / f"{name}-{target}-{version}.zip"
        archive.rename(destination)
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        checksums.append(f"{digest}  {destination.name}\n")
    (output / "SHA256SUMS").write_text("".join(checksums), encoding="utf-8")
    (output / "RELEASE_NOTES.md").write_text(
        f"# {name} {version}\n\nDeclared source: `{commit}`\nTag: `{tag}`\n\n"
        "Local source identity is caller-supplied and is not verified by this script. "
        "Publish only workflow-built candidates after exact-artifact checks.\n\n"
        "Verify downloads with `sha256sum -c SHA256SUMS`, then each ZIP with "
        f"`gh attestation verify FILE --repo {slug} "
        f"--signer-workflow {slug}/.github/workflows/release.yml --source-ref refs/heads/main`.\n\n"
        "## Changes\n\nOwner: summarize changes and migration steps before publishing.\n\n"
        "## Verification\n\nOffline unit tests and runtime packaging are checked by CI. "
        "Live installation and workflow execution are not established by this build. "
        "Owner: attach host evidence from TESTING.md before publishing.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepare(Path(__file__).resolve().parents[1], args.tag, args.output, args.commit)
