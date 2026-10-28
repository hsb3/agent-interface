# Proposal

## Frame

The owner, a solo developer, uses this plugin in Claude Code and Codex whenever they design a new CLI or check one they already built, so that agents can drive it without a person at the terminal. A new skill checks a CLI against a behavior standard for agent use (machine-readable output, data on stdout and diagnostics on stderr, structured errors that say whether a retry is safe, no prompts with stdin closed, bounded output with explicit continuation, mutations that are safe to retry) and reports ranked findings, each with its evidence, the agent task it breaks, a fix, and a test that would prove the fix; the existing naming skill is renamed so each skill keeps one job. It works when, on CLIs the owner already has, the check reports the failures agents actually hit, marks what source cannot prove as unknown instead of passing it, and a CLI fixed from its findings no longer gets them.

## What Changes

- The existing skill is renamed **menu-design** (`/agent-interface:menu-design` in Claude Code). It still designs and checks CLI command names and MCP tool names, and writes rename plans, exactly as before. `/agent-interface:agent-interface` no longer exists.
- A new skill, **cli-behavior**, takes requests to check or design how a CLI behaves for agents. Requests about command or tool names still go to menu-design.
- Asked to check a CLI, cli-behavior replies with findings, each naming its rule, the source lines it rests on, the agent task it breaks, a small fix, and a test that would show the fix works.
- Findings come worst first: what can lose or duplicate data, or hang an agent, before what only costs effort.
- What source cannot prove (a real hang, pagination that loses rows, a retry that runs twice) is reported as unknown with the test that would settle it, never as a pass.
- A rule that does not apply to a command (retry safety for a read-only command, pagination for a naturally bounded result) is recorded as not applicable with the reason, not flagged.
- Asked to design a new CLI's behavior, cli-behavior writes the contract: the output envelope, the error shape and codes, how output is bounded, and for each mutation how it is made safe to retry, plus one example success, one example failure and the tests that would fail on a broken CLI.
- Neither skill runs the CLI; both read its catalog and source.

## Non-goals

- Running the target CLI, even read-only or against a fixture.
- Editing the CLI or applying fixes; the owner does that from the findings.
- Checking a hand-written declaration of what the CLI does in place of its source.
- Skills for Agent Skill design and for MCP tool behavior (descriptions, output shapes). Both are planned next, as `skill-design` and `mcp-behavior`; this change names its skills, standards, rules and files so those can sit beside them without renaming.
- Before/after measurement of agent success, retries and output size (waits on the eval work in issue #11).
- A reviewer agent, hooks, MCP servers or apps.

## Capabilities

### New Capabilities

- `menu-design`: everything `agent-interface` covers today, under the new skill name.
- `cli-behavior`: checking a CLI's behavior for agent use against the behavior standard, and designing the behavior contract of a new CLI.

### Modified Capabilities

- `agent-interface`: removed; its requirements move to `menu-design`, with the check scoped to command and tool names and one added scenario that leaves behavior requests to `cli-behavior`.
