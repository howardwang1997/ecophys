# Compound III supply-cap activation preflight v2 runbook

Run v2 exactly once, only after its complete protocol commit is pushed, from a clean detached worktree at that
full commit. Do not probe a candidate endpoint first and do not substitute an endpoint after freeze. V1's
`artifacts/failure.json` and `RESULTS_V1.md` are immutable parents; v2 uses a separate `artifacts_v2` directory.
These four v2 output paths must be absent:

```bash
conda run -n ecophys python -m ecomd.research.compound_supply_cap_activation_v2 \
  data/manifests/compound_v3_supply_cap_activation_preflight_v2.yaml \
  --summary experiments/v14_compound_v3_supply_cap_activation_preflight/artifacts_v2/summary.json \
  --candidates experiments/v14_compound_v3_supply_cap_activation_preflight/artifacts_v2/candidates.json \
  --response-hashes experiments/v14_compound_v3_supply_cap_activation_preflight/artifacts_v2/http_evidence.json \
  --failure experiments/v14_compound_v3_supply_cap_activation_preflight/artifacts_v2/failure.json \
  --collection-commit <FULL_PUSHED_D1A_V2_PROTOCOL_COMMIT>
```

Before launch:

1. reproduce v1 manifest/result/failure hashes and its infrastructure-failure identity;
2. reproduce all D0b/source parents, four candidates, seven implementations and inherited scientific fields;
3. reproduce 105 ordered operations: 98 RPC plus seven source REST, with no PublicNode `eth_call`/`eth_getCode`;
4. run the bounded Compound tests, Ruff, format and strict mypy in the `ecophys` Conda environment;
5. confirm detached HEAD equals the remote protocol commit, the worktree is clean and all four v2 outputs absent;
6. confirm account/action/log/trace/price/liquidation/post-event/response access and all GPUs remain locked.

Preserve the first outcome without rerun. On completion, independently rebuild all manifest/parent/source/file/ABI
and request hashes, 24 cross-provider header identities, every Blockscout state snapshot, contemporaneous
utilization integer, integrity gate and decision. Verify the v1 artifact is unchanged and v2 `failure.json` absent.

On exception, verify all three v2 success outputs are absent and `failure.json` contains every operation/attempt,
the bounded exception and all completed normalized evidence without source/RPC bodies. Partial evidence must remain
explicitly incomplete and cannot authorize a scientific decision.

Never replace exact T−1 saturation with a near-cap diagnostic. Even a pass authorizes only a separate market-level
D1b design; account/response acquisition, G1 and every GPU job remain locked.
