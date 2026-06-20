# Workshop spine — Generative AI in Finance (NeurIPS, non-archival, 4pp)

**Angle:** the *generative-modeling methodology* — EcoMD as a differentiable, controllable scenario
generator, a warmup-scoring pitfall in how such generators are evaluated, and honest fidelity bounds.
(Sibling paper [ml4ps_spine.md] leads with the non-equilibrium *physics* — keep distinct.)

## Title options
1. **EcoMD: A Differentiable Generative Market Simulator — and a Burn-In Pitfall in Scoring It**
2. Controllable Stress Scenarios from a Differentiable Market Simulator (and How Not to Score Them)
3. Evaluating Generative Market Simulators: A Warmup Artifact in Stylized-Fact Matching

## Abstract (draft)
Generative simulators of markets are used for scenario generation and stress testing, and are scored
by how well their rollouts match stylized facts (fat tails, clustering). We present **EcoMD**, a
**differentiable** particle simulator whose differentiability enables gradient calibration and
**controllable shock interventions**, and we report a **measurement pitfall in how such generators are
evaluated**: standard rollout scoring **without a warmup discard** misreads a startup *equilibration
transient* as a stationary fat-tail match — inflating the apparent tail fidelity (Hill 3.9→6.6 once
warmup is discarded). We give the corrected protocol. Using the shock interface, we show EcoMD
generates **coherent-liquidation stress scenarios** with a distinctive order-flow signature (flow
memory 0.02→0.99 at the shock, relaxing), whereas exogenous price gaps are inert — a controllability
result. Finally we bound fidelity honestly: the model's heavy tails are *transient*, while real
1-minute crypto crash tails are *stationary* (pre-registered null test, 5 episodes) — a caveat for
anyone using such simulators for tail realism.

## Contributions (this paper)
- **C1.** **EcoMD**, a differentiable generative market simulator with a **controllable shock
  interface** for scenario generation / stress testing.
- **C2.** A **generative-model evaluation pitfall + fix**: warmup-inclusive stylized-fact scoring
  inflates fat-tail fidelity (a burn-in transient read as stationary); we give a corrected,
  warmup-discarded protocol and a sensitivity check.
- **C3.** **Controllability + honest fidelity bounds**: coherent-liquidation shocks produce a
  distinctive, relaxing order-flow scenario; price gaps are inert; and generated tails are transient
  while real tails are stationary (a scenario-realism caveat).

## Section spine (4 pages)

**1. Introduction / problem (½p).** Generative market simulators for scenario generation + stress
testing (Cont 2001 stylized facts; ABM sims e.g. ABIDES, Chopra 2022). Two practical questions: how do
we *evaluate* them (stylized-fact matching), and how *controllable* are the scenarios? Flag that
evaluation rigor is under-examined.

**2. EcoMD: a differentiable generative simulator (½p) — Fig 1.** Particle/Langevin generator; sample
paths + the stylized facts it produces. **Differentiability** → gradient calibration + a **shock
interface** (controllable interventions). *Honest prior-art:* differentiable ABMs exist (Dyer/
Quera-Bofarull 2023–25; Bouchaud-Cont 1998) — contribution is the controllable-scenario + evaluation
findings, not "first." 

**3. The evaluation pitfall (1p) — Fig 2.** *The headline methodology result.* Standard practice scores
the **full rollout** (no warmup discard). A startup *equilibration transient* produces a heavy tail
that the scorer reads as a stationary fat-tail *match* — but it's burn-in: dropping warmup moves Hill
3.9→6.6 (baseline) / 5.0→9.3 (a tuned variant), i.e. the steady state is light. So reported tail
fidelity can be **inflated by an evaluation artifact**. Fix: warmup-discarded scoring + a reported
warmup-sensitivity curve. Low-variance across seeds makes it look robust — it isn't. → *evidence:*
`r1_warmup_report.json`, `burnin_artifact_finding_2026-06-18.md`.

**4. Controllable scenarios (½p) — Fig 3a.** The shock interface generates stress scenarios. A
**coherent-liquidation** shock (`state_kick`, a fraction of agents repositioning together — a panic/
forced-selling analogue) yields a distinctive **order-flow signature**: imbalance memory 0.02→0.99 at
the shock, **relaxing over ~1k steps**; with a graded dose-response across 5 assets. An exogenous
**price gap** is **inert** (no order-flow or tail response) — a controllability finding about which
interventions actually drive the generator. → *evidence:* `ofi_transient_spx.json`,
`verdict_spx_jump.json`, exp 123 Stage 1.5/2a.

**5. Honest fidelity bounds (½p) — Fig 3b.** For scenario *realism*: the model's heavy tails are
**transient**, but real 1-minute crypto crash tails are **stationary** (pre-registered null test over
5 crashes; pooled Δα z=+1.03). So generated tails reproduce a *driven* heavy tail, not the real
*stationary* cube-law — a caveat for using such simulators as realistic tail generators. → *evidence:*
`stage3_realdata_pilot_2026-06-19.md`, `null_test_crash_tails.py`.

**6. Discussion (¼p).** Practical takeaways for the GenAI-in-finance community: (i) discard warmup when
scoring rollout-based generators; (ii) controllability is intervention-specific; (iii) tail fidelity is
transient — validate against real stationarity before trusting scenario tails.

## Figures (≤3)
- **Fig 1:** EcoMD sample paths + stylized-fact panel (what it generates) + the shock-interface schematic.
- **Fig 2:** the evaluation pitfall — scored tail fidelity with vs without warmup discard.
- **Fig 3:** (a) controllable stress scenario (OFI signature, state_kick vs inert price-gap); (b) the
  transient-vs-stationary real-data fidelity caveat.

## Distinctness vs the ML4PS sibling
This paper's *contribution* is the **generative-modeling methodology**: the simulator-as-generator +
the **evaluation pitfall** (§3, the headline) + controllability + fidelity bounds. The sibling's
contribution is the **physics** of the transient (relaxation, the non-eq mechanism, the stationarity
boundary). Here the burn-in finding is framed as an **evaluation-hygiene** point for generative
benchmarks (not a non-equilibrium-physics point), the shocks as **scenario controls** (not a physics
probe), and the audience/venue differ. Lead with §3 (evaluation) + §4 (controllable scenarios).

## Claims discipline (checklist)
- [ ] Every empirical claim cites an exp-123 artifact (above).
- [ ] No "first differentiable market sim" (cite Bouchaud-Cont 1998, Dyer 2023–25).
- [ ] Frame the burn-in finding as *generative-model evaluation hygiene*, not non-eq physics (that's the sibling).
- [ ] Cite Cont 2001, Chopra 2022 / ABIDES, Gabaix, Dyer 2023–25.
- [ ] Non-archival workshop; if also submitting the ML4PS sibling at the same NeurIPS, ensure genuine
      distinctness (different headline contribution) and consider emailing organizers.
