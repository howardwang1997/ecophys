#!/usr/bin/env bash
# Generic phase runner — config-parallel train + eval for any
# experiments/<dir>/ that contains config_*.yaml files.
#
# Fixed card assignment: only increments card counter when a job is
# actually launched (not on skips), ensuring all PARALLEL cards are used.
#
# Usage:
#   bash scripts/h20_run_phase.sh experiments/031_chunk_effect
#   PARALLEL=8 bash scripts/h20_run_phase.sh experiments/031_chunk_effect
#   DAEMON=1 bash scripts/h20_run_phase.sh experiments/031_chunk_effect
#   SKIP_DONE=0 bash scripts/h20_run_phase.sh experiments/031_chunk_effect

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

run_one() {
    local phase="$1" card="$2" label="$3" cfg="$4" outdir="$5"
    local skip_file="$outdir/training_log.json"
    local cmd_args=()
    if [[ "$phase" == "train" ]]; then
        skip_file="$outdir/training_log.json"
        cmd_args=(-m ecomd.training.train_distributed --config "$cfg" --out-dir "$outdir")
    else
        skip_file="$outdir/inference_merged.json"
        if [[ ! -f "$outdir/checkpoint.pt" ]]; then
            echo "  [skip-eval $label] no checkpoint" | tee -a "$QUEUE_LOG"
            return 1
        fi
        cmd_args=(-m ecomd.inference.run_large --ckpt "$outdir/checkpoint.pt" --config "$cfg" --n-steps 4000 --n-realizations-per-rank 4)
    fi

    if [[ "$SKIP_DONE" == "1" && -f "$skip_file" ]]; then
        echo "  [skip-$phase $label]" | tee -a "$QUEUE_LOG"
        return 1
    fi

    {
        local tag
        tag=$(echo "$phase" | tr '[:lower:]' '[:upper:]')
        echo "" | tee -a "$QUEUE_LOG"
        echo "═ $tag $label (card $card) ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
        local start=$(date +%s)
        local job_log="$outdir/${phase}_${TIMESTAMP}.log"
        CUDA_VISIBLE_DEVICES="$card" \
        timeout ${TIMEOUT_SECS:-14400} torchrun --nproc_per_node="$NPROC" --standalone \
            "${cmd_args[@]}" 2>&1 | tee "$job_log" >> "$QUEUE_LOG"
        local exit_code=${PIPESTATUS[0]}
        local elapsed=$(( $(date +%s) - start ))
        if [[ $exit_code -eq 0 ]]; then
            echo "  ✓ $phase $label ${elapsed}s (card $card)" | tee -a "$QUEUE_LOG"
        else
            echo "  ✗ $phase $label exit=$exit_code ${elapsed}s (card $card)" | tee -a "$QUEUE_LOG"
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

    if [[ -n "${CONFIG_ORDER_PREFIXES:-}" ]]; then
        local -a ordered=()
        local taken=":"
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
        echo "  CONFIG_ORDER_PREFIXES=$CONFIG_ORDER_PREFIXES" | tee -a "$QUEUE_LOG"
    fi
    echo "  Configs: ${#cfgs[@]}" | tee -a "$QUEUE_LOG"

    for phase in train eval; do
        local card=0
        local launched=0
        echo "" | tee -a "$QUEUE_LOG"
        echo "--- $phase pass ---" | tee -a "$QUEUE_LOG"
        for cfg in "${cfgs[@]}"; do
            local label=$(basename "$cfg" .yaml | sed 's/^config_//')
            local outdir="$CONFIG_DIR/results_${label}"
            while (( $(jobs -rp | wc -l) >= PARALLEL )); do
                wait -n
            done
            if run_one "$phase" "$card" "$label" "$cfg" "$outdir"; then
                card=$(( (card + 1) % PARALLEL ))
                launched=$((launched + 1))
            fi
        done
        wait
        echo "  $phase pass: $launched launched" | tee -a "$QUEUE_LOG"
    done

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
