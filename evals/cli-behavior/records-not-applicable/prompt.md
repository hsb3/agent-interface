---
max_turns: 60
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Create tool.py with exactly this content:

```python
import argparse
import json
import sys

DATA = "items.json"


def load():
    with open(DATA) as f:
        return json.load(f)


def item_list(args):
    for row in load():
        print(f"{row['id']}\t{row['name']}")
    return 0


def item_get(args):
    for row in load():
        if row["id"] == args.id:
            print(json.dumps(row, indent=2))
            return 0
    print(f"no item {args.id}", file=sys.stderr)
    return 1


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tool")
    nouns = parser.add_subparsers(dest="noun", required=True)
    item = nouns.add_parser("item").add_subparsers(dest="verb", required=True)
    item.add_parser("list", help="list items").set_defaults(func=item_list)
    get = item.add_parser("get", help="show one item")
    get.add_argument("id", type=int)
    get.set_defaults(func=item_get)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
```

Then check whether the CLI in tool.py is safe for agents to drive.
