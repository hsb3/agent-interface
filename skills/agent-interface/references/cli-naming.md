# CLI and MCP naming rules

Every CLI command and MCP tool name follows one grammar: a noun, then a verb. `tool issue list` is a CLI command. `issue_list` is its MCP tool. One grammar means a reader can guess a name they have not seen.

The word lists are in [cli-naming.json](cli-naming.json): approved verbs, synonyms, short forms, plural exceptions and root commands. This file holds the rules and does not repeat the lists. `tree.py check` applies the rules to a command tree ([tree-format.md](tree-format.md)). Each finding it returns names its rule in the `rule` field, using the ids below.

A finding is a **violation** or an **advisory**. A violation fails the check. An advisory is reported and does not fail it. Some findings propose a new name. Others name a problem and leave the choice to the owner.

## Verbs

### `approved-verbs`

The verb must be an approved verb, or a local verb of this CLI.

- `synonym` (violation): the verb is an automatic synonym of an approved verb. The check proposes the approved verb.
- `unlisted-verb` (advisory): the verb is in no list. No name is proposed.

Reason: one verb per meaning, so `list` never competes with `ls`.

### `confirm-only-synonyms`

A confirm-only synonym is reported, never renamed.

- `confirm-synonym` (advisory): no name is proposed. The owner decides.

Reason: these words can change meaning. `set` is not always `update`, and `pull` is not always `sync`.

## Nouns

These rules apply to CLI nouns. MCP nouns are not checked against them.

### `noun-singular`

Use the singular: `issue`, not `issues`. A noun that ends in `s` and is not a plural exception gets a `plural` finding (advisory). No name is proposed.

Reason: a trailing `s` is sometimes part of the word (`status`), so the check never removes it on its own authority.

### `noun-full-word`

Use the full word. A short form is allowed only when it is the common name (`repo`). If the long form is used where a short form is listed, the check reports `long-form` (violation) and proposes the short form.

Reason: one spelling per noun. Abbreviations that are not listed are not checked; the owner judges them.

### `noun-hyphenated`

Write a multi-word noun with a hyphen: `work-item`. An underscore in a CLI noun is `underscore-in-noun` (violation). The check proposes the hyphenated noun. In MCP names the noun uses an underscore (`work_item_list`), so this rule does not apply to them.

Reason: an underscore in an MCP name separates the noun from the verb, and a hyphen in a CLI keeps the noun one argument.

### `noun-not-verb`

A noun must not also be an approved verb. Use `job`, not `run`; `report`, not `check`. The rule applies to the whole noun, so `sync-state` passes. The finding is `noun-is-verb` (violation). No name is proposed.

Reason: `tool run run` cannot be read.

## Tree shape

### `tree-noun-verb`

A CLI uses either flat commands (`tool list`) or `tool noun verb` commands, not both. If it has both one-word and two-word commands, each one-word command is `mixed-shape` (violation). No name is proposed. This holds even with one noun (`list` next to `issue list`). Stubs, aliases, root commands and `depth` violations are not counted.

A CLI with one noun may use the flat form for all its commands. It is allowed, not required. MCP names always keep the noun (`note_list`).

Reason: a reader who has seen one command should know where the next one is.

### `tree-depth`

A command path has at most two words. Paths that start with a root command are exempt, because they are skipped. A longer path is `depth` (violation) and is not classified further. No name is proposed.

Reason: the standard has no area level yet.

## Names in one set

### `collisions`

If two proposed names are the same, or a proposed name is already a command, the check drops those proposals and reports one `collision` (violation). Its `path` is the target name. No name is proposed. The other findings keep their codes.

Already a command means any CLI path or MCP name in the tree, including stubs, aliases and root commands. CLI paths and MCP names share one set of names. A stubbed name is never reused.

Reason: a rename must not hide or replace another command.

### `complete-tree`

The check can only judge the commands it is given. If the tree says `complete: false`, the check reports `incomplete-tree` (advisory) with `path` set to `""`. The message lists the sources read. No name is proposed.

Reason: a clean result on a partial tree would be a false all-clear.

## MCP names

### `mcp-noun-verb`

An MCP tool name is `noun_verb`. The noun is everything before the last underscore. The verb is the last word. The findings are:

- `verb-first` (violation): the name starts with a verb, as in `list_notes`. The check proposes the noun first and the verb last (`note_list`). It removes a trailing `s` from the noun unless the noun is a plural exception. This is the one place a trailing `s` is removed, because the name changes anyway and the owner reviews the plan. If the first word is a confirm-only synonym, the name is flagged with no proposal, plus a `confirm-synonym` advisory.
- `verb-not-last` (advisory): a middle word is a verb, as in `issue_list_all`. No name is proposed.
- `ambiguous` (advisory): both the first and last word are verbs, or neither is (`check_run`, `random_id`). No name is proposed.
- `no-noun` (advisory): the name has no underscore (`slugify`). No name is proposed.

When the last word is a verb, it is checked as for a CLI path. An automatic synonym falls under `approved-verbs`. A confirm-only synonym falls under `confirm-only-synonyms` (`issue_set`).

Reason: the same grammar as the CLI, so `issue list` and `issue_list` are the same command.

## How names are classified

The check looks words up in the lists. It never decides by position alone.

For a CLI path:

1. A one-word path is a flat command, and its word is the verb. A two-word path is `noun verb`.
2. The verb is looked up. An approved or local verb passes. An automatic synonym is a `synonym` violation. A confirm-only synonym is a `confirm-synonym` advisory. Anything else is an `unlisted-verb` advisory.
3. The noun is checked against the noun rules.

For an MCP name, the check splits on `_` and looks up each word. A word is a verb if it is an approved verb, a synonym of either kind, or a local verb. The first row that matches wins:

| Order | Case | Result |
| --- | --- | --- |
| 1 | No underscore | `no-noun` |
| 2 | A middle word is a verb | `verb-not-last` |
| 3 | The last word is a verb and the first is not | `noun_verb`; the verb is then checked as for a CLI path |
| 4 | The first word is a verb and the last is not | `verb-first` |
| 5 | Both are verbs, or neither is | `ambiguous` |

A verb is always one word. A verb-first name that begins with an automatic synonym gets that synonym replaced by its verb in the proposal (`ls_notes` becomes `note_list`).

When one command has several renaming findings, each proposes the fully fixed name (`work-item list`). They are not collisions with each other.

## Finding sources

A finding about a command carries that command's `source` from the tree. A finding about the whole tree (`collision`, `incomplete-tree`) has `source: null`.

## Adding a verb to the shared list

A new verb must not be a synonym of an existing verb. At least two CLIs must need it. Record `added` (the date) and `needed_by` (the CLIs) with it in [cli-naming.json](cli-naming.json). The two-CLI rule also applies when a local verb is promoted into the shared list.

## Root commands, stubs and aliases

The check skips two kinds of entry:

- Entries whose `kind` is `stub` or `alias`. They are old names that point to a new one.
- Entries whose CLI path starts with a root command. Root commands are never checked or renamed. `serve` is a root command because MCP clients launch servers with `<tool> serve`.

Only the path is skipped. An `mcp_name` on a root-command entry is still checked.

## Local verbs

A tree may list `local_verbs` ([tree-format.md](tree-format.md)): words that count as approved for that CLI only. A CLI that is a function library might list its own verbs, such as `encode` or `parse`.

- Only the owner decides that a word becomes a local verb.
- The agent writes it to `local_verbs` on the owner's answer, and never on its own to make a finding go away.
- If the owner decides to keep a confirm-only synonym, record the word in `local_verbs`. For example, `set` for `config set`.
- Keep `local_verbs` when the tree is rebuilt.

Reason: a local verb is a decision to leave the standard, and only the owner can make it.

## Renames

- **One step per CLI.** Rename the command, update every caller found, and install a permanent stub for the old name, all in one commit.
- **Permanent stub.** A stub is hidden from `--help`, writes nothing to stdout, exits 2, and prints `renamed to: <new argv>` on stderr. The tree records it as `kind: stub`. The stub stays in the code, so it is the lasting record of the rename and the old name is never reused.
- **Working alias.** Use an alias only for a caller that cannot be edited right away. It gives the same stdout and exit code as the new command, and prints `renamed to: <new argv>` on stderr. The tree records it as `kind: alias`.
- **MCP tools are a hard cut.** Rename the tool with no alias tool. Update the tool list, tiers, snapshots and permission entries together.
- **Renames are pure.** A rename that also changes behavior or arguments is a separate change.

Finding callers and writing the rename plan are described in [remediation.md](remediation.md).
