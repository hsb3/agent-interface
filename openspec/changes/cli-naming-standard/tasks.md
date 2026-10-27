# Tasks

No task starts before design.md says `Status: Approved`.

## 1. Evals

- [ ] 1.1 evals/agent-interface/flags-synonym-verb for "Synonym verb"
- [ ] 1.2 evals/agent-interface/flags-verb-first-mcp-name for "Verb-first MCP tool name"
- [ ] 1.3 evals/agent-interface/keeps-unlisted-verb-advisory for "Unlisted verb"
- [ ] 1.4 evals/agent-interface/accepts-flat-one-noun-cli for "One-noun CLI in flat form"
- [ ] 1.5 evals/agent-interface/reports-incomplete-tree for "Incomplete command tree"
- [ ] 1.6 evals/agent-interface/skips-stub for "Existing rename stub"
- [ ] 1.7 evals/agent-interface/confirm-synonym-not-auto-renamed for "Confirm-only synonym"
- [ ] 1.8 evals/agent-interface/reports-collision-not-rename for "Two commands would collide"
- [ ] 1.9 evals/agent-interface/writes-rename-map-with-callers for "Rename plan with a caller"
- [ ] 1.10 evals/agent-interface/designs-noun-verb-tree for "New CLI from a description"
- [ ] 1.11 evals/agent-interface/asks-for-cli-when-missing for "No CLI named"
- [ ] 1.12 evals/agent-interface/ignores-ordinary-cli-use for "Ordinary CLI use"
- [ ] 1.13 evals/agent-interface/ignores-unrelated-request: update its prompt if needed for "Arithmetic question"

## 2. Build

- [ ] 2.1 `resources/cli-naming.json` from the approved starter vocabulary, and `tests/unit/test_cli_naming.py` vocabulary consistency test (fails first against an empty list)
- [ ] 2.2 `resources/cli-naming.md`, and `resources/README.md` rows; delete `resources/review-checklist.md` and its row
- [ ] 2.3 `skills/agent-interface/references/tree-format.md`
- [ ] 2.4 `skills/agent-interface/scripts/tree.py check`, with the name-classification table in `tests/unit/test_cli_naming.py` (watch it fail first)
- [ ] 2.5 `skills/agent-interface/references/remediation.md`
- [ ] 2.6 `skills/agent-interface/SKILL.md` description and routing body; `skills/agent-interface/agents/openai.yaml`
- [ ] 2.7 Delete `agents/agent-interface-reviewer.md`, `.claude-plugin/agents/agent-interface-reviewer.md` and the `agents` entry in `.claude-plugin/plugin.json`
- [ ] 2.8 `plugin.json` description, then mirror into `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`; README "Try it" and skills table
- [ ] 2.9 `TESTING.md` behavior tier adds `Bash` to `--allow-tools`

## 3. Verify

- [ ] 3.1 `python3 scripts/pack_plugin.py --sync` and `bin/gate`
- [ ] 3.2 Verify tier from TESTING.md; one host record row per host
- [ ] 3.3 Run the check on the notes toolkit (`/Users/henry/Developer/agent-toolkits/toolkits/notes`) as the first real remediation and keep its plan as evidence

## 4. Archive

- [ ] 4.1 Keep `evals/agent-interface/reviews-named-file` until archive
- [ ] 4.2 `openspec archive cli-naming-standard`
- [ ] 4.3 Delete `evals/agent-interface/reviews-named-file`; update the Purpose line in `openspec/specs/agent-interface/spec.md`
- [ ] 4.4 `bin/gate`
