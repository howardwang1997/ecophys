#!/usr/bin/env bash
# Exp 113 — Gabaix mechanism-level solve (the best-result swing; 2026-06-01).
# Changes the MECHANISM that sets the tail exponent: heterogeneous (Pareto-ζ) agent
# masses + concave (sqrt-δ) price impact, ζ/δ LEARNABLE and calibrated by soft_hill.
# GGPS (Nature 2003): Zipf sizes × sqrt impact → inverse-cubic law (α≈3). Both OFF =
# bit-exact. Gate: hill∈[2,4] AND acf2∈[.15,.55] vs baseline → SOLVE → 5-asset n=30.
#
# Usage on H20 (branch feature/exp113-gabaix-solve):
#   ssh h20 && cd ecophys
#   git fetch --all && git checkout feature/exp113-gabaix-solve && git pull
#   bash scripts/h20_pull_from_r2.sh
#   conda run -n ecophys python experiments/113_gabaix_solve/generate_configs.py
#   bash scripts/h20_113_gabaix.sh --probe      # gabaix_learn cfg: timing+stability
#   DAEMON=1 bash scripts/h20_113_gabaix.sh     # full 180-cfg queue
#   tail -f experiments/_113_*.log

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"
PHASE="experiments/113_gabaix_solve"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_113_${TIMESTAMP}.log"
PROBE_CFG="$PHASE/config_concave_learn_seed0.yaml"   # learnable δ concave = representative

probe() {
    echo "── probe: $(basename "$PROBE_CFG") ──" | tee -a "$MASTER_LOG"
    local out="$PHASE/results_gabaix_learn_seed0"; rm -rf "$out"
    SECONDS=0
    conda run -n ecophys torchrun --nproc_per_node=1 --standalone \
        -m ecomd.training.train_distributed --config "$PROBE_CFG" --out-dir "$out" 2>&1 | tee -a "$MASTER_LOG"
    echo "  probe wall-clock: ${SECONDS}s (~$((SECONDS/60))m) on 1 card" | tee -a "$MASTER_LOG"
    conda run -n ecophys python - "$out" <<'PY' 2>&1 | tee -a "$MASTER_LOG"
import json, sys, math, torch
from pathlib import Path
o=Path(sys.argv[1]); d=json.load(open(o/"inference_merged.json"))["aggregated"]
g=lambda k:(d.get(k,{}) or {}).get("mean")
hill, acf2, ag = g("hill_tail_index"), g("acf_squared_returns"), g("aggregational_gaussianity")
sd=torch.load(o/"checkpoint.pt", map_location="cpu")["sim_state_dict"]
z=next((float(torch.exp(v)) for k,v in sd.items() if k.endswith("mass_log_zeta")), None)
de=next((float(torch.sigmoid(v)) for k,v in sd.items() if k.endswith("impact_logit_delta")), None)
print(f"  hill={hill} acf2={acf2} agg={ag} | learned ζ={z} δ={de}")
print("  ✗ BLOWUP" if (ag and abs(ag)>1000) else "  ✓ stable")
print("  → if stable: DAEMON=1 bash scripts/h20_113_gabaix.sh")
PY
}

run_main() {
    echo "═══ EXP 113 GABAIX SOLVE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"
    SECONDS=0
    DAEMON=0 bash scripts/h20_run_phase.sh "$PHASE" 2>&1 | tee -a "$MASTER_LOG" \
        || echo "  [WARN] phase non-zero" | tee -a "$MASTER_LOG"
    echo "  [phase] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_phase.py "$PHASE" 2>&1 | tee -a "$MASTER_LOG" || true
    conda run -n ecophys python scripts/score_gabaix.py "$PHASE" 2>&1 | tee -a "$MASTER_LOG" || true
    conda run -n ecophys python -m ecomd.data.checkpoint_sync sync --delete-local 2>&1 | tee -a "$MASTER_LOG" || true
    echo "═══ DONE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  GATE (Mac): per-cell hill∈[2,4] AND acf2∈[.15,.55] vs baseline (Welch+Bonferroni)." | tee -a "$MASTER_LOG"
    echo "  + read learned (ζ,δ) vs GGPS (1, 0.5). SOLVE → 5-asset n=30 (no best-of-N)." | tee -a "$MASTER_LOG"
}

case "${1:-}" in
    --probe) probe; exit $? ;;
esac
if [[ "$DAEMON" == "1" ]]; then
    (run_main) >> "$MASTER_LOG" 2>&1 < /dev/null &
    echo "Started exp 113 in background (PID $!) — log: $MASTER_LOG"; echo "  tail -f $MASTER_LOG"
else
    run_main
fi
