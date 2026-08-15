# Runbook — Uniswap v3 U1R preperiod exposure census

Run once from the pushed protocol commit in a clean detached worktree:

```bash
conda run --no-capture-output -n ecophys python \
  experiments/v14_uniswap_v3_preperiod_exposure_census/collect_exposure_census.py \
  --collection-commit <full-protocol-git-sha>
```

The collector refuses overwrite and writes only:

- `artifacts/exposure_census.jsonl`;
- `artifacts/http_response_hashes.json`;
- `artifacts/summary.json`.

Independently verify the exact 1,000-row U0 population and order, both parent hashes, boundary headers, request
order and caps, recursive saturation partitions, deduplication counts, every output hash and every frozen gate.
Confirm that no raw response, decoded amount/price/liquidity, non-NPM manager address, identity history, control or
post-treatment field was retained.

Preserve a pass, scientific failure or transport failure without replacing pools, extending the window, changing
the endpoint or lowering thresholds. Do not rerun the 16 U1a pools separately: they are included uniformly in the
census. A pass first requires separate control and identity protocols. U2, learned models and all GPU jobs remain
locked.
