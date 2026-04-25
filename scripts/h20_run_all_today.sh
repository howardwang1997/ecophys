#!/usr/bin/env bash
# Master runner — three sequential jobs on H20:
#   1. N-scaling diagnostic (4 runs, ~10 min)
#   2. v2.1 SPX N10K retryA (1 run, ~5 min)
#   3. Eval existing checkpoints (3 runs, ~5 min)
#
# Usage:
#   git pull
#   DAEMON=1 nohup bash scripts/h20_run_all_today.sh > experiments/_run_all_today.log 2>&1 &
#   tail -f experiments/_run_all_today.log

set -uo pipefail

NPROC="${NPROC:-4}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export DIST_BACKEND="${DIST_BACKEND:-gloo}"
export ECOPHYS_DATA_DIR="${ECOPHYS_DATA_DIR:-$REPO_ROOT/data/sample}"
export PYTHONPATH="${PYTHONPATH:-$REPO_ROOT}"

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
MASTER_LOG="experiments/_run_all_today_${TIMESTAMP}.log"

exec > >(tee -a "$MASTER_LOG") 2>&1

echo "═════════════════════════════════════════════════════════════"
echo " H20 run-all — $(date)"
echo " NPROC=$NPROC  DIST_BACKEND=$DIST_BACKEND"
echo " LOG=$MASTER_LOG"
echo "═════════════════════════════════════════════════════════════"

# ─── Job 1: N-scaling ───────────────────────────────────────
echo ""
echo "═══ JOB 1/3: N-scaling ═══ $(date +%H:%M:%S)"
bash scripts/h20_n_scaling.sh
N_SCALE_EXIT=$?

# ─── Job 2: v2.1 retryA ─────────────────────────────────────
echo ""
echo "═══ JOB 2/3: v2.1 SPX N10K retryA ═══ $(date +%H:%M:%S)"
RETRYA_OUT="experiments/016_ecomd_v2/results_h20_retryA"
mkdir -p "$RETRYA_OUT"
torchrun --nproc_per_node="$NPROC" --standalone \
    -m ecomd.training.train_distributed \
    --config experiments/016_ecomd_v2/config_h20_spx_N10k_retryA.yaml \
    --out-dir "$RETRYA_OUT" 2>&1 | tee "$RETRYA_OUT/run_${TIMESTAMP}.log"
RETRYA_EXIT=${PIPESTATUS[0]}

# ─── Job 3: Eval existing ───────────────────────────────────
echo ""
echo "═══ JOB 3/3: Eval existing ═══ $(date +%H:%M:%S)"
bash scripts/h20_eval_existing.sh
EVAL_EXIT=$?

# ─── Summary ────────────────────────────────────────────────
echo ""
echo "═════════════════════════════════════════════════════════════"
echo " Done — $(date)"
echo " N-scaling:  exit=$N_SCALE_EXIT"
echo " RetryA:     exit=$RETRYA_EXIT"
echo " Eval:       exit=$EVAL_EXIT"
echo "═════════════════════════════════════════════════════════════"
