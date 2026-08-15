# Compound III supply-cap activation preflight v1 runbook

Run exactly once, only after the complete protocol commit is pushed, from a clean detached worktree at that full
commit. Do not issue a candidate source/getter capability probe first and do not substitute an endpoint after
freeze. These four output paths must be absent:

```bash
conda run -n ecophys python -m ecomd.research.compound_supply_cap_activation \
  data/manifests/compound_v3_supply_cap_activation_preflight_v1.yaml \
  --summary experiments/v14_compound_v3_supply_cap_activation_preflight/artifacts/summary.json \
  --candidates experiments/v14_compound_v3_supply_cap_activation_preflight/artifacts/candidates.json \
  --response-hashes experiments/v14_compound_v3_supply_cap_activation_preflight/artifacts/http_evidence.json \
  --failure experiments/v14_compound_v3_supply_cap_activation_preflight/artifacts/failure.json \
  --collection-commit <FULL_PUSHED_D1A_PROTOCOL_COMMIT>
```

Before launch:

1. reproduce all D0b v2 and source-metadata parent hashes, decisions and commit identities;
2. re-derive four survivors and seven unique implementation addresses/hashes in exact parent order;
3. reproduce the 141-operation plan: 134 RPC plus seven source REST, with exact method/provider totals;
4. run the bounded Compound tests, Ruff, formatter and strict mypy with the `ecophys` Conda environment;
5. confirm HEAD equals the remote protocol commit, the detached worktree is clean and all four outputs are absent;
6. confirm no account/action/log/trace/price/liquidation/response access and no GPU or external worker.

Preserve the first outcome without rerun. On full completion, independently rebuild parent/manifest hashes,
source-file and ABI evidence, all request hashes/order/attempts, bytecode and getter replicas, every historical
snapshot, utilization integers, integrity gates and the decision. Verify `failure.json` is absent.

On a caught exception, verify all three success outputs are absent and `failure.json` contains the bounded
exception, every preceding successful-operation hash, one record per HTTP attempt, matching attempt/byte totals,
no raw body, the infrastructure-failure decision and no authorized next stage.

Do not interpret 90%, 95% or 99% utilization as a pass. Do not query event/post-event aggregate totals to explain
the result. Even exact T−1 saturation authorizes only a separately preregistered market-level D1b design; account
and response acquisition, G1 and every GPU job remain locked.
