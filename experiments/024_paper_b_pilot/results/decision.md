# Paper B path decision (post-pilot)

## Pilot result (Mac N=1000, C4 ckpt)

| Quantity | Value |
|---|---|
| T_eff mean | +481.4 |
| T_eff std | 2.64 |
| **Relative std** | **0.55%** (effectively constant) |
| Cross-corr T_eff vs \|r\| | +0.128 |
| Cross-corr T_eff vs r² | +0.138 |
| Peak lag of T_eff→\|r(t+τ)\| | τ=0 (no precedence) |
| f_cons_mean_abs | 10.2 |
| f_diss_mean_abs | **0.003** ← tiny |
| f_stoch_mean_abs | 2.0 |
| σ̇ mean | -0.001 |

## Diagnosis

**The simulator is running near-equilibrium**. The dissipative force
channel is 3 orders of magnitude smaller than conservative + stochastic.
T_eff stays at 481 because f_diss is too small to perturb the equipartition
balance.

This is the **honest reality** for Paper B's "non-equilibrium thermodynamics
of markets" claim:

- We trained C4 to MATCH stylized facts of real returns
- The trained simulator achieves this by sitting near a Langevin equilibrium
  with bursty Hawkes excitation in the price layer
- But the AGENT-LEVEL state s(t) is at equilibrium → T_eff(s) is constant

## Three reactions

### Option A — Restrict Paper B to PRL (TUR alone)

The constant T_eff still admits a meaningful TUR check:
  Var(J)·⟨σ̇⟩ ≥ 2 k_B (steady-state TUR)
We can compute:
- J(t) = current of any conserved quantity (e.g., type-1 ↔ type-2 mass flow)
- ⟨σ̇⟩ time-mean = 0.001 (very small)
- Var(J) is non-zero from Langevin noise

Even at near-equilibrium, TUR saturation (or non-saturation) is a
publishable result. Single market, single regime, 1-page PRL or PRR.
**Prob 30-45%.**

### Option B — Force out-of-equilibrium driving

Modify the simulator to include explicit non-equilibrium forcing:
- Time-varying external field (Jarzynski work protocol from Paper B plan)
- FOMC-window driving (event-driven protocol — needs minute data!)
- Detune γ/T after training so simulator runs off-calibration

Then T_eff(t) WILL vary (driven system). This is what Doshi 2025 does:
they use realized vol as driving signal. We can do the same with our
Hawkes-amplified price.

**Recommended pilot**: re-run T_eff on a TRAJECTORY with imposed non-eq
driving (sinusoidal external potential or piecewise-stationary regime
shifts). See if T_eff(t) tracks the driving.

### Option C — Restrict the claim: T_eff(t) on price-LAYER only, not state

Paper B might claim:
**"Effective temperature of the PRICE process (not the latent state) 
shows critical scaling near volatility regimes."**

Compute T_eff_price = ⟨r²⟩ × (some factor) per window. Since price IS
non-stationary (Hawkes burstiness), this T_eff_price WILL vary. It's
not the agent T_eff but it's still a physics-grounded observable.

This sidesteps the "agent-level state at equilibrium" problem.

## Decision matrix

| Path | Effort | NP Prob | PRL Prob |
|---|---|---|---|
| A: PRL TUR alone | 1-2 weeks pilot + 4 weeks paper | 0% | **30-45%** |
| B: Add non-eq driving + redo pilot | 3-4 weeks code + 2 weeks pilot + 8 weeks paper | 8-12% | 25-35% |
| C: T_eff_price (not state) | 1 week pilot + 4 weeks paper | 5-10% | 35-45% |

**My recommendation**: Path A first (cheapest, highest immediate prob),
then if T_eff_price (Option C) on H20 N=10K shows structure, that
becomes the NP claim.

## Caveats on this pilot

1. **Mac N=1000** vs H20 N=10K. Larger N might break equipartition more
   visibly via finite-N effects.
2. **C4 ckpt loaded with strict=False** — buffer mismatch (twopop_type_idx
   regenerated) may have invalidated the type-conditional dynamics.
3. **Daily SPX data only** — Path C minute/L2 data WILL show different
   structure (the original Paper B premise).
4. **4000 steps is short** for picking up slow scaling.

**Action items**:
- Re-pilot at H20 N=10K with full ckpt (use weekend's spare time)
- Compute T_eff_price as an alternative observable
- If both flat → commit to PRL path
- If either shows structure → revise Paper B accordingly
