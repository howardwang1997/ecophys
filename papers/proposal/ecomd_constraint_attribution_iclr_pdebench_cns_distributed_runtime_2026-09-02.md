# CNS formal-worker partition runtime registration

Registered on 2026-09-02 before the fixed public CNS file completed download and before any value
or metric from it was read. This is an execution-only registration for the already frozen formal
experiment; it changes no scientific factor, seed, split, model, optimizer, horizon, metric, or
analysis rule.

The formal seed universe remains exactly 5000--5029. It is partitioned once into two disjoint
worker shards:

- `v100a`: seeds 5000--5014;
- `v100b`: seeds 5015--5029.

Each worker must train all four paired mechanisms for every assigned seed and emit the derived
post-hoc projection from the same `free` checkpoint. Thus every seed stays wholly within one
worker and retains matched training indices and initialization. The two shard JSONLs must be
merged byte-preservingly into seed/mechanism order and must cover exactly 30 seeds times five
records before the frozen analyzer can run.

The excluded CUDA preflight uses only seed 4999 and cannot enter the formal merge. Workers may
resume only their own run IDs. A missing, overlapping, substituted, or out-of-range seed is a hard
failure. Worker allocation cannot be revised in response to partial metrics; no partial formal
metric may be read.
