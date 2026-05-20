#!/usr/bin/env bash
# Re-run configs that failed due to missing EURUSD/NDX data.
# Data is now on H20; re-dispatch train+eval for the affected configs only.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-0}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_rerun_missing_${TIMESTAMP}.log"

# ── Collect failed config labels from the original log ──
ORIG_LOG="experiments/_weekend_20260515_111424.log"
if [[ ! -f "$ORIG_LOG" ]]; then
    echo "Original log not found: $ORIG_LOG" | tee -a "$MASTER_LOG"
    exit 1
fi

# Extract unique failed config names (remove card/exit suffix)
FAILED=$(grep "✗" "$ORIG_LOG" | sed 's/.*✗ //' | sed 's/ .*//' | sort -u | grep -E "eurusd|ndx|gold|btcusdt")
# Also include the trad_lm_gold failures
FAILED="${FAILED}
$(grep "✗" "$ORIG_LOG" | sed 's/.*✗ //' | sed 's/ .*//' | sort -u | grep 'trad_lm_gold')"
N_FAILED=$(echo "$FAILED" | sort -u | grep -c .)
echo "Re-running $N_FAILED failed configs" | tee -a "$MASTER_LOG"

# ── Helper functions ──
train_one() {
    local card="$1"; local label="$2"; local cfg="$3"; local outdir="$4"
    mkdir -p "$outdir"
    {
        echo "═ TRAIN $label (card $card) ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
        local start=$(date +%s)
        local job_log="$outdir/train_rerun_${TIMESTAMP}.log"
        CUDA_VISIBLE_DEVICES="$card" \
        timeout 2700 torchrun --nproc_per_node="$NPROC" --standalone \
            -m ecomd.training.train_distributed \
            --config "$cfg" --out-dir "$outdir" 2>&1 \
          | tee "$job_log" >> "$QUEUE_LOG"
        local exit_code=${PIPESTATUS[0]}
        local elapsed=$(( $(date +%s) - start ))
        if [[ $exit_code -eq 0 ]]; then
            echo "  ✓ $label ${elapsed}s (card $card)" | tee -a "$QUEUE_LOG"
        else
            echo "  ✗ $label exit=$exit_code ${elapsed}s (card $card)" | tee -a "$QUEUE_LOG"
        fi
    } &
}

eval_one() {
    local card="$1"; local label="$2"; local cfg="$3"; local outdir="$4"
    if [[ ! -f "$outdir/checkpoint.pt" ]]; then
        echo "  [skip-eval $label] no checkpoint" | tee -a "$QUEUE_LOG"
        return 0
    fi
    {
        echo "═ EVAL  $label (card $card) ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
        local start=$(date +%s)
        local elog="$outdir/eval_rerun_${TIMESTAMP}.log"
        CUDA_VISIBLE_DEVICES="$card" \
        timeout 2700 torchrun --nproc_per_node="$NPROC" --standalone \
            -m ecomd.inference.run_large \
            --ckpt "$outdir/checkpoint.pt" --config "$cfg" \
            --n-steps 4000 --n-realizations-per-rank 4 2>&1 \
          | tee "$elog" >> "$QUEUE_LOG"
        local exit_code=${PIPESTATUS[0]}
        local elapsed=$(( $(date +%s) - start ))
        if [[ $exit_code -eq 0 ]]; then
            echo "  ✓ eval $label ${elapsed}s (card $card)" | tee -a "$QUEUE_LOG"
        else
            echo "  ✗ eval $label exit=$exit_code (card $card)" | tee -a "$QUEUE_LOG"
        fi
    } &
}

run_traditional_one() {
    local card="$1"; local label="$2"; local cfg="$3"; local outdir="$4"
    rm -rf "$outdir"
    mkdir -p "$outdir"
    {
        echo "═ TRAD $label (card $card) ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
        local start=$(date +%s)
        CUDA_VISIBLE_DEVICES="$card" \
        timeout 600 conda run -n ecophys python scripts/run_traditional_baseline.py \
            --config "$cfg" --out-dir "$outdir" 2>&1 \
          | tee "${outdir}/traditional_rerun_${TIMESTAMP}.log" >> "$QUEUE_LOG"
        local exit_code=${PIPESTATUS[0]}
        local elapsed=$(( $(date +%s) - start ))
        if [[ $exit_code -eq 0 ]]; then
            echo "  ✓ $label ${elapsed}s (card $card)" | tee -a "$QUEUE_LOG"
        else
            echo "  ✗ $label exit=$exit_code ${elapsed}s (card $card)" | tee -a "$QUEUE_LOG"
        fi
    } &
}

run_baseline_one() {
    local card="$1"; local label="$2"; local cfg="$3"; local outdir="$4"
    rm -rf "$outdir"
    mkdir -p "$outdir"
    {
        echo "═ BASELINE $label (card $card) ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
        local start=$(date +%s)
        CUDA_VISIBLE_DEVICES="$card" \
        timeout 7200 conda run -n ecophys python scripts/run_baseline_fit_eval.py \
            --config "$cfg" --out-dir "$outdir" 2>&1 \
          | tee "${outdir}/baseline_rerun_${TIMESTAMP}.log" >> "$QUEUE_LOG"
        local exit_code=${PIPESTATUS[0]}
        local elapsed=$(( $(date +%s) - start ))
        if [[ $exit_code -eq 0 ]]; then
            echo "  ✓ $label ${elapsed}s (card $card)" | tee -a "$QUEUE_LOG"
        else
            echo "  ✗ $label exit=$exit_code ${elapsed}s (card $card)" | tee -a "$QUEUE_LOG"
        fi
    } &
}

# ── Build per-phase config lists ──

# Phase dirs and their types: ecomd | traditional | baseline
declare -a PHASE_DIRS=(
    "experiments/089b_cross_asset_attribution_30seed:ecomd"
    "experiments/091_calibration_ecomd_5asset:ecomd"
    "experiments/092_5asset_replication_30seed:ecomd"
    "experiments/093_5asset_traditional_baselines:traditional"
    "experiments/095_baseline_5asset_5seed:baseline"
)

QUEUE_LOG="$MASTER_LOG"

run_main() {
    echo "═══ RERUN MISSING DATA — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  N_FAILED=$N_FAILED PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"

    local total=0
    for entry in "${PHASE_DIRS[@]}"; do
        local dir="${entry%%:*}"
        local type="${entry##*:}"
        if [[ ! -d "$dir" ]]; then
            echo "  [skip] $dir not found" | tee -a "$MASTER_LOG"
            continue
        fi

        local label
        for fail_label in $FAILED; do
            local cfg="$dir/config_${fail_label}.yaml"
            if [[ -f "$cfg" ]]; then
                local outdir="$dir/results_${fail_label}"
                label="$fail_label"
                case "$type" in
                    ecomd)
                        while (( $(jobs -rp | wc -l) >= PARALLEL )); do wait -n; done
                        train_one $((total % PARALLEL)) "$label" "$cfg" "$outdir"
                        ;;
                    traditional)
                        while (( $(jobs -rp | wc -l) >= PARALLEL )); do wait -n; done
                        run_traditional_one $((total % PARALLEL)) "$label" "$cfg" "$outdir"
                        ;;
                    baseline)
                        while (( $(jobs -rp | wc -l) >= PARALLEL )); do wait -n; done
                        run_baseline_one $((total % PARALLEL)) "$label" "$cfg" "$outdir"
                        ;;
                esac
                total=$((total + 1))
            fi
        done
    done

    echo "  dispatched $total train/trad/baseline jobs" | tee -a "$MASTER_LOG"
    wait
    echo "  training/trad/baseline pass done" | tee -a "$MASTER_LOG"

    # ECoMD eval pass
    local eval_total=0
    for entry in "${PHASE_DIRS[@]}"; do
        local dir="${entry%%:*}"
        local type="${entry##*:}"
        [[ "$type" != "ecomd" ]] && continue
        for fail_label in $FAILED; do
            local cfg="$dir/config_${fail_label}.yaml"
            local outdir="$dir/results_${fail_label}"
            if [[ -f "$cfg" && -f "$outdir/checkpoint.pt" ]]; then
                while (( $(jobs -rp | wc -l) >= PARALLEL )); do wait -n; done
                eval_one $((eval_total % PARALLEL)) "$fail_label" "$cfg" "$outdir"
                eval_total=$((eval_total + 1))
            fi
        done
    done
    echo "  dispatched $eval_total eval jobs" | tee -a "$MASTER_LOG"
    wait

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ RERUN DONE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  $total train + $eval_total eval jobs completed" | tee -a "$MASTER_LOG"
}

if [[ "$DAEMON" == "1" ]]; then
    (run_main) >> "$MASTER_LOG" 2>&1 < /dev/null &
    pid=$!
    disown "$pid" 2>/dev/null || true
    echo "$pid" > "${MASTER_LOG}.pid"
    echo "started PID $pid; tail -f $MASTER_LOG"
else
    run_main
fi
