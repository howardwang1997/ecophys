# exp 125 — root-cause ablations + controllability atlas + rigor (workshop/NCS strengthening)

**Date:** 2026-06-29. **Purpose:** operationalize `papers/proposal/paper_a_rootcause_and_reframe_2026-06-29.md`.
Convert the central "negative" (light steady-state tail) into a *positive mechanistic result*
(why the tail is light + the exact missing ingredient), add the rigor and positive
controllability/relaxation results the two workshops need, and do it all **pre-registered** (see
`PREREG.md`). **No data buy.** Runs on existing `concave_d050` checkpoints (5 assets) on the
2+2+4+8 H20 fleet. Inference-only except G-D1b and G-E (small training).

All rollouts: `N_STEPS=8000`, `T_SHOCK=3000`, windowed Hill `W=500 stride=100 k_frac=0.1`, OFI logged,
warm-up discard `[0,500)` for any *steady-state* number (the burn-in fix — `project_burnin_artifact.md`).

## Checkpoints / configs (reuse)
- spx: `experiments/113_gabaix_solve/results_concave_d050_seed0/checkpoint.pt`
- ndx/gold/btc/eurusd: `experiments/114_concave_confirm/results_<asset>_concave_d050_seed0/checkpoint.pt`
- configs: `experiments/123_driven_transient/config_<asset>.yaml`
- (pull from R2 if absent: `bash scripts/h20_pull_from_r2.sh`)

---

## G-A — rigor: seed-robust headline numbers (both papers)
**Why:** every headline number currently lacks error bars (NCS table = 16 seeds, < the project ≥20–30
rule for a heavy-tail quantity — `feedback_seed_count_lottery`). Replace point estimates with mean+CI.
- **Arms:** `control`, `kick6` — **all 5 assets**, **n = 30 seeds**, OFI logged.
- **Plus the warm-up table:** `baseline` + `concave_d050`, `--save-trajectory`, n = 30, scored
  no-discard vs discard-50 (the 3.87→6.55 / 5.05→9.26 table).
- **Outputs (CI'd):** post-shock min α_ED, |ρ| spike, OFI-memory burst, dip-window excess kurtosis;
  warm-up Δ table. → `aggregate_atlas_cis.json`.

## G-B — controllability atlas: mechanism-robustness (GenAI lead, positive)
**Why:** rebut "state_kick is a mechanical latent perturbation" and turn binary controllability into a
graded **control surface**. Two *non-mechanical* market-meaningful drivers (new code, smoke-tested
`scripts/smoke_exp125_channels.py`): `temperature_spike` (T×m, a volatility/agitation shock) and
`liquidity_drop` (γ×1/d, a depth withdrawal — consistent with the model's own leverage-γ coupling,
`ecomd.py:88`).
- **Arms:** `control`, `kick6` (ref), `temp{m}` ∈ {2,3,5,8}, `liq{d}` ∈ {2,3,5,10} — with
  `--shock-dur` ∈ {1,20} (dur sweep; dur=20 the primary, since one-step T/γ is weak — see smoke).
- **Assets:** spx, ndx, btc (the 3 strong-signature assets) + gold; **n = 20**.
- **Outputs:** full signature (α_ED transient depth+τ, |ρ| spike, OFI-mem burst) per channel; the
  channel×observable atlas table + the price_jump-inert contrast.

## G-C — relaxation law + sharpened dose-response (ML4PS lead, positive)
**Why:** physics referees want a functional form for τ(dose) (now "no single τ, CV 71%").
- **Arms:** dense `state_kick` dose `kick{m}`, m ∈ {0.05,0.1,0.15,0.2,0.3,0.5,0.8,1,2,3,6,12}, spx +
  (ndx,btc); **n = 20**.
- **Outputs:** τ(dose) fit to candidate forms (power law τ ∝ (m−m_c)^{-z}; log; saturating); sigmoid
  dose-response with CIs. → `tau_dose_law.json`. Also fit the floor-free **dip-kurtosis(dose)**
  (avoids the α≈0.5 estimator floor).

## G-D — root-cause ablations: WHY the steady tail is light (THE NEW CORE, positive mechanism)
**Why:** convert N1 into the interventional mechanism (`reframe` §2–§3). All steady-state numbers are
warm-up-discarded.
- **G-D1a (Route A, cheap, inference-only).** On each asset's trained ckpt, override the bath noise at
  inference: `--noise-dist {normal,t(df5),t(df3),levy(α1.9),levy(α1.7),levy(α1.5)}`, **no shock**,
  measure **steady-state α_ED + all 11 facts**. *Predict:* heavier bath → heavier steady tail
  (α_ED↓), monotone in 1/df and in (2−α_levy); volatility-clustering ACF² degrades as the tail
  fattens (the Pareto cost). spx + btc; n = 20.
- **G-D1b (Route A, the real claim, small training).** **Train** spx with `noise_dist=levy,
  α=1.7` (2 seeds, 8-card) and score all 11 facts. *Predict:* a trained heavy-noise model reaches a
  stationary heavy tail but at a clustering/leverage cost (the Pareto frontier made explicit).
- **G-D2 (CLT self-averaging, cheap, decisive).** On the spx ckpt, **fixed trained dynamics**,
  override `--n-agents` N ∈ {100,300,1000,3000,10000,30000}, **no shock**, measure steady-state α_ED.
  *Predict:* α_ED **increases (lighter) with N** — the self-averaging signature. (This is the clean
  test exp 120's train-at-N confounded: here dynamics are held fixed, only N changes.) n = 20.
- **G-D3 (coupling/criticality sweep, optional).** Scale the pair-potential output (a `--pair-gain`
  multiplier, if cheap to add; else skip) and measure steady-state α_ED vs coupling. *Predict:*
  heavy-up only near a coordination threshold. Lower priority.

## G-E — transferable pitfall on a 2nd generator (both papers, positive "protocol")
**Why:** the warm-up pitfall is currently EcoMD-only (a conjecture). Validate on a 2nd model family.
- Reuse the neural-SDE baseline (`scripts/h20_108_neural_sde_scout.sh` / exp 108-110 infra): score its
  Hill **no-discard vs discard-50**. *Predict:* the same inflation → the audit is a transferable
  protocol, not an EcoMD quirk. 2-card; ~½ day if a ckpt exists, else 1 train.

---

## Fleet allocation (2+2+4+8 = 16 GPU; ~1 work-day window)
| node | jobs | ~rollouts | est. |
|---|---|---|---|
| **8-card** | G-B atlas (4 assets × ~10 arms × 20) + G-D1b train (2 seeds) | ~800 + train | ~6–8 h |
| **4-card** | G-A (5 assets × 2 × 30) + warm-up table | ~360 | ~4–5 h |
| **2-card #1** | G-C dose sweep (3 assets × 12 × 20) | ~720 | ~5–6 h |
| **2-card #2** | G-D1a noise (2 assets × 6 × 20) + G-D2 N-scan (6 × 20) + G-E | ~360 + train | ~5–6 h |
| CPU node | (idle; reserved for later L2) | | |

Rate basis: ~3 min/rollout/card at N_STEPS=8000 (exp 114: ~6 min / 4 rollouts on 2 cards). My
estimates run short — reserve EVAL time (`feedback_h20_day_budget`, `project_h20_fleet_scheduling`).

## Launch
`scripts/gpu_exp125_atlas.sh` — `fanout` (driver SSH) or per-node `worker`/`ablate` (see its header).
Analysis: `aggregate_atlas_cis.py`, `fit_tau_dose_law.py`, `score_noise_ablation.py` (reuse
`score_phase.py`/`compute_all` for the 11 facts), then commit reports + push.
