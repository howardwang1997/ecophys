#!/usr/bin/env bash
# Scratch orchestrator: wait for the 117_leverage sweep to drain (driver 626224 gone + GPU
# compute-apps empty on this box), then repoint this box's ecophys env editable ecomd
# h202_amar -> h204 (now safe — no 117 child will re-import), then auto-launch the exp-123
# R1 magnitude run (warmup-discard re-score of 113 baseline + concave_d050). Detached-safe:
# launch with `setsid bash scripts/_wait_then_r1.sh &` so it survives session drops.
#
# Why a watcher (not run-now): my 2 cards are at 99% finishing 117 (174/180). R1 is gate-
# independent (honest write-up of burn-in contamination), so it just needs to fire once the
# box frees. This mirrors scripts/_wait_then_zeta_ed.sh but launches the R1 job instead.
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$REPO_ROOT"

DRIVER_PID="${DRIVER_PID:-626224}"          # bash h20_run_phase.sh experiments/117_leverage
POLL="${POLL:-120}"                          # seconds between polls (2 min)
STABLE_NEEDS="${STABLE_NEEDS:-2}"            # consecutive idle polls to trigger
MAX_WAIT="${MAX_WAIT:-48h}"                  # hard cap so we never wait forever
ENV_PY="/root/miniconda3/envs/ecophys/bin/python"
SP="/root/miniconda3/envs/ecophys/lib/python3.11/site-packages"
TS="$(date +%Y%m%d_%H%M%S)"; WLOG="experiments/_wait_then_r1_${TS}.log"; mkdir -p experiments

log() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$WLOG"; }
gpu_busy() { local n; n=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | wc -l); echo "$n"; }
ck117() { ls /AI4S/Users/howardwang/h202_amar/ecophys/experiments/117_leverage/results_*/training_log.json 2>/dev/null | wc -l; }

log "═══ wait_then_r1 START ═══"
log "watching driver PID=$DRIVER_PID; poll=${POLL}s; stable=$STABLE_NEEDS; max_wait=$MAX_WAIT"
log "117 done at start: $(ck117)/180"

# --- preflight (fail fast if R1 prereqs vanished while waiting) ---
preflight() {
  local missing=0
  for c in \
    experiments/113_gabaix_solve/config_baseline_seed0.yaml \
    experiments/113_gabaix_solve/config_concave_d050_seed0.yaml ; do
    [ -f "$c" ] || { log "  [PREFLIGHT FAIL] missing $c"; missing=1; }
  done
  for ck in \
    experiments/113_gabaix_solve/results_baseline_seed0/checkpoint.pt \
    experiments/113_gabaix_solve/results_concave_d050_seed0/checkpoint.pt ; do
    [ -f "$ck" ] || { log "  [PREFLIGHT FAIL] missing checkpoint $ck"; missing=1; }
  done
  [ -f scripts/gpu_exp123_stage1.sh ] || { log "  [PREFLIGHT FAIL] missing gpu_exp123_stage1.sh"; missing=1; }
  [ -x "$ENV_PY" ] || { log "  [PREFLIGHT FAIL] $ENV_PY not executable"; missing=1; }
  return $missing
}

# --- wait loop ---
start=$(date +%s); max_s=$(( ${MAX_WAIT%h} * 3600 )); stable=0
while true; do
  now=$(date +%s); elapsed=$((now - start))
  [ $elapsed -gt $max_s ] && { log "MAX_WAIT $MAX_WAIT exceeded — giving up"; exit 2; }
  busy=$(gpu_busy)
  drv=0; kill -0 "$DRIVER_PID" 2>/dev/null && drv=1
  if [ "$busy" -eq 0 ]; then stable=$((stable+1)); else stable=0; fi
  log "poll: elapsed=${elapsed}s gpu_procs=$busy stable=$stable/$STABLE_NEEDS driver${DRIVER_PID}_alive=$drv 117_done=$(ck117)/180"
  [ "$stable" -ge "$STABLE_NEEDS" ] && { log "GPU idle x$STABLE_NEEDS → trigger."; break; }
  sleep "$POLL"
done

log "117 final: $(ck117)/180"
if ! preflight; then log "PREFLIGHT FAILED — not launching R1. Inspect $WLOG"; exit 3; fi
log "preflight OK (R1 configs + checkpoints + env present)"

# --- repoint THIS box's env editable ecomd h202_amar -> h204 (safe now: GPU idle = no 117 child) ---
log "repointing editable ecomd h202_amar -> h204 ..."
sed -i "s|howardwang/h202_amar/ecophys|howardwang/h204/ecophys|g" \
  "$SP/__editable__.ecomd-0.0.1.pth" "$SP/__editable___ecomd_0_0_1_finder.py" 2>/dev/null
"$ENV_PY" -c "import ecomd;print('  ecomd now from',ecomd.__file__)" 2>&1 | tee -a "$WLOG"

# --- launch R1 detached (survives this orchestrator exiting) ---
log "─── launching R1 magnitude (113 baseline + concave_d050, --save-trajectory) ───"
ENV_TAG="r1_$(date +%H%M)"
nohup env NPROC=2 N_STEPS="${N_STEPS:-8000}" ECOPHYS_ENV=ecophys \
  PATH="/root/miniconda3/bin:$PATH" \
  bash scripts/gpu_exp123_stage1.sh r1 >"experiments/123_driven_transient/_r1_${ENV_TAG}.log" 2>&1 &
R1_PID=$!
log "R1 launched PID $R1_PID → experiments/123_driven_transient/_r1_${ENV_TAG}.log"
log "monitor: tail -f experiments/123_driven_transient/_r1_${ENV_TAG}.log"
log "═══ wait_then_r1 orchestration DONE (R1 running detached) ═══"
