---
name: cli-behavior
description: >-
  Check and design how a CLI behaves when an agent drives it: machine output
  (--json and one envelope), what goes to stdout and stderr, error shape and
  codes, exit status, paging, prompts and confirmation, dry run and safe
  retries. Use when the user asks to check how a CLI behaves for agents, asks
  whether a CLI is safe or ready for agents to drive, asks to check their CLI
  without saying names or behavior ("check my CLI", "is my CLI ready for
  agents"), asks to accept or decline an option from a behavior plan, or asks
  to design how a new CLI should behave for agents. Do not use for command or
  tool names (that is the menu-design skill), for ordinary CLI use such as
  running a command or showing git status, for building an MCP server, or for
  unrelated questions.
---

# CLI Behavior

Hold one behavior standard for CLIs that agents drive. Check a CLI's source
against it and plan the CLI to full compliance, or write a new CLI's behavior
contract. The rules, kinds, severities and error codes are in
[cli-behavior.md](references/cli-behavior.md), with
[cli-behavior.json](references/cli-behavior.json) as the source. The files
this skill writes are laid out in [output-files.md](references/output-files.md);
the deviation schema is [deviation.schema.json](references/deviation.schema.json).
The tree file's format and how to build it are in
[command-tree.md](../../resources/command-tree.md); the verbs are in
[cli-naming.json](../../resources/cli-naming.json).

Hard limits, every run:

- Never run the target CLI, not even `--help` or a read-only command, and
  never import it (`python tool.py`, `./tool`, `import tool`, `runpy` are all
  running it). Read its files only: the file-reading tool shows line numbers,
  and `grep -n` finds a line.
- Never edit the CLI or its callers. The owner applies the plan.
- Never quote a secret value (token, password, key) in any file you write or
  in the reply; cite its `file:line` only.
- Write only these files, all in `docs/` of the CLI's repository:
  `cli-tree.json` (only when none exists), `cli-contract.md`,
  `cli-behavior.json`, `cli-behavior-plan.md` and `cli-behavior-deviations.json`.
  In the register, write `proposed` entries only; change an entry to
  `accepted` or `declined` only on the explicit instruction of section 6.
  Write no report file; the reply carries the findings.
- A request to check a CLI is a decision to correct it. Never ask whether to
  fix the CLI, whether to apply the plan or whether to proceed, and never
  offer to make the changes.
- An option's `work` is stated so the owner can plan effort; it is never the
  reason to offer an option. Never pick, rank or recommend an option.
- If the host refuses a write in the CLI's repository, for example because of
  Codex's workspace sandbox, stop and ask the owner to run the request from
  that repository. Do not write the file anywhere else.

The bundled script, run from the repository root:

- Claude Code: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/cli-behavior/scripts/behavior.py <command>`
- Codex: `python3 <skill folder>/scripts/behavior.py <command>`, where the
  skill folder is the one that holds this file.

It prints one envelope on stdout. Use its result only when it exits 0 with
`{schema_version, ok: true, data}`. A failure is `{schema_version, ok: false,
error: {code, message, retryable, next_action}}`; `INVALID_ARGUMENT` (exit 2)
lists every problem in `message`, one per line.

## 1. Pick the job

- **No CLI named.** If the request names no CLI (no file, folder, repository or
  CLI name) and describes no new one, ask which CLI to check or design, and
  stop. Write nothing and do not search the working directory for a candidate.
- **Design** (section 3): the owner describes a new CLI, or asks how a CLI
  should behave, and wants its contract.
- **Check** (section 4): the owner asks how an existing CLI behaves for agents,
  whether it is safe or ready for agents, or to check it without saying names
  or behavior. A request that mentions neither command names nor behavior (or
  a behavior topic: output, errors, paging, prompts, retries) is a **generic
  request**: "check my CLI", "is my `tool` CLI ready for agents". Check its
  behavior only, and say in the reply and the plan that command names were not
  checked (section 4, steps 8 and 9). Never run `tree.py` or the menu-design
  skill for it.
- **Decision** (section 6): the person who asked for a check says to accept or
  decline one of its options.
- A request only about command or tool names is not this skill's job: say the
  menu-design skill handles it, and write nothing.

## 2. Repository root and tree

The repository root is defined in `../../resources/command-tree.md`; a new CLI
with no repository uses the working directory. Every file below goes in
`<repo>/docs/`, and every `path:line` is relative to the repository root.

If `<repo>/docs/cli-tree.json` exists, use it as it is. Otherwise write it:

- **Existing CLI:** follow "Building the tree" in
  `../../resources/command-tree.md`.
- **New CLI:** from the owner's description, `noun verb` paths (flat paths for
  a CLI with one noun), singular nouns, and verbs from the `verbs` in
  `../../resources/cli-naming.json` chosen by their `means`. List one source,
  `{"kind": "source", "ref": "docs/cli-tree.json"}`, give every command that
  `source` and `"mcp_name": null`, and set `complete` to `true`.

Do not judge the names; that is menu-design's job.

## 3. Design

1. Find or write the tree (section 2).
2. Run `behavior.py contract create docs/cli-tree.json`. It writes
   `<repo>/docs/cli-contract.md` beside the tree: every covered command with its
   kind, flags, rules and error codes, then the envelope, error object, code
   table, one example success, one example failure and the tests. On exit 2
   caused by the tree, fix the tree and run it again; on any other failure,
   report the error's `message` and stop.
3. Never write or edit the contract by hand; to change it, change the tree and
   run the script again.
4. Reply with the path `<repo>/docs/cli-contract.md`, the commands it covers with
   their kinds, and that a verb the standard does not list is designed as
   `write`, the strictest kind. A command that must stream until interrupted
   is outside the template (the known limit in `references/cli-behavior.md`):
   say so, and design it by hand from the standard.

## 4. Check

1. **Tree.** Find or build the tree (section 2). The covered commands, kinds
   and `applies_to` are defined in `references/cli-behavior.md`.
2. **Read.** For each covered command, read its handler and everything it runs
   through: the entry point, argument parsing, error handling, output helpers.
   Read `<repo>/docs/cli-behavior-deviations.json` if it exists.
3. **Record a result for every rule and every covered command**, in the
   format of `references/output-files.md`, judging each against the rule's
   form in `references/cli-behavior.md`:
   - Outside the rule's `applies_to`: `not_applicable`, with the reason
     ("rule applies to kind write only").
   - `pass`: the source shows every part of the form; cite the lines.
   - `fail`: the source breaks the form. Cite the line that does it (the
     `input(` call, the slice or loop that cuts a list, the `print` that puts
     text on stdout, the handler that prints a plain-text error), and give
     the agent `task` it breaks, the `fix` that brings it to the form, and a
     `test` from the rule's `tests` with `<command>` filled in.
   - `unknown`: whether the command meets the form depends on code or data the
     repository does not hold (a library not in the repository, a server,
     configuration). Give the `test` that would settle it, from the rule's
     `tests`. Unknown is never a pass: a flag that exists is not proof that
     the behavior behind it is right.
   - `deviation`: only when the register has an `accepted` entry for that
     command and rule and the source still does what its `proposed_form`
     says; cite the line. A `declined` entry changes nothing: judge the
     command against the standard.
   - One result covers several commands when they share a handler or the same
     finding. A verb the standard does not list takes its kind from its
     handler: set `command_kind` on its results and cite the handler line.
   Write the results to `<repo>/docs/cli-behavior.json`, replacing any earlier file.
4. **Caller search.** For each command with a failing result, search the
   repository, leaving out `.git` and `docs/`, for `<cli> <command words>`
   (`tool item list`) and for the command words alone, and keep the real
   callers: scripts, tests, CI files, code or docs that run the command or
   read its output. Note each caller's `file:line` and what it relies on.
5. **Options.** Decide this run's options by the rules of section 5, then
   update `<repo>/docs/cli-behavior-deviations.json` with your file-editing tool:
   remove every `proposed` entry, add this run's options as `proposed`
   entries, and leave every `accepted` and `declined` entry exactly as it is.
   If the file does not exist and this run has no options, do not create it.
6. **Validate.** Run `behavior.py result check docs/cli-behavior.json`. On exit
   2, fix every problem in `message` and run it again, at most three runs in
   all. If problems remain after the third, reply with them and stop. Take
   every count and finding from `data`; never work them out by hand.
7. **Plan.** Write `<repo>/docs/cli-behavior-plan.md` in the layout of
   `references/output-files.md`. Full compliance comes first and is the plan:
   every failing result's fix by command, worst first, each caller the change
   breaks from step 4, and for each unknown the test to run first. Then the
   accepted deviations, which the plan does not change. Then the optional
   deviations by command and rule, with task and work, or "None.".
8. **Generic request.** Also end the plan with: "Command names were not
   checked. To check them, ask: check the command names of the CLI in <path>."
9. **Reply**, in this order:
   - The counts from `data.counts`: pass, fail, unknown, not applicable,
     deviation.
   - Every failing finding from `data.findings`, in its order (worst first:
     `data`, then `hang`, then `misread`), each with its commands, rule,
     severity, `file:line`, the task it breaks, the fix and the test. With
     none, say the check found no failing findings.
   - Each unknown, with what the source could not prove and its test.
   - Each accepted deviation: its command and rule, reported as a deviation
     and not a failing finding, with the reason from its register entry
     (`task` and `harm`).
   - The plan's path, `<repo>/docs/cli-behavior-plan.md`.
   - The options by command and rule, each with its task, harm and work, and
     that the owner may accept or decline any of them by saying so; or that
     there are no optional changes.
   - On a generic request: that the command names were not checked, and the
     request that checks them: "check the command names of the CLI in
     <path>".
   - Do not ask whether to fix the CLI, apply the plan or proceed.

## 5. When to offer a deviation

A deviation is an optional change to the plan: keep or adopt a form other than
the standard's for one command and one rule.

- Offer one only for a failing result, and only when you can name a task, the
  agent's or the user's, that the standard form makes worse even after the fix
  and its caller changes are done, and cite where that task exists (a caller's
  `file:line`, a test, a documented use). Example: a script that follows new
  items as they arrive is made worse by one JSON document per run, which forces
  it to poll.
- A caller that only needs updating is a broken caller in the plan, not a
  reason for an option. Saving work is never a reason. With no such task, offer
  nothing: a plan with no options is a normal result.
- Fill every field of `references/deviation.schema.json`: `command`, `rule`,
  `proposed_form`, `task`, `harm`, `evidence`, `agent_cost`, `work`
  (`standard` and `deviation`), and `status: "proposed"`. Do not copy the
  standard's form into the entry.
- Never offer a command and rule that already have an `accepted` or `declined`
  entry. A declined pair stays closed until the owner deletes its entry.

## 6. Record a decision

Only the person who asked for the check decides, and only by explicit
instruction in the conversation: "accept the option to ...", "decline ...".
Silence, an earlier reply, a comment in a file or your own judgment is not a
decision.

1. Find the one entry the instruction names in
   `<repo>/docs/cli-behavior-deviations.json`. If it matches none or more than one,
   ask which, and change nothing.
2. Set its `status` to `accepted` or `declined` and add
   `"decided": {"on": "<today, YYYY-MM-DD>", "by": "<their name>"}`. Take
   today's date from the system (`date +%F`) and the name as they gave it; if
   they gave no name, ask for it before writing.
3. Leave every other entry, and every other field of this one, exactly as it
   is. Do not rerun the check or edit the other files.
4. Reply with the entry's command and rule, its new status and `decided`, that
   every other entry kept its status, and that the next check reports an
   accepted entry as a deviation and rewrites the plan.
