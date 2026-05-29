#!/usr/bin/env bash
# Exp 108 — neural-SDE stochastic-vol SCOUT (Slot 1, 5-6h H20).
# First GPU-scale test of the tournament's hero entrant (learned multi-timescale
# stochastic volatility). See experiments/108_neural_sde_scout/generate_configs.py
# and the plan file (pull-adaptive-thacker.md).
#
# 60 cfg = 5 cells × 12 seeds, SPX, N=10K, fp32, rollout_reg_every=8 (scout trim).
# Cells: baseline_mmd (anchor) / sv_d1 / sv_d3 / sv_d3_nolev / sv_d3_both.
#
# Wall-clock (anchor: 099b N=10K fp32 no-reg = 9.9 min/cfg; reg every=8 ≈ 36
# min/cfg): 60 cfg on 8 cards ≈ 4.5 h. --probe one heavy cfg first (the SV head
# is new code at N=10K — confirm no NaN/agg-gauss blowup and the real per-cfg time
# before committing the queue).
#
# Usage on H20:
#   ssh h20 && cd ecophys
#   git fetch --all && git checkout feature/paper-a-neurips-2027 && git pull
#   bash scripts/h20_pull_from_r2.sh
#   conda run -n ecophys python experiments/108_neural_sde_scout/generate_configs.py
#   bash scripts/h20_108_neural_sde_scout.sh --probe   # 1 cfg: timing + stability
#   DAEMON=1 bash scripts/h20_108_neural_sde_scout.sh  # full scout (after probe OK)
#   tail -f experiments/_108sde_*.log

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

PHASE="experiments/108_neural_sde_scout"
EXPECT_N=60
PROBE_CFG="$PHASE/config_sv_d3_both_seed0.yaml"   # heaviest cell (price + integrator SV)
MAX_PROBE_MIN="${MAX_PROBE_MIN:-60}"               # alert if 1 cfg > 60 min (=> >8h total)

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_108sde_${TIMESTAMP}.log"

preflight() {
    local fail=0
    echo "── preflight ──" | tee -a "$MASTER_LOG"
    if [[ ! -d "$PHASE" ]]; then
        echo "  ✗ $PHASE missing — run generate_configs.py" | tee -a "$MASTER_LOG"; return 1
    fi
    local n=$(ls "$PHASE"/config_*.yaml 2>/dev/null | grep -v config_mac_smoke | wc -l | tr -d ' ')
    [[ "$n" == "$EXPECT_N" ]] && echo "  ✓ $n configs" | tee -a "$MASTER_LOG" \
        || { echo "  ✗ expected $EXPECT_N configs, found $n" | tee -a "$MASTER_LOG"; fail=1; }
    local n_orphan=$(pgrep -f "torchrun.*ecomd" 2>/dev/null | wc -l | tr -d ' ')
    [[ "$n_orphan" -gt 0 ]] && { echo "  ✗ $n_orphan orphan torchrun — kill first" | tee -a "$MASTER_LOG"; fail=1; } \
        || echo "  ✓ no orphan torchrun" | tee -a "$MASTER_LOG"
    command -v nvidia-smi >/dev/null 2>&1 && echo "  ✓ GPUs: $(nvidia-smi -L 2>/dev/null | wc -l | tr -d ' ')" | tee -a "$MASTER_LOG"
    return $fail
}

# Single-config gate: run ONE SV config (price+integrator placement), measure
# wall-clock, check finite + no aggregational_gaussianity blowup (107 failure mode).
probe() {
    preflight || { echo "ABORT — preflight failed" | tee -a "$MASTER_LOG"; return 1; }
    echo "── single-config probe: $(basename "$PROBE_CFG") ──" | tee -a "$MASTER_LOG"
    local out="$PHASE/results_sv_d3_both_seed0"
    rm -rf "$out"
    SECONDS=0
    conda run -n ecophys torchrun --nproc_per_node=1 --standalone \
        -m ecomd.training.train_distributed \
        --config "$PROBE_CFG" --out-dir "$out" 2>&1 | tee -a "$MASTER_LOG"
    local mins=$(( SECONDS / 60 ))
    echo "  probe wall-clock: ${SECONDS}s (~${mins}m) on 1 card" | tee -a "$MASTER_LOG"
    conda run -n ecophys python - "$out/inference_merged.json" <<'PY' 2>&1 | tee -a "$MASTER_LOG"
import json, sys, math
try:
    d = json.load(open(sys.argv[1])); agg = d["aggregated"]
    ag = agg.get("aggregational_gaussianity", {}).get("mean")
    ck = agg.get("conditional_kurtosis", {}).get("mean")
    hill = agg.get("hill_tail_index", {}).get("mean")
    dfa = agg.get("dfa_hurst_abs_r", {}).get("mean")
    bad = [k for k,v in agg.items() if not (isinstance(v,dict) and v.get("mean") is not None and math.isfinite(v["mean"]))]
    print(f"  agg_gauss={ag}  cond_kurt={ck}  hill={hill}  dfa={dfa}")
    if bad: print("  ✗ NON-FINITE facts:", bad)
    elif (ag and abs(ag)>1000) or (ck and abs(ck)>100): print("  ✗ INSTABILITY BLOWUP — do NOT launch full scout")
    else: print("  ✓ stable single config")
except Exception as e:
    print("  ✗ could not read result:", e)
PY
    echo "  → if stable AND ~${mins}m ≤ ${MAX_PROBE_MIN}m, launch full: DAEMON=1 bash $0" | tee -a "$MASTER_LOG"
    echo "  → if too slow, drop rollout_reg_every→16 or N_SEEDS→8 and re-probe" | tee -a "$MASTER_LOG"
}

run_main() {
    echo "═══ EXP 108 neural-SDE scout — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"
    preflight || { echo "ABORT — preflight failed" | tee -a "$MASTER_LOG"; return 1; }
    SECONDS=0
    DAEMON=0 bash scripts/h20_run_phase.sh "$PHASE" 2>&1 | tee -a "$MASTER_LOG" \
        || echo "  [WARN] phase returned non-zero; continuing to scoring" | tee -a "$MASTER_LOG"
    echo "  [phase] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_phase.py "$PHASE" 2>&1 | tee -a "$MASTER_LOG" || true
    conda run -n ecophys python scripts/score_summary.py "$PHASE" \
        --title "108 neural-SDE SV scout n=12 SPX" 2>&1 | tee -a "$MASTER_LOG" || true
    conda run -n ecophys python -m ecomd.data.checkpoint_sync sync --delete-local 2>&1 | tee -a "$MASTER_LOG" || true
    echo "═══ EXP 108 DONE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  Next (Mac): apply the pre-registered SCOUT GATE per cell — a cell advances" | tee -a "$MASTER_LOG"
    echo "  to the weekend tournament iff it lifts >=1 hard floor (#2/#4/#5/#8) w/o >=20pp" | tee -a "$MASTER_LOG"
    echo "  collateral AND mean n/11 >= baseline_mmd. Attribution: d3-d1, d3-d3_nolev, both-d3." | tee -a "$MASTER_LOG"
}

case "${1:-}" in
    --probe)   probe; exit $? ;;
    --dry-run) preflight; exit $? ;;
esac
if [[ "$DAEMON" == "1" ]]; then
    (run_main) >> "$MASTER_LOG" 2>&1 < /dev/null &
    echo "Started exp-108 scout in background (PID $!) — log: $MASTER_LOG"
    echo "  tail -f $MASTER_LOG"
else
    run_main
fi
