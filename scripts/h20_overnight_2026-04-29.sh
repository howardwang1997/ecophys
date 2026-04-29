#!/usr/bin/env bash
# Overnight 2026-04-29 — focused on Tier 4.2_no_u (the 6.10/11 winner).
#
# 4 phases, ~95 configs, ~1.5h on 8-card config-parallel:
#   048_arch_dyngraph_pairs    — retry partial-eval seeds (SKIP_DONE=1)
#   049_arch_4_2_no_u_repro    — 30 more seeds for tight CI on 6.10/11
#   050_arch_4_2_no_u_pairs    — gate × {1.1, 1.2, 1.3, 2.1} × 10 seeds
#   051_arch_4_2_no_u_triples  — gate + 1.3 + {1.1, 1.2, 2.1}; gate + 1.1 + 2.1
#
# Note on 048: p_4_2__1_3 cell still NaNs even with LN — the gate (which
# saw u via tier_4_2_dyngraph) + 1.3 features path is broken. The
# experiment is rerun in 050 as `p_42nu__1_3` (gate WITHOUT u + 1.3) which
# Mac smoke confirms is finite. So 048's p_4_2__1_3 will still NaN under
# this run but we keep it cycling for free in case we learn something.
#
# Usage:
#   ssh h20
#   cd ecophys
#   git fetch --all && git checkout feature/megnet-global-state && git pull
#   unset NPROC; bash scripts/h20_refresh_deps.sh
#   DAEMON=1 bash scripts/h20_overnight_2026-04-29.sh
#   tail -f experiments/_overnight_20260429_*.log

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

# Priority order: small dirs first (faster signal), then bigger ones.
DIRS=(
    "experiments/048_arch_dyngraph_pairs"           # retry partial evals
    "experiments/051_arch_4_2_no_u_triples"         # 20 cfgs — quickest novel signal
    "experiments/050_arch_4_2_no_u_pairs"           # 40 cfgs — pair combos
    "experiments/049_arch_4_2_no_u_repro"           # 30 cfgs — 4.2 alone repro
)

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_overnight_${TIMESTAMP}.log"

run_main() {
    echo "═══ OVERNIGHT 2026-04-29 — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"

    if [[ "${1:-}" == "--dry-run" ]]; then
        echo "DRY RUN — listing configs only" | tee -a "$MASTER_LOG"
        local total=0
        for d in "${DIRS[@]}"; do
            n=$(ls "$d"/config_*.yaml 2>/dev/null | wc -l)
            total=$((total + n))
            echo "  $d: $n configs" | tee -a "$MASTER_LOG"
        done
        echo "  total: $total configs" | tee -a "$MASTER_LOG"
        return 0
    fi

    for d in "${DIRS[@]}"; do
        echo "" | tee -a "$MASTER_LOG"
        echo "═══ PHASE: $d ═══" | tee -a "$MASTER_LOG"
        SECONDS=0
        bash scripts/h20_run_phase.sh "$d" 2>&1 | tee -a "$MASTER_LOG"
        echo "  [phase $d] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
    done

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ SCORING — $(date) ═══" | tee -a "$MASTER_LOG"
    for d in "${DIRS[@]}"; do
        echo "" | tee -a "$MASTER_LOG"
        echo "── score $d ──" | tee -a "$MASTER_LOG"
        conda run -n ecophys python scripts/score_phase.py "$d" 2>&1 | tee -a "$MASTER_LOG" || true
    done

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ ALL DONE — $(date) ═══" | tee -a "$MASTER_LOG"
}

if [[ "${1:-}" == "--dry-run" ]]; then
    run_main --dry-run
    exit 0
fi

if [[ "$DAEMON" == "1" ]]; then
    (run_main) >> "$MASTER_LOG" 2>&1 < /dev/null &
    pid=$!
    disown "$pid" 2>/dev/null || true
    echo "$pid" > "${MASTER_LOG}.pid"
    echo "started PID $pid; tail -f $MASTER_LOG"
else
    run_main
fi
