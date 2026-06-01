#!/usr/bin/env bash
# Exp 112 Part B — α scaling-curve diagnose (pure inference; runs AFTER Part A).
# Reuses the TRAINED baseline checkpoints from Part A (results_baseline_seed{0,1,2})
# and rolls them out under config overrides (N, ed_normalize, hawkes_kappa) via
# run_large. No retraining. ~30-45 min on 8 cards.
#
# Prereq: Part A done so results_baseline_seed{0,1,2}/checkpoint.pt exist
#   (the main launcher h20_112_tail_clamp.sh calls this before the delete-sync).
#
# Standalone usage on H20:
#   conda run -n ecophys python experiments/112_tail_clamp/scaling/generate_scaling_configs.py
#   bash scripts/h20_112_scaling.sh
#   conda run -n ecophys python scripts/score_scaling.py experiments/112_tail_clamp/scaling

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
export DIST_BACKEND="${DIST_BACKEND:-gloo}"
export PYTHONPATH="${PYTHONPATH:-$REPO_ROOT}"

PHASE="experiments/112_tail_clamp"
SCAN_DIR="$PHASE/scaling"
N_STEPS="${N_STEPS:-8000}"
N_CKPT="${N_CKPT:-3}"          # number of baseline checkpoints to anchor on
SKIP_DONE="${SKIP_DONE:-1}"
n_gpu="$(nvidia-smi -L 2>/dev/null | wc -l | tr -d ' ')"; n_gpu="${n_gpu:-1}"; [[ "$n_gpu" -lt 1 ]] && n_gpu=1

# Discover anchor checkpoints (first N_CKPT baseline seeds with a checkpoint).
mapfile -t CKPTS < <(ls -1 "$PHASE"/results_baseline_seed*/checkpoint.pt 2>/dev/null | head -n "$N_CKPT")
if [[ "${#CKPTS[@]}" -eq 0 ]]; then
    echo "ERROR: no baseline checkpoints under $PHASE/results_baseline_seed*/checkpoint.pt"
    echo "       run Part A first (bash scripts/h20_112_tail_clamp.sh)."
    exit 1
fi
echo "[scaling] anchoring on ${#CKPTS[@]} checkpoint(s): ${CKPTS[*]}"

mapfile -t CFGS < <(ls -1 "$SCAN_DIR"/config_*.yaml 2>/dev/null)
echo "[scaling] ${#CFGS[@]} scan configs × ${#CKPTS[@]} ckpts = $(( ${#CFGS[@]} * ${#CKPTS[@]} )) runs, n_steps=$N_STEPS"

card=0
run_one() {  # ckpt_seed cfg_tag ckpt cfg
    local cs="$1" tag="$2" ckpt="$3" cfg="$4"
    local out="$SCAN_DIR/results_${cs}_${tag}"
    if [[ "$SKIP_DONE" == "1" && -f "$out/inference_merged.json" ]]; then
        echo "  [skip $cs/$tag]"; return 0; fi
    mkdir -p "$out"
    CUDA_VISIBLE_DEVICES="$card" torchrun --nproc_per_node=1 --standalone \
        -m ecomd.inference.run_large --ckpt "$ckpt" --config "$cfg" \
        --out-dir "$out" --n-steps "$N_STEPS" --n-realizations-per-rank 1 \
        > "$out/run.log" 2>&1 &
}

for ckpt in "${CKPTS[@]}"; do
    cs="$(basename "$(dirname "$ckpt")" | sed 's/results_baseline_//')"  # e.g. seed0
    for cfg in "${CFGS[@]}"; do
        tag="$(basename "$cfg" .yaml | sed 's/^config_//')"
        run_one "$cs" "$tag" "$ckpt" "$cfg"
        card=$(( (card + 1) % n_gpu ))
        [[ "$card" -eq 0 ]] && wait   # drain a full wave of n_gpu jobs
    done
done
wait
echo "[scaling] all runs done → score: conda run -n ecophys python scripts/score_scaling.py $SCAN_DIR"
