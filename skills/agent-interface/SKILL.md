---
name: agent-interface
description: >-
  Design and check CLI command names and MCP tool names against a noun-verb
  naming standard, and plan renames that list every caller. Use when the user
  asks to check a CLI's command names, asks whether a CLI is noun-verb, asks to
  design the commands for a new CLI, asks to plan renames for or fix the verbs
  in a CLI, or asks to name or check MCP tools. Do not use for ordinary CLI use
  such as listing files or running a command, for building an MCP server or a
  multi-entry-point service (the agent-toolkits plugin's job), for writing
  skills, or for unrelated questions.
---

# Agent Interface

Check a CLI's command and MCP tool names against one noun-verb standard, plan
renames with their callers, or design a new CLI's commands. The rules are in
[cli-naming.md](references/cli-naming.md), the word lists in
[cli-naming.json](references/cli-naming.json), the tree file's fields in
[tree-format.md](references/tree-format.md), and the procedures in
[remediation.md](references/remediation.md).

Hard limits, every run:

- Never run the target CLI, not even `--help`, and never import it. Read its
  catalog and source files only.
- Never edit the CLI or its callers, and never add a stub. The owner applies
  renames.
- Write only two files, both in the CLI's repo: the tree, at
  `<repo>/docs/cli-tree.json`, and on a fix run the plan, at
  `<repo>/docs/cli-renames.json`. Write no report file; the reply carries the
  findings. The repo is the git repository that holds the CLI's source, else
  the working directory.
- If the host refuses a write in the CLI's repo, for example because of Codex's
  workspace sandbox, stop and ask the owner to run the request from that repo.
  Do not write the file anywhere else.

## 1. No CLI named

If the request names no CLI (no file, folder, repo or CLI name) and describes
no new one, ask which CLI to check, fix or design, and stop. Write nothing and
do not search the working directory for a candidate.

## 2. Build the tree

Follow "Building the tree" in `references/remediation.md`: merge the CLI's MCP
catalog (`toolkit.json`), when it has one, with the command definitions in its
source. List every source you read; set `complete` to `false` when a source
could not be read. On a rebuild, keep the existing tree's `local_verbs`. Write
the tree to `<repo>/docs/cli-tree.json`.

## 3. Check

From the repo root, run the bundled script on the tree:

- Claude Code: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/agent-interface/scripts/tree.py check docs/cli-tree.json`
- Codex: `python3 <skill folder>/scripts/tree.py check docs/cli-tree.json`,
  where the skill folder is the one that holds this file.

Trust exit 0 or 1 only when stdout parses as the envelope
`{schema_version, ok, standard_version, data}`. Exit 2 writes
`{ok: false, error: {code, message}}` to stderr and nothing to stdout: for
`invalid-tree`, fix the tree and run the check again; for anything else, report
the error and stop. Never work out findings by hand.

## 4. Reply

Report from the envelope only:

- The number of violations and the number of advisories, then each finding:
  its `path`, `severity`, `code` and `message`, and its proposed name.
- The proposed name is the finding's `suggest`, exactly. When `suggest` is
  `null`, say "no proposed name" and offer none of your own: no replacement
  verb, no flag, no other name.
- A `collision` finding: name the commands that would have been renamed to its
  `path`, and say that none of them gets a proposed name.
- A `confirm-synonym` advisory: ask the owner whether to keep the word. A
  "keep" is recorded by adding the word to the tree's `local_verbs`, then
  rerunning the check. Add a local verb only on the owner's answer, never to
  silence a finding.
- An `incomplete-tree` finding: say the tree is incomplete, so the result
  covers only part of the CLI; name the sources that were read and what could
  not be read.
- A dispatcher CLI (tools run as `call <name>`): say its names were checked as
  MCP names only.
- With no violations, say the check found no violations.
- The `rule` of each finding names its heading in
  `references/cli-naming.md`; use it for the reason.

## 5. Fix

When asked to fix or plan renames: do steps 2-4, then follow "Caller search"
in `references/remediation.md`. The roots are the folders the owner names,
and only those; with none named, use the default roots listed there. Write the
plan, at `<repo>/docs/cli-renames.json`, in the format remediation.md gives,
from the violations whose `suggest` is not `null`. Reply with the plan's path,
each rename and its callers, and the search command. Leave the CLI and every
caller unchanged.

## 6. Design

When asked to design a new CLI's commands: write a tree from the owner's
description using `noun verb` paths (or flat paths for a CLI with one noun),
singular nouns, MCP tool names as `noun_verb`, and only the verbs in
`references/cli-naming.json` plus local verbs the owner names. Pick the approved verb that fits each action: "see all"
is `list`, "look up one" is `get`, "change" or "rename" is `update`. A new CLI
has no source yet: list one source, `{"kind": "source", "ref":
"docs/cli-tree.json"}`, give every command that `source`, and set `complete`
to `true`. A new CLI with no repo uses the working directory as its repo root.
Then do steps 3-4, and reply with the tree's path and the check result.
