---
type: llm
weight: 1
---

The reply reports a behavior check whose failing findings include the
plain-text errors (an `error-object` failure, and possibly `stdout-data-only`
because a failure with `--json` leaves stdout empty), and offers no optional
change or deviation. Fail if the reply offers any optional change, such as
keeping plain-text errors.
