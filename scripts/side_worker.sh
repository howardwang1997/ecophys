#!/usr/bin/env bash
# Per-config queue runner for the 2-card side machines (H20-2 / H20-3), executed ON the side
# machine (rsynced over by h20_side_queue.sh). Unlike h20_run_phase.sh (train-all-then-eval-all),
# each job here is train+eval BACK-TO-BACK on one card, so a wall-clock CUTOFF can stop the queue
# between configs and every finished config is fully scored — partial queues are usable.
#
# Configs run in lexical order; 118/119 use seed-major file naming, so a cutoff leaves the cells
# with balanced seed counts.
#
# Usage (composed remotely by h20_side_queue.sh):
#   bash scripts/side_worker.sh --cutoff <epoch-secs> [--par 2] [--env ecophys] [--run-116] DIR [DIR...]
#
# --run-116 runs scripts/h20_116_criticality.sh first (pure-inference κ-sweep; it parallelises
# across the local GPUs itself and is NOT subject to the cutoff — it is short).
# Dirs are processed sequentially. SKIP_DONE semantics always on (training_log.json /
# inference_merged.json sentinels), so re-launching after an interruption resumes cleanly.

set -uo pipefail

CUTOFF=0; PAR=2; ENVN="ecophys"; RUN_116=0; DIRS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --cutoff)  CUTOFF="$2"; shift 2 ;;
        --par)     PAR="$2"; shift 2 ;;
        --env)     ENVN="$2"; shift 2 ;;
        --run-116) RUN_116=1; shift ;;
        *)         DIRS+=("$1"); shift ;;
    esac
done
[[ "$CUTOFF" -gt 0 ]] || { echo "usage: side_worker.sh --cutoff <epoch> [--par N] [--env E] [--run-116] DIR..."; exit 2; }

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
export DIST_BACKEND="${DIST_BACKEND:-nccl}"
export PYTHONPATH="${PYTHONPATH:-$REPO_ROOT}"
export WANDB_MODE="${WANDB_MODE:-offline}"   # side machines may lack W&B creds

# conda may be absent from non-interactive ssh PATH
if ! command -v conda >/dev/null 2>&1; then
    for c in "$HOME/miniconda3/etc/profile.d/conda.sh" "$HOME/anaconda3/etc/profile.d/conda.sh" \
             /opt/conda/etc/profile.d/conda.sh; do
        [[ -f "$c" ]] && source "$c" && break
    done
fi
command -v conda >/dev/null 2>&1 || { echo "[side] ERROR: conda not found"; exit 1; }

n_gpu="$(nvidia-smi -L 2>/dev/null | wc -l | tr -d ' ')"; n_gpu="${n_gpu:-0}"
[[ "$n_gpu" -lt 1 ]] && { echo "[side] ERROR: no GPUs visible"; exit 1; }
[[ "$PAR" -gt "$n_gpu" ]] && PAR="$n_gpu"
echo "[side] $(hostname): $n_gpu GPUs, PAR=$PAR env=$ENVN cutoff=$(date -d "@$CUTOFF" 2>/dev/null || echo "$CUTOFF")"

if [[ "$RUN_116" == "1" ]]; then
    echo "[side] ── exp 116 criticality (pure inference, pre-cutoff block) ── $(date)"
    conda run --no-capture-output -n "$ENVN" bash scripts/h20_116_criticality.sh \
        || echo "[side] WARN: 116 exited non-zero (continuing to δ-grid)"
fi

job() {  # card cfg outdir — train then eval, back-to-back on one card
    local card="$1" cfg="$2" out="$3"
    mkdir -p "$out"
    if [[ ! -f "$out/training_log.json" ]]; then
        CUDA_VISIBLE_DEVICES="$card" timeout "${TIMEOUT_SECS:-14400}" \
            conda run --no-capture-output -n "$ENVN" torchrun --nproc_per_node=1 --standalone \
            -m ecomd.training.train_distributed --config "$cfg" --out-dir "$out" \
            >> "$out/side_train.log" 2>&1 \
            || { echo "  ✗ train $(basename "$out") (card $card)"; return 0; }
    fi
    if [[ -f "$out/checkpoint.pt" && ! -f "$out/inference_merged.json" ]]; then
        CUDA_VISIBLE_DEVICES="$card" timeout "${TIMEOUT_SECS:-14400}" \
            conda run --no-capture-output -n "$ENVN" torchrun --nproc_per_node=1 --standalone \
            -m ecomd.inference.run_large --ckpt "$out/checkpoint.pt" --config "$cfg" \
            --n-steps 4000 --n-realizations-per-rank 4 \
            >> "$out/side_eval.log" 2>&1 \
            || { echo "  ✗ eval $(basename "$out") (card $card)"; return 0; }
    fi
    echo "  ✓ $(basename "$out") (card $card) $(date +%H:%M:%S)"
}

i=0; stopped=0
for dir in "${DIRS[@]}"; do
    echo "[side] ── queue $dir ── $(date)"
    for cfg in "$dir"/config_*.yaml; do
        [[ -e "$cfg" ]] || { echo "[side] no configs in $dir"; break; }
        label="$(basename "$cfg" .yaml | sed 's/^config_//')"
        out="$dir/results_${label}"
        [[ -f "$out/inference_merged.json" ]] && { echo "  [skip $label]"; continue; }
        if (( $(date +%s) >= CUTOFF )); then
            echo "[side] CUTOFF reached before $label — stopping queue"; stopped=1; break 2
        fi
        while (( $(jobs -rp | wc -l) >= PAR )); do wait -n; done
        job "$(( i % PAR ))" "$cfg" "$out" &
        i=$(( i + 1 ))
    done
done
wait
echo "[side] done $(date) — launched $i jobs$( ((stopped)) && echo ' (cutoff-stopped)')"
