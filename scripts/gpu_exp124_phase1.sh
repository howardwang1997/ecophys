#!/usr/bin/env bash
# exp 124 Phase 1 (sim side, NO data buy) — sharpen the order-flow prediction for the NCS route.
#   E-S1  OFI dose-response : spx kick dose sweep WITH OFI (reuse control/kick6/jump6 from the OFI run)
#   E-S2  cross-asset OFI   : control + kick6 (OFI) on ndx, gold, btcusdt, eurusd
# Then analyze_sim_ofi_transient per asset + commit the ofi_transient_*.json reports.
# Pure inference, reuse concave_d050 ckpts (all present on .56). OUT_TAG=ofi → does not touch old m1 npz.
# Sized for the 2-card box (100.91.139.56): ~510 rollouts ≈ 12 h.
#
#   DAEMON=1 bash scripts/gpu_exp124_phase1.sh
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$REPO_ROOT"
export PATH=/root/miniconda3/bin:${PATH:-}
ENV="${ECOPHYS_ENV:-ecophys}"
EXP="experiments/123_driven_transient"          # reuse the exp-123 configs/ckpts/results tree
NPROC="${NPROC:-$(nvidia-smi -L 2>/dev/null | wc -l)}"; NPROC="${NPROC:-2}"
N_REAL="${N_REAL:-$(( (30 + NPROC - 1) / NPROC ))}"
SPX_DOSES="${SPX_DOSES:-kick0.05 kick0.1 kick0.2 kick0.3 kick0.5 kick1 kick2 kick3 kick12}"  # kick6 already has OFI
XASSETS="${XASSETS:-ndx gold btcusdt eurusd}"
TS="$(date +%Y%m%d_%H%M%S)"; LOG="${EXP}/_ph1_${TS}.log"; mkdir -p "$EXP"
say(){ echo "[ph1 $(date +%H:%M:%S)] $*" | tee -a "$LOG" >&2; }

go(){
  say "═══ exp 124 Phase 1 — NPROC=$NPROC N_REAL=$N_REAL ($(date)) ═══"
  say "── E-S1: spx OFI dose-response ($SPX_DOSES) ──"
  ASSET=spx ARMS="$SPX_DOSES" NPROC="$NPROC" N_REAL="$N_REAL" SEED_BASE=70000 OUT_TAG=ofi \
    ECOPHYS_ENV="$ENV" bash scripts/gpu_exp123_stage1.sh worker 2>&1 | tee -a "$LOG" || say "[warn] spx doses partial"
  say "── E-S2: cross-asset OFI (control+kick6) on $XASSETS ──"
  local a
  for a in $XASSETS; do
    ASSET="$a" ARMS="control kick6" NPROC="$NPROC" N_REAL="$N_REAL" SEED_BASE=71000 OUT_TAG=ofi \
      ECOPHYS_ENV="$ENV" bash scripts/gpu_exp123_stage1.sh worker 2>&1 | tee -a "$LOG" || say "[warn] $a partial"
  done
  say "── analyze: OFI transient per asset (spx incl. doses+jump6 → keeps figure compat) ──"
  conda run --no-capture-output -n "$ENV" python scripts/analyze_sim_ofi_transient.py \
    --exp "$EXP" --asset spx --shock 3000 \
    --arms control kick0.05 kick0.1 kick0.2 kick0.3 kick0.5 kick1 kick2 kick3 kick6 kick12 jump6 \
    2>&1 | tee -a "$LOG" || say "[warn] spx analysis failed"
  for a in $XASSETS; do
    conda run --no-capture-output -n "$ENV" python scripts/analyze_sim_ofi_transient.py \
      --exp "$EXP" --asset "$a" --shock 3000 --arms control kick6 2>&1 | tee -a "$LOG" || say "[warn] $a analysis failed"
  done
  say "── push ──"
  BR="$(git rev-parse --abbrev-ref HEAD)"
  git add "$EXP"/ofi_transient_*.json 2>/dev/null || true
  if git diff --cached --quiet; then say "(nothing to commit)"; else
    git commit -q -m "exp 124 Phase 1: OFI dose-response (spx) + cross-asset OFI (ndx/gold/btc/eurusd)" \
      && { git push origin "$BR" 2>&1 | tee -a "$LOG" \
           || { git pull --rebase -q origin "$BR" && git push origin "$BR" 2>&1 | tee -a "$LOG"; }; }
  fi
  say "═══ DONE ($(date)) ═══"
}
if [[ "${DAEMON:-0}" == "1" ]]; then ( go ) >>"$LOG" 2>&1 < /dev/null & echo "ph1 detached (PID $!) — log: $LOG"; else go; fi
