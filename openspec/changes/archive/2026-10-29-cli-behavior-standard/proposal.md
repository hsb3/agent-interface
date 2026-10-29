# Proposal

## Frame

The owner, a solo developer, uses this plugin in Claude Code and Codex whenever they design a new CLI or check one they already built, so that agents can drive it without a person at the terminal. A new skill checks a CLI against a behavior standard for agent use (machine-readable output, data on stdout and diagnostics on stderr, structured errors that say whether a retry is safe, no prompts with stdin closed, bounded output with explicit continuation, mutations that are safe to retry) and reports ranked findings, each with its evidence, the agent task it breaks, a fix, and a test that would prove the fix, then plans the CLI to full compliance with any deviation offered only as an option; the existing naming skill is renamed so each skill keeps one job. It works when two design runs for unrelated CLIs give the same contract, when the check on a CLI the owner already has reports where it differs from the standard with a source line for each finding and marks what source cannot prove as unknown instead of passing it, and when a CLI fixed from its findings no longer gets them.

## What Changes

- The existing skill is renamed **menu-design** (`/agent-interface:menu-design` in Claude Code). It still designs and checks CLI command names and MCP tool names, and writes rename plans, exactly as before. `/agent-interface:agent-interface` no longer exists.
- A new skill, **cli-behavior**, takes requests to check or design how a CLI behaves for agents. Requests about command or tool names still go to menu-design.
- Asked to check a CLI, cli-behavior replies with findings, each naming its rule, the source lines it rests on, the agent task it breaks, the fix, and a test that would show the fix works.
- A request to check a CLI means correcting it is already decided. cli-behavior writes a plan that brings the CLI fully to the standard. Deviations appear only as optional changes to that plan, each with the task the standard form makes worse and the work involved; the person who asked for the check chooses. Accepted deviations are recorded with their reasons in the CLI's own register, and later checks report them as deviations, not failures.
- Findings come worst first: what can lose or duplicate data, or hang an agent, before what only costs effort.
- What source cannot prove (a real hang, pagination that loses rows, a retry that runs twice) is reported as unknown with the test that would settle it, never as a pass.
- A rule that does not apply to a command (retry safety for a read-only command, a dry run for a command that changes nothing) is recorded as not applicable with the reason, not flagged.
- Asked to design a new CLI's behavior, cli-behavior writes the contract: the output envelope, the error shape and codes, how output is bounded, and for each mutation how it is made safe to retry, plus one example success, one example failure and the tests that would fail on a broken CLI.
- Each skill carries its own deviation schema and register (`docs/<skill>-deviations.json`). The schema's required fields make the reasoning for a deviation explicit, and the skill's script rejects an entry that leaves one out. This change builds it for cli-behavior; menu-design keeps `local_verbs` until its own later change.
- Files both skills read (the naming vocabulary and the command-tree format and building steps) move to `resources/`.
- A request to check a CLI that names neither names nor behavior goes to cli-behavior, which says names were not checked.
- The plugin's own `tree.py` is brought to the behavior standard: a completed check exits 0, and errors carry the standard error object.
- Neither skill runs the CLI; both read its catalog and source.

## Non-goals

- Running the target CLI, even read-only or against a fixture.
- Editing the CLI or applying fixes; the owner does that from the plan.
- Choosing among optional deviations, or ranking them by the work they take.
- Changing how menu-design replies or records kept words; its plan-first reply and its own deviation register are a later change.
- Running the deviation schemas through an eval harness as a goal of their own.
- Checking a hand-written declaration of what the CLI does in place of its source.
- Skills for Agent Skill design and for MCP tool behavior (descriptions, output shapes). Both are planned next, as `skill-design` and `mcp-behavior`; this change names its skills, standards, rules and files so those can sit beside them without renaming.
- Before/after measurement of agent success, retries and output size (waits on the eval work in issue #11).
- A reviewer agent, hooks, MCP servers or apps.

## Capabilities

### New Capabilities

- `menu-design`: everything `agent-interface` covers today, under the new skill name.
- `cli-behavior`: checking a CLI's behavior for agent use against the behavior standard, and designing the behavior contract of a new CLI.

### Modified Capabilities

- `agent-interface`: removed; its requirements move to `menu-design`, with the check scoped to command and tool names, one added scenario that leaves behavior requests to `cli-behavior`.
