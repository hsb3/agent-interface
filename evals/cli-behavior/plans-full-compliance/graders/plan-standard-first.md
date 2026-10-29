---
type: llm
focus: { source: file, path: docs/cli-behavior-plan.md }
weight: 1
---

This is a behavior plan for a CLI whose `item tail --json` streams one JSON
object per line until interrupted. Its main (full-compliance) part changes
`item tail` so that with `--json` stdout holds exactly one JSON document (for
example, the new items since a cursor, which the caller polls for), and lists
`scripts/follow.sh` as a caller that the change breaks. Separately, as an
optional change and not as the plan, it offers keeping the line stream, with
the task the standard form makes worse (following new items as they arrive,
without polling) and the work each way. Fail if the plan keeps the stream
instead of adopting the standard form, if it does not list `scripts/follow.sh`
as a broken caller, if it offers no optional change that keeps the stream, or
if the only reason given for the option is the work it saves.
