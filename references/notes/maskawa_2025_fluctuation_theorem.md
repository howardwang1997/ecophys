# Maskawa, J. (2025) — Empirical Study on Fluctuation Theorem for Volatility Cascade Processes in Stock Markets

**Citation**: Maskawa, J. (2025). *Empirical Study on Fluctuation Theorem for Volatility Cascade Processes in Stock Markets.* Entropy, 27(4), 435. doi: [10.3390/e27040435](https://doi.org/10.3390/e27040435).

**Affiliation**: Department of Economics, Seijo University, Tokyo.

**Note on citation error**: Throughout the project (plan_v1, plan_v2, draft_sections, CLAUDE.md, multiple logs) this paper was previously misattributed as "Doshi et al. 2025". The correct first author is **Junichi Maskawa**. All in-repo citations were corrected 2026-05-21.

---

## Core claim

The volatility cascade process in stock markets — where volatility "flows" from longer time scales to shorter ones, analogous to energy cascades in turbulence — **satisfies an integral fluctuation theorem (IFT) to ~5% accuracy**, when modeled via a Langevin system within the framework of stochastic thermodynamics.

## Method

- Apply stochastic thermodynamics (Seifert framework) to a Langevin model of volatility cascades
- Define thermodynamic-like quantities (temperature, heat, work, entropy production) along volatility trajectories
- Empirically compute these quantities from intraday returns
- Test whether the integral fluctuation theorem ⟨exp(-Σ)⟩ = 1 holds

## Data

- FTSE 100 constituent stocks (normalized intraday log-prices), London Stock Exchange
- Two additional Tokyo Stock Exchange datasets
- Multi-scale: aggregates from intraday → daily resolution

## Findings

- IFT holds at the ~5% error level across all three datasets
- Multifractal / intermittency structure of volatility is consistent with cascade-style energy/heat redistribution
- The "thermodynamic" interpretation (T_eff, σ̇) is meaningful (consistent values) at the analyzed scales

## Importance for EcoPhys

**Paper B (Nature Physics flagship) anchor citation**: This is the most recent and best-quality empirical
demonstration that fluctuation-theorem identities hold *in real financial data*. EcoMD's Paper B claim is
that we can reproduce these identities *inside a differentiable simulator* — closing the loop from "FT
holds in data" to "FT also holds in a learned generative model of the data".

**Paper A (NeurIPS Methods)**: Cite in §2 Related Work as motivation for measurement infrastructure
(non-equilibrium thermodynamic quantities at intraday-to-daily scales).

**Where we extend**: Maskawa computes FT *offline from data*. We:
1. Compute these quantities *inside the simulator* (differentiable, GPU-batched)
2. Use FT residual as either a *training objective* or *evaluation metric*
3. Apply to Jarzynski-style *driven protocols* (FOMC windows) rather than steady-state cascade

---

## Why Maskawa's work is published in Entropy (MDPI), not PRL / Nature Physics

This is worth knowing because **we want to avoid the same fate for Paper B**. Three structural reasons:

### 1. The econophysics field is structurally marginalized

- Born in the 1990s (Mantegna-Stanley, Bouchaud-Sornette, Lux) at the boundary of physics + finance
- Mainstream finance (Fama-school efficient-markets / no-arbitrage) didn't accept the "power laws everywhere" framing
- Mainstream physics didn't accept it either — no first-principles derivation from a Hamiltonian, just analogies
- Caught between two communities, neither claims it as their own
- Net result: papers in *Physica A*, *Quantitative Finance*, *Entropy*, *EPJ B* (IF 2-3), almost never *Nature*, *PRL*, *RFS*
- Tóth-Lux-Sornette **2018 PRL** is the rare success — and it succeeded specifically because it *derived* a Boltzmann equation from order book microstructure, not just measured analogies

### 2. Specific to Maskawa's research style

- He's at Seijo University (private Tokyo university, not a research powerhouse like UTokyo / Kyoto)
- Mid-career researcher in a small Japanese econophysics community (alongside Aoyama, Takayasu, Mizuno)
- Publishes steadily (~1-2 papers/year) on stochastic thermodynamics of volatility for ~15 years
- Estimated H-index ~10-15; citations typically <30 per paper
- **Style is empirical / descriptive**, not theoretical / predictive — "we measured X, it satisfies identity Y" rather than "we derived a new law that predicts Z"
- Mainstream physics reviewers' default question is "what *new* phenomenon does this paper predict, that didn't exist before?" — empirical FT-on-volatility doesn't quite answer that

### 3. Specific to MDPI Entropy as a venue

- IF ~2.7 (decent for open-access middle-tier journal, not top)
- MDPI publisher is controversial in physics — fast review (~6 weeks) and high acceptance rate cause many physicists to view it as "where you publish when PRE / PRL would be too high a bar"
- Some excellent papers in Entropy, but the journal-level signal is weak

### 4. No bridge to ML / data-science community

- Maskawa's work is read by the small econophysics community, not by ML/finance audiences
- No collaboration with high-status finance theorists (Lo, Brunnermeier, Cochrane) or top ML labs
- Top venues (Nature, PRL, JFE, NeurIPS) require *bridging* — the paper has to matter to multiple communities at once
- "We measured a thermodynamic identity in volatility data" only matters to ~30 people worldwide

---

## What this implies for our Paper B strategy

The risk of being **"another Maskawa"** is real. To avoid it, Paper B must do *all four* things Maskawa's paper doesn't:

1. **Bold theoretical claim, not just empirical verification** — e.g. "T_eff diverges with critical exponent ν = 1/2 at crash onset, on ≥3 timescales" (a one-line testable law, not "FT holds at ~5% error")
2. **Bridge to ML community** — make differentiability and GPU-batched gradient-based parameter estimation the methodological hook, so ML people care
3. **Bridge to finance community** — show downstream finance utility (crash early-warning, tail-risk hedging) so finance people care
4. **High-status collaborator or pre-registration** — since we don't have the first, we use the second (arXiv pre-registration is in plan v3 rigor clauses)

The plan v3 + Path C strategy is **explicitly designed** to break the Maskawa pattern by binding pre-registered "one-line laws" + tier-1 high-freq data + cross-community framing. The $8-12k high-freq data commitment is the single biggest lever — it's what lets us make claims that hold on the data physicists *do* respect (HFT / minute resolution), not just daily-bar work that physics reviewers dismiss as "econometrics territory" (per logs/2026-04-24.md §"我承认的问题").
