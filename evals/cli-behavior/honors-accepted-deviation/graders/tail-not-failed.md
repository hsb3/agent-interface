---
type: regex
pattern: '\{(?=(?:"(?:[^"\\]|\\.)*"|\{(?:"(?:[^"\\]|\\.)*"|[^{}"])*\}|[^{}"])*?"rule":\s*"stdout-data-only")(?=(?:"(?:[^"\\]|\\.)*"|\{(?:"(?:[^"\\]|\\.)*"|[^{}"])*\}|[^{}"])*?"status":\s*"fail")(?=(?:"(?:[^"\\]|\\.)*"|\{(?:"(?:[^"\\]|\\.)*"|[^{}"])*\}|[^{}"])*?"item tail")'
match: not_contains
target: { source: file, path: docs/cli-behavior.json }
weight: 1
---
