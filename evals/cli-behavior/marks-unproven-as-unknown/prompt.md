---
max_turns: 60
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Create tool.py with exactly this content:

```python
import argparse
import json
import sys

from itemstore import Client


def item_list(args):
    if not 1 <= args.limit <= 100:
        error = {"code": "INVALID_ARGUMENT", "message": "--limit must be from 1 to 100", "retryable": False, "next_action": "run again with --limit 100 or less"}
        if args.json:
            print(json.dumps({"schema_version": 1, "ok": False, "error": error}))
        else:
            print(error["message"], file=sys.stderr)
        return 2
    client = Client()
    page = client.list_items(cursor=args.cursor, limit=args.limit)
    if not args.json:
        for row in page.items:
            print(row["name"])
        return 0
    envelope = {
        "schema_version": 1,
        "ok": True,
        "data": page.items,
        "page": {"next_cursor": page.next_cursor, "has_more": page.next_cursor is not None},
    }
    print(json.dumps(envelope))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tool")
    nouns = parser.add_subparsers(dest="noun", required=True)
    item = nouns.add_parser("item").add_subparsers(dest="verb", required=True)
    list_cmd = item.add_parser("list", help="list items")
    list_cmd.add_argument("--json", action="store_true")
    list_cmd.add_argument("--cursor")
    list_cmd.add_argument("--limit", type=int, default=20)
    list_cmd.set_defaults(func=item_list)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
```

Then check whether the CLI in tool.py is safe for agents to drive. The `itemstore` package is a client library that is not in this repository.
