#!/usr/bin/env bash
# H20 launcher — v2 ablation grid.
#
# Runs experiments/017_v2_ablation/run_grid.py on 4-card H20 using
# torchrun-based DDP. Since each grid assignment is an independent training
# run, we either:
#   (a) Run grid sequentially on rank 0 only (simpler, no cross-rank code)
#   (b) Shard grid across ranks so each rank owns a chunk
#
# For simplicity we use (a) — each grid entry is sequential on a single GPU.
# For (b), a future extension adds --rank / --world-size args to run_grid.py.
#
# Usage:
#   bash scripts/h20_launch_v2_ablation.sh mac_quick        # quick grid
#   bash scripts/h20_launch_v2_ablation.sh h20_full         # full grid
#   GRID_FILE=experiments/017_v2_ablation/grid_custom.yaml \
#       bash scripts/h20_launch_v2_ablation.sh custom

set -uo pipefail

GRID_NAME="${1:-mac_quick}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ -n "${GRID_FILE:-}" ]]; then
    GRID_PATH="$GRID_FILE"
else
    GRID_PATH="experiments/017_v2_ablation/grid_${GRID_NAME}.yaml"
fi

if [[ ! -f "$GRID_PATH" ]]; then
    echo "ERROR: grid file not found: $GRID_PATH"
    echo "Available:"
    ls experiments/017_v2_ablation/grid_*.yaml 2>/dev/null || echo "  (none)"
    exit 1
fi

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
RUN_LOG="experiments/017_v2_ablation/results/grid_run_${TIMESTAMP}.log"
mkdir -p experiments/017_v2_ablation/results

echo "─────────────────────────────────────────────────────────────"
echo " v2 ablation grid launch"
echo " GRID=$GRID_PATH"
echo " LOG=$RUN_LOG"
echo "─────────────────────────────────────────────────────────────"

if ! command -v python >/dev/null 2>&1; then
    echo "ERROR: python not in PATH — activate conda env"
    exit 1
fi

# Each run uses a single GPU via torch's default device select. We bind
# to device 0 here; for parallel sharding (future), replace with
# CUDA_VISIBLE_DEVICES=$rank per-shard and separate --skip / --limit args.
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"

START=$(date +%s)
python experiments/017_v2_ablation/run_grid.py --grid "$GRID_PATH" 2>&1 | tee "$RUN_LOG"
EXIT_CODE=${PIPESTATUS[0]}
END=$(date +%s)
ELAPSED=$((END - START))

echo ""
echo "─────────────────────────────────────────────────────────────"
echo " Grid finished: exit=$EXIT_CODE  elapsed=${ELAPSED}s (~$((ELAPSED/60))min)"
echo " Summary: experiments/017_v2_ablation/results/grid_summary.md"
echo " Log: $RUN_LOG"
echo "─────────────────────────────────────────────────────────────"

exit "$EXIT_CODE"
