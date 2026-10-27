# Supported hosts

One set of skills and personas serves every host. No host gets a fork of the
skill text.

| Host | Manifest | Install source | Status |
| --- | --- | --- | --- |
| Claude Code | `.claude-plugin/plugin.json` | `distributions/claude` via `.claude-plugin/marketplace.json` | See the host record |
| Codex | `.codex-plugin/plugin.json` | `distributions/openai` via `.agents/plugins/marketplace.json` | See the host record |
| Antigravity | `plugin.json` | Repository root | Untested |

`plugin.json` is canonical for name, version, description and publisher. Host
manifests repeat those values; the unit tests reject drift.

Personas in `agents/` are host-neutral. Claude Code gets thin adapters in
`.claude-plugin/agents/` that add its tool list and context isolation. Codex has
no named plugin agents: the skill spawns a general-purpose subagent and tells it
to read the persona file first.

Install the whole plugin. Copying `skills/` alone breaks skills that read
`agents/` or `docs/` at run time.

Tested versions and dates live in the
[host record](https://github.com/hsb3/agent-interface/blob/main/TESTING.md#host-record).
