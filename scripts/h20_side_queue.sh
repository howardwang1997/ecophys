#!/usr/bin/env bash
# Orchestrate a 2-card side machine (H20-2 / H20-3) FROM H20-1 via SSH — the GPU twin of
# h20_abides_remote.sh. Syncs code + data + configs over, starts scripts/side_worker.sh under
# nohup (returns immediately), and later pulls the results_* dirs back.
#
# Machine inventory comes from scripts/machines.local.json (copy scripts/machines.example.json
# and fill IPs/roots — gitignored). Required prereq on the side machine (one-time): a repo clone
# at <root> + a conda env <env> with this package installed (pip install -e .).
#
# Weekend-sprint queue assignment (2026-06-06):
#   h20_2: exp 116 criticality (pure inference) → δ-grid eurusd (exp 118)
#   h20_3: δ-grid ndx → δ-grid btcusdt (exp 118)
#
# Usage on H20-1 (CUTOFF_EPOCH is set by h20_sprint_driver.sh; default now+40h):
#   bash scripts/h20_side_queue.sh h20_2 launch
#   bash scripts/h20_side_queue.sh h20_2 status
#   bash scripts/h20_side_queue.sh h20_2 fetch

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

MACHINE="${1:?usage: $0 <h20_2|h20_3> <launch|status|fetch>}"
ACTION="${2:?usage: $0 <h20_2|h20_3> <launch|status|fetch>}"
MACH_FILE="scripts/machines.local.json"
[[ -f "$MACH_FILE" ]] || { echo "ERROR: $MACH_FILE missing — cp scripts/machines.example.json $MACH_FILE and fill IPs"; exit 1; }
[[ "$MACHINE" == "h20_2" || "$MACHINE" == "h20_3" ]] || { echo "ERROR: unknown machine $MACHINE (h20_2|h20_3)"; exit 2; }

mach() { python3 -c "import json; print(json.load(open('$MACH_FILE'))['$MACHINE'].get('$1', ''))" 2>/dev/null; }
HOST="$(mach host)"; USER_="$(mach user)"; PORT="$(mach ssh_port)"; ROOT="$(mach root)"; ENVN="$(mach env)"
PORT="${PORT:-22}"; ENVN="${ENVN:-ecophys}"; USER_="${USER_:-$USER}"
[[ -n "$HOST" && "$HOST" != "<填IP>" ]] || { echo "ERROR: $MACHINE host not filled in $MACH_FILE"; exit 1; }

SSH="ssh -p $PORT ${USER_}@${HOST}"
RS="rsync -az -e \"ssh -p $PORT\""
DEST="${USER_}@${HOST}:${ROOT}"
LOG_REL="experiments/_side_${MACHINE}.log"
CUTOFF_EPOCH="${CUTOFF_EPOCH:-$(( $(date +%s) + 40 * 3600 ))}"

case "$MACHINE" in
    h20_2) RUN_116="--run-116"; DIRS=(experiments/118_delta_grid/eurusd) ;;
    h20_3) RUN_116="";          DIRS=(experiments/118_delta_grid/ndx experiments/118_delta_grid/btcusdt) ;;
    *) echo "ERROR: unknown machine $MACHINE"; exit 2 ;;
esac

launch() {
    echo "[$MACHINE] ${USER_}@${HOST}:${PORT} root=$ROOT env=$ENVN cutoff=$(date -r "$CUTOFF_EPOCH" 2>/dev/null || date -d "@$CUTOFF_EPOCH" 2>/dev/null || echo "$CUTOFF_EPOCH")"
    $SSH "echo ok" >/dev/null || { echo "ERROR: cannot ssh — check $MACH_FILE / keys"; exit 1; }

    echo "[$MACHINE] syncing code + data + configs"
    $SSH "mkdir -p $ROOT/data $ROOT/scripts"
    eval "$RS --exclude '__pycache__' ecomd pyproject.toml '$DEST/'"
    eval "$RS scripts/side_worker.sh scripts/h20_116_criticality.sh '$DEST/scripts/'"
    eval "$RS data/raw '$DEST/data/'"
    for d in "${DIRS[@]}"; do
        $SSH "mkdir -p $ROOT/$d"
        eval "$RS --exclude 'results_*' --exclude '_*.log' '$d/' '$DEST/$d/'"
    done
    if [[ -n "$RUN_116" ]]; then
        # exp 116 scan configs + the anchor baseline checkpoints it infers from
        $SSH "mkdir -p $ROOT/experiments/116_criticality"
        eval "$RS --exclude 'results_*' --exclude '_*.log' experiments/116_criticality/ '$DEST/experiments/116_criticality/'"
        local n_anchor=0
        for a in experiments/113_gabaix_solve/results_baseline_seed*/checkpoint.pt; do
            [[ -e "$a" ]] || break
            local adir; adir="$(dirname "$a")"
            $SSH "mkdir -p $ROOT/$adir"
            eval "$RS '$a' '$DEST/$adir/'"
            n_anchor=$(( n_anchor + 1 )); [[ "$n_anchor" -ge 3 ]] && break
        done
        [[ "$n_anchor" -ge 1 ]] || { echo "ERROR: no 113 baseline checkpoint.pt on H20-1 — restore from R2 first (driver Phase 0 does this)"; exit 1; }
        echo "[$MACHINE] synced $n_anchor anchor checkpoint(s) for exp 116"
    fi

    echo "[$MACHINE] starting side_worker (nohup): ${RUN_116:+116 → }${DIRS[*]}"
    $SSH "cd $ROOT && : > $LOG_REL && nohup bash scripts/side_worker.sh --cutoff $CUTOFF_EPOCH --par 2 --env $ENVN $RUN_116 ${DIRS[*]} >> $LOG_REL 2>&1 & echo \"launched on \$(hostname) pid \$!\""
    echo "[$MACHINE] started. check: bash scripts/h20_side_queue.sh $MACHINE status"
}

status() {
    $SSH "cd $ROOT && for d in ${DIRS[*]} $( [[ -n "$RUN_116" ]] && echo experiments/116_criticality ); do \
            n=\$(ls \$d/results_*/inference_merged.json 2>/dev/null | wc -l | tr -d ' '); \
            t=\$(ls \$d/config_*.yaml 2>/dev/null | wc -l | tr -d ' '); \
            echo \"  \$d: \$n done\$( [ \$t -gt 0 ] && echo \" / \$t configs\")\"; done; \
          echo '── log tail ──'; tail -n 6 $LOG_REL 2>/dev/null"
}

fetch() {
    local dirs=("${DIRS[@]}")
    [[ -n "$RUN_116" ]] && dirs+=(experiments/116_criticality)
    for d in "${dirs[@]}"; do
        echo "[$MACHINE] pulling $d results back to H20-1"
        mkdir -p "$d"
        eval "$RS --include 'results_*/' --include 'results_*/**' --exclude '*' '$DEST/$d/' '$d/'" \
            || echo "  [warn] fetch $d failed"
        echo "  $(ls "$d"/results_*/inference_merged.json 2>/dev/null | wc -l | tr -d ' ') scored results in $d"
    done
}

case "$ACTION" in
    launch) launch ;;
    status) status ;;
    fetch)  fetch ;;
    *) echo "usage: $0 <h20_2|h20_3> <launch|status|fetch>"; exit 2 ;;
esac
