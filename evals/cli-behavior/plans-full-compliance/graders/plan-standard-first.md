---
type: llm
focus: { source: file, path: docs/cli-behavior-plan.md }
weight: 1
---

This is a behavior plan for a CLI whose `item list` prints a table. Its main
(full-compliance) part changes `item list` to the standard machine output
(`--json` with the `schema_version` / `ok` / `data` envelope, and paging), and
lists `scripts/count-open.sh` as a caller that the change breaks. Separately,
as an optional change and not as the plan, it offers keeping `item list`'s
table as the default output, with the reason for the option and the work it
takes. Fail if the plan keeps the table instead of adopting the standard
output, if it does not list `scripts/count-open.sh` as a broken caller, or if
it offers no optional change that keeps the table.
