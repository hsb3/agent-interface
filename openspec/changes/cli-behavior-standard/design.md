# Design

Status: Approved
<!-- Draft → In review → Approved. Only the owner sets Approved. -->

*   **Author:** hsb3
*   **Date:** 2026-10-28

## Context

agent-interface ships one skill today, `agent-interface`, which holds a noun-verb naming standard for CLI commands and MCP tool names, checks a CLI against it, plans renames, and designs a new CLI's command tree.

This change does two things:

1. It renames that skill `menu-design`. "Menu" is the set of commands a CLI offers or the set of tools an MCP server offers. Its naming results, and how it records a word the owner keeps (`local_verbs`), do not change. `tree.py`'s output and errors move to the new behavior standard.
2. It adds a second skill, `cli-behavior`, which holds one fixed standard for how a CLI behaves when an agent drives it: the shape of its output, which stream carries what, the shape and codes of its errors, how it pages long results, what it does with no terminal attached, and how its writes are made safe to repeat. The skill writes a new CLI's behavior contract from the standard. Asked to check an existing CLI, it reads the source, records a result for every rule, and writes a plan that brings the CLI to the standard, with any deviations as options (Goal 4).

The plugin owns this standard, as it owns the naming standard.

Normative inputs: [proposal.md](proposal.md) and the spec deltas for [cli-behavior](specs/cli-behavior/spec.md), [menu-design](specs/menu-design/spec.md) and [agent-interface](specs/agent-interface/spec.md).

Settled by the owner on 2026-10-28 and not reopened here:

- The first change covers CLI behavior only. Skill design and MCP tool behavior are planned as `skill-design` and `mcp-behavior` (Goal 8).
- One job per skill: the naming skill is renamed rather than expanded.
- The check reads source only. It never runs the target CLI, not even `--help` or a read-only command.
- agent-interface owns the behavior standard. agent-toolkits (`hsb3/agent-toolkits`) will be redesigned later to align with it and remove overlaps (hsb3/agent-toolkits#98, which also covers the naming follow-up hsb3/agent-toolkits#97). Until then the two standards differ (Risks); this design does not shape itself around agent-toolkits' current rules.

Owner decisions from the 2026-10-28 review (O1-O4) are recorded where they apply: the `menu-design` register is deferred, deviation options are `proposed` register entries, `--json` failures go to stdout, and `retryable` is fixed per code except where the command may already have acted.

## The Problem

The owner builds many small CLIs across separate projects. With no behavior standard, the agent in each project proposed a different design for the same concerns: a different JSON shape, a different error format, different paging flags, a confirmation prompt in one and a `--yes` flag in another. The owner steered each project by hand, and the CLIs built before that steering still differ. An agent that drives several of them has to learn each one, and every new project needs the same steering again.

Agents also hit failures a person at a terminal works around: a prompt that waits forever because stdin is closed, a table it has to scrape, a list cut at 50 rows with no sign that more exist, an error with no code saying whether a retry is safe, a write that runs twice after a timeout.

Two things exist today and neither solves this:

- The `agent-toolkit-standards` skill (`hsb3/agent-toolkits`, `skills/agent-toolkit-standards`, §2.5 to §2.7 and its logging section) gives guidance on paging, structured errors, safety labels and stderr logging. It covers only toolkits built with that kit, its rules leave the concrete form open ("pagination on by default", "`dry_run` support where feasible"), and nothing checks a CLI against them. Two agents following it can still produce two different envelopes.
- The earlier prototype of this plugin (private repository `hsb3/plugin-labs-private`) had a CLI checklist that told the agent to "pick the options the task needs". That instruction is the source of the divergence, not the fix for it.

The owner chose one skill per job over one skill covering names, behavior, and later MCP behavior and skill design.

## Goals

1.  **The same answer every time.** Two design runs for unrelated CLIs produce the same envelope fields, the same error object fields, the same error code set, and the same flag names for machine output, paging, confirmation, dry run and idempotency. Proved by a unit test that runs `contract create` on two unrelated trees and compares envelope fields, error fields, codes and flag names.
2.  **Every rule has one prescribed form.** Each rule in the standard names the exact field, flag, exit status or stream, not a choice among options. The standard lives in one bundled, versioned file, like `cli-naming.json`.
3.  **The check reports drift with evidence.** Each failing finding names its rule, the source `file:line`, the agent task it breaks, a fix, and a test that would show the fix works. On the notes toolkit, the check produces a results file that `result check` accepts, and every failing finding cites a line that exists.
4.  **Full compliance is the plan; deviations are options.** A check request means correcting the CLI is already decided, so the skill never asks whether to fix it. The plan brings every failing result to the standard. A deviation is offered only as an optional change, justified by the agent or user task the standard form makes worse; its `work` field (the change each way) is stated but is never the reason to offer it. The person who asked for the check chooses, and only an entry they accept counts as a deviation.
5.  **Unknown is never a pass.** What source cannot prove is reported as unknown with the test that would settle it; a rule that does not apply is recorded as not applicable with its reason.
6.  **Each skill carries its own deviation schema.** A deviation is proposed by filling in the skill's schema, whose required fields make the reasoning explicit (the task the standard form makes worse, the evidence that the task exists, what agents lose by deviating, the work each way). An entry missing a required field is rejected by the skill's script, so no deviation is recorded without every field filled in; whether the reasoning is sound is the requester's call. `menu-design` adopts the same pattern in its later plan-first change; until then it keeps `local_verbs`.
7.  **The rename keeps every naming result.** `menu-design` passes every eval case that `agent-interface` passed in the 2026-10-28 host run recorded in `TESTING.md`, under the new name. `tree.py`'s exit status, success envelope and error output change (see "The plugin's own scripts"); its findings do not.
8.  **Names leave room.** The skill, its standard file, its rule ids and its output files are named so `mcp-behavior` and `skill-design` fit beside them with no rename.

## Non-Goals

*   Running the target CLI in any form, including against a fixture.
*   Editing the CLI or applying fixes; the owner does that from the plan.
*   Choosing among optional deviations, or ranking them by the work they take.
*   Bringing `menu-design`'s reply onto the plan-first model. It keeps asking about a confirm-only word and recording a kept word in `local_verbs`, as today. Its plan-first wording and its own deviation register are a later change (O1).
*   Formal evaluation of the deviation schemas through an eval harness. The schemas are tools that shape the agent's reasoning, checked by the skill's script and `bin/gate`; the repo's eval cases still cover each spec scenario.
*   Checking a hand-written declaration of what the CLI does in place of its source.
*   The `skill-design` and `mcp-behavior` skills.
*   Measuring agent success, retries or output size before and after a fix (waits on hsb3/agent-interface#11).
*   Changing agent-toolkits. Its redesign is separate work (hsb3/agent-toolkits#98) and waits until this change ships.
*   HTTP APIs and SDKs. The standard covers command-line programs only.
*   A reviewer agent, hooks, MCP servers or apps.

## Open Questions

*   **Unknown ceiling.** Source-only evidence may leave many results unknown (whether stdout carries only data can depend on a library outside the repo). How large a share of unknown results on the notes toolkit makes the check not worth running? No threshold is set until the notes toolkit is measured.

## Critical User Journeys (CUJs)

### CUJ 1: Design a new CLI's behavior

*   **Given**: a new project with no CLI yet, or with `docs/cli-tree.json` from `menu-design`.
*   **When**: the owner asks "design how the `issues` CLI should behave for agents" and describes its commands.
*   **Then**: `docs/cli-contract.md` gives every command its kind, flags, applicable rules and error codes, plus the standard's envelope, error object, one example success, one example failure and the tests. A second project asking the same for a different CLI gets the same envelope, error fields, codes and flag names.

### CUJ 2: Check an existing CLI

*   **Given**: a CLI repo the owner built earlier.
*   **When**: the owner asks "check whether the notes CLI is safe for agents to drive".
*   **Then**: `docs/cli-behavior.json` holds results covering every command for every rule that applies to it; the reply gives the counts and the failing findings worst first, each with `file:line`, broken task, fix and test. `docs/cli-behavior-plan.md` brings the CLI fully to the standard and lists callers each change breaks; any deviations are `proposed` entries in `docs/cli-behavior-deviations.json`, listed in the plan. Unknowns carry the test that would settle them. The CLI is not run and not edited.

### CUJ 3: Fix and re-check

*   **Given**: the owner changed the CLI from the plan of CUJ 2 and told the agent to accept one optional deviation, which is now `accepted` in `docs/cli-behavior-deviations.json`.
*   **When**: the owner asks for the check again.
*   **Then**: the fixed findings now pass with a cited line, the accepted deviation is reported as a deviation with its reason, and the rest are unchanged.

## Technical Plan (Architecture)

### The standard

One file, `skills/cli-behavior/references/cli-behavior.json`, versioned like `cli-naming.json`, with prose reasons in `cli-behavior.md`. Every rule prescribes one form. The values below are a draft and open to review.

**Which commands get results.** A tree entry is covered when its `kind` is `command`, its `path` is not null, and its first word is not a root command (`help`, `version` and the other roots, read from `resources/cli-naming.json`). Aliases, stubs, MCP-only entries and root commands get no results. The command's verb is the last word of its path.

**Command kinds.** A rule applies by the kind of command, and the kind comes from the verb, so no one decides it per CLI:

| Kind | Verbs | Meaning for the rules |
|---|---|---|
| `read` | `list`, `get`, `search`, `check` | changes no record |
| `write` | `create`, `update`, `delete`, `sync`, `import`, `export`, `run`, `stop` | changes records, state or a file outside the command's own output |
| `long-running` | `start` | begins work that outlives the command |

`export` is a write because `cli-naming.json` defines it as writing data out to a file or service. A synonym (`ls`, `rm`) takes the kind of the verb it maps to in `cli-naming.json` (`synonyms` and `confirm_synonyms`). Any other verb: on a check, the kind is read from the handler and its line goes in that result's `evidence`; on a design run, or when no handler can be read, the kind is `write`, the strictest. `bin/gate` fails if a verb in `cli-naming.json` has no kind.

**Rules.** `applies_to` is `all`, a list of kinds or a list of verbs.

| Rule id | `applies_to` | Prescribed form | Severity |
|---|---|---|---|
| `json-flag` | `all` | `--json` selects machine output; a command whose only output is the envelope passes without it; a command that prints nothing records `not_applicable` | `misread` |
| `envelope` | `all` | with `--json`, success is `{"schema_version": 1, "ok": true, "data": ...}`; a list's `data` is an array, and the envelope adds a top-level `"page"` | `misread` |
| `stdout-data-only` | `all` | with `--json`, stdout holds exactly one JSON document, the success envelope or the failure envelope, even on a crash or a usage error; progress, logs and warnings go to stderr as free text | `misread` |
| `error-object` | `all` | with `--json`, a failure is `{"schema_version": 1, "ok": false, "error": {"code", "message", "retryable", "next_action"}}` on stdout, `code` from the table below; an uncaught exception becomes `INTERNAL` and a usage error `INVALID_ARGUMENT`, both as that envelope. Without `--json`, a failure is plain text on stderr with the same exit status (O3) | `misread` |
| `exit-status` | `all` | 0 success, 1 failure, 2 invalid usage, per the code table; a check that completes is a success even when it reports problems, and callers read `data` | `misread` |
| `no-prompt` | `all` | never waits on stdin for input or confirmation; missing input fails with `INVALID_ARGUMENT`; no pager, spinner or color when stdout is not a terminal or `--json` is set, and `NO_COLOR` is honored | `hang` |
| `confirm-flag` | verbs `delete` | proceeds only with `--yes`; without it, fails with `CONFIRMATION_REQUIRED` | `hang` |
| `paged-list` | verbs `list`, `search` | `--limit` (default 20, maximum 100; above 100 fails with `INVALID_ARGUMENT`) and `--cursor`; `page: {"next_cursor": <string or null>, "has_more": <bool>}`, where `has_more` is `true` exactly when `next_cursor` is not null; never stops early without `has_more: true`; a short list is paged too | `data` |
| `dry-run` | kinds `write` | `--dry-run` reports the changes in `data` and makes none | `data` |
| `idempotent-write` | kinds `write` | `create`, `import`, `run` take `--idempotency-key`: a repeat with the same key and arguments returns the first result, and the same key with different arguments fails with `CONFLICT`; how long keys are kept is not prescribed. `update`, `delete`, `sync`, `stop`, `export` are safe by end state; a `delete` of a record already gone exits 0 with `data.deleted: false` | `data` |
| `operation-handle` | kinds `long-running` | returns `data.operation_id`; status is read with `operation get <id>`; a `start` that stays in the foreground records `not_applicable` with its reason | `data` |
| `secret-input` | `all` | no secret as a flag value; read from an environment variable or a file; never print a secret | `data` |

Each rule in `cli-behavior.json` also carries its `tests`: strings with a `<command>` placeholder. Two of them are required by the spec: `no-prompt` has "run `<command>` with stdin closed and a required argument missing: it exits 2 with `INVALID_ARGUMENT` and does not wait", and `paged-list` has "read 250 records with `<command> --limit 20`: every record appears once, and the last page has `has_more: false`". The file holds one `example_success` and one `example_failure` envelope for the whole contract.

**Error codes.** A fixed set, modeled on the gRPC canonical status codes. A CLI adds a code only through an accepted deviation on `error-object`. `retryable` is fixed per code, except for the three codes where the command may already have acted; for those the command sets it (O4):

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

"Set by the command" means `true` only when repeating the command is safe: it is a read, its write gives the same end state when repeated, or the caller supplied `--idempotency-key`. `message` and `next_action` are strings; `next_action` names what the caller should do next and is never empty.

**Severity scale**, worst first:

1. `data`: an agent can lose, duplicate, corrupt or expose data, or read a partial result as complete.
2. `hang`: an agent can stall until it times out.
3. `misread`: an agent can misread the result or the failure.

A finding's severity is its rule's severity; findings are ordered by severity, then the tree's command order, then the rules table's order.

**Known limit.** The contract template cannot express some behavior, such as a command that streams output until interrupted. Such a CLI is designed by hand from the standard until a real case justifies more; on a check, the streaming command's difference is a deviation like any other.

### Results file: `docs/cli-behavior.json`

```json
{
  "standard_version": 1,
  "results": [
    {"commands": ["note list", "note search"], "rule": "paged-list", "status": "fail",
     "evidence": ["src/notes/cli.py:88"], "task": "read every note", "fix": "...", "test": "..."},
    {"commands": ["note list", "note get", "note search", "note create"], "rule": "error-object",
     "status": "unknown", "evidence": ["src/notes/cli.py:12"], "test": "..."},
    {"commands": ["note list", "note get", "note search"], "rule": "dry-run",
     "status": "not_applicable", "reason": "rule applies to kind write only"},
    {"commands": ["note create"], "command_kind": "write", "rule": "stdout-data-only",
     "status": "deviation", "evidence": ["src/notes/cli.py:140"]}
  ]
}
```

A result covers every command in its `commands` list; one result can record a shared handler once. Every rule has results covering every covered command: a command outside the rule's `applies_to` is recorded `not_applicable` with a reason, and that is the only status it may have. The CLI name and sources are read from the tree beside it.

| `status` | Required fields |
|---|---|
| `pass` | `evidence` |
| `fail` | `evidence`, `task`, `fix`, `test` |
| `unknown` | `test` |
| `not_applicable` | `reason` |
| `deviation` | `evidence`, and an `accepted` register entry for each command and the rule |

`command_kind` appears only when a kind was read from a handler (an unlisted verb), and its handler line is in `evidence`. Command paths use the same words as `docs/cli-tree.json`.

### Bundled script: `skills/cli-behavior/scripts/behavior.py`

Standard library only, like `tree.py`. Both commands print only the envelope, so they pass `json-flag` without a `--json` flag.

- `behavior.py contract create docs/cli-tree.json` writes `docs/cli-contract.md` beside the tree, from the tree and the standard: per command its kind, flags, applicable rule ids and error codes; then the envelope, the error object, the code table, one example success, one example failure and each applicable rule's tests. The same tree always gives the same bytes: commands in tree order, no dates, no randomness. Success `data` is `{"path"}`. With `--dry-run` it writes nothing and returns `data: {"path", "contract"}`. The agent's design job is the command list: when no tree exists, it writes `docs/cli-tree.json` first, then runs `contract create`.
- `behavior.py result check docs/cli-behavior.json` reads the tree and the register from the same folder. The repository root is the parent of that `docs/` folder. It checks that, for each rule, the results' `commands` lists together cover every covered command, and that a command outside the rule's `applies_to` appears only in a `not_applicable` result; that each status has its required fields; that each `evidence` item is `path:line`, repository-relative, with the line within the file; that each `deviation` result has its `accepted` entry; and that each register entry has every required field and names a covered command and a real rule. Problems are one `INVALID_ARGUMENT` failure, exit 2, with every problem in `message`, one per line. Success `data` is `{"standard_version", "counts": {"pass", "fail", "unknown", "not_applicable", "deviation"}, "findings": [failing results]}`, in the order given under Severity. The script reads cited files only to check that the line exists; it never judges the CLI's source.

The skill runs `result check` at most three times while fixing its results file, then reports the problems left.

### Plan file: `docs/cli-behavior-plan.md`

Written by the agent after the check (Goal 4). Two parts:

1. *Full compliance* (the primary plan): every failing result's fix, grouped by command, worst first; every caller in the repository each change breaks, found by searching the repository for `<cli> <command words>` and for code that reads the command's output; for each unknown, the test to run before deciding its fix.
2. *Optional deviations*: each `proposed` entry in the register (below), listed by command and rule with its `task` and `work`. A plan with no options is a normal result.

### Deviation schema and register

Each skill carries its own schema and its own register file, named `docs/<skill>-deviations.json`. This change builds it for `cli-behavior` only; `menu-design`, `mcp-behavior` and `skill-design` follow the same pattern in their own changes. The skill's prose says when to propose a deviation; the schema's required fields say what the proposal must show.

**Entry** (schema: `skills/cli-behavior/references/deviation.schema.json`):

| Field | Required | Meaning |
|---|---|---|
| `command`, `rule` | yes | a covered command in the tree and a rule id in the standard; together they key the entry, one entry per pair |
| `proposed_form` | yes | what the command does instead |
| `task` | yes | the agent or user task the standard form makes worse |
| `harm` | yes | how the standard form makes that task worse, concretely |
| `evidence` | yes | `file:line` or caller showing the task exists; at least one |
| `agent_cost` | yes | what an agent loses if the deviation is taken |
| `work` | yes | `{standard, deviation}`: the change each way, in plain words |
| `status` | yes | `proposed`, `accepted` or `declined` |
| `decided` | when not `proposed` | `{on, by}`: ISO date and who decided |

The register file is `{"standard_version": 1, "deviations": [...]}`. The standard's form for a rule is read from the standard by its rule id, not copied into the entry. Options live in the register as `proposed` entries, so the script checks their reasoning when they are proposed (O2):

- The agent writes an option as a `proposed` entry. On each check it replaces every `proposed` entry with the options of that run, so an unanswered proposal never goes stale; `accepted` and `declined` entries are left as they are.
- The agent moves an entry to `accepted` or `declined` only on explicit instruction, in the conversation, from the person who asked for the check, and records `decided`.
- A `declined` entry stays, and a later check does not propose the same command and rule again; deleting the entry reopens it.

`behavior.py` loads `deviation.schema.json` with `json.load` and takes the required fields and allowed `status` values from it, so the schema is the single source; it checks field types in code. No schema library is used.

`menu-design` keeps `local_verbs` in this change. Its register follows this pattern in the later change that brings its reply onto the plan-first model; that change also maps its finding codes (`unlisted-verb`, `confirm-synonym`, `plural`) to register rules and moves existing `local_verbs`.

### Shared resources

Files both skills read move to `resources/`, as in the EGM plugin (`google/elephant-goldfish-model`), and each skill links to them with a path relative to the skill (`../../resources/...`), which resolves on both hosts; `${CLAUDE_PLUGIN_ROOT}` stays only in shell command lines:

- `resources/cli-naming.json` (from `skills/agent-interface/references/`): the verbs, synonyms, short forms, plural exceptions and roots. `cli-behavior` reads the verbs to give each command its kind.
- `resources/command-tree.md`: the tree file's fields (today's `tree-format.md`), how the repository root is found, and all of "Building the tree" (today in `remediation.md`). `cli-behavior` builds the tree with it when none exists.

Rules prose (`cli-naming.md`), the remaining remediation procedures and `tree.py` stay in `menu-design`. `cli-behavior.json`, its prose, its schema and `behavior.py` stay in `cli-behavior`.

### Generic request

Decided by the agent at the owner's request, 2026-10-28. `cli-behavior` takes a request to check a CLI that names neither names nor behavior ("check my CLI", "is my CLI ready for agents"). Its reply and plan state that names were not checked and give the request that checks them. Reason: each skill keeps one job, and neither skill invokes the other; Codex documents no way for one skill to invoke another. The cost is one extra request. `menu-design`'s description keeps claiming only requests about names.

### The plugin's own scripts

Decided by the agent at the owner's request, 2026-10-28. `tree.py` is brought to the standard in this change, and `behavior.py` is written to it, because an agent using this plugin would otherwise read two output shapes from one plugin, which is the inconsistency this change exists to remove. Both are envelope-only, so they pass `json-flag` without `--json`. Changes to `tree.py`:

- A completed check is a success: exit 0, `ok: true`, `data: {"standard_version", "findings"}`. Today a check with violations exits 1 with `ok: false` and `standard_version` at the top level. No `counts` field is added; the skill counts by grouping `data.findings`, as it does today.
- Failures follow `error-object`: the failure envelope on stdout, with `retryable: false` and a `next_action`, including argparse usage errors and uncaught exceptions; stderr carries no JSON. `invalid-tree` and `usage` become `INVALID_ARGUMENT` (exit 2), with the tree problem in `message`; anything unexpected is `INTERNAL` (exit 1).

### Data flow

```text
                   resources/cli-naming.json   resources/command-tree.md
                         |  (verbs)                  |  (tree format, building)
          +--------------+---------------+-----------+
          v                              v
   menu-design                      cli-behavior
   tree.py check                    behavior.py contract create
                                    behavior.py result check
     reads  docs/cli-tree.json        reads  docs/cli-tree.json
                                             docs/cli-behavior.json (check)
                                             docs/cli-behavior-deviations.json
                                             references/cli-behavior.json
     writes docs/cli-tree.json        writes docs/cli-tree.json (only when none exists)
            docs/cli-renames.json            docs/cli-contract.md   (design)
                                             docs/cli-behavior.json (check)
                                             docs/cli-behavior-plan.md
                                             docs/cli-behavior-deviations.json
                                               (proposed; decided on instruction)
```

## Skills

| Skill | Trigger phrases | Must not trigger on | Writes |
| --- | --- | --- | --- |
| `menu-design` (renamed from `agent-interface`) | check a CLI's command names; is this CLI noun-verb; design the commands for a new CLI; plan renames; name or check MCP tools | how a CLI behaves for agents (output, errors, paging, prompts); ordinary CLI use; building an MCP server; writing skills; unrelated questions | `docs/cli-tree.json`, `docs/cli-renames.json` in the CLI's repository (unchanged) |
| `cli-behavior` (new) | check how a CLI behaves for agents; is my CLI ready for agents; check my CLI (naming neither names nor behavior); design how a new CLI should behave for agents | command or tool names; ordinary CLI use; building an MCP server; unrelated questions | `docs/cli-tree.json` (only when none exists), `docs/cli-contract.md`, `docs/cli-behavior.json`, `docs/cli-behavior-plan.md`, `docs/cli-behavior-deviations.json` (`proposed` entries; status changes only on the requester's instruction) in the CLI's repository |

## Reviewers

None. The 2026-10-27 brainstorm (archived change `openspec/changes/archive/2026-10-28-cli-naming-standard/`) decided against a reviewer agent.

## Bundled files

Detailed Implementation lists each file, its change and the reason. Summary:

- `resources/`: `cli-naming.json` (moved) and `command-tree.md` (new), read by both skills.
- `skills/menu-design/`: the renamed skill; `references/tree-format.md` merged into `resources/command-tree.md`; `scripts/tree.py` brought to the behavior standard.
- `skills/cli-behavior/`: `SKILL.md`, `agents/openai.yaml`, `assets/icon.svg`, `references/` (`cli-behavior.json`, `cli-behavior.md`, `output-files.md`, `deviation.schema.json`), `scripts/behavior.py`.
- No files added under `docs/`; four existing docs and the root `README.md` change.

## Hosts

| Host | In scope | Notes |
| --- | --- | --- |
| Claude Code | yes | Skills invoked as `/agent-interface:menu-design` and `/agent-interface:cli-behavior`; `/agent-interface:agent-interface` no longer exists. Scripts run through `${CLAUDE_PLUGIN_ROOT}`. |
| Codex | yes | Skills discovered from `skills/<skill>/SKILL.md`; `resources/` ships at the plugin root and is reached by skill-relative links; the install test asserts it is present. |
| Antigravity | untested | Unchanged from 0.1.0. |

## Image assets

One new icon, `skills/cli-behavior/assets/icon.svg`, drawn only with colors listed in `assets/brand.json`, with `viewBox="0 0 24 24"` and a `<title>`. `menu-design` keeps the existing skill icon.

## Hooks, MCP servers, apps

None.

## Detailed Implementation

Paths are relative to the repository root. "Moved" means `git mv`, so history follows the file. "The owner" is the person who asks for a check or design.

### Order of work

| Phase | Work | Sections | Must pass |
|---|---|---|---|
| 0 | Write every eval case the specs name (14 `cli-behavior`, 1 new `menu-design`), and copy the nine existing cases to `evals/menu-design/`, before the owner sets Approved | §4 evals, §2 evals | `bin/gate tests/unit/test_specs.py tests/unit/test_evals.py::test_each_skill_has_eval_cases` (`test_specs.py` requires the cases of an approved change) |
| 1 | Shared resources, the rename, and `tree.py` to the standard, together | §1, §2 | `bin/gate tests/unit/test_cli_naming.py tests/unit/test_link_integrity.py` |
| 2 | The behavior standard, `behavior.py` and its tests | §3 | `bin/gate tests/unit/test_cli_behavior.py` |
| 3 | The `cli-behavior` skill | §4 | `bin/gate tests/unit/test_frontmatter.py tests/unit/test_skill_load_limits.py tests/unit/test_manifests.py tests/unit/test_images.py` |
| 4 | Manifests, README, docs, AGENTS.md, distributions | §5 | `bin/gate` except the orphan-eval test, which waits for phase 6 |
| 5 | Host runs and the two live proofs, recorded in `TESTING.md` | §6 | the proofs in §6 |
| 6 | Archive the change; delete `evals/agent-interface/`; open the pull request | §7 | `bin/gate` and `bin/gate tests/integration` |
| 7 | After merge: tag and release 0.2.0 | — | the release workflow |

From phase 0 to phase 5, `test_no_orphan_eval_folders` fails: `evals/menu-design/` and `evals/cli-behavior/` exist before their skills (until phases 1 and 3), and `evals/agent-interface/` outlives its skill because the current spec names it until archive. Archiving is the branch's last commit, so the pull request's head passes `bin/gate`.

### 1. Shared resources

*   `resources/cli-naming.json` (moved from `skills/agent-interface/references/cli-naming.json`): the naming vocabulary, unchanged in content. Moves because `cli-behavior` reads its verbs to give each command a kind.
*   `resources/command-tree.md` (new): how both skills build a tree. Holds the tree file's fields and example (from `skills/agent-interface/references/tree-format.md`), the repo-root paragraph (`remediation.md` line 3), and all six subsections of "Building the tree" (Inputs, Reading argv paths, Kind renamed "Entry kind", Merging catalog and source, Sources that cannot be read, Rebuilding), from `skills/agent-interface/references/remediation.md`. "Rebuilding" keeps its meaning: copy the existing tree's `local_verbs`. The `invalid-tree` error text becomes `INVALID_ARGUMENT`. The mention of `cli-naming.md` becomes plain text, since that file stays in `menu-design`.
*   `resources/README.md`: replace "There are no shared resources yet" with a list of the two files and which skills read them.

### 2. `menu-design` (moved from `skills/agent-interface/`)

*   `skills/menu-design/SKILL.md`:
    *   Frontmatter `name: menu-design`. The description keeps its triggers for names and adds "Not for how a CLI behaves for agents (output, errors, paging, prompts); that is the cli-behavior skill." The heading becomes "Menu Design".
    *   Links become `../../resources/cli-naming.json` and `../../resources/command-tree.md` in place of the moved references.
    *   Step 3: use the result only when `tree.py` exits 0 with the success envelope on stdout. On exit 2 with `INVALID_ARGUMENT` caused by the tree, fix the tree and run again. On any other failure, report the failure envelope's `message` and stop.
    *   Step 4: group `data.findings` by `severity` for the counts, as today.
    *   The script path becomes `skills/menu-design/scripts/tree.py`.
*   `skills/menu-design/agents/openai.yaml`: `display_name: "Menu Design"`; short description unchanged.
*   `skills/menu-design/assets/icon.svg`: moved unchanged.
*   `skills/menu-design/references/cli-naming.md`: links to `../../../resources/cli-naming.json`; its links to `tree-format.md` (lines 5 and 110) point to `../../../resources/command-tree.md`.
*   `skills/menu-design/references/remediation.md`: the repo-root paragraph and "Building the tree" are replaced by a link to `../../../resources/command-tree.md`. Caller search and the rename map stay. Line 143 takes `standard_version` from the check's `data`.
*   `skills/agent-interface/references/tree-format.md`: deleted; its content is in `resources/command-tree.md`.
*   `skills/menu-design/scripts/tree.py`:
    *   Reads the vocabulary from `resources/cli-naming.json`, three folders above the script.
    *   A completed check exits 0 with `{"schema_version": 1, "ok": true, "data": {...}}`, where `data` holds `standard_version` and `findings`.
    *   Failures print the failure envelope on stdout as in the Technical Plan.
*   `tests/unit/test_cli_naming.py`: `SKILL` and `VOCAB` paths updated. Changed tests: `test_internal_error_exits_2` (copies the script into `tmp/skills/menu-design/scripts` with `tmp/resources/cli-naming.json`; expects `INTERNAL`, exit 1), `test_closed_stdout_exits_2` (expects `INTERNAL`, exit 1), `test_runs_on_the_system_python` (expects exit 0), `test_usage_error_exits_2` (expects `INVALID_ARGUMENT`), `assert_error` (reads the envelope from stdout and allows `schema_version`, `retryable`, `next_action`), `test_findings_carry_the_contract_fields` and every `env["data"]` read (now `env["data"]["findings"]`).
*   `evals/menu-design/` (copied in phase 0 from `evals/agent-interface/`): the nine cases. The two `no-skill.md` graders (`ignores-ordinary-cli-use`, `ignores-unrelated-request`) change their pattern from `agent-interface` to `menu-design`. New case: `leaves-behavior-to-cli-behavior`.

### 3. The behavior standard and its script

*   `skills/cli-behavior/references/cli-behavior.json` (new): `version: 1`; `kinds` (each verb mapped to `read`, `write` or `long-running`); `rules`, each with `id`, `applies_to` (`"all"`, `{"kinds": [...]}` or `{"verbs": [...]}`), `form`, `severity` and `tests`; `idempotency` (verbs that take `--idempotency-key`, verbs safe by end state); `error_codes`, each with `retryable` (`true`, `false` or `"command"`), `exit` and `when`; `severities` in order; `envelope` and `error_object` field lists; `example_success`, `example_failure`; paging defaults (`limit` 20, `max` 100).
*   `skills/cli-behavior/references/cli-behavior.md` (new): one `## <rule-id>` heading per rule with the prescribed form, an example, and "Reason:" in the style of `cli-naming.md`, written as bullet lines; the severity scale; the code table. Each heading is the rule id, matching a result's `rule` value.
*   `skills/cli-behavior/references/output-files.md` (new): field-by-field formats of `docs/cli-behavior.json` and the register, the layout of `docs/cli-behavior-plan.md` (full-compliance part, then optional deviations by command and rule), and the layout of `docs/cli-contract.md`.
*   `skills/cli-behavior/references/deviation.schema.json` (new): JSON Schema (draft 2020-12) for the register file: `standard_version` and `deviations`, each entry with the fields of the Technical Plan; `evidence` has `minItems: 1`; `work` requires `standard` and `deviation`; `decided` is required by an `if`/`then` on `status`.
*   `skills/cli-behavior/scripts/behavior.py` (new, standard library only): `contract create` and `result check` as in the Technical Plan. It reads `resources/cli-naming.json` three folders above the script. Failures print the failure envelope on stdout: invalid input is `INVALID_ARGUMENT`, exit 2; anything unexpected is `INTERNAL`, exit 1.
*   `tests/unit/test_cli_behavior.py` (new):
    *   every verb in `resources/cli-naming.json` has a kind, and every synonym's verb does;
    *   every rule has a severity from the scale, a valid `applies_to`, at least one test, and a `## <rule-id>` heading in `cli-behavior.md`;
    *   `contract create` run twice on the same tree gives identical bytes and covers every covered command; on two unrelated trees, the envelope fields, error fields, codes and flag names are the same (Goal 1); the contract contains the stdin-closed test and the over-one-page test; `--dry-run` writes nothing;
    *   `contract create` on the trees of evals/cli-behavior/designs-behavior-contract and designs-contract-from-tree gives a contract that every content grader's pattern in those cases matches, so the graders track the real standard;
    *   aliases, stubs, MCP-only entries and root commands get no section and need no results; an unlisted verb is `write` in the contract;
    *   `result check` on a valid file exits 0 with counts and findings in order; it accepts a `deviation` with an `accepted` entry and does not count `proposed` or `declined` entries as deviations;
    *   `result check` rejects, in one `INVALID_ARGUMENT` failure: a rule with a command left uncovered, a status other than `not_applicable` for a command outside the rule's `applies_to`, a missing field per status, evidence that is not `path:line` or past the end of the file, a `deviation` with no accepted entry, a register entry with a missing field, an unknown rule or an uncovered command;
    *   both scripts' failures are one envelope on stdout, with no JSON on stderr.
*   `tests/integration/test_install.py`: assert that the Codex install contains `resources/cli-naming.json`. The live Codex probe now picks `cli-behavior` (alphabetically first, line 16) and reads a bulleted line from its references (lines 69-71), which `cli-behavior.md` provides.

### 4. The `cli-behavior` skill

*   `skills/cli-behavior/SKILL.md` (new, under 24,000 bytes):
    *   Description: triggers on checking or designing how a CLI behaves for agents (machine output, errors, paging, prompts, retries, "is my CLI ready for agents", a generic "check my CLI"); not for command names (menu-design), ordinary CLI use, building an MCP server, or unrelated questions.
    *   Hard limits: never run or import the target CLI; never edit it; never quote a secret value in any file it writes, cite `file:line` only; write only `docs/cli-tree.json` (when none exists), `docs/cli-contract.md`, `docs/cli-behavior.json`, `docs/cli-behavior-plan.md` and `docs/cli-behavior-deviations.json`, where it writes `proposed` entries and changes an entry's status only on the owner's explicit instruction.
    *   Steps for design: find or build the tree with `../../resources/command-tree.md`; run `contract create`; reply with the path.
    *   Steps for check: find or build the tree; read each command's handler and record results, grouping commands that share a handler; mark what source cannot prove `unknown` with its test; run `result check`, at most three times; write the plan, including the caller search; replace the register's `proposed` entries; reply with counts, failing findings worst first, the plan path, the options by command and rule, and, for a generic request, that names were not checked.
    *   When to propose a deviation: only when a task the standard form makes worse can be named and evidenced; fill every schema field; never mark an entry `accepted` or `declined` without explicit instruction from the owner; never propose again a command and rule that have a `declined` entry.
    *   With no CLI named, ask which and write nothing.
*   `skills/cli-behavior/agents/openai.yaml` (new): `display_name: "CLI Behavior"`, short description "Check and design how a CLI behaves for agents", `icon_small` and `icon_large` `./assets/icon.svg`, and the existing `brand_color`.
*   `skills/cli-behavior/assets/icon.svg` (new): colors from `assets/brand.json` only, `viewBox="0 0 24 24"`, a `<title>`.
*   `evals/cli-behavior/<case>/prompt.md` and `graders/*.md` (new, written in phase 0), one case per scenario: `ignores-ordinary-cli-use`, `leaves-naming-to-menu-design`, `takes-generic-check-request`, `reports-behavior-findings`, `marks-unproven-as-unknown`, `records-not-applicable`, `passes-agent-ready-cli`, `plans-full-compliance`, `offers-no-padding-deviations`, `honors-accepted-deviation`, `accepts-deviation-on-instruction`, `designs-behavior-contract`, `designs-contract-from-tree`, `asks-for-cli-when-missing`. Each prompt creates its small CLI in the working directory, as the existing cases do. Graders that check written files use `file_exists` or a workspace `focus`; graders that check what the agent ran use `tool_used` with `input_match`; none uses `focus: last_message` for a file or transcript check, which made 7 of 10 cases fail in the 2026-10-27 host run.

### 5. Metadata, docs and packages

*   `plugin.json`: `version` 0.2.0; `description` and `longDescription` "Design and check CLI command and MCP tool names against a noun-verb standard, and how a CLI behaves for agents: output, errors, paging, prompts and safe retries."; `shortDescription` "CLI names and agent behavior" (28 characters; `test_manifests.py` allows 30); `capabilities` add "Check CLI behavior for agents" and "Design CLI behavior contracts".
*   `.claude-plugin/plugin.json`: version and description. `.codex-plugin/plugin.json`: version, description and the whole `interface` block. `.claude-plugin/marketplace.json`: both description fields (lines 6 and 11). `bin/gate` fails if any of them differ.
*   `README.md`: tagline from the new description; "Try it" gives one example per skill (`/agent-interface:menu-design`, `/agent-interface:cli-behavior`); the Skills table gets two rows with their icons and absolute GitHub links.
*   `docs/claude.md` (line 8): the files each skill writes. `docs/codex.md` (lines 4-6): `resources/` is read through skill-relative links. `docs/privacy.md` (line 3): two standard-library Python scripts. `docs/harnesses.md` (lines 15-16): `resources/` is read at run time beside `docs/`.
*   `AGENTS.md`: one line: each skill keeps its deviation schema at `references/deviation.schema.json` and its register at `docs/<skill>-deviations.json` in the target repository.
*   `distributions/`: regenerated with `python3 scripts/pack_plugin.py --sync`.

### 6. Proof

*   `bin/gate` and `bin/gate tests/integration` pass.
*   Host run: `claude plugin eval . --runs 1 --no-publish --allow-tools Write Edit Bash` over both skills; the nine cases that passed in the 2026-10-28 host run still pass under `menu-design` (Goal 7); results recorded in `TESTING.md`'s host record. Live Codex: `PLUGIN_LIVE=1 bin/gate tests/integration`, recorded likewise.
*   Live proof 1: the `cli-behavior` check on a scratch copy of the notes toolkit (`/Users/henry/Developer/agent-toolkits/toolkits/notes`, the naming proof's target; commit recorded in `TESTING.md`), end to end; `result check` accepts the results; every failing finding's `file:line` exists; the share of unknown results is recorded (the Open Question's first number). The owner then applies one fix, and a re-check shows that finding passes (CUJ 3). Outputs are kept in `~/.local/share/agent-artifacts/agent-interface/`, as the naming proof's were.
*   Live proof 2: the check on scratch copies of `tree.py` and `behavior.py`, one repository per script under `/private/tmp/agents/agent-interface/self-check/`, each with its own tree, reports no failing findings. `docs/*.md` ships in every package, so this run never writes into this repository.

### 7. OpenSpec

*   `openspec/changes/cli-behavior-standard/design.md`: this document.
*   `openspec/changes/cli-behavior-standard/tasks.md`: the phases above as checkboxes, each naming its proof.
*   At archive: `openspec/specs/menu-design/spec.md` and `openspec/specs/cli-behavior/spec.md` created, `openspec/specs/agent-interface/spec.md` removed, `evals/agent-interface/` deleted, the change moved under `openspec/changes/archive/`.

## Risks

| Risk | Impact | Mitigation or acceptance |
|---|---|---|
| The schema forces fields to be present, not their content to be sound | "harm: users prefer tables" passes validation | Required `evidence` (a `file:line` or caller) raises the bar; the owner is the final filter. Accepted. |
| Change size: a rename, a skill, a register, files moved to `resources/`, `tree.py`'s output | regressions in `menu-design` | Goal 7 is shown in a host run, not assumed; phase checkpoints name the tests. |
| `tree.py` exits 0 instead of 1 when violations are found | a caller gating on the exit status stops failing | Callers are this repository's tests and skill text only (`bin/gate` runs pytest; no workflow calls `tree.py`); both change in phase 1. |
| New eval graders have not run | a case passes or fails for grader reasons | Graders follow the types in §4; the first host run checks them, and a failing grader is fixed before the pull request. |
| Eval folders during the build | `test_no_orphan_eval_folders` fails from phase 0 until the archive | Each phase names the tests it must pass; archive is the branch's last commit, so the pull request's head passes `bin/gate`. |
| Overlapping triggers between the two skills | a request reaches the wrong skill | Routing scenarios on both sides (`leaves-naming-to-menu-design`, `leaves-behavior-to-cli-behavior`, `takes-generic-check-request`). |
| The check reads arbitrary source in the target repository | a secret could be quoted into a written file | Hard limit: never quote a secret value; cite `file:line` only. |
| The live proof would write into agent-toolkits | unwanted files in another repository | It runs on a scratch copy; outputs go to `~/.local/share/agent-artifacts/agent-interface/`. |
| Two standards until agent-toolkits is redesigned (hsb3/agent-toolkits#98) | toolkits built with agent-toolkit-standards fail parts of this check | Expected; accepted until the redesign. |
| Unknown ceiling (Open Questions) | the check may be mostly unknown on some CLIs | The notes-toolkit run records the first share. |

## Alternatives rejected

### Scope and ownership

*   **Expand the existing `agent-interface` skill to cover behavior.** One skill, one entry point. Rejected by the owner: one skill per job.
*   **Adopt agent-toolkit-standards §2.5 to §2.7 as the behavior standard.** No new standard to write. Rejected: those rules leave the form open ("pagination on by default", "`dry_run` support where feasible"), cover only toolkits built with that kit, and nothing checks a CLI against them. Two agents following them still produce two envelopes.
*   **Adopt the Command Line Interface Guidelines (clig.dev).** A published, widely read guide. Rejected: it is written for people at a terminal and leaves machine output forms open, so it does not fix the envelope, codes or flags.
*   **The prototype's checklist ("pick the options the task needs").** Rejected: leaving the choice to each run is what produced the divergence.

### Evidence

*   **Check a hand-written declaration of the CLI's contract (the prototype's `audit.py`).** Deterministic; needs no source reading. Rejected: it proves only what was declared, not what the code does.
*   **Run the CLI against a disposable fixture.** Would turn many unknowns into proven results. Rejected by the owner: the check reads source only. Unknowns carry the test that would settle them instead.
*   **Detect patterns in source with the script** (`input(` calls, writes to stdout). Rejected: it works for one language, misses patterns hidden in helpers, and its silence is easily read as a pass, which Goal 5 forbids.

### What the script does

*   **The script validates results only; the agent writes the contract by copying the standard.** Smaller script. Rejected: whether two contracts match would depend on the agent copying faithfully, so Goal 1 would hold only when nothing paraphrases.

### Deviations

*   **No deviations: the standard is mandatory.** Every CLI behaves the same. Rejected by the owner: some CLIs need behavior the standard cannot express, such as streaming output, and with no recorded exception they would leave the standard without saying why.
*   **The agent records a deviation whenever it writes a reason.** Rejected: each project's agent could justify its own variant, which brings back the divergence, now with recorded reasons. The agent proposes; the owner decides.
*   **Offer deviations ranked or chosen by the work they save.** Rejected by the owner: an option exists only to make the CLI better to use; work is stated so the owner can allocate effort, not used to pick.
*   **One register shared by both skills, in `resources/`.** One mechanism. Rejected by the owner: each skill has its own focus and carries its own schema and register.
*   **Options in the plan only, with an accepted-only register** (O2). Fewer statuses. Rejected by the owner: an option's reasoning would not be checked until accepted.
*   **Validate registers with a JSON Schema library.** Exact match with the schema file. Rejected: it adds a runtime dependency to scripts that use only the standard library; the script reads the schema's required fields and allowed values itself.

### Shared files

*   **Each skill bundles its own copy of the naming verbs and tree format, with a gate test against drift.** Self-contained skills. Rejected: `AGENTS.md` makes `resources/` the single source for anything more than one skill reads, and the gate can compare fields but not the wording of the building steps.
*   **`cli-behavior` reads `menu-design`'s reference files by path.** No copies, no move. Rejected: one skill would depend on another's internal layout.

### The standard's forms

*   **Error object on stderr, as the last line** (O3). Keeps the usual "errors to stderr" habit. Rejected: anything printed to stderr after the error (a shutdown warning, a library's exit message) leaves a last line that is not JSON.
*   **Error object anywhere on stderr, beside logs** (the first draft). Rejected: the agent must search log text for one JSON object, the scraping the standard exists to remove. With `--json`, stdout always holds one document instead, at the cost of a top-level handler and a usage-error override in every CLI.
*   **`retryable` worked out by one formula, or dropped** (O4). Rejected by the owner in favor of fixed values, with the command setting the three codes where it may already have acted.
*   **`--format json` or `--output json` instead of `--json`.** Room for more formats later. Rejected: the standard has one machine format, and a second flag value is a choice the standard exists to remove.
*   **Offset paging (`--offset`, `--page`).** Simple to implement. Rejected: rows inserted or deleted between pages shift the offset, so rows are skipped or repeated, a `data`-severity failure.
*   **`--force` instead of `--yes`.** Common in some tools. Rejected: `--force` often also means "override a safety check", so it does two jobs; `--yes` only answers the confirmation.

### Routing and the plugin's own scripts

*   **For a generic "check my CLI", ask which check.** Rejected: it costs the same extra turn as the chosen path, and delivers nothing in the first reply.
*   **For a generic request, run both checks.** The most complete reply. Rejected: one skill would have to invoke the other, which Codex documents no way to do, and it ties the two skills together.
*   **Leave `tree.py` for a later change.** Smaller change. Rejected: see "The plugin's own scripts".
*   **A reviewer agent, hooks or an MCP server (the prototype's delivery).** Rejected: the 2026-10-27 brainstorm decided against a reviewer agent, and `AGENTS.md` keeps hooks and servers out of runtime packages unless a design needs them; this one does not.

## Review

2026-10-28: consolidated EGM review (stages 5-9, fresh-context reviewers) with owner decisions O1-O4 and the remaining fixes applied by auto accept. Reports in `.dev/egm/` (local, gitignored): `consolidated_review_report.md` (actions, owner decisions, resolution log) and `goldfish_review_report.md` (per-action classification). Contested and not applied: `--fail-on` (no CI step calls `tree.py`), a `counts` field in `tree.py` (the skill groups findings), per-entry versioning and stale-evidence hashes, CLI-wide deviations, a separate decisions list, and a risk about target repositories publishing `docs/` (the skill already writes `docs/cli-tree.json` there). Remaining wording nits were recorded and left.
