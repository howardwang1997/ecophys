#!/usr/bin/env bash
# Branch A overnight — config-only sweeps on existing arch (no code change).
#   069 γ damping × 30 seeds = 150 (lottery-rule confirmation of E1 finding)
#   070 rr_s120 × 30 seeds   = 120 (only positive non-AR(1) score lift signal)
#   071 T-γ combo × 30        =  60 (best-of-both-worlds hypothesis)
#   072 σ_ed gentler × 8      =  32 (probe before scaling)
#   073 Hawkes/jump ablation  =  48 (decompose the AR(1) drift sources)
#
# Total 410 configs. Estimated H20 wall ~5-7h on 8-card config-parallel.
#
# Usage (on H20):
#   ssh h20
#   cd ecophys
#   git fetch --all && git checkout diagnostics/autocorr-ar1 && git pull
#   unset NPROC && bash scripts/h20_refresh_deps.sh
#   DAEMON=1 bash scripts/h20_branch_a_overnight.sh
#   tail -f experiments/_branch_a_*.log

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

DIRS=(
    # Order: confirmation first (smallest lottery uncertainty), then probes
    "experiments/069_gamma_damping_30seed"
    "experiments/070_rr_30seed_retest"
    "experiments/071_T_gamma_combo"
    "experiments/073_hawkes_jump_ablation"
    "experiments/072_sigma_ed_gentler"
)

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_branch_a_${TIMESTAMP}.log"

run_main() {
    echo "═══ BRANCH A OVERNIGHT — $(date) ═══" | tee -a "$MASTER_LOG"
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
    echo "═══ BRANCH A DONE — $(date) ═══" | tee -a "$MASTER_LOG"
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
