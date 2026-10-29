---
type: regex
pattern: '^(?=[\s\S]*retryable)(?=[\s\S]*INVALID_ARGUMENT)(?=[\s\S]*CONFIRMATION_REQUIRED)(?=[\s\S]*NOT_FOUND)(?=[\s\S]*CONFLICT)(?=[\s\S]*UNAUTHENTICATED)(?=[\s\S]*PERMISSION_DENIED)(?=[\s\S]*RATE_LIMITED)(?=[\s\S]*UNAVAILABLE)(?=[\s\S]*TIMEOUT)(?=[\s\S]*INTERNAL)'
target: { source: file, path: docs/cli-contract.md }
weight: 1
---
