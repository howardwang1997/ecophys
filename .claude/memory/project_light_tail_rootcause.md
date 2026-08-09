---
name: project_light_tail_rootcause
description: Root cause of EcoMD's light steady-state tail — exp 125 verdict: CLT self-averaging acts on the RETURN tail (α_ret rises with N) but NOT on excess demand (α_ED FLAT); two-stage mechanism, self-correction
metadata:
  type: project
---

**🔴 2026-08-09 EcoMD audit-spec finding.** The audited training API processes 24-step chunks but does
not return the recurrent global state $u$, so $u$ is reset between training chunks; formal inference
persists $u$ for 8,000 steps. Training also uses a drift proxy where inference uses compound-Poisson
jumps. These are concrete training/inference mismatches and plausible contributors to late-time
fidelity failure, but exp127 does **not** identify either as the causal explanation for the light tail.
Both must be repaired and ablated before a positive EcoMD model-paper claim. They are disclosed in the
Sim2Science technical appendix and promoted to the EcoMD v1 M0 release gate.

**🔴 2026-07-22 exp 126 audit update.** The five-asset extension confirms nearly flat raw-ED Hill vs N
and strongly rising raw/EWMA-standardized return Hill, but this is not yet a clean CLT mechanism proof:
the fixed additive price noise and nonlinear concave-impact/SNR mixture must be decomposed with
`sigma_price=0` and fixed-SNR controls. The full atlas confirms that coherent kick and the
reduced-friction (`liquidity_drop`) proxy fatten tails while `temperature_spike` is essentially control;
the market-liquidity interpretation remains an unvalidated mapping assumption. The dense dose result
supports a saturating **dip-amplitude** law, but its recovery estimator gives SPX tau=350 for all eight
doses and therefore contradicts the old tau(dose) headline. All 12 G-D1b Lévy models trained, but the
local Pareto JSON still has no trained-model point; fix raw-vs-post-impact ED logging before running the
H20 score/emit rescue. G-E remains unrun. See [[project_workshop_audit_2026-07-22]].

**🔴 2026-06-30 exp 125 RESULTS — self-correction (supersedes the 06-29 "CLT-on-ED" headline below).**
The pre-registered PRIMARY mechanism test **G-D2 (steady α_ED vs N at fixed trained dynamics) came back
FLAT**: α_ED ≈ 4.65–4.77 across N ∈ {100…30000} (spx & btc), inside window-std ≈0.7. So **CLT self-
averaging of *excess demand* is REFUTED** — the ED tail index is **dynamics-set (single-agent confining
potential, P1), not aggregation (P2)**. BUT the *return* tail **α_ret rises cleanly/monotonically with N**
(spx 5.49→8.65, btc 5.47→8.54, ≈1.3/decade): self-averaging is real but acts at the **price-formation /
√N-normalized return stage**, not the raw ED stage ⇒ **two-stage mechanism**, not the single "CLT on ED"
story. (α_ret is a *secondary* observable → re-pre-register + rule out a return-scaling-with-N artifact
before headlining; anti-gate-shopping.) **G-D1a** (heavy bath noise at inference, normal→Lévy α1.5,
infinite variance): α_ED **flat ~4.75** — a TRUE negative (override is live: α_ret moves 7.60→8.97), the
learned dissipative dynamics launder even infinite-variance shocks; Route A's cheap version FAILS, and
**G-D1b (trained-Lévy) + G-E (2nd-generator) did NOT run** (no dirs; optional jobs skipped). **G-D1a
clustering cost (computed 06-30): NO tails-vs-clustering tradeoff** — heavier Lévy makes BOTH worse (spx
hill_fact 5.04→6.79 lighter AND ACF² 0.264→0.237 less clustering; btc same) ⇒ the "heavy noise→heavier
tail at a clustering cost" Pareto is NOT supported by G-D1a; tails-XOR-dynamics must lean on
[[project_neural_sde_tournament]], not exp125. Positive contrast: coherent kick6 raises BOTH heaviness
(hill 5.0→2.7) AND clustering (ACF² 0.27→0.48), incoherent noise neither. **G-B atlas:** `liquidity_drop`
revives the transient (post-shock α_ED dip 3.15–3.40 ≥2 on spx/ndx/btc, 3/3) but `temperature_spike`
does NOT (dip 0.17–0.85) ⇒ sharper mechanism: **coherent-displacement / liquidity-withdrawal phenomenon,
NOT generic thermal agitation** (consistent w/ heavy-noise negative). **G-C dose law:** clean monotone
saturating sigmoid, onset 0.1–0.2σ, dip saturates ~3.9 (dose≥2), postmin floors ~0.5 (Hill floor → use
dip-kurtosis in saturation). **G-A rigor:** control α_ED 4.75–4.84 (n=32–56) tight; kick6 strong on
spx/ndx/btc/gold (postmin 0.47–0.57), eurusd weak (postmin 2.98, consistent [[project_eurusd_weak_ofi]]).
(Mac clone is partial `blob:none`; an intermittent fetch flake — not the Mac — caused the earlier hangs;
now fast-forwarded to `5929ce9ce`, all 544 files local, gaps above resolved.) See `logs/2026-06-30.md`.

---

**2026-06-29 root-cause verdict (user asked: why the negatives? fixable? fundamental?) — P2 now
REFUTED for ED, see 06-30 above.** EcoMD's
**light steady-state tail (Hill α_ED≈4.7, not cube-law) is FUNDAMENTAL**, from three first-principles
reasons: (P1) Boltzmann light tail of a smooth confining learned potential (power law needs U∼log|s|);
(P2) **CLT self-averaging** — ED=κΣΔs over N≈10⁴ finite-variance, short-correlation agents → Gaussian
aggregate → light, *stronger pull as N grows* (the dominant effect) — **⚠️ REFUTED 06-30: α_ED flat in
N; CLT acts on α_ret (returns), not ED**; (P3) sub-critical coupling (exp
116/120 smooth crossover, no N_c). Heavy tail is a **driven transient** because a shock imposes
system-spanning coordination transiently; CLT reasserts on relaxation. **This is the mechanism, not a
failure** — the central reframe: lead with *EcoMD-the-laboratory + the interventional mechanism of fat
tails* (we can switch the heavy tail on/off, which observation of real markets cannot).

**Solvability:** (A) heavy micro-noise (Lévy/Student-t — **in code & runnable**: `noise_dist∈{normal,t,
levy}`, `noise_levy_alpha`, CMS sampler) CAN install a stationary heavy tail but the index is hand-set
and trades off volatility clustering = the **Pareto cost**; (B) SV/multiplicative — explored, hit the
ceiling (exp 119 4.90; MoE/diffusion); (C) criticality — explored, no sharp N_c. ⇒ N1 is "fixable only
by changing the model class, at the cost of the temporal facts" = the Pareto-frontier finding itself.

**Negatives handling (user directive — fix-or-deemphasize, don't headline; honors [[feedback_no_downgrade]]):**
N1 light tail → reframe as the positive CLT mechanism; N2 (real return tails stationary, z=+1.03) is a
**DATA fact** (real markets carry the always-on heavy source EcoMD lacks), the *predicted boundary* →
demote to a one-paragraph scope note + order-flow handoff; N3 EP-flat → one sentence (Paper-B carve-out);
N4 Pareto ceiling → present as a positive structural result.

**exp 125** (`experiments/125_rootcause_controllability/`, binding PREREG, no data buy, reuses
concave_d050 ckpts): G-A rigor n=30 CIs; G-B controllability atlas (new non-mechanical channels
`temperature_spike`/`liquidity_drop` — rebut "state_kick is mechanical", GenAI lead); G-C τ(dose) law
(ML4PS); **G-D root-cause ablations = the new core** (D1 heavy-noise→stationary tail? cost to clustering;
**D2 steady α_ED vs N at FIXED trained dynamics = the clean CLT self-averaging proof** exp 120's
train-at-N confounded); G-E 2nd-generator pitfall. Driver `scripts/gpu_exp125_atlas.sh` (worker/ablate/
eval/fanout). PREREG pre-commits every arm to positive content either way (anti-gate-shopping guardrail).
Doc: `papers/proposal/paper_a_rootcause_and_reframe_2026-06-29.md`. See [[project_burnin_artifact]],
[[project_pareto_ceiling]], [[project_neural_sde_tournament]].
