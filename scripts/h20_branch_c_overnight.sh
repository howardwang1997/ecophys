#!/usr/bin/env bash
# Branch C overnight — v4 dynamics framework + model architecture additions.
#
# Two new code features (Mac-side, both committed in feature/adiabatic-collective):
#
#  1. ADIABATIC TIMESCALE SEPARATION (动力学框架):
#     - Added EcoMDConfig.inner_steps_per_price (default 1 = backward compat).
#     - When > 1, ecomd.py:step runs that many agent dynamics steps per
#       price formation update. Slow state (price, regime, agent_memory,
#       global_state) is FROZEN during the inner loop.
#     - Targets AR(1) drift root cause: per outer-step return = sum of
#       inner_n independent agent walks → much closer to random walk.
#     - Mori-Zwanzig adiabatic limit: ε = 1/inner_n.
#
#  2. COLLECTIVE COORDINATE PRICE (模型架构):
#     - New ecomd/models/price_formation.py:CollectivePrice +
#       CollectiveParams + 'collective' registry entry.
#     - p(t) = log[1 + Σ_i weight_i · intent_i(s_i)]; uses FULL agent state,
#       not just s[:,0] like the hand-crafted ExcessDemand.
#     - Permutation-invariant by construction (test in test_adiabatic_collective).
#     - No Hawkes self-excitation (kept clean for FDT/Jarzynski).
#     - Standard Mori-Zwanzig collective coordinate; Paper-B physics chain
#       traces from agent dynamics → ED → price cleanly.
#
# Tests (all passing on Mac):
#   tests/test_adiabatic_collective.py — 6 tests:
#     adiabatic inner=1 baseline shape
#     inner=5 increases per-outer motion ≥1.5×
#     CollectivePrice basic step finite
#     CollectivePrice permutation invariance
#     CollectivePrice end-to-end through simulator
#     adiabatic + collective compose
#
# Experiments tonight (210 configs total, est ~5h on 8-card config-parallel):
#   075 adiabatic × 30 seeds × 4 cells (inner ∈ {1,5,10,20}, all γ=10)  — 120
#   076 collective × 30 seeds × 3 cells (g1, g10, g10_inner5)            —  90
#
# Usage:
#   ssh h20 'cd ecophys && \
#       git fetch --all && \
#       git checkout feature/adiabatic-collective && git pull && \
#       unset NPROC && bash scripts/h20_refresh_deps.sh && \
#       DAEMON=1 bash scripts/h20_branch_c_overnight.sh'
#
# Run in a SEPARATE WORKTREE on H20 if Branch A and Branch B are already
# running there (single git tree per branch).

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

DIRS=(
    "experiments/075_adiabatic_30seed"
    "experiments/076_collective_price_30seed"
)

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_branch_c_${TIMESTAMP}.log"

run_main() {
    echo "═══ BRANCH C OVERNIGHT — $(date) ═══" | tee -a "$MASTER_LOG"
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
    echo "═══ BRANCH C DONE — $(date) ═══" | tee -a "$MASTER_LOG"
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
