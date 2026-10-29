---
max_turns: 60
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Create these files in the current directory with exactly this content.

`tool.py`:

```python
import argparse
import json
import sys
import time

EVENTS = "events.log"


class Failure(Exception):
    def __init__(self, code, message, next_action, status):
        super().__init__(message)
        self.code = code
        self.next_action = next_action
        self.status = status


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Failure("INVALID_ARGUMENT", message, "run `tool item <verb> --help` and fix the arguments", 2)


def emit(envelope):
    sys.stdout.write(json.dumps(envelope) + "\n")
    sys.stdout.flush()


def read_events():
    try:
        with open(EVENTS) as f:
            return [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return []


def item_get(args):
    events = [e for e in read_events() if e["item"] == args.id]
    if not events:
        raise Failure("NOT_FOUND", f"no item {args.id}", "run `tool item tail <id>` on a known id", 1)
    emit({"schema_version": 1, "ok": True, "data": events[-1]})
    return 0


def item_tail(args):
    with open(EVENTS) as f:
        try:
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                event = json.loads(line)
                if event["item"] == args.id:
                    emit({"schema_version": 1, "ok": True, "data": event})
        except KeyboardInterrupt:
            return 0


def main(argv=None):
    parser = Parser(prog="tool")
    nouns = parser.add_subparsers(dest="noun", required=True)
    item = nouns.add_parser("item").add_subparsers(dest="verb", required=True)
    get = item.add_parser("get", help="show an item's latest event")
    get.add_argument("id", type=int)
    get.set_defaults(func=item_get)
    tail = item.add_parser("tail", help="print an item's events as they happen, until interrupted")
    tail.add_argument("id", type=int)
    tail.set_defaults(func=item_tail)
    try:
        args = parser.parse_args(argv)
        return args.func(args)
    except Failure as exc:
        error = {"code": exc.code, "message": str(exc), "retryable": False, "next_action": exc.next_action}
        emit({"schema_version": 1, "ok": False, "error": error})
        return exc.status
    except Exception as exc:
        error = {"code": "INTERNAL", "message": f"unexpected error: {exc}", "retryable": False,
                 "next_action": "report this error with the command you ran"}
        emit({"schema_version": 1, "ok": False, "error": error})
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

`docs/cli-tree.json`:

```json
{
  "cli": "tool",
  "sources": [
    {
      "kind": "source",
      "ref": "tool.py"
    }
  ],
  "complete": true,
  "commands": [
    {
      "path": [
        "item",
        "get"
      ],
      "mcp_name": null,
      "kind": "command",
      "source": "tool.py"
    },
    {
      "path": [
        "item",
        "tail"
      ],
      "mcp_name": null,
      "kind": "command",
      "source": "tool.py"
    }
  ]
}
```

`docs/cli-behavior-deviations.json`:

```json
{
  "standard_version": 1,
  "deviations": [
    {
      "command": "item tail",
      "rule": "stdout-data-only",
      "proposed_form": "item tail prints one envelope per line as events arrive, until interrupted, instead of one JSON document",
      "task": "follow an item's events while a deploy runs",
      "harm": "one JSON document can only be printed when the command ends, and item tail runs until interrupted, so the agent would see no event until it stopped the command",
      "evidence": [
        "tool.py:53"
      ],
      "agent_cost": "an agent reads stdout line by line and parses each line as its own envelope",
      "work": {
        "standard": "replace item tail with a paged read of past events",
        "deviation": "none: item tail already streams"
      },
      "status": "accepted",
      "decided": {
        "on": "2026-10-21",
        "by": "Dana Reyes"
      }
    }
  ]
}
```

Then check again whether the CLI in tool.py is safe for agents to drive.
