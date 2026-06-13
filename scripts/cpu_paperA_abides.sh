#!/usr/bin/env bash
# CPU branch — run the two CPU-only Paper-A experiments DIRECTLY on the CPU box (100.105.21.7).
# ABIDES is CPU-only; both legs below are pure-CPU and parallelize across cores.
#
#   daily  (P0)  timescale-fair ABIDES daily re-run  → the agent-based leg of the 3-paradigm frontier.
#                Parallel-shards N_SEEDS sim-sessions across cores, scores in DAILY mode
#                (drops volume_volatility_corr; ABIDES mid has no volume) → results_<cell>_daily/.
#   sbi    (P1)  §7 calibration-cost leg: measure ABIDES per-sim wall T_sim on this box and project
#                the SBI calibration cost (O(10^3-10^4) sims) — the comparand for "ECoMD gradient
#                calibration ~100× faster". (SBI/search is sim-count-bound, so T_sim×budget is the
#                honest number; full SNPE is a refinement.)
#
# Prereqs on this box: clone of the repo + conda env `abides` (JPMC abides v1 importable) + `ecophys`.
#
# Usage (ssh user@100.105.21.7; cd ecophys):
#   git fetch --all && git checkout feature/abides-cpu-paperA && git pull
#   bash scripts/cpu_paperA_abides.sh daily --probe          # 1 seed/cell smoke (sims + daily score)
#   PARALLEL=32 N_SEEDS=300 bash scripts/cpu_paperA_abides.sh daily   # full fair re-run (background-able)
#   bash scripts/cpu_paperA_abides.sh sbi                    # §7 cost leg
#   bash scripts/cpu_paperA_abides.sh all                    # daily then sbi
#   tail -f experiments/_cpu_abides_*.log

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

ABIDES_ENV="${ABIDES_ENV:-abides}"
ECOPHYS_ENV="${ECOPHYS_ENV:-ecophys}"
N_SEEDS="${N_SEEDS:-300}"                     # daily-mode needs ≥~250 close-to-close returns
PARALLEL="${PARALLEL:-$( (command -v nproc >/dev/null && echo $(( $(nproc) > 4 ? $(nproc)-2 : 2 )) ) || echo 8)}"
BAR="${BAR:-60}"
EXP="experiments/105_abides_ceiling"
RAW="${EXP}/abides_raw"
CELLS=(rmsc03_base rmsc03_morenoise rmsc03_fewnoise rmsc03_morevalue rmsc03_fewvalue)
TS="$(date +%Y%m%d_%H%M%S)"
LOG="experiments/_cpu_abides_${TS}.log"
mkdir -p "$EXP"

# ── DAILY: parallel-sharded sims (local), then score in daily mode ──────────────
daily() {
  local probe=0; [[ "${1:-}" == "--probe" ]] && probe=1
  local nseeds="$N_SEEDS"; [[ $probe -eq 1 ]] && nseeds=1
  echo "═══ ABIDES DAILY re-run — $(date) — N_SEEDS=$nseeds PARALLEL=$PARALLEL ═══" | tee -a "$LOG"
  mkdir -p "$RAW"

  # shard [0..nseeds-1] into PARALLEL contiguous ranges; each worker runs all CELLS for its seeds
  local per=$(( (nseeds + PARALLEL - 1) / PARALLEL )) pids=()
  for ((w=0; w<PARALLEL; w++)); do
    local s=$(( w*per )); [[ $s -ge $nseeds ]] && break
    local e=$(( s+per-1 )); [[ $e -ge $nseeds ]] && e=$(( nseeds-1 ))
    echo "  worker $w: seeds $s..$e" | tee -a "$LOG"
    SEED_START="$s" SEED_END="$e" N_SEEDS="$nseeds" OUT_DIR="$RAW" ABIDES_ENV="$ABIDES_ENV" \
      bash scripts/h20_run_abides_calibrate.sh >>"$LOG" 2>&1 &
    pids+=("$!")
  done
  echo "  launched ${#pids[@]} workers; waiting…" | tee -a "$LOG"
  local fail=0; for p in "${pids[@]}"; do wait "$p" || fail=$((fail+1)); done
  [[ $fail -gt 0 ]] && echo "  [warn] $fail worker(s) returned non-zero (partial CSVs OK)" | tee -a "$LOG"

  echo "─── scoring DAILY (drop volume_volatility_corr) ───" | tee -a "$LOG"
  for cell in "${CELLS[@]}"; do
    conda run --no-capture-output -n "$ECOPHYS_ENV" python scripts/abides_to_returns.py \
      --abides-dir "$RAW" --cell "$cell" --out-dir "${EXP}/results_${cell}_daily" \
      --mode daily --bar "$BAR" --drop-facts volume_volatility_corr >>"$LOG" 2>&1 \
      || echo "  [warn] score $cell failed" | tee -a "$LOG"
  done
  conda run --no-capture-output -n "$ECOPHYS_ENV" python scripts/score_summary.py "$EXP" \
    --title "ABIDES daily fair re-run" 2>&1 | tee -a "$LOG" || true
  echo "═══ DAILY DONE — $(date) — results_*_daily/ ═══" | tee -a "$LOG"
  echo "  handback: git add ${EXP}/results_*_daily/inference_merged.json && commit && push (Mac pulls)" | tee -a "$LOG"
}

# ── SBI: measure ABIDES per-sim wall cost, project calibration budget vs ECoMD ──
sbi() {
  echo "═══ §7 ABIDES calibration-cost leg — $(date) ═══" | tee -a "$LOG"
  local probe_seeds="${SBI_TIMING_SEEDS:-4}"   # 4 seeds × 5 cells = 20 timed sims
  local tdir="${EXP}/_sbi_timing"; mkdir -p "$tdir"
  echo "  timing ${probe_seeds}×${#CELLS[@]} ABIDES sims to get per-sim wall T_sim…" | tee -a "$LOG"
  local t0; t0=$(date +%s)
  SEED_START=0 SEED_END=$(( probe_seeds-1 )) N_SEEDS="$probe_seeds" OUT_DIR="$tdir" ABIDES_ENV="$ABIDES_ENV" \
    bash scripts/h20_run_abides_calibrate.sh >>"$LOG" 2>&1 || echo "  [warn] timing run non-zero" | tee -a "$LOG"
  local t1; t1=$(date +%s)
  local nsims; nsims=$(ls "$tdir"/abides_*.csv 2>/dev/null | wc -l | tr -d ' ')
  conda run --no-capture-output -n "$ECOPHYS_ENV" python - "$((t1-t0))" "$nsims" "$EXP" <<'PY' 2>&1 | tee -a "$LOG"
import json, sys
from pathlib import Path
wall, nsims, expdir = float(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])
t_sim = wall / nsims if nsims else float("nan")
budgets = [1000, 5000, 10000]   # standard SBI (SNPE) forward-sim budgets
proj = {b: t_sim * b for b in budgets}
rec = {
    "abides_per_sim_wall_s": t_sim, "timed_sims": nsims, "timed_wall_s": wall,
    "projected_sbi_calibration_wall_s": proj,
    "projected_sbi_calibration_wall_h": {str(b): round(v/3600, 2) for b, v in proj.items()},
    "note": "SBI/search is sim-count-bound; calib wall = T_sim × budget. Compare to ECoMD gradient "
            "calibration wall (ecomd/calibration/wallclock_harness.py, ~10^2 grad steps).",
}
out = expdir / "sbi_cost_report.json"; out.write_text(json.dumps(rec, indent=2))
print(f"  T_sim ≈ {t_sim:.1f}s/sim  (from {nsims} sims in {wall:.0f}s)")
for b in budgets:
    print(f"  SBI budget {b:>6} sims → ~{proj[b]/3600:.1f} h to calibrate ABIDES")
print(f"  → compare to ECoMD gradient calib (~minutes). wrote {out}")
PY
  echo "═══ SBI cost leg DONE — $(date) ═══" | tee -a "$LOG"
  echo "  handback: git add ${EXP}/sbi_cost_report.json && commit && push" | tee -a "$LOG"
}

case "${1:-}" in
  daily) shift; daily "${1:-}" ;;
  sbi)   sbi ;;
  all)   daily "${2:-}"; sbi ;;
  *) echo "usage: $0 {daily [--probe] | sbi | all}"; exit 2 ;;
esac
