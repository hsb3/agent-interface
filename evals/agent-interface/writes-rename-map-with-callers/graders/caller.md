---
type: llm
weight: 1
---

In `docs/cli-renames.json`, the callers of the `issue ls` rename include the
script's location as `file:line`, ending in `scripts/standup.sh:3`. Line 3 is the
line that runs `tool issue ls`. A different line number, or no entry for that
script, fails.
