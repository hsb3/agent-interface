---
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Write, Bash]
---

Create tool.py with exactly this content:

```python
import argparse
import sys


def issue_ls(args):
    print("renamed to: tool issue list", file=sys.stderr)
    sys.exit(2)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tool")
    sub = parser.add_subparsers(dest="noun", required=True)

    issue = sub.add_parser("issue", help="work with issues")
    issue_sub = issue.add_subparsers(dest="verb", required=True, metavar="{list,get}")
    issue_sub.add_parser("list", help="list issues")
    issue_sub.add_parser("get", help="get one issue")
    ls = issue_sub.add_parser("ls")
    ls.set_defaults(func=issue_ls)

    args = parser.parse_args(argv)
    if getattr(args, "func", None):
        args.func(args)
    return args


if __name__ == "__main__":
    main()
```

Then check the command names of the CLI in tool.py.
