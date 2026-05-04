#!/usr/bin/env bash
# E3b — re-run inference on all 50 064 checkpoints with --save-trajectory,
# so we have raw return series available to compute ALL 11 stylized facts on
# AR(1)-whitened residuals (Mac-side scoring after this).
#
# Each rollout takes ~85s on H20 with NPROC=1. 50 seeds × 2 realizations = 100
# rollouts → ~2.5h serial OR ~20min in 8-card config-parallel.
#
# Approach: for each seed, run torchrun --nproc=1 with --save-trajectory.
# This produces trajectory_rank0_r0.npz and trajectory_rank0_r1.npz alongside
# the existing inference_rank_0.json. The trajectories are picked up by
# scripts/diagnose_ar1_residual_full_from_traj.py on Mac.
#
# Usage (on H20):
#   ssh h20
#   cd ecophys
#   git fetch --all && git checkout diagnostics/autocorr-ar1 && git pull
#   bash scripts/h20_e3b_save_trajectories.sh
#
# To run only a subset of seeds (e.g. for quick test):
#   E3B_SEEDS="51 70 60 39 38" bash scripts/h20_e3b_save_trajectories.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SRC_DIR="experiments/064_winner_50seed_repro"
N_REPS="${N_REPS:-2}"
N_STEPS="${N_STEPS:-4000}"
NPROC="${NPROC:-1}"
PARALLEL_SEEDS="${PARALLEL_SEEDS:-8}"   # how many seeds to run concurrently

if [[ -n "${E3B_SEEDS:-}" ]]; then
    SEEDS="$E3B_SEEDS"
else
    SEEDS=$(ls -d "$SRC_DIR"/results_p_4_2__2_1_seed* 2>/dev/null | \
            sed -E 's/.*seed([0-9]+)$/\1/' | sort -n)
fi

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
LOG="experiments/_e3b_traj_${TIMESTAMP}.log"
echo "═══ E3b: re-run inference with --save-trajectory ═══ $(date)" | tee -a "$LOG"
echo "  seeds: $(echo $SEEDS | tr '\n' ' ')" | tee -a "$LOG"
echo "  N_REPS=$N_REPS N_STEPS=$N_STEPS NPROC=$NPROC PARALLEL_SEEDS=$PARALLEL_SEEDS" | tee -a "$LOG"

run_one() {
    local seed=$1
    local out_dir="$SRC_DIR/results_p_4_2__2_1_seed$seed"
    local cfg="$SRC_DIR/config_p_4_2__2_1_seed$seed.yaml"
    local ckpt="$out_dir/checkpoint.pt"
    if [[ ! -f "$ckpt" ]] || [[ ! -f "$cfg" ]]; then
        echo "  [skip seed=$seed] missing ckpt or config" | tee -a "$LOG"
        return 0
    fi
    if [[ -f "$out_dir/trajectory_rank0_r0.npz" ]] && [[ "${SKIP_DONE:-1}" == "1" ]]; then
        echo "  [skip seed=$seed] already has trajectory_rank0_r0.npz" | tee -a "$LOG"
        return 0
    fi
    echo "  [seed=$seed] launching inference with --save-trajectory" | tee -a "$LOG"
    torchrun --nproc_per_node="$NPROC" --standalone \
        -m ecomd.inference.run_large \
        --ckpt "$ckpt" \
        --config "$cfg" \
        --n-steps "$N_STEPS" \
        --n-realizations-per-rank "$N_REPS" \
        --out-dir "$out_dir" \
        --save-trajectory \
        2>&1 | sed "s/^/    [seed=$seed] /" | tee -a "$LOG" || true
}

# Rough config-parallel: pipe seeds through xargs -P
echo "$SEEDS" | tr '\n' ' ' | tr ' ' '\n' | grep -v '^$' | \
    xargs -n 1 -P "$PARALLEL_SEEDS" -I {} bash -c "$(declare -f run_one); run_one {}"

echo "═══ E3b done — $(date) ═══" | tee -a "$LOG"
echo ""
echo "Next step (on Mac): pull trajectories and run scoring:"
echo "  bash scripts/h20_push_results_to_r2.sh   # on H20"
echo "  bash scripts/h20_pull_from_r2.sh         # on Mac"
echo "  conda run -n ecophys python scripts/diagnose_ar1_residual_full_from_traj.py"
