# Runbook — Uniswap v3 treatment conformance v2

Run once from the pushed v2 protocol commit in a clean detached worktree:

```bash
conda run -n ecophys python \
  experiments/v14_uniswap_v3_fee_treatment_conformance/collect_treatment.py \
  --collection-commit <full-v2-protocol-git-sha>
```

The default contract is `data/manifests/uniswap_v3_fee_treatment_conformance_v2.yaml`. The command must issue
exactly 11 successful read-only calls and write only:

- `artifacts_v2/treatment_ledger.jsonl`;
- `artifacts_v2/rpc_response_hashes.json`;
- `artifacts_v2/treatment_summary.json`.

Verify line count, SHA-256 digests, contract hash, collection commit, request count and every gate. Do not rerun,
replace the endpoint, change a batch or open any LP/market response. Even a pass first requires a new frozen U1
pre-treatment-only protocol.
