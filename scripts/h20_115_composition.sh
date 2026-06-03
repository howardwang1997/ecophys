#!/usr/bin/env bash
# Exp 115 — mechanism COMPOSITION: concave √-impact (tails) + SV/leverage (dynamics).
# Paper A's beat-SOTA + it's-a-method lever. The two mechanisms attack DISJOINT facts (113/114:
# concave fixes tails; 108 scout: sv_d3_both helps DFA/leverage). Compose → aim net > 5.96 (SOTA).
# 5 cells × 30 = 150 SPX cfg ≈ 19h on 8×H20. Both mechanisms = orthogonal price_formation flags.
#
# Usage on H20 (branch feature/exp113-gabaix-solve):
#   ssh h20 && cd ecophys
#   git fetch --all && git checkout feature/exp113-gabaix-solve && git pull
#   bash scripts/h20_pull_from_r2.sh
#   conda run -n ecophys python experiments/115_composition/generate_configs.py
#   bash scripts/h20_115_composition.sh --probe   # hero cell: concave+sv stability
#   DAEMON=1 bash scripts/h20_115_composition.sh   # full 150-cfg queue
#   tail -f experiments/_115_*.log

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"
PHASE="experiments/115_composition"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_115_${TIMESTAMP}.log"
PROBE_CFG="$PHASE/config_concave_sv_both_seed0.yaml"   # both mechanisms = riskiest stability

probe() {
    echo "── probe: $(basename "$PROBE_CFG") (concave+SV compose, stability) ──" | tee -a "$MASTER_LOG"
    local out="$PHASE/results_concave_sv_both_seed0"; rm -rf "$out"
    SECONDS=0
    conda run -n ecophys torchrun --nproc_per_node=1 --standalone \
        -m ecomd.training.train_distributed --config "$PROBE_CFG" --out-dir "$out" 2>&1 | tee -a "$MASTER_LOG"
    echo "  probe wall-clock: ${SECONDS}s (~$((SECONDS/60))m) on 1 card" | tee -a "$MASTER_LOG"
    conda run -n ecophys python - "$out" <<'PY' 2>&1 | tee -a "$MASTER_LOG"
import json, sys
from pathlib import Path
o=Path(sys.argv[1]); d=json.load(open(o/"inference_merged.json"))["aggregated"]
g=lambda k:(d.get(k,{}) or {}).get("mean")
print(f"  hill={g('hill_tail_index')} acf2={g('acf_squared_returns')} lev={g('leverage_effect')} "
      f"dfa={g('dfa_hurst_abs_r')} agg={g('aggregational_gaussianity')}")
ag=g("aggregational_gaussianity")
print("  ✗ BLOWUP" if (ag and abs(ag)>1000) else "  ✓ stable")
print("  → if stable: DAEMON=1 bash scripts/h20_115_composition.sh")
PY
}

run_main() {
    echo "═══ EXP 115 COMPOSITION — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC  (150 cfg ≈ 19h)" | tee -a "$MASTER_LOG"
    SECONDS=0
    DAEMON=0 bash scripts/h20_run_phase.sh "$PHASE" 2>&1 | tee -a "$MASTER_LOG" \
        || echo "  [WARN] phase non-zero" | tee -a "$MASTER_LOG"
    echo "  [phase] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_phase.py "$PHASE" 2>&1 | tee -a "$MASTER_LOG" || true
    conda run -n ecophys python scripts/score_composition.py "$PHASE" 2>&1 | tee -a "$MASTER_LOG" || true
    conda run -n ecophys python -m ecomd.data.checkpoint_sync sync --delete-local 2>&1 | tee -a "$MASTER_LOG" || true
    echo "═══ DONE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  GATE G1: concave_sv_both net>5.96 AND tail kept AND ≥1 dynamics floor lifted → champion." | tee -a "$MASTER_LOG"
    echo "  Champion → 5-asset n=30 confirmation (no best-of-N)." | tee -a "$MASTER_LOG"
}

case "${1:-}" in --probe) probe; exit $? ;; esac
if [[ "$DAEMON" == "1" ]]; then
    (run_main) >> "$MASTER_LOG" 2>&1 < /dev/null &
    echo "Started exp 115 in background (PID $!) — log: $MASTER_LOG"; echo "  tail -f $MASTER_LOG"
else
    run_main
fi
