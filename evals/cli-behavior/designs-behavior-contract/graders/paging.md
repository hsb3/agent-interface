---
type: regex
pattern: '^(?=[\s\S]*--limit)(?=[\s\S]*--cursor)(?=[\s\S]*next_cursor)(?=[\s\S]*has_more)'
target: { source: file, path: docs/cli-contract.md }
weight: 1
---
