---
type: llm
weight: 1
---

The reply reports a check result for the CLI in tool.py (for example a count of
violations and advisories, or a statement that nothing was found), and it
reports no violation because the commands `list`, `get` and `create` lack a
noun level. A reply that never reports a check result fails.
