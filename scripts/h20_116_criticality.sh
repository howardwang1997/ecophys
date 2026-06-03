#!/usr/bin/env bash
# Exp 116 — criticality probe (pure inference κ-sweep × 2 system sizes for finite-size scaling).
# Is the fat-tail overshoot a non-equilibrium PHASE TRANSITION? Sweep self-excitation κ; look for a
# critical κ_c where hill crosses 2, and whether the transition SHARPENS with N (FSS = true critical
# point vs smooth crossover). Reuses TRAINED baseline checkpoints — NO retraining. ~3h on 8 cards.
# Dual purpose: Paper A depth (why tails overshoot) + Paper B fork (does a phase transition exist?).
#
# Prereq: baseline checkpoints exist locally (113/114/115 results_*baseline*/checkpoint.pt). If they
# were delete-synced to R2, re-pull: bash scripts/h20_pull_from_r2.sh
#
# Usage on H20:
#   conda run -n ecophys python experiments/116_criticality/generate_configs.py
#   bash scripts/h20_116_criticality.sh
#   conda run -n ecophys python scripts/score_criticality.py experiments/116_criticality

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
export DIST_BACKEND="${DIST_BACKEND:-gloo}"
export PYTHONPATH="${PYTHONPATH:-$REPO_ROOT}"

PHASE="experiments/116_criticality"
N_STEPS="${N_STEPS:-8000}"
N_CKPT="${N_CKPT:-3}"
SKIP_DONE="${SKIP_DONE:-1}"
n_gpu="$(nvidia-smi -L 2>/dev/null | wc -l | tr -d ' ')"; n_gpu="${n_gpu:-1}"; [[ "$n_gpu" -lt 1 ]] && n_gpu=1

# Discover anchor checkpoints — prefer 113, then 114, then 115 baselines.
mapfile -t CKPTS < <(ls -1 experiments/11{3,4,5}_*/results_*baseline*/checkpoint.pt 2>/dev/null | head -n "$N_CKPT")
if [[ "${#CKPTS[@]}" -eq 0 ]]; then
    echo "ERROR: no baseline checkpoints found under experiments/11{3,4,5}_*/results_*baseline*/"
    echo "       re-pull from R2 (bash scripts/h20_pull_from_r2.sh) or run a baseline phase first."
    exit 1
fi
echo "[crit] anchoring on ${#CKPTS[@]} checkpoint(s): ${CKPTS[*]}"

mapfile -t CFGS < <(ls -1 "$PHASE"/config_*.yaml 2>/dev/null)
echo "[crit] ${#CFGS[@]} scan configs × ${#CKPTS[@]} ckpts = $(( ${#CFGS[@]} * ${#CKPTS[@]} )) runs, n_steps=$N_STEPS"

card=0
for ckpt in "${CKPTS[@]}"; do
    cs="$(basename "$(dirname "$ckpt")" | sed -E 's/^results_//; s/_seed/_s/')"
    for cfg in "${CFGS[@]}"; do
        tag="$(basename "$cfg" .yaml | sed 's/^config_//')"
        out="$PHASE/results_${cs}__${tag}"
        if [[ "$SKIP_DONE" == "1" && -f "$out/inference_merged.json" ]]; then echo "  [skip $cs/$tag]"; continue; fi
        mkdir -p "$out"
        CUDA_VISIBLE_DEVICES="$card" torchrun --nproc_per_node=1 --standalone \
            -m ecomd.inference.run_large --ckpt "$ckpt" --config "$cfg" \
            --out-dir "$out" --n-steps "$N_STEPS" --n-realizations-per-rank 1 \
            > "$out/run.log" 2>&1 &
        card=$(( (card + 1) % n_gpu ))
        [[ "$card" -eq 0 ]] && wait
    done
done
wait
echo "[crit] done → score: conda run -n ecophys python scripts/score_criticality.py $PHASE"
