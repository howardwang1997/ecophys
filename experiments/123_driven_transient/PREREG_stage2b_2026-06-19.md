# exp 123 Stage 2b — market-realistic shock channel (PRE-REGISTRATION, 2026-06-19)

**Frozen before any Stage 2b rollout.** NCS Gate 1 (see `papers/proposal/paper_a_b_ncs_strategy_2026-06-19.md`).

## Question

Stage 1/1.5/2a established the driven-transient (P) using `state_kick`, which displaces hidden
agent latents. A skeptic calls that **a mechanical latent perturbation, not market physics**. Does
the *same* heavy-tail dip-and-recover appear under an **exogenous, observable, economically-meaningful**
shock — a price gap?

## Channel (frozen)

**`price_jump`** (`ecomd/models/ecomd.py::_apply_shock`, validated `scripts/smoke_exp123_plumbing.py` T5):
at `T_SHOCK` inject an exogenous return `r = sign·mag·σ` (σ = the running volatility EWMA) into the
**realized return**. It (a) enters the recorded return series (a real price gap), (b) shifts the
observable log-price level, (c) re-drives the vol EWMA with the total move → clustering. Default
`sign=-1` (down-gap / crash); the Hill index is sign-blind. The heavy tail that follows is
**endogenous** — the model's response, not the injected point.

Contrast with `state_kick`: the perturbation lives in the **observable price**, not a hidden latent.
That is the rebuttal to "mechanical."

## Design (frozen)

- Asset: spx (concave_d050 ckpt reused). `n_steps=8000`, `T_SHOCK=3000`, n≈30 rollouts/arm.
- Arms: `control` (reused from Stage-1, channel-independent) + `jump{1,2,3,6,12}` (dose sweep, σ-units).
- Windowed Hill α_ED(t): W=500, stride=100, k_frac=0.1 (same estimator as Stage 1).

## Hypotheses + thresholds (frozen; reuse the Stage-1 H1–H4 gate, light≥4, heavy≤2, cube≈1.5)

- **H1** control steady-state [500,3000) α_ED ≥ 4 (light). *(reuse the existing spx control.)*
- **H2** ≥1 jump dose drives post-shock min α_ED ≤ 2 (the tail revives), graded with dose.
- **H3** every revived arm recovers to α_ED ≥ 4 by ~step 7000 (transient, not a permanent flip).
- **H4** post-shock min α_ED matches the t<500 burn-in template (|Δ| ≤ 1.0) — same mechanism.

## Known caveat (pre-registered, not post-hoc)

The injected gap is a single large |return| at `T_SHOCK`; with W=500/stride=100 it sits inside the
~5 windows centered within ±250 of `T_SHOCK`. So α in the **event window** (`[T_SHOCK, T_SHOCK+~500]`)
is partly the injected outlier, *not* purely endogenous. The **endogenous** signal is α remaining
depressed **beyond** `T_SHOCK+W` and then recovering (state_kick recovered over ~1000 steps = 2W).
We read H2/H3 as the persistence-and-recovery **past the event window**, and report the event-window
α separately. This is standard event-study hygiene.

## Decision (frozen, binding)

- **H1 ∧ H2 ∧ H3 ∧ H4 (past the event window) ⇒ Gate 1 PASS.** A market-realistic exogenous shock
  reproduces the driven transient → the effect is not a `state_kick` artifact; claim *driven-transient
  market dynamics*, not just latent mechanics. NCS Gate 1 met.
- **No revival at any dose ⇒ price_jump inert.** The level/return shock does not propagate into a tail.
  Report honestly; keep NCS Gate 1 OPEN; Paper A scopes the transient claim to the `state_kick`
  probe + names this as a limitation. Do **not** soft-pedal a null (see memory: no-downgrade).
- **Revival but H3 fails (permanent flip) ⇒** the exogenous shock pushes a regime change, not a
  transient — a different (still interesting) claim; reframe, do not force the unification.

Verdict artifact: `verdict_spx_jump.json` (`score_transfer_law.py --verdict … --channel jump`).
