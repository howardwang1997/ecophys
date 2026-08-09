---
name: project_workshop_audit_2026-07-22
description: 2026-07-22 audit of the two Paper-A workshop drafts, live NeurIPS 2026 targets, exp126 evidence, and submission blockers
metadata:
  type: project
---

## Venue correction (supersedes the 2026-06-19 target names)

As of 2026-07-22, after the official July 11 NeurIPS workshop-notification date, the public accepted
workshop registry contains neither ML4PS nor Generative AI in Finance for 2026. Do not continue writing
to those names without direct contradictory evidence from their organizers.

Closest live targets:

- **STODY — AI for Stochastic Dynamics: From Theoretical Foundations to Scientific Applications**
  (Sydney): best fit for the driven-transient stochastic-dynamics manuscript. Short-paper deadline
  2026-08-29 AoE.
- **Sim2Science — ML with Imperfect Scientific Models** (Paris): best fit for a genuinely distinct
  burn-in/stationarity-audit and simulator-misspecification paper. Five pages, double blind,
  non-archival; deadline 2026-08-29 AoE.

**2026-08-06 submission-status verification.** Both replacement venues are already open on OpenReview.
The public submission-invitation metadata gives STODY `cdate=2026-07-20 12:00 UTC` (2026-07-21 00:00
NZST) and Sim2Sci `cdate=2026-07-27 11:59 UTC` (2026-07-27 23:59 NZST). Both give
`duedate=2026-08-30 11:59 UTC`, i.e. 2026-08-29 23:59 AoE / 2026-08-30 23:59 NZST. The workshop
websites publish the common deadline but do not separately state an opening date; treat the OpenReview
invitation activation times as the authoritative operational opening times.

Recommended split: STODY owns controlled stochastic dynamics, mechanism contrasts, and the saturating
dip-amplitude law. Sim2Science owns the evaluation failure, warm-up sensitivity protocol, and the
second-generator transfer test. Do not send the current overlapping drafts unchanged: all five stored
figure assets are byte-identical and the evidence/text overlap is substantial. Ask both organizers about
related submissions and disclose the relationship if both are submitted.

## 2026-08-06 alternative-workshop scan

The defensible alternatives to the two primary targets are:

- **FMTS — Foundation Models for Temporal Systems**: best fallback for the stationarity/evaluation paper.
  The CFP explicitly welcomes simulators and temporal environments, transaction streams, regime shift,
  long-horizon/simulation consistency, and negative or preliminary results. Deadline 2026-08-29 AoE;
  four pages, double blind, non-archival. Fit is only medium-high because EcoMD is not a foundation model;
  pitch it as rigorous evaluation of a persistent-state temporal simulator, never as a foundation model.
- **AI for Science — Verification in the Age of AI Scientists**: a second credible fallback if W3/W4
  turns the stationarity gate into an actual verifier with specificity and failure-mode evidence. The CFP
  explicitly covers verification under imperfect simulators and surrogate-versus-experiment calibration.
  Deadline 2026-08-29 AoE; 4--8 pages, double blind, non-archival. A mere EcoMD warm-up anomaly is not
  enough for this venue.
- **DynaFront — Dynamics at Frontiers of Optimization, Sampling, and Games**: conditional fallback for
  the STODY paper only after a real mathematical contribution on Langevin relaxation, ergodicity, or
  sampling dynamics. The official CFP deadline is extended to 2026-09-04 AoE. The current empirical
  intervention atlas alone is a weak fit, so STODY remains clearly preferable.

Do not target R/PS, GDDL, PriGM, XAI4Science, or EconML with the current evidence. R/PS/GDDL require a
genuine representation/geometric-distributional contribution; PriGM needs generative-model theory;
XAI4Science is centered on interpretable foundation models in weather/climate; EconML is economics *for
ML* and interacting AI-model ecosystems, not a finance or market-simulation workshop. In particular, do
not revive the false MACE/equivariance description to manufacture an R/PS or GDDL fit.

Finance-specific watchlist: ICAIF 2026 workshop proposals are being notified 2026-08-03--09 and each
accepted workshop will set its own paper deadline; recheck when the accepted-workshop CFPs appear. The
Economic Complexity and Macroeconomic Dynamics workshop was thematically strong but its 2026-07-15
deadline has passed. FinNLP closes 2026-08-11 AoE but is an NLP/financial-document venue and is not a
credible destination for the present simulator papers.

Treat FMTS, AI for Science, and DynaFront as alternative routes, not additional copies of the same paper.
The present plan should still produce at most two genuinely distinct manuscripts: STODY for driven
dynamics and one of Sim2Science/FMTS/AI-for-Science for stationarity-aware evaluation.

## Implementation-to-paper correction

The producing exp 123/126 configs use `pairwise_kind: stochastic_mlp`, i.e. the permutation-symmetrized
Stochastic Pair Sampling pair-potential implementation. They do **not** use MACE-lite or E(3)-equivariant
message passing. MACE-lite v1 is the canonical failed architecture (0–4/11) retained as a failure record.
Both paper bodies and the shared hero figure currently say MACE-like/equivariant and must be corrected.

Differentiability supports gradient calibration, sensitivities, and potentially optimized control. The
scheduled shock interface is a simulator API feature and is not caused by differentiability. Raw ED and
|rho| are simulated latent-flow proxies; do not call them empirical order flow/OFI without L2 validation.
`liquidity_drop` is operationally a temporary multiplier that lowers effective Langevin friction; describe
it as a reduced-friction/depth proxy and state the mapping assumption.

## Exp 126 status relevant to the papers

- Full atlas, n=24 per arm: coherent kick strongly fattens the return tail on SPX/NDX/BTC/Gold but is weak
  on EURUSD; `temp5_d20` is essentially control; `liq5_d20` fattens tails on all five, with different
  magnitude. This supports “coherence/reduced friction, not generic thermal agitation,” within EcoMD.
- Dense dose law supports a saturating **dip-amplitude** curve (SPX R²=0.9743). It does not support the
  current dose-dependent-tau headline: SPX `tau_recovery` is 350 at all eight doses under the new
  estimator. Reconcile estimators and demote tau(dose).
- Raw ED Hill is nearly flat in N; raw and EWMA-standardized return Hill rise strongly over N. The
  pre-registered α_ret_std criterion passes, but a clean causal mechanism claim still needs
  `sigma_price=0`, fixed-SNR, and deterministic post-impact-term decomposition because the nonlinear
  impact/additive-noise mixture changes with N.
- G-D1b: 12 Lévy configs trained, but none has a local scored Pareto point. The rescue script exists at
  `scripts/gd1b_score_and_emit.sh`. Before H20 execution, fix the observable mismatch: exp 123 logs raw
  pre-impact ED, while exp126 Lévy configs omit `log_raw_excess_demand` and the scorer labels the
  post-impact quantity `steady_alphaED`.
- The current no-shock Pareto path also calls the window scorer with `shock_step=3000`; downstream
  `steady()` therefore averages only `[500,3000)` instead of the full post-warm-up interval. Existing
  `baseline_tdf5` has `ed_is_raw=0` as well. Rescore baseline and all Lévy arms with raw ED and explicit
  no-shock semantics; distinguish rollout count from checkpoint-seed count.
- G-E second-generator warm-up validation remains unrun/manual. Without it, cross-generator and
  “standard practice” claims must be narrowed to an EcoMD case study.

## Submission-critical wording constraints

- Hill alpha near 0.5 is a censored estimator floor; do not infer non-existence of moments from it.
- Five crypto episodes show **no systematic crash-induced heavy-up** with limited power; they do not
  establish universal/stationary real-market tails.
- `state_kick` imposes the instantaneous coherence by construction. Emergent content is recovery,
  dose-response, and contrasts with other intervention channels.
- `price_jump` updates realized return, price level, and volatility EWMA and can feed back through global
  state. Its weak downstream effect is a model-specific result, not a general statement that price/news
  shocks are inert.

## Repository health observed 2026-07-22

400 tests collected; 398 pass after excluding one Mac-OOM slow BPTT test and one stale hard-coded RNG
golden. The golden predates the intentional 2026-05-22 seeded SPS edge-sampling fix and should be replaced
with an invariant A/B equivalence test. `mypy --strict` reports 131 errors in 32/54 package files; focused
F/E9/B Ruff reports 77 findings. README and scripts README are materially stale. These are engineering
debts, but paper-critical observables/scorers, the RNG test, and Python-3.11 syntax should be fixed before
broad cleanup.
