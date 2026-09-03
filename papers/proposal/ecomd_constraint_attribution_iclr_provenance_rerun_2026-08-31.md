# ICLR pilot provenance rerun

Date: 2026-08-31, after all pilot compute completed and before the corrected selector accessed any
ID or OOD metric.

## Gate failure

The final raw snapshot contains 5,040 append-only records with matching local/remote file hashes.
The analyzer's provenance gate stopped before cell selection because 510 records lack `git_head`:

- 450 H-near full-grid expansion records;
- 60 C-ad2d learning-rate-correction records.

These are exactly the two jobs launched later as direct commands without the environment variables
used by the original worker launch. Their commands, resolved configs, executable source SHA-256
maps, host/software/GPU metadata, and final file hashes are present, but the frozen protocol states
that missing provenance invalidates a run and must be rerun rather than patched after results are
seen. No ID or OOD value was accessed by the failed selector invocation.

## Frozen clean rerun

The PI explicitly authorized two parallel replacement files:

1. `root@100.80.236.112`: full H-near grid, seeds 100--102, hidden
   `{32,64,128,256}`, epochs `{100,200,400,800}`, learning rates `{0.001,0.003,0.01}`, and arms
   `{free,free_res,hard,soft30}`, output `h_near_provenance_rerun.jsonl`.
2. `root@100.123.220.57`: corrected C-ad2d thin grid, seeds 100--102, channels `{8,16}`, epochs
   `{100,200}`, learning rates `{0.0003,0.001}`, and the same four arms, output
   `c_ad2d_provenance_rerun.jsonl`.

Both commands set:

- `ECOPHYS_GIT_HEAD=86dd76ee0127c5eb7945a5806bdad74548c62459`;
- `ECOPHYS_DIRTY=1`.

The original raw files remain immutable and are excluded, not edited. After both replacements
finish, verify their local/remote SHA-256 values and require every replacement record to contain
the exact Git HEAD, dirty flag, source hashes, and frozen seed/grid metadata. The corrected ID-only
selector then uses the original snapshot with `h_near.jsonl` and `c_ad2d.jsonl` replaced by these
two clean files. OOD remains unopened.

## Prevention

`constraint_iclr_common.provenance` now fails before training when neither Git nor explicit remote
environment variables can provide the Git HEAD or dirty state. The confirmation deployment must
set both variables and pass a one-record provenance preflight before production launch.
