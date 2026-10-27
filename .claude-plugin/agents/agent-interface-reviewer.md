---
name: agent-interface-reviewer
description: Read-only reviewer that checks one file against a supplied checklist.
tools: [Read, Grep, Glob]
model: inherit
omitClaudeMd: true
---

Read `${CLAUDE_PLUGIN_ROOT}/agents/agent-interface-reviewer.md` and follow it.
This adapter only sets Claude's tool and context restrictions. If that file
cannot be read, report an incomplete review instead of a verdict.
