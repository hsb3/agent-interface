---
max_turns: 40
allowed_tools: [Read, Glob, Grep, Skill, Write, Bash]
---

Create docs/cli-tree.json with exactly this content:

```json
{
  "cli": "tracker",
  "sources": [
    {
      "kind": "source",
      "ref": "tracker/cli.py"
    }
  ],
  "complete": true,
  "commands": [
    {
      "path": [
        "issue",
        "list"
      ],
      "mcp_name": null,
      "kind": "command",
      "source": "tracker/cli.py"
    },
    {
      "path": [
        "issue",
        "create"
      ],
      "mcp_name": null,
      "kind": "command",
      "source": "tracker/cli.py"
    },
    {
      "path": [
        "label",
        "delete"
      ],
      "mcp_name": null,
      "kind": "command",
      "source": "tracker/cli.py"
    }
  ]
}
```

Then design how the tracker CLI should behave when an agent drives it. Its commands are in docs/cli-tree.json.
