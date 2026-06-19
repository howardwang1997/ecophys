#!/usr/bin/env bash
# exp 123 Stage 2b — market-realistic shock channel (NCS Gate 1).
#
# Rebut "state_kick is a mechanical latent perturbation": drive the steady state out of
# equilibrium with an EXOGENOUS PRICE GAP (price_jump) instead of a hidden-latent kick, and ask
# whether the same heavy-tail dip-and-recover appears. price_jump injects r = -mag·σ into the
# REALIZED return at T_SHOCK (enters the return series, shifts the price level, drives the vol
# EWMA → clustering); the heavy tail that follows is ENDOGENOUS. See _apply_shock + PREREG.
#
# Pure inference, reuse the concave_d050 spx checkpoint. The control arm is channel-independent —
# we reuse the committed results_spx_control/windowed_hill_report.json (no re-run).
#
# Sized for the 2-card box (100.91.139.56): spx jump dose sweep {1,2,3,6,12}, n≈30/arm, ~2-2.5 h.
#
#   DAEMON=1 bash scripts/gpu_exp123_stage2b.sh            # detached, unattended
#   bash scripts/gpu_exp123_stage2b.sh                     # foreground

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$REPO_ROOT"
export PATH=/root/miniconda3/bin:${PATH:-}
ENV="${ECOPHYS_ENV:-ecophys}"
EXP="experiments/123_driven_transient"
ASSET="${ASSET:-spx}"
ARMS="${ARMS:-jump1 jump2 jump3 jump6 jump12}"            # price_jump dose sweep (σ-units)
NPROC="${NPROC:-$(nvidia-smi -L 2>/dev/null | wc -l)}"; NPROC="${NPROC:-2}"
N_REAL="${N_REAL:-$(( (30 + NPROC - 1) / NPROC ))}"        # ~30 rollouts/arm
SEED_BASE="${SEED_BASE:-50000}"
TS="$(date +%Y%m%d_%H%M%S)"; LOG="${EXP}/_stage2b_${TS}.log"; mkdir -p "$EXP"
say() { echo "[stage2b $(date +%H:%M:%S)] $*" | tee -a "$LOG" >&2; }

go() {
  say "═══ exp 123 Stage 2b (price_jump) — asset=$ASSET arms='$ARMS' NPROC=$NPROC N_REAL=$N_REAL ($(date)) ═══"
  say "── run jump dose arms (reuse spx ckpt; control reused from Stage-1) ──"
  ASSET="$ASSET" ARMS="$ARMS" NPROC="$NPROC" N_REAL="$N_REAL" SEED_BASE="$SEED_BASE" OUT_TAG=m1 \
    ECOPHYS_ENV="$ENV" bash scripts/gpu_exp123_stage1.sh worker 2>&1 | tee -a "$LOG" || say "[warn] worker partial"
  say "── eval (windowed Hill α(t)) on the new jump arms ──"
  bash scripts/gpu_exp123_stage1.sh eval 2>&1 | tee -a "$LOG" || say "[warn] eval partial"
  say "── verdict (channel=jump; reuses results_${ASSET}_control) ──"
  conda run --no-capture-output -n "$ENV" python scripts/score_transfer_law.py \
    --verdict "$EXP" --asset "$ASSET" --channel jump 2>&1 | tee -a "$LOG" | grep -E "DECISION|post-shock min by|^H1" || true
  say "── push ──"
  git add "$EXP"/results_${ASSET}_jump*/windowed_hill_report.json "$EXP"/verdict_${ASSET}_jump.json 2>/dev/null || true
  if git diff --cached --quiet; then say "(nothing to commit)"; else
    git commit -q -m "exp 123 Stage 2b: ${ASSET} price_jump dose sweep (${ARMS}) + jump-channel verdict" \
      && { git pull --rebase -q origin HEAD 2>/dev/null; git push origin HEAD 2>&1 | tee -a "$LOG"; }
  fi
  say "═══ DONE ($(date)) ═══"
}
if [[ "${DAEMON:-0}" == "1" ]]; then ( go ) >>"$LOG" 2>&1 < /dev/null & echo "stage2b detached (PID $!) — log: $LOG"; else go; fi
