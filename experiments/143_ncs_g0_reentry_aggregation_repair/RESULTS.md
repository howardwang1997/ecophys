# Experiment 143 result

**Decision:** `PASS_AGGREGATION_REPAIR`

**Scientific status:** `NO_ADMISSIBLE_REAL_CANDIDATE`; Plan v4 G0 remains FAIL.

## Provenance

- Preregistration commit: `b54bb2d05`.
- Repair implementation commit: `24c3f058c60d20886e7260f476cc6f0f2caec544`.
- Freeze/formal source commit: `a36fb3ae3a0238f93c51a23634ca7ec37e42767e`.
- Raw result SHA-256: `56084cbca83a8328804864660f08b90f23a077b85df4f83a4ad93e5bea4c0b32`.
- Reused fixture SHA-256: `6da9c773512a7b7c642e8ef7c0ba1e231a59c720c8ba9a83618299660d19bf2e`.
- Unchanged candidate-contract SHA-256: `96aed45ceba1e7c98bc3648c036c7302364bb4799ad0c6b2d9cd657c2a0a0f8e`.
- Frozen exp142 runner SHA-256: `3538ab7633e5a0a460e4bd7c88928637f505107d9ec0b4a1c05e024663f49d44`.

## Frozen gate results

All ten preregistered positive predicates passed:

| Gate | Result |
|---|---|
| Exact expected outcomes for all eight cases | PASS |
| Semantic hash invariance | PASS |
| No automated novelty PASS | PASS |
| No `PASS` candidate state | PASS |
| No real candidate in fixtures | PASS |
| No market data read | PASS |
| No sealed period opened | PASS |
| No GPU usage | PASS |
| Positive-only gate namespace | PASS |
| Frozen parent inputs | PASS |

The parent exp142 `FAIL_PROCESS_VALIDATION` was reproduced rather than rewritten. Both differently ordered
hypothetical manifests again shared semantic SHA-256
`a29bbf74fd20e47bf80f2de529e4eef03f0254681052763341f8033924413343`. Every case preserved its exp142 status and
reason codes.

## What was repaired

Raw resource observations now live outside the gate mapping. Zero market files, zero sealed periods and 0.0
GPU-hours map to the positively named predicates `no_market_data_read`, `no_sealed_period_opened` and
`no_gpu_usage`, each true. The aggregator rejects mappings containing an `actual_*` key or a non-literal boolean,
so the exp142 inversion cannot recur through the same interface.

## What this establishes

1. The Plan v4 re-entry contract deterministically rejects the declared v0 composition, performance/application
   novelty, incomplete theorem obligations, EcoMD-only evidence, premature data/GPU requests and unknown fields.
2. Canonical candidate hashing ignores irrelevant mapping and collection order for the frozen fixture.
3. The automated state machine can route a structurally complete document to human audit but cannot emit novelty
   PASS.
4. The corrected experiment-level aggregation obeys the frozen resource policy.

## What this does not establish

No fixture contains new mathematics. The review-ready object is deliberately hypothetical, and its primary-source
rows are structural test data rather than an audited non-equivalence finding. Exp143 therefore does not reopen G0,
authorize an estimator implementation, justify V100 work, update NCS probability or support a manuscript claim.

The next NCS-method action requires an actual theorem/identity and non-equivalence witness written independently of
this validator. In parallel, Plan v4's allowed zero-cost fallback is the frozen state-to-message observation map and
cross-defect simulator audit; neither can be counted as method novelty.

## Repository integration verification (not part of the formal run)

The immutable exp143 result was not rerun after repository integration. The branch-level verification performed
afterward established the following:

- pytest collected 659 tests. The 658 tests other than the existing 64-step checkpoint smoke test passed in
  resource-bounded file shards; the 38 tests covering the changed G0, checkpoint and dynamic-graph paths passed
  together on the final implementation.
- The checkpoint smoke test's old `N=200` setting was not a bounded CI check: it was killed on both the Mac and the
  46 GiB RTX2060 worker, where the kernel recorded 44,389,788 kB anonymous RSS. Commit `2ba695d34` changed only the
  smoke-test scale to `N=64` and registered the `slow` marker. The same 64-step forward/backward path then passed in
  5.98 s locally and 7.89 s on the RTX2060 host with CUDA hidden and four CPU threads.
- The remote compatibility check used a dedicated Conda clone with PyTorch 2.6.0. Its working copy was based at
  `8caadc272` with the exact current files copied in, so it was intentionally dirty rather than represented as a
  clean commit. SHA-256 values were `e792b230...` for `ecomd/models/ecomd.py`, `308a902b...` for the test and
  `5901dae8...` for `pyproject.toml`.
- Strict mypy passed all 91 `ecomd` source files. Diff-relevant Ruff checks (`E4,E7,E9,F,I`) passed. A full-repository
  Ruff scan still reports 876 inherited findings after expanding the sparse checkout; this branch does not claim
  to have repaired that unrelated lint backlog.

The explicit checkpoint import and semantic dynamic-graph regression guard are recorded in `a4f350b73`. These
integration repairs do not change the exp143 gate outputs or its scientific interpretation.
