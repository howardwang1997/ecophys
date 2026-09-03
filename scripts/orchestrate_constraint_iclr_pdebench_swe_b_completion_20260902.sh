#!/usr/bin/env bash
set -euo pipefail

SWE_ROOT_DIR=/root/ecophys_constraint_iclr_pdebench_swe_20260902
PYTHON_BIN=/data/ecophys_workshop/conda_env/bin/python
INCOMING_DIR="$SWE_ROOT_DIR/incoming_20260902"
TRANSFER_ARCHIVE="$INCOMING_DIR/swe_v100a_transfer_20260902.tar.gz"
TRANSFER_SIDECAR="$TRANSFER_ARCHIVE.sha256"
V100A_REL=experiments/constraint_attribution_iclr/pdebench/swe_factorial_v100a_20260902.jsonl
V100B_REL=experiments/constraint_attribution_iclr/pdebench/swe_factorial_v100b_20260902.jsonl
MERGED_REL=experiments/constraint_attribution_iclr/pdebench/swe_factorial_confirmation_20260902.jsonl
CORE_ANALYSIS_REL=experiments/constraint_attribution_iclr/pdebench/swe_factorial_analysis_20260902.json
CUBE_REL=experiments/constraint_attribution_iclr/pdebench/swe_enforcement_cube_derived_20260902.jsonl
CUBE_ANALYSIS_REL=experiments/constraint_attribution_iclr/pdebench/swe_enforcement_cube_analysis_20260902.json
CHECKPOINT_LOCK_REL=experiments/constraint_attribution_iclr/pdebench/swe_checkpoint_lock_20260902.json
DISTRIBUTED_CONFIG=configs/constraint_iclr/pdebench_swe_rdb_factorial_distributed_20260902.yaml
CUBE_CONFIG=configs/constraint_iclr/pdebench_swe_rdb_enforcement_cube_distributed_20260902.yaml

mkdir -p "$INCOMING_DIR"
printf 'watch_started %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
while [[ ! -s "$TRANSFER_SIDECAR" ]]; do
  sleep 30
done
if pgrep -f "run_constraint_iclr_pdebench_swe.py.*worker_id=v100b" >/dev/null; then
  printf 'blocked v100b_worker_is_still_alive\n'
  exit 30
fi
V100B_RECORD_COUNT=$(wc -l < "$SWE_ROOT_DIR/$V100B_REL")
if [[ "$V100B_RECORD_COUNT" != 75 ]]; then
  printf 'blocked expected_75_v100b_records observed=%s\n' "$V100B_RECORD_COUNT"
  exit 31
fi
cd "$INCOMING_DIR"
sha256sum -c "$(basename "$TRANSFER_SIDECAR")"
tar -xzf "$TRANSFER_ARCHIVE" -C "$SWE_ROOT_DIR"
cd "$SWE_ROOT_DIR"
sha256sum -c \
  experiments/constraint_attribution_iclr/deployment/pdebench_swe_completion_orchestration_20260902.sha256s
"$PYTHON_BIN" scripts/package_constraint_iclr_pdebench_swe_shard.py \
  --root "$SWE_ROOT_DIR" \
  --input "$SWE_ROOT_DIR/$V100A_REL" \
  --worker-id v100a \
  --validate-only
"$PYTHON_BIN" scripts/package_constraint_iclr_pdebench_swe_shard.py \
  --root "$SWE_ROOT_DIR" \
  --input "$SWE_ROOT_DIR/$V100B_REL" \
  --worker-id v100b \
  --validate-only
"$PYTHON_BIN" scripts/merge_constraint_iclr_pdebench_swe.py \
  --config "$DISTRIBUTED_CONFIG" \
  --v100a "$V100A_REL" \
  --v100b "$V100B_REL" \
  --output "$MERGED_REL"
"$PYTHON_BIN" scripts/analyze_constraint_iclr_pdebench_swe.py \
  --config "$DISTRIBUTED_CONFIG" \
  --input "$MERGED_REL" \
  --output "$CORE_ANALYSIS_REL"
ECOPHYS_GIT_HEAD=86dd76ee0127c5eb7945a5806bdad74548c62459 \
ECOPHYS_DIRTY=1 \
  "$PYTHON_BIN" scripts/run_constraint_iclr_pdebench_swe_enforcement_cube.py \
  --config-name pdebench_swe_rdb_enforcement_cube_distributed_20260902
CUBE_RECORD_COUNT=$(wc -l < "$SWE_ROOT_DIR/$CUBE_REL")
if [[ "$CUBE_RECORD_COUNT" != 90 ]]; then
  printf 'blocked expected_90_swe_cube_records observed=%s\n' "$CUBE_RECORD_COUNT"
  exit 32
fi
"$PYTHON_BIN" scripts/analyze_constraint_iclr_pdebench_swe_enforcement_cube.py \
  --config "$CUBE_CONFIG" \
  --derived-input "$CUBE_REL" \
  --core-input "$MERGED_REL" \
  --core-analysis "$CORE_ANALYSIS_REL" \
  --checkpoint-lock "$CHECKPOINT_LOCK_REL" \
  --output "$CUBE_ANALYSIS_REL"
sha256sum \
  "$SWE_ROOT_DIR/$V100A_REL" \
  "$SWE_ROOT_DIR/$V100B_REL" \
  "$SWE_ROOT_DIR/$MERGED_REL" \
  "$SWE_ROOT_DIR/$CORE_ANALYSIS_REL" \
  "$SWE_ROOT_DIR/$CHECKPOINT_LOCK_REL" \
  "$SWE_ROOT_DIR/$CUBE_REL" \
  "$SWE_ROOT_DIR/$CUBE_ANALYSIS_REL"
printf 'swe_pipeline_complete %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
