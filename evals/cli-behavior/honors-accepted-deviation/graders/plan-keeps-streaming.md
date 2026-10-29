---
type: llm
focus: { source: file, path: docs/cli-behavior-plan.md }
weight: 1
---

This is a behavior plan. It proposes no change to `item tail`'s streaming
output (one envelope per line, until interrupted). Naming it as an accepted
deviation is fine. Fail if any fix in the plan makes `item tail` return one
JSON document, stop streaming, or otherwise changes its streaming output.
