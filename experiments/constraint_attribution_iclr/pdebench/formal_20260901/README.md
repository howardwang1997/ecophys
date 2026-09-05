# PDEBench v2 formal confirmation artifacts

These are the immutable artifacts used by `papers/paper_d_constraints/main.tex`.
They were copied from the completed formal worker after all frozen integrity gates
passed and before manuscript editing.

| artifact | records / bytes | SHA-256 |
|---|---:|---|
| `confirmation_v2.jsonl` | 150 records / 1,683,025 bytes | `09e69b4e50bd39c152bef0e22e07d86a8b513f31ed119d887ed3077fb72d2fc3` |
| `analysis.json` | 11,819 bytes | `e1619126f46eb081ace19000d44771559029c49f22f0057812183fc7e2efb41a` |

The scientific protocol is frozen in
`papers/proposal/ecomd_constraint_attribution_iclr_pdebench_v2_freeze_2026-09-01.md`.
The data lock is `experiments/constraint_attribution_iclr/pdebench/data_lock_v2_beta0.4.json`.
The manuscript and figure generator consume only `analysis.json`; they do not
re-estimate effects from the raw records.
