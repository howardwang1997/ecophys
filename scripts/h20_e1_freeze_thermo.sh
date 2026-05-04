#!/usr/bin/env bash
# E1 — train 24 configs with frozen (T_eff, gamma_eff) at 4 (T, gamma) points.
#
# Hypothesis chain:
#   - E2 (Mac, 50 seeds): all checkpoints kept T≈0.052, γ≈0.98 — model did NOT
#     suppress noise. autocorr=0.6 is structural.
#   - E1 (this script): freeze (T, γ) and vary them. Test:
#       freezeTG_T05_g1   — sanity: same as init (autocorr should reproduce ~0.6)
#       freezeTG_T20_g1   — 4× noise floor; autocorr should drop a bit
#       freezeTG_T05_g10  — push toward overdamped (γ·dt=0.1); autocorr drops more
#       freezeTG_T05_g100 — fully overdamped (γ·dt=1.0); autocorr should hit ~0
#
# Each cell × 6 seeds = 24 runs. Estimated H20 wall ~3-4h on 8-card config-parallel.
#
# Usage (on H20):
#   ssh h20
#   cd ecophys
#   git fetch --all && git checkout diagnostics/autocorr-ar1 && git pull
#   unset NPROC; bash scripts/h20_refresh_deps.sh
#   DAEMON=1 bash scripts/h20_e1_freeze_thermo.sh
#   tail -f experiments/_e1_freeze_thermo_*.log

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

DIRS=(
    "experiments/067_ar1_diagnostics"
)

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_e1_freeze_thermo_${TIMESTAMP}.log"

run_main() {
    echo "═══ E1 FREEZE-THERMO BATCH — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"

    if [[ "${1:-}" == "--dry-run" ]]; then
        for d in "${DIRS[@]}"; do
            n=$(ls "$d"/config_*.yaml 2>/dev/null | wc -l)
            echo "  $d: $n configs" | tee -a "$MASTER_LOG"
        done
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
    echo "═══ E1 DONE — $(date) ═══" | tee -a "$MASTER_LOG"
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
