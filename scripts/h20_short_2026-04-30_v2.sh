#!/usr/bin/env bash
# Short batch 2026-04-30 v2 — extends v1 to keep exploring the
# 4.2 + 2.1 architecture after 052's regression-to-mean finding
# (35-seed mean 5.40, NOT 7.20; 10/11 ceiling at seed21).
#
# Priority order (small first, OOM-risky last):
#   056_v2_type_seed_sweep       12 cfgs — type_seed CI (NeurIPS-grade)
#   053_p_4_2__2_1_jump_tune     18 cfgs — λ × σ grid (already queued in v1)
#   054_p_4_2__2_1_triples       15 cfgs — full + 2.1 + (1.1/1.2/1.3) (already queued in v1)
#   055_chunk_n_tradeoff         25 cfgs — (N, chunk, h) memory tradeoff
#                                          Includes (N=5K, chunk=48) and
#                                          (N=2.5K, chunk=96) — first time
#                                          we test chunk > 24
#
# Total 70 configs, ~90-105 min on 8-card config-parallel.
# SKIP_DONE=1 so anything already done by v1 gets skipped automatically.
#
# WARNING: 055 cells nh_n2k5_c96 and possibly nh_n5k_c48 may OOM. Memory
# model says they should fit (N×chunk×h² roughly conserved) but real
# memory ≠ model. SKIP_DONE=1 means failed configs leave gaps but the
# successful ones still produce signal.
#
# Usage:
#   ssh h20
#   cd ecophys
#   git fetch --all && git checkout feature/megnet-global-state && git pull
#   unset NPROC; bash scripts/h20_refresh_deps.sh
#   DAEMON=1 bash scripts/h20_short_2026-04-30_v2.sh
#   tail -f experiments/_short_2026-04-30_v2_*.log

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

DIRS=(
    "experiments/056_v2_type_seed_sweep"
    "experiments/053_p_4_2__2_1_jump_tune"
    "experiments/054_p_4_2__2_1_triples"
    "experiments/055_chunk_n_tradeoff"
)

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_short_2026-04-30_v2_${TIMESTAMP}.log"

run_main() {
    echo "═══ SHORT 2026-04-30 v2 — $(date) ═══" | tee -a "$MASTER_LOG"
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
