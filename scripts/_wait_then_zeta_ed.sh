#!/usr/bin/env bash
# Scratch orchestrator: wait for the 117_leverage sweep to drain (driver 626224 gone +
# GPU compute-apps empty), then auto-launch the ζ_ED measurement. Detached-safe:
# launch with `setsid bash scripts/_wait_then_zeta_ed.sh &` so it survives session drops.
#
# Idle trigger = nvidia-smi compute-apps == 0 on 2 consecutive polls (guards against the
# brief between-config gap). 121_heldout is already 120/120 done; nothing else is queued.
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DRIVER_PID="${DRIVER_PID:-626224}"          # bash h20_run_phase.sh experiments/117_leverage
POLL="${POLL:-180}"                          # seconds between polls (3 min)
STABLE_NEEDS="${STABLE_NEEDS:-2}"            # consecutive idle polls to trigger
MAX_WAIT="${MAX_WAIT:-72h}"                  # hard cap so we never wait forever
TS="$(date +%Y%m%d_%H%M%S)"
WLOG="experiments/_wait_then_zeta_${TS}.log"
ZETA_LOG_GLOB="experiments/_zeta_ed_*.log"

AMAR="/AI4S/Users/howardwang/h202_amar/ecophys"
GPU_SCRIPT="scripts/gpu_zeta_ed_2card.sh"
EXP="experiments/122_zeta_ed"

log() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$WLOG"; }

gpu_busy() { local n; n=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | wc -l); echo "$n"; }
ck117_done() { ls "$AMAR"/experiments/117_leverage/results_*/checkpoint.pt 2>/dev/null | wc -l; }

log "═══ wait_then_zeta START ═══"
log "watching driver PID=$DRIVER_PID; poll=${POLL}s; stable=$STABLE_NEEDS; max_wait=$MAX_WAIT"
log "117 checkpoints present at start: $(ck117_done)/180"

# --- preflight (fail fast if the ζ_ED prereqs vanished while waiting) ---
preflight() {
  local missing=0
  for c in \
    experiments/113_gabaix_solve/config_concave_d050_seed0.yaml \
    experiments/114_concave_confirm/config_ndx_concave_d050_seed0.yaml \
    experiments/114_concave_confirm/config_gold_concave_d050_seed0.yaml \
    experiments/114_concave_confirm/config_eurusd_concave_d050_seed0.yaml \
    experiments/114_concave_confirm/config_btcusdt_concave_d050_seed0.yaml ; do
    [ -f "$c" ] || { log "  [PREFLIGHT FAIL] missing $c"; missing=1; }
  done
  for ck in \
    experiments/113_gabaix_solve/results_concave_d050_seed0/checkpoint.pt \
    experiments/114_concave_confirm/results_ndx_concave_d050_seed0/checkpoint.pt \
    experiments/114_concave_confirm/results_gold_concave_d050_seed0/checkpoint.pt \
    experiments/114_concave_confirm/results_eurusd_concave_d050_seed0/checkpoint.pt \
    experiments/114_concave_confirm/results_btcusdt_concave_d050_seed0/checkpoint.pt ; do
    [ -f "$ck" ] || { log "  [PREFLIGHT FAIL] missing checkpoint $ck"; missing=1; }
  done
  [ -f "$GPU_SCRIPT" ] || { log "  [PREFLIGHT FAIL] missing $GPU_SCRIPT"; missing=1; }
  conda run -n ecophys which torchrun >/dev/null 2>&1 || { log "  [PREFLIGHT FAIL] torchrun not on ecophys"; missing=1; }
  return $missing
}

# --- wait loop ---
start=$(date +%s); max_s=$(( ${MAX_WAIT%h} * 3600 ))
stable=0
while true; do
  now=$(date +%s); elapsed=$((now - start))
  if [ $elapsed -gt $max_s ]; then log "MAX_WAIT $MAX_WAIT exceeded — giving up"; exit 2; fi
  busy=$(gpu_busy)
  drv_alive=0; kill -0 "$DRIVER_PID" 2>/dev/null && drv_alive=1
  if [ "$busy" -eq 0 ]; then
    stable=$((stable + 1))
  else
    stable=0
  fi
  # status line every poll (and final)
  log "poll: elapsed=${elapsed}s  gpu_procs=$busy  stable=$stable/$STABLE_NEEDS  driver${DRIVER_PID}_alive=$drv_alive  117_done=$(ck117_done)/180"
  if [ "$stable" -ge "$STABLE_NEEDS" ]; then
    log "GPU idle on $STABLE_NEEDS consecutive polls → trigger."
    break
  fi
  sleep "$POLL"
done

log "driver$DRIVER_PID alive at trigger? $drv_alive  (0=exited, the expected case)"
log "117 final: $(ck117_done)/180 checkpoints"

# --- preflight then launch ---
if ! preflight; then log "PREFLIGHT FAILED — not launching ζ_ED. Inspect $WLOG"; exit 3; fi
log "preflight OK (configs + checkpoints + torchrun present)"

log "─── STEP 1: ζ_ED probe (spx only) ───"
bash "$GPU_SCRIPT" --probe 2>&1 | tee -a "$WLOG"
probe_ok=0
if ls "$EXP"/results_spx/trajectory_*.npz >/dev/null 2>&1; then
  log "  ✓ probe produced spx trajectories: $(ls "$EXP"/results_spx/trajectory_*.npz | wc -l)"
  probe_ok=1
else
  log "  ✗ probe did NOT produce spx trajectories — STOPPING (inspect $ZETA_LOG_GLOB)"
  exit 4
fi

log "─── STEP 2: ζ_ED daemon (remaining 4 assets + final scoring) ───"
# probe already did spx; skip it in daemon to avoid redo. run_all's final
# score_transfer_law --measure-zeta scans the whole EXP dir, so it still sees all 5.
ASSETS_OVERRIDE="ndx gold eurusd btcusdt" DAEMON=1 bash "$GPU_SCRIPT" >>"$WLOG" 2>&1
log "daemon handed off. Latest ζ_ED log: $(ls -t $ZETA_LOG_GLOB 2>/dev/null | head -1)"
log "monitor: tail -f $WLOG  ;  tail -f $(ls -t $ZETA_LOG_GLOB 2>/dev/null | head -1)"
log "═══ wait_then_zeta orchestration DONE ═══"
