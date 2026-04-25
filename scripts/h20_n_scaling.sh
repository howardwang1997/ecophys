#!/usr/bin/env bash
# N-scaling diagnostic — find where v0.9 acf_sim sign flips.
#
# H20 first-round result: at N=10K, acf_sim trains to **−0.33** (real +0.34)
# despite Mac N=200 hitting acf_lag1 ≈ +0.18 with same recipe. This script
# trains v0.9 at N ∈ {500, 2000, 5000, 10000} and writes inline training
# logs. Each is 200 iters × ~120s = ~10 min total on 4-card H20.
#
# Each run uses identical loss weights, lr, dt, chunk_steps (modulo OOM).
# Result is a sign-flip diagnostic: at which N does anti-clustering emerge?
#
# Usage on H20:
#   git pull
#   bash scripts/h20_n_scaling.sh
#
# Outputs:
#   experiments/020_n_scaling/results_n{500,2000,5000,10000}/training_log.json
#   experiments/_n_scaling_log_TIMESTAMP.txt — combined stdout

set -uo pipefail

NPROC="${NPROC:-4}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
QUEUE_LOG="experiments/_n_scaling_log_${TIMESTAMP}.txt"
: > "$QUEUE_LOG"

echo "─────────────────────────────────────────────────────────────" | tee -a "$QUEUE_LOG"
echo " N-scaling diagnostic — $(date)" | tee -a "$QUEUE_LOG"
echo " NPROC=$NPROC" | tee -a "$QUEUE_LOG"
echo "─────────────────────────────────────────────────────────────" | tee -a "$QUEUE_LOG"

run_n() {
    local N="$1"
    local config="experiments/020_n_scaling/config_n${N}.yaml"
    local outdir="experiments/020_n_scaling/results_n${N}"
    mkdir -p "$outdir"
    echo ""
    echo "═══ N=$N ═══ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
    local start=$(date +%s)
    export DIST_BACKEND="${DIST_BACKEND:-gloo}"
    torchrun --nproc_per_node="$NPROC" --standalone \
        -m ecomd.training.train_distributed \
        --config "$config" --out-dir "$outdir" 2>&1 \
      | tee -a "$QUEUE_LOG"
    local exit_code=${PIPESTATUS[0]}
    local elapsed=$(( $(date +%s) - start ))
    echo "  N=$N exit=$exit_code elapsed=${elapsed}s" | tee -a "$QUEUE_LOG"
}

run_n 500
run_n 2000
run_n 5000
run_n 10000

echo "" | tee -a "$QUEUE_LOG"
echo "─────────────────────────────────────────────────────────────" | tee -a "$QUEUE_LOG"
echo " Done. Check acf_sim trajectories:" | tee -a "$QUEUE_LOG"
echo "   conda run -n ecophys python -c \"" | tee -a "$QUEUE_LOG"
echo "     import json,numpy as np;from pathlib import Path" | tee -a "$QUEUE_LOG"
echo "     for N in [500,2000,5000,10000]:" | tee -a "$QUEUE_LOG"
echo "       d=json.loads(Path(f'experiments/020_n_scaling/results_n{N}/training_log.json').read_text())" | tee -a "$QUEUE_LOG"
echo "       last10=d['history'][-10:]" | tee -a "$QUEUE_LOG"
echo "       print(N, np.mean([r['acf_sim'] for r in last10]))\"" | tee -a "$QUEUE_LOG"
echo "─────────────────────────────────────────────────────────────" | tee -a "$QUEUE_LOG"
