# exp 126 — workshop-strengthening suite, FULL scope (ML4PS + GenAI-in-Finance)

**Date:** 2026-06-30. **Branch:** `feature/paper-a-figures-voice`. **No data buy.** Reuses the
`concave_d050` + `baseline` checkpoints (5 assets) for all inference; trains only the G-D1b Lévy Pareto.
Sized for **~a week on 4 cards (two 2-card boxes; one is the orchestrator, SSHing to the other)** — no
compute/time saving; run everything worth running. Operationalizes `logs/2026-06-30.md`: exp 125's
primary CLT-on-ED test was FLAT, heavy-noise Route A was only tested at inference, G-D1b/G-E unrun, and
the atlas/dose law covered 3 assets at one duration.

All rollouts: `N_STEPS=8000`, `T_SHOCK=3000`, windowed Hill `W=500 stride=100 k_frac=0.1`, warm-up
discard `[0,500)` for any steady-state number. Estimators frozen as in exp 125 PREREG.

## G-D1b — TRAINED heavy-noise Route-A PARETO (ML4PS core; the decisive test exp 125 skipped)
**Why:** exp 125 G-D1a showed *inference-time* Lévy noise does NOT heavy the steady tail (and reduces
clustering — no Pareto trade). The decisive question: does **end-to-end training** with a heavy bath
reach a heavy *stationary* tail, and at what cost to clustering/leverage?
- **Train** spx with `noise_dist=levy`, **α ∈ {1.9, 1.7, 1.5, 1.3} × 3 seeds = 12 models**
  (`config_levy{19,17,15,13}_spx_seed{0,1,2}.yaml`, byte-identical to `config_concave_d050_seed0.yaml`
  except the bath-noise field + seed — clean attribution). Smoke-validated on Mac (α=1.7 & 1.5 train
  with finite loss / no NaN, `logs/2026-06-30.md`).
- **Score** each trained ckpt + the shipped t(df5) baseline (NO shock): steady α_ED + all 11 facts,
  n≥30. **Output:** a **Pareto curve** hill_tail vs ACF²(r²) vs leverage as a function of α — the
  tails-XOR-dynamics frontier inside one architecture.

## G-B′ — controllability atlas, FULL surface (GenAI core)
**Why:** exp 125 ran temp/liq on 3 assets, DUR=20 only. Map the whole control surface.
- **5 assets × {temp3,temp5,temp8, liq3,liq5,liq10} × {DUR 1, 20, 50}** + `jump6` (price-jump-inert
  contrast, B2) + `control`. Each arm dir is `results_<asset>_<temp|liq><mag>_d<DUR>` so every
  magnitude×duration cell gets its own clean windowed report. n≈24.
- **Output:** the driver × magnitude × duration × asset control surface; reconfirms (liquidity revives,
  temperature does not), now with a magnitude axis (= the non-mechanical dose-response) and a duration
  axis (one-step vs sustained drive).

## G-C′ — relaxation/dose law, ALL 5 assets dense (ML4PS core)
- Dense `state_kick` dose `{0.05,0.1,0.2,0.5,1,2,6,12}` on **all 5 assets**, n≈24.
- `fit_tau_dose_law.py` fits dip(dose) to saturating / power-law / log forms (R²) per asset + onset.

## G-D2 + H-D2′ — α_ED-flat-in-N (5 assets) + return self-averaging w/ artifact control (ML4PS)
**Why:** confirm the refuted CLT-on-ED (α_ED flat) across all 5 assets at higher N, and decide whether
the return-tail self-averaging (α_ret rising) is genuine or a return-scaling artifact.
- **5 assets × N ∈ {100,300,1000,3000,10000,30000,60000,100000}**, save-trajectory, n≈32.
- `analyze_return_self_averaging.py`: α_ED(N), α_ret(N), and the decisive **EWMA-vol-standardized
  α_ret(N)** (re-pre-registered, see PREREG H-D2′).

## G-A — warm-up audit table (GenAI protocol core)
- Per-model no-discard-vs-discard Hill, computed from each model's own trajectory: the `control`
  (no-shock concave_d050) arms (5 assets, the dose block's control) + a **baseline-family** contrast
  (`spx`, `btcusdt` baseline checkpoints, no-shock) → `results_<asset>_warmup_baseline`. n≥40 on control.

## G-E — 2nd-generator warm-up pitfall (both papers) — SEPARATE block (see WORKPLAN.md)
Validate the warm-up audit on the neural-SDE generator family (`experiments/108_neural_sde_scout`).
**Not auto-wired** into the week-long detached run (different model class; can't smoke it here without
GPU) — a documented, ready-to-run block to fire after the core lands.

## NOT run
- **G-D3 coupling sweep:** `run_large` has no `--pair-gain`/coupling override → needs a code change;
  out of scope here. Noted as future work.
- **btc-Lévy training:** no verified btc `concave_d050` *training* config in-repo → the trained Pareto
  stays spx-only (the pre-registered asset); cross-asset light-tail evidence comes from the inference
  arms (G-D2 5-asset, G-D1a noise).

## Fleet & launch (4 cards; see WORKPLAN.md)
`scripts/gpu_exp126_orchestrate_2x2.sh launch` (run ON one 2-card box; `DRY=1` to preview). Per-node
driver `scripts/gpu_exp126_strengthen.sh {train|score|worker|ablate|noshock|eval}`. Analysis (also runs
on Mac): `aggregate_atlas_cis.py`, `fit_tau_dose_law.py`, `score_noise_ablation.py`,
`analyze_return_self_averaging.py`.
