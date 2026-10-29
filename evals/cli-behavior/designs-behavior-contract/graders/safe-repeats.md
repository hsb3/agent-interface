---
type: regex
pattern: '^(?=[\s\S]*--idempotency-key)(?=[\s\S]*(?:deleted|end state))(?=[\s\S]*--yes)'
target: { source: file, path: docs/cli-contract.md }
weight: 1
---
