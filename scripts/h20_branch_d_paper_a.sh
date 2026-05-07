#!/usr/bin/env bash
# Branch D — Paper A v4 mechanisms + baselines + cross-asset.
#
# Six experiment dirs:
#   073 Hawkes/jump ablation (leftover from Branch A)     48 cfgs
#   075 adiabatic inner_3/inner_10 (leftover from C)      60 cfgs
#   077 Lévy noise α∈{1.5,1.7,1.9}                        90 cfgs
#   078 asymmetric drag α∈{0.3,0.6,0.9}                   90 cfgs
#   079 memory kernel (λ,strength) sweep                  90 cfgs
#   080 baselines (GBM, GARCH, AR1+SV, Lux-Marchesi)     120 cfgs (CPU-only, separate runner)
#   081 BTC cross-asset (baseline + v4 combo)             60 cfgs
#
# Total GPU configs: 438 (073+075+077+078+079+081)
# Estimated H20 wall: 438 × 14min / 8 cards ≈ 12.8h
#
# Baselines (080) run separately via scripts/run_baseline.py on CPU
# (each takes ~2s, total ~4 min). We launch them in parallel on the
# H20 CPU side while GPU training runs.
#
# Usage (on H20):
#   ssh h20
#   cd ecophys
#   git fetch --all && git checkout feature/paper-a-v4-mechanisms && git pull
#   unset NPROC && bash scripts/h20_refresh_deps.sh
#   DAEMON=1 bash scripts/h20_branch_d_paper_a.sh
#   tail -f experiments/_branch_d_*.log

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

GPU_DIRS=(
    "experiments/073_hawkes_jump_ablation"
    "experiments/075_adiabatic_30seed"
    "experiments/077_levy_noise_30seed"
    "experiments/078_asym_drag_30seed"
    "experiments/079_memory_kernel_30seed"
    "experiments/081_btc_30seed"
)

BASELINE_DIR="experiments/080_baselines_30seed"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_branch_d_${TIMESTAMP}.log"

run_baselines_background() {
    echo "═══ BASELINES (CPU, background) — $(date) ═══" | tee -a "$MASTER_LOG"
    local n_done=0
    local n_total=$(ls "$BASELINE_DIR"/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
    echo "  baseline configs: $n_total" | tee -a "$MASTER_LOG"

    for cfg in "$BASELINE_DIR"/config_*.yaml; do
        local label=$(basename "$cfg" .yaml | sed 's/^config_//')
        local outdir="$BASELINE_DIR/results_${label}"
        if [[ "$SKIP_DONE" == "1" && -f "$outdir/inference_merged.json" ]]; then
            ((n_done++)) || true
            continue
        fi
        # Run in background, limit to 8 concurrent
        while (( $(jobs -rp | wc -l) >= 8 )); do
            sleep 1
        done
        (
            conda run -n ecophys python scripts/run_baseline.py \
                --config "$cfg" --out-dir "$outdir" >> "$MASTER_LOG" 2>&1
        ) &
    done
    wait
    echo "  baselines done: $n_total total, $n_done skipped" | tee -a "$MASTER_LOG"
}

run_main() {
    echo "═══ BRANCH D — PAPER A V4 — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"

    if [[ "${1:-}" == "--dry-run" ]]; then
        echo "DRY RUN — listing configs only" | tee -a "$MASTER_LOG"
        local total=0
        for d in "${GPU_DIRS[@]}"; do
            n=$(ls "$d"/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
            total=$((total + n))
            echo "  $d: $n configs" | tee -a "$MASTER_LOG"
        done
        n=$(ls "$BASELINE_DIR"/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
        echo "  $BASELINE_DIR: $n configs (CPU)" | tee -a "$MASTER_LOG"
        echo "  GPU total: $total configs" | tee -a "$MASTER_LOG"
        echo "  Estimated H20 wall: ~12.8h (438 cfgs × 14min / 8 cards)" | tee -a "$MASTER_LOG"
        return 0
    fi

    # Launch baselines in background (CPU-only, fast)
    run_baselines_background &
    baseline_pid=$!

    # GPU phases
    for d in "${GPU_DIRS[@]}"; do
        echo "" | tee -a "$MASTER_LOG"
        echo "═══ PHASE: $d ═══ $(date) ═══" | tee -a "$MASTER_LOG"
        SECONDS=0
        if ! bash scripts/h20_run_phase.sh "$d" 2>&1 | tee -a "$MASTER_LOG"; then
            echo "  [WARN] phase $d returned non-zero; continuing" | tee -a "$MASTER_LOG"
        fi
        echo "  [phase $d] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
    done

    # Wait for baselines to finish
    echo "" | tee -a "$MASTER_LOG"
    echo "═══ WAITING FOR BASELINES — $(date) ═══" | tee -a "$MASTER_LOG"
    wait "$baseline_pid" || echo "  [WARN] baselines returned non-zero" | tee -a "$MASTER_LOG"

    # Scoring
    echo "" | tee -a "$MASTER_LOG"
    echo "═══ SCORING — $(date) ═══" | tee -a "$MASTER_LOG"
    for d in "${GPU_DIRS[@]}" "$BASELINE_DIR"; do
        conda run -n ecophys python scripts/score_phase.py "$d" 2>&1 | tee -a "$MASTER_LOG" || \
            echo "  [WARN] scoring failed for $d" | tee -a "$MASTER_LOG"
    done

    # Continuous scoring (all dirs together)
    echo "" | tee -a "$MASTER_LOG"
    echo "═══ CONTINUOUS SCORING — $(date) ═══" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_continuous.py \
        "${GPU_DIRS[@]}" "$BASELINE_DIR" \
        --csv experiments/_branch_d_continuous_${TIMESTAMP}.csv \
        --target-dataset spx --target-period 2015-2026_daily \
        2>&1 | tee -a "$MASTER_LOG" || \
        echo "  [WARN] continuous scoring failed" | tee -a "$MASTER_LOG"

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ BRANCH D DONE — $(date) ═══" | tee -a "$MASTER_LOG"
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
