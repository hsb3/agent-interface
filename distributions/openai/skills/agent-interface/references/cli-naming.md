# CLI and MCP naming rules

Every CLI command and MCP tool name is a noun, then a verb: `tool issue list` and `issue_list`. One grammar lets a reader guess a name they have not seen.

[cli-naming.json](cli-naming.json) holds the verbs, synonyms, short forms, plural exceptions and root commands. `tree.py check` applies these rules to a command tree ([tree-format.md](tree-format.md)) and puts the rule id in each finding's `rule` field. A violation fails the check. An advisory is reported and does not. A finding about a command carries its `source`; `collision` and `incomplete-tree` have `source: null`.

## Verbs

### `approved-verbs`

The verb must be an approved verb or a local verb. `synonym` (violation) is an automatic synonym; the check proposes the approved verb. `unlisted-verb` (advisory) is in no list; no name is proposed.

Reason: one verb per meaning, so `list` never competes with `ls`.

### `confirm-only-synonyms`

A confirm-only synonym gets `confirm-synonym` (advisory). No name is proposed; the owner decides.

Reason: these words can change meaning. `set` is not always `update`.

## Nouns

These rules apply to CLI nouns only.

### `noun-singular`

Use the singular. A noun ending in `s` that is not a plural exception gets `plural` (advisory). No name is proposed.

Reason: a trailing `s` can be part of the word (`status`), so it is never removed on the check's own authority.

### `noun-full-word`

Use the full word, except a listed short form that is the common name (`repo`). The long form of a listed short form gets `long-form` (violation); the check proposes the short form. Unlisted abbreviations are the owner's call.

Reason: one spelling per noun.

### `noun-hyphenated`

Hyphenate multi-word nouns: `work-item`. An underscore in a CLI noun gets `underscore-in-noun` (violation); the check proposes the hyphenated noun. MCP names use an underscore (`work_item_list`).

Reason: in an MCP name the underscore separates noun from verb, so a CLI hyphen keeps the same noun one word.

### `noun-not-verb`

A noun must not be an approved verb: `job`, not `run`. Only the whole noun counts, so `sync-state` passes. The finding is `noun-is-verb` (violation); no name is proposed.

Reason: `tool run run` cannot be read.

## Tree shape

### `tree-noun-verb`

A CLI uses flat commands (`tool list`) or `tool noun verb`, not both. If it has both one-word and two-word commands, each one-word command gets `mixed-shape` (violation), even with one noun. No name is proposed. Stubs, aliases, root commands and `depth` violations are not counted. A one-noun CLI may be all flat. MCP names always keep the noun (`note_list`).

Reason: a reader who has seen one command should know where the next is.

### `tree-depth`

A path has at most two words. A longer path gets `depth` (violation) and is not classified further. No name is proposed. Paths starting with a root command are skipped, so exempt.

Reason: the standard has no area level yet.

## Names in one set

### `collisions`

If two proposed names are equal, or a proposed name is already a command, those proposals are dropped and one `collision` (violation) names the target. No name is proposed. "Already a command" covers every CLI path and MCP name in the tree, stubs, aliases and root commands included. A stubbed name is never reused.

Reason: a rename must not replace another command.

### `complete-tree`

A tree with `complete: false` gets `incomplete-tree` (advisory), `path` `""`, and the sources read in the message. No name is proposed.

Reason: a clean result on a partial tree is a false all-clear.

## MCP names

### `mcp-noun-verb`

An MCP name is `noun_verb`: the verb is the last word and the noun is everything before the last underscore. A last-word verb is then checked as for a CLI path, under `approved-verbs` or `confirm-only-synonyms`. The findings are:

- `verb-first` (violation), as in `list_notes`. The check proposes `note_list`, removing a trailing `s` from the noun unless it is a plural exception. This is the only place a trailing `s` is removed, because the name changes anyway and the owner reviews the plan. A leading automatic synonym is replaced by its verb (`ls_notes` gives `note_list`). A leading confirm-only synonym gets no proposal, plus `confirm-synonym`.
- `verb-not-last` (advisory): a middle word is a verb (`issue_list_all`). No name is proposed.
- `ambiguous` (advisory): the first and last words are both verbs or neither is (`check_run`, `random_id`). No name is proposed.
- `no-noun` (advisory): no underscore (`slugify`). No name is proposed.

Reason: the same grammar as the CLI.

## How names are classified

Words are looked up in the lists, never judged by position. A CLI path of one word is a flat command whose word is the verb; two words are `noun verb`. For an MCP name, a word is a verb if it is an approved verb, a synonym of either kind, or a local verb. The first matching row wins:

| Order | Case | Result |
| --- | --- | --- |
| 1 | No underscore | `no-noun` |
| 2 | A middle word is a verb | `verb-not-last` |
| 3 | Last word is a verb, first is not | `noun_verb` |
| 4 | First word is a verb, last is not | `verb-first` |
| 5 | Both or neither | `ambiguous` |

When one command has several renaming findings, each proposes the fully fixed name (`work-item list`); they do not collide with each other.

## Root commands, stubs and aliases

The check skips entries of kind `stub` or `alias`, and entries whose CLI path starts with a root command. Root commands are never checked or renamed; `serve` is one because MCP clients launch servers with `<tool> serve`. To open the MCP Inspector on the tool's own server, use the flag `<tool> serve --inspect`, not an `inspect` command. Only the path is skipped: an `mcp_name` on a root-command entry is still checked. A framework alias (argparse `aliases=`, commander `.alias()`) is recorded as `kind: alias` pointing at its command, so `ls` as an alias of `issue list` is skipped rather than proposed as a rename onto a command that already exists.

## Local verbs

A tree's `local_verbs` ([tree-format.md](tree-format.md)) are words approved for that CLI only.

- Only the owner decides that a word becomes a local verb.
- The agent writes it on the owner's answer, never on its own to silence a finding.
- A confirm-only synonym the owner keeps goes in `local_verbs` (`set` for `config set`).

Reason: a local verb leaves the standard, and only the owner can decide that.

## Adding a verb to the shared list

A new verb must not be a synonym of an existing verb, and at least two CLIs must need it. Record `added` (date) and `needed_by` (CLIs) in [cli-naming.json](cli-naming.json). The two-CLI rule also applies when promoting a local verb.

## Renames

- **One step per CLI.** Rename the command, update every caller found, and install a permanent stub, all in one commit.
- **Permanent stub.** Hidden from `--help`, no stdout, exit 2, and `renamed to: <new argv>` on stderr. The tree records it as `kind: stub`. It stays as the lasting record, and the old name is never reused.
- **Working alias.** Only for a caller that cannot be edited yet. Same stdout and exit code as the new command, and `renamed to: <new argv>` on stderr. The tree records it as `kind: alias`.
- **MCP hard cut.** Rename the tool with no alias tool, and update the tool list, tiers, snapshots and permission entries together.
- **Renames are pure.** A rename that also changes behavior or arguments is a separate change.

Finding callers and writing the rename plan: [remediation.md](remediation.md).
