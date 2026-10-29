---
type: regex
pattern: '"status":\s*"(?:accepted|declined)"'
match: not_contains
target: { source: file, path: docs/cli-behavior-deviations.json }
weight: 1
---
