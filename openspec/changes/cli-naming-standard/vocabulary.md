# Starter vocabulary and rules (approved)

The owner approved this on 2026-10-27 as the starting content for `skills/agent-interface/references/cli-naming.json` (the only list) and `skills/agent-interface/references/cli-naming.md` (the rules, which link to the list). It was committed here from the brainstorm's local notes so that a fresh clone can build the change. After the build, those two files are canonical and this file is history.

## Approved verbs (13)

| Verb | Means | Automatic synonyms (renamed by the check) | Confirm-only synonyms (reported, never renamed) |
| --- | --- | --- | --- |
| `list` | many records, paged | `ls`, `all` | `find` |
| `get` | exactly one result or an error, by any unique key | `view`, `info`, `describe`, `read` | `show`, `cat` |
| `search` | free-text query, ranked results | | |
| `create` | make a new record | `new`, `make` | `add` |
| `update` | change an existing record | `modify`, `patch` | `set`, `edit` |
| `delete` | remove a record | `rm`, `remove`, `del`, `destroy` | |
| `run` | execute something once and wait | `exec`, `execute`, `do` | |
| `start` | begin something that keeps running | `up`, `launch` | |
| `stop` | end something started | `down`, `kill`, `halt` | |
| `check` | inspect and report problems, change nothing | `lint`, `validate`, `verify` | |
| `sync` | make two copies match | | `pull`, `push`, `refresh` |
| `import` | bring data in from a file or service | `load`, `ingest` | |
| `export` | write data out to a file or service | `dump` | `save` |

`search` was added on 2026-10-27, because vault (`search_notes`) and notes (`note_search`) need it.

**Adding a verb:** it must not be a synonym of an existing verb, and at least two CLIs must need it. Each added verb records `added` (date) and `needed_by` (CLIs) in the JSON list.

**Confirm-only synonyms** can change meaning (`set` is not always `update`), so the check reports them for the owner to decide and never proposes a rename.

**Renames are pure:** a rename that also changes behavior or arguments is a separate change.

## Root commands (never checked or renamed)

`help`, `version`, `completion`, `serve`, `setup`, `init`, `doctor`, `update`. `serve` is exempt because MCP clients launch servers with `<tool> serve`. `doctor` (the tool's own health check) and `update` (update the tool itself) are added on 2026-10-27 by the owner; `update` stays an approved verb under a noun (`note update`). Opening the MCP Inspector on the tool's own server is the flag `<tool> serve --inspect`, not an `inspect` command (owner, 2026-10-28).

## Local verbs

A tree file may declare `local_verbs`: words the check treats as approved for that CLI only. A function-library CLI declares its own verbs here, for example `core` with `encode`, `parse`, `hash` and `round`. When the owner decides to keep a confirm-only synonym, the word is recorded here too, for example `set` for `config set`. Only the owner adds local verbs; the agent never adds one to silence a finding. The two-CLI rule applies only when promoting a local verb into the shared list.

## Noun form

1. **Singular:** `issue`, not `issues`. A noun ending in `s` that is not in `plural_exceptions` (`status`, `alias`, `process`, `address`) gets a `plural` advisory with no proposed name. A trailing `s` is never removed on its own authority.
2. **Full word:** a short form is allowed only when it is the common name (`repo`). Allowed short forms are listed in `short_forms`, which maps each short form to its long form (`"repo": "repository"`). The check flags the long form when a short form is listed. Unknown abbreviations are not checked; the owner judges them.
3. **Multi-word nouns are hyphenated:** `work-item`. In MCP names the hyphen becomes an underscore inside the noun (`work_item_list`). An underscore inside a CLI noun is a violation.
4. **No noun is also an approved verb:** not `run`, `check` or `sync` as nouns; use `job`, `report` or `sync-state`. The rule applies to the whole noun, so `sync-state` passes.

## Tree shape

5. **Two or more nouns:** `tool noun verb`. Mixing flat leaves (`tool list`) and noun-verb leaves (`tool issue list`) in one CLI is a violation.
6. **One noun:** the flat form (`tool list`) is allowed, not required. MCP names always keep the noun (`note_list`).
7. **No deeper levels in v1:** any command path longer than `noun verb` is a violation. A later grammar trial may allow an area level (`tool area noun verb`) for CLIs with more than 50 leaf commands. Until then the check counts no leaves.

## Classifying CLI paths

The check skips commands of kind `stub` or `alias`, and commands whose first word is a root command. For every other command:

- A one-word path is a flat leaf, and its word is the verb. A two-word path is `noun verb`. A path longer than two words is a `depth` violation and is not classified further.
- The verb word is looked up in this order: approved verb or local verb (passes), automatic synonym (`synonym` violation, proposes the verb), confirm-only synonym (`confirm-synonym` advisory), otherwise `unlisted-verb` advisory.
- The noun is checked against noun-form rules 1-4.

## Classifying MCP names

The check splits a name on `_` and looks each word up. A word counts as a verb if it is an approved verb, a synonym of either kind, or a local verb. The first matching row wins:

| Order | Case | Example | Result |
| --- | --- | --- | --- |
| 1 | No underscore | `slugify` | `no-noun` advisory |
| 2 | A middle word is a verb | `issue_list_all` | `verb-not-last` advisory; no proposed name |
| 3 | Last word is a verb, first is not | `issue_list`, `work_item_list` | `noun_verb`; the noun is everything before the last underscore, and its verb is then checked as for CLI paths |
| 4 | First word is a verb, last is not | `list_notes` | `verb-first` violation; proposes the noun followed by the verb, with a trailing `s` removed from the noun unless it is a plural exception: `note_list` |
| 5 | Both or neither | `check_run`, `random_id` | `ambiguous` advisory; no proposed name |

A verb is always exactly one word. A verb-first rename is the one place a trailing `s` is removed, because the name changes anyway and the owner reviews the plan.

## Severities

| Code | Severity | Proposes a name |
| --- | --- | --- |
| `synonym` | violation | yes: the approved verb |
| `verb-first` | violation | yes: `noun_verb` |
| `underscore-in-noun` | violation | yes: the hyphenated noun |
| `long-form` | violation | yes: the listed short form |
| `noun-is-verb` | violation | no |
| `depth` | violation | no |
| `mixed-shape` | violation | no |
| `collision` | violation | no |
| `confirm-synonym` | advisory | no |
| `unlisted-verb` | advisory | no |
| `ambiguous` | advisory | no |
| `verb-not-last` | advisory | no |
| `no-noun` | advisory | no |
| `plural` | advisory | no |
| `incomplete-tree` | advisory | no |

**Collisions:** if two proposed names are the same, or a proposed name is already a command, both findings keep their codes but lose their proposed names, and one `collision` finding names the target. Only violations that propose a name go into a rename plan.

## Finding details

Settled 2026-10-27 during the build, where the rules above left a case open:

- **`source`:** each command in the tree carries a `source` holding one `sources[].ref`; a finding about a command copies it. Findings about the whole tree (`incomplete-tree`, `collision`) have `source: null`.
- **Several renaming violations on one command** (`work_item ls` is both `underscore-in-noun` and `synonym`): every such finding proposes the fully fixed name (`work-item list`). The collision rule compares proposed names across different commands only, never a command's findings with each other.
- **`mixed-shape`:** only when the CLI has both one-word and two-word leaves, counting only commands that are not skipped and not `depth` violations. One finding per one-word leaf, with `path` set to that leaf.
- **`collision`:** `path` is the target name, `source` is `null`, `rule` names the collision rule. "Already a command" covers every `path` and `mcp_name` in the tree, including stubs, aliases and root commands, since a stubbed name is never reused.
- **MCP nouns:** not checked against noun-form rules in v1. The only noun change in an MCP name is the trailing-`s` removal in a verb-first suggestion.
- **Verb-first name starting with a synonym:** an automatic synonym is replaced by its verb in the suggestion (`ls_notes` → `note_list`), as one `verb-first` finding. A confirm-only synonym (`show_notes`) gives a `verb-first` finding with no proposed name, plus a `confirm-synonym` advisory.
- **Local verbs in MCP names** count as verbs, so `encode_list` in a CLI with `local_verbs: ["encode"]` is `ambiguous`.
- **Root commands:** the whole entry is skipped only by its `path`; an `mcp_name` on a root-command entry is still classified.
- **One name space:** collisions compare CLI paths and MCP names as one set of names.

## Renames

- **One step per CLI:** rename the command, update every caller the search finds, and install a permanent stub for the old name, all in one commit. A working alias is used only for a caller that can't be edited right away. It gives the same stdout and exit code and prints `renamed to: <new argv>` on stderr, and it is recorded in the tree as `kind: alias`.
- **Stub:** hidden from `--help`, writes nothing to stdout, exits 2, and prints `renamed to: <new argv>` on stderr. The tree marks it `kind: stub`, and the check skips it. A stubbed name is never reused. Because the stub stays in the CLI's code, it is the lasting record of the rename.
- **MCP tools:** hard cut, meaning the tool is renamed with no alias tool. `toolkit.json` tools, tiers, toolsnaps and `mcp__` permission entries are updated together.
- **Caller search:** best effort, because the permanent stub catches anything the search misses. The roots are the folders the owner names, or else the defaults in `remediation.md`: `~/Developer`, `~/.claude`, `~/.codex`, `~/.claude.json`, shell rc files, crontab and launchd. Excluded: `dev-memory.me`, session transcripts, plugin caches, `.git`, `distributions/` and `node_modules`; stale names there are what the stub is for. Patterns: the space form (`tool ls`), the argv-list form (`"tool", "ls"`) and the old MCP name.
- **Plan:** `docs/cli-renames.json` in the CLI's repo is rewritten on each fix run. It holds the standard version, the exact search command, and for each rename the old name, the new name and each caller as a `~/`-relative `file:line`. It never holds the matched text, because caller files can hold secrets.
