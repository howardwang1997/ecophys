---
description: Free/open-data feasibility execution state from 2026-08-19: exp137 dynamic LOBSTER baselines, exp138 SQD zero-target qualification, exp139 CUDA numerical envelope, and Tardis access blocker.
---

# Free/open-data feasibility — 2026-08-19

This is an archived parallel execution forked from `bcb025bd9`, not the canonical post-`a8bf89427` research
state. The remote branch independently occupied exp137--143 and closed the original NCS method route at G0;
any reusable result below requires renumbering and explicit reconciliation before migration.

- `experiments/138_sqd_zero_target_qualification/` Q0a passed all nine declared SQD EVM datasets using only
  metadata, finalized heads and repeated header windows. No Aave/event rows were queried. Target extraction
  remains locked until frozen Q0b validates non-target joins, independent hashes, immutable export and terms.
- `experiments/139_cuda_compute_calibration/` failed overall. Every `N=500` cell passed across 2×V100 and
  RTX2060; every `N>=2,000` cell failed finite/mechanics gates despite ample HBM. Treat `N=500` as the supported
  production ceiling until a preregistered stability diagnosis. Do not interpret failed-cell runtime as
  throughput.
- The RTX2060 default `ecophys` environment has a PyTorch/driver mismatch; the existing
  `ecophys-g0-regression` Conda environment is CUDA-compatible. No driver was changed.
- `experiments/137_free_lobster_dynamic_baselines/` passed 5/5 independent symbol paths. Across 947,911
  chronological transitions, 927,811/927,811 visible dynamic queue changes reconstructed exactly. Median
  combined observation-only gain was 0.271 nats/event and fell to 0.080/0.023 under 5/20-event staleness. These
  controls are now mandatory for G3, but one-day samples do not establish temporal or cross-domain validity.
- All eight held LOBSTER archives are staged in private R2 at `free/lobster_samples/2012-06-21/`. Canonical
  exp137 paths use five non-duplicate symbols and retain per-input SHA256.
- Tardis's documented no-key sample URL returned Cloudflare 403 from two egresses. Record it as an external
  access blocker; do not claim the sample was acquired. Existing free LOBSTER covers one-day equity plumbing,
  not crypto or representative temporal validation.
- Execution board: `papers/proposal/free_open_data_feasibility_2026-08-19.md`.
