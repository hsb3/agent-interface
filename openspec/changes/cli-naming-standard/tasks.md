# Tasks

No task starts before design.md says `Status: Approved`.

## 1. Evals

- [x] 1.1 evals/agent-interface/reports-violations-and-advisories for "Violations and advisories"
- [x] 1.2 evals/agent-interface/accepts-flat-one-noun-cli for "One-noun CLI in flat form"
- [x] 1.3 evals/agent-interface/reports-incomplete-tree for "Incomplete command tree"
- [x] 1.4 evals/agent-interface/skips-stub for "Existing rename stub"
- [x] 1.5 evals/agent-interface/writes-rename-map-with-callers for "Rename plan with a caller" (names the workspace as the search root)
- [x] 1.6 evals/agent-interface/designs-noun-verb-tree for "New CLI from a description"
- [x] 1.7 evals/agent-interface/asks-for-cli-when-missing for "No CLI named"
- [x] 1.8 evals/agent-interface/ignores-ordinary-cli-use for "Ordinary CLI use" (allows `Bash`)
- [x] 1.9 evals/agent-interface/ignores-unrelated-request: update its prompt if needed for "Arithmetic question"

## 2. Build

- [x] 2.1 `skills/agent-interface/references/cli-naming.json` from `vocabulary.md`, and the vocabulary consistency test in `tests/unit/test_cli_naming.py` (fails first against an empty list)
- [x] 2.2 `skills/agent-interface/references/cli-naming.md` from `vocabulary.md`, one reason per rule; delete `resources/review-checklist.md` and its row in `resources/README.md`
- [x] 2.3 `skills/agent-interface/references/tree-format.md`
- [x] 2.4 `skills/agent-interface/scripts/tree.py check`, with the MCP-name classification table and the tree-in, findings-and-exit-code-out table in `tests/unit/test_cli_naming.py` (watch both fail first)
- [x] 2.5 `skills/agent-interface/references/remediation.md`
- [x] 2.6 `skills/agent-interface/SKILL.md` description and routing body; `skills/agent-interface/agents/openai.yaml`
- [x] 2.7 Delete `agents/agent-interface-reviewer.md`, `.claude-plugin/agents/agent-interface-reviewer.md` and the `agents` entry in `.claude-plugin/plugin.json`; update `docs/claude.md`, `docs/codex.md` and `docs/harnesses.md`
- [x] 2.8 `plugin.json` description, `longDescription`, `shortDescription` and `capabilities`, then copy into `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`; `README.md` tagline, "Try it" and skills table; `docs/privacy.md`
- [x] 2.9 `TESTING.md` behavior tier adds `Bash` to `--allow-tools`

## 3. Verify

- [x] 3.1 `python3 scripts/pack_plugin.py --sync` and `bin/gate`
- [x] 3.2 Verify tier from TESTING.md; one host record row per host
- [x] 3.3 Run the check and fix on the notes toolkit (`/Users/henry/Developer/agent-toolkits/toolkits/notes`) as the first real remediation, and keep its plan as evidence. Applying the plan is agent-toolkits' work, done when it adopts this standard (hsb3/agent-toolkits#97). Evidence: `~/.local/share/agent-artifacts/agent-interface/2026-10-27-notes-remediation/`; the gap it found is issue #6

## 4. Archive

- [ ] 4.1 Keep `evals/agent-interface/reviews-named-file` until archive
- [ ] 4.2 `openspec archive cli-naming-standard`
- [ ] 4.3 Delete `evals/agent-interface/reviews-named-file`; update the Purpose line in `openspec/specs/agent-interface/spec.md`
- [ ] 4.4 `bin/gate`
