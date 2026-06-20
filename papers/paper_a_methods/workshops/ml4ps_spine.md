# Workshop spine — ML & the Physical Sciences (NeurIPS, non-archival, 4pp)

**Angle:** the *physics* — heavy tails as a non-equilibrium driven transient in a Langevin particle
market simulator, its relaxation, and the honest real-data stationarity boundary. (Sibling paper
[genai_finance_spine.md] leads with the generative-modeling/evaluation angle — keep distinct.)

## Title options
1. **Heavy Tails as a Non-Equilibrium Transient in a Differentiable Particle Market Simulator**
2. Driven Transients, Not Stationary Laws: Fat Tails in a Langevin Market Simulator
3. A Non-Equilibrium Stationarity Pitfall in Simulated Market Fat Tails

## Abstract (draft)
Fat-tailed returns are usually treated as a *stationary* property (the inverse-cubic law, Gabaix et
al.). We study their origin in **EcoMD**, a differentiable Langevin particle simulator of a market,
and find the opposite: the **steady state is light-tailed** (Hill α≈4.7), and heavy, cube-law-and-
beyond tails (α→0.5) appear **only transiently** when the system is driven out of equilibrium — at
initialization or by a controlled shock — and **relax on a finite timescale** (τ≈240 steps). This
makes warmup-inclusive rollout scoring **misread the equilibration transient as a stationary law**.
The transient is specific to *coherent agent-state displacement* (it does not appear under an
exogenous price shock, in either the return tail or order-flow imbalance), and it leaves a clean
non-equilibrium order-flow signature (lag-1 flow memory 0.02→0.99 at the shock, relaxing). On real
1-minute crypto crashes, by contrast, the return tail is **stationary** across calm and crash (a
pre-registered null test over 5 episodes). The simulator's heavy tail is thus a **non-equilibrium
phenomenon of the model**, not a stationary market law — localizing a missing stationary heavy-tail
mechanism in this class of simulators.

## Contributions (this paper)
- **C1.** In a Langevin market simulator, heavy tails are a **driven non-equilibrium transient**
  (light steady state → shock → α→0.5 → relax, τ≈240), characterized over 5 assets with a sigmoid
  dose-response.
- **C2.** A **non-equilibrium measurement pitfall**: warmup-inclusive scoring confounds the
  equilibration transient with a stationary tail (the prior cube-law "match" was burn-in inflation).
- **C3.** **Mechanistic specificity + an honest boundary**: the transient needs coherent latent
  displacement (inert to exogenous price gaps, on tail *and* order flow); and real return tails are
  stationary (pre-registered null test) — so the effect is a simulator property.

## Section spine (4 pages)

**1. Introduction / problem (½p).** Inverse-cubic tail as a stationary universal law (Gabaix; Cont
2001). Question: in a *mechanistic* particle simulator, is the fat tail stationary or a non-eq
transient — and does naive scoring tell them apart? Frame as non-equilibrium statistical mechanics of
a driven system.

**2. EcoMD as a Langevin particle market (½p).** Agents = particles in latent space; overdamped
Langevin dynamics with learned interaction potentials (MACE-lite, Batatia 2022); price via excess
demand. *Honest prior-art:* differentiable / Langevin market models exist (Bouchaud-Cont 1998;
Dyer/Quera-Bofarull 2023–25) — we do **not** claim first; the contribution is the non-equilibrium
finding. Pre-impact excess demand = the order-flow quantity; raw-ED logging.

**3. Heavy tails are a driven transient (1p) — Fig 1.** Control: steady-state α_ED≈4.7, flat. A
controlled `state_kick` at t=T drives α_ED→0.5 (heavier than cube) and it **relaxes to ≈4.7 within
~1k steps**. Same depth as the t=0 equilibration template ⇒ burn-in *is* this transient. Generalizes
5/5 assets; **sigmoid dose-response** (onset ~0.1–0.2, saturated floor ~0.5). Relaxation timescale τ
(exp fit): burn-in τ≈20, deep-shock τ≈240 (≈10× slower). → *evidence:* exp 123 Stage 1/1.5/2a/2d.

**4. The measurement pitfall (½p) — Fig 2.** Standard Hill on the full rollout (no warmup discard)
inflates the tail: baseline 3.9→6.6, concave 5.0→9.3 under warmup discard (R1). So the prior
"stationary cube-law solve" was burn-in inflation. Lesson: **report warmup sensitivity**; steady-state
tails are light. → *evidence:* `r1_warmup_report.json`, `burnin_artifact_finding_2026-06-18.md`.

**5. Mechanism + non-equilibrium order-flow signature (½p) — Fig 3a.** The transient needs *coherent
latent displacement*: an exogenous price gap (`price_jump`) is **inert** — α_ED flat ~4.6, α_ret stays
light, and order-flow imbalance is identical to control. Under `state_kick`, order flow shows a clean
non-eq signature: lag-1 flow memory 0.02→**0.99** at the shock (perfect transient persistence),
relaxing. → *evidence:* `verdict_spx_jump.json`, `ofi_transient_spx.json`.

**6. The real-data boundary (½p) — Fig 3b.** Pre-registered null test on 5 real 1-min crypto crashes
(COVID-2020, China-2021, Celsius-2022, Luna, FTX): Δα(crash−pre) pooled z=+1.03 vs a calm null
(0.02±0.43) — real return tails are **stationary** cube-law in calm and crash (Gabaix-Plerou-Stanley).
⇒ the simulator's transient is a model property; it localizes a missing **stationary heavy-tail
mechanism**. → *evidence:* `stage3_realdata_pilot_2026-06-19.md`, `null_test_crash_tails.py`.

**7. Discussion (¼p).** Non-equilibrium framing + stationarity-hygiene for ABM/market-sim measurement;
the order-flow non-eq signature (cf. Maskawa 2025 fluctuation theorems) as the bridge to real-data
follow-up.

## Figures (≤3)
- **Fig 1:** α_ED(t) control vs shocked (dip-and-recover) + dose-response sigmoid inset + τ.
- **Fig 2:** Hill with vs without warmup discard (the inflation).
- **Fig 3:** (a) OFI memory burst-and-relax (state_kick) vs inert (price_jump); (b) real-crash null test.

## Distinctness vs the GenAI-in-Finance sibling
This paper's *contribution* is the **physics** (non-eq transient + relaxation + the stationarity
boundary + the order-flow non-eq signature). The sibling's contribution is the **generative-model
methodology** (controllable scenario generation + the evaluation-hygiene pitfall + fidelity bounds).
Shared evidence, different headline claim, different audience. Keep §3 (physics of the transient)
and §5–6 (non-eq order flow + boundary) as the load-bearing content here; the eval pitfall is a
*supporting* point (§4), not the headline.

## Claims discipline (checklist)
- [ ] Every empirical claim cites an exp-123 artifact (above).
- [ ] No "first differentiable market sim" (cite Bouchaud-Cont 1998, Dyer 2023–25).
- [ ] No "real markets are non-equilibrium-transient" — §6 explicitly says the *opposite* (stationary).
- [ ] Cite Cont 2001, Gabaix, Tóth-Lux-Sornette 2018, Maskawa 2025, Batatia 2022.
- [ ] Non-archival workshop → fine to submit alongside the full paper; confirm the year's CFP.
