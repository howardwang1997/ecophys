# D1_06 — DGP-only, zero-GPU K-variance preflight (K freeze evidence)

**Authorization.** PI decision `pi_reexploration_d1_authorization_20260906` item D1_06:
CPU-only execution of the DGP engine and request-generation machinery for instrument
calibration; K in {4, 8, 16} frozen before D0 and immutable after (contract C2(e)),
default 8. No GPU, no trained models, no cell endpoints, no outcome access, no market
data, no writes under the frozen `a2_exit_20260905` bundle.

**Artifacts.** `dgp_stream.py` (minimal lumpable request-stream generator),
`run_preflight.py` (replay + statistics + variance decomposition + K-table),
`preflight_config.json`, `results.json` (38 KB, deterministic),
`determinism_check.json` + `.verify/results.json` (byte-identical re-run), tests at
`tests/test_k_preflight_dgp.py` (5 tests, green).

## Design

- **Generator (calibration-grade, NOT the D0 corpus generator).** M0 policy class —
  the strongest-lumpability point of the M0/M1-lumpable class of contract C2(a): each
  episode's request stream (3 multi-order ask levels + resting bids, 2 resting ask
  adds, 3 aggressive buys each ending strictly inside a multi-order pool with
  1 <= V* <= R*-2, 1/6 single-unit stratum, latency-window straddling pools by
  construction) is a pure function of the episode stream RNG; nothing feeds back on
  the tape or allocation identity. Master seeds 31000-31031 (namespace disjoint from
  all training/Paper-D/D2 ranges). Substream seeds derived by sha256
  (`derive(root, "stream" | "draw", ...)`), version-independent of RNG libraries.
- **Replay structure.** 32 seeds x 6 episodes; each episode evaluated under BOTH arms
  (`fifo`, `random_unit_within_price`) x 16 draw replays (nested: K=4 subset of 8
  subset of 16), request stream byte-identical across all evaluations of an episode;
  only the engine draw seed (prestate.seed) varies. Per-seed per-replay value = mean
  over episodes, mirroring the contract's per-seed K-draw-mean cell value.
- **Statistics (DGP-native consumers, theory-appendix sense).** Nulls (stream-
  deterministic, verify zero draw variance): `c_risk_rawflow`, `c_lat_rawflow`,
  `cleared_volume_units`, `clearing_notional`. Draw-dependent: `c_lat_exec`
  (realized latency-window executed notional, Theorem 1(e)(ii) direction),
  `alloc_hhi_mean`, `alloc_l2_mean`, `alloc_proprata_dev_mean` (allocation-vector
  deviation from pro-rata using DGP ground-truth pools), `n_maker_orders_filled`.
- **Variance identity and estimators.** `E[B(K)] = V_between + W/K`; `B(K)` =
  across-seed variance of realized K-draw means; `W` = mean within-seed 16-replay
  variance; `V_between = B(16) - W/16`; ratios vs between and vs total; seeded
  seed-level bootstrap (2000 draws) 95% CI on the between ratio.
- **Engine-grounded invariants (all 0 failures across 192 episodes / 576 walks).**
  FIFO payload-projection identity across the 16 draw replays (the F_exec-layer G8
  analog; state-hash envelopes legitimately differ because `prestate_hash` binds the
  draw seed); request-boundary `aggregate_state_hash` sequence identity across BOTH
  arms and all 16 replays (engine-native confirmation of aggregate-tape kernel and
  draw invariance on this generator — 32 evaluations per episode); random-unit
  accepted-stream identity; null-statistic zero draw variance; zero rejections
  (resource-slack M0 tape); generator-predicted cleared volume and per-walk
  (target price, V*, swept units) match the tape exactly. V* ladder realized:
  V*=1: 88, V*=2: 75, ... up to V*=20; all 192 episodes fully window-straddling.

## K-choice table (random_unit arm; ratio = draw contribution W(K) / between-seed variance)

| statistic | V_between | W | K=4 ratio [CI] | K=8 ratio [CI] | K=16 ratio [CI] |
|---|---|---|---|---|---|
| c_risk_rawflow* | 137866.6 | 0.0 | 0 [0,0] | 0 [0,0] | 0 [0,0] |
| c_lat_rawflow* | 56275.6 | 0.0 | 0 [0,0] | 0 [0,0] | 0 [0,0] |
| cleared_volume_units* | 3.23 | 0.0 | 0 [0,0] | 0 [0,0] | 0 [0,0] |
| clearing_notional* | 34316.1 | 0.0 | 0 [0,0] | 0 [0,0] | 0 [0,0] |
| c_lat_exec | 41245.4 | 725.2 | 0.0044 [0.0029, 0.0088] | 0.0022 [0.0015, 0.0044] | 0.0011 [0.0007, 0.0022] |
| alloc_l2_mean | 0.129 | 0.004 | 0.0083 [0.0056, 0.0161] | 0.0042 [0.0028, 0.0080] | 0.0021 [0.0014, 0.0040] |
| n_maker_orders_filled | 0.165 | 0.018 | 0.0271 [0.0185, 0.0475] | 0.0136 [0.0093, 0.0238] | 0.0068 [0.0046, 0.0119] |
| alloc_hhi_mean | 0.0034 | 0.0012 | 0.0694 [0.0417, 0.1696] | 0.0347 [0.0208, 0.0848] | 0.0173 [0.0104, 0.0424] |
| alloc_proprata_dev_mean | 0.0051 | 0.0141 | 0.7832 [0.4726, 1.8813] | 0.3916 [0.2363, 0.9406] | 0.1958 [0.1182, 0.4703] |

\* null controls: exactly zero draw variance on both arms (verified), ratios 0 by construction.

## Recommendation

**K = 16** under the preregistered conservative rule (smallest K in {4,8,16} such that
EVERY random_unit draw-dependent statistic has bootstrap 95% upper bound of the
between-ratio <= 0.10) — with an explicit insufficiency flag: `alloc_proprata_dev_mean`
fails the 10% criterion at every authorized K (draw variance exceeds its between-seed
variance; ratio 0.196 at K=16), so the rule returns "none_in_set" and 16 is the best
available value. Reading of the table (descriptive, not a re-tuned rule):

- **Endpoint-shaped functional statistics** (notional- and volume-weighted tape
  functionals: `c_lat_exec`, `alloc_l2_mean`, `n_maker_orders_filled`) clear the 10%
  bar by an order of magnitude already at K=4 (worst CI upper 4.8%); K=8 gives
  <= 2.4%. The Stage-1 endpoint (conserving-channel rollout error) is a functional of
  this shape, but this preflight cannot verify that pre-D0 (caveat 1).
- **Allocation-concentration** (`alloc_hhi_mean`): K=8 clears 10% with CI upper 8.5%;
  K=4 does not (CI upper 17.0%).
- **Allocation-shape deviation** (`alloc_proprata_dev_mean`): between-seed-stable but
  draw-noisy at these pool sizes; per-seed means of this statistic class remain
  draw-noisy at ANY K in the authorized set. If per-seed allocation-shape quantities
  matter downstream, no authorized K fixes them — a property of the statistic class,
  not of K.

PI options at the D0 freeze: (a) adopt K=16 (adds ~1x eval compute over K=8; eval is
~96 of ~650 Stage-1 V100-h, so ~+15%), accepting the documented residual on
allocation-shape statistics; (b) adopt K=8 on the reading that endpoint-shaped
functionals dominate and the contract's paired CRN makes contrast draw-variance at
most the single-arm values above (conservative bound); both readings are supported by
the table; the frozen rule's mechanical output is 16. K=4 is not supported
(`alloc_hhi_mean` CI upper 17% and no margin anywhere).

## Determinism

`results.json` is a pure function of (config, code); no timestamps or absolute paths.
Verified: two independent runs (default dir and `.verify/`) produce sha256-identical
files `f61e410cd59c37b5624504a3cdf057c701b4b682067f948d2f8528ace018c2d4`
(`determinism_check.json`).

## Honest caveats

1. **This preflight bounds ONLY the DGP-side draw-replay component** of per-seed
   variance. Stage-1 endpoint channels additionally carry training noise, neural
   decode error and horizon-rollout divergence that no zero-GPU, no-trained-model
   preflight can see; the K freeze conditions on the DGP-side component alone.
2. **Between-seed variance here is calibration-generator design variance**; the
   frozen D0 corpus generator may differ (and must be M0/M1-lumpable per C2(a)). If
   the D0 generator adds feedback channels (e.g., own cash/inventory for makers),
   re-run this preflight against it before freezing K — cheap (24 s CPU).
3. **CRN direction is conservative**: the contract replays the same K draw streams
   across cells within a seed, so paired-contrast draw variance is at most the
   single-arm draw variance measured here; reported ratios are upper bounds for the
   contract's contrasts.
4. **The training-time kernel stream** (one draw consumer per through-M arm) is
   outside this preflight's scope.
5. The FIFO arm is exactly draw-invariant (verified), so K>1 on deterministic-kernel
   cells buys only the G8 byte-identity determinism gate; it cannot inform the K
   choice.

## PI ruling (2026-09-06, addendum D1_11 to decision pi_reexploration_d1_authorization_20260906)

Presented options: (a) K = 16 (~+15% Stage-1 eval V100-h, the frozen conservative rule's
output `none_in_set`) vs (b) K = 8 (functional-statistic + CRN-paired reading; all
endpoint-shaped statistics clear the 10% bar by an order of magnitude at K=8).

**PI chose (a): "用需要算力多的那个" — K = 16 FROZEN.** Contract C2 amended (k = 1..16);
gates G8/G10 updated to 16 draw-records; C16 ledger item (11). The K adjustment window is
closed; K is immutable through D0 and after. Caveat 2 above still applies: if the D0 corpus
generator adds feedback channels, re-run this preflight against it before the freeze.
