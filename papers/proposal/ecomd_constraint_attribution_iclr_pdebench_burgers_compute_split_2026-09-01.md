# PDEBench Burgers outcome-blind two-V100 compute split

Frozen 2026-09-01 NZST while the exact public file was still downloading, before the data-admission
result and before any Burgers model preflight or formal run.

If and only if the frozen data gate passes and a model snapshot/decision is subsequently validated,
formal seeds are partitioned by identity rather than runtime or outcome:

- V100a (`100.80.236.112`): seeds 4000--4014;
- V100b (`100.123.220.57`): seeds 4015--4029.

The partitions are disjoint and their union is exactly the already frozen set 4000--4029. Seed
3999 remains the sole excluded CUDA preflight and runs on V100b. Both hosts must use the same
dataset SHA-256, data-lock SHA-256, executable snapshot, Git provenance, model settings, four
trained mechanisms, and evaluation grid. If V100a remains occupied by the advection factorial,
its half waits; no seed moves between workers.

Each worker writes a separate append-only JSONL and checkpoint directory. After both halves reach
75 records, the files are copied locally with remote/local SHA-256 receipts. The merger preserves
every JSON line byte-for-byte, rejects duplicate or missing seed/mechanism pairs, and orders records
only by seed and the fixed mechanism order `free`, `projection`, `free_res`, `hard_abs`, `hard`.
The combined 150-record file alone enters the frozen factorial analyzer.

Frozen scheduler and merger identities:

- `scripts/launch_constraint_iclr_pdebench_burgers_factorial_distributed.py` SHA-256
  `80f7410953077d728d476e63b62451f431f6d6e7b8b59fed87969e3603d9520a`;
- `scripts/merge_constraint_iclr_pdebench_factorial.py` SHA-256
  `5a357fff8f7840a2a7d2f855fe6c30ca418e0bbd6e02209aac89772328a3a93d`.

This changes only scheduling and deterministic assembly. It does not change a scientific factor,
seed, threshold, stopping rule, or analysis, and it cannot be revised from partial metrics.
