#!/usr/bin/env bash
# Exp 112 — tail-clamp probe (the ONE untested mechanistic lever; 2026-06-01).
# After the weekend tournament closed the solve arc with no winner and exp 109
# proved the fat-tail overshoot is DYNAMICAL not distributional, this tests a soft
# differentiable clamp on the realized return. PRE-REGISTERED GATE: a cell is a
# SOLVE iff it lifts hill into [2,4] WITHOUT killing acf2 clustering (breaks the
# tail⊥dynamics Pareto coupling). No cell does both → commit to the diagnose.
#
# 5 cells × 20 seeds = 100 cfg, SPX, N=10K fp32, MMD long-rollout every=4 (~5-6h).
#
# Usage on H20:
#   ssh h20 && cd ecophys
#   git fetch --all && git checkout feature/paper-a-neurips-2027 && git pull
#   bash scripts/h20_pull_from_r2.sh
#   conda run -n ecophys python experiments/112_tail_clamp/generate_configs.py
#   bash scripts/h20_112_tail_clamp.sh --probe    # 1 clamp cfg: timing+stability
#   DAEMON=1 bash scripts/h20_112_tail_clamp.sh   # full queue
#   tail -f experiments/_112_*.log

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"
PHASE="experiments/112_tail_clamp"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_112_${TIMESTAMP}.log"
PROBE_CFG="$PHASE/config_tclamp_rel_c3_seed0.yaml"  # most aggressive clamp = stability worst case

probe() {
    echo "── probe: $(basename "$PROBE_CFG") ──" | tee -a "$MASTER_LOG"
    local out="$PHASE/results_tclamp_rel_c3_seed0"; rm -rf "$out"
    SECONDS=0
    conda run -n ecophys torchrun --nproc_per_node=1 --standalone \
        -m ecomd.training.train_distributed --config "$PROBE_CFG" --out-dir "$out" 2>&1 | tee -a "$MASTER_LOG"
    echo "  probe wall-clock: ${SECONDS}s (~$((SECONDS/60))m) on 1 card" | tee -a "$MASTER_LOG"
    conda run -n ecophys python - "$out/inference_merged.json" <<'PY' 2>&1 | tee -a "$MASTER_LOG"
import json, sys, math
d=json.load(open(sys.argv[1]))["aggregated"]
g=lambda k: (d.get(k,{}) or {}).get("mean")
hill, acf2, ag, ck = g("hill_tail_index"), g("acf_squared_returns"), g("aggregational_gaussianity"), g("conditional_kurtosis")
print(f"  hill={hill} acf2={acf2} agg={ag} cond_kurt={ck}")
print("  ✗ BLOWUP" if (ag and abs(ag)>1000) or (ck and abs(ck)>100) else "  ✓ stable")
print("  → if stable: DAEMON=1 bash scripts/h20_112_tail_clamp.sh")
PY
}

run_main() {
    echo "═══ EXP 112 TAIL-CLAMP — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"
    SECONDS=0
    DAEMON=0 bash scripts/h20_run_phase.sh "$PHASE" 2>&1 | tee -a "$MASTER_LOG" \
        || echo "  [WARN] phase returned non-zero" | tee -a "$MASTER_LOG"
    echo "  [phase] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_phase.py "$PHASE" 2>&1 | tee -a "$MASTER_LOG" || true
    conda run -n ecophys python scripts/score_summary.py "$PHASE" --title "112 tail-clamp n=20 SPX" 2>&1 | tee -a "$MASTER_LOG" || true

    # ── Part B: α scaling-curve diagnose (pure inference from Part-A baseline ckpts,
    #    BEFORE the delete-sync so the checkpoints are still local) ──
    echo "" | tee -a "$MASTER_LOG"; echo "═══ PART B: α scaling diagnose — $(date) ═══" | tee -a "$MASTER_LOG"
    conda run -n ecophys python "$PHASE/scaling/generate_scaling_configs.py" 2>&1 | tee -a "$MASTER_LOG" || true
    SECONDS=0
    bash scripts/h20_112_scaling.sh 2>&1 | tee -a "$MASTER_LOG" || echo "  [WARN] scaling phase non-zero" | tee -a "$MASTER_LOG"
    echo "  [scaling] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_scaling.py "$PHASE/scaling" 2>&1 | tee -a "$MASTER_LOG" || true

    conda run -n ecophys python -m ecomd.data.checkpoint_sync sync --delete-local 2>&1 | tee -a "$MASTER_LOG" || true
    echo "═══ DONE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  Part A GATE (Mac): per-cell hill∈[2,4] AND acf2 in-band vs baseline (Welch+Bonferroni)." | tee -a "$MASTER_LOG"
    echo "    Both → SOLVE → 5-asset n=30. Neither → coupling confirmed → diagnose-centered Paper A." | tee -a "$MASTER_LOG"
    echo "  Part B: α_inf intercept (B1), control flatness (B1n), hill/acf2 vs κ Pareto map (B2)." | tee -a "$MASTER_LOG"
}

case "${1:-}" in
    --probe) probe; exit $? ;;
esac
if [[ "$DAEMON" == "1" ]]; then
    (run_main) >> "$MASTER_LOG" 2>&1 < /dev/null &
    echo "Started exp 112 in background (PID $!) — log: $MASTER_LOG"; echo "  tail -f $MASTER_LOG"
else
    run_main
fi
