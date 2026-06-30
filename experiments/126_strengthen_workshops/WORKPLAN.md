# exp 126 — work plan (natural language), FULL scope on 4 cards

**Date:** 2026-06-30. **Branch:** `feature/paper-a-figures-voice`. Companion to `DESIGN.md` /
`PREREG.md`. Plain-language plan for the full workshop-strengthening suite on **two 2-card boxes
(4 cards)**, run unattended over about a week. No compute or time saving — everything worth running is
queued.

## Goal of this run
Give both workshop papers a complete, honest, thorough core. For **ML4PS**: a full trained-Lévy Pareto
curve (does end-to-end heavy-noise training buy a stationary heavy tail, and at what clustering/leverage
cost, across α=1.9→1.3?), the relaxation/dose law on all five assets, the α_ED-flat-in-N result
confirmed across five assets and out to N=100k, and the re-pre-registered, artifact-controlled
return-tail self-averaging test. For **GenAI-in-Finance**: the full controllability surface (five
assets × temperature/liquidity × three magnitudes × three durations) so the "coherence/liquidity, not
thermal agitation" mechanism is shown on the whole grid, plus the warm-up audit table. No data buy; the
only training is the Lévy models.

## The two machines and who does what
Two GPU boxes, two cards each. **One of them is the orchestrator** — you launch from it, it runs its own
half locally and SSHes the other box to run its half. **This Claude session cannot reach the boxes, so
the launch must originate on the orchestrator box.** The 8-card box is not used this round.

- **Orchestrator box (`localhost` in the node map, 2 cards)** — **owns all training** (so the Lévy
  checkpoints stay local for scoring). Its queue: (1) train the 12 Lévy models, (2) score them + the
  t(df5) baseline, (3) the **temperature** half of the controllability atlas (5 assets × 3 mags × 3
  durations), (4) the dense **dose law** on all 5 assets, (5) the **return self-averaging** N-scan for
  spx and ndx.
- **Other box (`gpu2b` by default, 2 cards, the SSH target)** — its queue: (1) the **liquidity** half of
  the atlas (5 assets × 3 mags × 3 durations) + the `price_jump` inert-contrast, (2) the **return
  self-averaging** N-scan for btc, gold, eurusd, (3) the **warm-up baseline-family** no-shock arms
  (spx, btc).

Both boxes reuse the existing `concave_d050` + `baseline` checkpoints pulled from R2; only the
orchestrator trains.

## How it is launched
One command on the orchestrator box: `bash scripts/gpu_exp126_orchestrate_2x2.sh launch`. It (1) updates
code and pulls checkpoints from R2 locally, (2) SSHes the other box and starts its batch detached with
`nohup`, and (3) starts the orchestrator's own batch **also detached with nohup**, so the command
returns immediately and both halves survive disconnects. Preview first with
`DRY=1 bash scripts/gpu_exp126_orchestrate_2x2.sh launch`. Node addresses come from
`scripts/machines.local.json` on the orchestrator (keys `localhost`, `gpu2b`); if the other box's key
differs, override inline: `NODE_2CARD=h20_3 bash scripts/gpu_exp126_orchestrate_2x2.sh launch`.

## Timeline (estimate)
Basis: ~62 min per single-card training (exp 114), ~3 min per 8000-step rollout per card (exp 114),
padded ~30% (and my estimates run short). Rough rollout budget: orchestrator ≈ train (12 cfgs ÷ 2 cards
× ~1 h ≈ 6 h) + score (~7 h) + atlas-temp (~27 h) + dose (~27 h) + self-averaging spx,ndx (~13 h);
other box ≈ atlas-liq (~27 h) + self-averaging btc,gold,eurusd (~19 h) + warm-up (~2 h). So **each box
≈ 3–3.5 days**, comfortably inside a week. The N=60k/100k self-averaging arms are slower than 3
min/rollout, so treat the tail of the schedule as the soft spot.

## Monitoring
`bash scripts/gpu_exp126_orchestrate_2x2.sh status` any time — counts the Lévy checkpoints written and
the trajectory files on each box, and tails each box's log. A box is done when its log prints
`EXP126_LOCAL_DONE` (orchestrator) / `EXP126_REMOTE_DONE` (other box). **Gather only after BOTH print
their DONE line.**

## Gather and evaluate
When both boxes are done: `bash scripts/gpu_exp126_orchestrate_2x2.sh gather` rsyncs the other box's
results (incl. the Lévy checkpoints and score trajectories) back to the orchestrator, then `… eval` runs
the windowed tail-index on every arm and the four analysis scripts —
`aggregate_atlas_cis.py` (rigor CIs + the full atlas surface + coherent/incoherent contrast),
`fit_tau_dose_law.py` (the 5-asset dose law), `score_noise_ablation.py` (the tail-vs-clustering Pareto,
incl. the trained Lévy curve + exp-125's G-D1a inference noise), and `analyze_return_self_averaging.py`
(α_ED/α_ret/α_ret_std vs N over 5 assets) — and pushes the report JSONs to git. All four are
smoke-validated on the exp-125 data on the Mac; on H20 they pick up the new arms and the trajectory npz
for the vol-standardized control.

## G-E — the one block left MANUAL (run it after the core, or skip)
The 2nd-generator warm-up validation uses a different model class (neural-SDE), which I could not
smoke-test here, so I did NOT wire its training into the week-long detached run (a NaN/hang mid-queue
could otherwise stall the core). To run it on the early-finishing other box once the core is in:
```
# on the other 2-card box, in the repo:
conda run -n ecophys python experiments/108_neural_sde_scout/generate_configs.py
bash scripts/h20_108_neural_sde_scout.sh --probe        # 1 cfg: stability + timing
DAEMON=1 PARALLEL=2 bash scripts/h20_108_neural_sde_scout.sh   # trim to a couple cells/seeds
```
Then roll out a resulting neural-SDE checkpoint no-shock with `--save-trajectory` and compare its Hill
no-discard vs discard-50 (the same windowed-vs-fact comparison the warm-up table uses). Tell me when its
trajectories exist and I'll fold the comparison into `aggregate_atlas_cis`.

## What each result will mean (decided in advance, per PREREG)
- **G-D1b Pareto:** heavier α → heavier stationary tail (hill down toward ~3) at rising clustering/
  leverage cost ⇒ the named missing ingredient + the quantified Pareto frontier (ML4PS headline). If it
  self-averages anyway ⇒ the light tail is a property of the learned dynamics, not the noise. Report the
  full (hill, ACF², leverage) vs α curve either way.
- **H-D2′:** vol-standardized α_ret rises with N ⇒ genuine CLT on returns (re-pre-registered two-stage
  mechanism); flat ⇒ the raw rise was a scaling artifact and α_ED-flat stands. Only the standardized
  control licenses the headline.
- **G-B′ / G-C′ / G-A:** the full control surface (liquidity revives / temperature doesn't, scaled in
  mag & dur), the 5-asset τ/dip(dose) law, and the warm-up no-discard-vs-discard table.

## Contingencies
- Missing checkpoint on a box: `bash scripts/h20_pull_from_r2.sh` there.
- A box dies mid-run: arms are independent and idempotent per (arm, tag); relaunch only that box's batch
  (re-run its block, or the per-node Option-B commands in the driver header).
- **Lévy α=1.3 training diverges (NaN):** plausible for the heaviest bath through BPTT (smoke only
  covered 1.7 & 1.5, both clean). It is a reportable finding (PREREG H-D1b stability note); the α=1.9/
  1.7/1.5 points carry the Pareto curve. The `train` step is non-fatal per-config (a dead config just
  leaves no checkpoint and `score` skips it).
- N=100k self-averaging arm too slow/OOM on a card: drop it (the 100→30k span already gives the trend);
  it is the last arm in each self-averaging block.
