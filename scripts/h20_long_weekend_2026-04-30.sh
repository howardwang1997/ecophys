#!/usr/bin/env bash
# 3-day long-weekend H20 batch — 14 dirs, 455 configs, est ~10-15h total
# wall time on 8-card config-parallel. SKIP_DONE=1 means crashes don't
# lose work and re-launching picks up where we left off.
#
# Design rationale:
# - 052 showed `p_4_2__2_1` regresses to 5.40 mean at 35 seeds (the 7.20
#   was 5-seed lottery). New code (bf16, rollout_reg) tries to lift mean
#   beyond 5.40 by attacking train/eval horizon mismatch (24→4000 step).
# - Order: small new-code dirs first (fail fast), then bigger sweeps,
#   then slow runs last.
#
# Phase order:
#   v2 batch (already designed, SKIP_DONE-auto-skips if done):
#     056_v2_type_seed_sweep         12 cfgs
#     053_p_4_2__2_1_jump_tune       18 cfgs
#     054_p_4_2__2_1_triples         15 cfgs
#     055_chunk_n_tradeoff           25 cfgs
#
#   NEW code, fail-fast (run first to surface bugs early):
#     057_rollout_reg_sweep          30 cfgs — exercises rollout_reg path
#     058_bf16_chunk_sweep           30 cfgs — exercises bf16 path
#     059_bf16_rollout_combo         32 cfgs — both new paths
#
#   Mid-size sweeps (no new code):
#     062_type_seed_deep             40 cfgs — paper-grade type_seed CI
#     063_winner_arch_retest         32 cfgs — new tier combos at winner
#     061_lr_niters_sweep            48 cfgs — convergence study
#     060_jump_grid_wide             75 cfgs — full 5×5 jump basin
#
#   Big runs (slowest, last):
#     064_winner_50seed_repro        50 cfgs — winner @ 50 more seeds
#     065_long_training              24 cfgs — n_iters=400/800
#     066_bigN_bf16                  24 cfgs — N=15K/20K (paper-grade)
#
# Usage:
#   ssh h20
#   cd ecophys
#   git fetch --all && git checkout feature/megnet-global-state && git pull
#   unset NPROC; bash scripts/h20_refresh_deps.sh
#   DAEMON=1 bash scripts/h20_long_weekend_2026-04-30.sh
#   tail -f experiments/_long_weekend_*.log

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

DIRS=(
    # v2 batch (skip if already done)
    "experiments/056_v2_type_seed_sweep"
    "experiments/053_p_4_2__2_1_jump_tune"
    "experiments/054_p_4_2__2_1_triples"
    "experiments/055_chunk_n_tradeoff"
    # NEW code paths first — fail fast if bf16 / rollout_reg break
    "experiments/057_rollout_reg_sweep"
    "experiments/058_bf16_chunk_sweep"
    "experiments/059_bf16_rollout_combo"
    # Mid sweeps
    "experiments/062_type_seed_deep"
    "experiments/063_winner_arch_retest"
    "experiments/061_lr_niters_sweep"
    "experiments/060_jump_grid_wide"
    # Big slow runs last
    "experiments/064_winner_50seed_repro"
    "experiments/065_long_training"
    "experiments/066_bigN_bf16"
)

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_long_weekend_${TIMESTAMP}.log"

run_main() {
    echo "═══ LONG-WEEKEND BATCH 2026-04-30 — $(date) ═══" | tee -a "$MASTER_LOG"
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

    # Phase loop. Each phase is wrapped so a crash in one doesn't kill
    # the rest — important for 3-day autonomous runs.
    for d in "${DIRS[@]}"; do
        echo "" | tee -a "$MASTER_LOG"
        echo "═══ PHASE: $d ═══ $(date) ═══" | tee -a "$MASTER_LOG"
        SECONDS=0
        if ! bash scripts/h20_run_phase.sh "$d" 2>&1 | tee -a "$MASTER_LOG"; then
            echo "  [WARN] phase $d returned non-zero; continuing to next phase" | tee -a "$MASTER_LOG"
        fi
        echo "  [phase $d] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
    done

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ SCORING ALL DIRS — $(date) ═══" | tee -a "$MASTER_LOG"
    for d in "${DIRS[@]}"; do
        echo "" | tee -a "$MASTER_LOG"
        echo "── score $d ──" | tee -a "$MASTER_LOG"
        conda run -n ecophys python scripts/score_phase.py "$d" 2>&1 | tee -a "$MASTER_LOG" || \
            echo "  [WARN] scoring failed for $d" | tee -a "$MASTER_LOG"
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
