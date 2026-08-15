# Runbook — Uniswap v3 U1a preperiod support

Run once from the pushed protocol commit in a clean detached worktree:

```bash
conda run -n ecophys python \
  experiments/v14_uniswap_v3_preperiod_support/collect_preperiod_support.py \
  --collection-commit <full-protocol-git-sha>
```

The collector refuses overwrite and writes only:

- `artifacts/pool_support.jsonl`;
- `artifacts/identity_sample.jsonl`;
- `artifacts/http_response_hashes.json`;
- `artifacts/summary.json`.

Independently verify artifact hashes, 16 pool rows, exact sample membership, window headers, all request/byte caps,
no duplicate/conflicting logs, identity sample selection and every gate. A result may be pass or failure; do not
rerun, replace the endpoint, add pools, extend the window or lower thresholds.

Do not query treatment/post-treatment pool events after this command. A pass first requires separate committed
U1b and control-source protocols. U2 response access and all GPU/model jobs remain locked.
