# Compound III source-metadata preflight runbook

Run once only after the protocol commit is pushed. The source checkout must be the clean official repository at
the frozen commit. The runner itself performs no network operation.

```bash
conda run -n ecophys python \
  experiments/v14_compound_v3_metadata_preflight/collect.py \
  data/manifests/compound_v3_metadata_preflight_v1.yaml \
  --source-repo /private/tmp/compound-comet-source-20260816 \
  --output experiments/v14_compound_v3_metadata_preflight/artifacts/summary.json
```

Before copying an artifact into the active branch, independently check the source remote, commit and clean status,
all nine gates, market/address uniqueness, file hashes and final artifact SHA-256. Do not fetch chain data or alter
the manifest after seeing the result.
