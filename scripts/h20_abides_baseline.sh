#!/usr/bin/env bash
# H20-side end-to-end ABIDES ceiling probe: run sims → score 11 facts → push R2.
# Runs independently of the 104 training run (can go in parallel; ABIDES is CPU).
#
# Usage (on H20, after `git pull`):
#   ABIDES_ENV=abides bash scripts/h20_abides_baseline.sh
#
# Produces experiments/105_abides_ceiling/results_<cell>/inference_merged.json,
# scored with the SAME scorer as EcoMD so the comparison is like-for-like.

set -euo pipefail

ABIDES_ENV="${ABIDES_ENV:-abides}"
ECOPHYS_ENV="${ECOPHYS_ENV:-ecophys}"
N_SEEDS="${N_SEEDS:-6}"
MODE="${MODE:-intraday}"            # intraday | daily  (see abides_to_returns.py caveat)
BAR="${BAR:-60}"
EXP_DIR="experiments/105_abides_ceiling"
RAW_DIR="${EXP_DIR}/abides_raw"
LOG="${EXP_DIR}/abides_run.log"
mkdir -p "$EXP_DIR"

CELLS=(rmsc04_base rmsc04_morenoise rmsc04_fewnoise rmsc04_morevalue rmsc04_fewvalue)

echo "═══ ABIDES ceiling probe $(date -u +%FT%TZ) ═══" | tee "$LOG"

# 1) run ABIDES sims (abides env)
ABIDES_ENV="$ABIDES_ENV" N_SEEDS="$N_SEEDS" OUT_DIR="$RAW_DIR" \
  bash scripts/h20_run_abides_calibrate.sh 2>&1 | tee -a "$LOG"

# 2) score each cell into inference_merged.json (ecophys env has compute_all)
for cell in "${CELLS[@]}"; do
  conda run --no-capture-output -n "$ECOPHYS_ENV" python scripts/abides_to_returns.py \
    --abides-dir "$RAW_DIR" --cell "$cell" \
    --out-dir "${EXP_DIR}/results_${cell}" --mode "$MODE" --bar "$BAR" \
    2>&1 | tee -a "$LOG" || echo "  [warn] scoring $cell failed" | tee -a "$LOG"
done

# 3) summarise with the canonical scorers (same as EcoMD phases)
conda run --no-capture-output -n "$ECOPHYS_ENV" python scripts/score_phase.py "$EXP_DIR" 2>&1 | tee -a "$LOG" || true
conda run --no-capture-output -n "$ECOPHYS_ENV" python scripts/score_summary.py "$EXP_DIR" \
  --title "ABIDES ceiling probe (rmsc04 variants)" 2>&1 | tee -a "$LOG" || true

# 4) hand back results. PRIMARY path = git (lightweight JSON + scoreboard come
#    back to Mac via `git pull`, exactly like the 102/103 results did). The big
#    raw mid-price CSVs (abides_raw/) are .gitignored below; only push them to R2
#    if you want them archived (best-effort, non-fatal).
echo "─── result handoff ───" | tee -a "$LOG"
echo "  git: commit experiments/105_abides_ceiling (results_*/inference_merged.json + scoreboard.md) and push;" | tee -a "$LOG"
echo "       Mac pulls — same flow as 102/103." | tee -a "$LOG"
if [[ "${PUSH_RAW_R2:-0}" == "1" ]]; then
  conda run --no-capture-output -n "$ECOPHYS_ENV" python -m ecomd.data.r2_sync upload \
    "$RAW_DIR/" "h20_abides_raw/$(date -u +%Y%m%d)/" 2>&1 | tee -a "$LOG" || \
    echo "  [warn] R2 raw-CSV archive non-zero" | tee -a "$LOG"
fi

echo "═══ ABIDES probe done $(date -u +%FT%TZ) — see $EXP_DIR/scoreboard.md ═══" | tee -a "$LOG"
