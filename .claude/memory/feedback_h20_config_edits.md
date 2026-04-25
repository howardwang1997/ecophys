---
name: H20 edits configs in-place during runs — don't revert
description: Every H20 training run may edit YAML configs (chunk_steps, grad_clip, etc.) to fit the actual hardware. When pulling H20-side commits back to Mac, treat those edits as ground truth and don't overwrite them.
type: feedback
---

# H20 in-place config edits

**Rule**: Every time the user runs a training script on H20, expect that
the config file gets edited in place to fit the actual hardware (most
commonly OOM-driven changes to `chunk_steps`, but also `grad_clip`,
`n_iters`, batch sizes). The edits are pushed back as part of the H20
results commit.

**Why**: H20 user (or auto-tuner) finds the highest stable values for the
machine and locks them. The 2026-04-25 H20 run #1 edited
`experiments/{013,014,016,017}/config_*.yaml chunk_steps: 32 → 24` because
32 OOMs at 96 GB HBM; this was committed as part of "h20 run". On Mac I
later wrote a new config and bumped chunk back to 32 — the user pointed
out this would break the next H20 run.

**How to apply**:
1. **When writing a new H20 config**, do NOT pre-set hardware-bound
   fields (`chunk_steps`, `grad_clip_max_norm`, `n_iters` if H20 might
   short-cycle) to specific values without leaving a comment that the
   H20 user can re-tune. Better: pick the largest value known to work,
   add a comment `# H20: tune down if OOM`.
2. **When pulling H20 commits**, `git diff` configs first. If H20 changed
   a field, treat it as authoritative. Do not "restore" the Mac value
   unless explicitly asked.
3. **When proposing a config retry**, copy the H20-current config and
   apply only the new knobs (κ, ws, lr, etc.); do not regress the
   hardware fields back to Mac defaults.

This reduces the friction of running on H20 because the user does not
have to re-tweak the same OOM fix on every cycle.
