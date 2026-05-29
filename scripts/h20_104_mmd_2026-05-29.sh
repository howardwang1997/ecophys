#!/usr/bin/env bash
# Exp 104 — Path B0: fair test of distribution-matching (MMD) on a long rollout.
# Launched 2026-05-29 after Path A (exp 107, per-fact surrogates) was falsified
# at the pre-registered gate. See papers/proposal/plan_v3_addendum_2026-05-28.md
# and experiments/104_mmd_longroll_n30/generate_configs.py.
#
# 150 cfg = 5 cells × 30 seeds, SPX, N=10K, fp32 (the PROVEN-STABLE regime —
# exp 107's N=2000/bf16 destabilised aggregational_gaussianity). MMD fires only
# on the 512-return rollout-reg path (every=4). w_mmd swept {20,50,100} (Mac
# calibration: w_mmd~50 makes MMD ~50% of the structural scale).
#
# Wall-clock estimate (anchor: 099b N=10K fp32 no-reg = 9.9 min/cfg):
#   reg-cfg ≈ 63 min, baseline-cfg ≈ 10 min -> 150 cfg on 8 cards ≈ 16 h.
#   (every=8 -> ~10 h / 25 MMD fires; N_SEEDS=20 -> ~11 h, if a tighter window.)
#
# Wall-clock is UNVERIFIED for this regime (fp32 + N=10K + 512-rollout every=2),
# so this script GATES on a single-config timing+stability probe before the full
# sweep — do NOT skip it (the N-cut that broke 107 was an unverified regime).
#
# Usage on H20:
#   ssh h20 && cd ecophys
#   git fetch --all && git checkout feature/paper-a-neurips-2027 && git pull
#   bash scripts/h20_pull_from_r2.sh
#   conda run -n ecophys python experiments/104_mmd_longroll_n30/generate_configs.py
#   bash scripts/h20_104_mmd_2026-05-29.sh --probe      # 1 cfg: timing + stability gate
#   DAEMON=1 bash scripts/h20_104_mmd_2026-05-29.sh     # full sweep (after probe OK)
#   tail -f experiments/_104mmd_*.log

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

PHASE="experiments/104_mmd_longroll_n30"
EXPECT_N=150
PROBE_CFG="$PHASE/config_mmd_w50_longroll_seed0.yaml"   # heaviest cell (MMD active)
# Expected ~63 min/reg-cfg (N=10K fp32, steps=512 every=4; anchor 099b=9.9 min
# no-reg). Full 150 cfg on 8 cards ≈ 16 h. Alert if a single cfg blows past 90
# min (=> >24 h total; drop rollout_reg_every→8 for ~10 h, or N_SEEDS→20).
MAX_PROBE_MIN="${MAX_PROBE_MIN:-90}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_104mmd_${TIMESTAMP}.log"

preflight() {
    local fail=0
    echo "── preflight ──" | tee -a "$MASTER_LOG"
    if [[ ! -d "$PHASE" ]]; then
        echo "  ✗ $PHASE missing — run generate_configs.py" | tee -a "$MASTER_LOG"; return 1
    fi
    local n=$(ls "$PHASE"/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
    [[ "$n" == "$EXPECT_N" ]] && echo "  ✓ $n configs" | tee -a "$MASTER_LOG" \
        || { echo "  ✗ expected $EXPECT_N configs, found $n" | tee -a "$MASTER_LOG"; fail=1; }
    local n_orphan=$(pgrep -f "torchrun.*ecomd" 2>/dev/null | wc -l | tr -d ' ')
    [[ "$n_orphan" -gt 0 ]] && { echo "  ✗ $n_orphan orphan torchrun — kill first" | tee -a "$MASTER_LOG"; fail=1; } \
        || echo "  ✓ no orphan torchrun" | tee -a "$MASTER_LOG"
    command -v nvidia-smi >/dev/null 2>&1 && echo "  ✓ GPUs: $(nvidia-smi -L 2>/dev/null | wc -l | tr -d ' ')" | tee -a "$MASTER_LOG"
    return $fail
}

# Single-config gate: run ONE MMD config, measure wall-clock, check it produced
# a finite result with no aggregational_gaussianity blowup (the 107 failure mode).
probe() {
    preflight || { echo "ABORT — preflight failed" | tee -a "$MASTER_LOG"; return 1; }
    echo "── single-config probe: $(basename "$PROBE_CFG") ──" | tee -a "$MASTER_LOG"
    local out="$PHASE/results_mmd_w50_longroll_seed0"
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
    bad = [k for k,v in agg.items() if not (isinstance(v,dict) and v.get("mean") is not None and math.isfinite(v["mean"]))]
    print(f"  agg_gaussianity={ag}  conditional_kurtosis={ck}")
    if bad: print("  ✗ NON-FINITE facts:", bad)
    elif (ag and abs(ag)>1000) or (ck and abs(ck)>100): print("  ✗ INSTABILITY BLOWUP — do NOT launch full sweep at this regime")
    else: print("  ✓ stable single config")
except Exception as e:
    print("  ✗ could not read result:", e)
PY
    echo "  → if stable AND ~${mins}m ≤ ${MAX_PROBE_MIN}m, launch full: DAEMON=1 bash $0" | tee -a "$MASTER_LOG"
    echo "  → if too slow, drop budget config-only (rollout_reg_every=4 or N=5000) and re-probe" | tee -a "$MASTER_LOG"
}

run_main() {
    echo "═══ EXP 104 MMD long-rollout — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"
    preflight || { echo "ABORT — preflight failed" | tee -a "$MASTER_LOG"; return 1; }
    SECONDS=0
    DAEMON=0 bash scripts/h20_run_phase.sh "$PHASE" 2>&1 | tee -a "$MASTER_LOG" \
        || echo "  [WARN] phase returned non-zero; continuing to scoring" | tee -a "$MASTER_LOG"
    echo "  [phase] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_phase.py "$PHASE" 2>&1 | tee -a "$MASTER_LOG" || true
    conda run -n ecophys python scripts/score_summary.py "$PHASE" \
        --title "104 MMD long-rollout (Path B0) n=30 SPX" 2>&1 | tee -a "$MASTER_LOG" || true
    conda run -n ecophys python -m ecomd.data.checkpoint_sync sync --delete-local 2>&1 | tee -a "$MASTER_LOG" || true
    echo "═══ EXP 104 DONE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  Next (Mac): Welch+Bonferroni — best mmd_w* vs hybrid_nomm_longroll (isolated MMD)" | tee -a "$MASTER_LOG"
    echo "  + vs baseline_v3 (headline). Pass→exp 106 5-asset; fail→Path B2 (MoE)." | tee -a "$MASTER_LOG"
}

case "${1:-}" in
    --probe)   probe; exit $? ;;
    --dry-run) preflight; exit $? ;;
esac
if [[ "$DAEMON" == "1" ]]; then
    (run_main) >> "$MASTER_LOG" 2>&1 < /dev/null &
    echo "Started exp-104 queue in background (PID $!) — log: $MASTER_LOG"
    echo "  tail -f $MASTER_LOG"
else
    run_main
fi
