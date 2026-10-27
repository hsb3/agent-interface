# Claude Code notes

Invoke skills as `/agent-interface:<skill>`. Claude substitutes
`${CLAUDE_PLUGIN_ROOT}` in skill bodies; resolve bundled `docs/` against it and
a skill's `references/` and `scripts/` against the skill folder. Never guess a
cache path or read another installed copy.

Write reports to the working directory, not the session scratchpad. Resource
reads outside the project go through the normal permission prompts; this plugin
installs no hooks and no permission rules.

Local test without installing: `claude --plugin-dir distributions/claude`.
