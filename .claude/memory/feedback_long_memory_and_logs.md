---
name: Long-term memory and work logging discipline (EcoPhys)
description: User explicitly requires Claude to maintain long-term memory in this project's .claude/ dir AND write dated work logs after each session. Purpose is cross-session continuity and reproducibility.
type: feedback
originSessionId: c6748c05-53ac-462d-9535-154e95f91d9f
---
# Long-term Memory + Work Logs

**Rule**: After every substantive work session on EcoPhys, update two locations:
1. **Global project memory** at `/Users/howardwang/.claude/projects/-Users-howardwang-Desktop-playground-ecophys/memory/` — update existing files when facts change; add new memory files when new lasting context emerges.
2. **Project work log** at `<repo>/logs/YYYY-MM-DD.md` — one file per calendar date the session touched. Append if the file already exists.

**Why**: User stated: "你要在每次工作后把工作记录在文档里" (you must record work in docs after each session). Solo research → future-self continuity depends on these logs. Also a habit a good researcher maintains (not just for Claude).

**How to apply**:
- **Work log structure** (`logs/YYYY-MM-DD.md`):
  - `## Session N (HH:MM)` — if multiple sessions per day
  - Goal of session
  - What was done (key decisions, code changes, experiments run, papers read)
  - Results / findings (metrics, unexpected observations)
  - Open questions / blockers
  - Next steps
- **Memory file discipline**:
  - Project-level facts that will remain true → update `project_overview.md`
  - User preferences that emerge → new or updated `feedback_*.md`
  - New external resource (journal, dataset, tool) → update `reference_*.md`
  - Don't write ephemeral task state to memory — that belongs in logs/tasks.
- Whenever a memory file is changed or added, keep the `MEMORY.md` index accurate (one line per file).
- Whenever a substantive decision is made (architecture choice, venue target change, experiment design), record **the decision + its reason** so future-self can re-evaluate later.
