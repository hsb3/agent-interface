---
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Write, Bash]
---

Create these two files in the current directory with exactly this content.

`tool.py`:

```python
import argparse
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tool")
    nouns = parser.add_subparsers(dest="noun", required=True)

    label = nouns.add_parser("label").add_subparsers(dest="verb", required=True)
    label.add_parser("ls", help="list labels")

    issue = nouns.add_parser("issue").add_subparsers(dest="verb", required=True)
    issue.add_parser("ls", help="list open issues")
    issue.add_parser("all", help="list every issue")

    report = nouns.add_parser("report").add_subparsers(dest="verb", required=True)
    report.add_parser("frobnicate", help="rebuild the weekly report")

    config = nouns.add_parser("config").add_subparsers(dest="verb", required=True)
    set_value = config.add_parser("set", help="set a config value")
    set_value.add_argument("key")
    set_value.add_argument("value")

    args = parser.parse_args(argv)
    print(f"{args.noun} {args.verb}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`toolkit.json`:

```json
{
  "name": "tool",
  "surfaces": { "cli": "tool" },
  "tools": ["list_notes"]
}
```

Then check the command names of this toolkit: the CLI in tool.py and the MCP
tools in its catalog, toolkit.json.
