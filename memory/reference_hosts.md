# Host profiles: one section per machine

Every legatus reads **only this machine's section** at boot: `bash tools/legati/host-section.sh` prints the `## <hostname>` section that matches `hostname -s` (case-insensitive), up to the next `## ` heading. A machine without a section → the legatus tells you and does not assume a toolchain.

> [!todo] You
> Add one section per machine you work from (`/start-here`, step 6, writes the first one with you). Keep each section short: it is read at every session start. Delete the example below once you have your own.

## example-laptop

- **What it is:** laptop, macOS, Apple Silicon, 16 GB. Daily driver; travels.
- **Harnesses:** Claude Code (logged in); Codex (`codex login` done, `install-hooks.sh codex` run on 2026-11-22, hooks approved).
- **Repo path:** `~/Code/my-workshop`.
- **Toolchain:** `pandoc`, `typst`, `python3` 3.12, `uv`, `node`, `llm` (with the `llm-ollama` plugin).
- **Models:** no local models here; `llm -m gpt-…` with a key in `llm keys`; a local Ollama server on the desk machine when on the home network.
- **External repos:** none.
- **Notes:** on battery most of the day: no long local-model batches here.
