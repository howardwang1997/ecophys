#!/usr/bin/env bash
# Focused launcher for feature/megnet-global-state new experiments
# (Tiers 4.1 + 4.2 only). Runs the 4 new dirs sequentially:
#
#   045_arch_tier_4_1_megnet      — 20 configs (u into pair vs ext-only)
#   047_arch_tier_4_2_dyngraph    — 20 configs (gate w/ vs w/o u)
#   046_arch_megnet_pairs         — 15 configs (4_1 × {1.1, 3.1, 2.1})
#   048_arch_dyngraph_pairs       — 15 configs (4_2 × {1.1, 2.1, 1.3})
#
# Total 70 configs. ~1.5-2h on 8-card config-parallel.
#
# Usage:
#   ssh h20
#   cd ecophys
#   git fetch --all && git checkout feature/megnet-global-state && git pull
#   unset NPROC; bash scripts/h20_refresh_deps.sh
#   DAEMON=1 bash scripts/h20_megnet_run.sh
#
# Tail:
#   tail -f experiments/_megnet_run_*.log
#
# This is a separate driver (not h20_arch_overnight.sh) so we don't
# iterate over 037-044 just to SKIP_DONE-skip them.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

# Priority order: single tiers first (highest information per config),
# then pair combos.
DIRS=(
    "experiments/045_arch_tier_4_1_megnet"
    "experiments/047_arch_tier_4_2_dyngraph"
    "experiments/046_arch_megnet_pairs"
    "experiments/048_arch_dyngraph_pairs"
)

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
MASTER_LOG="experiments/_megnet_run_${TIMESTAMP}.log"

run_main() {
    echo "═══ MEGNet RUN — $(date) ═══" | tee -a "$MASTER_LOG"
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
