#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/data/ecophys_workshop/repo}"
PYTHON_BIN="${PYTHON_BIN:-/data/ecophys_workshop/conda_env/bin/python}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-/data/ecophys_workshop/artifacts/exp133}"
QUEUE_ROOT="${QUEUE_ROOT:-/data/ecophys_workshop/queue/exp133}"
GIT_SHA="${GIT_SHA:?GIT_SHA is required}"
BLOCKER_SERVICE="${BLOCKER_SERVICE:-}"
RELEASE_MARKER="${RELEASE_MARKER:-}"
POLL_SECONDS="${POLL_SECONDS:-60}"
STABLE_POLLS="${STABLE_POLLS:-10}"
MAX_WAIT_SECONDS="${MAX_WAIT_SECONDS:-1209600}"

mkdir -p "$ARTIFACT_ROOT" "$QUEUE_ROOT"
STATUS="$QUEUE_ROOT/status.json"
LOG="$QUEUE_ROOT/queue.log"
RUN_LOG="$QUEUE_ROOT/run.log"
RESULT="$ARTIFACT_ROOT/V100_RESULTS_${GIT_SHA:0:12}.json"
WORK_ROOT="$ARTIFACT_ROOT/work_${GIT_SHA:0:12}"
LOCK="$QUEUE_ROOT/queue.lock"

exec 9>"$LOCK"
if ! flock -n 9; then
    printf '[%s] another exp133 queue process owns %s\n' "$(date -Is)" "$LOCK" >>"$LOG"
    exit 11
fi

write_status() {
    local state="$1"
    local detail="$2"
    local temporary="${STATUS}.tmp.$$"
    "$PYTHON_BIN" - "$temporary" "$state" "$detail" "$GIT_SHA" "$RESULT" <<'PY'
import json
import os
import sys
from datetime import datetime

path, state, detail, git_sha, result = sys.argv[1:]
payload = {
    "state": state,
    "detail": detail,
    "updated_at": datetime.now().astimezone().isoformat(),
    "git_sha": git_sha,
    "result": result,
    "pid": os.getppid(),
}
with open(path, "w", encoding="utf-8") as stream:
    json.dump(payload, stream, indent=2, sort_keys=True)
    stream.write("\n")
PY
    mv "$temporary" "$STATUS"
    printf '[%s] state=%s detail=%s\n' "$(date -Is)" "$state" "$detail" >>"$LOG"
}

result_passes() {
    [ -f "$RESULT" ] || return 1
    "$PYTHON_BIN" - "$RESULT" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    payload = json.load(stream)
raise SystemExit(0 if payload.get("all_checks_pass") is True else 1)
PY
}

if result_passes; then
    write_status "already_complete" "passing result already exists"
    exit 0
fi

for required in \
    "$PYTHON_BIN" \
    "$REPO_ROOT/experiments/133_distributed_exact_resume/run_exact_resume.py" \
    "$REPO_ROOT/experiments/133_distributed_exact_resume/run_stage.py"; do
    if [ ! -e "$required" ]; then
        write_status "preflight_failed" "missing $required"
        exit 12
    fi
done

if ! "$PYTHON_BIN" -c 'import torch; raise SystemExit(0 if torch.cuda.is_available() else 1)'; then
    write_status "preflight_failed" "CUDA unavailable in configured Python"
    exit 13
fi

write_status "waiting" "waiting for blocker release and ${STABLE_POLLS} stable idle polls"
started="$(date +%s)"
stable=0
while true; do
    now="$(date +%s)"
    elapsed=$((now - started))
    if [ "$elapsed" -gt "$MAX_WAIT_SECONDS" ]; then
        write_status "timed_out" "maximum queue wait exceeded"
        exit 14
    fi

    if [ -n "$RELEASE_MARKER" ] && [ -e "$RELEASE_MARKER" ]; then
        stable=0
        write_status "held_for_priority_queue" "graphene release marker exists"
        sleep "$POLL_SECONDS"
        continue
    fi

    blocker_active=0
    if [ -n "$BLOCKER_SERVICE" ] && systemctl is-active --quiet "$BLOCKER_SERVICE"; then
        blocker_active=1
    fi
    compute_processes="$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null | sed '/^[[:space:]]*$/d' | wc -l)"
    utilization="$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')"
    utilization="${utilization:-100}"

    if [ "$blocker_active" -eq 0 ] && [ "$compute_processes" -eq 0 ] && [ "$utilization" -le 5 ]; then
        stable=$((stable + 1))
    else
        stable=0
    fi
    write_status \
        "waiting" \
        "elapsed=${elapsed}s blocker=${blocker_active} compute=${compute_processes} util=${utilization}% stable=${stable}/${STABLE_POLLS}"
    if [ "$stable" -ge "$STABLE_POLLS" ]; then
        break
    fi
    sleep "$POLL_SECONDS"
done

if [ -n "$RELEASE_MARKER" ] && [ -e "$RELEASE_MARKER" ]; then
    write_status "held_for_priority_queue" "release marker appeared before launch"
    exit 15
fi
if [ "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null | sed '/^[[:space:]]*$/d' | wc -l)" -ne 0 ]; then
    write_status "race_avoided" "new compute process appeared before launch"
    exit 16
fi

write_status "running" "launching single-V100 exact-resume gate"
set +e
PYTHONPATH="$REPO_ROOT" OMP_NUM_THREADS=1 "$PYTHON_BIN" \
    "$REPO_ROOT/experiments/133_distributed_exact_resume/run_exact_resume.py" \
    --out "$RESULT" \
    --work-root "$WORK_ROOT" \
    --nproc 1 \
    --device cuda \
    --git-sha "$GIT_SHA" >"$RUN_LOG" 2>&1
run_status=$?
set -e

if [ "$run_status" -ne 0 ]; then
    write_status "failed" "runner exited $run_status; inspect $RUN_LOG"
    exit "$run_status"
fi
if ! result_passes; then
    write_status "scientific_gate_failed" "runner completed but all_checks_pass is false"
    exit 17
fi
write_status "complete" "all CUDA exact-resume checks passed"
