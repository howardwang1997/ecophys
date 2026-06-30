#!/usr/bin/env bash
# Scratch orchestrator: wait for the R1 magnitude run (on the 2-card peer 10.239.72.172) to
# finish, run the windowed-Hill + R1-warmup eval (CPU, on the idle 8-card box), then commit +
# push the exp-123 Stage-1 results to feature/exp113-gabaix-solve. Detached-safe:
# launch with `setsid bash scripts/_wait_then_push_123.sh &` so it survives session drops.
#
# Scope: ONLY experiments/123_driven_transient/ (+ scripts/_wait_then_*.sh + logs/2026-06-18.md).
# .gitignore already drops *.npz / *.pt, so only JSON reports + logs are committed (no big blobs).
# spx (8-card) + ndx (2-card) are already done; R1 (2-card) is the last GPU run.
set -uo pipefail
REPO_ROOT="/AI4S/Users/howardwang/h204/ecophys"; cd "$REPO_ROOT"
PEER="10.239.72.172"; CARD8="10.239.69.71"
EXP="experiments/123_driven_transient"
BRANCH="feature/exp113-gabaix-solve"
POLL="${POLL:-120}"; STABLE_NEEDS="${STABLE_NEEDS:-1}"; MAX_WAIT="${MAX_WAIT:-6h}"
TS="$(date +%Y%m%d_%H%M%S)"; WLOG="experiments/_wait_then_push_123_${TS}.log"

log() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$WLOG"; }

r1_alive_on_peer() { ssh -o ConnectTimeout=10 "$PEER" 'pgrep -f "gpu_exp123_stage1.sh r1" | grep -v grep | head -1' 2>/dev/null; }
r1_last_cell_done() { ssh -o ConnectTimeout=10 "$PEER" "[ \$(ls $REPO_ROOT/$EXP/r1_spx_concave_d050/inference_rank_*.json 2>/dev/null | wc -l) -ge 1 ] && echo yes || echo no" 2>/dev/null | tr -d '\n'; }

log "═══ wait_then_push_123 START ═══"
log "watching R1 on $PEER; poll=${POLL}s; stable=$STABLE_NEEDS; max_wait=$MAX_WAIT"
log "spx(8card) + ndx(2card) already done; R1 baseline cell was ~6/16 at setup"

start=$(date +%s); max_s=$(( ${MAX_WAIT%h} * 3600 )); stable=0
while true; do
  now=$(date +%s); elapsed=$((now - start))
  [ $elapsed -gt $max_s ] && { log "MAX_WAIT exceeded — giving up"; exit 2; }
  al="$(r1_alive_on_peer)"; [ -z "$al" ] && al=0 || al=1
  last="$(r1_last_cell_done)"
  if [ "$al" -eq 0 ] && [ "$last" = "yes" ]; then stable=$((stable+1)); else stable=0; fi
  log "poll: elapsed=${elapsed}s r1_alive=$al last_cell_done=$last stable=$stable/$STABLE_NEEDS"
  [ "$stable" -ge "$STABLE_NEEDS" ] && { log "R1 done → trigger."; break; }
  sleep "$POLL"
done

# --- eval on the idle 8-card box (CPU: windowed Hill per arm + R1 warmup score) ---
log "─── EVAL (windowed-Hill α(t) + R1-warmup) on 8-card ───"
if ssh -o ConnectTimeout=15 "$CARD8" "export PATH=/root/miniconda3/bin:\$PATH; cd $REPO_ROOT && bash scripts/gpu_exp123_stage1.sh eval" 2>&1 | tee -a "$WLOG" | tail -20; then
  log "eval exit OK"
else
  log "WARN: eval non-zero/failed — will push raw results without reports (inspect $WLOG)"
fi
# inventory of reports produced
log "reports present:"
for r in "$EXP"/results_*/m*/windowed_hill_report.json "$EXP"/r1_spx_*/windowed_hill_report.json "$EXP"/r1_warmup_report.json; do
  [ -f "$r" ] && log "  ✓ $r"
done

# --- commit + push (scoped to exp 123) ---
log "─── COMMIT + PUSH to $BRANCH ───"
git add experiments/123_driven_transient scripts/_wait_then_r1.sh scripts/_wait_then_push_123.sh logs/2026-06-18.md 2>&1 | tail -1
staged=$(git diff --cached --numstat 2>/dev/null | wc -l)
log "staged $staged files (npz/pt auto-excluded by .gitignore)."
if [ "$staged" -gt 0 ]; then
  git commit -m "exp 123 Stage-1 results + eval: spx(4 arms) + ndx(2 arms) + R1

Driven-transient run on 3-box fleet. spx control/kick{3,6,12} (n=32/arm, 8-card),
ndx control/kick6 (n=30/arm, 2-card), R1 magnitude baseline+concave_d050 (2-card).
Note: 8-card hit NCCL barrier error on all 4 spx arms AFTER npz save — trajectory
data verified intact (188/188 npz finite, correct shapes, shock signatures present);
inference_merged.json missing for spx arms only (eval reads npz directly). Verdict
reports (windowed-Hill α(t), R1-warmup) included where eval produced them." 2>&1 | tee -a "$WLOG" | tail -3
  log "pushing..."
  if git push origin "$BRANCH" 2>&1 | tee -a "$WLOG" | tail -5; then
    log "✓ PUSHED $staged files to $BRANCH (rev $(git rev-parse --short HEAD))"
  else
    log "✗ PUSH FAILED (auth/network?) — commit is local at $(git rev-parse --short HEAD)"; exit 4
  fi
else
  log "nothing new to commit."
fi
log "═══ wait_then_push_123 DONE ═══"
