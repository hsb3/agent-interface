---
type: llm
focus: { source: file, path: docs/cli-behavior.json }
weight: 1
---

This is a behavior results file. The result whose `rule` is `paged-list` and
whose `commands` include `item list` has `status` `unknown`, and its `test`
reads more rows than one page holds (for example 250 rows at `--limit 20`) and
checks that every row appears once. Fail if that result's status is `pass` or
`fail`, or if its test does not read past the first page.
