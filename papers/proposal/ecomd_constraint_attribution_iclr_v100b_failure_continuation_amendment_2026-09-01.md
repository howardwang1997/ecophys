# ICLR confirmation V100b failure-continuation amendment

Frozen: 2026-09-01 NZST (`2026-09-01T05:10:10Z`), after the first locked B-Burgers
job failed at the strict JSON append gate and before any synthetic confirmation metric value was
read or analyzed. The PI authorized execution under the publication-priority plan in interactive
chat.

## Immutable parents

- current-machine decision:
  `research/discovery/decisions/constraint_attribution_iclr_confirmation_20260831.yaml`, SHA-256
  `9d6e1e67cc0055b719c1b904f266123e29b9b31f1f24008a58bafbc8ea49dace`;
- confirmation snapshot SHA-256:
  `b70c000cdd1c70d676ce1846f74e66d147bcd8a03a0fc0a84564e8e0cbbb1305`;
- final ID-only selection lock SHA-256:
  `5100ae5ca6f757a5166fba3692fd912e19e7a0c7a4da65980488e92a402c604e`;
- earlier A-Burgers amendment:
  `research/discovery/decisions/constraint_attribution_iclr_failure_continuation_20260831.yaml`,
  SHA-256 `52619d431b5671205a1a4976c6174b49e7b63c5debd7cdd955d5481f4c80b324`;
- B-Burgers incident:
  `experiments/constraint_attribution_iclr/deployment/v100b_bburgers_nonfinite_incident_20260901.yaml`,
  SHA-256 `89a3fe99f57b56e58c9de248496f76a03c548a85bbcc75f2e3455d0460f7e40b`.

## B-Burgers disposition

The first B-Burgers job was the unchanged locked cell `free`, capacity 16, 400 epochs, learning
rate 0.001, seed 1000. Training/evaluation reached record construction, but strict JSON
serialization rejected at least one non-finite numeric field. The runner printed no metric value,
the output remains zero bytes, and no partial record was recovered.

B-Burgers is permanently `failed_incomplete` in this confirmation. Preserve its zero-byte output
and all logs. Do not retry, repair numerics, change the grid/model/hyperparameters, replace the
seed, or infer an effect from the absence of records. This is symmetric with the already frozen
A-Burgers scientific disposition, while recording that B-Burgers had one attempt rather than two.

## Outcome-blind C-ad2d continuation

The only authorized V100b work is the previously unstarted `C:ad2d` system from the same lock.
The executable allowlist is
`configs/constraint_iclr/confirmation_manifest_v100b_c_continuation_20260901.yaml`, SHA-256
`052d4719542d6b5a0fe1ae8f3498e5c2baa486a2bee39a0d0ef479d626a0d823`.
It contains the same six selected mechanism/cell jobs, seeds 1000--1029, and therefore 240
expected records including derived projection controls. Existing V100b outputs remain append-only;
run-ID skipping is required. No A, B, H, or M2 job is in the continuation manifest.

## Amended completeness and inference gate

After C-ad2d reaches exactly 240 valid records, the formal synthetic block consists of eight
complete systems:

`A:advection`, `A:diffusion`, `B:advection`, `B:diffusion`, `C:ad2d`,
`H:contraction_near`, `H:contraction_strong`, and `M2:fifo_cda`.

`A:burgers` and `B:burgers` must both be disclosed as deterministic/numeric
`failed_incomplete` systems and excluded from every effect estimate, p-value, equivalence decision,
multiplicity family, and aggregate success denominator. The analyzer may run exactly once only
after coverage, uniqueness, provenance, lock binding, finiteness, and the two incident artifacts
all pass. Claims must be system-specific; eight complete systems cannot be described as all frozen
systems.

This amendment changes only failure accounting, the V100b allowlist, and the completeness count.
It does not open any model outcome, alter a scientific setting, or license a result-driven stop.
