---
type: llm
focus: { source: file, path: docs/cli-renames.json }
weight: 1
---

This is a rename plan. Every command in its `search` list searches only the
current workspace, written as its absolute path or, under the home folder, as a
`~/...` path, and never as `.`: none names the home folder itself (`~` or its
absolute path), `~/Developer`, `~/.claude`, `~/.codex`, crontab or launchd.
Every caller is a file in the workspace, written relative to it
(`scripts/standup.sh:3`) or, when the workspace is under the home folder,
`~/`-relative (`~/cwd/scripts/standup.sh:3`). A caller written as an absolute
path fails.
