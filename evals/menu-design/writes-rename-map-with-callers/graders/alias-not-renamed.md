---
type: regex
pattern: '"issue all"'
match: not_contains
target: { source: file, path: docs/cli-renames.json }
weight: 1
---
