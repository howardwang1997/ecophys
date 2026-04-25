#!/usr/bin/env bash
# H20 inference on already-trained checkpoints from tomorrow.sh queue.
# Produces full 11-fact stylized-facts JSON for Paper A scoreboard.
#
# Each variant has: train_distributed wrote checkpoint.pt + training_log.json
# to results_*/. We run inference rollouts using the matching config + ckpt
# to get final stylized-facts scores (not just the inline 3-stat training
# proxies).
#
# Usage on H20:
#   git pull
#   bash scripts/h20_eval_existing.sh           # all 3 successful runs
#   bash scripts/h20_eval_existing.sh v09_spx   # single
#   NPROC=4 bash scripts/h20_eval_existing.sh

set -uo pipefail

NPROC="${NPROC:-4}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# (variant, config, ckpt-dir)
declare -a JOBS=(
    "v09_spx|experiments/013_v0p9_sps/config_h20_spx_N10k.yaml|experiments/013_v0p9_sps/results_spx"
    "v09_btc|experiments/013_v0p9_sps/config_h20_btc_N10k.yaml|experiments/013_v0p9_sps/results_btc"
    "v10_hawkes|experiments/014_v1p0_hawkes/config_h20_spx_hawkes.yaml|experiments/014_v1p0_hawkes/results_spx"
)

REQUESTED="${1:-all}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

run_one() {
    local label="$1"
    local config="$2"
    local resdir="$3"
    local ckpt="$resdir/checkpoint.pt"
    local log="$resdir/eval_${TIMESTAMP}.log"

    echo ""
    echo "═══ EVAL $label ═══ $(date +%H:%M:%S)"
    echo "  config=$config"
    echo "  ckpt=$ckpt"
    if [[ ! -f "$ckpt" ]]; then
        echo "  ✗ checkpoint missing — skip"
        return 1
    fi

    export DIST_BACKEND="${DIST_BACKEND:-gloo}"
    local start=$(date +%s)
    torchrun --nproc_per_node="$NPROC" --standalone \
        -m ecomd.inference.run_large \
        --ckpt "$ckpt" --config "$config" \
        --n-steps 4000 --n-realizations-per-rank 2 2>&1 | tee "$log"
    local exit_code=${PIPESTATUS[0]}
    local elapsed=$(( $(date +%s) - start ))
    if [[ $exit_code -eq 0 ]]; then
        echo "  ✓ $label done in ${elapsed}s — merged: $resdir/inference_merged.json"
    else
        echo "  ✗ $label FAILED exit=$exit_code"
    fi
}

for entry in "${JOBS[@]}"; do
    IFS='|' read -r label config resdir <<< "$entry"
    if [[ "$REQUESTED" != "all" && "$REQUESTED" != "$label" ]]; then continue; fi
    run_one "$label" "$config" "$resdir"
done

echo ""
echo "All eval jobs done. To pull stylized-facts numbers on Mac:"
echo "  git add experiments/{013_v0p9_sps,014_v1p0_hawkes}/results_*/inference_merged.json"
echo "  git commit -m 'H20 eval: inference_merged.json for v0.9/v1.0 ckpts'"
echo "  git push"
