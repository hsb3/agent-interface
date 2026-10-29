---
type: regex
pattern: '^(?=[\s\S]*stdin closed)(?=[\s\S]*250[^\n]*--limit 20)'
target: { source: file, path: docs/cli-contract.md }
weight: 1
---
