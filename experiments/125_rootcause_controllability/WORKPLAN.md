# exp 125 — work plan (natural language)

**Date:** 2026-06-29. **Branch:** `feature/paper-a-figures-voice`. Companion to `DESIGN.md` /
`PREREG.md` / the reframe doc. This is the plain-language plan for running the suite on the fleet now
that the **4-card box is down** and its load has been moved onto the 8-card box.

## Goal of this run
Turn the central "negative" (EcoMD's light steady-state tail) into the paper's positive, mechanistic
result, and produce the rigor + positive controllability/relaxation evidence the two workshops need.
The single most important number we are after is **G-D2: does the steady-state order-flow tail get
lighter as the number of agents N grows?** If yes, that is the direct interventional proof of CLT
self-averaging — the mechanism behind the whole story.

## The machines and who does what
Three GPU boxes are in play (the 4-card box is offline; the CPU box stays idle, reserved for later
limit-order-book work):

- **8-card box** — the workhorse. It runs the controllability atlas (G-B), the migrated rigor sweep
  that the dead 4-card box was meant to do (G-A), and the spx slices of the dose-law (G-C) and the
  root-cause ablations (G-D). It carries the most because it has the most cards.
- **2-card orchestrator** — the box you launch everything from. Besides coordinating, it runs its own
  local slice of the dose-law (the ndx and btc dose sweeps, G-C). It reaches the other two boxes over
  the internal network and starts their jobs by SSH; this Claude session cannot reach the boxes, so
  the orchestration must originate here.
- **other 2-card box** — runs the btc root-cause ablations (G-D), and finishes earliest, so it is the
  natural place to add the two optional training jobs afterward (G-D1b train-with-Lévy, G-E
  second-generator pitfall).

All three reuse the existing `concave_d050` checkpoints (5 assets) pulled from R2 — no retraining for
the main suite, no data purchase.

## How it is launched
One command on the orchestrator box: `bash scripts/gpu_exp125_orchestrate.sh launch`. It (1) updates
the code and pulls checkpoints from R2 on every node, (2) starts the 8-card and other-2-card batches
detached with `nohup` so they survive disconnects, and (3) runs the orchestrator's own local batch.
Preview first with `DRY=1 bash scripts/gpu_exp125_orchestrate.sh launch`. The node addresses come from
`scripts/machines.local.json` on the orchestrator (keys `gpu8`, `gpu2b`, and `localhost`).

## Timeline (estimate)
Basis: about 3 minutes per rollout per card at 8,000 steps (measured in exp 114), padded ~30% for
checkpoint loading, the R2 pull, and the fact that my estimates tend to run short.

- 8-card box: ~1,230 rollouts → **~8 hours** (≈10 h padded).
- 2-card orchestrator: ~320 rollouts → **~8 hours** (≈10 h padded).
- other 2-card box: ~240 rollouts → **~6 hours** (≈8 h padded), then free for the optional training.

So expect a **single overnight window (~10–11 hours)** end to end, with the 8-card box and the
orchestrator finishing together as the long poles. If you want a shorter ~5–6 h day-job instead, cut
the dose-law to spx+ndx only and drop the n from ~20 to ~16 — say the word and I will re-emit the
batches.

## Monitoring
Check progress any time with `bash scripts/gpu_exp125_orchestrate.sh status` — it counts the
trajectory files written on each node and tails each node's log. A node is done when its log prints
`EXP125_<NODE>_DONE`.

## Gather and evaluate
When all three nodes are done: `bash scripts/gpu_exp125_orchestrate.sh gather` rsyncs the remote
results back to the orchestrator, then `... eval` runs the windowed tail-index, the OFI signature, and
the per-arm scoring, and pushes the report JSONs to git. (Three small aggregation scripts —
`aggregate_atlas_cis.py`, `fit_tau_dose_law.py`, `score_noise_ablation.py` — are still to be written;
the raw data they consume is already captured by every run, so they can be added while the runs are in
flight. The 11 stylized facts per rollout are emitted automatically by the runner.)

## What each result will mean (decided in advance, per PREREG)
- **G-D2 (α_ED vs N):** rising with N ⇒ the headline mechanism figure (self-averaging proven). Flat ⇒
  the cause is the single-agent potential, not aggregation — still a clean localization.
- **G-D1 (heavy noise):** a stationary heavy tail appears, at a volatility-clustering cost ⇒ we have
  named and demonstrated the missing ingredient and the Pareto cost. It does not ⇒ the light tail is
  even more robust than CLT alone predicts.
- **G-B (atlas):** temperature-spike and liquidity-drop also revive the transient ⇒ "mechanism-robust,
  not a mechanical artifact" (GenAI headline). They do not ⇒ "specifically a coherence phenomenon" — a
  sharper mechanism statement. Either way is positive content; both are reported in full.
- **G-A / G-C:** error bars on every headline number, and a clean τ(dose) relaxation law.

## Contingencies
- A node refuses to start (missing checkpoint): run `bash scripts/h20_pull_from_r2.sh` on it.
- A node dies mid-run: its arms are independent and idempotent per output tag; re-launch only that
  node's batch.
- If the 8-card box is also under contention, move the spx G-C/G-D slices off it onto the
  early-finishing other-2-card box.
