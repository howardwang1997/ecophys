# CoW competition HEAD enumeration runbook

Run only from the commit that contains the frozen manifest and from a clean worktree:

```bash
conda run -n ecophys python experiments/v14_cow_competition_head_enumeration/enumerate_head.py
```

The runner derives the request sequence from
`data/manifests/cow_competition_head_enumeration_v1.yaml`, enforces one request per second, sends HEAD with
streaming enabled, never reads response content and writes a status-only JSONL ledger. It refuses to overwrite a
summary or resolved manifest.

If transport interruption requires a resume, keep the partial ledger byte-for-byte and supply both `--resume`
and the original 40-character collection commit. The existing ledger must be an exact prefix of the frozen ID
sequence. Do not delete failures or substitute IDs.

On pass, inspect and commit these three files before any GET:

- `experiments/v14_cow_competition_head_enumeration/artifacts/head_request_ledger.jsonl`
- `experiments/v14_cow_competition_head_enumeration/artifacts/head_enumeration_summary.json`
- `data/manifests/cow_competition_head_enumeration_v1_resolved.yaml`

Do not start a payload collector until the resolved manifest commit is on the remote branch. GPU workers remain
idle; this stage is CPU/network metadata only.
