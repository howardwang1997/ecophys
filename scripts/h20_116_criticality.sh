#!/usr/bin/env bash
# Exp 116 v2 — finite-size scaling (FSS) of the fat-tail overshoot in SYSTEM SIZE N.
# v1's N=2000 readout showed hill(κ) is FLAT → κ is not the control parameter, N is. This sweeps
# hill(N) at fixed learned dynamics over a dense N ladder: is there a critical N_c where the tail
# index crosses α=2 (hill=2) with finite-size scaling (true emergent transition) or a smooth
# crossover? Pure inference from frozen baseline checkpoints — NO retraining. The lightweight
# trajectory recorder (run_large, 2026-06-08 fix) makes N=14000 × T=8000 inference fit one card
# (was the v1 N=10k OOM cause: 5×(T,N,d) tensors ≈ 100 GB → now O(T) memory).
#
# Run on H20-1 (8 cards). Each config does N_REALIZATIONS seeds (run_large realizations) for hill CIs.
# Anchors auto-restore from R2 if delete-synced.
#
# Usage on H20-1:
#   conda run -n ecophys python experiments/116_criticality/generate_configs.py
#   bash scripts/h20_116_criticality.sh
#   conda run -n ecophys python scripts/score_criticality.py experiments/116_criticality
# Tunables: N_STEPS(8000) N_CKPT(3) N_REALIZATIONS(5) SKIP_DONE(1)

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
export DIST_BACKEND="${DIST_BACKEND:-gloo}"
export PYTHONPATH="${PYTHONPATH:-$REPO_ROOT}"

PHASE="experiments/116_criticality"
N_STEPS="${N_STEPS:-8000}"
N_CKPT="${N_CKPT:-3}"
N_REALIZATIONS="${N_REALIZATIONS:-5}"
SKIP_DONE="${SKIP_DONE:-1}"
n_gpu="$(nvidia-smi -L 2>/dev/null | wc -l | tr -d ' ')"; n_gpu="${n_gpu:-1}"; [[ "$n_gpu" -lt 1 ]] && n_gpu=1

# Discover anchor checkpoints — prefer 113, then 114, then 115 baselines. Restore from R2 if absent.
mapfile -t CKPTS < <(ls -1 experiments/11{3,4,5}_*/results_*baseline*/checkpoint.pt 2>/dev/null | head -n "$N_CKPT")
if [[ "${#CKPTS[@]}" -lt "$N_CKPT" ]]; then
    echo "[crit] only ${#CKPTS[@]}/$N_CKPT anchors local — restoring 113 baselines from R2"
    for s in 0 1 2; do
        d="experiments/113_gabaix_solve/results_baseline_seed$s"
        [[ -f "$d/checkpoint.pt" ]] && continue
        conda run -n ecophys python -m ecomd.data.r2_sync download "checkpoints/$d" "$d" 2>/dev/null \
            || echo "  [warn] could not restore $d"
    done
    mapfile -t CKPTS < <(ls -1 experiments/11{3,4,5}_*/results_*baseline*/checkpoint.pt 2>/dev/null | head -n "$N_CKPT")
fi
if [[ "${#CKPTS[@]}" -eq 0 ]]; then
    echo "ERROR: no baseline checkpoints found/restorable. bash scripts/h20_pull_from_r2.sh first."
    exit 1
fi
echo "[crit] anchoring on ${#CKPTS[@]} checkpoint(s): ${CKPTS[*]}"

mapfile -t CFGS < <(ls -1 "$PHASE"/config_*.yaml 2>/dev/null)
echo "[crit] ${#CFGS[@]} configs × ${#CKPTS[@]} anchors × $N_REALIZATIONS seeds = $(( ${#CFGS[@]} * ${#CKPTS[@]} * N_REALIZATIONS )) rollouts, n_steps=$N_STEPS, ${n_gpu} cards"

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
            --out-dir "$out" --n-steps "$N_STEPS" --n-realizations-per-rank "$N_REALIZATIONS" \
            > "$out/run.log" 2>&1 &
        card=$(( (card + 1) % n_gpu ))
        [[ "$card" -eq 0 ]] && wait
    done
done
wait
echo "[crit] done → score: conda run -n ecophys python scripts/score_criticality.py $PHASE"
