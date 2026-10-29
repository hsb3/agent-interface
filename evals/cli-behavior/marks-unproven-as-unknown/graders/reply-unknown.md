---
type: llm
weight: 1
---

The reply reports whether `item list` returns every row when paging as unknown
(not proven by the source, because the cursor goes to a client library outside
the repository), and names a test that would settle it. Fail if the reply says
paging works, counts it as a pass, or reports it as a failing finding.
