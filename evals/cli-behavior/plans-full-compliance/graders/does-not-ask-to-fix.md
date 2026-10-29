---
type: llm
weight: 1
---

The reply reports the check and points to the plan without asking the user
whether to fix the CLI, whether to apply the plan, or whether to proceed.
Mentioning that the user may accept or decline an optional change is fine.
Fail if the reply asks whether the CLI should be fixed or the plan applied, or
offers to make the changes and waits for a yes.
