---
type: llm
weight: 1
---

The reply reports `item tail`'s streaming output as an accepted deviation, not
as a failing finding, and gives its reason: `item tail` runs until interrupted,
so one JSON document would show the agent no event until the command stopped
(following an item's events during a deploy). Fail if the reply lists
`item tail`'s streaming as a failing finding, or omits the reason.
