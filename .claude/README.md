# `.claude/` — Project-Local Claude Code Configuration

This directory holds Claude Code configuration and persistent research memory
for the EcoPhys project.

## Layout

- `memory/` — **long-term research memory** (versioned in git). Contains:
  - `MEMORY.md` — index of all memory files
  - `project_overview.md` — research program + current plan status
  - `user_role.md` — user profile + hardware + budget
  - `feedback_*.md` — rules/preferences accumulated over sessions
  - `reference_*.md` — registries (data sources, venues)
  - Symlinked into `~/.claude/projects/-Users-howardwang-Desktop-playground-ecophys/memory/`
    so Claude Code reads it from the standard path while the files live in git.
- `settings.local.json` — local machine permission grants (git-ignored, see root `.gitignore`).
- Future: `agents/`, `commands/` if we add project-specific ones.

## Why memory is in git (decided 2026-04-24)

- **Version control**: research decisions need history, not be silently overwritten
- **Portability**: clone the repo → whole research context travels with it
- **Backup**: survives local machine loss
- **Reviewability**: changes to "project_overview" deserve diff scrutiny like code

**Canonical location** of memory is `.claude/memory/` in this repo.
The `~/.claude/projects/.../memory/` path is a symlink — Claude Code reads through
it, but never edit there directly.

## Adding new memory

Use Claude's memory tooling normally — it writes through the symlink into
`.claude/memory/` and `git status` will show the change. Review + commit as
you would any other research artifact.
