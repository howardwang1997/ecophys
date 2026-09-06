# E-5 — Frozen Hydra configs + seed/stream manifest

Build item E-5 of the D0 build register (simulator contracts section 4; prereg v2
C1-C4, C8/Annex B, C14 restated section 3.4, C16 items (11)-(16)). Built
2026-09-07 on git head `16b0ea981003987a474f4f44a9c721e89a80a902`,
outcome-blind, code-only, CPU second-scale checks only.

## What was built

- **`configs/reexploration/`** — a 20-file Hydra tree (Hydra 1.3.2,
  `version_base="1.2"`). Select one option per group:
  `block=<b1|b2|b3|b4_variant_a|b4_variant_b> arm=<...> axis=<id|pop_2x|tick_2x|kswap>`.
  - **block** binds lineage x DGP x seed namespace x Stage-2 subset x
    truncation conditions (B1 = L1 x lab-asset, 11000-11029, 30 seeds;
    B2 = L1 x garch, first-15; B3 = L2 x lab-asset, 12000-12029;
    B4-variantA/B = L2 x garch / multiscale_logvol, first-15).
  - **lineage** records the frozen module hyperparameters (L1-2
    coordinate-heads / L2 fact-surrogate) — the validator asserts equality
    against the sibling dataclass defaults, so the tree cannot drift.
  - **dgp** records the full 30-field E-2 `DGPConfig` mapping (ID axis);
    `negative_jump_iid` has **no selectable option** (exclusion by absence,
    cross-checked against E-2 `D2_NAMED_NOT_RUN`).
  - **arm** records the 4 trained arms ({absolute, increment} x {raw,
    through_m}); **axis** records the 4 conditions (kswap: DGP truth
    unchanged, only the inference kernel swaps to random_unit_within_price,
    raw-infer kswap evaluations are byte-identical duplicates of the ID
    stratum).
  - Horizons {1, 4, 16, 31} (h=64 descriptive), K=16 draws, the 2 inference
    enforcements and the 8 cells/seed are **eval-time parameters** under
    `eval`, not training parameters.
  - `audit/a10.yaml` is the KT-A4 two-estimator audit cell (retrains B1's
    (increment, through-M-train, raw-infer) cell under perturb-and-map on
    all 30 paired seeds, reusing B1's data/init/train_kernel substreams).
- **`ecomd/reexploration/campaign.py`** — the enumeration + seed authority:
  450 trainings / 299,520 confirmatory records **reproduced by explicit
  grid enumeration** (validate_counts raises on any mismatch with the
  section-3.4 tables); 18 disjointness checks (fail loudly via
  SeedCollisionError); Hydra-tree validation against the frozen sibling
  surfaces; canonical-JSON manifest builder.
- **`experiments/reexploration/seed_stream_manifest_20260907/seeds_manifest.json`**
  — sha256 `361679c4a56e8e7fe7d393499ed22f5c9f61bef81706a1befa8ca7df27ea32f8`
  (41,258 bytes). Records both training namespaces (11000-11029 L1,
  12000-12029 L2) with Stage-2 first-15 / reflexive first-10 subsets; the 5
  disjoint instrument namespaces (enrichment 20260972, resampler 20260973,
  S3 20260974-76, K-preflight reserved 31000-31099 masters 31000-31031, PAM
  fixture 20260906); all 60 seed roots with all 20 named substream integers
  (SeedSequence.spawn derivation); the Annex B(a) bootstrap salt and all 15
  (block, family) bootstrap seeds; the rank-seed posture note.
- **`scripts/reexploration/validate_e5_configs.py`** — one-shot validator
  (config tree + arithmetic + disjointness + on-disk manifest byte-equality
  vs rebuild; exit 1 on failure; ~4 s CPU).
- **`tests/test_e5_configs.py`** — 16 tests, 6.9 s, CPU only.

## C14 self-check outcome

The enumeration reproduced the preregistered targets exactly — 240 + 180 + 30
= **450 trainings**; 122,880 + 92,160 = **215,040** mandatory-axes; **76,800**
truncation; **7,680** audit; **299,520** confirmatory total; **420**
horizon-one probes; 2,048 records per seed. **No discrepancy was found**;
the STOP-and-record condition did not trigger. Any future drift raises
`CampaignArithmeticError` (tested).

## Notable recorded resolutions (full list with reasons in receipt.json)

- Train hyperparameters bind the frozen sibling-module defaults; production
  iteration counts are pinned by the D0 trainer runtime.
- Rank-seed posture pinned to world_size=1 (at world_size>=3 the L1 rank-2
  seeds would numerically equal the K-preflight masters — flag 5).
- s_ch (channel_scales) never materialized in the tree (Annex B(e)
  hash-sealed DGP-only branch).
- The E-2 preflight re-run was NOT executed (separate PI-visible remote
  step).

## Reproduce

```bash
conda run -n ecophys python scripts/reexploration/validate_e5_configs.py
conda run -n ecophys python -m pytest tests/test_e5_configs.py -q
```
