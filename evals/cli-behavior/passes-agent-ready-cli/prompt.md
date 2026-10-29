---
max_turns: 60
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Create tool.py with exactly this content:

```python
import argparse
import json
import os
import sys

STORE = "store.json"
CODES = {
    "INVALID_ARGUMENT": (False, 2),
    "NOT_FOUND": (False, 1),
    "CONFLICT": (False, 1),
    "INTERNAL": (False, 1),
}


class Failure(Exception):
    def __init__(self, code, message, next_action):
        super().__init__(message)
        self.code = code
        self.next_action = next_action


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Failure("INVALID_ARGUMENT", message, "run `tool item <verb> --help` and fix the arguments")


def emit(envelope):
    sys.stdout.write(json.dumps(envelope) + "\n")


def succeed(data, page=None):
    envelope = {"schema_version": 1, "ok": True, "data": data}
    if page is not None:
        envelope["page"] = page
    emit(envelope)
    return 0


def fail(code, message, next_action):
    retryable, status = CODES[code]
    error = {"code": code, "message": message, "retryable": retryable, "next_action": next_action}
    emit({"schema_version": 1, "ok": False, "error": error})
    return status


def load():
    try:
        with open(STORE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"items": [], "keys": {}}


def save(store):
    with open(STORE + ".tmp", "w") as f:
        json.dump(store, f)
    os.replace(STORE + ".tmp", STORE)


def item_list(args):
    if not 1 <= args.limit <= 100:
        raise Failure("INVALID_ARGUMENT", "--limit must be from 1 to 100", "run again with --limit 100 or less")
    try:
        after = int(args.cursor) if args.cursor else 0
    except ValueError:
        raise Failure("INVALID_ARGUMENT", "--cursor is not a cursor from this command", "run again without --cursor")
    rows = sorted((r for r in load()["items"] if r["id"] > after), key=lambda r: r["id"])
    page = rows[: args.limit]
    next_cursor = str(page[-1]["id"]) if len(rows) > args.limit else None
    return succeed(page, {"next_cursor": next_cursor, "has_more": next_cursor is not None})


def item_get(args):
    for row in load()["items"]:
        if row["id"] == args.id:
            return succeed(row)
    raise Failure("NOT_FOUND", f"no item {args.id}", "run `tool item list` to find the id")


def item_create(args):
    store = load()
    request = {"name": args.name}
    if args.idempotency_key in store["keys"]:
        first = store["keys"][args.idempotency_key]
        if first["request"] != request:
            raise Failure("CONFLICT", "idempotency key reused with other arguments", "use a new --idempotency-key")
        return succeed(first["result"])
    row = {"id": max((r["id"] for r in store["items"]), default=0) + 1, "name": args.name}
    if args.dry_run:
        return succeed({"would_create": row})
    store["items"].append(row)
    if args.idempotency_key:
        store["keys"][args.idempotency_key] = {"request": request, "result": row}
    save(store)
    return succeed(row)


def build_parser():
    parser = Parser(prog="tool")
    nouns = parser.add_subparsers(dest="noun", required=True)
    item = nouns.add_parser("item").add_subparsers(dest="verb", required=True)
    list_cmd = item.add_parser("list", help="list items")
    list_cmd.add_argument("--limit", type=int, default=20)
    list_cmd.add_argument("--cursor")
    list_cmd.set_defaults(func=item_list)
    get = item.add_parser("get", help="show one item")
    get.add_argument("id", type=int)
    get.set_defaults(func=item_get)
    create = item.add_parser("create", help="create an item")
    create.add_argument("--name", required=True)
    create.add_argument("--idempotency-key")
    create.add_argument("--dry-run", action="store_true")
    create.set_defaults(func=item_create)
    return parser


def main(argv=None):
    try:
        args = build_parser().parse_args(argv)
        print(f"tool: running item {args.verb}", file=sys.stderr)
        return args.func(args)
    except Failure as exc:
        return fail(exc.code, str(exc), exc.next_action)
    except Exception as exc:
        return fail("INTERNAL", f"unexpected error: {exc}", "report this error with the command you ran")


if __name__ == "__main__":
    sys.exit(main())
```

Then check whether the CLI in tool.py is safe for agents to drive.
