---
type: regex
pattern: '\{(?=(?:"(?:[^"\\]|\\.)*"|\{(?:"(?:[^"\\]|\\.)*"|[^{}"])*\}|[^{}"])*?"rule":\s*"error-object")(?=(?:"(?:[^"\\]|\\.)*"|\{(?:"(?:[^"\\]|\\.)*"|[^{}"])*\}|[^{}"])*?"status":\s*"fail")'
target: { source: file, path: docs/cli-behavior.json }
weight: 1
---
