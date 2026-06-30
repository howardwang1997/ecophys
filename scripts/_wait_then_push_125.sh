#!/usr/bin/env bash
# exp 125 — end-to-end watcher. Polls all 3 nodes for completion, then runs eval +
# commits + pushes the results (and the btc->btcusdt + git-pull-nonfatal orchestrator
# fixes) to feature/paper-a-figures-voice. Detached-safe: setsid bash ... &
#
# Completion = (local launch PID gone AND my GPU idle) AND 8-card log has
# EXP125_8CARD_DONE AND 2-card-b log has EXP125_2CARDB_DONE. All 3 nodes write to the
# shared GPFS h204 checkout, so gather is a no-op (results already centralized) -> skip
# straight to eval. "一直跑不要停": this only WATCHES; it never kills the runs.
set -uo pipefail
REPO_ROOT="/AI4S/Users/howardwang/h204/ecophys"; cd "$REPO_ROOT"
export PATH=/root/miniconda3/bin:${PATH:-}
EXP="experiments/125_rootcause_controllability"
BR="feature/paper-a-figures-voice"
LAUNCH_PID="${LAUNCH_PID:-1255561}"        # the `... orchestrate.sh launch` setsid PID
CARD8="10.239.69.71"; CARD2B="10.239.72.172"
POLL="${POLL:-300}"; STABLE_NEEDS="${STABLE_NEEDS:-1}"; MAX_WAIT="${MAX_WAIT:-16h}"
TS="$(date +%Y%m%d_%H%M%S)"; WLOG="${EXP}/_waitpush_${TS}.log"

log(){ printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$WLOG"; }
my_gpu_busy(){ local n; n=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | wc -l); echo "$n"; }
local_done(){ kill -0 "$LAUNCH_PID" 2>/dev/null && echo 0 || echo 1; }   # 1 = launch exited
node_done(){ ssh -o ConnectTimeout=10 "$1" "grep -q '$2' ${EXP}/_node_${3}_*.log 2>/dev/null && echo 1 || echo 0" 2>/dev/null | tr -d '\n'; }

log "═══ exp125 waitpush START ═══"
log "watching: local launch PID=$LAUNCH_PID, 8card=$CARD8 (EXP125_8CARD_DONE), 2cardb=$CARD2B (EXP125_2CARDB_DONE)"
log "poll=${POLL}s stable=$STABLE_NEEDS max_wait=$MAX_WAIT"

start=$(date +%s); max_s=$(( ${MAX_WAIT%h} * 3600 )); stable=0
# rich per-poll status (the periodic monitor): global npz + each node GPU util
gp8(){ ssh -o ConnectTimeout=8 "$CARD8"  'nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader 2>/dev/null|tr "\n" " "' 2>/dev/null; }
gp2(){ ssh -o ConnectTimeout=8 "$CARD2B" 'nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader 2>/dev/null|tr "\n" " "' 2>/dev/null; }
npz(){ find "$REPO_ROOT/$EXP"/results_*/*/trajectory_*.npz 2>/dev/null | wc -l; }
while true; do
  now=$(date +%s); elapsed=$((now - start))
  [ $elapsed -gt $max_s ] && { log "MAX_WAIT exceeded — giving up (inspect runs manually)"; exit 2; }
  ld="$(local_done)"; mb="$(my_gpu_busy)"
  d8="$(node_done "$CARD8"  EXP125_8CARD_DONE  gpu8)"
  d2="$(node_done "$CARD2B" EXP125_2CARDB_DONE gpu2b)"
  all=1
  { [ "$ld" = 1 ] && [ "$mb" -eq 0 ] && [ "$d8" = 1 ] && [ "$d2" = 1 ]; } || all=0
  [ "$all" = 1 ] && stable=$((stable+1)) || stable=0
  log "MONITOR elapsed=${elapsed}s npz=$(npz) | local_launch=$ld my_gpu=$mb | 8card[$d8] gpu=[$(gp8)] | 2cardb[$d2] gpu=[$(gp2)] | all=$all stable=$stable/$STABLE_NEEDS"
  [ "$stable" -ge "$STABLE_NEEDS" ] && { log "ALL 3 NODES DONE → trigger eval+push."; break; }
  sleep "$POLL"
done

# --- eval (windowed α(t) per arm + OFI; eval_all also commits $EXP/*.json + pushes) ---
log "─── EVAL ───"
if bash scripts/gpu_exp125_orchestrate.sh eval 2>&1 | tee -a "$WLOG" | tail -15; then
  log "eval exit OK"
else
  log "WARN: eval non-zero — proceeding to broader commit of raw results anyway"
fi

# --- broader commit + push (per-arm result JSONs + the orchestrator fixes) ---
log "─── COMMIT + PUSH (results + btc->btcusdt fix) ───"
git add experiments/125_rootcause_controllability scripts/gpu_exp125_orchestrate.sh 2>&1 | tail -1
staged=$(git diff --cached --numstat 2>/dev/null | wc -l)
log "staged $staged files (.gitignore drops npz/pt)."
if [ "$staged" -gt 0 ]; then
  git commit -m "exp 125 results: root-cause ablations + atlas + rigor + dose law

Run on 3-box fleet (8card atlas/rigor/dose/ablate + 2card-b btcusdt ablate + 2card
orchestrator ndx/btcusdt dose). Includes orchestrator fix: ASSET btc -> btcusdt (config
naming) + git-pull non-fatal under set -e for the shared GPFS checkout. Inference-only on
concave_d050 ckpts (5 assets). Per-arm windowed-hill + inference JSONs committed; raw
trajectory npz gitignored." 2>&1 | tee -a "$WLOG" | tail -3
  log "pushing (with rebase fallback)..."
  if git push origin "$BR" 2>&1 | tee -a "$WLOG" | tail -4; then
    log "✓ PUSHED to $BR ($(git rev-parse --short HEAD))"
  else
    log "non-fast-forward → rebase + retry"
    git pull --rebase -q origin "$BR" 2>&1 | tail -2 | tee -a "$WLOG"
    if git push origin "$BR" 2>&1 | tee -a "$WLOG" | tail -4; then
      log "✓ PUSHED after rebase ($(git rev-parse --short HEAD))"
    else
      log "✗ PUSH FAILED — commit local at $(git rev-parse --short HEAD); resolve manually"; exit 4
    fi
  fi
else
  log "nothing new to commit beyond eval_all's push."
fi
log "═══ exp125 waitpush DONE ═══"
