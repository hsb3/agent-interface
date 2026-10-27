---
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Write, Bash]
---

Create tool.py with exactly this content:

```python
import argparse


def main(argv=None):
    parser = argparse.ArgumentParser(prog="notes")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list notes")
    get = sub.add_parser("get", help="show one note")
    get.add_argument("id")
    create = sub.add_parser("create", help="make a note")
    create.add_argument("title")
    return parser.parse_args(argv)


if __name__ == "__main__":
    main()
```

Then check the command names of the CLI in tool.py.
