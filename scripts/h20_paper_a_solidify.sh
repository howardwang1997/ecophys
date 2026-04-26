#!/usr/bin/env bash
# Paper A solidify batch — 6 phases (L/M/N/O/P/Q), ~60 configs.
#
# Designed to run AFTER the weekend batch (`feature/h20-batch-v3`)
# completes. Idempotent (SKIP_DONE=1 default), independent result dir
# (`experiments/025_paper_a_solidify/`), so it doesn't touch weekend
# results.
#
# Usage on H20:
#   unset NPROC                              # safety
#   git pull
#   git checkout feature/paper-a-solidify
#   bash scripts/yfinance_ingest_paper_a.sh  # one-time data fetch
#   DAEMON=1 bash scripts/h20_paper_a_solidify.sh   # all 6 phases
#   tail -f experiments/025_paper_a_solidify/_run_*.log
#
# Single phase:  bash scripts/h20_paper_a_solidify.sh L

set -uo pipefail

# Hard NPROC=1 unset (env contamination guard)
if [[ "${NPROC:-}" == "1" && -z "${FORCE_NPROC:-}" ]]; then
    echo "[guard] env had NPROC=1 — unsetting"
    unset NPROC
fi
NPROC="${NPROC:-4}"
DAEMON="${DAEMON:-0}"
SKIP_DONE="${SKIP_DONE:-1}"
PHASES="${1:-L M N O P Q}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export DIST_BACKEND="${DIST_BACKEND:-gloo}"
export ECOPHYS_DATA_DIR="${ECOPHYS_DATA_DIR:-$REPO_ROOT/data/sample}"
export PYTHONPATH="${PYTHONPATH:-$REPO_ROOT}"

n_gpu="$(nvidia-smi -L 2>/dev/null | wc -l | tr -d ' ')"
n_gpu="${n_gpu:-0}"
echo "[guard] NPROC=$NPROC  visible GPUs=$n_gpu  PHASES=$PHASES"

CONFIG_DIR="experiments/025_paper_a_solidify"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
QUEUE_LOG="$CONFIG_DIR/_run_${TIMESTAMP}.log"
mkdir -p "$CONFIG_DIR"
: > "$QUEUE_LOG"

train_one() {
    local label="$1"
    local config="$2"
    local outdir="$3"
    mkdir -p "$outdir"
    if [[ "$SKIP_DONE" == "1" && -f "$outdir/training_log.json" ]]; then
        echo "  [skip-train $label]" | tee -a "$QUEUE_LOG"
        return 0
    fi
    # Skip placeholder configs (P series 1-3)
    if [[ "$label" == p1_* || "$label" == p2_* || "$label" == p3_* ]]; then
        echo "  [skip $label] placeholder (deferred to follow-up)" | tee -a "$QUEUE_LOG"
        return 0
    fi
    echo "" | tee -a "$QUEUE_LOG"
    echo "═ TRAIN $label ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
    local start=$(date +%s)
    local job_log="$outdir/train_${TIMESTAMP}.log"
    timeout 2700 torchrun --nproc_per_node="$NPROC" --standalone \
        -m ecomd.training.train_distributed \
        --config "$config" --out-dir "$outdir" 2>&1 \
      | tee "$job_log" >> "$QUEUE_LOG"
    local exit_code=${PIPESTATUS[0]}
    local elapsed=$(( $(date +%s) - start ))
    if [[ $exit_code -eq 0 ]]; then
        echo "  ✓ $label ${elapsed}s" | tee -a "$QUEUE_LOG"
    else
        echo "  ✗ $label exit=$exit_code (${elapsed}s)" | tee -a "$QUEUE_LOG"
    fi
}

eval_one() {
    local label="$1"
    local config="$2"
    local outdir="$3"
    if [[ "$SKIP_DONE" == "1" && -f "$outdir/inference_merged.json" ]]; then
        echo "  [skip-eval $label]" | tee -a "$QUEUE_LOG"
        return 0
    fi
    if [[ ! -f "$outdir/checkpoint.pt" ]]; then
        echo "  [skip-eval $label] no checkpoint" | tee -a "$QUEUE_LOG"
        return 0
    fi
    echo "" | tee -a "$QUEUE_LOG"
    echo "═ EVAL  $label ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
    local start=$(date +%s)
    local elog="$outdir/eval_${TIMESTAMP}.log"
    # 4 realizations per rank → 16 total per config — tighter CI than weekend's 8
    timeout 2700 torchrun --nproc_per_node="$NPROC" --standalone \
        -m ecomd.inference.run_large \
        --ckpt "$outdir/checkpoint.pt" --config "$config" \
        --n-steps 4000 --n-realizations-per-rank 4 2>&1 \
      | tee "$elog" >> "$QUEUE_LOG"
    local exit_code=${PIPESTATUS[0]}
    local elapsed=$(( $(date +%s) - start ))
    if [[ $exit_code -eq 0 ]]; then
        echo "  ✓ eval $label ${elapsed}s" | tee -a "$QUEUE_LOG"
    else
        echo "  ✗ eval $label exit=$exit_code" | tee -a "$QUEUE_LOG"
    fi
}

run_phase() {
    local phase="$1"
    local lower=$(echo "$phase" | tr 'A-Z' 'a-z')
    local cfgs=("$CONFIG_DIR"/config_${lower}*.yaml)
    if [[ ! -e "${cfgs[0]}" ]]; then
        echo "[phase $phase] no configs found — skip"
        return 0
    fi
    echo "" | tee -a "$QUEUE_LOG"
    echo "──── PHASE $phase (${#cfgs[@]} configs) ────" | tee -a "$QUEUE_LOG"
    for cfg in "${cfgs[@]}"; do
        local label=$(basename "$cfg" .yaml | sed 's/^config_//')
        local outdir="$CONFIG_DIR/results_${label}"
        train_one "$label" "$cfg" "$outdir"
    done
    for cfg in "${cfgs[@]}"; do
        local label=$(basename "$cfg" .yaml | sed 's/^config_//')
        local outdir="$CONFIG_DIR/results_${label}"
        eval_one "$label" "$cfg" "$outdir"
    done
}

main() {
    echo "═══ PAPER A SOLIDIFY BATCH — $(date) ═══" | tee -a "$QUEUE_LOG"
    echo " PHASES=$PHASES NPROC=$NPROC SKIP_DONE=$SKIP_DONE" | tee -a "$QUEUE_LOG"

    for phase in $PHASES; do
        run_phase "$phase"
    done

    echo "" | tee -a "$QUEUE_LOG"
    echo "──── SCORE ────" | tee -a "$QUEUE_LOG"
    if conda run -n ecophys python scripts/score_paper_a_solidify.py 2>&1 | tee -a "$QUEUE_LOG"; then
        echo "  → $CONFIG_DIR/scoreboard.md" | tee -a "$QUEUE_LOG"
    fi

    echo "" | tee -a "$QUEUE_LOG"
    echo "═══ DONE — $(date) ═══" | tee -a "$QUEUE_LOG"
}

if [[ "$DAEMON" == "1" ]]; then
    # Subshell preserves all local vars + env
    (main) >> "$QUEUE_LOG" 2>&1 < /dev/null &
    pid=$!
    disown "$pid" 2>/dev/null || true
    echo "$pid" > "${QUEUE_LOG}.pid"
    echo "started PID $pid; tail -f $QUEUE_LOG"
else
    main
fi
