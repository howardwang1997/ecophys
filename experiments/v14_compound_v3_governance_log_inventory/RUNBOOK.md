# Compound III governance-log inventory v1 runbook

Run exactly once after the protocol commit is pushed, from a clean detached worktree at that exact commit. The
three output paths must not exist:

```bash
conda run -n ecophys python -m ecomd.research.compound_governance_inventory \
  data/manifests/compound_v3_governance_log_inventory_v1.yaml \
  --summary experiments/v14_compound_v3_governance_log_inventory/artifacts/summary.json \
  --inventory experiments/v14_compound_v3_governance_log_inventory/artifacts/governance_logs.json \
  --response-hashes experiments/v14_compound_v3_governance_log_inventory/artifacts/rpc_response_hashes.json \
  --collection-commit <FULL_PUSHED_PROTOCOL_COMMIT>
```

Before launch, verify the worktree is clean, both parent hashes match, the end block/hash is unchanged and the
expected root plan is 48 intervals times seven addresses. Do not substitute a provider after any failure.

Afterward independently verify:

- the collection commit and manifest hash;
- chain ID, start/end headers and cross-parent end-block hash;
- 336 root queries, plus only deterministic saturation children if present;
- allowed-method counts, retry history, byte/attempt/row caps and absence of duplicate/conflicting rows;
- every strict ABI decode and each provisional candidate's complete check vector;
- all ten gate values, decision string and three artifact SHA-256 values; and
- that no account, action, response, receipt, payload, trace, price or liquidation data were accessed.

Preserve either pass or failure unchanged. A pass unlocks a new receipt/payload/finality preflight only; do not
start account collection, causal analysis, model training or a GPU job.
