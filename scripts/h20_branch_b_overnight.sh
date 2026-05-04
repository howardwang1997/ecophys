#!/usr/bin/env bash
# Branch B overnight — clean-physics ablation + U(t) energy logging.
#
# Code change: ecomd/models/potentials.py:conservative_forces now optionally
# returns U_value. Wired through ecomd.py:step → record dict → TrajectoryRecorder
# → EcoMDTrajectory.total_potential → run_large.py npz output.
#
# Inference traces saved as trajectory_rank0_r{i}.npz now contain
# `total_potential` (T,) for Paper-B Jarzynski W = ΔU bookkeeping. Existing
# pipelines (training, scoring) untouched — total_potential is optional.
#
# Experiment 074: 5 cells × 30 seeds = 150 configs. Each cell freezes T=0.05,
# γ=10 (E1's overdamped fix) and strips ONE memory injector. Diagnoses which
# v3 architecture component contributes most to the residual AR(1) drift.
#
# Estimated H20 wall ~3-4h on 8-card config-parallel.
#
# Usage (on H20):
#   ssh h20
#   cd ecophys
#   git fetch --all && git checkout feature/gradient-potential-v4 && git pull
#   unset NPROC && bash scripts/h20_refresh_deps.sh
#   DAEMON=1 bash scripts/h20_branch_b_overnight.sh
#   tail -f experiments/_branch_b_*.log

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

DIRS=(
    "experiments/074_clean_physics_ablation"
)

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_branch_b_${TIMESTAMP}.log"

run_main() {
    echo "═══ BRANCH B OVERNIGHT — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"

    if [[ "${1:-}" == "--dry-run" ]]; then
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
        echo "═══ PHASE: $d ═══ $(date) ═══" | tee -a "$MASTER_LOG"
        SECONDS=0
        if ! bash scripts/h20_run_phase.sh "$d" 2>&1 | tee -a "$MASTER_LOG"; then
            echo "  [WARN] phase $d returned non-zero; continuing" | tee -a "$MASTER_LOG"
        fi
        echo "  [phase $d] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
    done

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ SCORING — $(date) ═══" | tee -a "$MASTER_LOG"
    for d in "${DIRS[@]}"; do
        conda run -n ecophys python scripts/score_phase.py "$d" 2>&1 | tee -a "$MASTER_LOG" || \
            echo "  [WARN] scoring failed for $d" | tee -a "$MASTER_LOG"
    done

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ BRANCH B DONE — $(date) ═══" | tee -a "$MASTER_LOG"
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
