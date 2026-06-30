#!/usr/bin/env bash
# Wait for 117_leverage to fully finish, then dump results to github via a git worktree on
# feature/exp113-gabaix-solve (the canonical daily-dump branch). Uses a worktree so the main
# checkout (which sits on the user's WIP branch diagnostics/zeta-ed-burnin-artifact) is NEVER
# touched. Launch detached: nohup setsid bash scripts/_wait_then_push.sh &!
#
# Trigger = 117 driver PID 626224 exited AND nvidia-smi compute-apps == 0 (sustained).
# Collects: 117_leverage (from h202_amar local mount) + pending 114/118/121 (from main repo).
# Excludes: 122_zeta_ed* (ζ_ED refuted/deferred), scratch scripts, *.pt, *.npz (gitignored anyway).
set -uo pipefail
REPO_ROOT="/AI4S/Users/howardwang/h204/ecophys"
AMAR="/AI4S/Users/howardwang/h202_amar/ecophys"
DRIVER_PID="${DRIVER_PID:-626224}"
POLL="${POLL:-180}"
STABLE_NEEDS="${STABLE_NEEDS:-2}"
MAX_WAIT="${MAX_WAIT:-72h}"
DUMP_BRANCH="feature/exp113-gabaix-solve"
WT="/tmp/opencode/exp113-dump-wt"
TS="$(date +%Y%m%d_%H%M%S)"
PLOG="experiments/_wait_then_push_${TS}.log"
cd "$REPO_ROOT"

log() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$PLOG"; }
gpu_procs() { nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | wc -l; }
ck117() { ls "$AMAR"/experiments/117_leverage/results_*/training_log.json 2>/dev/null | wc -l; }

log "═══ wait_then_push START ═══"
log "watching driver PID=$DRIVER_PID; poll=${POLL}s; dump branch=$DUMP_BRANCH"
log "117 done at start: $(ck117)/180"

start=$(date +%s); max_s=$(( ${MAX_WAIT%h} * 3600 )); stable=0
while true; do
  now=$(date +%s); elapsed=$((now - start))
  [ $elapsed -gt $max_s ] && { log "MAX_WAIT exceeded — giving up"; exit 2; }
  busy=$(gpu_procs)
  drv=0; kill -0 "$DRIVER_PID" 2>/dev/null && drv=1
  if [ "$busy" -eq 0 ]; then stable=$((stable+1)); else stable=0; fi
  log "poll: elapsed=${elapsed}s gpu=$busy stable=$stable/$STABLE_NEEDS driver=${drv} 117_done=$(ck117)/180"
  [ "$stable" -ge "$STABLE_NEEDS" ] && { log "GPU idle x$STABLE_NEEDS → trigger."; break; }
  sleep "$POLL"
done

fin=$(ck117)
log "117 final: $fin/180  (if <180, driver crashed — dump proceeds anyway with what completed)"
if [ "$fin" -lt 180 ]; then log "WARNING: 117 incomplete ($fin/180). Pushing partial."; fi

# --- fetch + worktree on the dump branch ---
log "fetching origin..."
git fetch origin "$DUMP_BRANCH" 2>&1 | tee -a "$PLOG" | tail -2
git worktree remove --force "$WT" 2>/dev/null
log "adding worktree at $WT on $DUMP_BRANCH..."
if ! git worktree add "$WT" "$DUMP_BRANCH" 2>&1 | tee -a "$PLOG"; then
  log "worktree add FAILED — aborting push"; exit 3; fi
cd "$WT"
log "ff-merge to origin/$DUMP_BRANCH (local was 1 behind)..."
git merge --ff-only "origin/$DUMP_BRANCH" 2>&1 | tee -a "$PLOG" | tail -2 || log "WARN: ff-merge failed (will push on top of local tip)"

# --- collect results into worktree ---
log "collecting 117_leverage from h202_amar..."
rsync -a --exclude='*.pt' --exclude='*.npz' \
  "$AMAR/experiments/117_leverage/" "$WT/experiments/117_leverage/" 2>&1 | tail -1
log "  117 files in worktree: $(find $WT/experiments/117_leverage/results_* -name training_log.json 2>/dev/null | wc -l)/180"

for exp in 114_concave_confirm 118_delta_grid 121_heldout_regime; do
  if [ -d "$REPO_ROOT/experiments/$exp" ]; then
    log "collecting $exp from main repo..."
    rsync -a --exclude='*.pt' --exclude='*.npz' --exclude='122_zeta_ed*' \
      "$REPO_ROOT/experiments/$exp/" "$WT/experiments/$exp/" 2>&1 | tail -1
  fi
done

# --- commit + push (experiments only; never scripts/122_zeta_ed) ---
git add experiments 2>&1 | tail -1
staged=$(git diff --cached --numstat 2>/dev/null | wc -l)
log "staged $staged files."
if [ "$staged" -gt 0 ]; then
  msg="daily results dump $(date '+%Y-%m-%d %H:%M') (117 leverage complete $fin/180)"
  git commit -m "$msg" 2>&1 | tee -a "$PLOG" | tail -3
  log "pushing to origin/$DUMP_BRANCH..."
  if git push origin "$DUMP_BRANCH" 2>&1 | tee -a "$PLOG" | tail -5; then
    log "✓ PUSHED $staged files to $DUMP_BRANCH"
  else
    log "✗ PUSH FAILED (auth/network?) — commit saved in worktree $WT"; exit 4
  fi
else
  log "nothing new to commit."
fi

cd "$REPO_ROOT"
git worktree remove --force "$WT" 2>/dev/null
log "═══ wait_then_push DONE ═══"
log "main checkout untouched (still on $(git branch --show-current))."
