---
max_turns: 40
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
    print("Loading items...")
    items = load()
    print(f"{'ID':<6}NAME")
    for item in items[:50]:
        print(f"{item['id']:<6}{item['name']}")
    print("Done.")
    return 0


def item_delete(args):
    items = load()
    answer = input("Are you sure? [y/N] ")
    if answer.strip().lower() != "y":
        print("Cancelled.")
        return 1
    kept = [item for item in items if item["id"] != args.id]
    if len(kept) == len(items):
        print(f"Error: item {args.id} not found")
        return 1
    with open(DATA, "w") as f:
        json.dump(kept, f)
    print(f"Deleted item {args.id}.")
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
    try:
        return args.func(args)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

Then check whether the errors and output of the CLI in tool.py are safe for an agent to drive.
