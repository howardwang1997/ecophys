#!/usr/bin/env bash
set -euo pipefail

SWE_ROOT_DIR=/root/ecophys_constraint_iclr_pdebench_swe_20260902
ADVECTION_ROOT_DIR=/root/ecophys_constraint_iclr_pdebench_cube_v4_20260901
PYTHON_BIN=/data/ecophys_workshop/conda_env/bin/python
B_HOST=root@100.123.220.57
SWE_WORKER_PID=1709983
SWE_SHARD_REL=experiments/constraint_attribution_iclr/pdebench/swe_factorial_v100a_20260902.jsonl
TRANSFER_REL=experiments/constraint_attribution_iclr/pdebench/transfer_20260902
TRANSFER_DIR="$SWE_ROOT_DIR/$TRANSFER_REL"
TRANSFER_ARCHIVE="$TRANSFER_DIR/swe_v100a_transfer_20260902.tar.gz"
TRANSFER_MANIFEST="$SWE_ROOT_DIR/experiments/constraint_attribution_iclr/pdebench/swe_v100a_transfer_manifest_20260902.json"
TRANSFER_SIDECAR="$TRANSFER_ARCHIVE.sha256"
B_INCOMING_DIR=/root/ecophys_constraint_iclr_pdebench_swe_20260902/incoming_20260902
GAUGE_OUTPUT_REL=experiments/constraint_attribution_iclr/pdebench/advection_gauge_feedback_20260902.jsonl
GAUGE_ANALYSIS_REL=experiments/constraint_attribution_iclr/pdebench/advection_gauge_feedback_analysis_20260902.json

printf 'watch_started %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
while kill -0 "$SWE_WORKER_PID" 2>/dev/null; do
  sleep 30
done
if pgrep -f "run_constraint_iclr_pdebench_swe.py.*worker_id=v100a" >/dev/null; then
  printf 'blocked another_v100a_worker_is_alive\n'
  exit 20
fi
SWE_RECORD_COUNT=$(wc -l < "$SWE_ROOT_DIR/$SWE_SHARD_REL")
printf 'swe_worker_exited records=%s time=%s\n' \
  "$SWE_RECORD_COUNT" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
if [[ "$SWE_RECORD_COUNT" != 75 ]]; then
  printf 'blocked expected_75_swe_records\n'
  exit 21
fi
sha256sum "$SWE_ROOT_DIR/$SWE_SHARD_REL"
cd "$SWE_ROOT_DIR"
sha256sum -c \
  experiments/constraint_attribution_iclr/deployment/pdebench_swe_completion_orchestration_20260902.sha256s
mkdir -p "$TRANSFER_DIR"
"$PYTHON_BIN" scripts/package_constraint_iclr_pdebench_swe_shard.py \
  --root "$SWE_ROOT_DIR" \
  --input "$SWE_ROOT_DIR/$SWE_SHARD_REL" \
  --worker-id v100a \
  --archive "$TRANSFER_ARCHIVE" \
  --manifest "$TRANSFER_MANIFEST" \
  --sidecar "$TRANSFER_SIDECAR"
ssh -o BatchMode=yes -o ConnectTimeout=10 "$B_HOST" mkdir -p "$B_INCOMING_DIR"
scp -o BatchMode=yes -o ConnectTimeout=10 "$TRANSFER_ARCHIVE" \
  "$B_HOST:$B_INCOMING_DIR/"
scp -o BatchMode=yes -o ConnectTimeout=10 "$TRANSFER_SIDECAR" \
  "$B_HOST:$B_INCOMING_DIR/"
printf 'swe_transfer_delivered %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cd "$ADVECTION_ROOT_DIR"
sha256sum -c \
  experiments/constraint_attribution_iclr/deployment/pdebench_gauge_feedback_snapshot_20260902.sha256s
"$PYTHON_BIN" -m pytest tests/test_constraint_iclr_pdebench_gauge_feedback.py -q
ECOPHYS_GIT_HEAD=86dd76ee0127c5eb7945a5806bdad74548c62459 \
ECOPHYS_DIRTY=1 \
  "$PYTHON_BIN" scripts/run_constraint_iclr_pdebench_gauge_feedback.py
GAUGE_RECORD_COUNT=$(wc -l < "$ADVECTION_ROOT_DIR/$GAUGE_OUTPUT_REL")
if [[ "$GAUGE_RECORD_COUNT" != 60 ]]; then
  printf 'blocked expected_60_gauge_records observed=%s\n' "$GAUGE_RECORD_COUNT"
  exit 22
fi
"$PYTHON_BIN" scripts/analyze_constraint_iclr_pdebench_gauge_feedback.py
sha256sum \
  "$ADVECTION_ROOT_DIR/$GAUGE_OUTPUT_REL" \
  "$ADVECTION_ROOT_DIR/$GAUGE_ANALYSIS_REL"
printf 'gauge_pipeline_complete %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
