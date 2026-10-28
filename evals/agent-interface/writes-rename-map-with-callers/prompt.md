---
max_turns: 40
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Create these two files in the current directory with exactly this content.

`tool.py`:

```python
import argparse
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tool")
    nouns = parser.add_subparsers(dest="noun", required=True)

    issue = nouns.add_parser("issue").add_subparsers(dest="verb", required=True)
    issue.add_parser("ls", help="list open issues")
    get = issue.add_parser("get", help="show one issue")
    get.add_argument("id")

    args = parser.parse_args(argv)
    print(f"{args.noun} {args.verb}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`scripts/standup.sh`:

```sh
#!/bin/sh
echo "Open issues:"
tool issue ls
```

Then fix the command names in the CLI in tool.py. For callers, search only this
workspace, the current directory.
