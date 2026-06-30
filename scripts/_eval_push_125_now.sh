#!/usr/bin/env bash
# exp 125 — one-shot eval + commit + push (runs now that all 3 nodes are DONE).
# Detached-safe: ( setsid nohup bash scripts/_eval_push_125_now.sh >log 2>&1 & )
set -uo pipefail
REPO="/AI4S/Users/howardwang/h204/ecophys"; cd "$REPO"
export PATH=/root/miniconda3/bin:${PATH:-}
EXP="experiments/125_rootcause_controllability"
BR="feature/paper-a-figures-voice"
TS="$(date +%Y%m%d_%H%M%S)"; WLOG="$EXP/_evalpush_${TS}.log"
log(){ printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$WLOG"; }

log "═══ exp125 EVAL+PUSH START ═══"
log "trajectories: $(find $EXP/results_*/ trajectory_*.npz 2>/dev/null | wc -l) ... $(find "$EXP"/results_*/*/trajectory_*.npz 2>/dev/null | wc -l) npz total"

log "─── EVAL (windowed α(t) per arm + OFI; eval_all also commits $EXP/*.json) ───"
if bash scripts/gpu_exp125_orchestrate.sh eval 2>&1 | tee -a "$WLOG" | tail -20; then
  log "eval exit OK"
else
  log "WARN: eval non-zero — committing raw results anyway"
fi

log "─── broader COMMIT + PUSH (per-arm result JSONs + orchestrator btc->btcusdt + git-pull-nonfatal fixes) ───"
git add experiments/125_rootcause_controllability scripts/gpu_exp125_orchestrate.sh 2>&1 | tail -1
staged=$(git diff --cached --numstat 2>/dev/null | wc -l)
log "staged $staged files (.gitignore drops npz/pt)."
if [ "$staged" -gt 0 ]; then
  git commit -m "exp 125 results: root-cause ablations + controllability atlas + rigor + dose law

3-box fleet run (8card atlas/rigor/dose/ablate + 2card-b btcusdt ablate + 2card orchestrator
ndx/btcusdt dose), 1792 trajectories. Inference-only on concave_d050 ckpts (5 assets). Includes
orchestrator fix (ASSET btc->btcusdt config naming + git-pull non-fatal under set -e for the shared
GPFS checkout). Per-arm windowed-hill + inference JSONs committed; raw trajectory npz gitignored." 2>&1 | tee -a "$WLOG" | tail -3
  log "pushing (rebase fallback)..."
  if git push origin "$BR" 2>&1 | tee -a "$WLOG" | tail -4; then
    log "✓ PUSHED to $BR ($(git rev-parse --short HEAD))"
  else
    git pull --rebase -q origin "$BR" 2>&1 | tail -2 | tee -a "$WLOG"
    if git push origin "$BR" 2>&1 | tee -a "$WLOG" | tail -4; then
      log "✓ PUSHED after rebase ($(git rev-parse --short HEAD))"
    else
      log "✗ PUSH FAILED — local commit at $(git rev-parse --short HEAD); resolve manually"; exit 4
    fi
  fi
else
  log "nothing new beyond eval_all's commit."
fi
log "═══ exp125 EVAL+PUSH DONE ═══"
