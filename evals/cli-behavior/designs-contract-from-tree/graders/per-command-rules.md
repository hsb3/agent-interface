---
type: regex
pattern: '^(?=[\s\S]*--cursor)(?=[\s\S]*--idempotency-key)(?=[\s\S]*--yes)(?=[\s\S]*CONFIRMATION_REQUIRED)'
target: { source: file, path: docs/cli-contract.md }
weight: 1
---
