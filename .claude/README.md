# `.claude/` — Project-Local Claude Code Configuration

This directory holds Claude Code configuration that is scoped to the EcoPhys project (as opposed to the global `~/.claude/`).

Currently empty by design — add only when a specific need arises:

- `settings.local.json` — permission grants and hooks specific to this repo (use the `update-config` skill / `/config` to manage)
- `agents/` — project-specific subagent definitions if custom research/code-review agents are needed
- `commands/` — project-specific slash commands

The project's behavioral guidance lives in the root `CLAUDE.md` and the global memory at `~/.claude/projects/-Users-howardwang-Desktop-playground-ecophys/memory/`, not here.
