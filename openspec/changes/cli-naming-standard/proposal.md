# Proposal

## Frame

The owner, a solo developer, uses this plugin in Claude Code and Codex whenever they design a new CLI or fix the command names of one they already built. It checks a CLI's commands and MCP tool names against one noun-verb naming standard (13 approved verbs, noun rules, root-command exemptions) and writes a rename plan with every caller it found. It works when the check flags the drift the owner sees today (`ls`/`list`/`show`, verb-first MCP names) with no false renames, and when a CLI fixed from its plan passes the check.

## What Changes

- The skill no longer reviews an arbitrary file against a checklist; it designs and checks CLI command names.
- Asked to check a CLI, the skill writes the CLI's command tree to a file in that CLI's repo, runs the bundled check, and replies with the counts of violations and advisories and each finding.
- The check flags synonym verbs (`issue ls` → `issue list`), verb-first MCP names (`list_notes` → `note_list`), nouns that are also verbs, and mixed flat and noun-verb commands, and proposes the rename for each.
- Synonyms that can change meaning (`set`, `show`, `push`, `pull`, ...) and renames that would make two commands collide are reported without a proposed rename.
- Root commands (`help`, `version`, `completion`, `serve`, `setup`, `init`) and existing rename stubs are never flagged.
- Asked to fix a CLI, the skill writes a rename plan into the CLI's repo listing each old name, the new name, and the location of every caller found in the folders the owner names. It does not edit the CLI.
- Asked to design a new CLI, the skill writes a noun-verb command tree using the approved verbs and checks it before replying.
- The skill never runs the CLI it checks; it reads the CLI's catalog and source.
- The plugin no longer ships the fresh-context reviewer agent.

## Non-goals

- The grammar trial that compares noun-verb with other structures for CLIs over 50 commands. Deferred to a later change.
- Applying renames inside a target CLI; the owner does that from the plan.
- Naming rules for skills, and output, error or pagination rules for CLIs.
- Reading from or writing to the owner's dev knowledge base.
- Hooks, MCP servers or apps.

## Capabilities

### Modified Capabilities

- `agent-interface`: replaces "review a named file" with designing, checking and planning renames for CLI command names; "stay out of unrelated requests" is reworded for the new task.
