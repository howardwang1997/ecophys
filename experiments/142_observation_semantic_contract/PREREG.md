# Experiment 142 — observation-semantic contract firewall

**Frozen:** 2026-08-10, after the static field audit at commit `5aaa4013`, but before the contract module,
formal fixtures, runner or result file exists

**Status:** F1 machine-enforcement preflight only; the real message/order-level route already FAILed, while
`aggregate_bin` + P3 remains AMBER

**Cost boundary:** generated deterministic fixtures only; Mac CPU in the `ecophys` Conda environment; no real
archive, held-out data, fitting, GPU, purchase, H20 or compute expansion

## Question and claim boundary

Can a versioned, machine-readable contract reject every currently known mismatch between a simulator path and
the external observation claim *before* a fitting callback can run, while accepting the current adapter only
as a synthetic fixture and accepting a narrowly specified aggregate-bin P3 design?

A PASS establishes only that the repository can enforce the frozen support vocabulary and known prohibitions.
It does not show that aggregate-bin observables fit real markets, that the declared measurement model is
identified, that a causal latent filter works, that the audit framework is novel, or that EcoMD contains real
market physics. A validator cannot establish truth from self-declaration; implementation attestations and
external tests remain later gates.

## Information inspected before freezing

- Exp136 established exact continuation and self-generated recovery for one event per EcoMD transition.
- Exp137 added dynamic queue/price synthetic baselines, but its latent is exogenous and its price is not linked
  to EcoMD's internal price.
- Exp138 validated an external six-mark projection and causal queue/Hawkes evaluator without an EcoMD latent.
- The frozen field audit found that `EcoMDL2Adapter` uses a deterministic simulator-step clock, model-unit
  sizes, a new integer for every event including removals/executions, and a book price independent of EcoMD's
  internal price. The repository has no frozen causal inference rule from past real observations to EcoMD
  latent state.

No contract implementation, generated fixture output or prospective gate result was inspected before this
freeze. Exp141 is intentionally unused because the prior numerical-work log reserved it as a stopped rerun.

## Frozen schema

The implementation must use immutable typed records and JSON-safe enum values. The top-level contract contains
exactly these semantic groups; implementation-only names may differ, but the serialized keys and values must
be documented in the result:

1. `schema_version` and a human-readable declaration name;
2. `support_level`: `synthetic_fixture`, `aggregate_bin`, `aggregate_event` or `individual_order`;
3. `data_scope`: generated or external;
4. clock kind, count law and optional positive seconds-per-step/bin;
5. price choice P1/P2/P3, scored price processes and whether a train-only measurement link exists;
6. latent-size unit, observed-size unit and train-only measurement/conversion status;
7. output identity field, event/order semantics, persistent lifecycle and matching/priority capability;
8. latent source label, access rule, directional sign anchor, model-input role and required negative controls.

Validation returns a deterministic sorted tuple of stable error codes and a sorted tuple of warnings. It must
never infer a higher support level from field names. JSON serialization must reject unknown keys and values;
round-tripping must preserve the canonical payload exactly.

## Frozen positive declarations

Exactly three positive fixtures are required:

1. **Current adapter / synthetic only.** `synthetic_fixture`, generated scope, simulator-step clock, exactly one
   event per transition, emitted-book price only, model-unit size, and the existing `order_id` field explicitly
   declared an event counter/schema placeholder. It must validate with the warning
   `SYNTHETIC_ORDER_ID_IS_EVENT_COUNTER`; no external equivalence is implied.
2. **Aggregate-bin P3.** External aggregate bins at a fixed 60-second width; binned mid returns, observed
   shares/contracts and aggregate counts; train-only measurement links from EcoMD return/volume predictors;
   no event/order identity; unconditional train-calibrated simulation or a causal filter only;
   `latent_flow_alignment` retains its latent name. Its frozen controls contain both `sign_flip` and
   `observation_only`. It must validate without errors or warnings.
3. **Structurally admissible aggregate-event P2 fixture.** External aggregate events with a conditional event
   intensity, emitted-book price as the sole scored price process, train-only size mapping, `event_id`, causal
   latent access and both frozen controls. It must validate without errors or warnings. This fixture is a schema
   example, not an assertion that the corresponding emitter exists.

No positive individual-order fixture is required because EcoMD lacks the implementation evidence. A contract
that merely asserts a matching engine would not establish that capability.

## Frozen single-defect mutations and error codes

Each mutation starts from the closest valid positive declaration and changes only the named semantic fact.
It must fail with the exact primary code shown; additional codes fail the isolation gate.

| Case | Single mutation | Exact error code |
|---|---|---|
| N1 | external aggregate-event clock changed to exactly one event per simulator transition | `EXTERNAL_EVENT_CLOCK_REQUIRES_CONDITIONAL_LAW` |
| N2 | both EcoMD internal and emitted-book prices scored under P2 with no measurement link | `DUAL_PRICE_PROCESS_WITHOUT_LINK` |
| N3 | aggregate-bin width removed | `AGGREGATE_BIN_REQUIRES_PHYSICAL_SECONDS` |
| N4 | aggregate-event `event_id` changed to `order_id` while retaining event-counter semantics | `EVENT_COUNTER_MUST_NOT_BE_ORDER_ID` |
| N5 | support raised to individual order without lifecycle/matching/priority capability | `INDIVIDUAL_ORDER_CAPABILITIES_MISSING` |
| N6 | external observed size relabeled shares while the train-only model-to-market mapping is removed | `MARKET_SIZE_REQUIRES_TRAIN_ONLY_LINK` |
| N7 | `latent_flow_alignment` relabeled empirical OFI | `LATENT_PROXY_MUST_NOT_BE_LABELED_OFI` |
| N8 | fixed structural sign anchor changed to sign-flipped for a directional latent claim | `DIRECTIONAL_SIGN_CONTRADICTS_ANCHOR` |
| N9 | latent access changed to test-conditioned | `TEST_CONDITIONED_LATENT_FORBIDDEN` |
| N10 | model inputs changed to observation-only while retaining a latent-incremental claim | `LATENT_CLAIM_REQUIRES_LATENT_INPUT` |
| N11 | `sign_flip` removed from controls for a directional latent claim | `SIGN_FLIP_CONTROL_REQUIRED` |
| N12 | `observation_only` removed from controls for a latent-incremental claim | `OBSERVATION_ONLY_CONTROL_REQUIRED` |

The validator may report warnings for valid synthetic fixtures, but no mutation may be rescued by downgrading
the requested support internally. The caller must submit a new explicit lower-support declaration.

## Frozen current-adapter runtime probe

Use root seed `142202608`, 256 finite latent-alignment values drawn uniformly on `[-1,1]`, the default adapter
book depth and an adapter configuration chosen before running to give positive probability to both adds and
removals. The probe may instantiate `EcoMDL2Adapter`; it may not run EcoMD, fit a likelihood or read external
data. It records:

- emitted row count versus latent-step count;
- exact timestamp increments and configured `dt`;
- uniqueness/contiguity of the current `order_id` field;
- how many cancellation/deletion/execution rows refer to an ID observed in a prior row;
- the declared price source and size unit.

The expected structural facts are 256 rows, one row per latent step, exact fixed-step timestamps, 256 unique
consecutive IDs, and zero removals/executions referencing a previous ID. These facts must be reported, not
treated as external-validity success. If the frozen seed produces no removal/execution, the experiment fails;
the seed cannot be replaced.

## Frozen fit firewall

Provide one public wrapper that validates a contract before invoking a supplied callback. For every N1--N12
mutation, a counting callback must be invoked zero times and the exact validation failure must escape. For each
positive declaration, it must be invoked exactly once and return an unchanged sentinel. Catching an error and
continuing to fit fails.

## Frozen hard gates

1. **Chronology/provenance:** preregistration commit precedes implementation; formal result records protocol
   hash, implementation git SHA, dirty flag, Conda environment and Python/package versions.
2. **Schema determinism:** all three positives and twelve mutations round-trip through strict JSON; canonical
   JSON and repeated validation are byte/deterministically identical; unknown keys/enums are rejected.
3. **Positive scope:** the three positive declarations have exactly the errors/warnings specified above.
4. **Mutation isolation:** all N1--N12 mutations return exactly their frozen single error code; none passes or
   adds an unrelated secondary failure.
5. **No silent support escalation:** changing only the current-adapter support/data scope to each external
   level (`aggregate_bin`, `aggregate_event`, `individual_order`) fails; the validator preserves the requested
   level in the returned report.
6. **Fit firewall:** invalid callbacks run zero times; valid callbacks run exactly once and preserve the
   sentinel result.
7. **Adapter probe:** every frozen structural fact above is reproduced and all probe values are finite.
8. **Code quality:** focused pytest passes; Ruff passes on changed Python; strict mypy passes on the contract
   module and formal runner.
9. **Complete reporting:** canonical declarations, warnings/errors, all mutations, callback counts, adapter
   probe, hashes, environment, runtime and peak RSS appear in `SEMANTIC_CONTRACT_RESULTS.json` and the human
   result report. Missing or post-hoc excluded cases fail.

All nine gates are required. Error codes, fixtures and pass criteria cannot change after any formal output is
inspected. A code defect discovered by smoke requires a fix and clean implementation commit; the formal run is
performed once from that commit.

## Execution and interpretation

Use `conda run -n ecophys python experiments/142_observation_semantic_contract/run_contract.py` with one CPU
thread. Expected cost is under two CPU core-hours and 2 GiB RAM; in practice it should finish in minutes. The
formal runner must reject an uncommitted implementation, but may write its result into the then-clean tree.

A PASS promotes only the `aggregate_bin` + P3 semantic design from AMBER to a code-enforced specification. The
next F1 experiment must implement the aggregate-bin observation object and exact synthetic reconstruction; a
separate later preregistration is required before any real-data fit. A FAIL closes the observation bridge until
a new versioned schema and independent protocol are frozen; it must not be bypassed by using exp136 terminology.
