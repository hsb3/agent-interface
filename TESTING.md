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
- Grade statically whenever the check allows it: a `regex` on the file the skill writes, on the script's output in `trace`, or on a phrase the skill prescribes; a `not_contains` regex for "must not say X". Use `llm` only for a positive judgment over free text. The judge answers one word, and it fails correct long replies against "Fail if" rubrics. Case-insensitive patterns use `flags: i`; JavaScript has no leading `(?i)`.
- A grader that checks a result also checks that the result came from the bundled script (the file it read and the command it ran), so a run that answers from reasoning alone fails.
- Before merging new cases, an independent reviewer that sees only the spec and the case files confirms each case fails a skill that breaks its scenario.
- Agent sandboxes in Claude Code refuse commands containing the word "eval", so the behavior tier runs from the main session, not from a subagent.

## Host record

| Host | Version | Date | Commit | Install | Behavior | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Code | 2.1.312 | 2026-10-27 | 5e23e37 | not run | fail: 3 of 10 cases pass, mean Δ +0.17, $2.82 | Graders that check the workspace or transcript use `llm` with the default `focus: last_message`, so they cannot pass; `reviews-named-file` is the retired reviewer case kept until archive. |
| Codex | codex-cli 0.163.0 | 2026-10-27 | 5e23e37 | pass | pass: live `codex exec` turn discovered and read the skill | `PLUGIN_LIVE=1 bin/gate tests/integration`: 6 passed. |
| Claude Code | 2.1.312 | 2026-10-28 | d82ed2d | not run | pass: 9 of 10 cases, mean Δ +0.52, $2.76; `reports-incomplete-tree` then 3 of 3 after its rubric was reworded | `reviews-named-file` fails as expected: the retired reviewer case, deleted at archive (task 4.3). Trace shows `${CLAUDE_PLUGIN_ROOT}` substituted in the skill body. |
| Claude Code | 2.1.312 | 2026-10-29 | c04f6f8, graders 17e14fd | not run | pass: 30 of 33 cases, mean Δ +0.56, $14.07; all 10 `menu-design` and 14 `cli-behavior` cases pass once the three misfiring graders were fixed, re-scored against the kept workspaces and traces (139 of 139 static graders) | The three failures were grader patterns, not skill behavior: a plan that ends with the generic-request line, a reply saying "didn't check", and a `grep -v "^./tool.py"` read as running the CLI. An earlier run that day with `llm` graders on negative rubrics scored 28 of 33 ($14.20); the judge failed correct replies, so those graders became static checks. The 9 `agent-interface` cases are the pre-rename copies, deleted at archive. |
| Codex | codex-cli 0.163.0 | 2026-10-29 | 5906620 | pass | pass: live `codex exec` turn discovered the installed `cli-behavior` skill and read its bundled reference | `PLUGIN_LIVE=1 bin/gate tests/integration`: 6 passed. |
