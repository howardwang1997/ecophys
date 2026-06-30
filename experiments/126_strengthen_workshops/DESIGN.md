# exp 126 — workshop-strengthening suite (ML4PS + GenAI-in-Finance)

**Date:** 2026-06-30. **Branch:** `feature/paper-a-figures-voice`. **No data buy.** Reuses the
`concave_d050` checkpoints (5 assets) for all inference arms; trains only G-D1b. Operationalizes the
post-exp-125 analysis (`logs/2026-06-30.md`): exp 125 came back with the primary CLT-on-ED test FLAT,
the heavy-noise Route-A only tested at inference (no Pareto trade), and G-D1b/G-E unrun; the atlas/dose
law covered 3 assets. This suite closes those gaps so each workshop has a complete, honest core.

All rollouts: `N_STEPS=8000`, `T_SHOCK=3000`, windowed Hill `W=500 stride=100 k_frac=0.1`, warm-up
discard `[0,500)` for any steady-state number. Estimators frozen as in exp 125 PREREG.

## G-D1b — TRAINED heavy-noise Route A (ML4PS core; the decisive test exp 125 skipped)
**Why:** exp 125 G-D1a showed *inference-time* Lévy noise does NOT heavy the steady tail (and reduces
clustering — no Pareto trade). The decisive question is whether **end-to-end training** with a heavy
bath reaches a heavy *stationary* tail, and at what cost to volatility clustering / leverage.
- **Train** spx with `noise_dist=levy`, `noise_levy_alpha ∈ {1.7 (×2 seeds), 1.5 (×1)}` — configs
  `config_levy{17,15}_spx_seed*.yaml`, **byte-identical to `config_concave_d050_seed0.yaml` except the
  bath-noise fields + seed** (clean attribution). 1 card/train, ~4 h each (8-card box).
- **Score** each trained ckpt + the as-shipped `concave_d050` (Student-t df5) baseline: NO shock,
  steady α_ED + all 11 facts. **Outputs** the tails-XOR-dynamics Pareto point: (hill_tail vs ACF²(r²)
  vs leverage) for {t-df5 baseline, Lévy1.7, Lévy1.5}.

## G-B′ — controllability atlas completion (GenAI core)
**Why:** exp 125 ran temp/liq on spx/ndx/btc only (gold/eurusd kick6-only), DUR=20 only.
- `temp{3,5}`, `liq{3,5}` on **gold + eurusd** at DUR=20 (atlas_dur20), and **DUR=1** on all 5 assets
  (atlas_dur1) — the duration contrast (one-step vs sustained drive). n≈24.
- Gives the full **5-asset × {state_kick, temperature, liquidity} × {dur 1,20}** control surface, and
  reconfirms the exp-125 finding (liquidity revives, temperature does not).

## G-C′ — relaxation/dose law completion (ML4PS core)
**Why:** dose law was spx/ndx/btc only; physics referees want it across markets.
- Dense `state_kick` dose `{0.05,0.1,0.2,0.5,1,2,6,12}` on **gold + eurusd**; n≈20.
- `fit_tau_dose_law.py` fits dip(dose) to saturating / power-law / log forms (R²) on all 5 assets.

## H-D2′ — return-tail self-averaging, re-pre-registered + artifact control (ML4PS refinement)
**Why:** exp 125 found α_ED flat but α_ret rising with N (≈1.3/decade). α_ret rising is the candidate
headline mechanism but was a *secondary* observable → must be re-pre-registered AND controlled for a
trivial return-scaling-with-N artifact.
- Re-run spx + btc `nscan{100…30000}`, **save trajectory**; `analyze_return_self_averaging.py` computes
  α_ED(N), α_ret(N), and the decisive **EWMA-vol-standardized α_ret(N)**. If the standardized return
  tail still lightens with N ⇒ genuine CLT shape change; if flat ⇒ scaling artifact and α_ED-flat stands.

## G-E (optional, lowest priority) — 2nd-generator warm-up pitfall (both papers)
Reuse `experiments/108_neural_sde_scout` / `scripts/h20_108_neural_sde_scout.sh`: score the neural-SDE
baseline's Hill no-discard vs discard-50. Validates the warm-up audit as a *transferable* protocol.
Run on the early-finishing 2-card box only if time remains (needs a neural-SDE ckpt or 1 train).

## Fleet (8 + 2 + 2 = 12 cards; 4-card still down) — see WORKPLAN.md
| node | jobs | est. |
|---|---|---|
| **8-card** | G-D1b train (3 cfgs) + score (4 models) + G-B′ atlas dur completion | ~5–7 h (train = long pole) |
| **2-card (other)** | G-C′ dose gold+eurusd + H-D2′ btc nscan | ~5–6 h |
| **2-card (orchestrator)** | H-D2′ spx nscan + drives the other two by SSH | ~3–4 h |

## Launch / analysis
`scripts/gpu_exp126_orchestrate.sh launch` (run ON the 2-card orchestrator; `DRY=1` to preview).
Per-node driver `scripts/gpu_exp126_strengthen.sh {train|score|worker|ablate|eval}`.
Analysis (also runs on Mac now): `aggregate_atlas_cis.py`, `fit_tau_dose_law.py`,
`score_noise_ablation.py`, `analyze_return_self_averaging.py` (all take `--exp <dirs…>`).
