#!/usr/bin/env bash
# exp 123 follow-up — completes the dose-response + multi-asset story (pure inference, reuse ckpts):
#   - spx ONSET micro-sweep: state_kick mag {0.05, 0.1, 0.2} → where does revival turn on? (threshold <0.3)
#   - eurusd THRESHOLD test: mag {6, 12} → does a bigger kick revive eurusd (sub-threshold) or not (absent)?
# Then eval + all-asset verdict + push. Detached/unattended. Reuses the validated worker.
#
#   DAEMON=1 bash scripts/gpu_exp123_followup.sh

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$REPO_ROOT"
export PATH=/root/miniconda3/bin:${PATH:-}
ENV="${ECOPHYS_ENV:-ecophys}"
EXP="experiments/123_driven_transient"
NPROC="${NPROC:-$(nvidia-smi -L 2>/dev/null | wc -l)}"; NPROC="${NPROC:-8}"
TS="$(date +%Y%m%d_%H%M%S)"; LOG="${EXP}/_followup_${TS}.log"; mkdir -p "$EXP"
say() { echo "[followup $(date +%H:%M:%S)] $*" | tee -a "$LOG" >&2; }
nreal() { echo $(( (32 + NPROC - 1) / NPROC )); }

go() {
  say "═══ exp 123 follow-up — NPROC=$NPROC ($(date)) ═══"
  say "── spx onset micro-sweep kick0.05/0.1/0.2 ──"
  ASSET=spx ARMS="kick0.05 kick0.1 kick0.2" NPROC="$NPROC" N_REAL="$(nreal)" SEED_BASE=10000 OUT_TAG=m1 \
    ECOPHYS_ENV="$ENV" bash scripts/gpu_exp123_stage1.sh worker 2>&1 | tee -a "$LOG" || say "[warn] spx onset partial"
  say "── eurusd threshold kick6/kick12 ──"
  ASSET=eurusd ARMS="kick6 kick12" NPROC="$NPROC" N_REAL="$(nreal)" SEED_BASE=40000 OUT_TAG=m1 \
    ECOPHYS_ENV="$ENV" bash scripts/gpu_exp123_stage1.sh worker 2>&1 | tee -a "$LOG" || say "[warn] eurusd threshold partial"
  say "── eval + verdict ──"
  bash scripts/gpu_exp123_stage1.sh eval 2>&1 | tee -a "$LOG" || say "[warn] eval partial"
  for a in spx ndx gold eurusd btcusdt; do
    conda run --no-capture-output -n "$ENV" python scripts/score_transfer_law.py --verdict "$EXP" --asset "$a" \
      2>&1 | tee -a "$LOG" | grep -E "DECISION|post-shock min by" || true
  done
  say "── push ──"
  git add "$EXP"/results_*/windowed_hill_report.json "$EXP"/r1_warmup_report.json "$EXP"/verdict_*.json 2>/dev/null || true
  if git diff --cached --quiet; then say "(nothing to commit)"; else
    git commit -q -m "exp 123 follow-up: spx onset micro-sweep (mag 0.05/0.1/0.2) + eurusd threshold (mag 6/12) + verdicts" \
      && git push origin HEAD 2>&1 | tee -a "$LOG"; fi
  say "═══ DONE ($(date)) ═══"
}
if [[ "${DAEMON:-0}" == "1" ]]; then ( go ) >>"$LOG" 2>&1 < /dev/null & echo "followup detached (PID $!) — log: $LOG"; else go; fi
