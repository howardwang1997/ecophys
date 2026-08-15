# Post-hoc NEMDE RHS tail diagnostic plan

**Fixed before tail IDs/expressions were inspected:** 2026-08-15T07:19:00Z

**Parent result commit:** `12c53172767f61ea42ef40956f425eea9fb11633`

## Status and purpose

This is a descriptive, explicitly post-hoc diagnostic of the two already consumed cases. It cannot change
`PARTIAL_INPUT_SIDE_DYNAMIC_RHS_RECONSTRUCTION`, relax the frozen p95 limit, remove any equation from a denominator
or authorize a whole-day/full-solver experiment.

The only question is what kind of mechanism creates the observed sparse error tail: unsupported stack/group
execution, unresolved input state, SCADA quality handling, generic-equation expansion or another expression
family.

## Fixed inputs and implementation

- the exact two raw range hashes and XML hashes from the original RHS manifest;
- committed result summary SHA-256
  `704b20a54e8232eda57ebdc4525182c8586b104f400dbdddb0a9aa29c6e57119`;
- clean Nempy commit `2d3cef0e5545c820067fecddfa2e2fd984ac5583` and its frozen source hashes;
- one already validated sentinel document (`-1e100` output RHS); the original dual-sentinel integrity result is not
  rerun or reinterpreted;
- zero AEMO requests, zero new market data and zero GPU-hours.

## Fixed outputs

For each case, report all of the following without individual production or predicted RHS values:

1. counts/fractions above normalized error thresholds `1e-8`, `1e-6`, `1e-4`, `1e-3`, `1e-2` and `0.1`;
2. the top 25 successful equations by normalized error, with constraint ID, absolute/normalized error and an
   expression descriptor;
3. every failed equation, exception type/message and terminal Nempy function/line;
4. direct and recursively expanded operation counts and SPD-type counts;
5. term/group/default/generic-reference/branch counts;
6. unresolved input-term counts under the pinned resolver's documented data sources;
7. referenced SCADA entry counts, multiple-entry IDs, `GoodValues=False`, `EMS_Good=False`, `EMS_Replaced=True`
   and `Can_Use_Value=False` counts;
8. descriptive slices for those binary features, every operation and every SPD type: equation count, original-tail
   count above `1e-3`, tail fraction, median/p95/max normalized error.

Top-error ties are broken by constraint ID. Quantiles retain linear Type-7 interpolation. Every successful
equation with a production reference stays in aggregate denominators; every exception is preserved.

## Prohibited analyses

- no new accuracy threshold, pass/fail label or “near pass” label;
- no equation removal, winsorization, robust-only headline or median substitution;
- no production RHS used as an input or repair target during evaluation;
- no code patch to Nempy in this diagnostic;
- no fresh interval, full day, solver, EcoMD, Experiment 156 or GPU job;
- no individual raw RHS, SCADA value or XML content in Git.

## Decision use

The diagnostic may nominate one concrete input-only repair hypothesis. It cannot validate that hypothesis. Any
repair must be implemented in a separate protocol and evaluated on fresh mechanically selected intervals with
thresholds frozen before their RHS values are opened. If the tail is diffuse or depends on production-only state,
the input-only replay route remains blocked.
