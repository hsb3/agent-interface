---
type: llm
weight: 1
---

The reply lists `config set` as an advisory, not a violation, and says that the
owner must decide on it, for example by asking whether to keep `set`. The reply
proposes no new name for it. Saying that `set` is a possible synonym of `update`
is fine. Fail if the reply presents `config update`, or any other name, as the
rename for `config set`.
