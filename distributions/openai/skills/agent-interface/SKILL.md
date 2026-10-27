---
name: agent-interface
description: >-
  Review one file against the bundled checklist using a fresh-context reviewer.
  Replace this description with the task phrases that should route to the skill.
---

# Agent Interface

In Claude Code, read `${CLAUDE_PLUGIN_ROOT}/docs/claude.md` first. In Codex,
read [Codex integration](../../docs/codex.md) first.

Review the file the user names against the canonical checklist,
`resources/review-checklist.md` under the plugin root.

1. Confirm the target path exists. If none was given, ask for one and stop.
2. Spawn the `agent-interface-reviewer` subagent in a fresh context. Where the
   harness has no agent by that name, spawn a fresh-context general-purpose
   subagent told to read `agents/agent-interface-reviewer.md` first. Pass the
   absolute target path and the absolute checklist path, nothing else. If your
   harness cannot create a fresh-context subagent, say so and stop.
3. Write the reviewer's findings to `agent-interface-report.md` in the working
   directory. Do not paste the report into chat.
4. Reply with the report path and the number of findings.
