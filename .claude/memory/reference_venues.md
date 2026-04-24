---
name: Target venue registry (EcoPhys)
description: Target publication venues with deadlines, acceptance characteristics, realistic fit for the three pillars. Guides paper positioning and scheduling.
type: reference
originSessionId: c6748c05-53ac-462d-9535-154e95f91d9f
---
# Target Venue Registry — EcoPhys

## ML Conferences (Paper A — methods)

| Venue | Acceptance | Typical deadline | Fit for EcoPhys | Notes |
|---|---|---|---|---|
| **NeurIPS** | ~25% | May (abstract), May+1wk (full) | C1 + ablations + 1 downstream task | Main target for Paper A. Prefers novel methodology + clear theory hook. |
| **ICML** | ~23% | Jan–Feb | Same as NeurIPS | Secondary; earlier deadline → useful if NeurIPS slips. |
| **ICLR** | ~22% | Sept–Oct | Same | Good fit; openreview can help. |
| **ICAIF** (ACM) | ~30–40% | Aug | C1 + finance-flavored C3 task | Lower bar; useful fallback / community building. |
| **NeurIPS-W ML4Fin / TS workshops** | higher | Summer | Early arXiv + workshop visibility before main submission | Consider for arxiv announcement around M3. |

## Physics Journals (Paper B — non-equilibrium thermodynamics)

| Venue | Scope | Fit | Notes |
|---|---|---|---|
| **Nature Physics** | New physical phenomena, cross-domain universality | **PRIMARY target for Paper B (plan v3 + Path C, 2026-04-24).** Requires: A1 T_eff critical scaling on ≥3 timescales + B2 Jarzynski with FOMC/earnings protocol + all 7 sanity checks pass + Wk 28 arXiv pre-registration. | **15–22%** joint probability after Path C high-freq data commitment ($8–12k). Was ~3–8% under plan v2. Multi-scale A1 + FOMC-protocol B2 + L2 B3 each close a specific reviewer attack. See `plan_v3.md` §3, §6. |
| **PNAS** | Interdisciplinary | Alternative flagship if NP desks-reject; more applied-leaning framing | Re-home Paper B with minor framing changes if needed. |
| **Physical Review Letters (PRL)** | Short letters, broad interest | **Primary retreat target** for Paper B if NP fails any gate. Also: **Paper B.5 (TUR companion) independently targets PRL.** | 4-page limit — forces clarity. Tóth-Lux-Sornette 2018 published here. Tested retreat path in plan v3 §7. |
| **Physical Review X** | Longer, open-access, high-impact | Alternative to PRL with more length | Slower review. |
| **Physical Review E** | Stat mech, nonlinear dynamics, complex systems | Solid tier-2 fallback | Well-defined audience; comfortable home for econophysics. |
| **Physica A** | Stat mech + applications | Tier-3, higher acceptance | Always-open fallback. |
| **J Stat Mech (IOP)** | Stat mech + complexity | Like Physica A | Fallback. |

## Finance Journals (Paper C, optional)

| Venue | Fit | Notes |
|---|---|---|
| **Journal of Financial Economics (JFE)** | If C3 has strong econ interpretation | High bar; slow review. |
| **Review of Financial Studies (RFS)** | Same tier as JFE | Same notes. |
| **Journal of Financial Econometrics** (OUP) | Econometric/methodology bent | Good fit if paper leans empirical. |
| **Quantitative Finance** (T&F) | ABM-friendly, methods-friendly | **Most realistic finance home**. |
| **Journal of Empirical Finance** | Empirical finance, returns, microstructure | Solid fit. |
| **Journal of Economic Dynamics and Control (JEDC)** | Agent-based models, macro | **Most ABM-friendly**; several ABM market-sim papers here. |

## Practical scheduling

- Paper A (methods): aim NeurIPS 2026 if plan tracks Wk 40–46; fallback ICLR 2027 or ICML 2027.
- Paper B (physics): aim PRL after M4 success; try Nature Physics as one-time pre-PRL submission (15-day desk reject worst case). Submission Wk 50+.
- Paper C (finance): optional; QF or JEDC depending on how the applications chapter develops.

## Go/no-go gates
- **Wk 33 M4**: if no clear cross-market universal quantity found, abandon Nature Physics lottery and commit to PRL-only for Paper B.
- **Wk 26 M3**: if stylized facts match does not clearly beat baselines, consider switching Paper A target from NeurIPS/ICML main to NeurIPS-W + ICAIF.
