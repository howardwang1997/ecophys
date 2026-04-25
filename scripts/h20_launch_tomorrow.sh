#!/usr/bin/env bash
# Master launcher — runs tomorrow's planned experiments sequentially on H20.
# Produced overnight (2026-04-24) for daytime execution.
#
# Experiment queue (sequential, each ~5-15 min on 4-card H20 DDP gloo):
#   1. v0.9 SPS on SPX daily, N=10000 (headline scaling result)
#   2. v0.9 SPS on BTC 1m, N=10000 (cross-asset at scale)
#   3. v1.0 Hawkes self-excitation on SPX daily, N=10000 (ACF shape fix)
#   4. v0.8 OOS crash validation (train 2015-2019, eval 2020 H1)  [runs on Mac-size]
#
# Total expected wall time: ~30-60 minutes (depending on H20 throughput).
#
# Usage on H20:
#   git pull
#   bash scripts/h20_launch_tomorrow.sh
#
# Or run individual experiments:
#   CONFIG=experiments/013_v0p9_sps/config_h20_spx_N10k.yaml \
#     bash scripts/h20_launch_v1.sh
#
# Results go to experiments/<id>/results/ ; summary appended to
# logs/2026-04-25.md at the end.

set -uo pipefail  # note: NOT -e so one failure doesn't kill queue

NPROC="${NPROC:-4}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
QUEUE_LOG="experiments/_queue_log_${TIMESTAMP}.txt"
: > "$QUEUE_LOG"

echo "─────────────────────────────────────────────────────────────" | tee -a "$QUEUE_LOG"
echo " EcoMD multi-experiment queue — $(date)" | tee -a "$QUEUE_LOG"
echo " NPROC=$NPROC  REPO=$REPO_ROOT" | tee -a "$QUEUE_LOG"
echo " Queue log: $QUEUE_LOG" | tee -a "$QUEUE_LOG"
echo "─────────────────────────────────────────────────────────────" | tee -a "$QUEUE_LOG"

if ! command -v torchrun >/dev/null 2>&1; then
    echo "ERROR: torchrun not found. Activate conda env:"
    echo "  conda activate ecophys"
    exit 1
fi

run_h20_job() {
    local label="$1"
    local config="$2"
    local out_subdir="$3"
    echo ""
    echo "═══ JOB $label ═══ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
    echo "  config=$config" | tee -a "$QUEUE_LOG"
    echo "  out=$out_subdir" | tee -a "$QUEUE_LOG"
    mkdir -p "$out_subdir"
    local job_log="$out_subdir/run_${TIMESTAMP}.log"
    local start=$(date +%s)
    export DIST_BACKEND="${DIST_BACKEND:-gloo}"
    torchrun \
        --nproc_per_node="$NPROC" \
        --standalone \
        -m ecomd.training.train_distributed \
        --config "$config" \
        --out-dir "$out_subdir" 2>&1 | tee "$job_log"
    local exit_code=${PIPESTATUS[0]}
    local elapsed=$(( $(date +%s) - start ))
    if [[ $exit_code -eq 0 ]]; then
        echo "  ✓ $label done in ${elapsed}s" | tee -a "$QUEUE_LOG"
    else
        echo "  ✗ $label FAILED (exit=$exit_code, ${elapsed}s)" | tee -a "$QUEUE_LOG"
    fi
}

run_mac_job() {
    # Lighter experiments that don't need DDP (e.g., crash OOS at N=200).
    local label="$1"
    local cmd="$2"
    echo ""
    echo "═══ JOB $label (non-DDP) ═══ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
    echo "  cmd=$cmd" | tee -a "$QUEUE_LOG"
    local start=$(date +%s)
    bash -c "$cmd" 2>&1 | tee -a "$QUEUE_LOG"
    local exit_code=${PIPESTATUS[0]}
    local elapsed=$(( $(date +%s) - start ))
    if [[ $exit_code -eq 0 ]]; then
        echo "  ✓ $label done in ${elapsed}s" | tee -a "$QUEUE_LOG"
    else
        echo "  ✗ $label FAILED (exit=$exit_code, ${elapsed}s)" | tee -a "$QUEUE_LOG"
    fi
}

# ─── Job 1: v0.9 SPS on SPX daily, N=10K ───
run_h20_job \
    "01_v09_sps_spx_N10k" \
    "experiments/013_v0p9_sps/config_h20_spx_N10k.yaml" \
    "experiments/013_v0p9_sps/results_spx"

# ─── Job 2: v0.9 SPS on BTC 1m, N=10K ───
# Requires target_dataset/period handling in train_distributed. If the
# distributed trainer doesn't yet understand target_dataset=btcusdt, this
# job will fall back to whatever the default loader is. Skip if it errors.
run_h20_job \
    "02_v09_sps_btc_N10k" \
    "experiments/013_v0p9_sps/config_h20_btc_N10k.yaml" \
    "experiments/013_v0p9_sps/results_btc"

# ─── Job 3: v1.0 Hawkes self-excitation on SPX daily, N=10K ───
run_h20_job \
    "03_v10_hawkes_spx" \
    "experiments/014_v1p0_hawkes/config_h20_spx_hawkes.yaml" \
    "experiments/014_v1p0_hawkes/results_spx"

# ─── Job 4: Crash OOS validation (runs on Mac scale, fast, no DDP) ───
# Use whichever Python is on PATH inside the active conda env. On H20 the
# previous "conda run -n ecophys python ..." failed because the inner shell
# couldn't resolve `python` — `conda run` requires either the env's bin to
# be on PATH or `--cwd` set. Using `${CONDA_PREFIX}/bin/python` if defined,
# else falling back to plain `python` (assumes user already activated env).
PY_BIN="${PY_BIN:-${CONDA_PREFIX:+${CONDA_PREFIX}/bin/python}}"
PY_BIN="${PY_BIN:-python}"
run_mac_job \
    "04_crash_oos_v08_train2015_2019" \
    "$PY_BIN experiments/015_crash_oos/run.py --config experiments/015_crash_oos/config_v08_train_2015_2019.yaml"

echo ""
echo "─────────────────────────────────────────────────────────────" | tee -a "$QUEUE_LOG"
echo " Queue finished $(date)" | tee -a "$QUEUE_LOG"
echo "─────────────────────────────────────────────────────────────" | tee -a "$QUEUE_LOG"

echo ""
echo "Next steps (analysis, on Mac):"
echo "  git add -A && git commit -m 'H20 tomorrow results' && git push"
echo "  (then on Mac: git pull && I will read training_log.json's and write a comparison)"
