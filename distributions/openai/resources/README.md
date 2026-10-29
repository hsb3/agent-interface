# Resources

Canonical standards and shared instructions that more than one skill reads at
run time. Each file here is the single source: skills link to it by path and
never copy its rules.

- [cli-naming.json](cli-naming.json): the naming vocabulary (verbs, synonyms,
  short forms, plural exceptions, root commands). `menu-design` checks names
  against it; `cli-behavior` reads its verbs to give each command a kind.
- [command-tree.md](command-tree.md): the `docs/cli-tree.json` format, how the
  repo root is found, and how to build the tree. Both skills build trees with it.

A file used by only one skill belongs in that skill's `references/` folder
instead.
