---
type: regex
pattern: '\b(?:shall I|should I|do you want me to|want me to|would you like me to|like me to (?:apply|fix|make|implement|start)|ready to proceed|shall we proceed)\b'
flags: i
match: not_contains
target: last_message
weight: 1
---
