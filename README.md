<p align="center"><img src="assets/icon.svg" width="64" height="64" alt=""></p>

<h1 align="center">Agent Interface</h1>

<p align="center">Design and check CLI command and MCP tool names against a noun-verb standard, and plan renames that list affected callers.</p>

## Install

### Claude Code

```sh
claude plugin marketplace add hsb3/agent-interface
claude plugin install agent-interface@agent-interface
```

### Codex

```sh
codex plugin marketplace add hsb3/agent-interface
codex plugin add agent-interface@agent-interface
```

### Antigravity

```sh
agy plugin install https://github.com/hsb3/agent-interface
```

Start a new session after installing. Antigravity support is untested; see
[supported hosts](docs/harnesses.md).

## Try it

Ask your agent "check my CLI's command names" and name the CLI, for example
`mytool`. In Claude Code you can also run `/agent-interface:agent-interface`; in
Codex, pick the Agent Interface skill. The agent lists the CLI's commands, runs
the check, and replies with the number of violations and advisories and the
names to change.

## Skills

<table>
  <thead><tr><th align="left">Skill</th><th align="left">Use it to…</th></tr></thead>
  <tbody>
    <tr valign="top"><td width="200"><img src="skills/agent-interface/assets/icon.svg" width="20" height="20" alt="" align="top">&nbsp;<a href="https://github.com/hsb3/agent-interface/blob/main/skills/agent-interface/SKILL.md">Agent Interface</a></td><td>Design and check CLI command and MCP tool names against a noun-verb standard, and plan renames that list affected callers.</td></tr>
  </tbody>
</table>

## Learn more

- [Project site](https://hsb3.github.io/agent-interface/)
- [Supported hosts](docs/harnesses.md), [Claude Code notes](docs/claude.md), [Codex notes](docs/codex.md)
- [Privacy](docs/privacy.md) and [verifying releases](docs/releases.md)
- [Testing and host records](https://github.com/hsb3/agent-interface/blob/main/TESTING.md)
