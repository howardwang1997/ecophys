#!/usr/bin/env bash
# exp 123 OVERNIGHT — Stage-1.5 (spx sub-threshold dose sweep) + Stage-2a (multi-asset revival),
# then eval + verdict + push. Pure inference, reuse checkpoints, fully unattended/detached.
# Reuses the validated gpu_exp123_stage1.sh worker. Safe to run on any box on the shared NFS checkout.
#
#   bash scripts/gpu_exp123_overnight.sh             # foreground
#   DAEMON=1 bash scripts/gpu_exp123_overnight.sh    # detached + log (recommended overnight)
#
# Knobs: NPROC (default = #GPUs on the box), DAEMON, SKIP_STAGE2=1 (sub-threshold only).

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$REPO_ROOT"
export PATH=/root/miniconda3/bin:${PATH:-}          # conda on non-interactive PATH (h20 boxes)
ENV="${ECOPHYS_ENV:-ecophys}"
EXP="experiments/123_driven_transient"
NPROC="${NPROC:-$(nvidia-smi -L 2>/dev/null | wc -l)}"; NPROC="${NPROC:-2}"
SKIP_STAGE2="${SKIP_STAGE2:-0}"
TS="$(date +%Y%m%d_%H%M%S)"; LOG="${EXP}/_overnight_${TS}.log"; mkdir -p "$EXP"
say() { echo "[overnight $(date +%H:%M:%S)] $*" | tee -a "$LOG" >&2; }
nreal() { echo $(( ($1 + NPROC - 1) / NPROC )); }     # rollouts target → per-rank count

go() {
  say "═══ exp 123 overnight — NPROC=$NPROC ($(date)) ═══"

  # ── Stage 1.5: spx sub-threshold dose sweep (control + kick3/6/12 already done in Stage-1) ──
  say "── Stage 1.5: spx sub-threshold kick0.3/0.5/1/2 (target n≈32) ──"
  ASSET=spx ARMS="kick0.3 kick0.5 kick1 kick2" NPROC="$NPROC" N_REAL="$(nreal 32)" \
    SEED_BASE=10000 OUT_TAG=m1 ECOPHYS_ENV="$ENV" \
    bash scripts/gpu_exp123_stage1.sh worker 2>&1 | tee -a "$LOG" || say "[warn] Stage 1.5 partial"

  # ── Stage 2a: multi-asset revival confirm (control + kick3), reuse 114 concave_d050 ckpts ──
  if [[ "$SKIP_STAGE2" != "1" ]]; then
    for a in gold eurusd btcusdt; do
      say "── Stage 2a: $a control+kick3 (target n≈30) ──"
      ASSET="$a" ARMS="control kick3" NPROC="$NPROC" N_REAL="$(nreal 30)" \
        SEED_BASE=40000 OUT_TAG=m1 ECOPHYS_ENV="$ENV" \
        bash scripts/gpu_exp123_stage1.sh worker 2>&1 | tee -a "$LOG" || say "[warn] $a failed (e.g. btc data) — continuing"
    done
  fi

  # ── eval (windowed Hill α(t) all arms + R1) + per-asset verdict ──
  say "── eval + verdict ──"
  bash scripts/gpu_exp123_stage1.sh eval 2>&1 | tee -a "$LOG" || say "[warn] eval partial"
  for a in spx ndx gold eurusd btcusdt; do
    conda run --no-capture-output -n "$ENV" python scripts/score_transfer_law.py \
      --verdict "$EXP" --asset "$a" 2>&1 | tee -a "$LOG" | grep -E "DECISION|H2 shock" || true
  done

  # ── push the small report JSONs (trajectories stay gitignored) ──
  say "── push reports ──"
  git add "$EXP"/results_*/windowed_hill_report.json "$EXP"/r1_warmup_report.json "$EXP"/verdict_*.json 2>/dev/null || true
  if git diff --cached --quiet; then
    say "(nothing to commit)"
  else
    git commit -q -m "exp 123 overnight: Stage-1.5 sub-threshold dose sweep + Stage-2a multi-asset + verdicts" \
      && git push origin HEAD 2>&1 | tee -a "$LOG"
  fi
  say "═══ DONE ($(date)) — read DECISION lines + dose-response in the log ═══"
}

if [[ "${DAEMON:-0}" == "1" ]]; then
  ( go ) >>"$LOG" 2>&1 < /dev/null &
  echo "overnight running detached (PID $!) — log: $LOG  (tail -f it)"
else
  go
fi
