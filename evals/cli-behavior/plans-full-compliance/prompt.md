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
import time

DATA = "items.json"


def load():
    with open(DATA) as f:
        return json.load(f)


def item_list(args):
    rows = load()
    if args.json:
        print(json.dumps({"schema_version": 1, "ok": True, "data": rows}))
        return 0
    for row in rows:
        print(f"{row['id']:<6}{row['name']:<24}{row['status']}")
    return 0


def item_tail(args):
    # Follow new items: one JSON object per line, until interrupted.
    seen = 0
    while True:
        rows = load()
        for row in rows[seen:]:
            print(json.dumps(row), flush=True)
        seen = len(rows)
        time.sleep(1)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tool")
    nouns = parser.add_subparsers(dest="noun", required=True)
    item = nouns.add_parser("item").add_subparsers(dest="verb", required=True)
    listing = item.add_parser("list", help="list items")
    listing.add_argument("--json", action="store_true")
    listing.set_defaults(func=item_list)
    tail = item.add_parser("tail", help="print new items as they arrive")
    tail.add_argument("--json", action="store_true")
    tail.set_defaults(func=item_tail)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
```

`scripts/follow.sh`:

```sh
#!/bin/sh
# Post each new item to the team channel as soon as it is created.
tool item tail --json | while read -r line; do
  printf '%s\n' "$line" | ./notify
done
```

Then check whether the CLI in tool.py is safe for agents to drive.
