#!/usr/bin/env bash
# Overnight H20 batch — train + eval + score 23 configs sequentially.
#
# A0..A5  re-run with proper 4-card DDP (was single-GPU last round)
# B0..B5  same architectures, CONSERVATIVE v3 hyperparams
# C0..C5  same architectures, EXPANDED loss (autocorr_r + hill_max)
# D0..D4  longer training (400 iters) on the most promising configs
#
# Total: ~23 train + ~23 eval × ~3 min on 4-card H20 = ~2-3 hours.
#
# Usage:
#   git pull
#   bash scripts/h20_overnight_v3.sh                    # foreground
#   DAEMON=1 nohup bash scripts/h20_overnight_v3.sh &   # background
#
# Idempotent: skips configs that already have inference_merged.json.

set -uo pipefail

# Hard NPROC=1 unset (last run wasted single-GPU)
if [[ "${NPROC:-}" == "1" && -z "${FORCE_NPROC:-}" ]]; then
    echo "[guard] env had NPROC=1 — unsetting to use default 4-card DDP"
    unset NPROC
fi
NPROC="${NPROC:-4}"
DAEMON="${DAEMON:-0}"
SKIP_DONE="${SKIP_DONE:-1}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export DIST_BACKEND="${DIST_BACKEND:-gloo}"
export ECOPHYS_DATA_DIR="${ECOPHYS_DATA_DIR:-$REPO_ROOT/data/sample}"
export PYTHONPATH="${PYTHONPATH:-$REPO_ROOT}"

# Detect GPU count for sanity
n_gpu="$(nvidia-smi -L 2>/dev/null | wc -l | tr -d ' ')"
n_gpu="${n_gpu:-0}"
echo "[guard] NPROC=$NPROC  visible GPUs=$n_gpu"

# All configs to run, in priority order.
# Format: ID|config_path|out_dir
declare -a JOBS=(
    "A0|experiments/022_h20_batch/config_a0_baseline.yaml|experiments/022_h20_batch/results_a0"
    "A1|experiments/022_h20_batch/config_a1_multi_asset.yaml|experiments/022_h20_batch/results_a1"
    "A2|experiments/022_h20_batch/config_a2_multi_asset_mshawkes.yaml|experiments/022_h20_batch/results_a2"
    "A3|experiments/022_h20_batch/config_a3_multi_asset_regime.yaml|experiments/022_h20_batch/results_a3"
    "A4|experiments/022_h20_batch/config_a4_multi_asset_twopop.yaml|experiments/022_h20_batch/results_a4"
    "A5|experiments/022_h20_batch/config_a5_all_features.yaml|experiments/022_h20_batch/results_a5"
    "B0|experiments/022_h20_batch/config_b0_baseline.yaml|experiments/022_h20_batch/results_b0"
    "B1|experiments/022_h20_batch/config_b1_multi_asset.yaml|experiments/022_h20_batch/results_b1"
    "B2|experiments/022_h20_batch/config_b2_multi_asset_mshawkes.yaml|experiments/022_h20_batch/results_b2"
    "B3|experiments/022_h20_batch/config_b3_multi_asset_regime.yaml|experiments/022_h20_batch/results_b3"
    "B4|experiments/022_h20_batch/config_b4_multi_asset_twopop.yaml|experiments/022_h20_batch/results_b4"
    "B5|experiments/022_h20_batch/config_b5_all_features.yaml|experiments/022_h20_batch/results_b5"
    "C0|experiments/022_h20_batch/config_c0_baseline.yaml|experiments/022_h20_batch/results_c0"
    "C1|experiments/022_h20_batch/config_c1_multi_asset.yaml|experiments/022_h20_batch/results_c1"
    "C2|experiments/022_h20_batch/config_c2_multi_asset_mshawkes.yaml|experiments/022_h20_batch/results_c2"
    "C3|experiments/022_h20_batch/config_c3_multi_asset_regime.yaml|experiments/022_h20_batch/results_c3"
    "C4|experiments/022_h20_batch/config_c4_multi_asset_twopop.yaml|experiments/022_h20_batch/results_c4"
    "C5|experiments/022_h20_batch/config_c5_all_features.yaml|experiments/022_h20_batch/results_c5"
    "D0|experiments/022_h20_batch/config_d0_a0_long.yaml|experiments/022_h20_batch/results_d0"
    "D1|experiments/022_h20_batch/config_d1_b0_long.yaml|experiments/022_h20_batch/results_d1"
    "D2|experiments/022_h20_batch/config_d2_b4_long.yaml|experiments/022_h20_batch/results_d2"
    "D3|experiments/022_h20_batch/config_d3_c0_long.yaml|experiments/022_h20_batch/results_d3"
    "D4|experiments/022_h20_batch/config_d4_c4_long.yaml|experiments/022_h20_batch/results_d4"
)

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
QUEUE_LOG="experiments/022_h20_batch/_overnight_${TIMESTAMP}.log"
mkdir -p experiments/022_h20_batch
: > "$QUEUE_LOG"

train_one() {
    local label="$1"
    local config="$2"
    local outdir="$3"
    mkdir -p "$outdir"
    if [[ "$SKIP_DONE" == "1" && -f "$outdir/training_log.json" ]]; then
        echo "[skip-train $label] training_log.json exists" | tee -a "$QUEUE_LOG"
        return 0
    fi
    echo "" | tee -a "$QUEUE_LOG"
    echo "═══ TRAIN $label ═══ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
    echo "  config=$config" | tee -a "$QUEUE_LOG"
    local start=$(date +%s)
    local job_log="$outdir/train_${TIMESTAMP}.log"
    torchrun --nproc_per_node="$NPROC" --standalone \
        -m ecomd.training.train_distributed \
        --config "$config" --out-dir "$outdir" 2>&1 \
      | tee "$job_log" >> "$QUEUE_LOG"
    local exit_code=${PIPESTATUS[0]}
    local elapsed=$(( $(date +%s) - start ))
    if [[ $exit_code -eq 0 ]]; then
        echo "  ✓ $label trained in ${elapsed}s" | tee -a "$QUEUE_LOG"
    else
        echo "  ✗ $label TRAIN FAILED exit=$exit_code (${elapsed}s)" | tee -a "$QUEUE_LOG"
    fi
}

eval_one() {
    local label="$1"
    local config="$2"
    local outdir="$3"
    if [[ "$SKIP_DONE" == "1" && -f "$outdir/inference_merged.json" ]]; then
        echo "[skip-eval $label] inference_merged.json exists" | tee -a "$QUEUE_LOG"
        return 0
    fi
    if [[ ! -f "$outdir/checkpoint.pt" ]]; then
        echo "[skip-eval $label] no checkpoint" | tee -a "$QUEUE_LOG"
        return 0
    fi
    echo "" | tee -a "$QUEUE_LOG"
    echo "═══ EVAL  $label ═══ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
    local start=$(date +%s)
    local elog="$outdir/eval_${TIMESTAMP}.log"
    torchrun --nproc_per_node="$NPROC" --standalone \
        -m ecomd.inference.run_large \
        --ckpt "$outdir/checkpoint.pt" --config "$config" \
        --n-steps 4000 --n-realizations-per-rank 2 2>&1 \
      | tee "$elog" >> "$QUEUE_LOG"
    local exit_code=${PIPESTATUS[0]}
    local elapsed=$(( $(date +%s) - start ))
    if [[ $exit_code -eq 0 ]]; then
        echo "  ✓ $label evaled in ${elapsed}s" | tee -a "$QUEUE_LOG"
    else
        echo "  ✗ $label EVAL FAILED exit=$exit_code" | tee -a "$QUEUE_LOG"
    fi
}

main() {
    echo "═══ OVERNIGHT v3 batch — $(date) ═══" | tee -a "$QUEUE_LOG"
    echo " NPROC=$NPROC SKIP_DONE=$SKIP_DONE" | tee -a "$QUEUE_LOG"

    # Train all
    echo "" | tee -a "$QUEUE_LOG"
    echo "─── PHASE 1: TRAIN (${#JOBS[@]} configs) ───" | tee -a "$QUEUE_LOG"
    for entry in "${JOBS[@]}"; do
        IFS='|' read -r label config outdir <<< "$entry"
        train_one "$label" "$config" "$outdir"
    done

    # Eval all
    echo "" | tee -a "$QUEUE_LOG"
    echo "─── PHASE 2: EVAL (${#JOBS[@]} configs) ───" | tee -a "$QUEUE_LOG"
    for entry in "${JOBS[@]}"; do
        IFS='|' read -r label config outdir <<< "$entry"
        eval_one "$label" "$config" "$outdir"
    done

    # Score (Mac will re-do this but we run on H20 too for early visibility)
    echo "" | tee -a "$QUEUE_LOG"
    echo "─── PHASE 3: SCORE ───" | tee -a "$QUEUE_LOG"
    if conda run -n ecophys python scripts/score_v3_batch.py 2>&1 | tee -a "$QUEUE_LOG"; then
        echo "  scoreboard: experiments/022_h20_batch/scoreboard.md" | tee -a "$QUEUE_LOG"
    fi

    echo "" | tee -a "$QUEUE_LOG"
    echo "═══ OVERNIGHT done $(date) ═══" | tee -a "$QUEUE_LOG"
    echo "Next: git add -A && git commit -m 'overnight v3 results' && git push" | tee -a "$QUEUE_LOG"
}

if [[ "$DAEMON" == "1" ]]; then
    nohup bash -c "$(declare -f train_one eval_one main); main" >> "$QUEUE_LOG" 2>&1 &
    pid=$!
    echo "$pid" > "${QUEUE_LOG}.pid"
    echo "started PID $pid; tail -f $QUEUE_LOG"
else
    main
fi
