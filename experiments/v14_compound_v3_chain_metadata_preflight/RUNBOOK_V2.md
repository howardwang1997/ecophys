# Compound III chain-metadata v2 runbook

Run exactly once only after the v2 protocol commit is pushed, from a clean detached EcoPhys worktree:

```bash
conda run -n ecophys python -m ecomd.research.compound_v3_chain_metadata \
  data/manifests/compound_v3_chain_metadata_preflight_v2.yaml \
  --summary experiments/v14_compound_v3_chain_metadata_preflight/artifacts_v2/summary.json \
  --response-hashes experiments/v14_compound_v3_chain_metadata_preflight/artifacts_v2/rpc_response_hashes.json \
  --collection-commit <FULL_PUSHED_V2_PROTOCOL_COMMIT>
```

Before launch, confirm both output paths are absent and Git status is empty. Afterward independently verify the
manifest/source hashes, exact 62-call method vector, `head - snapshot == 64`, explicit block use, archive header,
code hashes, address decoding, all twelve gates and artifact hashes. Describe the snapshot as 64-block confirmed,
never consensus-finalized. Do not substitute an endpoint, depth, block, market or getter after a failure.
