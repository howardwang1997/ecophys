---
name: neural-sde-tournament-beyond-framework
description: "2026-05-29 program pivot: after Path A falsified + ABIDES 2-3/11 (paradigm-level ceiling), go BEYOND the Langevin framework via a tournament of new architectures, seeded by a scout. Hero = learned stochastic-vol / Neural-SDE diffusion."
metadata:
  type: project
---

**Why (2026-05-29):** Path A (per-fact surrogates, exp 107) was falsified (p=0.81) and
ABIDES — a different paradigm — scores only 2-3/11, so the ~5.1 ceiling is **paradigm-level,
not architecture-level**. The failing facts are ALL volatility-structure facts (fat tails #2,
agg-gaussianity #4, Fano #5, DFA long-memory #8). The simulator's volatility was fixed,
hand-designed, and **detached** (zero gradient). User directive: pursue the best result
**beyond the current architecture/framework**.

**Strategy (user choices):** a **tournament** of beyond-framework entrants on a 60h weekend,
seeded by a **5-6h scout** (exp 108). See plan `pull-adaptive-thacker.md` + addendum.

**Hero entrant = Neural-SDE stochastic-volatility head (BUILT + smoke-gated 2026-05-29):**
- `ecomd/models/stoch_vol.py` `StochVolProcess`: K-component mean-reverting **log-OU** latent.
  Multi-timescale (distinct kappa_k → DFA #8 / agg-gauss #4), stochastic innovation (tails #2 /
  Fano #5), asymmetric `relu(-r)` leverage coupling (#9/#11). `sigma_eff = sigma_price *
  exp(g·softmax(a)·v)`. Positivity (exp) + hard bound (tanh clamp) → no agg-gauss blow-up.
- Two placements, flag-gated: **price-level** (`price_formation_kwargs.sv_price_enabled`,
  primary — modulates the return scale) and **integrator-level** (`sv_integrator_enabled`,
  scales the Langevin noise → multiplicative-noise overdamped Langevin = Paper-B physics).
- **Key plumbing fact:** the vol latent rides in `PriceState` (the ONLY carrier surviving both
  the MMD/rollout-reg path and the custom-autograd packer). It is threaded through
  `EcoMDStepFunction` (has_vol flag, like h_global) and **must be detached in
  `train._detach_price`** — else the 512-step rollout-reg carries an O(512) graph → OOM/blow-up.
  Grouped-checkpoint path (bptt_checkpoint_every>0) raises (drops vol_latent); use 0.
- OFF (sv_price_enabled=False) = bit-exact prior behaviour (module not built, no extra RNG draw).
- **Build gate PASSED:** `tests/test_stoch_vol.py` (11 tests) + full suite 370 passed; N=500
  inference smoke: liveness (5/5 sv params get grad through custom-fn), loss 1.34→0.95,
  finite, **agg_gauss=411 (<1000), hill=4.20, DFA=0.800 in-band** — early vol-structure signal
  (NOT a result: n=1, N=500).

**Scout = exp 108** (`experiments/108_neural_sde_scout/`, launcher `h20_108_neural_sde_scout.sh
--probe`): 60 cfg = 5 cells × 12 seeds, SPX, N=10K fp32, reg_every=8 (~5h). Cells: baseline_mmd /
sv_d1 / sv_d3 / sv_d3_nolev / sv_d3_both. **Pre-registered scout gate (binds the weekend):** a
cell advances iff it lifts ≥1 hard floor (#2/#4/#5/#8) w/o ≥20pp collateral AND mean n/11 ≥
baseline_mmd. Attribution: d3−d1 = multi-timescale; d3−d3_nolev = leverage; both−d3 = placement.

**2026-05-29 SCOUT RESULT (exp 108) + revised plan:** SV head = **LATERAL Pareto move** — net
n/11 flat (~4.8 vs baseline_mmd), HELPS DFA #8 (33→45% in-band) / leverage #9 (33→50%) / gain-loss
#3, WORSENS the worst floor. **NEW diagnostic: the blocker is a fat-tail OVERSHOOT** — hill≈1.38,
91% of runs α<2 (infinite variance), band [2,4]; source = agent-level Student-t(df5)+jumps(λ0.5),
which SV amplifies. `sv_d3` hero cell was SIGTERM-killed (complete on weekend). User: run a BROAD
tournament (may exceed 60h); **demote SV** to a Paper-B confirmation leg (complete sv_d3 + keep
sv_d3_both for DFA/leverage gains).

**Entrants BUILT + smoked 2026-05-29 (tests: 378 passed):**
- **A2 MoE** — `ecomd/models/moe_router.py` `AgentExpertRouter`: soft learned per-agent gate over K
  (γ,T) experts = finite-variance mixture-of-normals fat tails (Lévy alternative) + info-asymmetry
  channel (NESS); load-balance reg via a ~4-line aux-loss hook in `train_distributed.py` (before
  `total.backward()`). EcoMDConfig flags OFF=bit-exact. Smoke: router live, expert usage uniform
  (no collapse), finite. ⚠ hill stayed 1.40 with tamed noise at N=500 → a DYNAMICAL tail source
  beyond the noise dist. exp 110 (5 cells×30, N=10K, MMD every=4).
- **A3 diffusion** — `ecomd/baselines/score_diffusion.py` conditional autoregressive DDPM
  (fit/sample baseline, registered in `scripts/run_baseline_fit_eval.py`). Smoke: OPPOSITE failure
  mode — finite tails (hill 5), DFA in-band, but undershoots vol-clustering. exp 111 (cond+marginal).
- **Bracket-0 tail attack** — exp 109 config-only grid noise_df{5,10,30,normal}×jump{0.5,0.1,0}×
  {SV off, sv_d3}, reg OFF (fast marginal screen): can hill enter [2,4] w/o collapsing Fano/agg?

**Weekend orchestrator:** `scripts/h20_weekend_tournament_2026-05-30.sh --probe` → tail-attack(109)
→ sv_d3 completion(108) → MoE(110) → diffusion(111) → score. **Per-FACT gate** (hill/agg/DFA
in-band rate, NOT just n/11 — the scout showed net n/11 hides per-fact movement) vs baseline_mmd.

**2026-06-01 TOURNAMENT RESULT (commit `ba57867cc`, verified on Mac from raw inference JSONs —
`conda run` swallows stdout here, use `~/miniconda3/envs/ecophys/bin/python` directly):**
NO entrant breaks the ~5.1-5.2 ceiling; "solve" arc still has no winner. But the **"diagnose"
is now strong + mechanistically grounded**:
- **Fat-tail overshoot is DYNAMICAL, not distributional (proven, the key finding).** 109
  `normal_j00` (Gaussian noise, jump_lambda=0) still gives hill=1.30 (band [2,4], deep α<2).
  Removing Student-t+jumps entirely does NOT fix tails → source is the excess-demand/interaction
  dynamics, not a noise knob. Kills noise-taming hypothesis cleanly.
- **MoE (mixture-of-Gaussians) did NOT pull hill into band** — best `moe_k4_tamed_lbw001` hill
  1.36, n/11 4.83 ≈ baseline parity. **Diffusion = exact OPPOSITE failure**: diffusion_cond hill
  3.15 IN BAND but acf2=0.09 (undershoots clustering) + agg=3.15 (too Gaussian, band [10,200]).
  Both hill AND agg flip the SIGN of their error between physics (overshoot) and generative
  (undershoot). **SV confirmed demoted** (sv_d3 worst, 4.33).
- **THE PAPER-A CONTRIBUTION (reframe):** a per-fact **Pareto frontier across 3 paradigms** where
  tail-shape and vol-dynamics are mutually exclusive — physics-sim=dynamics but overshoots tails
  (dynamically); deep-generative=tails but no dynamics; agent-based(ABIDES)=neither (2-3/11).
  Reframes Paper A from falsified "beat SOTA" → honest, stronger "map+explain a paradigm-level
  frontier." Config side-finding: jumps were hurting net (normal_j00 5.20 > t5+jump anchor 4.80).

Bracket 2 ceiling map: 111 + existing 080/095b SPX baselines + **ABIDES timescale-fair re-run**
(still owed; scripts exist, adjust to multi-sim-day→daily).

**2026-06-01 — exp 112 tail-clamp probe (the one untested lever; BUILT + smoked, awaiting H20):**
soft differentiable clamp `r=scale·tanh(r/scale)` in `price_formation.py` (`tail_clamp_c`/`_mode`,
OFF=bit-exact, via `price_formation_kwargs`). `tests/test_tail_clamp.py` (6) pass. exp 112 = 5
cells × 20 seeds, N=10K fp32, MMD every=4; launcher `h20_112_tail_clamp.sh`. **Pre-registered:
SOLVE iff hill∈[2,4] AND acf2 stays in-band (breaks the tail⊥dynamics coupling); else → commit
diagnose, clamp = final negative control.** Mac N=400 directional smoke (n=1, wiring/direction
only): clamp THINS tails (hill 3.06→4.9-5.6) AND drops acf2 (0.31→0.14-0.27) — Pareto coupling
visible; `rel_c3` retains most acf2. **KEY new fact: the fat-tail overshoot is N-DEPENDENT —
baseline hill=3.06 at N=400 vs 1.39 at N=10K**, so tail-fattening scales with system size (a
physics result for the diagnose), and the SOLVE gate can only be decided at N=10K. Prior: clamp
tightens the frontier but doesn't break it.

One untested mechanistic lever: a tail-clamp in the price-formation map (likely kills acf2 per
Pareto coupling — smoke supports this, H20 confirms). Champion confirmation moot unless 112 wins;
the diagnose figure is the deliverable.

**exp 112 Part B — α scaling-curve diagnose (BUILT, pure inference, folded into the 112 launcher,
commit `cfd691f86`):** turns the "why the overshoot exists" mechanism into a measured experiment.
Runs `run_large` from the trained Part-A baseline checkpoints under config overrides (a ckpt loads
cleanly across N — the N-sized buffers are `persistent=False`). 3 families, 3 ckpts × 22 cfg,
n_steps=8000, ~40min: **B1** hill(N) ed_norm=False (does the tail fatten with N? smoke 3.06@400→
1.39@10K), **B1n** hill(N) ed_norm=True CONTROL (should flatten → isolates aggregate-flow SNR:
collective mode ~N vs idiosyncratic ~√N), **B2** hill(κ_hawkes) AND acf2(κ) — self-excitation is
the SHARED source of tails+clustering, so this maps the Pareto coupling vs the actual control
param. Pre-registered (`score_scaling.py`, verified on synthetic data): B1 fit hill=α_inf+c/N,
**α_inf<2 ⇒ intrinsically infinite-variance in thermo limit**; B2 disjoint κ-windows ⇒ coupling
confirmed, overlap ⇒ a coupling-tuned knob-solve (better than the clamp). NOTE: temperature/gamma
are nn.Parameters (ckpt overrides config) so NOT scannable; hawkes_kappa/beta/ed_normalize are
ExcessDemandParams floats so they DO bite. Part A (solve) + Part B (why/how-hard) → diagnose
publishable either way.

**2026-06-01 — user: "not just a diagnose, I want the BEST result" → mechanism-level solve
(exp 113, BUILT on branch `feature/exp113-gabaix-solve` commit `566780fac`; ζ/δ ranges to be
re-centered when 112 scaling returns).** Why the tournament missed: every entrant
(MMD/MoE/SV/diffusion) attacked the loss/noise/paradigm layer, NONE changed the mechanism that
SETS the tail exponent (`log_ret=β·κ·Σ Δpos_i`). The principled untried lever with theory
predicting α≈3 = the **Gabaix mechanism** (GGPS Nature 2003): real markets' inverse-cubic law =
Zipf large-trader sizes (ζ≈1) × square-root impact. Our model lacks BOTH (homogeneous agents,
`excess_demand=κ·Σ dpos` no per-agent mass; linear impact). exp 113 = heterogeneous masses
`ED=κ·Σ wᵢ·Δposᵢ` (wᵢ power-law ζ) + concave impact `log_ret=β·sign(ED)·|ED|^δ` (δ≈0.5),
flag-gated OFF=bit-exact. These set the UNCONDITIONAL tail (size dist + impact) — a DIFFERENT
object from the Hawkes temporal feedback that makes clustering → plausibly DECOUPLES tails from
clustering (the clamp can't). Odds ~35-45% (targets right physics + has quantitative theory;
still a bet: power-law-mass training stability, concave-impact collateral unknown).
**CRITICAL design rule (user asked "can we add the target to the loss?"):** we ALREADY do
loss-only tail-matching (baseline `w_hill/soft_hill`; Path A exp 107 strong per-fact surrogates)
→ FALSIFIED p=0.81. **fact-as-loss-target on a FIXED mechanism = invalid test** — a loss only
selects within the mechanism's reachable set, and α≈3-with-clustering isn't in homogeneous
herding's manifold (that's what "paradigm ceiling" means). The CORRECT use: mechanism FIRST
(enlarge reachable set), THEN make the new params **ζ, δ learnable** and let `soft_hill` calibrate
them to α≈3 (loss constrains MECHANISM PARAMS, not output hill). 112 Part B's measured α(ζ,δ)
scaling validates the learned point (theory × data). Scope: these 2 mechanisms thorough → 5-asset
n=30, not a broad tournament. **BUILT:** price_formation.py (het_mass + concave-impact flags,
OFF=bit-exact, ζ=exp(mass_log_zeta)/δ=sigmoid(impact_logit_delta) learnable, join sim.parameters
→ soft_hill-calibrated), tests/test_gabaix_mechanism.py (9 pass), experiments/113_gabaix_solve
(6×30), scripts/score_gabaix.py (extracts LEARNED ζ/δ vs GGPS 1,0.5 + hill/acf2 gate),
h20_113_gabaix.sh. **Mac smoke sign-checks reframed the swing (2 findings):** (1) concave impact hill↑ AND acf2
KEPT (0.43→0.36) = the decoupling the clamp couldn't → **concave sqrt-impact (Tóth-Lillo-Bouchaud)
is the real lever.** (2) heterogeneous masses MISFIRED TWICE — v1 (wᵢ·Δposᵢ) thinned (dense
Gaussian → weighted Gaussian); v2 (additive Σwᵢ·tᵢ heavy flow) ALSO thinned (hill 3.24→5.39)
because FIXED Pareto weights → one whale dominates every step → time-tail tracks the innovation
(t df=4→hill≈4), NOT the size dist. Faithful GGPS would need a per-step heavy flow with learnable
tail index — but **our baseline already OVER-produces tail (hill 1.4), so adding size-heaviness is
the WRONG direction.** **DECISION (user 2026-06-01, option A): DROP masses, refocus exp 113 on a
clean CONCAVE-IMPACT solve.**

**exp 113 FINAL (concave-impact solve, on branch `feature/exp113-gabaix-solve`):** replace linear
β·ED with β·sign(ED)·s·(|ED|/s)^δ (price_formation.py, impact_concave_enabled, δ=sigmoid param,
OFF=bit-exact). 6 cells × 30: baseline / concave_d{040,050,060,070} fixed (the hill(δ) curve) /
concave_learn (δ learnable init 0.6, soft_hill-calibrated — does the loss FIND α≈3?). Gate:
hill∈[2,4] AND acf2∈[.15,.55] vs baseline → 5-asset n=30. score_gabaix.py extracts learned δ.
Het-masses code REMAINS gated-OFF in price_formation.py (kept for record, unused). Paper story:
"synchronization OVER-produces heavy tails (α<2); a concave sqrt-impact law restores the empirical
inverse-cubic α≈3 WHILE preserving clustering (reshapes the driver, not the return) — first
differentiable sim to hit both." See [[project_surrogate_rolloutlen_trap]], [[feedback_no_downgrade]].

See [[project_paper_a_neurips_2027]], [[project_pareto_ceiling]],
[[project_surrogate_rolloutlen_trap]], [[project_chunk_oom_constraint]], [[feedback_no_downgrade]].
