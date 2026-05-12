#!/usr/bin/env bash
# Generic phase runner — config-parallel train + eval for any
# experiments/<dir>/ that contains config_*.yaml files.
#
# Usage:
#   bash scripts/h20_run_phase.sh experiments/031_chunk_effect
#   bash scripts/h20_run_phase.sh experiments/032_arch_regime_sweep
#
# Daemon mode:
#   DAEMON=1 bash scripts/h20_run_phase.sh experiments/031_chunk_effect
#
# Skip already-done:  SKIP_DONE=1 (default 1)
# Force re-run all:   SKIP_DONE=0
#
# Eval is single-rank × 4 realizations per config. To switch to
# 32 realizations (8-rank DDP) for tighter CI, set NPROC=8 PARALLEL=1
# (one config at a time × 8 ranks each).

set -uo pipefail

CONFIG_DIR="${1:?usage: $0 <config_dir>}"

NPROC="${NPROC:-1}"
PARALLEL="${PARALLEL:-8}"
DAEMON="${DAEMON:-0}"
SKIP_DONE="${SKIP_DONE:-1}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export DIST_BACKEND="${DIST_BACKEND:-nccl}"
export PYTHONPATH="${PYTHONPATH:-$REPO_ROOT}"

n_gpu="$(nvidia-smi -L 2>/dev/null | wc -l | tr -d ' ')"
n_gpu="${n_gpu:-0}"
echo "[guard] NPROC=$NPROC PARALLEL=$PARALLEL visible GPUs=$n_gpu DIR=$CONFIG_DIR"

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
QUEUE_LOG="$CONFIG_DIR/_run_${TIMESTAMP}.log"
mkdir -p "$CONFIG_DIR"
: > "$QUEUE_LOG"

train_one_card() {
    local card="$1"; local label="$2"; local cfg="$3"; local outdir="$4"
    mkdir -p "$outdir"
    if [[ "$SKIP_DONE" == "1" && -f "$outdir/training_log.json" ]]; then
        echo "  [skip-train $label]" | tee -a "$QUEUE_LOG"
        return 0
    fi
    {
        echo "" | tee -a "$QUEUE_LOG"
        echo "═ TRAIN $label (card $card) ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
        local start=$(date +%s)
        local job_log="$outdir/train_${TIMESTAMP}.log"
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
    return 0
}

eval_one_card() {
    local card="$1"; local label="$2"; local cfg="$3"; local outdir="$4"
    if [[ "$SKIP_DONE" == "1" && -f "$outdir/inference_merged.json" ]]; then
        echo "  [skip-eval $label]" | tee -a "$QUEUE_LOG"
        return 0
    fi
    if [[ ! -f "$outdir/checkpoint.pt" ]]; then
        echo "  [skip-eval $label] no checkpoint" | tee -a "$QUEUE_LOG"
        return 0
    fi
    {
        echo "" | tee -a "$QUEUE_LOG"
        echo "═ EVAL  $label (card $card) ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
        local start=$(date +%s)
        local elog="$outdir/eval_${TIMESTAMP}.log"
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
    return 0
}

main() {
    echo "═══ PHASE RUN — $(date) ═══" | tee -a "$QUEUE_LOG"
    echo "  CONFIG_DIR=$CONFIG_DIR NPROC=$NPROC PARALLEL=$PARALLEL SKIP_DONE=$SKIP_DONE" | tee -a "$QUEUE_LOG"

    cfgs=( "$CONFIG_DIR"/config_*.yaml )
    if [[ ${#cfgs[@]} -eq 0 ]]; then
        echo "[error] no config_*.yaml in $CONFIG_DIR" | tee -a "$QUEUE_LOG"
        return 1
    fi

    # Optional priority ordering (added 2026-05-12). When CONFIG_ORDER_PREFIXES
    # is set (comma-separated list of cell-name prefixes), configs whose
    # label starts with one of those prefixes are run FIRST, in the listed
    # order. Remaining configs run after, in alphabetic order. Use this to
    # ensure the most important / longest-running cells land before any
    # H20 process death (Branch D failure mode at ~12h).
    #
    # Implementation note: we avoid bash 4 associative arrays (declare -A)
    # because some H20 environments still ship bash 3.2 and aborting under
    # `set -u` would kill the phase. Instead we use a delimited "taken"
    # string and substring matching.
    if [[ -n "${CONFIG_ORDER_PREFIXES:-}" ]]; then
        local -a ordered=()
        local taken=":"   # delimited so we can substring-match safely
        local prefix cfg label
        local IFS_BACKUP="$IFS"
        IFS=',' read -ra prefixes <<< "$CONFIG_ORDER_PREFIXES"
        IFS="$IFS_BACKUP"
        for prefix in "${prefixes[@]}"; do
            for cfg in "${cfgs[@]}"; do
                label=$(basename "$cfg" .yaml | sed 's/^config_//')
                if [[ "$label" == "${prefix}"* && "$taken" != *":${cfg}:"* ]]; then
                    ordered+=("$cfg")
                    taken="${taken}${cfg}:"
                fi
            done
        done
        for cfg in "${cfgs[@]}"; do
            if [[ "$taken" != *":${cfg}:"* ]]; then
                ordered+=("$cfg")
            fi
        done
        cfgs=("${ordered[@]}")
        echo "  CONFIG_ORDER_PREFIXES=$CONFIG_ORDER_PREFIXES (first ${#prefixes[@]} prefix groups prioritised)" | tee -a "$QUEUE_LOG"
    fi
    echo "  Configs: ${#cfgs[@]}" | tee -a "$QUEUE_LOG"

    # Train pass
    local card=0
    for cfg in "${cfgs[@]}"; do
        local label=$(basename "$cfg" .yaml | sed 's/^config_//')
        local outdir="$CONFIG_DIR/results_${label}"
        while (( $(jobs -rp | wc -l) >= PARALLEL )); do
            wait -n
        done
        train_one_card "$card" "$label" "$cfg" "$outdir"
        card=$(( (card + 1) % PARALLEL ))
    done
    wait

    # Eval pass
    card=0
    for cfg in "${cfgs[@]}"; do
        local label=$(basename "$cfg" .yaml | sed 's/^config_//')
        local outdir="$CONFIG_DIR/results_${label}"
        while (( $(jobs -rp | wc -l) >= PARALLEL )); do
            wait -n
        done
        eval_one_card "$card" "$label" "$cfg" "$outdir"
        card=$(( (card + 1) % PARALLEL ))
    done
    wait

    echo "" | tee -a "$QUEUE_LOG"
    echo "═══ DONE — $(date) ═══" | tee -a "$QUEUE_LOG"
}

if [[ "$DAEMON" == "1" ]]; then
    (main) >> "$QUEUE_LOG" 2>&1 < /dev/null &
    pid=$!
    disown "$pid" 2>/dev/null || true
    echo "$pid" > "${QUEUE_LOG}.pid"
    echo "started PID $pid; tail -f $QUEUE_LOG"
else
    main
fi
