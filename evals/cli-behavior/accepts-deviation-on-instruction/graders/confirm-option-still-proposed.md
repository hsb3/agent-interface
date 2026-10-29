---
type: regex
pattern: '\{(?=(?:"(?:[^"\\]|\\.)*"|\{(?:"(?:[^"\\]|\\.)*"|[^{}"])*\}|[^{}"])*?"command":\s*"item delete")(?=(?:"(?:[^"\\]|\\.)*"|\{(?:"(?:[^"\\]|\\.)*"|[^{}"])*\}|[^{}"])*?"rule":\s*"confirm-flag")(?=(?:"(?:[^"\\]|\\.)*"|\{(?:"(?:[^"\\]|\\.)*"|[^{}"])*\}|[^{}"])*?"status":\s*"proposed")'
target: { source: file, path: docs/cli-behavior-deviations.json }
weight: 1
---
