#!/usr/bin/env bash
set -euo pipefail

ROOT=/root/ecophys_constraint_iclr_unet_20260902
CONDA=/root/miniconda3/bin/conda
ENV_PREFIX=/data/ecophys_workshop/conda_env
WATCHER_PID=247200
INCOMING_DIR="$ROOT/incoming_20260903"
V100A_ARCHIVE="$INCOMING_DIR/unet_v100a_transfer_20260903.tar.gz"
V100A_SIDECAR="$V100A_ARCHIVE.sha256"
V100A_REL=experiments/constraint_attribution_iclr/pdebench/unet_factorial_v100a_20260902.jsonl
V100B_REL=experiments/constraint_attribution_iclr/pdebench/unet_factorial_v100b_20260902.jsonl
MERGED_REL=experiments/constraint_attribution_iclr/pdebench/unet_factorial_merged_20260902.jsonl
CORE_ANALYSIS_REL=experiments/constraint_attribution_iclr/pdebench/unet_factorial_analysis_20260903.json
CUBE_REL=experiments/constraint_attribution_iclr/pdebench/unet_enforcement_cube_20260903.jsonl
CUBE_ANALYSIS_REL=experiments/constraint_attribution_iclr/pdebench/unet_enforcement_cube_analysis_20260903.json
CHECKPOINT_LOCK_REL=experiments/constraint_attribution_iclr/pdebench/unet_factorial_checkpoint_lock_20260903.json
V100B_TRANSFER_DIR="$ROOT/experiments/constraint_attribution_iclr/pdebench/transfer_20260903"
V100B_ARCHIVE="$V100B_TRANSFER_DIR/unet_v100b_transfer_20260903.tar.gz"
V100B_MANIFEST="$ROOT/experiments/constraint_attribution_iclr/pdebench/unet_v100b_transfer_manifest_20260903.json"
V100B_SIDECAR="$V100B_ARCHIVE.sha256"
CONFIG=configs/constraint_iclr/pdebench_advection_unet_enforcement_cube_20260903.yaml
SNAPSHOT_MANIFEST=experiments/constraint_attribution_iclr/deployment/unet_completion_snapshot_20260903.sha256s

run_python() {
  "$CONDA" run --no-capture-output -p "$ENV_PREFIX" python "$@"
}

mkdir -p "$INCOMING_DIR" "$V100B_TRANSFER_DIR"
printf 'watch_started %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
while kill -0 "$WATCHER_PID" 2>/dev/null; do
  sleep 30
done
if pgrep -f "run_constraint_iclr_pdebench_fno.py.*worker_id=v100b" >/dev/null; then
  printf 'blocked v100b_worker_is_still_alive\n'
  exit 30
fi
if [[ ! -f "$ROOT/$V100B_REL" ]]; then
  printf 'blocked missing_v100b_shard\n'
  exit 31
fi
V100B_RECORD_COUNT=$(wc -l < "$ROOT/$V100B_REL")
if [[ "$V100B_RECORD_COUNT" != 75 ]]; then
  printf 'blocked expected_75_v100b_records observed=%s\n' "$V100B_RECORD_COUNT"
  exit 32
fi

cd "$ROOT"
sha256sum -c "$SNAPSHOT_MANIFEST"
run_python scripts/package_constraint_iclr_pdebench_unet_shard.py \
  --root "$ROOT" \
  --input "$ROOT/$V100B_REL" \
  --worker-id v100b \
  --archive "$V100B_ARCHIVE" \
  --manifest "$V100B_MANIFEST" \
  --sidecar "$V100B_SIDECAR"

while [[ ! -s "$V100A_SIDECAR" ]] || [[ ! -s "$V100A_ARCHIVE" ]]; do
  sleep 30
done
cd "$INCOMING_DIR"
sha256sum -c "$(basename "$V100A_SIDECAR")"
tar -xzf "$V100A_ARCHIVE" -C "$ROOT"

cd "$ROOT"
run_python scripts/package_constraint_iclr_pdebench_unet_shard.py \
  --root "$ROOT" --input "$ROOT/$V100A_REL" --worker-id v100a --validate-only
run_python scripts/package_constraint_iclr_pdebench_unet_shard.py \
  --root "$ROOT" --input "$ROOT/$V100B_REL" --worker-id v100b --validate-only
run_python scripts/merge_constraint_iclr_pdebench_factorial.py \
  --config "$CONFIG" \
  --inputs "$V100A_REL" "$V100B_REL" \
  --output "$MERGED_REL"
if [[ "$(wc -l < "$ROOT/$MERGED_REL")" != 150 ]]; then
  printf 'blocked expected_150_merged_records\n'
  exit 33
fi
run_python scripts/analyze_constraint_iclr_pdebench_factorial.py \
  --config "$CONFIG" \
  --input "$MERGED_REL" \
  --output "$CORE_ANALYSIS_REL"

env ECOPHYS_GIT_HEAD=86dd76ee0127c5eb7945a5806bdad74548c62459 \
  ECOPHYS_DIRTY=1 \
  "$CONDA" run --no-capture-output -p "$ENV_PREFIX" python \
  scripts/run_constraint_iclr_pdebench_enforcement_cube.py \
  --config-name pdebench_advection_unet_enforcement_cube_20260903
if [[ "$(wc -l < "$ROOT/$CUBE_REL")" != 90 ]]; then
  printf 'blocked expected_90_cube_records\n'
  exit 34
fi
run_python scripts/analyze_constraint_iclr_pdebench_enforcement_cube.py \
  --config "$CONFIG" \
  --derived-input "$CUBE_REL" \
  --core-input "$MERGED_REL" \
  --core-analysis "$CORE_ANALYSIS_REL" \
  --checkpoint-lock "$CHECKPOINT_LOCK_REL" \
  --output "$CUBE_ANALYSIS_REL"
sha256sum \
  "$ROOT/$V100A_REL" \
  "$ROOT/$V100B_REL" \
  "$ROOT/$MERGED_REL" \
  "$ROOT/$CORE_ANALYSIS_REL" \
  "$ROOT/$CHECKPOINT_LOCK_REL" \
  "$ROOT/$CUBE_REL" \
  "$ROOT/$CUBE_ANALYSIS_REL" \
  "$V100B_ARCHIVE" \
  "$V100B_MANIFEST" \
  "$V100B_SIDECAR"
printf 'unet_pipeline_complete %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
