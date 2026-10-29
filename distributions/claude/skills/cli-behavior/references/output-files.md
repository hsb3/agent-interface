# Output files

The files the cli-behavior skill writes, all in `docs/` of the CLI's repository. The repository root is the parent of that `docs/` folder; every path inside these files is relative to it. The tree, `docs/cli-tree.json`, has its own format in [command-tree.md](../../../resources/command-tree.md).

## Results: `docs/cli-behavior.json`

Written on a check, from reading the source. `behavior.py result check` validates it against the tree and the register in the same folder.

```json
{
  "standard_version": 1,
  "results": [
    {"commands": ["note list", "note search"], "rule": "paged-list", "status": "fail",
     "evidence": ["src/notes/cli.py:88"], "task": "read every note",
     "fix": "add --limit (default 20, maximum 100) and --cursor, and the page object",
     "test": "read 250 records with `notes note list --limit 20`: every record appears once, and the last page has `has_more: false`"},
    {"commands": ["note list", "note get", "note search", "note create"], "rule": "error-object",
     "status": "unknown", "evidence": ["src/notes/cli.py:12"],
     "test": "run `notes note get 999 --json`: stdout is the failure envelope with `error.code` `NOT_FOUND`"},
    {"commands": ["note list", "note get", "note search"], "rule": "dry-run",
     "status": "not_applicable", "reason": "rule applies to kind write only"},
    {"commands": ["note archive"], "command_kind": "write", "rule": "stdout-data-only",
     "status": "deviation", "evidence": ["src/notes/cli.py:140"]}
  ]
}
```

Top level:

| Field | Type | Meaning |
|---|---|---|
| `standard_version` | integer | `version` of `cli-behavior.json`, now `1` |
| `results` | list of results | every rule's results, covering every covered command |

Each result:

| Field | Type | Meaning |
|---|---|---|
| `commands` | non-empty list of strings | covered command paths, words joined by spaces, as in the tree (`"item list"`). One result can cover every command that shares a handler or a finding |
| `rule` | string | a rule id from `cli-behavior.json` |
| `status` | string | `pass`, `fail`, `unknown`, `not_applicable` or `deviation` |
| `evidence` | non-empty list of strings | `path:line`, repository-relative, each line within the file: the line that shows the result |
| `task` | string | the agent task the failure breaks, in plain words |
| `fix` | string | the change that brings the command to the rule's form |
| `test` | string | a test that would show the fix works or settle an unknown; start from the rule's `tests` in the standard with `<command>` replaced by `<cli> <command path>` |
| `reason` | string | why the rule does not apply |
| `command_kind` | `read`, `write` or `long-running` | only for a verb the standard does not list, read from its handler; that handler line is in `evidence`, and every result for the command gives the same kind |

Required fields by status:

| `status` | Required fields |
|---|---|
| `pass` | `evidence` |
| `fail` | `evidence`, `task`, `fix`, `test` |
| `unknown` | `test` (add `evidence` when a line shows why it is unknown) |
| `not_applicable` | `reason` |
| `deviation` | `evidence`, and an `accepted` register entry for each command and the rule |

Coverage:

- For every rule, the results' `commands` lists together name every covered command at least once.
- A command outside the rule's `applies_to` appears only in a `not_applicable` result, with a reason such as "rule applies to kind write only" or "rule applies to verbs list and search only".
- A command inside `applies_to` may still be `not_applicable` when the rule's form says so, such as `secret-input` for a command that takes no secret ("the CLI takes no credential or secret").

## Register: `docs/cli-behavior-deviations.json`

Each option offered on a check, and each decision on one. Schema: [deviation.schema.json](deviation.schema.json); `result check` reports a problem for an entry with a missing or empty field.

```json
{
  "standard_version": 1,
  "deviations": [
    {
      "command": "item tail",
      "rule": "stdout-data-only",
      "proposed_form": "item tail prints one envelope per line as items arrive, until interrupted",
      "task": "follow new items as they arrive",
      "harm": "one JSON document is printed only when the command ends, so a follower would have to poll",
      "evidence": ["scripts/follow.sh:3"],
      "agent_cost": "an agent parses each stdout line as its own envelope and must interrupt the command",
      "work": {"standard": "return the new items since a cursor as one document, and change scripts/follow.sh to poll", "deviation": "none: item tail already streams"},
      "status": "proposed"
    }
  ]
}
```

| Field | Required | Meaning |
|---|---|---|
| `standard_version` | yes (top level) | `1` |
| `deviations` | yes (top level) | list of entries; may be empty |
| `command` | yes | a covered command path in the tree |
| `rule` | yes | a rule id in the standard; `command` and `rule` together key the entry, one entry per pair |
| `proposed_form` | yes | what the command does instead of the standard form |
| `task` | yes | the agent or user task the standard form makes worse |
| `harm` | yes | how the standard form makes that task worse, concretely |
| `evidence` | yes | at least one `file:line` or caller showing the task exists |
| `agent_cost` | yes | what an agent loses if the deviation is taken |
| `work` | yes | `{"standard": ..., "deviation": ...}`: the change each way, in plain words |
| `status` | yes | `proposed`, `accepted` or `declined` |
| `decided` | when not `proposed` | `{"on": "YYYY-MM-DD", "by": "<who decided>"}` |

- The standard's form is read from `cli-behavior.json` by rule id; never copy it into an entry.
- `proposed` entries are replaced on every check by that check's options. `accepted` and `declined` entries are never removed or rewritten by a check.
- Only an `accepted` entry makes a result's status `deviation`.

## Plan: `docs/cli-behavior-plan.md`

Written after `result check` accepts the results. Layout:

```markdown
# Behavior plan: <cli>

Results: docs/cli-behavior.json (standard version 1): <n> pass, <n> fail, <n> unknown, <n> not applicable, <n> deviation.

## Full compliance

### <command>

- <rule> (<severity>), <file:line>: <fix>. Test: <test>.
- Unknown, <rule>: run <test> first, then <the fix if it fails>.
- Callers this breaks: <file:line>: <what breaks> and <the change the caller needs>.

### <next command>

...

## Accepted deviations

- <command>, <rule>: <proposed_form>. Reason: <task>; <harm>. Accepted <on> by <by>. This plan does not change it.

## Optional deviations

- <command>, <rule>: <proposed_form>. Task: <task>. Harm: <harm>. Agent cost: <agent_cost>. Work: standard, <work.standard>; deviation, <work.deviation>.

Declined: <command>, <rule> (<on>, <by>).
```

- Full compliance is the plan. It gives every failing result's fix, grouped by command, commands in order of their worst finding and each command's lines worst first, as `result check` orders `findings`. Several rules with one fix may share a line.
- Every unknown gives the test to run before deciding its fix.
- "Callers this breaks" lists every caller in the repository that a change breaks, from the caller search; write "Callers this breaks: none found" when the search finds none.
- Leave out "Accepted deviations" when there are none. A command whose only results are passes, unknowns with no test to run, or accepted deviations gets no section.
- "Optional deviations" lists each `proposed` entry of this run by command and rule. With none, write "None." A plan with no options is a normal result. Never rank options or recommend one.
- List `declined` entries in one line after the options, so the owner sees they stay closed.
- On a generic request, end with: "Command names were not checked. To check them, ask: check the command names of the CLI in <path>."

## Contract: `docs/cli-contract.md`

Written only by `behavior.py contract create`; never by hand. The same tree always gives the same bytes. With `--idempotency-key`, the file ends with a comment holding the key and the tree's SHA-256: a repeat with that key and the same tree returns the first result, and with a changed tree fails with `CONFLICT`. Layout:

- `# Behavior contract: <cli>`, and a line saying the file is generated from the tree and the standard's version.
- `## Commands`: per covered command, in tree order, a `### <command path>` section with its kind, flags (`--json`, `--yes`, `--limit`, `--cursor`, `--dry-run`, `--idempotency-key` as its rules require), applicable rule ids and error codes.
- `## Rules`: the form of each rule that applies to some command.
- `## Envelope`: the success and failure fields, the list `page` object and the `--limit` default and maximum.
- `## Error object`: its fields, how `retryable` is set, and `next_action`.
- `## Error codes`: the code table with `retryable`, exit status and when.
- `## Examples`: one success envelope and one failure envelope.
- `## Tests`: per command, each applicable rule's tests with `<command>` filled in, including the stdin-closed test and the 250-record read for a list.
