# Paper A / Paper B venue strategy after the driven-transient pivot

> **⚠️ SUPERSEDED (2026-06-19 PM) by `paper_a_dual_track_plan_2026-06-19.md`.** This memo assumed the
> NCS anchor would be a real-market *return-tail* driven transient (Gate 2). The Stage 3 pilot
> (5 crypto crashes + a formal null test) **refuted** that: real return tails are stationary cube-law
> in calm and crash. The dual-track plan re-aims NCS at a *different observable* (order-flow/L2) and
> makes NeurIPS the primary track. Kept for history.

**Date:** 2026-06-19
**Status:** strategy memo after exp-123 Stage 1/1.5/2a — SUPERSEDED (see above)
**Context:** The stationary cube-law / concave-impact solve was refuted as burn-in-contaminated.
Exp 123 turned this into a stronger and more honest claim: in EcoMD, heavy tails are not stationary
properties, but driven non-equilibrium transients that recur under shock and relax back to a
light-tailed steady state.

## Executive decision

Paper A can be positioned for **Nature Computational Science** as a stretch target, but only if it is
written as a computational-science discovery enabled by a new simulator, not as a routine ML-methods
paper or a stylized-facts benchmark.

The safe default remains:

- **Paper A default target:** NeurIPS / ICML / ICLR-style methods + simulator physics.
- **Paper A stretch target:** Nature Computational Science, conditional on Stage 2b and a real-data
  pilot.
- **Paper B target:** Nature Physics / PRL / Science Advances, conditional on real-market
  thermodynamic signatures.

The relationship should be:

- **Paper A:** introduce EcoMD and use it for controlled computational experiments showing that
  heavy tails in a differentiable particle market simulator are reproducible driven transients.
- **Paper B:** test whether real markets obey the same non-equilibrium physics, using real crash
  windows, entropy production, effective temperature, Jarzynski/TUR-style protocols, and EcoMD as
  the calibrated measurement/counterfactual substrate.

## Why Nature Computational Science is plausible

Nature Computational Science's scope includes computational techniques, mathematical models,
simulation frameworks, and their use to solve complex scientific problems across applied physics
and computational social science. EcoMD fits this scope if framed correctly:

1. It is a differentiable particle simulator for a complex social/financial system.
2. It enables controlled interventions that are impossible in real markets.
3. It exposes non-equilibrium diagnostics: raw excess demand, windowed tail index, shock-response,
   relaxation time, and eventually entropy-production channels.
4. It converts a measurement failure into a computational-science result: warmup-inclusive scoring
   misreads a transient as a stationary law.

The NCS-worthy claim is not "we built a simulator." It is:

> A differentiable particle simulator enables controlled computational experiments on market
> non-equilibrium dynamics, revealing that heavy tails are driven transients rather than stationary
> properties.

This is close to NCS if the result is shown to be robust to realistic shock channels and anchored,
even lightly, in real market episodes.

## What Paper A should claim

Paper A should use careful scope control:

> We introduce EcoMD, a calibrated differentiable particle simulator for market dynamics. In this
> simulator, the steady state is light-tailed, while heavy tails emerge reproducibly under
> non-equilibrium driving and relax on a finite timescale.

Allowed strong claims:

- EcoMD is a calibrated differentiable particle simulator suitable for controlled non-equilibrium
  market experiments.
- In EcoMD / MD-style differentiable market simulation, warmup-inclusive rollout scoring confounds
  transient and stationary tails.
- Controlled shocks revive the same heavy-tail relaxation template seen at initialization.
- The effect generalizes across SPX, NDX, gold, BTC/USDT, and EUR/USD in exp 123.
- Thresholds are asset-dependent, plausibly scaling with intrinsic volatility.

Claims to avoid in Paper A unless Stage 3 is strong:

- "Real market fat tails are driven transients."
- "The inverse cubic law is explained in real markets."
- "Universal critical scaling" or "market thermodynamics is established."
- Nature Physics-level claims around T_eff, Jarzynski, TUR, or entropy-production universality.

Those belong to Paper B.

## What Paper B should claim

Paper B should start where Paper A stops:

> Real market stress episodes exhibit non-equilibrium transient signatures consistent with the
> controlled EcoMD protocols: tail-index dips, finite-time recovery, entropy-production bursts,
> and effective-temperature scaling.

Paper B's load-bearing evidence should be real data first:

- 2010 flash crash, 2020 COVID crash, FTX/Luna, SVB, FOMC or CPI windows.
- Windowed Hill alpha on returns and order-flow proxies.
- Relaxation-time fits and cross-asset scaling.
- Entropy production / effective temperature / TUR / Jarzynski protocols.
- EcoMD counterfactuals and mechanism decomposition as supporting evidence.

Paper B should not spend much space re-proving EcoMD. It should cite Paper A for the simulator,
calibration, shock protocol, and measurement caveats.

## NCS gate for Paper A

Paper A should be considered NCS-ready only if the following gates pass.

### Gate 1: market-realistic shock channel

Current exp 123 is strong but uses `state_kick`, which a skeptical reviewer can call a mechanical
latent-state perturbation.

Required:

- price-jump shock and/or liquidity-drop shock passes H1/H2/H3/H4;
- ideally one information/news channel, if propagation is meaningful in the current model;
- the alpha dip-and-recover shape remains close to the state-kick template.

Decision:

- If price-jump or liquidity-drop works: Paper A can claim driven-transient market dynamics, not just
  latent-state mechanics.
- If only state_kick works: keep NCS as unlikely; target NeurIPS/ICML and scope as simulator physics.

### Gate 2: real-data pilot

NCS does not require the full Paper B physics program, but Paper A needs a real-world anchor if the
title says "financial markets" rather than "market simulators."

Required minimum:

- one or two real crash/stress windows with windowed alpha dip-and-recover;
- matched calm control windows;
- honest failure cases if the signature is absent or noisy.

Decision:

- If real data shows the same qualitative transient: NCS becomes credible.
- If real data is inconclusive: Paper A remains a strong methods/simulator-physics paper, but should
  not be sold as a market-discovery paper.

### Gate 3: computational framework clarity

The paper must foreground the reusable computational method:

- differentiable particle simulator;
- raw pre-impact excess-demand logging;
- shock schedules and controlled counterfactual protocols;
- windowed non-equilibrium diagnostics;
- warmup/stationarity hygiene;
- gradient calibration and agent-level force decomposition.

If these are scattered as implementation details, the paper reads like a finance/ML benchmark. If
they are presented as the framework, the paper reads like computational science.

## Recommended Paper A structure for NCS

1. **Problem:** market fat-tail and volatility dynamics are usually measured passively; real markets
   cannot be experimentally shocked under controlled conditions.
2. **Framework:** EcoMD, a calibrated differentiable particle simulator for controlled
   non-equilibrium market experiments.
3. **Measurement correction:** warmup-inclusive scoring confounds transient and stationary tails;
   the previous stationary cube-law solve was a burn-in artifact.
4. **Controlled discovery:** steady state is light-tailed; shocks revive heavy tails; the transient
   relaxes on a finite timescale.
5. **Robustness:** dose response, five assets, asset-dependent thresholds, and realistic shock
   channels.
6. **Real-data pilot:** real crash windows show whether the same alpha dip-and-recover is visible
   outside the simulator.
7. **Handoff:** EcoMD provides the calibrated differentiable substrate for Paper B's real-market
   thermodynamic protocols.

## Title options

Conservative / methods-safe:

> EcoMD: A Calibrated Differentiable Particle Simulator for Non-Equilibrium Market Dynamics

NCS stretch, simulator-scoped:

> A Differentiable Particle Simulator Reveals Driven-Transient Heavy Tails in Market Dynamics

NCS stretch, stronger real-market framing:

> Controlled Computational Experiments Reveal Driven-Transient Heavy Tails in Financial Markets

Use the third only if Stage 2b and the real-data pilot are clean.

## Practical next steps

1. **Stage 2b:** implement and run price-jump / liquidity-drop shock channels.
2. **Stage 2d:** fit relaxation time `tau` from existing exp 123 windows by dose and asset.
3. **Verdict hygiene:** reconcile the `verdict_spx.json` P* / `H2=false` strict-monotonicity record
   with the Stage 1.5 claim that the dose-response is resolved.
4. **Stage 3 pilot:** run windowed alpha on at least two real stress episodes plus calm controls.
5. **Rewrite Paper A outline:** replace the stale "7/11 calibrated tool" and "stationary concave
   solve" spine with the controlled non-equilibrium experiment spine.

## Bottom line

Aim the writing at NCS quality now, but do not commit to NCS submission until Stage 2b and the
real-data pilot are in hand. If those pass, Paper A is a plausible Nature Computational Science
submission. If they do not, the same manuscript remains a strong NeurIPS/ICML methods and
simulator-physics paper, while Paper B retains the Nature Physics ambition.
