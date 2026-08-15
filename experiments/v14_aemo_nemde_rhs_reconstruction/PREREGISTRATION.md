# AEMO NEMDE input-side dynamic-RHS reconstruction preregistration

**Frozen:** 2026-08-15T06:58:00Z

**Parent:** `eb53bfa4eb02f9b80ebe53c4b876fdd3e927a61f`

**Status at freeze:** unexecuted; neither retained range was rematerialized and no RHS value was opened for this
experiment.

## Question

Can the input-side dynamic generic-constraint equations in two consumed production NEMDE cases be evaluated by a
pinned open implementation without borrowing realized `ConstraintSolution/@RHS` values?

This is a component-feasibility test, not a full NEMDE replay. It is deliberately run before downloading a full
day or installing a mathematical solver.

## Frozen sample

The only cases are interval 144 on 1 January and 1 December 2021. They were selected and consumed by the prior ZIP
inventory/XML-conformance protocols. They cannot become confirmatory observations and cannot be replaced.

The exact 1 MiB range objects already exist under two frozen R2 keys. Their sizes, SHA-256 values, member metadata,
CRCs and decompressed XML SHA-256 values are copied verbatim into
`data/manifests/aemo_nemde_rhs_reconstruction_v1.yaml`. Execution makes exactly zero AEMO source requests. R2
materialization must verify remote metadata and local bytes before a ZIP header or XML byte is opened. Source
fallback and mismatched overwrite are prohibited.

## Frozen external engine

- Repository: `https://github.com/UNSW-CEEM/nempy.git`
- Commit: `2d3cef0e5545c820067fecddfa2e2fd984ac5583`
- Package version: 3.0.3
- Runtime parser: `xmltodict==0.12.0`
- Audited source hashes: `rhs_calculator.py` and `xml_cache.py` as listed in the manifest

The checkout must be clean and every pin/hash must match. This protocol calls only the XML cache and RHS
calculator. It does not import a market solver, run CBC/Gurobi or use MMSDM tables.

## Leakage control

For each case the analyzer performs this fixed sequence:

1. reproduce exact range hash, local-member metadata, deflate EOF, XML size, CRC and prior XML SHA;
2. parse the production document and seal intervention-zero constraint RHS in a reference mapping;
3. create two deep copies and replace **every** output `ConstraintSolution/@RHS` with `-1e100` or `1e100`;
4. construct the pinned `RHSCalc` separately on each sentinel document;
5. attempt every input dynamic RHS equation exactly once, sorted by constraint ID;
6. preserve every exception and nonfinite result;
7. only after predictions exist, score the first sentinel predictions against the sealed references.

No input field may be mutated. No equation may be dropped, repaired or retried. Successful values must be exactly
equal as Python float hexadecimal representations across sentinels, and success/error status must match for every
equation. Individual production/predicted RHS values are not committed to Git.

## Frozen metrics and gates

For equation `i`, normalized error is

`|predicted_i - production_i| / max(1, |production_i|)`.

Quantiles use linear Type-7 interpolation. Each case independently requires:

- at least one input dynamic equation;
- production reference coverage = 100%;
- successfully scored evaluation coverage at least 95%;
- sentinel success/error outcome match = 100%;
- exact value match among dual-success equations = 100%;
- median normalized error at most `1e-8`;
- 95th-percentile normalized error at most `1e-3`.

Both cases must pass every gate for `PASS_INPUT_SIDE_DYNAMIC_RHS_RECONSTRUCTION`. If provenance and sentinel
integrity pass but an accuracy/coverage gate fails, the immutable decision is
`PARTIAL_INPUT_SIDE_DYNAMIC_RHS_RECONSTRUCTION`. Any R2, engine-pin or sentinel-integrity failure gives
`FAIL_INPUT_SIDE_DYNAMIC_RHS_INTEGRITY`. Maximum error is descriptive and cannot change the decision.

## Claim boundary

A pass means only that Nempy reconstructs this dynamic-RHS component on these two development cases without using
the realized RHS answer. It permits the **design** of a one-day schema/output-alignment gate.

It does not validate:

- static constraint construction or a full input-only optimization;
- prices, unit targets, flows, binding sets or counterfactual rules;
- exact production NEMDE equivalence;
- participant submissions, rejected actions, strategy or adaptation;
- EcoMD, Experiment 156 or a learned surrogate.

All V100/2060 jobs, paid data, raw redistribution and downstream causal/model claims remain locked.

## Resources

- new AEMO requests: 0;
- immutable R2 reads: two objects, 2 MiB total;
- compute: local CPU, expected seconds to minutes, less than 1 GB RAM;
- GPU-hours: 0;
- paid-data spend: 0.

## Commands after protocol commit

From a clean detached worktree at the pushed protocol commit:

```bash
conda run -n ecophys python experiments/v14_aemo_nemde_rhs_reconstruction/materialize.py \
  --env-file /Users/howardwang/Desktop/playground/ecophys/.env.r2
conda run -n ecophys python experiments/v14_aemo_nemde_rhs_reconstruction/analyze.py \
  --nempy-root /private/tmp/nempy-audit-20260815
```

The generated credential-free receipt and summary are copied back, validated against the protocol commit and
committed with `RESULTS.md`. Raw ranges and XML are never copied into Git.
