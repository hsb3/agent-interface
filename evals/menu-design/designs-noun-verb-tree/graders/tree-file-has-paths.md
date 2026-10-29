---
type: regex
pattern: '^(?=[\s\S]*\[\s*"issue",\s*"list"\s*\])[\s\S]*\[\s*"label",\s*"create"\s*\]'
target: { source: file, path: docs/cli-tree.json }
weight: 1
---
