#!/usr/bin/env bash
# One-shot status snapshot for the wait_then_zeta orchestration. Print compact, single-block.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$REPO_ROOT"
AMAR="/AI4S/Users/howardwang/h202_amar/ecophys"

orch=$(pgrep -af "_wait_then_zeta_ed" | grep -v grep | awk '{print $1}' | head -1)
[ -n "$orch" ] && orch="ALIVE(pid $orch)" || orch="DEAD ⚠"
gpu_procs=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | wc -l)
gpu_util=$(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | tr '\n' ' ')
done117=$(ls "$AMAR"/experiments/117_leverage/results_*/training_log.json 2>/dev/null | wc -l)
drv=$(kill -0 626224 2>/dev/null && echo alive || echo exited)
wlog=$(ls -t experiments/_wait_then_zeta_*.log 2>/dev/null | head -1)
zlog=$(ls -t experiments/_zeta_ed_*.log 2>/dev/null | head -1)
zeta_npz=$(ls experiments/122_zeta_ed/results_*/trajectory_*.npz 2>/dev/null | wc -l)
zeta_rep=$([ -f experiments/122_zeta_ed/zeta_ed_report.json ] && echo yes || echo no)

echo "── $(date '+%F %T') ──"
echo "orchestrator : $orch"
echo "GPU          : procs=$gpu_procs  util/mem=[$gpu_util]"
echo "117 driver   : $drv   |  117_done = $done117/180"
echo "ζ_ED started : npz=$zeta_npz  report=$zeta_rep"
echo "last wait-log: $(grep -E 'poll:|STEP|trigger|probe' "$wlog" 2>/dev/null | tail -1)"
if [ -n "$zlog" ]; then echo "last zeta-log: $(tail -1 "$zlog" 2>/dev/null)"; fi
