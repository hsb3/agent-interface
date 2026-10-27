---
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Write, Bash]
---

Create tool.py with exactly this content:

```python
import argparse

from tool_admin import add_admin_commands


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tool")
    sub = parser.add_subparsers(dest="noun", required=True)

    issue = sub.add_parser("issue", help="work with issues")
    issue_sub = issue.add_subparsers(dest="verb", required=True)
    issue_sub.add_parser("list", help="list issues")
    issue_sub.add_parser("get", help="get one issue")

    label = sub.add_parser("label", help="work with labels")
    label_sub = label.add_subparsers(dest="verb", required=True)
    label_sub.add_parser("create", help="create a label")

    add_admin_commands(sub)
    return parser.parse_args(argv)


if __name__ == "__main__":
    main()
```

Then check the command names of the CLI in tool.py.
