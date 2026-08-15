# Compound III all-candidate mechanics preflight v1 runbook

Run once only after the protocol commit is pushed, from a clean detached worktree at that exact commit. The three
output paths must not exist:

```bash
conda run -n ecophys python -m ecomd.research.compound_candidate_mechanics \
  data/manifests/compound_v3_candidate_mechanics_preflight_v1.yaml \
  --summary experiments/v14_compound_v3_candidate_mechanics_preflight/artifacts/summary.json \
  --candidates experiments/v14_compound_v3_candidate_mechanics_preflight/artifacts/candidates.json \
  --response-hashes experiments/v14_compound_v3_candidate_mechanics_preflight/artifacts/rpc_response_hashes.json \
  --collection-commit <FULL_PUSHED_PROTOCOL_COMMIT>
```

Before launch, verify the worktree is clean, all four parent hashes reproduce, 14 candidates re-derive exactly,
the ordered first two candidates are the borrow-factor rows and the exact no-retry plan is 187 RPC plus one Beacon
operation. Run all candidate-mechanics and parent tests. Do not make a capability probe or substitute a provider.

Afterward independently verify:

- collection commit, manifest/parent hashes and exact candidate order;
- exact ordered request/provider/method/parameter plan, retry history, byte/node/input/log caps and all response
  hashes;
- transaction/receipt/D0 log identity and two-provider headers for all 14;
- complete trace roots, four exact required-call counts and every unclassified stateful call;
- T-1/T implementation/admin/code and eight-word getter diffs;
- neighbor timestamps, both finalized heights and Beacon-to-explicit-execution hash agreement;
- all global gates and every candidate check without dropping a failure; and
- absence of account, participant action/trace, liquidation, price and response access.

Preserve either outcome. A pass permits D1 exposure protocol design only; do not open accounts or start GPU work.
