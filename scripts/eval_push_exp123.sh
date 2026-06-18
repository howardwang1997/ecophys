#!/usr/bin/env bash
# exp 123 — one-shot eval → verdict → push. RUN ON THE BOX that holds the trajectory npz
# (the H20 NFS checkout where Stage-1 wrote results_*/m{1,2}/ + r1_*). Pure CPU, ~10–15 min.
# Emits the H1–H4 driven-transient verdict (P / A / ambiguous) + the R1 magnitude table, then
# pushes only the small report JSONs (trajectories stay gitignored).
#
#   bash scripts/eval_push_exp123.sh            # foreground (watch the DECISION line)
#   DAEMON=1 bash scripts/eval_push_exp123.sh   # background + log, then `tail -f` the log

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$REPO_ROOT"
ENV="${ECOPHYS_ENV:-ecophys}"
EXP="experiments/123_driven_transient"
TS="$(date +%Y%m%d_%H%M%S)"; LOG="${EXP}/_evalpush_${TS}.log"
PY() { conda run --no-capture-output -n "$ENV" python "$@"; }

go() {
  echo "── exp 123 eval ($(date)) ──" | tee -a "$LOG"
  bash scripts/gpu_exp123_stage1.sh eval 2>&1 | tee -a "$LOG"      # windowed Hill α(t) per arm + R1
  echo "── H1–H4 verdict ──" | tee -a "$LOG"
  PY scripts/score_transfer_law.py --verdict "$EXP" --asset spx 2>&1 | tee -a "$LOG"
  PY scripts/score_transfer_law.py --verdict "$EXP" --asset ndx 2>&1 | tee -a "$LOG" || true
  echo "── push report JSONs (trajectories stay gitignored) ──" | tee -a "$LOG"
  git add "$EXP"/results_*/windowed_hill_report.json "$EXP"/r1_warmup_report.json \
          "$EXP"/verdict_*.json 2>/dev/null || true
  if git diff --cached --quiet; then
    echo "(nothing to commit — did eval find trajectory npz? check the log above)" | tee -a "$LOG"
  else
    git commit -q -m "exp 123 eval: windowed Hill α(t) per arm + H1–H4 verdict + R1 warmup-discard" \
      && git push origin HEAD 2>&1 | tee -a "$LOG"
  fi
  echo "── DONE — read the 'DECISION:' line(s) above ──" | tee -a "$LOG"
}

if [[ "${DAEMON:-0}" == "1" ]]; then
  (go) >>"$LOG" 2>&1 < /dev/null &
  echo "eval+push in background (PID $!) — log: $LOG  (tail -f it)"
else
  go
fi
