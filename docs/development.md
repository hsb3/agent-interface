# Development

How this repo is run. The rules agents follow are in [AGENTS.md](../AGENTS.md); test
tiers and host records are in [testing.md](testing.md). This file does not ship.

## Work queues

GitHub issues are the only task tracker, with two queues:

- `bug`: the rework queue. A bug is fixed directly, with no OpenSpec change.
- `enhancement`: the product-enhancement queue. An accepted request becomes an
  OpenSpec change before any code.

A separate board such as Backlog.md is more than a repo this size needs.

## Design workflow: OpenSpec with the `plugin-change` schema

Every feature or behavior change is an OpenSpec change on the custom schema in
[openspec/schemas/plugin-change/](../openspec/schemas/plugin-change/schema.yaml):

1. `openspec new change <name>` starts it.
2. **Proposal:** who it is for, the task, and how success is known.
3. **Specs:** each scenario names the eval case that proves it, and `bin/gate`
   checks both directions.
4. **Design:** drafted with `/egm:egm-draft`, reviewed in fresh context with
   `/egm:egm-review`, findings settled with `/egm:egm-resolve`. Code waits until
   the design says `Status: Approved`. EGM reports stay in `.dev/egm/`
   (gitignored).
5. **Tasks:** built, verified, then `openspec archive <change>` moves the change
   to `openspec/changes/archive/` and updates `openspec/specs/`.

## Lineage

This repo was generated from the template in plugin-factory, an unpublished
generator for plugins that install in Claude Code and Codex from one source
tree. plugin-factory adapts its structure and release process from Google's
[Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model)
(Apache-2.0), and the EGM plugin supplies the design-review step above.

## Brand kit

`assets/` holds the one-time brand kit; every SVG may use only the colors in
`assets/brand.json`, and `bin/gate` enforces that. For further logo or icon work,
the [logo-design skill](https://github.com/kaankiziltug/logo-design-skill) is the
reference.
