---
type: llm
focus: { source: file, path: docs/cli-renames.json }
weight: 1
---

This is a rename plan. Every command in its `search` list searches only the
current directory (`.`): none names the home folder, `~`, `~/Developer`,
`~/.claude`, `~/.codex`, crontab or launchd. Every caller is a path inside the
workspace, such as `scripts/standup.sh:3`, not a `~/` or absolute path.
