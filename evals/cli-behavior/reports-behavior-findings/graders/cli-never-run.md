---
type: tool_used
tool: Bash
input_match: '(?:python[\d.]*|uv run)\s+(?:-[A-Za-z]+\s+)*(?:\\?["''])?(?:[^\s"'';&|]*/)?tool\.py\b|(?:^|[";&|(]|\\")\s*(?:[^\s"'';&|]*/)tool\.py\b|python[\d.]*\s+(?:-[A-Za-z]+\s+)*-m\s+tool\b|\bimport\s+tool\b|from\s+tool\s+import|(?:exec|runpy)[^"]*tool\.py'
min: 0
max: 0
weight: 1
---
