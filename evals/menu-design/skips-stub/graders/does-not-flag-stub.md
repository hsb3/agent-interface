---
type: llm
weight: 1
---

The reply reports a check result for the CLI in tool.py, and it does not flag
`issue ls` in any way: not as a synonym, not as a collision with `issue list`,
and not as anything else. Mentioning that `issue ls` was skipped as a rename
stub is allowed; listing it as a finding is not. A reply that never reports a
check result fails.
