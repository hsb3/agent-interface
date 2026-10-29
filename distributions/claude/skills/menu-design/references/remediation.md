# Remediation procedures

The repo root and how to build the tree are in [command-tree.md](../../../resources/command-tree.md).

## Caller search

Run only on a fix run, after the check, for the violations whose `suggest` is not null. If no violation has one, run no search.

### Roots

- If the user names folders, search only those: no default roots, no crontab, no launchd.
- Give `.` and any relative folder as an absolute path, written `~/...` when it is under the home folder (`~/Developer/tool` or `/work/tool`, never `.`). Run `rg` in a subshell from `/` (`(cd / && rg ...)`): it matches the exclusion globs against each path relative to the working directory, so run from inside `~/.claude` the `.claude/` part is lost and transcripts and plugin caches are searched.
- Otherwise: `~/Developer`, `~/.claude`, `~/.codex`, `~/.claude.json`, `~/.zshrc`, `~/.zprofile`, `~/.bashrc`, `~/.bash_profile`, `~/.profile`, plus crontab and launchd (below). Leave out roots that do not exist.

### Exclusions

`dev-memory.me`, session transcripts (`~/.claude/projects`, `~/.codex/sessions`, `~/.codex/archived_sessions`), plugin caches (`~/.claude/plugins/cache`, `~/.codex/plugins/cache`), `.git`, `distributions/`, `node_modules`, and the CLI's `docs/cli-tree.json` and `docs/cli-renames.json`.

### Patterns

For each rename, all fixed strings:

- space form: `<cli> <old path>`, for example `tool issue ls`;
- argv-list form: the old path's words, `"issue", "ls"`. This also finds lists that start with the CLI name (`["tool", "issue", "ls"]`) and in-process calls that pass argv without it (`main(["issue", "ls"])`). For a one-word path, use `"tool", "ls"`; its in-process form `["ls"` also matches unrelated calls such as `run(["ls", "-la"])`, so it is searched only in the CLI's own repo, in a second `rg` run (below);
- for an MCP rename, the old MCP name: `list_notes`.

### The command

One `rg` run covers every pattern of every rename:

```sh
(cd / && rg --hidden --line-number --fixed-strings --with-filename --no-heading --only-matching \
  -e '<pattern>' ... \
  --glob '!dev-memory.me' --glob '!**/.claude/projects/**' --glob '!**/.codex/sessions/**' \
  --glob '!**/.codex/archived_sessions/**' --glob '!**/.codex/plugins/cache/**' \
  --glob '!**/.claude/plugins/cache/**' --glob '!.git' --glob '!distributions' \
  --glob '!node_modules' --glob '!**/docs/cli-tree.json' --glob '!**/docs/cli-renames.json' \
  <root> ...)
```

Example, for `tool issue ls` over the repo at `/work/tool`:

```sh
(cd / && rg --hidden --line-number --fixed-strings --with-filename --no-heading --only-matching \
  -e 'tool issue ls' -e '"issue", "ls"' \
  --glob '!dev-memory.me' --glob '!**/.claude/projects/**' --glob '!**/.codex/sessions/**' \
  --glob '!**/.codex/archived_sessions/**' --glob '!**/.codex/plugins/cache/**' \
  --glob '!**/.claude/plugins/cache/**' --glob '!.git' --glob '!distributions' \
  --glob '!node_modules' --glob '!**/docs/cli-tree.json' --glob '!**/docs/cli-renames.json' \
  /work/tool)
```

When a renamed path has one word, run the same command a second time with only the `["<word>"` patterns and the CLI's repo root as the only root.

- Put each pattern in single quotes, so the double quotes of the argv form need no escaping. Write a single quote inside a pattern as `'\''`.
- `--only-matching` makes each line `file:line:<the pattern that matched>`. The pattern tells you which rename the match belongs to, and no file contents are printed.
- Exit 1 means no matches. Exit 2 with output means some path was unreadable; keep the matches.

### Crontab and launchd (default roots only)

```sh
crontab -l 2>/dev/null | rg --line-number --only-matching --fixed-strings -e '<pattern>' ... | sed 's/^/crontab:/'
find ~/Library/LaunchAgents -name '*.plist' 2>/dev/null | while IFS= read -r p; do plutil -convert xml1 -o - "$p" | rg --line-number --only-matching --fixed-strings -e '<pattern>' ... | sed "s|^|$p:|"; done
```

The caller is `crontab:<line>`, or `<plist path>:<line in the converted output>`.

### Without rg

If `rg` is not on PATH, run:

```sh
grep -rnoHF -e '<pattern>' ... --exclude-dir=dev-memory.me --exclude-dir=.git \
  --exclude-dir=distributions --exclude-dir=node_modules \
  --exclude=cli-tree.json --exclude=cli-renames.json <root> ... \
  | grep -vF -e /.claude/projects/ -e /.codex/sessions/ -e /.codex/archived_sessions/ \
    -e /.claude/plugins/cache/ -e /.codex/plugins/cache/
```

### Recording

Record each command exactly as run, in order, for the plan's `search` field. Join continued lines into one, and keep `~` as typed rather than the expanded home path.

The search is best effort: it misses commands assembled from variables, files outside the roots, and files a repo's `.gitignore` hides from `rg`.

## The rename plan: `docs/cli-renames.json`

Write it in the CLI's repo, only on a fix run. Rewrite it whole each time; never merge it with an old plan. With no violation whose `suggest` is not null, write `"search": []` and `"renames": []`.

| Field | Value |
|-------|-------|
| `standard_version` | The check envelope's `data.standard_version`. |
| `search` | The recorded commands. |
| `renames` | A list of `{old, new, callers}`. |

- `renames` holds only violations whose `suggest` is not null, one entry per old name.
- `old` and `new` are the finding's `path` and `suggest` exactly as the check prints them: a space-joined CLI path without the CLI name (`issue ls` to `issue list`), or an MCP name (`list_notes` to `note_list`).
- `callers` is a de-duplicated list of `file:line` strings, sorted by file and then line, or `[]` when none were found. A path under the home folder is written `~/`-relative. Any other path is relative to the search root that contained it, with a leading `./` removed. Never write an absolute path or the matched text.

Example, from a default-roots search:

```json
{
  "standard_version": 1,
  "search": [
    "(cd / && rg --hidden --line-number --fixed-strings --with-filename --no-heading --only-matching -e 'tool issue ls' -e '\"issue\", \"ls\"' -e 'list_notes' --glob '!dev-memory.me' --glob '!**/.claude/projects/**' --glob '!**/.codex/sessions/**' --glob '!**/.codex/archived_sessions/**' --glob '!**/.codex/plugins/cache/**' --glob '!**/.claude/plugins/cache/**' --glob '!.git' --glob '!distributions' --glob '!node_modules' --glob '!**/docs/cli-tree.json' --glob '!**/docs/cli-renames.json' ~/Developer ~/.claude ~/.codex ~/.claude.json ~/.zshrc ~/.zprofile)",
    "crontab -l 2>/dev/null | rg --line-number --only-matching --fixed-strings -e 'tool issue ls' -e '\"issue\", \"ls\"' -e 'list_notes' | sed 's/^/crontab:/'",
    "find ~/Library/LaunchAgents -name '*.plist' 2>/dev/null | while IFS= read -r p; do plutil -convert xml1 -o - \"$p\" | rg --line-number --only-matching --fixed-strings -e 'tool issue ls' -e '\"issue\", \"ls\"' -e 'list_notes' | sed \"s|^|$p:|\"; done"
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

Never edit the CLI or its callers.
