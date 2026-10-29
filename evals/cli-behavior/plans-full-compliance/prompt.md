---
max_turns: 80
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Create these files in the current directory with exactly this content.

`tool.py`:

```python
import argparse
import json
import sys

DATA = "items.json"


def load():
    with open(DATA) as f:
        return json.load(f)


def item_list(args):
    print(f"{'ID':<6}{'NAME':<24}STATUS")
    for row in load():
        print(f"{row['id']:<6}{row['name']:<24}{row['status']}")
    return 0


def item_delete(args):
    rows = load()
    kept = [row for row in rows if row["id"] != args.id]
    if len(kept) == len(rows):
        print(f"error: no item {args.id}", file=sys.stderr)
        return 1
    with open(DATA, "w") as f:
        json.dump(kept, f)
    print(f"deleted item {args.id}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tool")
    nouns = parser.add_subparsers(dest="noun", required=True)
    item = nouns.add_parser("item").add_subparsers(dest="verb", required=True)
    item.add_parser("list", help="list items").set_defaults(func=item_list)
    delete = item.add_parser("delete", help="delete an item")
    delete.add_argument("id", type=int)
    delete.set_defaults(func=item_delete)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
```

`scripts/count-open.sh`:

```sh
#!/bin/sh
# How many items are still open, for the daily report.
tool item list | awk 'NR > 1 && $3 == "open"' | wc -l
```

`scripts/prune.sh`:

```sh
#!/bin/sh
# Nightly: delete every closed item.
tool item list | awk 'NR > 1 && $3 == "closed" { print $1 }' | while read -r id; do tool item delete "$id"; done
```

Then check whether the CLI in tool.py is safe for agents to drive.
