---
type: regex
pattern: '\{(?=(?:"(?:[^"\\]|\\.)*"|\{(?:"(?:[^"\\]|\\.)*"|[^{}"])*\}|[^{}"])*?"old":\s*"issue ls")(?=(?:"(?:[^"\\]|\\.)*"|\{(?:"(?:[^"\\]|\\.)*"|[^{}"])*\}|[^{}"])*?"new":\s*"issue list")'
target: { source: file, path: docs/cli-renames.json }
weight: 1
---
