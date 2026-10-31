# Agent guidelines

- `plugin.json` is canonical for name, version, description, license and publisher.
  Change it first, then mirror the value into `.claude-plugin/plugin.json` and
  `.codex-plugin/plugin.json`; `bin/gate` rejects drift.
- Never edit `distributions/` by hand. After any change to shipped files run
  `python3 scripts/pack_plugin.py --sync`; marketplaces install those folders.
- A new feature or behavior change is an OpenSpec change on the `plugin-change`
  schema (`openspec new change <name>`). Code changes wait until its `design.md`
  says `Status: Approved`. Bug fixes need no change. The full workflow, lineage
  and brand-kit notes are in [docs/development.md](docs/development.md).
- Work queues are GitHub issues: `bug` is the rework queue, fixed directly;
  `enhancement` is the feature queue, and each accepted request becomes an
  OpenSpec change before code.
- Every spec scenario ends with `- **EVAL** evals/<skill>/<case>`; every eval case
  is named by a scenario. `bin/gate` enforces both directions. Named cases must
  exist once the change's `design.md` is Approved; a draft may name cases not yet written.
- Skills: folder name equals frontmatter `name`; body under 24,000 bytes; each has
  `agents/openai.yaml` and `assets/icon.svg`.
- `resources/` is canonical: shared standards read at run time by more than one
  skill or reviewer. Link to a resource; never copy its rules into a skill.
- Personas in `agents/` stay host-neutral. Claude tool lists and `omitClaudeMd`
  belong only in the matching `.claude-plugin/agents/` adapter.
- `docs/*.md` is user-facing: it ships in every package and publishes to the
  optional site, except `docs/development.md` and `docs/testing.md`. Development
  files (`AGENTS.md`, those two, `openspec/`) never ship; shipped files link to
  them by absolute GitHub URL.
- Images come from the one-time brand kit: every SVG uses only colors listed in
  `assets/brand.json`, and every PNG has its SVG source beside it.
- Each skill keeps its deviation schema at `references/deviation.schema.json`
  and writes its register to `docs/<skill>-deviations.json` in the target repository.
- Runtime packages carry no hooks, MCP servers or apps unless a change's design
  adds them and the packer and tests change with it.
- Done means `bin/gate` passes and `docs/testing.md` records any host run claimed.
- EGM artifact directory: .dev/egm
