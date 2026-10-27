# Claude Code notes

Invoke skills as `/agent-interface:<skill>`. Claude substitutes
`${CLAUDE_PLUGIN_ROOT}` in skill and agent bodies; resolve bundled `agents/` and
`docs/` against it and a skill's `references/` against the skill folder. Never
guess a cache path or read another installed copy.

Reviewer agents are registered from `.claude-plugin/agents/`. Each adapter reads
its shared persona from `agents/`, limits tools (read-only reviewers get `Read`,
`Grep`, `Glob`) and sets `omitClaudeMd: true` so the reviewer starts without
project or user instructions. Spawn a new agent per review; do not fork the
conversation. This is context isolation, not filesystem isolation.

`/plugin` > Errors reports that the default `agents/` folder is ignored because
the manifest lists agents. That is expected: loading `agents/` directly would
drop the adapters' tool limits.

Write reports to the working directory, not the session scratchpad. Resource
reads outside the project go through the normal permission prompts; this plugin
installs no hooks and no permission rules.

Local test without installing: `claude --plugin-dir distributions/claude`.
