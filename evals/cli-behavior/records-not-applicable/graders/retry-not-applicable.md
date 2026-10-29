---
type: regex
pattern: '\{(?=(?:"(?:[^"\\]|\\.)*"|\{(?:"(?:[^"\\]|\\.)*"|[^{}"])*\}|[^{}"])*?"rule":\s*"idempotent-write")(?=(?:"(?:[^"\\]|\\.)*"|\{(?:"(?:[^"\\]|\\.)*"|[^{}"])*\}|[^{}"])*?"status":\s*"not_applicable")(?=(?:"(?:[^"\\]|\\.)*"|\{(?:"(?:[^"\\]|\\.)*"|[^{}"])*\}|[^{}"])*?"reason":)'
target: { source: file, path: docs/cli-behavior.json }
weight: 1
---
