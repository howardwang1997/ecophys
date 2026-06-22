# Controlled Computational Experiments on Non-Equilibrium Market Dynamics with a Differentiable Particle Simulator

*Long-form draft for **Nature Computational Science** (Paper A → NCS route). Markdown working draft.
Strategy: `papers/proposal/paper_a_dual_track_plan_2026-06-19.md`; experiment plan + pre-registration:
`experiments/124_order_flow_transient/{DESIGN,PREREG_phase2}.md`. **§7.2 (real-market order-flow
results) is intentionally BLANK** — pending the Tardis L2 buy; all other sections are complete.*

> **Status note (remove before submission).** This draft is complete except the load-bearing
> **Phase-2 real-market result (§7.2)**, which decides the paper's central market claim and hence its
> venue. The framing, abstract, and discussion are written conditionally so the Phase-2 outcome slots
> in against the **pre-registered gates** (G-main / G-null) without any post-hoc reframing.

---

## Abstract

Heavy-tailed returns and other "stylized facts" of markets are almost always studied **passively** —
estimated from observational data and treated as **stationary** properties — because real markets
cannot be experimentally shocked under controlled conditions. We introduce **EcoMD**, a calibrated,
**differentiable** particle simulator of a market (agents are particles under overdamped Langevin
dynamics with learned interactions; the price forms from aggregate excess demand), and use it as a
**controlled-experiment platform**: its differentiability supports gradient calibration, scheduled
interventions, and exact mechanism attribution that observational study and non-differentiable
agent-based models cannot. With it we (i) identify and correct a **measurement artifact** — scoring
rollouts without a warm-up discard misreads a startup *equilibration transient* as a stationary
fat-tail law; (ii) show, by controlled intervention, that in EcoMD heavy tails are a **driven
non-equilibrium transient** (light steady state, *α≈4.7*; shock-driven heavy tail, *α→0.5*; finite
relaxation, *τ≈240* steps; sigmoid dose-response across five assets); (iii) localize the **mechanism** —
only coherent latent displacement drives it, exogenous price shocks are inert, and it leaves a sharp,
dose-responsive **order-flow-coherence** signature; and (iv) establish the **boundary**: real return
tails are *stationary* across calm and crash (pre-registered null test, five episodes), so the
transient is a property of this model class, pinpointing a missing stationary heavy-tail mechanism. The
simulator turns this boundary into a **falsifiable real-market prediction**: the non-equilibrium
signature absent from real *returns* should appear in real *order flow*. **[§7.2 — pending: the
pre-registered test of this prediction on real limit-order-book data; outcome and figure to be filled.]**

## 1. Introduction

Two facts sit uneasily together. First, the heavy (inverse-cubic) tail of returns and the clustering of
volatility are among the most reproducible empirical regularities in finance [Cont 2001; Gabaix et al.
2003; Plerou et al. 1999], and are routinely treated as **stationary** properties of the return
process. Second, markets are manifestly **driven, open, non-equilibrium** systems — order arrives,
liquidity is consumed and replenished, participants react — yet we almost never get to ask *causal*,
interventional questions about them, because we cannot shock a real market under controlled conditions
and watch it relax.

A *mechanistic, differentiable simulator* changes what questions are askable. If agents are particles
in a Langevin many-body system whose macroscopic observable is the price, then "steady state,"
"relaxation time," and "driven transient" become precise, measurable dynamical statements, and
differentiability adds gradient calibration and exact attribution. We use such a simulator, **EcoMD**,
not to argue it is novel as an object — differentiable agent-based market models exist [Bouchaud & Cont
1998; Dyer et al. 2024; Chopra et al. 2023] — but as a **controlled-experiment platform** to answer a
question observational study cannot: *is the heavy tail a stationary law or a non-equilibrium transient,
and does that distinction survive contact with real data?*

Our contributions:

1. **A measurement correction (§3).** Warm-up-inclusive rollout scoring confounds a startup
   equilibration transient with a stationary tail; we give the corrected protocol. This is a hygiene
   result for the entire rollout-scored ABM / generative-market-model literature.
2. **A controlled discovery (§4).** By scheduled intervention, heavy tails in EcoMD are a **driven
   non-equilibrium transient** — light steady state, shock-driven heavy tail, finite-time relaxation,
   sigmoid dose-response, five assets.
3. **Mechanism attribution (§5).** Only coherent agent-state displacement drives the transient;
   exogenous price shocks are inert; the transient leaves a sharp, dose-responsive order-flow-coherence
   signature.
4. **A boundary and a prediction (§6–§7).** Real *return* tails are stationary (the controlled
   transient is model-specific), which converts into a falsifiable prediction about real *order flow* —
   **tested in §7.2 [pending]**.

## 2. The EcoMD computational framework

**Dynamics.** EcoMD evolves *N* agents *sᵢ ∈ ℝᵈ* by overdamped Langevin dynamics,
*ṡᵢ = −∇U({s}) + √(2T) ξᵢ*, with a learned equivariant interaction potential *U* (a message-passing
form in the spirit of MACE [Batatia et al. 2022]) and temperature *T*. The log-price increment is
*Δpₜ = β·EDₜ + σηₜ*, where the pre-impact excess demand *EDₜ = κ Σᵢ Δsᵢ,₀* is the net signed agent
flow. Calibration is by gradient descent against a panel of stylized facts.

**Why differentiability matters here.** Three capabilities distinguish EcoMD from observational study
and from non-differentiable agent-based simulators [Byrd et al. 2020, ABIDES] and make the controlled
experiments below possible:

- *Scheduled interventions.* A shock interface injects a controlled perturbation mid-rollout — a
  coherent latent displacement, an exogenous price gap, a liquidity change — driving the system out of
  its steady state on demand and letting us watch it relax. This is the experimental knob real markets
  lack.
- *Exact observables.* The simulator exposes the pre-impact excess demand and the per-step order-flow
  imbalance directly, so non-equilibrium diagnostics (windowed tail index, order-flow memory,
  relaxation time) are measured on the generating quantity, not inferred.
- *Gradient attribution.* Differentiability supports calibration and mechanism attribution
  (which interactions produce which fact) that black-box simulators cannot provide.

We use these as a **methodology**: pose a causal question about market dynamics, answer it by controlled
intervention in the simulator, and then test the resulting prediction against real data.

## 3. A measurement correction: warm-up confounds transient and stationary tails

A central, transferable finding concerns how rollout-based market models are *evaluated*. The fat-tail
fact is the Hill tail index *α* of returns [Hill 1975]; standard practice computes it on the **entire**
rollout. But a fresh rollout is out of equilibrium and relaxes to its steady state over an initial
transient during which the aggregate flow is heavy-tailed. A warm-up-inclusive estimate therefore reads
this startup transient as a stationary heavy tail.

Discarding the first ~50 steps moves the estimate sharply toward the light steady state (Table 1, Figure
1): the baseline Hill index rises 3.87 → 6.55, and a concave-impact variant previously tuned to "match"
the cube law rises 5.05 → 9.26. The steady state is **light**-tailed (*α≈4.7* for excess demand); the
apparent fat-tail match was burn-in inflation. The artifact is *rewarded, not caught*: the
warm-up-inclusive (heavier) reading sits closer to the empirical cube-law target than the true light
steady state, so a stylized-fact scorer registers a *better* match; its low cross-seed variance
reinforces the illusion of a robust law.

**Corrected protocol.** (i) Compute each stylized fact over a sliding window and plot it against
warm-up-discard length *W*; (ii) discard to the plateau *W\**; (iii) report the score at *W\** with the
sensitivity curve, flagging any fact that shifts by more than a tolerance over [0,*W\**] as
transient-contaminated. We recommend this as default hygiene for rollout-scored market models.

**Table 1.** Hill tail index with vs. without a warm-up discard (EcoMD, *T*=8000; higher = lighter).

| model | no discard | discard 50 | Δ |
|---|---|---|---|
| baseline | 3.87 | 6.55 | +2.68 |
| concave-impact (tuned to "solve") | 5.05 | 9.26 | +4.21 |

## 4. Controlled discovery: heavy tails are a driven transient

We now use the intervention knob. In the unperturbed steady state the order-flow tail is light
(*α_ED≈4.7*, flat). We apply a controlled **coherent displacement** (a `state_kick`: a fraction of
agents displaced together) at *t=3000*. The tail **craters to *α_ED≈0.5*** — heavier than the cube law —
and **relaxes back to ≈4.7 within ~10³ steps** (Figure 2, left). The depth matches the *t=0*
equilibration template: the initial burn-in (§3) *is* this same transient. An exponential fit gives a
relaxation time *τ≈240* steps (vs. *τ≈20* for the faster cold-start).

The effect is systematic. Across **five assets** (equities, NASDAQ, gold, crypto, FX) the post-shock
tail follows a **monotonic sigmoid dose-response** in shock magnitude (onset ~0.1–0.2σ, saturating to a
floor *α≈0.5*; Figure 2, right), with an **asset-dependent threshold** that tracks intrinsic volatility
(the low-volatility FX pair needs a larger shock). None of this is imposed by the perturbation: the
steady state being *light* (the opposite of real markets), the finite relaxation time, the graded
dose-response, and the mechanism-specificity of §5 are emergent properties of the trained dynamics. In
EcoMD, the heavy tail is a property of the *driven*, not the steady, state.

![Driven transient + sigmoid dose-response](figures/fig1_transient.png)

**Figure 2.** (left) order-flow tail *α_ED(t)*: control stays light (≈4.7); a coherent shock at *t=3000*
craters it to ≈0.5 and it relaxes back (*τ≈240*); the *t=0* burn-in dip is the same transient. (right)
the sigmoid dose-response — post-shock minimum *α_ED* vs. shock magnitude.

## 5. Mechanism and channels: what drives the transient

**Only coherent latent displacement.** An exogenous price shock (injecting a return into the price — a
news-shock analogue) is **inert**: across magnitudes up to 12σ the excess-demand tail stays light
(*α_ED≈4.6*), the return tail only nudges (~7.7 → 6.0, still far from heavy), and the order-flow
imbalance is statistically identical to control. A price gap does not propagate into a coordinated
order-flow response. The transient is specific to perturbing the *agents'* coordination, not the
*observable price* — consistent with reading a crash as coordinated liquidation rather than an exogenous
price move.

**The order-flow signature.** Under the coherent shock, order flow shows a sharp, quantitatively
characterized signature (Figure 3a): the lag-1 autocorrelation of order-flow imbalance (OFI) jumps from
~0.02 to ~1.0 at the shock — flow becomes transiently coherent and persistent — and relaxes back. It has
a **clean monotonic sigmoid dose-response** (onset ~0.1–0.2σ → ~1.0 by ~1σ; a sharper observable than
the tail), **generalizes across four of five assets** (the low-vol FX pair sub-threshold, tracking its
volatility), and relaxes on a **sharp timescale *τ_OFI≈22* steps — ~10× faster than the return-tail
*τ_ED≈236***. The system thus exhibits *two* non-equilibrium timescales: a near-instantaneous
order-flow-coherence impulse and a slower tail relaxation.

**On entropy production (honest).** We computed a sign-level entropy-production proxy on the joint
*(Δp, OFI)* process — the KL divergence between forward and time-reversed pair-transition statistics —
and it was **flat**. The signature is order-flow *persistence/coherence*, not sign-level
*irreversibility* (a persistent, AR-like process can be time-reversible). A finer entropy-production
treatment connects to non-equilibrium stochastic thermodynamics [Seifert 2012] and fluctuation-theorem
studies of market cascades [Maskawa 2025] and is deferred (a companion physics program).

## 6. The real-market boundary: return tails are stationary

The controlled experiments concern the simulator. Do real markets share the transient? We test it
directly on returns. On five real one-minute crypto crash episodes (COVID-2020, the May-2021 selloff,
the June-2022 deleveraging, Terra/Luna, FTX) we pre-registered *Δα = α(crash) − α(pre)* on
volatility-standardized returns and compared it to a null distribution from a long calm window. The
driven-transient hypothesis predicts *Δα ≪ 0*; instead the pooled effect is *z = +1.03* (slightly
*lighter*), with one of five episodes a significant heavier-tail hit — within the false-positive rate
for five tests (Figure 3b). **Real return tails are stationary** — approximately cube-law in calm and
crash alike, consistent with inverse-cubic universality [Gabaix et al. 2003; Tóth et al.].

This is a clean, controlled result with a precise consequence: EcoMD's heavy tail is a non-equilibrium
property *of the model* — because it has no stationary heavy-tail source (a structural property, not a
training shortfall), it can produce heavy tails only transiently. The light steady state is itself the
finding, and it localizes the missing ingredient — a stationary heavy-tail mechanism — for this class of
simulators. It also sharpens the next question: *if the non-equilibrium driving is real but absent from
the return tail, where is it?*

![Measurement pitfall, OFI signature, and real-data boundary](figures/fig2_mech_boundary.png)

**Figures 1 & 3.** (a) **[Fig 1]** Hill index vs. warm-up discard — the measurement pitfall of §3
(both cells rise out of the cube-law band once the transient is dropped). (b) **[Fig 3a]** OFI memory
bursts (0.02 → ~1.0) and relaxes under the coherent shock, flat under a price gap (§5). (c) **[Fig 3b]**
real-crash *Δα* against the calm null — real return tails do not heavy-up (§6). *(Panels currently
combined from the shared figure set; split + renumber at LaTeX conversion.)*

## 7. The order-flow test: from simulator prediction to real data

### 7.1 The simulator's prediction (complete)

The mechanism in §5 answers the question of §6: in EcoMD the driving is invisible in the return tail of
a price-shock channel but loud in **order flow** under coordinated liquidation. This yields a sharp,
**pre-registerable prediction** for real markets: at real crash onsets — which are coordinated
liquidation events, not exogenous price gaps — **order-flow memory should burst toward perfect
persistence**, with (i) a monotonic (sigmoid) dependence on crash severity, (ii) generalization across
asset classes with a volatility-dependent threshold, (iii) a sharp relaxation, *precisely where the
return tail is stationary*. The full quantitative prediction is frozen in
`experiments/124_order_flow_transient/PREREG_phase2.md`.

### 7.2 The real-data test (PENDING — to be filled)

> **[BLANK — Phase 2.]** This section reports the pre-registered test of §7.1 on real
> limit-order-book data (Tardis L2, BTC/ETH, ≥2 stress episodes + calm controls). The setup, statistic,
> null, and binding decision gates are frozen in `PREREG_phase2.md`:
>
> - **Statistic.** *Δ(observable) = obs(crash) − obs(pre)* vs a calm-window-pair null; primary
>   observable = OFI memory (lag-1 autocorrelation of signed OFI), secondary = OFI tail, saturation.
> - **Gates (binding).** *G-main:* OFI memory bursts (one-sided *p ≤ 0.05*) on **≥2 episodes**, where
>   the return tail is stationary (the discriminating condition), surviving four controls
>   (vol-confound, reversibility surrogate, placebo onsets, returns cross-check). *G-null:* no burst on
>   any episode.
>
> **To fill on completion:**
> - **[Table 2 — real OFI memory/tail Δ per episode + pooled z, vs the calm null.]**
> - **[Figure 4 — real crash OFI memory burst-and-relax vs calm; EcoMD-predicted vs observed.]**
> - **Outcome (one of, per the frozen gates):**
>   - *G-main (positive):* "Real crash order flow shows the predicted memory burst where returns are
>     stationary, matching the EcoMD prediction in shape/dose/timescale — a controlled-experiment-derived
>     real-market discovery enabled by the simulator." → the central NCS claim.
>   - *G-null (negative):* "Real order flow is also stationary; the EcoMD transient is sim-only across
>     both returns and order flow." → the paper retreats to the simulator-physics + measurement-correction
>     contribution (§3–§6), an honest, self-contained result.

## 8. Discussion

EcoMD demonstrates a methodology: pose a causal question about market dynamics that observational study
cannot answer, resolve it by controlled intervention in a differentiable simulator, and convert the
result into a falsifiable real-data prediction. Along the way it delivers a transferable measurement
correction (warm-up hygiene for rollout-scored models), a controlled characterization of heavy tails as
a driven transient with an explicit mechanism and order-flow signature, and an honest boundary (real
return tails are stationary) that itself generates the §7 prediction.

**Scope and limitations.** The dynamical results are from a single simulator; the warm-up pitfall is
conjectured general to rollout-scored generators initialized off their steady state (to be verified
across model families). The return-tail boundary uses free intraday (crypto) data. The decisive
real-market test (§7.2) requires limit-order-book data and is pending. Entropy-production /
fluctuation-theorem treatment of the order-flow signature is deferred to a companion physics program
(Paper B), keeping this paper's contribution the *computational methodology* and the *order-flow
coherence* discovery.

## Methods (brief)

EcoMD: overdamped Langevin integrator; equivariant message-passing interaction potential; excess-demand
price formation; gradient calibration to a stylized-fact panel. Shock interface: scheduled
`state_kick` (coherent latent displacement) and `price_jump` (exogenous realized-return injection);
pre-impact excess demand and per-step order-flow imbalance logged directly. Windowed Hill index, OFI
memory (lag-1 autocorrelation), saturation, and exponential relaxation fits as described per section.
Real-data tests use a pre-registered null-distribution protocol over crash vs. calm window-pairs with
volatility standardization (`experiments/124_order_flow_transient/PREREG_phase2.md`). Full configs,
seeds, and analysis code in the repository.

## References
Cont 2001; Gabaix, Gopikrishnan, Plerou & Stanley 2003; Plerou et al. 1999; Bouchaud & Cont 1998; Dyer
et al. 2024; Chopra et al. 2023; Byrd et al. 2020 (ABIDES); Batatia et al. 2022 (MACE); Hill 1975; Tóth
et al.; Maskawa 2025; Seifert 2012.
