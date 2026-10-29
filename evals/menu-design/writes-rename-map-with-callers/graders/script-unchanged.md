---
type: regex
pattern: '\ntool issue ls\n?$'
target: { source: file, path: scripts/standup.sh }
weight: 1
---
