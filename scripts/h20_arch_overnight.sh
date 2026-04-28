#!/usr/bin/env bash
# Master driver — feature/arch-extensions overnight batch.
# Runs experiments/037..044 sequentially with SKIP_DONE=1, so the run
# is recoverable if interrupted partway (next launch picks up where
# the previous one left off).
#
# Usage:
#   ssh h20 'cd ecophys && git pull && DAEMON=1 bash scripts/h20_arch_overnight.sh'
#
# Total ~3-4h on 8-card config-parallel.
#
# Env knobs:
#   DAEMON=1              run in background, return PID
#   SKIP_DONE=0           force re-run even if output exists (default 1)
#   PARALLEL=8            configs in flight per dir (default 8)
#   NPROC=1               ranks per torchrun job (default 1; 8 enables DDP eval)
#
# Per-dir runs use scripts/h20_run_phase.sh under the hood. After all
# 8 dirs finish, scoreboards are produced for each.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

DIRS=(
    "experiments/037_arch_tier_1_1_memory"
    "experiments/040_arch_tier_2_1_jumps"
    "experiments/042_arch_tier_3_1_isab"
    "experiments/045_arch_tier_4_1_megnet"
    "experiments/047_arch_tier_4_2_dyngraph"
    "experiments/038_arch_tier_1_2_kernels"
    "experiments/039_arch_tier_1_3_features"
    "experiments/041_arch_tier_2_2_multitimescale"
    "experiments/043_arch_pairs"
    "experiments/046_arch_megnet_pairs"
    "experiments/048_arch_dyngraph_pairs"
    "experiments/044_arch_all_stacked"
)

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
MASTER_LOG="experiments/_arch_overnight_${TIMESTAMP}.log"

run_main() {
    echo "═══ ARCH OVERNIGHT — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"

    if [[ "${1:-}" == "--dry-run" ]]; then
        echo "DRY RUN — listing configs only" | tee -a "$MASTER_LOG"
        for d in "${DIRS[@]}"; do
            n=$(ls "$d"/config_*.yaml 2>/dev/null | wc -l)
            echo "  $d: $n configs" | tee -a "$MASTER_LOG"
        done
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
