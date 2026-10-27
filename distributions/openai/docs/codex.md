# Codex notes

Invoke skills by picking them from the skill list or typing
`$agent-interface:<skill>`. From `<plugin>/skills/<skill>/SKILL.md`, the plugin
root is three directories up. Resolve bundled `agents/` and `docs/` against it
and `references/` against the skill folder. Never substitute similarly named
files from the user's project.

Codex has no named plugin agents. To run a reviewer, spawn a general-purpose
subagent with a fresh context: set `fork_context: false`, or `fork_turns: "none"`
when the schema offers that instead. Tell it to read `agents/<persona>.md` first
and pass absolute paths only. If no fresh-context subagent tool is available,
stop and say so; a review in the same context is not independent.

Ask one plain-text question when no structured question tool is available.
Link generated files with absolute-path Markdown links, not `file://` links.
