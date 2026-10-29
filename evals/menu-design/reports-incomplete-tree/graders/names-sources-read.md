---
type: regex
pattern: '^(?![\s\S]*"ref":\s*"[^"]*tool_admin)[\s\S]*"ref":\s*"(?:\./)?tool\.py"'
target: { source: file, path: docs/cli-tree.json }
weight: 1
---
