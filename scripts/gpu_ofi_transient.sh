#!/usr/bin/env bash
# exp 123 Route-A (sim side): does order-flow imbalance show a shock transient the tail missed?
# Fresh spx rollouts WITH OFI logged (control + kick6 + jump6), then analyze + commit the report.
# Reuses the concave_d050 spx checkpoint. OUT_TAG=ofi → does not touch the old m1/ npz.
#
#   DAEMON=1 bash scripts/gpu_ofi_transient.sh
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$REPO_ROOT"
export PATH=/root/miniconda3/bin:${PATH:-}
ENV="${ECOPHYS_ENV:-ecophys}"
EXP="experiments/123_driven_transient"
ASSET="${ASSET:-spx}"
NPROC="${NPROC:-$(nvidia-smi -L 2>/dev/null | wc -l)}"; NPROC="${NPROC:-2}"
N_REAL="${N_REAL:-$(( (30 + NPROC - 1) / NPROC ))}"
TS="$(date +%Y%m%d_%H%M%S)"; LOG="${EXP}/_ofi_${TS}.log"; mkdir -p "$EXP"
say(){ echo "[ofi $(date +%H:%M:%S)] $*" | tee -a "$LOG" >&2; }
go(){
  say "═══ OFI transient run — asset=$ASSET NPROC=$NPROC N_REAL=$N_REAL ($(date)) ═══"
  ASSET="$ASSET" ARMS="control kick6 jump6" NPROC="$NPROC" N_REAL="$N_REAL" SEED_BASE=60000 OUT_TAG=ofi \
    ECOPHYS_ENV="$ENV" bash scripts/gpu_exp123_stage1.sh worker 2>&1 | tee -a "$LOG" || say "[warn] worker partial"
  say "── analyze OFI transient ──"
  conda run --no-capture-output -n "$ENV" python scripts/analyze_sim_ofi_transient.py \
    --exp "$EXP" --asset "$ASSET" --arms control kick6 jump6 --shock 3000 2>&1 | tee -a "$LOG" || say "[warn] analyze failed"
  say "── revision add-ons: C-a DHVG irreversibility / B3 dip stat / F-a centered memory ──"
  conda run --no-capture-output -n "$ENV" python scripts/analyze_transient_extras.py \
    --exp "$EXP" --asset "$ASSET" --arms control kick6 jump6 --shock 3000 2>&1 | tee -a "$LOG" || say "[warn] extras failed"
  say "── push ──"
  BR="$(git rev-parse --abbrev-ref HEAD)"
  git add "$EXP/ofi_transient_${ASSET}.json" "$EXP/irrev_dhvg_${ASSET}.json" \
          "$EXP/dip_stat_${ASSET}.json" "$EXP/ofi_memory_centered_${ASSET}.json" 2>/dev/null || true
  if git diff --cached --quiet; then say "(nothing to commit)"; else
    git commit -q -m "exp 123 Route-A: OFI transient + revision add-ons (DHVG/dip/centered-memory) (${ASSET})" \
      && { git push origin "$BR" 2>&1 | tee -a "$LOG" \
           || { git pull --rebase -q origin "$BR" && git push origin "$BR" 2>&1 | tee -a "$LOG"; }; }
  fi
  say "═══ DONE ($(date)) ═══"
}
if [[ "${DAEMON:-0}" == "1" ]]; then ( go ) >>"$LOG" 2>&1 < /dev/null & echo "ofi detached (PID $!) — log: $LOG"; else go; fi
