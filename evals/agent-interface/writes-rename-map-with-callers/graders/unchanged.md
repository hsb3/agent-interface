---
type: llm
weight: 1
---

At the end of the run, `tool.py` and `scripts/standup.sh` still have exactly the
content the prompt gave them. The agent did not edit, overwrite, move or delete
either file. For example, it did not rename `ls` to `list`, add a stub command,
or change the script's `tool issue ls` line.
