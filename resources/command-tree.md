# Command tree

Both skills describe a CLI's commands in one file, `docs/cli-tree.json` in the CLI's repo. This file gives its format, how the repo root is found, and how to build it from the CLI's catalog and source.

## Repo root

The repo root is the working directory when the CLI's catalog or source is inside it. Otherwise it is the git repository that contains the CLI's source (`git -C <source folder> rev-parse --show-toplevel`). In a monorepo, it is the CLI's own folder, the one holding its `toolkit.json` or package file.

## The tree file

The command-tree file lists every command and MCP tool name of one CLI. An agent writes it to `docs/cli-tree.json` in the CLI's repo. `tree.py check` reads it. A file that breaks any rule below makes the check exit 2 with an `INVALID_ARGUMENT` error. The naming rules the check applies are in `cli-naming.md`, in the menu-design skill.

### Top-level fields

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `cli` | string | yes | The CLI's name. |
| `sources` | list of `{kind, ref}` | yes | Every source read. `kind` is `"catalog"` or `"source"`. `ref` is a repo-relative path. |
| `complete` | boolean | yes | `false` when a source could not be read. |
| `local_verbs` | list of strings | no | Words approved for this CLI only. Only the owner adds them. Keep them when the tree is rebuilt. |
| `commands` | list of commands | yes | May be empty. |

### Command fields

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `path` | array of words, or `null` | yes (key) | The argv words of the command. `null` for an MCP tool with no CLI command. Never an empty array; each word is non-empty and has no spaces. |
| `mcp_name` | string, or `null` | yes (key) | The MCP tool name, with no empty word between underscores. At least one of `path` and `mcp_name` is non-null. |
| `kind` | `"command"`, `"alias"` or `"stub"` | yes | What the entry is. |
| `source` | string | yes | One of the `sources[].ref` values: the source this command was read from. Findings about the command report it. |
| `renamed_to` | non-empty array of words | for `alias` and `stub` | The new argv, for example `["notes", "note", "list"]`; for a framework alias, the argv of the command it runs, CLI name first (`["tool", "issue", "list"]`). |

### Rules

- The check trusts `kind` as written. The agent sets it from the source.
- The check skips commands of kind `alias` and `stub`.
- A dispatcher CLI runs tools as `call <name>`. List each tool by `mcp_name` with `path: null`, and leave out `call`. The reply then says its names were checked as MCP names only.
- A CLI whose command paths are generated from a catalog records the paths it actually exposes. The catalog is their `source`.

### Example

```json
{
  "cli": "notes",
  "sources": [
    {"kind": "catalog", "ref": "toolkit.json"},
    {"kind": "source", "ref": "src/notes/cli.py"}
  ],
  "complete": true,
  "local_verbs": ["archive"],
  "commands": [
    {"path": ["note", "list"], "mcp_name": "note_list", "kind": "command", "source": "src/notes/cli.py"},
    {"path": ["note", "ls"], "mcp_name": null, "kind": "stub", "source": "src/notes/cli.py", "renamed_to": ["notes", "note", "list"]},
    {"path": null, "mcp_name": "note_search", "kind": "command", "source": "toolkit.json"}
  ]
}
```

## Building the tree

Write `docs/cli-tree.json` in the format above. Read files only: never run the target CLI, not even `--help`, and never import it.

### Inputs

1. **Catalog.** If the repo has a `toolkit.json` (the agent-toolkits catalog file), read it. `surfaces.cli` is the CLI name (the tree's `cli`); each name in `tools` is an MCP tool name. Add the file to `sources` as `{"kind": "catalog", "ref": "toolkit.json"}`.
2. **Source.** Find where the CLI defines its commands and read every file that registers one. Add each as `{"kind": "source", "ref": "<repo-relative path>"}`. Without a catalog, the CLI name comes from argparse `prog=`, the console-script or `bin` entry point, or commander's `.name()`. The CLI name is never a path word.

### Reading argv paths

A path is the chain of names from the root parser down to a leaf (a command with no subcommands of its own).

**argparse**
- `p.add_subparsers()` opens a level; each `sub.add_parser("name")` adds a word under the parser that owns `sub`. Follow the variables: `issue = nouns.add_parser("issue").add_subparsers()` then `issue.add_parser("ls")` is `["issue", "ls"]`.
- `aliases=["x"]` gives each alias its own entry: the same path with the last word replaced, `kind: "alias"`, and `renamed_to` the full argv of the command it aliases, CLI name first (`["tool", "issue", "list"]`).
- The handler is the `set_defaults(func=...)` function, or the `if args.verb == ...` branch that runs it.

**click**
- `@click.group()` makes a group; `@grp.command()` and `@grp.group()` add children; `grp.add_command(cmd, name="x")` adds `cmd` under `x`, else under its own name.
- The name is the `name` argument, else the function name, lowercased. Since click 7, `_` becomes `-` (`def list_all` is `list-all`); since click 8.2, a trailing `_command`, `_cmd`, `_group` or `_grp` is also dropped. Check the click version the project pins.

**commander**
- `program.command("issue")` returns the new command; `issue.command("ls")` nests under it as `["issue", "ls"]`. Only the first word of `.command("get <id>")` is the name; `<id>` and `[x]` are arguments. `.addCommand(new Command("x"))` attaches a built command.
- `.command("name", "description")` is a stand-alone executable subcommand: read its `<prog>-name` file as well.
- `.alias("ls")` and `.aliases([...])` give each alias its own entry, recorded as for argparse `aliases=`.

### Entry kind

Read each handler:

- It writes nothing to stdout, prints `renamed to: <argv>` on stderr and exits 2: `stub`. `renamed_to` is that argv split into words: `renamed to: tool issue list` gives `["tool", "issue", "list"]`.
- It runs the new command and also prints `renamed to: <argv>`: `alias`, with `renamed_to` taken the same way. A framework alias (argparse `aliases=`, commander `.alias()`) is also `alias`, set as above.
- Anything else: `command`. Hidden from help (`help=argparse.SUPPRESS`, a `metavar` that leaves a choice out, click `hidden=True`, commander `{ hidden: true }`) is a hint, not proof.

### Merging catalog and source

A CLI command and an MCP tool share one entry (both `path` and `mcp_name` set) only when the source shows they are the same operation, for example the tool handler calls the command's function. Otherwise each gets its own entry; the catalog tool has `path: null` and `source: "toolkit.json"`. The dispatcher form (`call <name>`) and catalog-generated paths follow the rules above.

### Sources that cannot be read

If any registration cannot be read, for example `add_admin_commands(sub)` imported from a module that is not in the repo, or commands built at run time from data you cannot read, then:

- set `complete: false`;
- keep every source you did read in `sources`, and never list the unread one;
- remember the unread name (here `tool_admin`) so the reply can say what could not be read.

### Rebuilding

If `docs/cli-tree.json` already exists, copy its `local_verbs` into the new tree exactly. Never add a local verb unless the owner asks for it.
