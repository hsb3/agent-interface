# Testing

| Tier | Command | Needs | Proves |
| --- | --- | --- | --- |
| Unit | `bin/gate` | uv | Manifests agree, links resolve, every spec scenario names an existing eval and every eval is traced, images stay on the brand palette, packages are lean and reproducible, distributions are current |
| Install | `bin/gate tests/integration` | `claude`, `codex`, `openspec` CLIs; no model use | Claude strict validation passes; Codex installs the plugin in a throwaway `CODEX_HOME`; OpenSpec schema and specs validate strictly |
| Behavior | `claude plugin eval . --runs 1 --no-publish --allow-tools Write,Bash` | Claude login; uses model quota | Skills route and produce their artifacts, with a no-plugin baseline |
| Live Codex | `PLUGIN_LIVE=1 bin/gate tests/integration` | Codex login; uses model quota | Installed skill is discovered and read in a real `codex exec` turn |

CI runs the unit tier only. Install, behavior and live tiers run locally before a
release; record each run below.

## Host record

| Host | Version | Date | Commit | Install | Behavior | Notes |
| --- | --- | --- | --- | --- | --- | --- |
