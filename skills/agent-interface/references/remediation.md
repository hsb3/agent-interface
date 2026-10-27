# Remediation procedures

How to build a CLI's command tree, search for callers of names being renamed, and write the rename plan. Build the tree on every run. Run the caller search and write the plan only on a fix run.

The repo root is the git repository that contains the CLI's source (`git -C <source folder> rev-parse --show-toplevel`), else the working directory. Both output files go under `docs/` there.

## Building the tree

Write `docs/cli-tree.json` in the format of [tree-format.md](tree-format.md). Read files only: never run the target CLI, not even `--help`, and never import it.

### Inputs

1. **Catalog.** If the repo has a `toolkit.json` (the agent-toolkits catalog file), read it. `surfaces.cli` is the CLI name (the tree's `cli`); each name in `tools` is an MCP tool name. Add the file to `sources` as `{"kind": "catalog", "ref": "toolkit.json"}`.
2. **Source.** Find where the CLI defines its commands and read every file that registers one. Add each as `{"kind": "source", "ref": "<repo-relative path>"}`. Without a catalog, the CLI name comes from argparse `prog=`, the console-script or `bin` entry point, or commander's `.name()`. The CLI name is never a path word.

### Reading argv paths

A path is the chain of names from the root parser down to a leaf (a command with no subcommands of its own). Groups are not entries.

**argparse**
- `p.add_subparsers()` opens a level; each `sub.add_parser("name")` adds a word under the parser that owns `sub`. Follow the variables: `issue = nouns.add_parser("issue").add_subparsers()` then `issue.add_parser("ls")` is `["issue", "ls"]`.
- `aliases=["x"]` gives each alias its own entry, the same path with the last word replaced.
- The handler is the `set_defaults(func=...)` function, or the `if args.verb == ...` branch that runs it.
- `help=argparse.SUPPRESS`, or a `metavar` that leaves a choice out, only hides it from help.

**click**
- `@click.group()` makes a group; `@grp.command()` and `@grp.group()` add children; `grp.add_command(cmd, name="x")` adds `cmd` under `x`, else under its own name.
- The name is the `name` argument, else the function name, lowercased. Since click 7, `_` becomes `-` (`def list_all` is `list-all`); since click 8.2, a trailing `_command`, `_cmd`, `_group` or `_grp` is also dropped. Check the click version the project pins.
- The root group is the one the entry point names; its name is the CLI, not a path word.
- `hidden=True` only hides it from help.

**commander**
- `program.command("issue")` returns the new command; `issue.command("ls")` nests under it as `["issue", "ls"]`. Only the first word of `.command("get <id>")` is the name; `<id>` and `[x]` are arguments. `.addCommand(new Command("x"))` attaches a built command.
- `.command("name", "description")` (a description as the second argument) is a stand-alone executable subcommand: read its `<prog>-name` file as well.
- `.alias("ls")` and `.aliases([...])` give each alias its own entry, as for argparse.
- `{ hidden: true }` only hides it from help.

### Kind

Read each handler:

- It writes nothing to stdout, prints `renamed to: <argv>` on stderr and exits 2: `stub`. `renamed_to` is that argv split into words: `renamed to: tool issue list` gives `["tool", "issue", "list"]`.
- It runs the new command and also prints `renamed to: <argv>`: `alias`, with `renamed_to` taken the same way.
- Anything else: `command`. Hidden from help is a hint, not proof.

### Merging catalog and source

A CLI command and an MCP tool share one entry (both `path` and `mcp_name` set) only when the source shows they are the same operation, for example the tool handler calls the command's function. Otherwise each gets its own entry; the catalog tool has `path: null` and `source: "toolkit.json"`. The dispatcher form (`call <name>`) and catalog-generated paths follow the rules in [tree-format.md](tree-format.md).

### Sources that cannot be read

`sources` lists only files actually read. If any registration cannot be read, for example `add_admin_commands(sub)` imported from a module that is not in the repo, or commands built at run time from data you cannot read, then:

- set `complete: false`;
- keep every source you did read in `sources`, and never list the unread one;
- remember the unread name (here `tool_admin`) so the reply can say what could not be read.

### Rebuilding

If `docs/cli-tree.json` already exists, copy its `local_verbs` into the new tree exactly. Never add a local verb unless the owner asks for it.

## Caller search

Run only on a fix run, after the check, for the violations whose `suggest` is not null. If no violation has one, run no search and write the plan with `"search": []` and `"renames": []`.

### Roots

- If the user names folders, search only those: no default roots, no crontab, no launchd.
- Otherwise: `~/Developer`, `~/.claude`, `~/.codex`, `~/.claude.json`, `~/.zshrc`, `~/.zprofile`, `~/.bashrc`, `~/.bash_profile`, `~/.profile`, plus crontab and launchd (below). Leave out roots that do not exist.

### Exclusions

`dev-memory.me`, session transcripts (`~/.claude/projects`, `~/.codex/sessions`, `~/.codex/archived_sessions`), plugin caches (`~/.claude/plugins/cache`, `~/.codex/plugins/cache`), `.git`, `distributions/`, `node_modules`, and the CLI's `docs/cli-tree.json` and `docs/cli-renames.json`. Stale names in these places are what the permanent stub is for.

### Patterns

For each rename, all fixed strings:

- space form: `<cli> <old path>`, for example `tool issue ls`;
- argv-list form: `"tool", "issue", "ls"`;
- for an MCP rename, the old MCP name: `list_notes`.

### The command

One `rg` run covers every pattern of every rename:

```sh
rg --hidden --line-number --fixed-strings --with-filename --no-heading --only-matching \
  -e '<pattern>' ... \
  --glob '!dev-memory.me' --glob '!**/.claude/projects/**' --glob '!**/.codex/sessions/**' \
  --glob '!**/.codex/archived_sessions/**' --glob '!**/.codex/plugins/cache/**' \
  --glob '!**/.claude/plugins/cache/**' --glob '!.git' --glob '!distributions' \
  --glob '!node_modules' --glob '!**/docs/cli-tree.json' --glob '!**/docs/cli-renames.json' \
  <root> ...
```

Example, for `tool issue ls` over the current directory:

```sh
rg --hidden --line-number --fixed-strings --with-filename --no-heading --only-matching \
  -e 'tool issue ls' -e '"tool", "issue", "ls"' \
  --glob '!dev-memory.me' --glob '!**/.claude/projects/**' --glob '!**/.codex/sessions/**' \
  --glob '!**/.codex/archived_sessions/**' --glob '!**/.codex/plugins/cache/**' \
  --glob '!**/.claude/plugins/cache/**' --glob '!.git' --glob '!distributions' \
  --glob '!node_modules' --glob '!**/docs/cli-tree.json' --glob '!**/docs/cli-renames.json' \
  .
```

- Put each pattern in single quotes, so the double quotes of the argv form need no escaping. Write a single quote inside a pattern as `'\''`.
- `--only-matching` makes each line `file:line:<the pattern that matched>`. The pattern tells you which rename the match belongs to, and no file contents are printed.
- Exit 1 means no matches. Exit 2 with output means some path was unreadable; keep the matches.

### Crontab and launchd (default roots only)

```sh
crontab -l 2>/dev/null | rg --line-number --only-matching --fixed-strings -e '<pattern>' ... | sed 's/^/crontab:/'
find ~/Library/LaunchAgents -name '*.plist' 2>/dev/null | while IFS= read -r p; do plutil -convert xml1 -o - "$p" | rg --line-number --only-matching --fixed-strings -e '<pattern>' ... | sed "s|^|$p:|"; done
```

The `find` form works in zsh and bash and does nothing when there are no plists. The caller is `crontab:<line>`, or `<plist path>:<line in the converted output>`.

### Without rg

If `rg` is not on PATH, run the equivalent `grep` and record it the same way. `--exclude-dir` matches only a folder's own name, so the multi-part exclusions are filtered from the output instead:

```sh
grep -rnoHF -e '<pattern>' ... --exclude-dir=dev-memory.me --exclude-dir=.git \
  --exclude-dir=distributions --exclude-dir=node_modules \
  --exclude=cli-tree.json --exclude=cli-renames.json <root> ... \
  | grep -vF -e /.claude/projects/ -e /.codex/sessions/ -e /.codex/archived_sessions/ \
    -e /.claude/plugins/cache/ -e /.codex/plugins/cache/
```

### Recording

Record each command exactly as run, in order, for the plan's `search` field. Join continued lines into one, and keep `~` as typed rather than the expanded home path.

The search is best effort. It misses commands assembled from variables, files outside the roots, and files a repo's `.gitignore` hides from `rg`. The permanent stub catches those callers.

## The rename plan: `docs/cli-renames.json`

Write it in the CLI's repo, only on a fix run. Rewrite it whole each time; never merge it with an old plan.

| Field | Value |
|-------|-------|
| `standard_version` | The check envelope's `standard_version`. |
| `search` | The exact commands run, in order. |
| `renames` | A list of `{old, new, callers}`. |

- `renames` holds only violations whose `suggest` is not null, one entry per old name: several findings on one command propose the same name, so list it once. Findings with `suggest: null` (confirm-only synonyms, collisions, advisories) never appear.
- `old` and `new` are the finding's `path` and `suggest` exactly as the check prints them: a space-joined CLI path without the CLI name (`issue ls` to `issue list`), or an MCP name (`list_notes` to `note_list`).
- `callers` is a de-duplicated list of `file:line` strings, sorted by file and then line, or `[]` when none were found. A path under the home folder is written `~/`-relative. Any other path is relative to the search root that contained it, with a leading `./` removed. Never write an absolute path or the matched text: caller files can hold secrets.

Example, from a default-roots search:

```json
{
  "standard_version": 1,
  "search": [
    "rg --hidden --line-number --fixed-strings --with-filename --no-heading --only-matching -e 'tool issue ls' -e '\"tool\", \"issue\", \"ls\"' -e 'list_notes' --glob '!dev-memory.me' --glob '!**/.claude/projects/**' --glob '!**/.codex/sessions/**' --glob '!**/.codex/archived_sessions/**' --glob '!**/.codex/plugins/cache/**' --glob '!**/.claude/plugins/cache/**' --glob '!.git' --glob '!distributions' --glob '!node_modules' --glob '!**/docs/cli-tree.json' --glob '!**/docs/cli-renames.json' ~/Developer ~/.claude ~/.codex ~/.claude.json ~/.zshrc ~/.zprofile",
    "crontab -l 2>/dev/null | rg --line-number --only-matching --fixed-strings -e 'tool issue ls' -e '\"tool\", \"issue\", \"ls\"' -e 'list_notes' | sed 's/^/crontab:/'",
    "find ~/Library/LaunchAgents -name '*.plist' 2>/dev/null | while IFS= read -r p; do plutil -convert xml1 -o - \"$p\" | rg --line-number --only-matching --fixed-strings -e 'tool issue ls' -e '\"tool\", \"issue\", \"ls\"' -e 'list_notes' | sed \"s|^|$p:|\"; done"
  ],
  "renames": [
    {
      "old": "issue ls",
      "new": "issue list",
      "callers": ["crontab:4", "~/Developer/tool/scripts/standup.sh:3", "~/Developer/tool/tests/test_cli.py:12"]
    },
    {
      "old": "list_notes",
      "new": "note_list",
      "callers": ["~/.claude/settings.json:27"]
    }
  ]
}
```

The skill never edits the CLI or its callers. The owner reviews the plan and applies it.
