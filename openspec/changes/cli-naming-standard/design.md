# Design

Status: Approved
<!-- Draft → In review → Approved. Only the owner sets Approved. -->

## Context

The owner's CLIs and MCP tools were built at different times with different naming habits: `ls`, `list` and `show` for the same job, `verb_noun` MCP names, plural nouns. This change replaces the scaffold's generic file reviewer (`agent-interface-reviewer`) with one naming standard and a deterministic check. A new CLI designed with the skill then passes `tree.py check`, and each existing CLI gets a rename plan.

[proposal.md](proposal.md) states the goals and non-goals, and [the spec delta](specs/agent-interface/spec.md) states the behavior; both are normative for this design. [vocabulary.md](vocabulary.md) holds the approved verbs, synonyms, noun rules, classification rules and severities. The build copies it into the skill's references, and this design does not repeat its lists.

These decisions were settled in the brainstorm and its two review rounds and are not reopened here:

- Every CLI uses noun-verb, and MCP tool names are `noun_verb`. A grammar trial (a later change) may allow an extra area level for CLIs with more than 50 leaf commands; v1 allows no level deeper than `noun verb`.
- The plugin owns its standard and never reads the owner's dev knowledge base.
- Names are classified by looking words up in the verb list, never by their position.
- Each CLI is renamed in one step and keeps a permanent stub for each old name: a hidden command that prints `renamed to: <new argv>` on stderr and exits 2. MCP tools are renamed with no alias or stub.
- No callers exist outside the owner's own machine.

**Downstream:** once this change ships, agent-toolkits adopts this standard (hsb3/agent-toolkits#97). Until then, `agent-toolkit-standards` still prescribes `verb_noun` tool names (`references/standards.md:41`), so toolkits it generates fail this check. That is expected, not a blocker. This plugin depends on nothing in agent-toolkits.

The brainstorm notes stay local under `.dev/egm/` (gitignored). Everything the build needs from them is in `vocabulary.md` and this design.

## Skills

| Skill | Trigger phrases | Must not trigger on | Writes |
| --- | --- | --- | --- |
| `agent-interface` | "check my CLI's command names", "is this CLI noun-verb", "design the commands for a new CLI", "plan renames for `<cli>`", "fix the verbs in `<cli>`", "name these MCP tools" | ordinary CLI use ("list the files here"), building an MCP server or multi-entry-point service (the agent-toolkits plugin's job), writing skills, unrelated questions | `docs/cli-tree.json` and, on fix, `docs/cli-renames.json` in the target CLI's repo |

The skill body only routes, and nothing is written until a target is known:

1. **No CLI named:** ask which one and write nothing.
2. **Build the tree:** following `references/remediation.md`, merge the CLI's MCP catalog (`toolkit.json`, the agent-toolkits catalog file, when it has one) with the command definitions in its source. Record each source read, and mark the tree incomplete when a source could not be read. Rebuilding keeps the existing tree's `local_verbs`. The skill never runs the target CLI.
3. **Check:** run `python3 <script path> check docs/cli-tree.json`. Trust exit 0 or 1 only when stdout parses as the envelope.
4. **Reply:** give the counts of violations and advisories and list each finding with its proposed name. For a confirm-only synonym, ask whether to keep the word. A "keep" is recorded by adding the word to `local_verbs`.
5. **Fix** (steps 2-4, then): run the caller search and write `docs/cli-renames.json` from the violations that propose a name. The skill edits neither the CLI nor its callers.
6. **Design:** write a noun-verb tree from the owner's description that uses only approved verbs, plus local verbs the owner names. Then run steps 3-4. A new CLI with no repo yet uses the working directory as its repo root.

If the host refuses a write in the CLI's repo, for example because of Codex's workspace sandbox, the skill stops and asks the owner to run it from that repo.

## Reviewers

| Persona | Purpose | Claude tools | Fresh context |
| --- | --- | --- | --- |

None. The check is deterministic over a tree that the agent builds and the owner reviews in the git diff. The owner makes every judgment call a reviewer would make: confirm-only synonyms and `local_verbs`. The scaffold's `agent-interface-reviewer` persona, its Claude adapter and its manifest entry are deleted.

## Bundled files

Added:

- `skills/agent-interface/references/cli-naming.json`: the only copy of the vocabulary, built from `vocabulary.md`. Fields:
  - `version`;
  - `verbs`, a map from verb to `{means}`, where verbs added after the first 12 also carry `added` and `needed_by`;
  - `synonyms`, a map from automatic synonym to verb;
  - `confirm_synonyms`, a map from confirm-only synonym to verb;
  - `short_forms`, a map from short form to long form;
  - `plural_exceptions`, a list;
  - `root_commands`, a list.
- `skills/agent-interface/references/cli-naming.md`: the rules in prose, with a one-line reason for each. It links to the JSON and does not repeat its lists.
- `skills/agent-interface/references/tree-format.md`: the tree file's fields and types:
  - Top level: `cli`, `sources` (each with `kind` `catalog` or `source`, and `ref`, a repo-relative path), `complete`, `local_verbs` and `commands`.
  - Each command: `path` (an array of words, or `null` for an MCP tool with no CLI command), `mcp_name` (a string or `null`; at least one of the two is set), `kind` (`command`, `alias` or `stub`), `renamed_to` (an array, required for `alias` and `stub`) and `source` (one `sources[].ref`).
  - The check trusts `kind` as written; the agent sets it from the source.
  - A dispatcher CLI that runs tools as `call <name>` lists each tool by `mcp_name` with `path: null` and leaves out `call`. The reply then says that its names were checked as MCP names only.
  - A CLI whose command paths are generated from a catalog records the paths it actually exposes, with the catalog as their source.
- `skills/agent-interface/scripts/tree.py`: needs only the Python standard library, version 3.9 or later. That is the version macOS ships with the Command Line Tools; nothing here needs 3.11. It has one flat command, `tree.py check <tree.json>`, following the standard it enforces (one noun, `tree`, so the flat form is allowed). It reads `../references/cli-naming.json` relative to its own file. The output contract is under "Check output" below.
- `skills/agent-interface/references/remediation.md`, which covers:
  - building the tree from a catalog and from argparse, click and commander definitions in source, keeping `local_verbs` when rebuilding;
  - the caller search: one `rg --hidden --line-number --fixed-strings` command template over the roots and patterns in `vocabulary.md`, plus `crontab -l` and launchd plists converted with `plutil -convert xml1 -o -`;
  - recording the exact search command;
  - the `docs/cli-renames.json` format: `standard_version`, `search`, and `renames` with `old`, `new` and `callers` as `file:line`, `~/`-relative under the home folder and otherwise relative to the search root, never the matched text. The file is rewritten on each fix run.
- Evals: one case per spec scenario under `evals/agent-interface/<case>/`, nine in all. Each case writes its own small fixture (a Python argparse CLI, or a `toolkit.json`) in the eval workspace, and names that workspace as the caller-search root. Each case's `prompt.md` lists its tools. Cases that run the check, or `ls`, include `Bash`.
- `tests/unit/test_cli_naming.py`:
  - the MCP-name classification table in `vocabulary.md`, with its expected results;
  - a vocabulary consistency test: no synonym of either kind is also a verb or a root command, no synonym appears twice, and every synonym points to an entry in `verbs`;
  - a table of trees in and findings plus exit code out, with at least one row per code in the severities table, exit codes 0, 1 and 2, and an internal error.

Changed:

- `plugin.json` `description` and `interface.longDescription`, then the same text copied by hand into `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`: "Design and check CLI command and MCP tool names against a noun-verb standard, and plan renames that list affected callers."
- `interface.shortDescription` becomes "Noun-verb CLI and MCP naming".
- `interface.capabilities` becomes "Check CLI and MCP names", "Plan renames with callers" and "Design noun-verb commands".
- `skills/agent-interface/agents/openai.yaml` `short_description` becomes "Check CLI and MCP names against a noun-verb standard".
- `skills/agent-interface/SKILL.md`: a description built from the trigger phrases above, and the routing body above.
- `README.md`: the tagline, which drops "and skills"; "Try it", rewritten for checking a CLI; and the skills table.
- `docs/claude.md` and `docs/codex.md`: delete the reviewer-agent paragraphs, including the `/plugin` > Errors note about the ignored `agents/` folder. Say that a skill's `scripts/` resolve against the skill folder, like `references/`.
- `docs/harnesses.md`: delete the personas and adapters paragraph, and the reference to `agents/`.
- `docs/privacy.md`: the plugin now ships a script and searches the folders named for callers. It writes caller locations, never their contents, and sends nothing anywhere.
- `resources/README.md`: remove the `review-checklist.md` row and state that there are no shared resources yet.
- `.claude-plugin/plugin.json`: remove the `agents` entry.
- `TESTING.md`: the behavior tier command adds `Bash` to `--allow-tools`.

Removed:

- `resources/review-checklist.md`
- `agents/agent-interface-reviewer.md`
- `.claude-plugin/agents/agent-interface-reviewer.md`
- `evals/agent-interface/reviews-named-file`, deleted only after this change is archived. Its scenario is in the living spec until then, so deleting it earlier fails the gate.

The vocabulary sits in the skill's `references/`, not in `resources/`: once the reviewer is gone it has one reader, and `AGENTS.md` keeps `resources/` for files with more than one reader. This reverses round 2 decision 12. The packer already ships `skills/*/references/**` and `skills/*/scripts/**`, so the packer does not change.

### Check output

On exit 0 or 1, stdout is `{schema_version: 1, ok, standard_version, data}`:

- `ok` is false exactly when `data` holds a violation.
- `standard_version` is `cli-naming.json`'s `version`.
- `data` holds the findings, sorted by `path` and then `code`. Each finding is `{code, severity, path, message, suggest, rule, source}`:
  - `path` is the CLI path as a space-joined string, or the MCP name;
  - `suggest` is the proposed name, or `null`;
  - `rule` names the `cli-naming.md` rule applied;
  - `source` is the tree `sources[].ref` that the command came from.
- An incomplete tree yields one `incomplete-tree` finding with `path` set to `""` and the sources read listed in `message`.

The codes and their severities are in `vocabulary.md` under "Severities".

| Exit | Meaning | Output |
| --- | --- | --- |
| 0 | no findings, or advisories only | envelope on stdout |
| 1 | at least one violation | envelope on stdout |
| 2 | invalid tree (not JSON, a missing required field, an unknown `kind`) or an internal error | `{ok: false, error: {code, message}}` on stderr, nothing on stdout |

`main` catches every exception and exits 2, so a traceback never looks like exit 1. The error shape follows the proof-of-concept checker's envelope, without its `retryable` and `next_action` fields, which have no use here.

Script path: `${CLAUDE_PLUGIN_ROOT}/skills/agent-interface/scripts/tree.py` in Claude Code, and `scripts/tree.py` relative to the skill folder in Codex.

## Hosts

| Host | In scope | Notes |
| --- | --- | --- |
| Claude Code | yes | Behavior tier via `claude plugin eval` runs every case |
| Codex | yes | Live tier tests that the skill is discovered; the check itself is untested in Codex |
| Antigravity | untested | |

## Image assets

No new images. The skill keeps its existing icon.

## Hooks, MCP servers, apps

None.

## Risks

- **The check covers only commands present in the tree.** A tree built from a catalog alone misses admin commands. The tree records its sources and `complete`, and an incomplete tree produces an `incomplete-tree` finding.
- **The agent can build a wrong tree,** for example with a wrong path or a stub misread as a real command. The check cannot catch this. The owner reviews the tree in the git diff before applying a plan, and every finding names its `source`.
- **The caller search misses some callers,** for example commands built from variables, or files outside the roots. The plan records the search command so it can be rerun, and the permanent stub fails loudly for any caller that was missed.
- **Caller files can hold secrets** (`~/.claude.json`, MCP `env` blocks, shell rc files). The plan records relative `file:line` only, never the matched text, so a pushed repo leaks no file contents.
- **The prose rules and the JSON vocabulary could contradict each other.** The prose never lists vocabulary, and the unit test checks the JSON's consistency.

## Alternatives rejected

- **Choosing the grammar per CLI:** this would undo the uniformity the change exists for.
- **Splitting MCP names by position:** for unmigrated names like `list_notes`, this would make `list` the noun and `notes` the verb.
- **A two-phase rename with a working alias first:** the dev knowledge base is frozen and still holds old names, so the caller search would never come back empty and phase two would never start.
- **A fresh-context reviewer:** every judgment call it would make goes to the owner instead.
- **A plain-text command list instead of a JSON tree:** it cannot mark stubs or sources.
- **Script extractors for argparse and `toolkit.json` (round 2 G13):** this would build a parser framework to guard a tree the owner reads in a diff.
- **Running the target's `--help` as a fallback:** it can run a hand-written CLI's default action. Reading the source is enough for the owner's own CLIs, and an unreadable source is reported as an incomplete tree.
- **A separate `cli-naming-report.md`:** the envelope already holds every finding, so the reply carries them and the run writes nothing outside the CLI's repo.

## Review

<!-- EGM review reports used, findings rejected and why. -->

Brainstorm reviews (not design reviews): `.dev/egm/goldfish_findings.md` (round 1, F1-F22) and `.dev/egm/goldfish_findings_r2.md` (round 2, G1-G27). Round 1 was superseded by round 2's brief. The owner accepted every round 2 recommendation.

Design review on 2026-10-27, with all four feature-spec stages; Stage 9 was skipped because the design has no implementation plan. Reports: `.dev/egm/zoom_out_report.md`, `comprehension_report.md`, `critic_report.md`, `intermediate_zoom_out_report.md`, `consolidated_review_report.md` and `goldfish_review_report.md`. The owner accepted every consolidated recommendation, including scope cuts D1-D5.

Rejected findings:

- **Script extractors and an on-disk `sha256` check (C-M1):** see Alternatives rejected.
- **A schema version on the tree (C-M10):** the tree is rebuilt on every check, so no old tree is ever read.
- **A test that the prose lists no vocabulary (C-N3):** one rule sentence covers it, and a test would add maintenance for little gain.
- **Search bounds and plan merge rules (C-M2, C-M4):** the caller search is best effort, and the stub is the backstop.
- **An empty Reviewers table and Antigravity "untested" (C-N9, C-N21):** both come from the schema's design template.
