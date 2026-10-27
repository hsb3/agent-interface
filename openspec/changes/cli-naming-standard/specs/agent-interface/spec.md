## ADDED Requirements

### Requirement: Check a CLI's command names
When asked to check a named CLI, the skill SHALL write that CLI's command tree to `docs/cli-tree.json` in the CLI's repository, run the bundled check against the bundled naming standard, write the findings to `cli-naming-report.md` in the working directory, and reply with the number of violations and advisories and the report path. A violation SHALL carry the proposed new name.

#### Scenario: Synonym verb
- **WHEN** the user asks to check a CLI whose commands include `issue ls`
- **THEN** the report lists `issue ls` as a violation with the proposed name `issue list`
- **EVAL** evals/agent-interface/flags-synonym-verb

#### Scenario: Verb-first MCP tool name
- **WHEN** the user asks to check a toolkit whose catalog names a tool `list_notes`
- **THEN** the report lists `list_notes` as verb-first with the proposed name `note_list`
- **EVAL** evals/agent-interface/flags-verb-first-mcp-name

#### Scenario: Unlisted verb
- **WHEN** the CLI has a command `report frobnicate` and `frobnicate` is not an approved verb
- **THEN** the report lists it as an advisory with no proposed name
- **EVAL** evals/agent-interface/keeps-unlisted-verb-advisory

#### Scenario: One-noun CLI in flat form
- **WHEN** the CLI has one noun and its commands are `list`, `get` and `create` with no noun level
- **THEN** the report has no violation for the missing noun level
- **EVAL** evals/agent-interface/accepts-flat-one-noun-cli

#### Scenario: Incomplete command tree
- **WHEN** the skill could read only part of the CLI's commands
- **THEN** the report says the tree is incomplete and names the sources that were read
- **EVAL** evals/agent-interface/reports-incomplete-tree

#### Scenario: Existing rename stub
- **WHEN** the CLI has a hidden command `issue ls` that only prints `renamed to: tool issue list` and exits 2
- **THEN** the report does not flag `issue ls`
- **EVAL** evals/agent-interface/skips-stub

### Requirement: Never propose a rename that can change meaning or collide
The skill SHALL report a command that uses a confirm-only synonym, or two commands that would be renamed to the same name, without proposing a rename for any of them.

#### Scenario: Confirm-only synonym
- **WHEN** the CLI has a command `config set`
- **THEN** the report lists `config set` as an advisory that needs the owner's decision, with no proposed name
- **EVAL** evals/agent-interface/confirm-synonym-not-auto-renamed

#### Scenario: Two commands would collide
- **WHEN** the CLI has both `issue ls` and `issue all`
- **THEN** the report lists a collision on `issue list` and proposes no rename for either command
- **EVAL** evals/agent-interface/reports-collision-not-rename

### Requirement: Plan renames with their callers
When asked to fix a CLI's names, the skill SHALL write `docs/cli-renames.json` in the CLI's repository listing each proposed rename with every caller found in the configured search roots as `file:line`, the search command it ran, and the standard version, and SHALL NOT edit the CLI's code or its callers.

#### Scenario: Rename plan with a caller
- **WHEN** the user asks to fix a CLI with `issue ls`, and a script in the workspace runs `tool issue ls`
- **THEN** `docs/cli-renames.json` maps `issue ls` to `issue list` and lists that script's `file:line`, and the CLI and the script are unchanged
- **EVAL** evals/agent-interface/writes-rename-map-with-callers

### Requirement: Design a new CLI's commands
When asked to design the commands for a new CLI, the skill SHALL write a noun-verb command tree that uses only approved verbs or declared local verbs to `docs/cli-tree.json`, run the check on it, and reply with the tree path and the check result.

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
- **THEN** the agent answers directly and writes no report
- **EVAL** evals/agent-interface/ignores-unrelated-request

#### Scenario: Ordinary CLI use
- **WHEN** the user asks the agent to list the files in the current directory
- **THEN** the agent runs the command without the skill and writes no report
- **EVAL** evals/agent-interface/ignores-ordinary-cli-use

## REMOVED Requirements

### Requirement: Review a named file
**Reason**: The scaffold's generic file review is replaced by checking CLI command names against the naming standard.
**Migration**: None; nothing depends on the file review. Its eval case is deleted after this change is archived.
