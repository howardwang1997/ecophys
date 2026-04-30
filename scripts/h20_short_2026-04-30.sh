#!/usr/bin/env bash
# Short batch 2026-04-30 — repro + tune + extend the 048 9/11 winner.
#
# Priority order (small dirs first, fastest signal):
#   052_p_4_2__2_1_repro       30 cfgs — confirm 7.20/11 mean is real (not 5-seed lottery)
#   053_p_4_2__2_1_jump_tune   18 cfgs — λ × σ grid around (0.5, 0.01)
#   054_p_4_2__2_1_triples     15 cfgs — winner + (1.1 / 1.2 / 1.3) × 5 seeds each
#
# Total 63 configs, ~75-90 min on 8-card config-parallel.
#
# WARNING: 054 cell tri_42_21_13 (winner + 1.3 features_all) may NaN
# the same way 048 p_4_2__1_3 did — full 4.2 (with u) + features path
# was unstable even with LN. Run anyway; if it works it's the most
# interesting result. SKIP_DONE=1 means a partial-eval batch can be
# completed by re-launching.
#
# Usage:
#   ssh h20
#   cd ecophys
#   git fetch --all && git checkout feature/megnet-global-state && git pull
#   unset NPROC; bash scripts/h20_refresh_deps.sh
#   DAEMON=1 bash scripts/h20_short_2026-04-30.sh
#   tail -f experiments/_short_2026-04-30_*.log

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

DIRS=(
    "experiments/052_p_4_2__2_1_repro"
    "experiments/053_p_4_2__2_1_jump_tune"
    "experiments/054_p_4_2__2_1_triples"
)

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_short_2026-04-30_${TIMESTAMP}.log"

run_main() {
    echo "═══ SHORT 2026-04-30 — $(date) ═══" | tee -a "$MASTER_LOG"
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
