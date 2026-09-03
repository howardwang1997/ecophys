# ICLR enforcement-cube checkpoint-lock runtime amendment

Registered 2026-09-01 NZST while the fresh Advection factorial had 94/150 append-only
records, with both workers alive, before any partial metric was accessed, before the parent
factorial analyzer was run, and before any enforcement-cube record existed.

The frozen cube protocol requires every derived evaluation to bind the exact trained parent
checkpoint. The parent factorial records contain the checkpoint path and parent run ID, but the
original runner did not store a checkpoint byte hash inside each record. This implementation-only
amendment specifies the missing integrity artifact without changing an estimand, seed, cell,
metric, threshold, or interpretation.

After the core JSONL reaches exactly 150 valid records and its frozen analyzer passes, the cube
runner must create one canonical checkpoint lock before evaluating a derived cell. The lock must:

1. bind the SHA-256 of the complete core JSONL and its completed frozen analysis;
2. enumerate exactly the 120 trained parent run IDs (`free`, `free_res`, `hard_abs`, and `hard`)
   with the checkpoint path copied from the corresponding parent record;
3. verify each checkpoint payload's parent run ID, schema, and frozen completed epoch count;
4. record the checkpoint file byte count and SHA-256; and
5. be written atomically and treated as immutable. If a lock already exists, regeneration is
   forbidden unless its canonical contents are byte-identical.

Every derived record must bind the checkpoint-lock SHA-256 and repeat its parent's checkpoint
path and SHA-256, parent run ID, training-index digest, initialization digest, and a canonical
SHA-256 of the parent provenance object. Before loading weights, the runner must re-hash the
checkpoint and compare it to the lock. The analyzer must verify all of these bindings against the
complete parent records and checkpoint lock.

The three derived forward-map interventions and all inferential rules remain exactly those in the
parent cube freeze. This amendment cannot authorize retraining, checkpoint repair, metric access
before complete coverage, or replacement of a failed raw hard-trained rollout.
