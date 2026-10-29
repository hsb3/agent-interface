---
type: regex
pattern: '"status":\s*"fail"'
match: not_contains
target: { source: file, path: docs/cli-behavior.json }
weight: 1
---
