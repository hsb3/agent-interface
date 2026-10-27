# Design

Status: Draft
<!-- Draft → In review → Approved. Only the owner sets Approved. -->

## Context

The owner's CLIs and MCP tools were built at different times with different naming habits (`ls`/`list`/`show`, `verb_noun` MCP names, plural nouns). This change replaces the scaffold's generic file reviewer with one naming standard and a deterministic check, so every new CLI starts uniform and existing ones get a rename plan.

Source: the brainstorm brief and two rounds of fresh-context review, `.dev/egm/concepts_brief.md`, `.dev/egm/starter_vocabulary.md`, `.dev/egm/round2_decisions.md` (local, gitignored). Settled there and not reopened here:

- Noun-verb for every CLI; MCP tool names are `noun_verb`. Only a CLI with more than 50 leaf commands may use another structure, and only after a grammar trial, which is a later change.
- The plugin owns its standard and never reads the owner's dev knowledge base.
- Names are classified by looking words up in the verb list, never by position.
- Renames happen in one step per CLI, leaving a permanent stub; MCP renames are a hard cut.
- Solo use: no outside callers.

## Skills

| Skill | Trigger phrases | Must not trigger on | Writes |
| --- | --- | --- | --- |
| `agent-interface` | "check my CLI's command names", "is this CLI noun-verb", "design the commands for a new CLI", "plan renames for `<cli>`", "fix the verbs in `<cli>`", "name these MCP tools" | ordinary CLI use ("list the files here"), building an MCP server or multi-entry-point service (agent-toolkits), writing skills, unrelated questions | `docs/cli-tree.json` and `docs/cli-renames.json` in the target CLI's repo; `cli-naming-report.md` in the working directory |

The skill body only routes: check, fix (check, then plan), or design. Procedures live in `references/`, rules in `resources/`. If no CLI is named, it asks and writes nothing.

## Reviewers

| Persona | Purpose | Claude tools | Fresh context |
| --- | --- | --- | --- |

None. The check is deterministic, and judgment calls (confirm-only synonyms, unknown abbreviations, plurals) go to the owner in the report. The scaffold's `agent-interface-reviewer` persona, its Claude adapter and its manifest entry are deleted.

## Bundled files

Added:

- `resources/cli-naming.json`: the only copy of the vocabulary. Fields: `version`; `verbs` (13, each with meaning, and `added`/`needed_by` for verbs added after the first 12); `synonyms` (renamed automatically); `confirm_synonyms` (reported only); `short_forms`; `plural_exceptions`; `root_commands`; `caller_search` (roots, exclusions, patterns).
- `resources/cli-naming.md`: the rules in prose (noun form, tree shape, name classification, renames, stub contract), linking to the JSON without repeating its lists.
- `skills/agent-interface/scripts/tree.py`: Python standard library only, 3.11 or later. One flat command, `tree.py check <tree.json>`, following the standard it enforces (one noun, flat form). Output is a JSON envelope `{schema_version, ok, standard_version, data: [{code, severity, path, message, suggest, rule, source}]}`. Exit 0 when clean or advisory only, 1 on any violation, 2 on an invalid tree.
- `skills/agent-interface/references/tree-format.md`: the tree file schema. Each command is the path observed (`["issue","list"]`) with `mcp_name`, `kind` (`command`, `alias`, `stub`), `renamed_to`, `hidden`; top level `cli`, `sources` (`kind`, `ref`, `sha256`), `complete`, `local_verbs`.
- `skills/agent-interface/references/remediation.md`: building the tree (merge the catalog or `toolkit.json` with framework definitions in source; `--help` only when neither works, only at root and noun levels, stdin closed, 10-second timeout); running the caller search from `caller_search` with `rg` and recording the exact command; the rename plan format; per-framework notes for hiding a stub (argparse `help=SUPPRESS` with `metavar`, click `hidden=True`, commander `.hideHelp()`).
- Evals: one case per scenario in the spec delta, each writing its own small fixture CLI or `toolkit.json` in the workspace. Cases that run the check allow `Bash`.
- `tests/unit/test_cli_naming.py`: the name-classification table (`issue_list`, `work_item_list`, `list_notes`, `check_run`, `issue_list_all`, `slugify`) and a vocabulary consistency test (no synonym is also a verb, no synonym appears twice, every synonym points to a verb).

Changed:

- `plugin.json` description, then mirrored into `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`: "Design and check CLI command and MCP tool names against one noun-verb standard, and plan renames with their callers." The OpenAI extension's short description and capability line change to match, as does `skills/agent-interface/agents/openai.yaml`.
- `skills/agent-interface/SKILL.md`: new description and routing body.
- `resources/README.md`: lists the two new resources.
- `README.md`: "Try it" and the skills table.
- `.claude-plugin/plugin.json`: `agents` entry removed.
- `TESTING.md`: the behavior tier command adds `Bash` to `--allow-tools`.

Removed: `resources/review-checklist.md`, `agents/agent-interface-reviewer.md`, `.claude-plugin/agents/agent-interface-reviewer.md`, and, after archive, `evals/agent-interface/reviews-named-file`.

Script path: `${CLAUDE_PLUGIN_ROOT}/skills/agent-interface/scripts/tree.py` in Claude Code; the skill-relative path in Codex, per `docs/codex.md`.

## Hosts

| Host | In scope | Notes |
| --- | --- | --- |
| Claude Code | yes | Behavior tier via `claude plugin eval` |
| Codex | yes | Live tier confirms the skill is discovered; the script path is resolved by the agent |
| Antigravity | untested | |

## Image assets

No new images. The skill keeps its existing icon.

## Hooks, MCP servers, apps

None.

## Risks and alternatives

- **The check is only as good as the tree.** A tree built from a catalog alone misses admin commands; the tree records its sources and `complete`, and an incomplete tree is reported.
- **Caller search misses dynamic invocations** (commands built from variables). The plan records the search command so it can be re-run; the permanent stub catches what the search missed.
- **Running `--help` can execute a hand-written CLI's leaf command.** Never run on leaves; last resort only.
- **Two copies of the rules (JSON and prose) could drift.** The prose never lists vocabulary; the unit test checks the JSON's consistency.
- Rejected in the brainstorm: choosing grammar per CLI (undoes uniformity); splitting MCP names by position (garbles every unmigrated name); a two-phase rename with a working alias (the frozen knowledge base means the caller search never comes back empty); a fresh-context reviewer (no judgment the owner doesn't make); a plain-text command list instead of a JSON tree (cannot mark stubs or sources).

## Open for design review

1. Report location: findings go to `cli-naming-report.md` in the working directory, while the tree and plan go into the CLI's repo. Alternative: all three in the CLI's repo.
2. Caller search: done by the agent with `rg` following `remediation.md`, rather than by `tree.py`. Moving it into the script would make it deterministic but would add a second command to the script.

## Review

<!-- EGM review reports used, findings rejected and why. -->

Brainstorm reviews (not design reviews): `.dev/egm/goldfish_findings.md` (round 1, F1-F22) and `.dev/egm/goldfish_findings_r2.md` (round 2, G1-G27). All round 2 recommendations were accepted by the owner. No design review has run yet.
