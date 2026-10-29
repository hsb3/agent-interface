---
type: llm
weight: 1
---

The reply reports the result of a check of how the `tool` CLI behaves for
agents, says that its command names were not checked, and gives the request
the user can make to check them (for example "check the command names of the
CLI in tool.py"). Fail if the reply never says the names were not checked, if
it reports naming findings as if names were checked, or if it gives no request
for checking them.
