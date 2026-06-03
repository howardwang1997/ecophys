#!/usr/bin/env bash
# Run the timescale-fair ABIDES re-run on a SEPARATE CPU machine, orchestrated FROM H20 via SSH.
# ABIDES is CPU-only (no GPU) → offload it to a side box so the H20 GPUs stay on Paper-A training.
# YOU fill the side machine's IP on H20:  export ABIDES_HOST=<ip>   (the only required setting).
#
# Pipeline: H20 syncs the runner to the remote → remote runs ~300 sim-sessions/cell in P parallel
# shards → H20 pulls the CSVs back → H20 scores in DAILY mode (volume_volatility_corr marked N/A,
# since ABIDES mid-price carries no volume) → score_phase → the three-paradigm frontier figure.
#
# Config (env vars, set on H20):
#   ABIDES_HOST       (required) side machine IP/host         e.g. 10.0.0.7
#   ABIDES_USER       ssh user                                default: $USER
#   ABIDES_SSH_PORT   ssh port                                default: 22
#   ABIDES_REMOTE_DIR repo path on the side machine           default: ~/ecophys
#   ABIDES_ENV        conda env name on the side machine      default: abides
#   N_SEEDS           sim-sessions per cell (daily needs ≥250) default: 300
#   PARALLEL          parallel shards on the side machine     default: 8
#
# Prereqs on the side machine: a clone of this repo at ABIDES_REMOTE_DIR + a conda env ABIDES_ENV
# with JPMC abides (v1) importable. (Setup is one-time; this script does not install abides.)
#
# Usage on H20:
#   export ABIDES_HOST=<ip>                 # <-- you fill this
#   bash scripts/h20_abides_remote.sh launch   # sync + start remote workers (nohup, returns)
#   bash scripts/h20_abides_remote.sh status   # tail remote progress
#   bash scripts/h20_abides_remote.sh fetch    # pull CSVs back + score daily on H20

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

: "${ABIDES_HOST:?set ABIDES_HOST=<side-machine-ip> on H20 first (export ABIDES_HOST=10.0.0.x)}"
ABIDES_USER="${ABIDES_USER:-$USER}"
ABIDES_SSH_PORT="${ABIDES_SSH_PORT:-22}"
ABIDES_REMOTE_DIR="${ABIDES_REMOTE_DIR:-~/ecophys}"
ABIDES_ENV="${ABIDES_ENV:-abides}"
N_SEEDS="${N_SEEDS:-300}"
PARALLEL="${PARALLEL:-8}"

SSH="ssh -p $ABIDES_SSH_PORT ${ABIDES_USER}@${ABIDES_HOST}"
RSYNC_E="ssh -p $ABIDES_SSH_PORT"
RAW_REL="experiments/105_abides_ceiling/abides_raw"
REMOTE_RAW="${ABIDES_REMOTE_DIR}/${RAW_REL}"
REMOTE_LOG="${ABIDES_REMOTE_DIR}/experiments/_abides_remote.log"
CELLS=(rmsc03_base rmsc03_morenoise rmsc03_fewnoise rmsc03_morevalue rmsc03_fewvalue)

launch() {
    echo "[remote] ${ABIDES_USER}@${ABIDES_HOST}:${ABIDES_SSH_PORT}  dir=$ABIDES_REMOTE_DIR  env=$ABIDES_ENV"
    $SSH "echo ok" >/dev/null || { echo "ERROR: cannot ssh to $ABIDES_HOST — check IP/user/port/keys"; exit 1; }
    echo "[remote] syncing runner script to side machine"
    rsync -e "$RSYNC_E" -az scripts/h20_run_abides_calibrate.sh \
        "${ABIDES_USER}@${ABIDES_HOST}:${ABIDES_REMOTE_DIR}/scripts/" \
        || { echo "ERROR: rsync failed (is $ABIDES_REMOTE_DIR a repo clone on the side box?)"; exit 1; }
    # shard N_SEEDS into PARALLEL contiguous ranges, launch each as a background worker
    local per=$(( (N_SEEDS + PARALLEL - 1) / PARALLEL ))
    echo "[remote] launching $PARALLEL shards × ~$per sessions, ${#CELLS[@]} cells, N_SEEDS=$N_SEEDS (nohup)"
    $SSH "cd $ABIDES_REMOTE_DIR && : > $REMOTE_LOG && for s in \$(seq 0 $((PARALLEL-1))); do \
            a=\$(( s * $per )); b=\$(( a + $per - 1 )); [ \$b -ge $((N_SEEDS-1)) ] && b=$((N_SEEDS-1)); \
            [ \$a -gt $((N_SEEDS-1)) ] && continue; \
            nohup env SEED_START=\$a SEED_END=\$b N_SEEDS=$N_SEEDS ABIDES_ENV=$ABIDES_ENV \
              bash scripts/h20_run_abides_calibrate.sh >> $REMOTE_LOG 2>&1 & \
          done; echo \"launched on \$(hostname); raw → $REMOTE_RAW; log → $REMOTE_LOG\""
    echo "[remote] started. check: bash scripts/h20_abides_remote.sh status"
}

status() {
    echo "[remote] CSVs so far:"
    $SSH "ls $REMOTE_RAW 2>/dev/null | wc -l | xargs echo '  count:'; tail -n 8 $REMOTE_LOG 2>/dev/null"
    echo "[remote] target: ${#CELLS[@]} cells × $N_SEEDS = $(( ${#CELLS[@]} * N_SEEDS )) CSVs"
}

fetch() {
    mkdir -p "$RAW_REL"
    echo "[remote] pulling CSVs back to H20"
    rsync -e "$RSYNC_E" -az "${ABIDES_USER}@${ABIDES_HOST}:${REMOTE_RAW}/" "$RAW_REL/" \
        || { echo "ERROR: rsync pull failed"; exit 1; }
    local n; n="$(ls "$RAW_REL"/*.csv 2>/dev/null | wc -l | tr -d ' ')"
    echo "[remote] $n CSVs on H20 → scoring DAILY (vol_vol_corr N/A)"
    for cell in "${CELLS[@]}"; do
        conda run -n ecophys python scripts/abides_to_returns.py \
            --abides-dir "$RAW_REL" --cell "$cell" \
            --out-dir "experiments/105_abides_ceiling/results_${cell}_daily" \
            --mode daily --drop-facts volume_volatility_corr || echo "  [warn] $cell scoring failed"
    done
    conda run -n ecophys python scripts/score_phase.py experiments/105_abides_ceiling 2>&1 | tail -25 || true
    echo "[remote] done. ABIDES daily-fair cells = results_*_daily → assemble the three-paradigm figure."
}

case "${1:-}" in
    launch) launch ;;
    status) status ;;
    fetch)  fetch ;;
    *) echo "usage: ABIDES_HOST=<ip> bash scripts/h20_abides_remote.sh {launch|status|fetch}"; exit 2 ;;
esac
