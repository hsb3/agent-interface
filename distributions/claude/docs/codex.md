# Codex notes

Invoke skills by picking them from the skill list or typing
`$agent-interface:<skill>`. From `<plugin>/skills/<skill>/SKILL.md`, the plugin
root is three directories up. Resolve bundled `docs/` against it and a skill's
`references/` and `scripts/` against the skill folder. Shared `resources/` ship
at the plugin root and are reached by links relative to the skill
(`../../resources/...`). Never substitute
similarly named files from the user's project.

Ask one plain-text question when no structured question tool is available.
Link generated files with absolute-path Markdown links, not `file://` links.
