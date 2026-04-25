#!/usr/bin/env bash
# H20 inference for the v3 batch — score each trained ckpt on stylized facts.

set -uo pipefail

NPROC="${NPROC:-4}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

n_gpu="$(nvidia-smi -L 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$n_gpu" -ge 2 && "$NPROC" -lt 2 ]]; then
    echo "WARNING: NPROC=$NPROC with $n_gpu GPUs visible; bumping NPROC=$n_gpu."
    [[ -z "${FORCE_NPROC:-}" ]] && NPROC="$n_gpu"
fi

declare -a JOBS=(
    "A0|experiments/022_h20_batch/config_a0_baseline.yaml|experiments/022_h20_batch/results_a0"
    "A1|experiments/022_h20_batch/config_a1_multi_asset.yaml|experiments/022_h20_batch/results_a1"
    "A2|experiments/022_h20_batch/config_a2_multi_asset_mshawkes.yaml|experiments/022_h20_batch/results_a2"
    "A3|experiments/022_h20_batch/config_a3_multi_asset_regime.yaml|experiments/022_h20_batch/results_a3"
    "A4|experiments/022_h20_batch/config_a4_multi_asset_twopop.yaml|experiments/022_h20_batch/results_a4"
    "A5|experiments/022_h20_batch/config_a5_all_features.yaml|experiments/022_h20_batch/results_a5"
)

REQUESTED="${1:-all}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

export DIST_BACKEND="${DIST_BACKEND:-gloo}"
export ECOPHYS_DATA_DIR="${ECOPHYS_DATA_DIR:-$REPO_ROOT/data/sample}"

for entry in "${JOBS[@]}"; do
    IFS='|' read -r label config outdir <<< "$entry"
    if [[ "$REQUESTED" != "all" && "$REQUESTED" != "$label" ]]; then continue; fi
    ckpt="$outdir/checkpoint.pt"
    if [[ ! -f "$ckpt" ]]; then
        echo "[skip $label] no checkpoint at $ckpt"
        continue
    fi
    echo ""
    echo "═══ EVAL $label ═══ $(date +%H:%M:%S)"
    log="$outdir/eval_${TIMESTAMP}.log"
    torchrun --nproc_per_node="$NPROC" --standalone \
        -m ecomd.inference.run_large \
        --ckpt "$ckpt" --config "$config" \
        --n-steps 4000 --n-realizations-per-rank 2 2>&1 | tee "$log"
done

echo ""
echo "All done. Run on Mac for scoreboard:"
echo "  conda run -n ecophys python scripts/score_v3_batch.py"
