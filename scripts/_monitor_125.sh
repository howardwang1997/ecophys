#!/usr/bin/env bash
# exp 125 — periodic status logger. Appends one compact snapshot every POLL sec to
# _monitor.log. Each node is probed over SSH for GPU util + DONE marker + current arm.
# Detached-safe: setsid bash scripts/_monitor_125.sh </dev/null >>_monitor.out 2>&1 &
# Watch-only; never stops the runs.
set -uo pipefail
REPO="/AI4S/Users/howardwang/h204/ecophys"
EXP="experiments/125_rootcause_controllability"
P="$REPO/$EXP"
LOG="$P/_monitor.log"
POLL="${POLL:-600}"
sleep 5   # brief startup delay so the launcher's command channel closes before first SSH probe

probe(){  # $1=ip $2=key(gpu8/gpu2b) $3=marker(EXP125_8CARD_DONE / EXP125_2CARDB_DONE)
  ssh -o ConnectTimeout=8 "$1" "
    if grep -q '$3' $P/_node_$2_*.log 2>/dev/null; then s=DONE; else s=run; fi
    g=\$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader 2>/dev/null | tr '\n' ' ')
    a=\$(grep -hoE 'ASSET=[a-z]+|results_[a-z0-9._]+/(atlas|rigor|dose|root)' $P/_node_$2_*.log 2>/dev/null | tail -1)
    printf '%s[%s]: gpu=[%s] %s\n' '$2' \"\$s\" \"\$g\" \"\$a\"
  " 2>/dev/null
}

while true; do
  ts="$(date '+%F %T')"
  npz=$(find "$P"/results_*/*/trajectory_*.npz 2>/dev/null | wc -l)
  watch=$(pgrep -f _wait_then_push_125 >/dev/null 2>&1 && echo alive || echo DEAD)
  mest=$(kill -0 1255561 2>/dev/null && echo run || echo done)
  mgpu=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader 2>/dev/null | tr '\n' ' ')
  marm=$(grep -hoE 'ASSET=[a-z]+|results_[a-z0-9._]+/(atlas|rigor|dose|root)' "$P"/_run_*.log 2>/dev/null | tail -1)
  {
    echo "── $ts ── global_npz=$npz watcher=$watch"
    echo "  $(probe 10.239.69.71 gpu8  EXP125_8CARD_DONE)"
    echo "  $(probe 10.239.72.172 gpu2b EXP125_2CARDB_DONE)"
    echo "  me[$mest]: gpu=[$mgpu] $marm"
  } >> "$LOG" 2>&1
  sleep "$POLL"
done
