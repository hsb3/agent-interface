# CLI behavior rules

How a CLI behaves when an agent drives it: one prescribed form per rule, so two CLIs built to the standard look the same to an agent. [cli-behavior.json](cli-behavior.json) is the source: rule ids, `applies_to`, forms, severities, tests, the error codes and the examples are read from it, and where this file and the JSON differ, the JSON wins. `behavior.py contract create` copies it into a contract; `behavior.py result check` checks results against it. Each heading below is a rule id, the value of a result's `rule` field.

## Which commands get results

- A tree entry is covered when its `kind` is `command`, its `path` is not null, and its first word is not a root command (`root_commands` in [cli-naming.json](../../../resources/cli-naming.json)). Aliases, stubs, MCP-only entries and root commands get no results.
- A command's path is its tree `path` words joined by spaces (`item list`), the same words as `docs/cli-tree.json`.
- The verb is the last word of the path. A synonym (`ls`, `rm`) takes the verb it maps to in `cli-naming.json` (`synonyms` and `confirm_synonyms`).

## Command kinds

A rule applies by the kind of command, and the kind comes from the verb (`kinds` in `cli-behavior.json`):

| Kind | Verbs | Meaning for the rules |
|---|---|---|
| `read` | `list`, `get`, `search`, `check` | changes no record |
| `write` | `create`, `update`, `delete`, `sync`, `import`, `export`, `run`, `stop` | changes records, state or a file outside the command's own output |
| `long-running` | `start` | begins work that outlives the command |

- `export` is a write: it writes data out to a file or service.
- Any other verb: on a check, read the kind from the handler, record it as `command_kind` on that command's results, and cite the handler line in their `evidence`. On a design run, or when no handler can be read, the kind is `write`, the strictest.
- `applies_to` is `"all"`, `{"kinds": [...]}` or `{"verbs": [...]}`. A command outside a rule's `applies_to` is recorded `not_applicable`, with the reason, and nothing else.

## Severity

Worst first. A finding's severity is its rule's severity.

1. `data`: an agent can lose, duplicate, corrupt or expose data, or read a partial result as complete.
2. `hang`: an agent can stall until it times out.
3. `misread`: an agent can misread the result or the failure.

Findings are ordered by severity, then the tree's command order, then the order of the rules below. `result check` returns them in that order.

## What the rules judge

- The output rules (`json-flag`, `envelope`, `stdout-data-only`, `error-object`, `paged-list`) are judged on the output with `--json`. Without `--json`, output is free text for people; only its exit status is judged, by `exit-status`.
- `idempotent-write` judges a repeat: a run after the first one finished. Two runs at the same time are outside the rule.

## json-flag

- Applies to: all commands. Severity: `misread`.
- Form: `--json` selects machine output. A command whose only output is the envelope passes without the flag. A command that prints nothing records `not_applicable`.
- Example: `tool item list --json` prints the envelope; `tool item list` may print a table.
- Fails when: the command prints text or a table and has no `--json`.
- Reason: an agent should never scrape a table to read a result.

## envelope

- Applies to: all commands. Severity: `misread`.
- Form: with `--json`, success is `{"schema_version": 1, "ok": true, "data": ...}`. A list's `data` is an array, and the envelope adds a top-level `"page"` (see `paged-list`).
- Example: `{"schema_version": 1, "ok": true, "data": {"id": "a1", "title": "First record"}}`.
- Fails when: `--json` prints bare data (`[...]` or `{...}`) with no `schema_version` and `ok`.
- Reason: one shape for every command lets an agent check `ok` before reading `data`, and `schema_version` tells it when the shape changes.

## stdout-data-only

- Applies to: all commands. Severity: `misread`.
- Form: with `--json`, stdout holds exactly one JSON document, the success envelope or the failure envelope, even on a crash or a usage error. Progress, logs and warnings go to stderr as free text.
- Example: `print("Loading...", file=sys.stderr)`; never `print("Loading...")` beside the envelope.
- Fails when: progress lines share stdout with the data; a failure under `--json` leaves stdout empty or holds a traceback; a command prints one JSON object per line.
- Reason: an agent parses stdout once; a second document or a stray line breaks the parse.

## error-object

- Applies to: all commands. Severity: `misread`.
- Form: with `--json`, a failure is `{"schema_version": 1, "ok": false, "error": {"code", "message", "retryable", "next_action"}}` on stdout, `code` from the error-code table below. An uncaught exception becomes `INTERNAL` and a usage error `INVALID_ARGUMENT`, both as that envelope. Without `--json`, a failure is plain text on stderr with the same exit status.
- Example: `{"schema_version": 1, "ok": false, "error": {"code": "NOT_FOUND", "message": "no record a9", "retryable": false, "next_action": "run the list command to find the record's id"}}`.
- Fails when: a failure is only plain text, or the object lacks a field, or `code` is not in the table.
- Reason: the code and `retryable` tell an agent whether to retry, fix its input or stop, without reading prose.

## exit-status

- Applies to: all commands. Severity: `misread`.
- Form: 0 success, 1 failure, 2 invalid usage, per the error-code table. A check that completes is a success even when it reports problems; callers read `data`.
- Example: an unknown flag exits 2; a missing record exits 1.
- Fails when: a failure exits 0, or a usage error exits 1.
- Reason: the exit status is the first thing a caller reads; it must agree with the envelope.

## no-prompt

- Applies to: all commands. Severity: `hang`.
- Form: never waits on stdin for input or confirmation; missing input fails with `INVALID_ARGUMENT`. No pager, spinner or color when stdout is not a terminal or `--json` is set, and `NO_COLOR` is honored.
- Example: a missing name fails with `INVALID_ARGUMENT` and exit 2; it never calls `input()`.
- Fails when: any `input()`, `getpass()`, `read` or confirmation prompt can run, or a pager opens.
- Reason: an agent's stdin is closed or never answered, so a prompt hangs until the agent times out.

## confirm-flag

- Applies to: verb `delete`. Severity: `hang`.
- Form: proceeds only with `--yes`; without it, fails with `CONFIRMATION_REQUIRED` (exit 2) and changes nothing.
- Example: `tool item delete 7 --yes`.
- Fails when: the delete asks on stdin, or runs with no flag at all.
- Reason: `--yes` answers the confirmation without a prompt; `--force` is not used, because it often also overrides safety checks.

## paged-list

- Applies to: verbs `list`, `search`. Severity: `data`.
- Form: `--limit` (default 20, maximum 100; above 100 fails with `INVALID_ARGUMENT`) and `--cursor`. The envelope has `page: {"next_cursor": <string or null>, "has_more": <bool>}`, where `has_more` is `true` exactly when `next_cursor` is not null. Never stops early without `has_more: true`; a short list is paged too. Judged on the `--json` output, so without `--json` a list may print rows as free text.
- Example: `{"schema_version": 1, "ok": true, "data": [...], "page": {"next_cursor": "41", "has_more": true}}`; the next call is `tool item list --json --cursor 41`.
- Fails when: the list is cut at a fixed size with no sign that more exist, or prints every row with no bound, or pages by offset.
- Reason: an agent reads a silently cut list as complete; offset paging skips or repeats rows when rows change between pages.

## dry-run

- Applies to: kind `write`. Severity: `data`.
- Form: `--dry-run` reports the changes in `data` and makes none.
- Example: `tool item create --name x --dry-run` returns `{"would_create": {...}}` and writes nothing.
- Fails when: a write has no `--dry-run`, or the flag still changes something.
- Reason: an agent can show or check a change before it makes it.

## idempotent-write

- Applies to: kind `write`. Severity: `data`.
- Form: `create`, `import` and `run` take `--idempotency-key`: a repeat with the same key and arguments returns the first result, and the same key with different arguments fails with `CONFLICT`; how long keys are kept is not prescribed. `update`, `delete`, `sync`, `stop` and `export` are safe by end state: running them twice leaves the same state as once. A `delete` of a record already gone exits 0 with `data.deleted: false`. A repeat is a run after the first one finished; two runs at the same time are outside this rule.
- Example: `tool item create --name x --idempotency-key 9f2c` run twice creates one item.
- Fails when: a repeated create makes a second record, or a repeated delete fails with `NOT_FOUND`.
- Reason: an agent retries after a timeout without knowing whether the first run acted.

## operation-handle

- Applies to: kind `long-running`. Severity: `data`.
- Form: returns `data.operation_id` at once; status is read with `operation get <id>`. A `start` that stays in the foreground records `not_applicable` with its reason.
- Example: `tool job start --json` returns `{"data": {"operation_id": "op-12"}}`; `tool operation get op-12` reads its status.
- Fails when: the command returns before the work ends and gives no handle to follow it.
- Reason: an agent that loses track of started work starts it again.

## secret-input

- Applies to: all commands. Severity: `data`.
- Form: no secret as a flag value; read it from an environment variable or a file; never print a secret.
- Example: `TOOL_TOKEN` in the environment, or `--token-file path`; never `--token abc`.
- Not applicable when: the command takes no credential or secret; record that as the reason.
- Reason: flag values land in shell history, process lists and agent transcripts.

## Error codes

A fixed set, modeled on the gRPC canonical status codes. A CLI adds a code only through an accepted deviation on `error-object`. `retryable` is fixed per code, except for the three marked "set by the command", where the command may already have acted:

| Code | `retryable` | Exit status | When |
|---|---|---|---|
| `INVALID_ARGUMENT` | `false` | 2 | bad flags, arguments or input, including a usage error |
| `CONFIRMATION_REQUIRED` | `false` | 2 | a `delete` run without `--yes` |
| `NOT_FOUND` | `false` | 1 | the named record does not exist |
| `CONFLICT` | set by the command | 1 | the change conflicts with current state, or an idempotency key is reused with different arguments |
| `UNAUTHENTICATED` | `false` | 1 | no or expired credentials |
| `PERMISSION_DENIED` | `false` | 1 | credentials lack the right |
| `RATE_LIMITED` | `true` | 1 | refused before running; retry after the delay in `next_action` |
| `UNAVAILABLE` | set by the command | 1 | a dependency could not be reached |
| `TIMEOUT` | set by the command | 1 | the command gave up waiting |
| `INTERNAL` | `false` | 1 | anything unexpected, including an uncaught exception |

- "Set by the command" means `true` only when repeating the command is safe: it is a read, its write gives the same end state when repeated, or the caller supplied `--idempotency-key`.
- `message` and `next_action` are strings; `next_action` names what the caller should do next and is never empty.

## Known limit

- The contract template cannot express some behavior, such as a command that streams output until interrupted. Design such a CLI by hand from this standard. On a check, the streaming command fails `stdout-data-only`, and keeping the stream is an optional deviation like any other.
