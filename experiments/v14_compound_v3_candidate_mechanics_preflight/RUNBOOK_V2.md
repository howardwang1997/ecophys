# Compound III all-candidate mechanics preflight v2 runbook

Run v2 exactly once, only after its protocol commit is pushed, from a clean detached worktree at that full commit.
Do not issue a frozen-candidate raw-trace capability probe first. These four paths must not exist:

```bash
conda run -n ecophys python -m ecomd.research.compound_candidate_mechanics \
  data/manifests/compound_v3_candidate_mechanics_preflight_v2.yaml \
  --summary experiments/v14_compound_v3_candidate_mechanics_preflight/artifacts_v2/summary.json \
  --candidates experiments/v14_compound_v3_candidate_mechanics_preflight/artifacts_v2/candidates.json \
  --response-hashes experiments/v14_compound_v3_candidate_mechanics_preflight/artifacts_v2/http_evidence.json \
  --failure experiments/v14_compound_v3_candidate_mechanics_preflight/artifacts_v2/failure.json \
  --collection-commit <FULL_PUSHED_V2_PROTOCOL_COMMIT>
```

Before launch:

1. reproduce the v1 manifest/result and all D0/exposure/chain parent hashes;
2. confirm all 14 candidates re-derive exactly in the frozen order and values;
3. confirm the no-retry plan is 173 RPC + 14 Blockscout raw-trace REST + one Beacon REST, with 188 total;
4. run the targeted tests, Ruff, formatting and strict mypy using Conda;
5. verify the detached worktree is clean and its HEAD equals the pushed protocol commit; and
6. verify all four output paths are absent.

After the command exits, preserve its first outcome without rerunning or substituting an endpoint.

If collection completes, independently verify that `failure.json` is absent and that the three success artifacts
record the exact manifest/commit/parent hashes, candidates, operation order, provider/method/path totals, every HTTP
attempt, response hashes, global caps, finality evidence, all candidate checks and all twelve gates.

If collection raises, independently verify that all three success artifacts are absent and `failure.json` contains
the bounded exception, every successful operation available before failure, one record for every HTTP attempt,
matching attempt/byte totals, no raw response body, the infrastructure-failure decision and no authorized next
stage. A failed endpoint or malformed/incomplete trace is not a candidate-mechanics result.

In either outcome, verify that no account, participant-action/trace, liquidation, price/oracle or response row was
opened and that no paid data, external worker or GPU was used. D1 and G1 remain locked unless a complete v2 result
passes every frozen gate.
