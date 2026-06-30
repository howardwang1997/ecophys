# exp 126 — work plan (natural language)

**Date:** 2026-06-30. **Branch:** `feature/paper-a-figures-voice`. Companion to `DESIGN.md` /
`PREREG.md`. Plain-language plan for running the workshop-strengthening suite on the fleet. The 4-card
box is still down, so this suite is sized for **three GPU boxes: one 8-card and two 2-card**.

## Goal of this run
Give each of the two workshop papers a complete, honest core. For **ML4PS**: the decisive trained-Lévy
Route-A point (does end-to-end heavy-noise training buy a stationary heavy tail, and at what clustering
cost?), the relaxation/dose law extended to all five assets, and a re-pre-registered, artifact-
controlled test of the return-tail self-averaging. For **GenAI-in-Finance**: the controllability atlas
completed to all five assets and both shock durations, so the "coherence/liquidity, not thermal
agitation" mechanism is shown on the full surface. No retraining except the Lévy models; no data buy.

## The machines and who does what
Three GPU boxes are in play (the 4-card box is offline; any CPU box stays idle):

- **8-card box** — the workhorse and the long pole. It does the only training in this suite: the
  **G-D1b Lévy models** (three configs, one card each, ~4 h), then **scores** those checkpoints plus
  the shipped Student-t baseline, and finally runs the **controllability-atlas duration completion**
  (the two missing assets at the sustained duration, and a one-step-duration contrast across all five
  assets). It carries the most because training dominates the wall-clock.
- **2-card orchestrator** — the box you launch everything from. Besides coordinating, it runs its own
  local slice: the **spx return-self-averaging N-scan** (saving trajectories so the vol-standardized
  control can be computed). It reaches the other two boxes over the internal network and starts their
  jobs by SSH; **this Claude session cannot reach the boxes, so the orchestration must originate here.**
- **other 2-card box** — runs the **dose law on the two missing assets** (gold, eurusd) and the **btc
  return-self-averaging N-scan**. It finishes earliest, so it is the natural place to add the optional
  **G-E second-generator** job afterward, if time remains.

All three reuse the existing `concave_d050` checkpoints (5 assets) pulled from R2; only G-D1b trains.

## How it is launched
One command on the orchestrator box: `bash scripts/gpu_exp126_orchestrate.sh launch`. It (1) updates the
code and pulls checkpoints from R2 on every node, (2) starts the 8-card and other-2-card batches
detached with `nohup` so they survive disconnects, and (3) runs the orchestrator's own local batch.
Preview first with `DRY=1 bash scripts/gpu_exp126_orchestrate.sh launch`. The node addresses come from
`scripts/machines.local.json` on the orchestrator (keys `gpu8`, `gpu2b`, `localhost`); override the two
remote keys inline if yours differ, e.g. `NODE_8CARD=h20_1 NODE_2CARD=h20_3 bash …orchestrate.sh launch`.

## Timeline (estimate)
Basis: ~4 h per single-card training (matches `scripts/_h20_1_batch.sh`'s 14400 s cap) and ~3 min per
8000-step rollout per card (exp 114), padded ~30% for checkpoint loading, the R2 pull, and the fact that
my estimates run short.

- 8-card box: G-D1b train (3 cards busy ~4 h, others idle) → score (4 models, minutes) → atlas dur
  completion (~1–2 h) ⇒ **~5–7 h** end to end, train being the long pole.
- 2-card orchestrator: spx N-scan (~3–4 h).
- other 2-card box: gold+eurusd dose + btc N-scan (~5–6 h), then free for optional G-E.

So expect a **single overnight window (~6–8 h)**, with the 8-card box the long pole. The orchestrator
and the other 2-card box finish earlier.

## Monitoring
`bash scripts/gpu_exp126_orchestrate.sh status` any time — it counts the Lévy checkpoints written and
the trajectory files on each node and tails each node's log. A node is done when its log prints
`EXP126_8CARD_DONE` / `EXP126_2CARDB_DONE`. **Do not gather until the 8-card prints its DONE line** —
training is the long pole and the score step runs after it.

## Gather and evaluate
When all three nodes are done: `bash scripts/gpu_exp126_orchestrate.sh gather` rsyncs the remote results
(including the Lévy checkpoints and score trajectories) back to the orchestrator, then
`… eval` runs the windowed tail-index on every arm and the four analysis scripts —
`aggregate_atlas_cis.py` (rigor CIs + the coherent/incoherent contrast), `fit_tau_dose_law.py` (the
5-asset dose law), `score_noise_ablation.py` (the tail-vs-clustering Pareto, now including the trained
Lévy point), and `analyze_return_self_averaging.py` (α_ED/α_ret/α_ret_std vs N) — and pushes the report
JSONs to git. All four already run on the Mac against the exp-125 JSONs; on H20 they additionally pick up
the new arms and the trajectory npz for the vol-standardized control.

## What each result will mean (decided in advance, per PREREG)
- **G-D1b (trained Lévy):** a heavier stationary tail at a clustering/leverage cost ⇒ the named missing
  ingredient + the Pareto cost (ML4PS headline). It self-averages anyway ⇒ the light tail is a property
  of the learned dynamics, not the noise (still positive). Either way report (hill, ACF², leverage).
- **H-D2′ (return self-averaging):** vol-standardized α_ret rises with N ⇒ genuine CLT on returns (the
  re-pre-registered two-stage mechanism). Flat ⇒ the raw rise was a scaling artifact and α_ED-flat
  stands. Only the standardized control licenses the headline.
- **G-B′ (atlas):** confirms liquidity revives / temperature does not, on the full 5-asset × dur surface.
- **G-C′ (dose law):** a clean τ/dip(dose) law on all five assets (best-fit form + R² per asset).

## Contingencies
- A node refuses to start (missing checkpoint): run `bash scripts/h20_pull_from_r2.sh` on it.
- A node dies mid-run: arms are independent and idempotent per output tag; relaunch only that node's
  batch (re-run the matching block from the orchestrator, or the per-node Option-B command in the
  driver header).
- **Lévy α=1.5 training diverges (NaN):** expected possibility for an infinite-variance bath through
  BPTT. It is a reportable finding (PREREG H-D1b stability note); α=1.7 (two seeds) carries the claim.
  If α=1.7 also diverges, fall back to α=1.9 by adding `config_levy19_spx_seed0.yaml` (same recipe).
- If the 8-card box is under contention, move the atlas dur completion onto the early-finishing other
  2-card box (its arms are pure inference).
