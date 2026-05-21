---
name: MACE-lite v1 canonical failure case (2026-04-22)
description: MACE-lite v1 failed at 0-4/11 across 8 ablations in 2026-04-22 due to two architectural causes (per-node readout smooths force 60-190× too small; k-NN biased sparsity loses long-range pair signal). v0.9 Stochastic Pair Sampling (SPS) was designed as the explicit fix. Any future learned-potential work must respect this failure record.
type: project
---

## What failed

MACE-lite v1 (`ecomd/models/mace_lite.py`, 328 LoC, tested in `tests/test_mace_lite.py`, used in `experiments/006-008`) failed at **0-4/11 across 8 ablations** on SPX daily.

## Why it failed (two architectural causes)

1. **Force magnitude 60-190× too small** — per-node MLP readout averages out per-edge contributions. The aggregation `h^(1) = Σ_j m_ij` followed by per-node MLP smooths out the burst-and-decay structure that's essential for vol clustering.
2. **k-NN biased sparsity** — locality in feature space loses long-range pair signal. Real market microstructure has nontrivial fat-tail interactions that k-NN cuts.

Source: `papers/proposal/improvement_paths.md` C3 + `papers/proposal/scaling_v1.md` §2 + `logs/2026-04-25.md` 关键发现 #1, #3.

## The fix (already done, not MACE-related)

**v0.9 Stochastic Pair Sampling (SPS)** in `ecomd/models/potentials.py` (`StochasticPairwisePotential`). Properties:
- Unbiased random pair sampling (vs k-NN biased local)
- Preserves O(N²) pair-sum scale via (N-1)/k rescaling
- NO per-node readout — keeps φ(s_i, s_j) directly
- Preserves v0.x burst-and-decay physics

v3 hand-crafted mechanism family (Branch D/E/F → 089-099 → current SOTA Gold zumdn 5.96) is built on SPS, NOT MACE-lite.

## Why this matters

The 089-099 Pareto ceiling at ~5.5/11 holds across **4 architectures**: v0.x complete pair, v1 MACE-lite (failed), v0.9 SPS (~5.0-5.5), Tier 4.2 dynamic graph (5.14), v3 hand-crafted (best 5.96). This is significantly stronger evidence than "v3 family is bounded" — multiple architectural families converge near the same ceiling.

## Implication for future Paper A work (Track B-MACEv2)

Per user instruction 2026-05-21, MACE-lite v2 CAN be retried as Paper A Track B-MACEv2, but ONLY with **explicit failure-aware safeguards** (`papers/proposal/paper_a_next_steps_2026-05-21.md` §7):

| Failure mode 2026-04-22 | Required mitigation in v2 |
|---|---|
| Per-node readout smooths | `F = -∇U` via autograd readout, NOT per-edge MLP readout |
| k-NN biased sparsity | Hybrid graph: k-NN UNION SPS random pairs, OR pure SPS with attention |
| Body-order 3/4 smoothing | Default body_order=2, only test 3/4 if smoke shows comparable force magnitude |
| Force magnitude 60-190× shortfall | **Mac smoke pre-flight gate**: measure `\|\|F_v2\|\| / \|\|F_v3_baseline\|\|`. If ratio < 0.5×, HARD STOP — do not commit H20 |

## Why: lessons learned

Smoke-test gates exist because the original 2026-04-22 ablations went to H20 without a force-magnitude pre-flight check, wasting ~20h H20 wall-clock on 8 ablations that all failed for the same architectural reason. Future learned-potential work cannot repeat this — the pre-flight gate makes the cost of repeating the mistake near-zero.

## How to apply

- When anyone (user, agent, future self) proposes learned interaction potentials, check this memory first.
- Any new `*.py` learned-potential module must be a NEW file, not modify `mace_lite.py` — v1 stays as failure record.
- Force-magnitude assertion against v3 baseline is a required unit test for any new learned-potential module.
- The original `ecomd/models/mace_lite.py` is kept on disk as documentation of what doesn't work; do not delete.

## Linked

- [[project_paper_a_neurips_2027]] — Track B-MACEv2 description
- [[project_pareto_ceiling]] — multi-architecture ceiling evidence
- `papers/proposal/improvement_paths.md` C3 — fix proposal
- `papers/proposal/scaling_v1.md` §2 — comparison table v1 vs v0.9 SPS
- `logs/2026-04-25.md` 关键发现 #1, #3 — original failure record
