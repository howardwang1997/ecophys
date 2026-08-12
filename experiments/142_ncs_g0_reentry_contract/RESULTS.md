# Experiment 142 result

**Decision:** `FAIL_PROCESS_VALIDATION`

**Scientific status:** `NO_ADMISSIBLE_REAL_CANDIDATE`; Plan v4 G0 remains FAIL.

## Provenance

- Plan commit: `fd99b1262`.
- Contract implementation commit: `f33db765f`.
- Preregistration/fixture/runner commit: `48db22ef2f081d11faf1ca8c6aa05580eed0b167`.
- Fixture SHA-256: `6da9c773512a7b7c642e8ef7c0ba1e231a59c720c8ba9a83618299660d19bf2e`.
- Runner SHA-256: `3538ab7633e5a0a460e4bd7c88928637f505107d9ec0b4a1c05e024663f49d44`.
- Raw result SHA-256: `ec41af58e886d111b5fdedb5c5ce12de57d3f8ebda19dc762d427741ef4671db`.
- Execution environment: Mac CPU, Conda `ecophys`; zero market files, zero sealed periods and zero GPU-hours.

## Case-level results

All eight controlled cases exactly matched their preregistered status, reason-code list and schema-error condition.
The two semantically identical, differently ordered hypothetical manifests shared candidate SHA-256
`a29bbf74fd20e47bf80f2de529e4eef03f0254681052763341f8033924413343`. No case emitted an automated novelty PASS,
and the status enum has no `PASS` state.

| Case | Frozen outcome | Match |
|---|---|---|
| Review-ready hypothetical | `READY_FOR_HUMAN_AUDIT` | yes |
| Reordered review-ready hypothetical | `READY_FOR_HUMAN_AUDIT` | yes; same semantic hash |
| Rejected v0 composition | `REJECTED_EQUIVALENT` | yes |
| Performance-only EcoMD proposal | `REJECTED_EQUIVALENT` | yes |
| Incomplete new label | `INCOMPLETE` | yes |
| EcoMD-only formal claim | `ECO_MD_ONLY` | yes |
| Pre-G0 resource violation | `INCOMPLETE` | yes |
| Unknown schema field | schema error | yes |

## Why the overall process gate failed

The runner represented the desired observation “no market data was read” as
`actual_market_data_read: false`, then computed the overall decision with `all(gates.values())`. The false
observation was therefore treated as a failed pass predicate even though it denotes policy compliance. All other
gate values were true. This is an aggregation-semantics bug, not a candidate-assessment or scientific failure.

The frozen exp142 JSON is not edited and exp142 is not rerun. Its FAIL remains the formal result. A repair must use
a new experiment number, rename every aggregate field as a positive pass predicate, preregister the exact mapping
and verify that no raw observation is directly folded into the decision.

## Scientific consequence

Exp142 neither provides nor rejects a new mathematical method: it contains no real candidate. The useful result is
that the candidate contract correctly rejects the old composition and common laundering paths at case level, while
the experiment-level aggregator needs repair. Candidate implementation, V100 runs, market data and NCS claims stay
blocked.
