# Claude Code notes

Invoke skills as `/agent-interface:<skill>`. Claude substitutes
`${CLAUDE_PLUGIN_ROOT}` in skill bodies; resolve bundled `docs/` against it and
a skill's `references/` and `scripts/` against the skill folder; shared
`resources/` are linked relative to the skill. Never guess a
cache path or read another installed copy.

The skills write only into the target CLI's repository. Menu Design writes `docs/cli-tree.json`, and `docs/cli-renames.json` when planning renames. CLI Behavior writes `docs/cli-tree.json` when none exists, `docs/cli-contract.md` when designing, and `docs/cli-behavior.json`, `docs/cli-behavior-plan.md` and `docs/cli-behavior-deviations.json` when checking. Resource
reads outside the project go through the normal permission prompts; this plugin
installs no hooks and no permission rules.

Local test without installing: `claude --plugin-dir distributions/claude`.
