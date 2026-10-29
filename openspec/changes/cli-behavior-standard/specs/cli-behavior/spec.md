# Spec Delta

## Purpose

Hold a behavior standard for CLIs that agents drive, check a CLI's source against it, plan the CLI to full compliance with any deviations offered as options, and design the behavior contract of a new CLI.

## ADDED Requirements

### Requirement: Stay out of unrelated requests
The skill SHALL NOT run for requests that do not ask to check or design how a CLI behaves for agents, including ordinary use of a CLI and requests about command or tool names. A request to check a CLI that names neither names nor behavior SHALL be taken by this skill, whose reply SHALL say that names were not checked.

#### Scenario: Ordinary CLI use
- **WHEN** the user asks the agent to show the git status of the current folder
- **THEN** the agent runs the command without the skill and writes no files
- **EVAL** evals/cli-behavior/ignores-ordinary-cli-use

#### Scenario: Naming request
- **WHEN** the user asks to check a named CLI's command names
- **THEN** the agent does not use this skill
- **EVAL** evals/cli-behavior/leaves-naming-to-menu-design

#### Scenario: Generic check request
- **WHEN** the user asks to check whether their `tool` CLI is ready for agents, without mentioning names or behavior
- **THEN** the agent checks its behavior, and the reply says the command names were not checked and gives the request that checks them
- **EVAL** evals/cli-behavior/takes-generic-check-request

### Requirement: Check a CLI's behavior
When asked to check how a named CLI behaves for agents, the skill SHALL read the CLI's catalog and source without running the CLI, write `docs/cli-behavior.json` in the CLI's repository with each rule's result for each command (pass, fail, unknown, not applicable or deviation), and reply with the counts and the failing findings, worst first. Each failing finding SHALL name its rule, the source `file:line`, the agent task it breaks, a fix, and a test that would show the fix works.

#### Scenario: CLI with behavior failures
- **WHEN** the user asks to check a CLI whose `item list` prints a table with progress lines on stdout and silently stops at 50 rows, whose errors are printed as plain text with exit 1, and whose `item delete` asks "Are you sure?" on stdin
- **THEN** the reply lists the prompt on `item delete` and the silent cut at 50 rows before the missing machine-readable output and the unstructured errors, each with its `file:line`, broken task, fix and test, `docs/cli-behavior.json` exists in the CLI's repository, and the CLI was never run
- **EVAL** evals/cli-behavior/reports-behavior-findings

#### Scenario: Behavior the source cannot prove
- **WHEN** the CLI's `item list --json --cursor` passes the cursor to a client library that is not in the repository
- **THEN** whether paging returns every row is reported as unknown, with a test such as reading 250 rows at page size 20, and is not counted as a pass
- **EVAL** evals/cli-behavior/marks-unproven-as-unknown

#### Scenario: Rule that does not apply
- **WHEN** every command of the CLI only reads data
- **THEN** retry safety and dry-run are recorded as not applicable with the reason, and neither is reported as a failing finding
- **EVAL** evals/cli-behavior/records-not-applicable

#### Scenario: Agent-ready CLI
- **WHEN** the CLI already has JSON output in a versioned envelope, diagnostics on stderr, structured errors with a retryable flag, no prompts, cursor paging and an idempotency key on its one mutation
- **THEN** the reply reports no failing findings
- **EVAL** evals/cli-behavior/passes-agent-ready-cli

### Requirement: Plan the CLI to full compliance
A request to check a CLI SHALL be treated as a decision to correct it: the skill SHALL NOT ask whether to fix it. After the check, the skill SHALL write `docs/cli-behavior-plan.md` in the CLI's repository, whose primary plan brings every failing result to the standard, lists each change that breaks a caller, and gives each unknown the test to run first.

#### Scenario: Plan with an optional deviation
- **WHEN** the check finds that `item list` prints a table, and a script in the CLI's repository parses that table
- **THEN** `docs/cli-behavior-plan.md` gives the standard JSON output as the plan, lists the script as a broken caller, and offers keeping the table as the default output as an optional change with its reason and its work, and the reply does not ask whether to fix the CLI
- **EVAL** evals/cli-behavior/plans-full-compliance

### Requirement: Offer deviations only as options
Deviations SHALL appear only as optional changes to the plan, each a `proposed` entry in `docs/cli-behavior-deviations.json` that fills every field of the skill's deviation schema. Work is stated, not used to choose. The skill SHALL NOT pick an option, and SHALL change an entry to accepted or declined only on explicit instruction from the person who asked for the check. A later check SHALL report an accepted deviation as a deviation with its reason, not as a failing finding.

#### Scenario: No deviation worth offering
- **WHEN** the check's only failure is that errors are printed as plain text, and nothing in the repository reads them
- **THEN** the plan offers no optional changes
- **EVAL** evals/cli-behavior/offers-no-padding-deviations

#### Scenario: Accepted deviation
- **WHEN** `docs/cli-behavior-deviations.json` records that the user accepted `item tail` streaming lines instead of returning one JSON document, with its reason
- **THEN** that result is reported as a deviation with the reason, not as a failing finding, and the plan does not change it
- **EVAL** evals/cli-behavior/honors-accepted-deviation

#### Scenario: Accepting an option on instruction
- **WHEN** the plan offers keeping the table as the default output of `item list`, and the user says to accept it
- **THEN** that entry in `docs/cli-behavior-deviations.json` is `accepted` with the date and who decided, and every other entry keeps its status
- **EVAL** evals/cli-behavior/accepts-deviation-on-instruction

### Requirement: Design a new CLI's behavior contract
When asked to design how a new CLI should behave for agents, the skill SHALL write `docs/cli-contract.md` with the output envelope, the error shape and codes, how output is bounded, and for each mutation how a retry is made safe, plus one example success, one example failure, and the tests that would fail on a CLI that breaks the contract, and reply with the file path. When `docs/cli-tree.json` exists, the contract SHALL cover each command in it.

#### Scenario: New CLI from a description
- **WHEN** the user describes a CLI that lists, creates and deletes issues
- **THEN** `docs/cli-contract.md` exists with the envelope, the error codes with whether each is retryable, paging for the list, how a repeated create or delete is made safe, one example success, one example failure, and tests including a run with stdin closed and a read of more rows than one page holds
- **EVAL** evals/cli-behavior/designs-behavior-contract

#### Scenario: Contract for an existing command tree
- **WHEN** `docs/cli-tree.json` lists `issue list`, `issue create` and `label delete`
- **THEN** `docs/cli-contract.md` covers each of the three commands
- **EVAL** evals/cli-behavior/designs-contract-from-tree

### Requirement: Ask for a missing target
The skill SHALL ask which CLI to check or design when the request names none, and SHALL write nothing until it has one.

#### Scenario: No CLI named
- **WHEN** the user asks to check whether their CLI is safe for agents to drive without saying which CLI
- **THEN** the agent asks which CLI and writes no files
- **EVAL** evals/cli-behavior/asks-for-cli-when-missing
