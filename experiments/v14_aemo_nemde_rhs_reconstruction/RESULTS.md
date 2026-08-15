# AEMO NEMDE input-side dynamic-RHS reconstruction result

**Decision:** `PARTIAL_INPUT_SIDE_DYNAMIC_RHS_RECONSTRUCTION`

**Protocol commit:** `8a26320a3b2c1755e873d9c96d06a5196cf45ede`

**Summary SHA-256:** `704b20a54e8232eda57ebdc4525182c8586b104f400dbdddb0a9aa29c6e57119`

## Bottom line

The leakage-control and coverage results are strong, but the frozen accuracy gate failed in both cases. Nempy's
input-side evaluator produced exactly the same success/error outcome and exactly the same successful float under
`-1e100` and `+1e100` output-RHS sentinels. It evaluated 772/774 and 882/884 dynamic equations, with complete
production-reference coverage. Median normalized error was far below the frozen `1e-8` limit.

However, normalized p95 error was `0.00416664` before 5MS and `0.00194488` after 5MS/WDR, both above the frozen
`0.001` ceiling. The immutable result is therefore partial, not pass. A one-day alignment/replay gate, full
input-only replay claim and every GPU/model downstream remain locked.

## Provenance and integrity

- Both exact prior ranges were materialized from R2; new AEMO request count was zero.
- Each remote/local object reproduced its frozen 1 MiB size and SHA-256.
- Local ZIP member metadata, raw-deflate EOF, uncompressed size, CRC and prior XML SHA-256 all reproduced.
- The Nempy checkout was clean at commit `2d3cef0e5545c820067fecddfa2e2fd984ac5583`; both audited source hashes
  matched.
- Every output `ConstraintSolution/@RHS` was replaced independently in both sentinel documents before engine
  construction. No equation was filtered, repaired or retried.
- Integrity decision: pass. Materialization receipt SHA-256:
  `7e475dd334ac5f3005cab2135b4e21206d7d51db8c6e0555ef4bc25a2ebbaba6`.

## Frozen metrics

| Metric | 2021-01-01 pre-5MS | 2021-12-01 post-5MS/WDR | Gate |
|---|---:|---:|---:|
| dynamic equations | 774 | 884 | at least 1 |
| scored equations | 772 | 882 | — |
| reference coverage | 1.000000 | 1.000000 | 1.000000 |
| evaluation coverage | 0.997416 | 0.997738 | at least 0.95 |
| sentinel outcome match | 1.000000 | 1.000000 | 1.000000 |
| sentinel successful-value match | 1.000000 | 1.000000 | 1.000000 |
| median normalized error | `4.11044e-10` | `1.34254e-10` | at most `1e-8` |
| p95 normalized error | `0.00416664` | `0.00194488` | at most `0.001` — **failed** |
| p99 normalized error | `0.988812` | `0.00668113` | report only |
| maximum normalized error | `0.996800` | `0.500001` | report only |

Two equations per case raised `IndexError` under both sentinels:

- pre-5MS: `Q_NIL_STRGTH_MEWF`, `S_NIL_STRENGTH_1`;
- post-5MS/WDR: `DSNAP_T_ROCOF_3`, `N^^N_NIL_3`.

Their identical failure under both sentinels supports leakage isolation but counts against evaluated coverage as
pre-registered.

## Interpretation

The experiment establishes that realized production RHS is not needed for the vast majority of these two dynamic
equation evaluations. It does not establish production equivalence. The very small median and much larger upper
tail indicate a sparse mismatch regime that is scientifically important: using production output RHS in a
standard historical recreation can conceal precisely those difficult constraints.

The result must not be “rescued” by relaxing p95 from `0.001`, deleting outliers or reporting median alone. A
descriptive diagnostic may use these already consumed cases to classify tail errors by equation operation and
missing input state. Any repair must be frozen separately and validated on fresh mechanically selected intervals.

## Claim boundary

Supported:

- the two retained objects and pinned engine passed provenance/integrity checks;
- successful dynamic-RHS predictions are invariant to two extreme output-RHS sentinels;
- input-side evaluation coverage is above 99.7% in both development cases;
- the frozen accuracy criterion did not pass.

Not supported:

- validated input-side dynamic-RHS equivalence;
- full input-only NEMDE replay, prices, targets, flows or binding-set fidelity;
- counterfactual rule execution, participant adaptation, causality or EcoMD;
- Experiment 156, learned surrogate training or any GPU job.

## Resources

- new AEMO requests: 0;
- R2 materialized bytes: 2,097,152;
- mathematical solver: none;
- GPU-hours: 0;
- paid-data spend: 0.

## Next admissible action

Freeze no new success threshold. Run a clearly post-hoc, descriptive audit on these consumed cases that reports
the complete tail-error IDs, expression operations, referenced SPD types and error concentration. If it identifies
a concrete input-only repair, preregister that repair on fresh deterministic intervals before reopening results.
Until such a fresh test passes, do not download a whole day or run a full solver.
