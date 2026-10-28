## ADDED Requirements

### Requirement: Check a CLI's command names
When asked to check a named CLI, the skill SHALL write that CLI's command tree to `docs/cli-tree.json` in the CLI's repository, run the bundled check against the bundled naming standard, and reply with the number of violations and advisories and each finding. A violation with a safe rename SHALL carry the proposed name; a confirm-only synonym, or a rename that would collide, SHALL be reported with no proposed name.

#### Scenario: Violations and advisories
- **WHEN** the user asks to check a toolkit whose CLI commands include `label ls`, `issue ls`, `issue all`, `report frobnicate` and `config set`, and whose catalog names a tool `list_notes`
- **THEN** the reply lists `label ls` as a violation with the proposed name `label list`, `list_notes` as verb-first with the proposed name `note_list`, a collision on `issue list` with no proposed name for `issue ls` or `issue all`, `report frobnicate` as an advisory with no proposed name, and `config set` as an advisory that needs the owner's decision, with no proposed name, and `docs/cli-tree.json` exists in the CLI's repository and the reply's findings come from running the bundled check on it
- **EVAL** evals/agent-interface/reports-violations-and-advisories

#### Scenario: One-noun CLI in flat form
- **WHEN** the CLI has one noun and its commands are `list`, `get` and `create` with no noun level
- **THEN** the reply has no violation for the missing noun level, and `docs/cli-tree.json` exists in the CLI's repository and the reply's findings come from running the bundled check on it
- **EVAL** evals/agent-interface/accepts-flat-one-noun-cli

#### Scenario: Incomplete command tree
- **WHEN** the skill could read only part of the CLI's commands
- **THEN** the reply says the tree is incomplete and names the sources that were read, and `docs/cli-tree.json` exists in the CLI's repository and the reply's findings come from running the bundled check on it
- **EVAL** evals/agent-interface/reports-incomplete-tree

#### Scenario: Existing rename stub
- **WHEN** the CLI has a hidden command `issue ls` that only prints `renamed to: tool issue list` and exits 2
- **THEN** the reply does not flag `issue ls`, and `docs/cli-tree.json` exists in the CLI's repository and the reply's findings come from running the bundled check on it
- **EVAL** evals/agent-interface/skips-stub

### Requirement: Plan renames with their callers
When asked to fix a CLI's names, the skill SHALL write `docs/cli-renames.json` in the CLI's repository listing each proposed rename with every caller found in the search roots (the folders the user names, or the default roots) as a `file:line` relative to the home folder or the search root, without the matched text, the search command it ran, and the standard version, and SHALL NOT edit the CLI's code or its callers.

#### Scenario: Rename plan with a caller
- **WHEN** the user asks to fix a CLI with `issue ls`, names the workspace as the search root, and a script in the workspace runs `tool issue ls`
- **THEN** `docs/cli-renames.json` maps `issue ls` to `issue list` and lists that script's `file:line`, and the CLI and the script are unchanged
- **EVAL** evals/agent-interface/writes-rename-map-with-callers

### Requirement: Design a new CLI's commands
When asked to design the commands for a new CLI, the skill SHALL write a noun-verb command tree that uses only approved verbs or local verbs the user names to `docs/cli-tree.json`, run the check on it, and reply with the tree path and the check result.

#### Scenario: New CLI from a description
- **WHEN** the user describes a CLI that manages issues and labels, listing what each should do
- **THEN** `docs/cli-tree.json` exists with paths such as `issue list` and `label create`, and the reply says the check found no violations
- **EVAL** evals/agent-interface/designs-noun-verb-tree

### Requirement: Ask for a missing target
The skill SHALL ask which CLI to check, fix or design when the request names none, and SHALL write nothing until it has one.

#### Scenario: No CLI named
- **WHEN** the user asks to check their CLI's command names without saying which CLI
- **THEN** the agent asks which CLI and writes no files
- **EVAL** evals/agent-interface/asks-for-cli-when-missing

## MODIFIED Requirements

### Requirement: Stay out of unrelated requests
The skill SHALL NOT run for requests that do not ask to design, check or rename a CLI's commands or MCP tool names, including ordinary use of a CLI.

#### Scenario: Arithmetic question
- **WHEN** the user asks an unrelated question
- **THEN** the agent answers directly and writes no files
- **EVAL** evals/agent-interface/ignores-unrelated-request

#### Scenario: Ordinary CLI use
- **WHEN** the user asks the agent to list the files in the current directory
- **THEN** the agent runs the command without the skill and writes no files
- **EVAL** evals/agent-interface/ignores-ordinary-cli-use

## REMOVED Requirements

### Requirement: Review a named file
**Reason**: The scaffold's generic file review is replaced by checking CLI command names against the naming standard.
**Migration**: None; nothing depends on the file review. Its eval case is deleted after this change is archived.
