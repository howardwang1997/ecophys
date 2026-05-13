---
name: Architectural floors — autocorr_returns + zumbach_asymmetry
description: Two of the 11 Cont 2001 facts are unreachable by any v3 + V4 + B-round mechanism composition; practical ceiling is 9/11 not 11/11
type: project
---

Across 1500+ trained models in Branch D/E/F (077-088), **two stylized facts fail in every cell tested**, regardless of mechanism mix:

1. **`autocorr_returns`**: every cell μ ≈ 0.32-0.46, band requires [-0.1, 0.2]. Caused by the AR(1) drift artifact (returns are AR(1) ρ̂=0.904, not random walk). Even the most-stable cells (`conf_b3_k3_pure`) only reach 32% pass. Source: smooth force-field drift `(f_cons + f_diss)/γ · dt` in `ecomd/physics/integrator.py:327` is autocorrelated by construction.

2. **`zumbach_asymmetry`**: every cell μ ≈ -0.03 to -0.12 (NEGATIVE), band requires [+0.001, +0.5] (POSITIVE). **Wrong sign**, not just out of range. Caused by absence of any directional/causal-asymmetry mechanism in v3. Memory kernel (V4 mech 3) modulates noise symmetrically in lag direction — does not produce positive Zumbach. Computation at `ecomd/eval/stylized_facts.py:603-674`.

**Why:** Until 2026-05-13, "ceiling at 5-6/11" was treated as a stochastic/coverage problem — try harder mechanisms, more seeds. Branch F's 50-seed confirmation across 14 cells showed it's deterministic: these 2 facts cannot be lifted by any combination of the existing mechanism family. The architecture has a 9/11 cap, not 11/11.

**How to apply:** 
- Stop interpreting cell mean=5/11 as "halfway there"; interpret as "5 of 9 reachable facts" (~56%, much closer to ceiling).
- Any new mechanism proposal must declare which floor it targets (autocorr or zumbach) and what collateral damage to expect.
- Paper A (NeurIPS 2027) frames these as falsification findings, not bugs — see `project_paper_a_neurips_2027.md`.
- AR(1) and Zumbach patches are scheduled in M1 of the NeurIPS 2027 plan; the *outcome* of those patches (whether they lift the floors or trade other facts) is the headline experimental finding.
