---
type: regex
pattern: '\\*"severity\\*":\s*\\*"violation\\*",(?:\s|\\+n)*\\*"path'
match: not_contains
target: trace
weight: 1
---
