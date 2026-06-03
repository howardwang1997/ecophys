#!/usr/bin/env bash
# Exp 114 — 5-asset confirmation of the concave √-impact solve (the pre-registered solve gate).
# exp 113 (SPX) landed: concave β·sign(ED)·s·(|ED|/s)^δ with δ=0.5 (Tóth-Lillo-Bouchaud √-law)
# thins the fat-tail OVERSHOOT to hill≈3 (empirical inverse-cubic), acf² preserved, no collateral,
# net +1.27 (Welch p=0.0014, d=0.90). 114 asks: does the SAME δ=0.5 reproduce α≈3 across markets?
# 390 cfg ≈ 50h on 8×H20 (single-card/cfg ~62min, PARALLEL=8). NO best-of-N — this IS the gate.
#
# Assets: spx, ndx, gold, eurusd (daily) + btcusdt (1-minute = the strongest universality leg).
# Cells:  baseline, concave_d045 (hardens the hill(δ) crossing), concave_d050 (the champion).
# spx baseline + concave_d050 are REUSED from exp 113 (only spx d045 runs here).
#
# Usage on H20 (branch feature/exp113-gabaix-solve):
#   ssh h20 && cd ecophys
#   git fetch --all && git checkout feature/exp113-gabaix-solve && git pull
#   bash scripts/h20_pull_from_r2.sh                 # needs spx/ndx/gold/eurusd daily + btcusdt 1m
#   conda run -n ecophys python experiments/114_concave_confirm/generate_configs.py
#   bash scripts/h20_114_concave_confirm.sh --probe  # btc d050 cfg: timing + data + stability
#   DAEMON=1 bash scripts/h20_114_concave_confirm.sh # full 390-cfg queue (~50h)
#   tail -f experiments/_114_*.log

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"
PHASE="experiments/114_concave_confirm"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_114_${TIMESTAMP}.log"
PROBE_CFG="$PHASE/config_btcusdt_concave_d050_seed0.yaml"   # btc 1m + concave = riskiest path

probe() {
    echo "── probe: $(basename "$PROBE_CFG") (btc 1m data + concave stability) ──" | tee -a "$MASTER_LOG"
    local out="$PHASE/results_btcusdt_concave_d050_seed0"; rm -rf "$out"
    SECONDS=0
    conda run -n ecophys torchrun --nproc_per_node=1 --standalone \
        -m ecomd.training.train_distributed --config "$PROBE_CFG" --out-dir "$out" 2>&1 | tee -a "$MASTER_LOG"
    echo "  probe wall-clock: ${SECONDS}s (~$((SECONDS/60))m) on 1 card" | tee -a "$MASTER_LOG"
    conda run -n ecophys python - "$out" <<'PY' 2>&1 | tee -a "$MASTER_LOG"
import json, sys
from pathlib import Path
o=Path(sys.argv[1]); d=json.load(open(o/"inference_merged.json"))["aggregated"]
g=lambda k:(d.get(k,{}) or {}).get("mean")
print(f"  hill={g('hill_tail_index')} acf2={g('acf_squared_returns')} agg={g('aggregational_gaussianity')}")
ag=g("aggregational_gaussianity")
print("  ✗ BLOWUP" if (ag and abs(ag)>1000) else "  ✓ stable")
print("  → if stable + btc data loaded: DAEMON=1 bash scripts/h20_114_concave_confirm.sh")
PY
}

run_main() {
    echo "═══ EXP 114 CONCAVE CONFIRM (5-asset) — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC  (390 cfg ≈ 50h)" | tee -a "$MASTER_LOG"
    SECONDS=0
    DAEMON=0 bash scripts/h20_run_phase.sh "$PHASE" 2>&1 | tee -a "$MASTER_LOG" \
        || echo "  [WARN] phase non-zero" | tee -a "$MASTER_LOG"
    echo "  [phase] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_phase.py "$PHASE" 2>&1 | tee -a "$MASTER_LOG" || true
    conda run -n ecophys python scripts/score_concave_confirm.py "$PHASE" 2>&1 | tee -a "$MASTER_LOG" || true
    conda run -n ecophys python -m ecomd.data.checkpoint_sync sync --delete-local 2>&1 | tee -a "$MASTER_LOG" || true
    echo "═══ DONE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  GATE: d050 vs each asset's baseline — hill∈[2,4] AND acf²∈[.15,.55], Welch+Bonferroni." | tee -a "$MASTER_LOG"
    echo "  SOLVE-CONFIRMED iff ✓ on ≥4/5 assets + no ≥20pp collateral. δ*_fit≈0.5 ⇒ √-law universal." | tee -a "$MASTER_LOG"
}

case "${1:-}" in
    --probe) probe; exit $? ;;
esac
if [[ "$DAEMON" == "1" ]]; then
    (run_main) >> "$MASTER_LOG" 2>&1 < /dev/null &
    echo "Started exp 114 in background (PID $!) — log: $MASTER_LOG"; echo "  tail -f $MASTER_LOG"
else
    run_main
fi
