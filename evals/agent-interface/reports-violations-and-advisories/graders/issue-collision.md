---
type: llm
weight: 1
---

The reply reports a collision on `issue list`, because `issue ls` and `issue all`
would both be renamed to it. The reply proposes no new name for either `issue ls`
or `issue all`. Fail if the reply proposes renaming either one, to `issue list`
or to any other name such as `issue list --all`.
