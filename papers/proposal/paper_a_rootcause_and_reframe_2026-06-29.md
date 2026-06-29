# Paper A — root-cause analysis of the "negative" results, and the positive reframe

**Date:** 2026-06-29. **Author:** research-partner / reviewer-2 pass at the user's request:
(1) treat *building EcoMD* as a positive result; (2) diagnose the root cause of each negative —
fix if fixable, de-emphasize if not; (3) decide whether any negative is *fundamental* (from
principle or from data). Grounded in the code (cited file:line) and the prior experiment record
(`.claude/memory/`, `logs/`). Operationalized by the pre-registered experiment suite
`experiments/125_rootcause_controllability/`.

---

## 0. The reframe in one line

EcoMD's headline is **not** "we reproduce fat tails." It is: **a differentiable, controllable,
equivariant molecular-dynamics market laboratory in which we can switch the heavy tail on and off by
driving the system — and thereby show, interventionally, *why* a stationary fat tail is hard to get
endogenously.** The light steady state is the *evidence for that mechanism*, not a failure to be
hidden. Everything below supports that reframe and keeps it honest.

---

## 1. The four "negative" results, named

- **N1 (central).** The *steady-state* excess-demand / return tail is **light** (Hill α ≈ 4.7), not
  the empirical cube law (α ≈ 3). Heavy tails appear only as a **driven transient**. (The earlier
  "stationary cube-law solve" was a burn-in artifact — `project_burnin_artifact.md`.)
- **N2.** Real one-minute crypto crash *return* tails do **not** heavy-up (pooled z = +1.03); the
  driven transient is simulator-specific across returns.
- **N3.** The sign-level entropy-production proxy is **flat** at the shock (E-S3): the signature is
  order-flow *coherence/persistence*, not irreversibility.
- **N4.** The **Pareto ceiling**: no single configuration matches all 11 stylized facts at once;
  fattening the tail breaks volatility clustering / leverage and vice versa (tails XOR dynamics —
  `project_pareto_ceiling.md`, `project_neural_sde_tournament.md`).

N1 is the load-bearing one; N2/N3 are scope, N4 is the structural tradeoff. I diagnose N1 fully and
treat the rest in its light.

---

## 2. Why is the steady state light? Three first-principles reasons

**(P1) Boltzmann tail of a smooth potential.** Overdamped Langevin with additive finite-variance
noise and a smooth confining potential has the stationary density *p(s) ∝ exp(−U(s)/T)*. A power-law
marginal needs *U(s) ∼ c·log|s|* at large |s|; a learned MACE-lite/MLP potential grows
super-logarithmically (it confines), so the single-agent marginal is (sub-)exponential — **light by
construction**. You do not get a power law from a generic smooth potential in a Gaussian bath.

**(P2) Central-limit self-averaging of the aggregate — the dominant effect.** The price is driven by
*ED_t = κ Σ_{i=1}^N Δs_{i,0}* (`price_formation.py:344`), a sum over *N ≈ 10⁴* agents. If the agent
increments have finite variance and a finite correlation length *ξ*, the CLT applies to the sum (with
an effective block count ∝ *N/ξ^d*): **ED → Gaussian, α_ED → ∞ (light), and the larger N the
stronger the pull.** This is generic — *any* large, weakly-coupled finite-variance particle market
self-averages to a light aggregate tail. Note α is scale-invariant, so the `ed_normalize` √N option
(`price_formation.py:152,345`) changes ED's *scale* but not this tail conclusion.

**(P3) Sub-critical coupling.** (P2) fails only if *ξ* diverges (criticality), so a few
system-spanning coordinated clusters dominate the sum and it stops self-averaging → heavy aggregate.
The **trained model sits away from such a point**: exp 116/120 found *hill(N)* is a *smooth
crossover* with **no sharp N_c and no finite-size sharpening** (`project_neural_sde_tournament.md`).
So the learned dynamics are sub-critical → self-averaging holds → light.

**Synthesis (the principled statement, and the paper's thesis).** *In a finite-variance, sub-critical,
large-N Langevin market the stationary aggregate tail is light by the central limit theorem. A heavy
stationary tail requires either (a) a heavy microscopic source (infinite-variance agent noise) or
(b) persistent system-spanning coordination (near-critical, or externally driven).* EcoMD's heavy
tail is a **driven transient** precisely because a coherent-displacement shock imposes (b)
**transiently**; when it relaxes, the CLT reasserts and the tail goes light again. This is the
mechanism, demonstrated by intervention — something pure observation of real markets cannot do — and
it takes the *dynamics-generated* side (Clark 1973; LeBaron 2001) against the *stationary-equilibrium-law*
side (Gabaix 2003) **for this model class**.

---

## 3. Is N1 fixable? The three routes, and what we already know

| Route | mechanism | in code? | status / evidence | verdict |
|---|---|---|---|---|
| **A. Heavy micro-noise** | α-stable / Student-t agent innovations; stable laws closed under summation ⇒ α-stable ED ⇒ stationary power law | **yes** — `noise_dist ∈ {normal,t,levy}`, `noise_levy_alpha`, CMS sampler (`integrator.py:101,177,313`; `ecomd.py:76`) | partially probed (exp 108 "Student-t/Lévy overshoot"); tournament: transient overshoot is *dynamical not distributional* (Gaussian+0 jumps still overshoots). Whether Lévy gives a clean **stationary** cube-law, and at what cost to other facts, was **never cleanly isolated** | **fixable but the index is put in by hand**, and almost certainly trades against clustering/leverage (N4). Decisive ablation = **G-D1** below |
| **B. Multiplicative noise / SV / subordination** | finite-variance innovations, fat tail via a fluctuating vol clock (Clark/LeBaron) | **yes** — `sv_integrator_enabled`, `sv_integrator_gain` (`ecomd.py:318,909`), Hawkes χ_t, leverage-γ coupling (`ecomd.py:88`) | **explored, hit the ceiling**: exp 119 SV 4.90<5.96; MoE stuck hill≈1.36; diffusion gets tail in-band but kills clustering (acf²=0.09) | **not cleanly solvable** without breaking dynamics — this *is* the Pareto frontier |
| **C. Near-critical endogenous coordination** | tune coupling so ξ diverges → heavy aggregate with no drive | partially (pair-potential strength) | **explored, no sharp criticality**: exp 116/120 smooth crossover, no N_c; train-at-N is T-confounded | **not achieved**; forcing criticality unproven |

**Conclusion on solvability.** N1 is **partly fixable but at a known, structural cost.** Route A can
*install* a stationary heavy tail, but (i) the exponent is hand-set (not emergent) and (ii) the
evidence says it sacrifices volatility clustering / leverage — i.e. you can buy a heavy stationary
marginal **or** clean temporal dynamics, **not both at once.** That tradeoff *is* the deep finding, so
"solving" N1 by Route A does not remove the result — it *sharpens* it into the Pareto-frontier claim.

---

## 4. Is anything *fundamental*? Yes — and naming it is the contribution

**Fundamental from principle (model class):**
1. **CLT self-averaging** (§2 P2) — a large-N finite-variance sub-critical aggregate is light-tailed.
   This is a theorem-level limit, not a tuning miss. → directly testable as **steady-state α_ED vs N**
   (G-D2): the tail should get *lighter* as N grows, at *fixed trained dynamics*.
2. **Smooth-potential Boltzmann light tail** (§2 P1).
3. **Tails-XOR-dynamics Pareto frontier** (N4) — the marginal-fattening mechanisms (heavy noise,
   strong/concave impact) overwrite the temporal structure that produces clustering, and vice versa.

**Fundamental from data:**
1. **The calibration target cannot pin the tail.** The objective *L = Σ_k w_k (g_k(r) − g_k\*)²*
   (`losses.py`) carries the tail as **one weakly-weighted, high-variance soft-Hill term** among 11
   facts; on warm-up-discarded finite returns the optimizer has little gradient to install a precise
   α ≈ 3 and a strong incentive to spend that capacity on easier facts. (Consistent with the burn-in
   artifact: the apparent "solve" came from burn-in, not from the loss.)
2. **N2 is a property of the *data*, not of EcoMD.** Real return tails are stationary cube-law (heavy
   in calm *and* crash). The real market **already carries the always-on heavy source EcoMD lacks**;
   crashes do not switch it on. So the driven-transient picture is not *supposed* to transfer to real
   *returns* — N2 is the predicted boundary, and it points to where a transient *could* live
   (order flow), i.e. the Paper-A→NCS / Paper-B handoff. Not a defect.
3. **Data-budget limit, not fundamental:** N2's test is low-power (5 free-crypto episodes).

---

## 5. What to do with each negative (the user's directive applied)

- **N1 — keep, but reframe as the mechanism (positive).** State the CLT/self-averaging principle,
  *prove the missing ingredient interventionally* (G-D1 Lévy installs a stationary heavy tail; G-D2
  α_ED↑ with N), and present the light steady state as *evidence*. This converts the central negative
  into the paper's main mechanistic result. **De-emphasize the word "fails"; lead with "we explain."**
- **N2 — demote to a one-paragraph scope note.** Honest, brief, framed as the *predicted* boundary
  (real markets carry the stationary source the model lacks) + the order-flow handoff. Not a section
  headline. Stays in (per `feedback_no_downgrade`), but small — exactly what the user asked.
- **N3 — one sentence**, as the Paper-A/Paper-B carve-out (coherence = Paper A; entropy production =
  Paper B). Already minimal.
- **N4 — present as a *positive* structural result** (a measured Pareto frontier of a model class),
  not a defeat. It is already framed this way in `project_pareto_ceiling.md`.

**GenAI-in-Finance paper specifically:** lead with (i) EcoMD as a controllable generator and (ii) the
controllability atlas (G-B) + the warm-up evaluation protocol; carry the tail story as the
mechanistic "know your generator's tail" result (G-D); N2 becomes a single validation caveat. The
balance shifts decisively positive without hiding anything.

---

## 6. The honest-framing guardrail

"Report more positive results" is achieved by (a) the EcoMD-as-platform contribution, (b) the
*mechanistic* reframe of N1, and (c) **new pre-registered experiments designed to yield positive
mechanism content** — not by deletion or spin. The guardrail against gate-shopping is the binding
pre-registration `experiments/125_rootcause_controllability/PREREG.md`, which freezes the predictions
and the decision rules **before** the runs, and commits to reporting every arm. Both outcomes of each
ablation are written as positive content in advance (e.g. "Lévy installs a stationary tail at a
clustering cost" *or* "even Lévy cannot, tightening the structural limit"). This satisfies
`feedback_no_downgrade` and the user's request simultaneously.

---

## 7. Bottom line

- The light steady state is **fundamental** (CLT self-averaging + smooth-potential Boltzmann tail),
  not a bug. We can *name it, prove it by intervention, and show the exact missing ingredient.*
- It is **"fixable" only by changing the model class** (heavy noise / criticality), and doing so
  **costs the temporal stylized facts** — which is itself the Pareto-frontier result.
- N2 is a **data fact** (real tails carry a stationary source), the predicted boundary, not a model
  defect.
- Therefore the strongest *and* most honest paper leads with **EcoMD-the-laboratory + the
  interventional mechanism of fat tails**, demotes N2/N3 to scope, and presents N1/N4 as positive
  mechanistic/structural findings. Experiments to lock this in: `experiments/125_*` (G-D the
  root-cause ablations are the new core; G-A/B/C the rigor + controllability + relaxation-law).
