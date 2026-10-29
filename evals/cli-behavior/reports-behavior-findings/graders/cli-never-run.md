---
type: tool_used
tool: Bash
input_match: '(?:python[\d.]*|uv run)\s+(?:-[A-Za-z]+\s+)*(?:\./)?tool\.py|[";&|]\s*\./tool\.py|python[\d.]*\s+(?:-[A-Za-z]+\s+)*-m\s+tool\b|\bimport\s+tool\b|from\s+tool\s+import'
min: 0
max: 0
weight: 1
---
