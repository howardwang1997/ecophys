# Compound III source-metadata preflight v2 runbook

From the clean detached EcoPhys worktree root:

```bash
conda run -n ecophys python -m ecomd.research.compound_v3_metadata \
  data/manifests/compound_v3_metadata_preflight_v1.yaml \
  --source-repo /private/tmp/compound-comet-source-20260816 \
  --output experiments/v14_compound_v3_metadata_preflight/artifacts/summary.json
```

Do not use the v1 direct-script wrapper. After execution, independently verify the source remote/commit/clean
state, all nine gates, six market records, unique addresses, file hashes and final artifact SHA-256. Do not fetch
chain data or change the manifest after seeing the result.
