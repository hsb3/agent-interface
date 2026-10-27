# Command-tree file format

The command-tree file lists every command and MCP tool name of one CLI. An agent writes it to `docs/cli-tree.json` in the CLI's repo. `tree.py check` reads it. A file that breaks any rule below makes the check exit 2 with an `invalid-tree` error.

## Top-level fields

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `cli` | string | yes | The CLI's name. |
| `sources` | list of `{kind, ref}` | yes | Every source read. `kind` is `"catalog"` or `"source"`. `ref` is a repo-relative path. |
| `complete` | boolean | yes | `false` when a source could not be read. |
| `local_verbs` | list of strings | no | Words approved for this CLI only. Only the owner adds them. Keep them when the tree is rebuilt. |
| `commands` | list of commands | yes | May be empty. |

## Command fields

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `path` | array of words, or `null` | yes (key) | The argv words of the command. `null` for an MCP tool with no CLI command. Never an empty array. |
| `mcp_name` | string, or `null` | yes (key) | The MCP tool name. At least one of `path` and `mcp_name` is non-null. |
| `kind` | `"command"`, `"alias"` or `"stub"` | yes | What the entry is. |
| `source` | string | yes | One of the `sources[].ref` values: the source this command was read from. Findings about the command report it. |
| `renamed_to` | array of words | for `alias` and `stub` | The new argv, starting with the CLI name. |

## Rules

- The check trusts `kind` as written. The agent sets it from the source.
- The check skips commands of kind `alias` and `stub`.
- A dispatcher CLI runs tools as `call <name>`. List each tool by `mcp_name` with `path: null`, and leave out `call`. The reply then says its names were checked as MCP names only.
- A CLI whose command paths are generated from a catalog records the paths it actually exposes. The catalog is their `source`.

## Example

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
