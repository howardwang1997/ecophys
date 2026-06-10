#!/usr/bin/env bash
# Daily 17:00 results collection from ALL machines + git push from H20-1.
# SCPs result files (training_log.json, inference_merged.json, checkpoint.pt,
# run logs) from H20-2/3/4 into the local repo, then commits + pushes.
#
# Usage: nohup bash scripts/_daily_push.sh > /tmp/daily_push.log 2>&1 &
set -uo pipefail

REPO_ROOT="/AI4S/Users/howardwang/h204/ecophys"
cd "$REPO_ROOT"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*"; }

collect_remote() {
    local host="$1" remote_root="$2" label="$3"
    log "  Collecting from $label ($host)..."
    local tmp="/tmp/${label}_daily"
    rm -rf "$tmp"
    mkdir -p "$tmp"

    local n_files
    n_files=$(ssh -o ConnectTimeout=15 root@${host} \
        "cd ${remote_root} && \
         find experiments \( -name 'training_log.json' -o -name 'inference_merged.json' \
           -o -name 'run_info.json' -o -name '*_run_*.log' -o -name 'train_*.log' -o -name 'eval_*.log' \
           -o -name 'abides_raw' -o -name '*.csv' \) \
           -not -name 'checkpoint.pt' -not -path '*/checkpoint.pt' \
         | wc -l" 2>/dev/null)
    log "    $label: $n_files result files found"

    if [[ "$n_files" -eq 0 ]] 2>/dev/null; then return; fi

    ssh -o ConnectTimeout=15 root@${host} \
        "cd ${remote_root} && \
         find experiments \( -name 'training_log.json' -o -name 'inference_merged.json' \
           -o -name 'run_info.json' -o -name '*_run_*.log' -o -name 'train_*.log' -o -name 'eval_*.log' \
           -o -name 'abides_raw' -o -name '*.csv' \) \
           -not -name 'checkpoint.pt' -not -path '*/checkpoint.pt' \
           -print0 | tar czf - --null -T -" \
        2>/dev/null | tar xzf - -C "$tmp" 2>/dev/null

    local n_copied=$(find "${tmp}" -type f 2>/dev/null | wc -l)
    rsync -a "${tmp}/" "${REPO_ROOT}/" 2>/dev/null
    log "    $label: $n_copied files merged → local repo"
    rm -rf "$tmp"
}

do_push() {
    log "═══════════════════════════════════════"
    log "DAILY PUSH START $(date '+%Y-%m-%d %H:%M')"
    log "═══════════════════════════════════════"

    source /root/miniconda3/bin/activate ecophys

    # 1) H20-2: 121 held-out + 117 leverage
    log "[1/4] H20-2 (10.239.75.28) — 121 held-out + 117 leverage"
    collect_remote 10.239.75.28 /AI4S/Users/howardwang/h202_amar/ecophys h20_2

    # 2) H20-3: 114 btcusdt + 117 leverage
    log "[2/4] H20-3 (10.239.68.24) — 114 btcusdt + 117 leverage"
    collect_remote 10.239.68.24 /root/ecophys h20_3

    # 3) H20-4: ABIDES ceiling
    log "[3/4] H20-4 (10.239.71.11) — ABIDES daily baseline"
    collect_remote 10.239.71.11 /root/ecophys h20_4

    # 4) Progress summary
    log "[4/4] Progress summary:"
    python3 -c "
import glob
dirs = [
    ('118 ndx',       'experiments/118_delta_grid/ndx'),
    ('118 gold',      'experiments/118_delta_grid/gold'),
    ('118 eurusd',    'experiments/118_delta_grid/eurusd'),
    ('118 btc',       'experiments/118_delta_grid/btcusdt'),
    ('114 topup',     'experiments/114_concave_confirm'),
    ('121 r1',        'experiments/121_heldout_regime/r1'),
    ('121 r2',        'experiments/121_heldout_regime/r2'),
    ('117 leverage',  'experiments/117_leverage'),
    ('105 abides',    'experiments/105_abides_ceiling'),
]
for name, d in dirs:
    t = len(glob.glob(f'{d}/config_*.yaml'))
    done = len(glob.glob(f'{d}/results_*/training_log.json'))
    inf = len(glob.glob(f'{d}/results_*/inference_merged.json'))
    if t > 0 or done > 0:
        print(f'  {name:15s}: train {done:3d} eval {inf:3d}')
" 2>&1 | while read line; do log "$line"; done

    # 5) Git add + commit + push
    log "Git commit + push..."
    git add -A 2>&1 | tail -1
    local staged=$(git diff --cached --numstat 2>/dev/null | wc -l)
    if [[ $staged -gt 0 ]]; then
        git commit -m "daily results dump $(date '+%Y-%m-%d %H:%M')" 2>&1 | tail -3
        git push origin feature/exp113-gabaix-solve 2>&1 | tail -3
        log "Pushed $staged files."
    else
        log "Nothing new to commit."
    fi

    log "═══════════════════════════════════════"
    log "DAILY PUSH DONE"
    log "═══════════════════════════════════════"
}

log "=== DAILY PUSH DAEMON START $(date) ==="
log "Fires at 17:00 CST daily. Collecting from H20-2/3/4 before push."

while true; do
    now=$(date +%H:%M)
    if [[ "$now" == "17:00" ]]; then
        do_push 2>&1 | tee -a /tmp/daily_push.log
        sleep 120
    fi
    sleep 55
done
