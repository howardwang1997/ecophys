# ICLR confirmation failure-continuation amendment

Date: 2026-08-31, after the deterministic A-burgers failure was reproduced once under the exact
frozen configuration, before any confirmation metric value, pilot OOD value, or confirmation
analysis was accessed.

Parents and immutable identities:

- current machine decision:
  `research/discovery/decisions/constraint_attribution_iclr_confirmation_20260831.yaml`, SHA-256
  `9d6e1e67cc0055b719c1b904f266123e29b9b31f1f24008a58bafbc8ea49dace`;
- confirmation snapshot SHA-256:
  `b70c000cdd1c70d676ce1846f74e66d147bcd8a03a0fc0a84564e8e0cbbb1305`;
- final ID-only lock SHA-256:
  `5100ae5ca6f757a5166fba3692fd912e19e7a0c7a4da65980488e92a402c604e`;
- incident record:
  `experiments/constraint_attribution_iclr/deployment/v100a_aburgers_nonfinite_incident_20260831.yaml`,
  SHA-256 `44f3241022e241b9af2d4fac4f554bc98d34f672c5370dbb9835272347a33d13`.

The PI explicitly approved this minimal revision after the failure and its scope were explained.

## Deterministic failure disposition

The first locked A-burgers confirmation job (`free`, capacity 128, 400 epochs, learning rate
0.001, seed 1000) reached the strict JSON append gate with a non-finite output and wrote no record.
The single identical retry allowed by the parent decision reproduced the same failure. No outcome
metric value was printed or inspected.

A-burgers is permanently classified as `failed_incomplete` for this confirmation:

- preserve the zero-byte output, both logs, their hashes, and the incident record;
- do not attempt a third run;
- do not change the model, numerics, hyperparameters, grid, mechanism, tolerance, or code;
- do not replace, omit selectively, or add a seed;
- do not treat the missing records as zero effects or successful observations.

A-advection and A-diffusion remain completed immutable confirmation systems. The A-burgers failure
does not invalidate their records and does not license a statement about all of family A.

## Outcome-blind V100a continuation

V100a may now run only the following previously unstarted systems from the unchanged final lock:

- `H:contraction_near`;
- `H:contraction_strong`;
- `M2:fifo_cda`.

The executable allowlist is
`configs/constraint_iclr/confirmation_manifest_v100a_continuation_20260831.yaml`. It contains 18
unchanged mechanism/cell jobs and therefore 720 expected JSONL records after the derived projection
controls. It contains no A system. Seeds remain exactly 1000--1029, output remains append-only, and
run-ID skipping remains enabled. The source snapshot, final selection lock, Hydra configurations,
runners, and all scientific settings remain byte-for-byte unchanged.

V100b remains governed by the parent decision and its original frozen manifest. An operationally
interrupted launcher may be resumed only with the identical snapshot, lock, manifest, seeds, and
append-only run-ID skipping; this amendment adds no V100b job and changes no V100b setting.

## Completeness and analysis gate

No analyzer may run until all three continuation systems and all four V100b systems complete and
the usual coverage, provenance, lock-binding, uniqueness, and finiteness gates pass. At that point:

- A-burgers must appear in the audit as unavailable due to a prospectively documented
  deterministic non-finite failure;
- A-burgers contributes no effect estimate, p-value, equivalence decision, multiplicity test, or
  aggregate success count;
- inference is limited to the nine systems with complete records, with system-specific wording;
- the failed system must be disclosed in the paper, limitations, compute accounting, and artifact
  documentation.

This is a failure-handling and execution-allocation amendment only. It does not reopen selection,
inspect outcomes, repair the failed configuration, or broaden any scientific claim.
