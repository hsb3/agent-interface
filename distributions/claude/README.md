<p align="center"><img src="assets/icon.svg" width="64" height="64" alt=""></p>

<h1 align="center">Agent Interface</h1>

<p align="center">Design and check CLI command and MCP tool names against a noun-verb standard, and how a CLI behaves for agents: output, errors, paging, prompts and safe retries.</p>

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

- **Names.** Ask your agent "check my CLI's command names" and name the CLI,
  for example `mytool`. In Claude Code you can also run
  `/agent-interface:menu-design`; in Codex, pick the Menu Design skill. The agent
  lists the CLI's commands, runs the check, and replies with the number of
  violations and advisories and the names to change.
- **Behavior.** Ask "check how `mytool` behaves for agents". In Claude Code you
  can also run `/agent-interface:cli-behavior`; in Codex, pick the CLI Behavior
  skill. The agent reads the CLI's source, records a result for each rule and
  command, and writes a plan that brings the CLI to the standard, with any
  optional deviations for you to accept or decline.

## Skills

<table>
  <thead><tr><th align="left">Skill</th><th align="left">Use it to…</th></tr></thead>
  <tbody>
    <tr valign="top"><td width="200"><img src="skills/menu-design/assets/icon.svg" width="20" height="20" alt="" align="top">&nbsp;<a href="https://github.com/hsb3/agent-interface/blob/main/skills/menu-design/SKILL.md">Menu Design</a></td><td>Design and check CLI command and MCP tool names against a noun-verb standard, and plan renames that list affected callers.</td></tr>
    <tr valign="top"><td width="200"><img src="skills/cli-behavior/assets/icon.svg" width="20" height="20" alt="" align="top">&nbsp;<a href="https://github.com/hsb3/agent-interface/blob/main/skills/cli-behavior/SKILL.md">CLI Behavior</a></td><td>Check and design how a CLI behaves for agents: machine output, errors, paging, prompts and safe retries, with a plan to full compliance.</td></tr>
  </tbody>
</table>

## Learn more

- [Project site](https://hsb3.github.io/agent-interface/)
- [Supported hosts](docs/harnesses.md), [Claude Code notes](docs/claude.md), [Codex notes](docs/codex.md)
- [Privacy](docs/privacy.md) and [verifying releases](docs/releases.md)
- [Testing and host records](https://github.com/hsb3/agent-interface/blob/main/TESTING.md)
