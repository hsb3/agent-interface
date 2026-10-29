---
type: llm
focus: { source: file, path: docs/cli-behavior-plan.md }
weight: 1
---

This is a behavior plan for a CLI whose failures are printed as plain text.
Its main part fixes the errors to the standard error object. It offers no
optional change or deviation: an empty optional-changes section, or a
statement that there are none, is fine. Fail if it offers any optional change,
such as keeping plain-text errors.
