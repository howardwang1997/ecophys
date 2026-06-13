#!/usr/bin/env bash
# GPU branch (2-card H20) — measure ζ_ED directly to CLOSE the tail-transfer derivation.
#
# Theory (papers/paper_a_methods/theory_tail_transfer.md):  α_return = ζ_ED / δ  ⇒  δ* = ζ_ED/3.
# The δ-grid INFERS ζ_ED≈1.5 via Hill·δ; this measures it DIRECTLY (Hill on the |ED| series) so the
# chain ED-tail → transfer → return-tail is verified end-to-end. Prediction: ζ_ED≈1.50 (ndx≈1.60).
#
# Per asset: locate the concave_d050 checkpoint (reuse if present, else restore from R2, else retrain
# 1 seed), then run run_large.py --save-trajectory (dumps excess_demand) into a FRESH dir under
# experiments/122_zeta_ed/ (never clobbers the δ-grid results), then Hill-estimate |ED|.
#
# Usage (on the 2-card box, branch feature/zeta-ed-gpu):
#   ssh <2card> && cd ecophys
#   git fetch --all && git checkout feature/zeta-ed-gpu && git pull
#   bash scripts/h20_pull_from_r2.sh                 # ensure the 5 assets' parquet are present
#   bash scripts/gpu_zeta_ed_2card.sh --probe        # spx only: locate/retrain + traj + ζ_ED smoke
#   DAEMON=1 bash scripts/gpu_zeta_ed_2card.sh       # all 5 assets (background)
#   tail -f experiments/_zeta_ed_*.log
#
# Cost: reuse path ≈ minutes/asset (inference only); retrain fallback ≈ ~62 min/asset on 2 cards.

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

ENV="${ECOPHYS_ENV:-ecophys}"
NPROC="${NPROC:-2}"                 # 2-card box
SEED="${SEED:-0}"                   # which trained seed to reuse / retrain
N_STEPS="${N_STEPS:-8000}"          # long rollout → more |ED| tail mass for a stable Hill
N_REAL="${N_REAL:-2}"              # per rank; ×NPROC ranks = total rollouts/asset
FORCE_RETRAIN="${FORCE_RETRAIN:-0}"
DAEMON="${DAEMON:-0}"
EXP="experiments/122_zeta_ed"
mkdir -p "$EXP"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="experiments/_zeta_ed_${TS}.log"

# asset → "config_path|ckpt_dir"  (spx from 113; ndx/gold/eurusd/btcusdt from 114)
declare -A SRC=(
  [spx]="experiments/113_gabaix_solve/config_concave_d050_seed${SEED}.yaml|experiments/113_gabaix_solve/results_concave_d050_seed${SEED}"
  [ndx]="experiments/114_concave_confirm/config_ndx_concave_d050_seed${SEED}.yaml|experiments/114_concave_confirm/results_ndx_concave_d050_seed${SEED}"
  [gold]="experiments/114_concave_confirm/config_gold_concave_d050_seed${SEED}.yaml|experiments/114_concave_confirm/results_gold_concave_d050_seed${SEED}"
  [eurusd]="experiments/114_concave_confirm/config_eurusd_concave_d050_seed${SEED}.yaml|experiments/114_concave_confirm/results_eurusd_concave_d050_seed${SEED}"
  [btcusdt]="experiments/114_concave_confirm/config_btcusdt_concave_d050_seed${SEED}.yaml|experiments/114_concave_confirm/results_btcusdt_concave_d050_seed${SEED}"
)

run_asset() {
  local asset="$1" cfg ckdir ckpt out
  cfg="${SRC[$asset]%%|*}"; ckdir="${SRC[$asset]##*|}"; ckpt="${ckdir}/checkpoint.pt"
  out="${EXP}/results_${asset}"; mkdir -p "$out"
  echo "── $asset ── cfg=$cfg" | tee -a "$LOG"
  if [[ ! -f "$cfg" ]]; then echo "  [SKIP] config missing: $cfg" | tee -a "$LOG"; return 0; fi

  # checkpoint_sync has no programmatic 'restore' (only scan/sync/cleanup) — the δ-grid checkpoints
  # were synced to R2 + deleted locally. To reuse the EXACT trained model, manually place its
  # checkpoint.pt at "$ckpt" first (scp from the training box / R2). Otherwise retrain 1 seed — fine
  # for ζ_ED (a seed-robust model property); it just isn't the identical δ-grid seed.
  if [[ "$FORCE_RETRAIN" == "1" || ! -f "$ckpt" ]]; then
    echo "  no local checkpoint at $ckpt → retraining 1 seed (concave_d050) into $out" | tee -a "$LOG"
    conda run --no-capture-output -n "$ENV" torchrun --nproc_per_node="$NPROC" --standalone \
      -m ecomd.training.train_distributed --config "$cfg" --out-dir "$out" >>"$LOG" 2>&1 \
      || { echo "  [ERR] retrain failed for $asset" | tee -a "$LOG"; return 1; }
    ckpt="${out}/checkpoint.pt"
  else
    echo "  reusing trained checkpoint $ckpt" | tee -a "$LOG"
  fi
  [[ -f "$ckpt" ]] || { echo "  [ERR] no checkpoint for $asset" | tee -a "$LOG"; return 1; }

  echo "  inference --save-trajectory (n_steps=$N_STEPS × $((NPROC*N_REAL)) rollouts) → $out" | tee -a "$LOG"
  conda run --no-capture-output -n "$ENV" torchrun --nproc_per_node="$NPROC" --standalone \
    -m ecomd.inference.run_large --ckpt "$ckpt" --config "$cfg" --out-dir "$out" \
    --save-trajectory --n-steps "$N_STEPS" --n-realizations-per-rank "$N_REAL" >>"$LOG" 2>&1 \
    || { echo "  [ERR] inference failed for $asset" | tee -a "$LOG"; return 1; }
  echo "  ✓ $asset: $(ls "$out"/trajectory_*.npz 2>/dev/null | wc -l) trajectory npz" | tee -a "$LOG"
}

run_all() {
  echo "═══ ζ_ED MEASUREMENT (2-card) — $(date) — NPROC=$NPROC SEED=$SEED ═══" | tee -a "$LOG"
  local assets="${ASSETS_OVERRIDE:-spx ndx gold eurusd btcusdt}"
  for a in $assets; do run_asset "$a" || echo "  [continue] $a failed, moving on" | tee -a "$LOG"; done
  echo "─── measuring ζ_ED (Hill on |ED|) vs Hill·δ prediction ───" | tee -a "$LOG"
  conda run --no-capture-output -n "$ENV" python scripts/score_transfer_law.py --measure-zeta "$EXP" \
    2>&1 | tee -a "$LOG" || true
  echo "═══ DONE — $(date) ═══" | tee -a "$LOG"
  echo "  handback: git add $EXP/zeta_ed_report.json $EXP/results_*/inference_merged.json && commit && push" | tee -a "$LOG"
  echo "  (trajectory_*.npz are large — gitignored; push to R2 only if you want them archived)" | tee -a "$LOG"
}

case "${1:-}" in
  --probe) ASSETS_OVERRIDE="spx" run_all; exit $? ;;
esac
if [[ "$DAEMON" == "1" ]]; then
  (run_all) >>"$LOG" 2>&1 < /dev/null &
  echo "Started ζ_ED run in background (PID $!) — log: $LOG"; echo "  tail -f $LOG"
else
  run_all
fi
