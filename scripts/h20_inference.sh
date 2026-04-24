#!/usr/bin/env bash
# H20 inference launcher. Argument: 'v1' or 'v1plus' (or a full path to config).
#
# Usage:
#   bash scripts/h20_inference.sh v1
#   bash scripts/h20_inference.sh v1plus
#   NPROC=8 bash scripts/h20_inference.sh v1
#   bash scripts/h20_inference.sh v1 --n-steps 8000 --n-realizations-per-rank 4

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <v1|v1plus> [extra torchrun args...]"
    exit 1
fi

VARIANT="$1"; shift

case "$VARIANT" in
    v1)
        CONFIG=experiments/006_ecomd_v1/config_h20.yaml
        CKPT=experiments/006_ecomd_v1/results/checkpoint.pt
        ;;
    v1plus|v1+)
        CONFIG=experiments/007_ecomd_v1plus/config_h20.yaml
        CKPT=experiments/007_ecomd_v1plus/results/checkpoint.pt
        ;;
    *)
        # assume caller passed a config path directly
        CONFIG="$VARIANT"
        CKPT="$(dirname "$CONFIG")/results/checkpoint.pt"
        ;;
esac

NPROC="${NPROC:-4}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -f "$CKPT" ]]; then
    echo "ERROR: checkpoint not found at $CKPT"
    echo "Run training first: bash scripts/h20_launch_${VARIANT}.sh"
    exit 1
fi

echo "─────────────────────────────────────────────────────────────"
echo " EcoMD inference launch"
echo " VARIANT=$VARIANT   NPROC=$NPROC"
echo " CONFIG=$CONFIG"
echo " CKPT=$CKPT"
echo "─────────────────────────────────────────────────────────────"

CMD=(torchrun
    --nproc_per_node="$NPROC"
    --standalone
    -m ecomd.inference.run_large
    --ckpt "$CKPT"
    --config "$CONFIG"
    "$@"
)

echo " Launch command:"
echo "   ${CMD[*]}"
echo ""

if [[ "${DRY_RUN:-0}" == "1" ]]; then
    echo " DRY_RUN=1 — exiting."
    exit 0
fi

exec "${CMD[@]}"
