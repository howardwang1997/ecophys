#!/usr/bin/env bash
# Loss redesign + BPTT-checkpoint ablation batch — 4 phases (1/2/4/5),
# ~109 configs.
#
# 8-card H20 strategy: **config-parallel** rather than DDP.
#   PARALLEL=8: 8 different configs run simultaneously, one per CUDA card.
#   NPROC=1   : each config is single-rank (no DDP overhead per config).
#   This maximises throughput for ablation studies. For final multi-seed
#   CI runs in Phase 2, NPROC>1 + DDP gives 8-rank gradient averaging
#   and tighter eval CI; controlled per-phase.
#
# Backend: NCCL by default (8-card NVLink), gloo as fallback if NCCL
# rendezvous fails (then ~10% slower all-reduce).
#
# Usage on H20:
#   unset NPROC
#   git pull && git checkout feature/bptt-checkpoint
#   bash scripts/h20_refresh_deps.sh        # one-time, picks up any new deps
#   DAEMON=1 bash scripts/h20_loss_ablation.sh        # all 4 phases
#   tail -f experiments/027_loss_redesign/_run_*.log
#
# Single phase:        bash scripts/h20_loss_ablation.sh 1
# Multi phases:        bash scripts/h20_loss_ablation.sh "1 2"
# Force re-run all:    SKIP_DONE=0 bash scripts/h20_loss_ablation.sh

set -uo pipefail

# NPROC=1 is correct for config-parallel; only override if user explicitly
# wants DDP within configs (FORCE_NPROC=1 to confirm intent).
NPROC="${NPROC:-1}"
PARALLEL="${PARALLEL:-8}"          # how many configs run simultaneously
DAEMON="${DAEMON:-0}"
SKIP_DONE="${SKIP_DONE:-1}"
PHASES="${1:-1 2 4 5}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export DIST_BACKEND="${DIST_BACKEND:-nccl}"
export ECOPHYS_DATA_DIR="${ECOPHYS_DATA_DIR:-$REPO_ROOT/data/sample}"
export PYTHONPATH="${PYTHONPATH:-$REPO_ROOT}"

n_gpu="$(nvidia-smi -L 2>/dev/null | wc -l | tr -d ' ')"
n_gpu="${n_gpu:-0}"
echo "[guard] NPROC=$NPROC PARALLEL=$PARALLEL visible GPUs=$n_gpu PHASES=$PHASES BACKEND=$DIST_BACKEND"

CONFIG_DIR="experiments/027_loss_redesign"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
QUEUE_LOG="$CONFIG_DIR/_run_${TIMESTAMP}.log"
mkdir -p "$CONFIG_DIR"
: > "$QUEUE_LOG"

# ── train_one_config_parallel: launches a single config on a specific card,
#    returns immediately (caller manages parallelism via wait/jobs).
# ─────────────────────────────────────────────────────────────────────────
train_one_card() {
    local card="$1"
    local label="$2"
    local config="$3"
    local outdir="$4"
    mkdir -p "$outdir"
    if [[ "$SKIP_DONE" == "1" && -f "$outdir/training_log.json" ]]; then
        echo "  [skip-train $label]" | tee -a "$QUEUE_LOG"
        return 0
    fi
    local job_log="$outdir/train_${TIMESTAMP}.log"
    {
        echo "" | tee -a "$QUEUE_LOG"
        echo "═ TRAIN $label (card $card) ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
        local start=$(date +%s)
        CUDA_VISIBLE_DEVICES="$card" \
        timeout 2700 torchrun --nproc_per_node="$NPROC" --standalone \
            -m ecomd.training.train_distributed \
            --config "$config" --out-dir "$outdir" 2>&1 \
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
    local card="$1"
    local label="$2"
    local config="$3"
    local outdir="$4"
    if [[ "$SKIP_DONE" == "1" && -f "$outdir/inference_merged.json" ]]; then
        echo "  [skip-eval $label]" | tee -a "$QUEUE_LOG"
        return 0
    fi
    if [[ ! -f "$outdir/checkpoint.pt" ]]; then
        echo "  [skip-eval $label] no checkpoint" | tee -a "$QUEUE_LOG"
        return 0
    fi
    local elog="$outdir/eval_${TIMESTAMP}.log"
    {
        echo "" | tee -a "$QUEUE_LOG"
        echo "═ EVAL  $label (card $card) ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
        local start=$(date +%s)
        # Single-rank eval × 4 reals = 4 reals/config (Phase 1 default).
        # For Phase 2 multi-seed CI, override PARALLEL=2 + NPROC=4 manually
        # to get 32 reals/config tighter CI (configs run 2 at a time).
        CUDA_VISIBLE_DEVICES="$card" \
        timeout 2700 torchrun --nproc_per_node="$NPROC" --standalone \
            -m ecomd.inference.run_large \
            --ckpt "$outdir/checkpoint.pt" --config "$config" \
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

# ── run_phase: spawn TRAIN jobs in parallel groups of PARALLEL, then
#    spawn EVAL jobs in parallel groups of PARALLEL.
# ─────────────────────────────────────────────────────────────────────────
run_phase() {
    local phase="$1"
    local cfg_glob="$CONFIG_DIR/phase${phase}/config_*.yaml"
    local cfgs=()
    for cfg in $cfg_glob; do
        [[ -f "$cfg" ]] && cfgs+=("$cfg")
    done
    if [[ ${#cfgs[@]} -eq 0 ]]; then
        echo "[phase $phase] no configs found in $cfg_glob — skip"
        return 0
    fi
    echo "" | tee -a "$QUEUE_LOG"
    echo "──── PHASE $phase (${#cfgs[@]} configs, ${PARALLEL}-config parallel) ────" | tee -a "$QUEUE_LOG"

    # Train pass — config-parallel
    local card=0
    for cfg in "${cfgs[@]}"; do
        local label=$(basename "$cfg" .yaml | sed 's/^config_//')
        local outdir="$CONFIG_DIR/results_phase${phase}/${label}"

        # Wait if all cards in flight
        while (( $(jobs -rp | wc -l) >= PARALLEL )); do
            wait -n
        done

        train_one_card "$card" "$label" "$cfg" "$outdir"
        card=$(( (card + 1) % PARALLEL ))
    done
    wait

    # Eval pass — config-parallel
    card=0
    for cfg in "${cfgs[@]}"; do
        local label=$(basename "$cfg" .yaml | sed 's/^config_//')
        local outdir="$CONFIG_DIR/results_phase${phase}/${label}"

        while (( $(jobs -rp | wc -l) >= PARALLEL )); do
            wait -n
        done

        eval_one_card "$card" "$label" "$cfg" "$outdir"
        card=$(( (card + 1) % PARALLEL ))
    done
    wait
}

main() {
    echo "═══ LOSS ABLATION BATCH — $(date) ═══" | tee -a "$QUEUE_LOG"
    echo "  PHASES=$PHASES NPROC=$NPROC PARALLEL=$PARALLEL SKIP_DONE=$SKIP_DONE" | tee -a "$QUEUE_LOG"
    echo "  BACKEND=$DIST_BACKEND" | tee -a "$QUEUE_LOG"

    for phase in $PHASES; do
        run_phase "$phase"
    done

    echo "" | tee -a "$QUEUE_LOG"
    echo "──── SCORE ────" | tee -a "$QUEUE_LOG"
    if conda run -n ecophys python scripts/score_loss_ablation.py 2>&1 | tee -a "$QUEUE_LOG"; then
        echo "  → $CONFIG_DIR/scoreboard.md" | tee -a "$QUEUE_LOG"
    else
        echo "  (scoring failed — re-run manually)" | tee -a "$QUEUE_LOG"
    fi

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
