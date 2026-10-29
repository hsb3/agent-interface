# Tasks

Phase 0 (section 1) is written before the owner sets `Status: Approved`, because `test_specs.py` requires every eval case an approved change names. No task in sections 2-6 starts before design.md says `Status: Approved`. Each phase names the tests it must pass (design.md, "Order of work"); `test_no_orphan_eval_folders` fails from phase 0 until the archive.

## 1. Evals (phase 0)

- [x] 1.1 Copy the nine `evals/agent-interface/*` cases to `evals/menu-design/` (keep the originals until archive); in the copies of `ignores-ordinary-cli-use/graders/no-skill.md` and `ignores-unrelated-request/graders/no-skill.md`, match `menu-design` instead of `agent-interface`
- [x] 1.2 evals/menu-design/leaves-behavior-to-cli-behavior for "Behavior request"
- [x] 1.3 evals/cli-behavior/ignores-ordinary-cli-use for "Ordinary CLI use"
- [x] 1.4 evals/cli-behavior/leaves-naming-to-menu-design for "Naming request"
- [x] 1.5 evals/cli-behavior/takes-generic-check-request for "Generic check request"
- [x] 1.6 evals/cli-behavior/reports-behavior-findings for "CLI with behavior failures"
- [x] 1.7 evals/cli-behavior/marks-unproven-as-unknown for "Behavior the source cannot prove"
- [x] 1.8 evals/cli-behavior/records-not-applicable for "Rule that does not apply"
- [x] 1.9 evals/cli-behavior/passes-agent-ready-cli for "Agent-ready CLI"
- [x] 1.10 evals/cli-behavior/plans-full-compliance for "Plan with an optional deviation"
- [x] 1.11 evals/cli-behavior/offers-no-padding-deviations for "No deviation worth offering"
- [x] 1.12 evals/cli-behavior/honors-accepted-deviation for "Accepted deviation"
- [x] 1.13 evals/cli-behavior/accepts-deviation-on-instruction for "Accepting an option on instruction"
- [x] 1.14 evals/cli-behavior/designs-behavior-contract for "New CLI from a description"
- [x] 1.15 evals/cli-behavior/designs-contract-from-tree for "Contract for an existing command tree"
- [x] 1.16 evals/cli-behavior/asks-for-cli-when-missing for "No CLI named"
- [x] 1.17 Independent review: a reviewer that sees only the specs and the case files confirms each case fails a skill that breaks its scenario (TESTING.md, "Writing eval cases"). Done 2026-10-29: 10 of 15 cases fixed (5859265, a5a5888); review summary in the owner's local notes (.dev/eval-synopsis.md)
- [ ] 1.18 `bin/gate tests/unit/test_specs.py tests/unit/test_evals.py::test_each_skill_has_eval_cases`; then the owner sets `Status: Approved`

## 2. Shared resources, rename and `tree.py` (phase 1)

- [ ] 2.1 `git mv skills/agent-interface skills/menu-design`; frontmatter `name`, heading, description ("Not for how a CLI behaves for agents"), script path; `agents/openai.yaml` display name
- [ ] 2.2 `git mv` `references/cli-naming.json` to `resources/cli-naming.json`; `tree.py` reads it three folders above the script
- [ ] 2.3 `resources/command-tree.md` from `tree-format.md`, the repo-root paragraph and all six "Building the tree" subsections; delete `references/tree-format.md`; cut the moved text from `remediation.md` and link to the new file; `remediation.md` line 143 reads `data.standard_version`; `resources/README.md` lists both files
- [ ] 2.4 `cli-naming.md` and `SKILL.md` links become skill-relative (`../../resources/...`, `../../../resources/...` from `references/`)
- [ ] 2.5 `tree.py`: completed check exits 0 with `data: {standard_version, findings}`; failures are the envelope on stdout (`INVALID_ARGUMENT` exit 2, `INTERNAL` exit 1, `retryable`, `next_action`), including usage errors and uncaught exceptions. Change the tests named in design.md §2 first and watch them fail against the old script
- [ ] 2.6 `SKILL.md` steps 3 and 4 for the new envelope
- [ ] 2.7 `bin/gate tests/unit/test_cli_naming.py tests/unit/test_link_integrity.py`

## 3. Behavior standard and script (phase 2)

- [ ] 3.1 `tests/unit/test_cli_behavior.py` with every case in design.md §3; watch it fail with no standard or script
- [ ] 3.1a In `tests/unit/test_cli_behavior.py`, run `contract create` on the tree in evals/cli-behavior/designs-contract-from-tree and on a test tree for the `tracker` CLI described in designs-behavior-contract (that case has no fixture tree) and assert every content grader's pattern matches the output, so the graders track the real standard
- [ ] 3.2 `skills/cli-behavior/references/cli-behavior.json` (kinds, rules with `applies_to` and `tests`, idempotency verbs, error codes, severities, envelope fields, examples, paging defaults)
- [ ] 3.3 `skills/cli-behavior/references/deviation.schema.json`
- [ ] 3.4 `skills/cli-behavior/scripts/behavior.py`: `contract create` (with `--dry-run`) for "New CLI from a description" and "Contract for an existing command tree"; `result check` for "Check a CLI's behavior", "Behavior the source cannot prove", "Rule that does not apply", "Accepted deviation"
- [ ] 3.5 `tests/integration/test_install.py`: assert the Codex install contains `resources/cli-naming.json`
- [ ] 3.6 `bin/gate tests/unit/test_cli_behavior.py`

## 4. The `cli-behavior` skill (phase 3)

- [ ] 4.1 `skills/cli-behavior/references/cli-behavior.md` (one `## <rule-id>` per rule, bullet lines) and `references/output-files.md`
- [ ] 4.2 `skills/cli-behavior/SKILL.md`: description and routing for "Stay out of unrelated requests" and "Generic check request"; hard limits; design and check steps; "Plan the CLI to full compliance"; "Offer deviations only as options"; "Ask for a missing target"
- [ ] 4.3 `skills/cli-behavior/agents/openai.yaml` and `assets/icon.svg` (brand colors, `viewBox="0 0 24 24"`, `<title>`)
- [ ] 4.4 `bin/gate tests/unit/test_frontmatter.py tests/unit/test_skill_load_limits.py tests/unit/test_manifests.py tests/unit/test_images.py`

## 5. Metadata, docs and packages (phase 4)

- [ ] 5.1 `plugin.json` 0.2.0, description, `longDescription`, `shortDescription` "CLI names and agent behavior", `capabilities`; mirror into `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` (whole `interface` block) and both `.claude-plugin/marketplace.json` descriptions
- [ ] 5.2 `README.md` tagline, "Try it" (one example per skill) and the two-row Skills table
- [ ] 5.3 `docs/claude.md`, `docs/codex.md`, `docs/privacy.md`, `docs/harnesses.md` as in design.md §5
- [ ] 5.4 `AGENTS.md`: the deviation schema and register line
- [ ] 5.5 `python3 scripts/pack_plugin.py --sync` and `bin/gate` (all but `test_no_orphan_eval_folders`)

## 6. Verify (phase 5)

- [ ] 6.1 `bin/gate tests/integration`
- [ ] 6.2 Behavior tier from TESTING.md over both skills; the nine cases that passed on 2026-10-28 still pass under `menu-design` (Goal 7); one host record row
- [ ] 6.3 Live Codex: `PLUGIN_LIVE=1 bin/gate tests/integration`; one host record row
- [ ] 6.4 Live proof 1: the check on a scratch copy of `/Users/henry/Developer/agent-toolkits/toolkits/notes` (commit recorded); `result check` accepts the results; every cited line exists; record the share of unknowns; the owner applies one fix and a re-check passes it (CUJ 3); outputs kept in `~/.local/share/agent-artifacts/agent-interface/`
- [ ] 6.5 Live proof 2: the check on scratch copies of `tree.py` and `behavior.py` under `/private/tmp/agents/agent-interface/self-check/` reports no failing findings

## 7. Archive (phase 6)

- [ ] 7.1 `openspec archive cli-behavior-standard`
- [ ] 7.2 Delete `evals/agent-interface/`
- [ ] 7.3 `python3 scripts/pack_plugin.py --sync`, `bin/gate` and `bin/gate tests/integration`
- [ ] 7.4 Open the pull request (the ruleset requires one); after merge, tag and release 0.2.0
