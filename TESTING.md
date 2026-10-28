# Testing

| Tier | Command | Needs | Proves |
| --- | --- | --- | --- |
| Unit | `bin/gate` | uv | Manifests agree, links resolve, every spec scenario names an existing eval and every eval is traced, images stay on the brand palette, packages are lean and reproducible, distributions are current |
| Install | `bin/gate tests/integration` | `claude`, `codex`, `openspec` CLIs; no model use | Claude strict validation passes; Codex installs the plugin in a throwaway `CODEX_HOME`; OpenSpec schema and specs validate strictly |
| Behavior | `claude plugin eval . --runs 1 --no-publish --allow-tools Write Edit Bash` | Claude login; uses model quota | Skills route and produce their artifacts, with a no-plugin baseline |
| Live Codex | `PLUGIN_LIVE=1 bin/gate tests/integration` | Codex login; uses model quota | Installed skill is discovered and read in a real `codex exec` turn |

CI runs the unit tier only. Install, behavior and live tiers run locally before a
release; record each run below.

## Writing eval cases

- Every spec scenario names one case with `- **EVAL** evals/<skill>/<case>`; the gate requires the case to exist once the change's `design.md` says `Status: Approved`, and a draft may name cases not yet written.
- A case is `prompt.md` (frontmatter: integer `max_turns`, an `allowed_tools` list) plus at least one file in `graders/` (frontmatter `type`, that type's options and `weight`; an `llm` body states pass and fail conditions). Use the existing cases under `evals/` as the template.
- Fixtures: the prompt tells the agent to create each fixture file with exact content in the eval workspace before making the request. The `case.yaml` `context.scaffold_script` alternative needs `--scaffold`, which the behavior tier command does not pass.
- Fixtures never reference real home paths or other repos; a case that searches for callers names the eval workspace as the search root.
- A grader that says "writes no files" or "edits nothing" can only fail if the case grants `Write` or `Edit`; grant the tool so the negative check is real. The behavior tier's `--allow-tools` must include every gated tool any case lists.
- An `llm` grader sees only the final reply unless its `focus` is `trace` or `{ source: file, path: ... }`. Check a written file with `file_exists` or a file `focus`/`target`, and a command the agent ran with `tool_used` and `input_match`; never ask the reply-only judge about either.
- A grader that checks a result also checks that the result came from the bundled script (the file it read and the command it ran), so a run that answers from reasoning alone fails.
- Before merging new cases, an independent reviewer that sees only the spec and the case files confirms each case fails a skill that breaks its scenario.
- Agent sandboxes in Claude Code refuse commands containing the word "eval", so the behavior tier runs from the main session, not from a subagent.

## Host record

| Host | Version | Date | Commit | Install | Behavior | Notes |
| --- | --- | --- | --- | --- | --- | --- |
