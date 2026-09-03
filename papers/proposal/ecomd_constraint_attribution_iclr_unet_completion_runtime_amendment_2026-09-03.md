# U-Net replication completion runtime amendment

Registered 2026-09-03 NZST after V100-A had exited with exactly 75 append-only core
records for seeds 7000--7014, while V100-B still had zero records because its immutable
PDEBench file transfer had stopped at 634,521,600 of 8,232,966,952 bytes. No partial
training metric was read, the core analyzer had not been run, and no U-Net enforcement-cube
record existed.

The frozen U-Net protocol already requires exactly 150 core records, a one-shot core
analysis, a lock over 120 parent checkpoints, and exactly 90 zero-training inference-toggle
records. The deployed snapshot contained the core runner and analyzers but omitted a
config-aware shard merger, an exact checkpoint-transfer package, and a cube configuration
capable of accepting the registered 7000--7029 seed universe. The V100-B watcher also waited
for the dataset byte count without owning or resuming the transfer. These are runtime and
integrity defects, not scientific outcomes.

This amendment authorizes only the following outcome-blind repairs:

1. resume the exact immutable dataset transfer to V100-B and require the frozen byte count
   and SHA-256 before training can start;
2. package each completed 75-record worker shard with exactly its 60 referenced final
   checkpoints, a canonical manifest, and an archive SHA-256 sidecar;
3. merge only the two registered shards, requiring exact seed-by-mechanism coverage and the
   frozen U-Net benchmark identifier;
4. generalize the existing cube runner's formal seed guard and source-config provenance so
   it accepts an explicitly registered `formal_seed_universe`, while retaining the historical
   3000--3029 default; and
5. run the existing factorial and cube analyzers only after their respective exact coverage,
   checkpoint, provenance, and finite-value gates pass.

V100-A remains assigned seeds 7000--7014 and V100-B remains assigned 7015--7029. No seed,
architecture, checkpoint, split, resolution, horizon, metric, SESOI, bootstrap rule,
classification rule, or admission rule changes. No third GPU, retraining of completed arms,
checkpoint substitution, partial metric access, early analysis, or result-contingent stopping
is authorized. The completed V100-A shard is preserved byte-for-byte before operational work.
