---
type: llm
weight: 1
---

The reply reports `item tail`'s streaming output as an accepted deviation, not
as a failing finding, and gives the reason recorded in the register: its task
(follow an item's events while a deploy runs) or its harm (one JSON document
can only be printed when the command ends, and item tail runs until
interrupted, so the agent would see no event until it stopped the command).
Fail if the reply lists `item tail`'s streaming as a failing finding, or gives
neither the task nor the harm.
