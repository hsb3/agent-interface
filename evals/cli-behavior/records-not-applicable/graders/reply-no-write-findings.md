---
type: llm
weight: 1
---

The reply reports a behavior check of the CLI in tool.py. Its failing findings
do not include a missing `--dry-run` flag, missing retry safety or a missing
`--idempotency-key` (both commands only read data). Saying that those rules do
not apply is fine. Fail if either appears as a failing finding, or if the reply
reports no check result.
