# Runbook — Uniswap v3 treatment conformance

Run only from the committed protocol in a clean detached worktree:

```bash
conda run -n ecophys python \
  experiments/v14_uniswap_v3_fee_treatment_conformance/collect_treatment.py \
  --collection-commit <full-protocol-git-sha>
```

The command refuses to overwrite any artifact. It should issue eleven read-only JSON-RPC requests at no more
than one request per second and produce:

- `artifacts/treatment_ledger.jsonl` — exactly 1,000 normalized mechanism rows on pass;
- `artifacts/rpc_response_hashes.json` — request/response hashes and retry metadata;
- `artifacts/treatment_summary.json` — gates and disposition.

Before accepting the result, independently verify:

```bash
wc -l experiments/v14_uniswap_v3_fee_treatment_conformance/artifacts/treatment_ledger.jsonl
shasum -a 256 experiments/v14_uniswap_v3_fee_treatment_conformance/artifacts/*
conda run -n ecophys python -m pytest -q tests/test_uniswap_v3_fee_treatment.py
```

Do not run an LP, swap, pool-volume or price collector after this command. A passing result first requires a new
committed protocol that uses only pre-treatment information to select and assess identity-covered pools.

