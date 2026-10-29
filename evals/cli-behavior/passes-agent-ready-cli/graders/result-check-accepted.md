---
type: llm
focus: trace
weight: 1
---

The last run of `behavior.py result check` printed an envelope with `"ok": true`.
Fail if no run of `behavior.py result check` appears, or if the last one printed
`"ok": false` (for example `INVALID_ARGUMENT`).
