# PDEBench v2 deployment gate

Recorded: 2026-09-01 NZST, after v2 data admission and before any CUDA/model run.

## Immutable identities

- V2 protocol SHA-256: `01d300410364b07e779c2c2462cdd60f720a24a86622675f4df0f7c604724307`.
- Data lock SHA-256: `78705fc8f0c342bc5f937756fce93ab60c660acbb24d15a5ea90a620f7890687`.
- Dataset SHA-256: `d973ff2bb3c2a5edf42957ff029b78672451532ebd6bf475848ff23cfd3ee3b6`.
- Snapshot:
  `experiments/constraint_attribution_iclr/deployment/constraint_iclr_pdebench_v2_snapshot_20260901.tar.gz`.
- Snapshot bytes: 34,764.
- Snapshot SHA-256: `6392bb2a7b217e06e9d79ffde55afd57612d2cc9c815f130ccc6eeccc0078970`.
- Archive contents: 17 hash-listed files plus the per-file SHA-256 manifest. Clean-room extraction
  passed all 17 checks.

The v2 data gate passed at all factors. Maximum target-mean drift is below `4.47e-7`; maximum
block-restriction/native mean discrepancy is below `1.32e-8`. Frozen limits are `1e-5` and `1e-6`.
The v1 failed-admission artifact remains included and v1 has zero model records.

## Local gates

- 19/19 focused PDEBench tests pass, including block-average algebra, streaming HDF5 loading,
  FNO arm parameter equality, hard conservation, projection identity, checkpoint resume plumbing,
  full synthetic runner smoke, data-lock binding, analyzer pairing, and launch construction.
- Ruff passes on every included new script/test.
- The preflight dry-run includes only excluded seed 1999, 64 training trajectories, one epoch,
  eight excluded evaluation trajectories, and horizon one.
- No PDEBench model outcome exists at this gate.

## Remote activation

Prefer `howardwang@100.105.21.7` only if it becomes reachable and its RTX 2060S is idle. Otherwise
wait for either V100 to finish its existing synthetic worker naturally; never interrupt or
colocate. Remote roots are respectively
`/home/howardwang/ecophys_constraint_iclr_pdebench_v2_20260901/` and
`/root/ecophys_constraint_iclr_pdebench_v2_20260901/`.

For the selected idle host:

1. copy the exact snapshot, verify archive SHA-256, extract, and pass all per-file hashes;
2. stage the exact dataset by official download or verified transfer, then require byte, MD5,
   SHA-256, schema, finiteness, and v2 data-lock agreement;
3. use the host's existing Conda Python, install `h5py>=3.11` only if absent, and pass 19 tests;
4. set `ECOPHYS_GIT_HEAD=86dd76ee0127c5eb7945a5806bdad74548c62459` and `ECOPHYS_DIRTY=1`;
5. run the excluded seed-1999 CUDA preflight. Require correct GPU provenance, five finite records,
   equal trained parameter counts, exact lock/protocol/amendment hashes, factor restrictions,
   target invariant, and horizon-one projection identity; do not use its metric magnitude;
6. only after the preflight passes, launch formal seeds 2000--2029 under one exclusive GPU lock.

Formal output is append-only and expected to contain exactly 150 records. Monitoring may inspect
only process health, GPU/memory/disk, counts, run-ID coverage, hashes, provenance, pairing,
finiteness, and algebraic booleans. Partial metric values and the frozen analyzer remain forbidden.

