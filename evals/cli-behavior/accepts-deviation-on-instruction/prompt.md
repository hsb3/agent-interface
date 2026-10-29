---
max_turns: 30
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
        "list"
      ],
      "mcp_name": null,
      "kind": "command",
      "source": "tool.py"
    },
    {
      "path": [
        "item",
        "delete"
      ],
      "mcp_name": null,
      "kind": "command",
      "source": "tool.py"
    }
  ]
}
```

`docs/cli-behavior.json`:

```json
{
  "standard_version": 1,
  "results": [
    {
      "commands": [
        "item list",
        "item delete"
      ],
      "rule": "json-flag",
      "status": "fail",
      "evidence": [
        "tool.py:36",
        "tool.py:37"
      ],
      "task": "read the command's result as data",
      "fix": "add --json to both commands",
      "test": "run `tool item list --json`: stdout is one JSON document"
    },
    {
      "commands": [
        "item list",
        "item delete"
      ],
      "rule": "envelope",
      "status": "fail",
      "evidence": [
        "tool.py:16",
        "tool.py:28"
      ],
      "task": "read the command's result as data",
      "fix": "with --json, print the success envelope",
      "test": "run `tool item list --json`: schema_version is 1 and ok is true"
    },
    {
      "commands": [
        "item list",
        "item delete"
      ],
      "rule": "stdout-data-only",
      "status": "fail",
      "evidence": [
        "tool.py:14",
        "tool.py:28"
      ],
      "task": "parse stdout as one document",
      "fix": "with --json, print only the envelope on stdout",
      "test": "run `tool item delete 1 --json --yes`: stdout parses as one JSON document"
    },
    {
      "commands": [
        "item list",
        "item delete"
      ],
      "rule": "error-object",
      "status": "fail",
      "evidence": [
        "tool.py:24"
      ],
      "task": "tell a retryable failure from a final one",
      "fix": "with --json, print the failure envelope on stdout",
      "test": "run `tool item delete 999 --json --yes`: error.code is NOT_FOUND"
    },
    {
      "commands": [
        "item list",
        "item delete"
      ],
      "rule": "exit-status",
      "status": "pass",
      "evidence": [
        "tool.py:25"
      ]
    },
    {
      "commands": [
        "item list",
        "item delete"
      ],
      "rule": "no-prompt",
      "status": "pass",
      "evidence": [
        "tool.py:13",
        "tool.py:20"
      ]
    },
    {
      "commands": [
        "item delete"
      ],
      "rule": "confirm-flag",
      "status": "fail",
      "evidence": [
        "tool.py:20"
      ],
      "task": "delete only what the agent meant to delete",
      "fix": "require --yes; without it fail with CONFIRMATION_REQUIRED",
      "test": "run `tool item delete 1`: it exits 2 with CONFIRMATION_REQUIRED"
    },
    {
      "commands": [
        "item list"
      ],
      "rule": "paged-list",
      "status": "fail",
      "evidence": [
        "tool.py:15"
      ],
      "task": "read every item without an unbounded output",
      "fix": "add --limit (default 20, maximum 100) and --cursor, and the page object",
      "test": "read 250 records with `tool item list --limit 20`: every record appears once, and the last page has has_more: false"
    },
    {
      "commands": [
        "item delete"
      ],
      "rule": "dry-run",
      "status": "fail",
      "evidence": [
        "tool.py:37"
      ],
      "task": "see what a delete would change before making it",
      "fix": "add --dry-run",
      "test": "run `tool item delete 1 --dry-run --yes`: items.json is unchanged"
    },
    {
      "commands": [
        "item delete"
      ],
      "rule": "idempotent-write",
      "status": "fail",
      "evidence": [
        "tool.py:25"
      ],
      "task": "retry a delete after a timeout",
      "fix": "exit 0 with data.deleted false when the item is already gone",
      "test": "run `tool item delete 1 --yes` twice: both exit 0"
    },
    {
      "commands": [
        "item list",
        "item delete"
      ],
      "rule": "secret-input",
      "status": "not_applicable",
      "reason": "the CLI takes no credential or secret"
    }
  ]
}
```

`docs/cli-behavior-plan.md`:

```markdown
# Behavior plan: tool

Results: docs/cli-behavior.json (standard version 1): 2 pass, 8 fail, 0 unknown, 1 not applicable, 0 deviation.

## Full compliance

### item list

- paged-list (data), tool.py:15: add `--limit` (default 20, maximum 100) and `--cursor`, and the `page` object.
- json-flag, envelope, stdout-data-only (misread), tool.py:14, tool.py:16, tool.py:36: add `--json`; with it, print only the success envelope on stdout.
- error-object (misread), tool.py:24: with `--json`, print the failure envelope on stdout.
- Callers this breaks: `scripts/count-open.sh:3` and `scripts/prune.sh:3` read the table and would see only its first page. Move them to `tool item list --json` and follow `page.next_cursor`.

### item delete

- dry-run (data), tool.py:37: add `--dry-run`.
- idempotent-write (data), tool.py:25: exit 0 with `data.deleted: false` when the item is already gone.
- confirm-flag (hang), tool.py:20: require `--yes`; without it fail with `CONFIRMATION_REQUIRED`.
- json-flag, envelope, stdout-data-only, error-object (misread), tool.py:24, tool.py:28, tool.py:37: as for item list.
- Callers this breaks: `scripts/prune.sh:3` runs `tool item delete` without `--yes`.

## Optional deviations

- item list, paged-list: keep the table as the default output of item list, with every row; page only with `--json`. Task: count open items and prune closed ones in the nightly scripts. Work: standard, page the table and move both scripts to `--json`; deviation, page only under `--json`.
- item delete, confirm-flag: keep deleting without `--yes`. Task: prune closed items nightly. Work: standard, add `--yes` and pass it in scripts/prune.sh; deviation, none.

Declined: item delete, dry-run (2026-10-20, Dana Reyes).
```

`docs/cli-behavior-deviations.json`:

```json
{
  "standard_version": 1,
  "deviations": [
    {
      "command": "item list",
      "rule": "paged-list",
      "proposed_form": "without --json, item list keeps its current default output: the full table with every row; --limit and --cursor apply with --json",
      "task": "count open items and prune closed ones from the table in the nightly scripts",
      "harm": "a paged default table holds 20 rows, so the scripts would miss every item after the first page",
      "evidence": [
        "scripts/count-open.sh:3",
        "scripts/prune.sh:3"
      ],
      "agent_cost": "an agent that runs item list without --json gets every row, with no bound on the output",
      "work": {
        "standard": "page the table and move both scripts to --json with next_cursor",
        "deviation": "page only under --json"
      },
      "status": "proposed"
    },
    {
      "command": "item delete",
      "rule": "confirm-flag",
      "proposed_form": "item delete keeps deleting without --yes",
      "task": "prune closed items nightly",
      "harm": "scripts/prune.sh runs item delete with no flag, so it would fail with CONFIRMATION_REQUIRED",
      "evidence": [
        "scripts/prune.sh:3"
      ],
      "agent_cost": "an agent can delete an item with no confirmation step",
      "work": {
        "standard": "add --yes and pass it in scripts/prune.sh",
        "deviation": "none"
      },
      "status": "proposed"
    },
    {
      "command": "item delete",
      "rule": "dry-run",
      "proposed_form": "item delete has no --dry-run",
      "task": "delete closed items",
      "harm": "a dry run adds a flag the nightly script never uses",
      "evidence": [
        "scripts/prune.sh:3"
      ],
      "agent_cost": "an agent cannot preview a delete",
      "work": {
        "standard": "add --dry-run to item delete",
        "deviation": "none"
      },
      "status": "declined",
      "decided": {
        "on": "2026-10-20",
        "by": "Dana Reyes"
      }
    }
  ]
}
```

I'm Dana Reyes. I asked you to check how the CLI in tool.py behaves for agents, and the files in docs/ are that check, its plan and its options. I accept the option to keep the table as the default output of item list.
