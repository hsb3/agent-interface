---
type: regex
pattern: '^(?=[\s\S]*schema_version)(?=[\s\S]*"ok":\s*true)(?=[\s\S]*"ok":\s*false)(?=[\s\S]*next_action)'
target: { source: file, path: docs/cli-contract.md }
weight: 1
---
