---
type: regex
pattern: '\s(?:~|~/Developer|~/\.claude|~/\.codex|/Users/[^/\s\"]+|\.)/?(?=[\s)''"\\]|$)|crontab|launchd|"callers":\s*\[[^\]]*"/'
match: not_contains
target: { source: file, path: docs/cli-renames.json }
weight: 1
---
