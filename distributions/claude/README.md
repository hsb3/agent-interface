<p align="center"><img src="assets/icon.svg" width="64" height="64" alt=""></p>

<h1 align="center">Agent Interface</h1>

<p align="center">Design and audit efficient, agent-friendly CLIs and skills with source-backed guidance and bounded offline checks.</p>

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

In Claude Code, run `/agent-interface:agent-interface notes.md`. In Codex, pick the
Agent Interface skill and name a file. The skill writes `agent-interface-report.md`
and replies with its path.

## Skills

<table>
  <thead><tr><th align="left">Skill</th><th align="left">Use it to…</th></tr></thead>
  <tbody>
    <tr valign="top"><td width="200"><img src="skills/agent-interface/assets/icon.svg" width="20" height="20" alt="" align="top">&nbsp;<a href="skills/agent-interface/SKILL.md">Agent Interface</a></td><td>Review one file against the bundled checklist.</td></tr>
  </tbody>
</table>

## Learn more

- [Supported hosts](docs/harnesses.md), [Claude Code notes](docs/claude.md), [Codex notes](docs/codex.md)
- [Privacy](docs/privacy.md) and [verifying releases](docs/releases.md)
- [Testing and host records](https://github.com/hsb3/agent-interface/blob/main/TESTING.md)
