# Compound III chain-metadata runbook

Run exactly once only after the protocol commit is pushed, from a clean detached EcoPhys worktree:

```bash
conda run -n ecophys python -m ecomd.research.compound_v3_chain_metadata \
  data/manifests/compound_v3_chain_metadata_preflight_v1.yaml \
  --summary experiments/v14_compound_v3_chain_metadata_preflight/artifacts/summary.json \
  --response-hashes experiments/v14_compound_v3_chain_metadata_preflight/artifacts/rpc_response_hashes.json \
  --collection-commit <FULL_PUSHED_PROTOCOL_COMMIT>
```

Before launch, confirm both output paths are absent and Git status is empty. Afterward independently verify the
manifest/source hashes, request/method counts, block hashes, code hashes, address decoding, all twelve gates and
artifact hashes. Do not substitute an endpoint, block, market or getter after a failure.
