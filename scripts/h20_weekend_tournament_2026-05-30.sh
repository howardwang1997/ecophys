#!/usr/bin/env bash
# Weekend tournament (2026-05-30) — REVISED after the exp 108 scout reframed the
# blocker as a fat-tail OVERSHOOT (hill 1.38, 91% α<2). Runs the brackets in order;
# may span >1 weekend (completeness over wall-clock). See the plan file.
#
# Brackets:
#   0  109_tail_attack    config-only tail screen (reg OFF, ~10min/cfg, 135 cfg)  ← FIRST, cheapest
#   1  110_moe_tournament A2 MoE mixture fat-tails (N=10K, MMD every=4, 150 cfg)
#   1  111_diffusion      A3 conditional DDPM (baseline fit/sample, 60 cfg)
#   1  108 sv_d3          complete the SIGTERM-killed SV hero (SKIP_DONE re-runs the missing)
#   2  ceiling map        assemble 111 + existing 080/095b SPX baselines + ABIDES fair re-run (manual)
#
# Usage on H20:
#   ssh h20 && cd ecophys
#   git fetch --all && git checkout feature/paper-a-neurips-2027 && git pull
#   bash scripts/h20_pull_from_r2.sh
#   for e in 109_tail_attack 110_moe_tournament 111_diffusion; do \
#       conda run -n ecophys python experiments/$e/generate_configs.py; done
#   bash scripts/h20_weekend_tournament_2026-05-30.sh --probe   # 1 heavy MoE cfg: timing+stability
#   DAEMON=1 bash scripts/h20_weekend_tournament_2026-05-30.sh  # full tournament
#   tail -f experiments/_weekend_*.log

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_weekend_${TIMESTAMP}.log"

PROBE_CFG="experiments/110_moe_tournament/config_moe_k8_tamed_seed0.yaml"  # heaviest (8 experts + reg)

probe() {
    echo "── probe: heaviest MoE cfg $(basename "$PROBE_CFG") ──" | tee -a "$MASTER_LOG"
    local out="experiments/110_moe_tournament/results_moe_k8_tamed_seed0"; rm -rf "$out"
    SECONDS=0
    conda run -n ecophys torchrun --nproc_per_node=1 --standalone \
        -m ecomd.training.train_distributed --config "$PROBE_CFG" --out-dir "$out" 2>&1 | tee -a "$MASTER_LOG"
    echo "  probe wall-clock: ${SECONDS}s (~$((SECONDS/60))m) on 1 card" | tee -a "$MASTER_LOG"
    conda run -n ecophys python - "$out/inference_merged.json" <<'PY' 2>&1 | tee -a "$MASTER_LOG"
import json, sys, math
d=json.load(open(sys.argv[1]))["aggregated"]
g=lambda k: (d.get(k,{}) or {}).get("mean")
ag, ck, hill = g("aggregational_gaussianity"), g("conditional_kurtosis"), g("hill_tail_index")
bad=[k for k,v in d.items() if not (isinstance(v,dict) and v.get("mean") is not None and math.isfinite(v["mean"]))]
print(f"  hill={hill} agg={ag} cond_kurt={ck}")
print("  ✗ NON-FINITE:"+str(bad) if bad else ("  ✗ BLOWUP" if (ag and abs(ag)>1000) or (ck and abs(ck)>100) else "  ✓ stable"))
PY
    echo "  → if stable, launch full: DAEMON=1 bash $0" | tee -a "$MASTER_LOG"
}

run_phase_sim() {  # train_distributed phases (109, 110)
    local d="$1"; local title="$2"
    echo "" | tee -a "$MASTER_LOG"; echo "═══ PHASE $d ═══ $(date) ═══" | tee -a "$MASTER_LOG"
    SECONDS=0
    DAEMON=0 bash scripts/h20_run_phase.sh "$d" 2>&1 | tee -a "$MASTER_LOG" \
        || echo "  [WARN] $d returned non-zero" | tee -a "$MASTER_LOG"
    echo "  [phase $d] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_phase.py "$d" 2>&1 | tee -a "$MASTER_LOG" || true
    conda run -n ecophys python scripts/score_summary.py "$d" --title "$title" 2>&1 | tee -a "$MASTER_LOG" || true
}

run_phase_baseline() {  # run_baseline_fit_eval phases (111)
    local d="$1"; local title="$2"
    echo "" | tee -a "$MASTER_LOG"; echo "═══ PHASE $d (baseline) ═══ $(date) ═══" | tee -a "$MASTER_LOG"
    SECONDS=0
    bash scripts/h20_run_baseline_phase.sh "$d" 2>&1 | tee -a "$MASTER_LOG" \
        || echo "  [WARN] $d returned non-zero" | tee -a "$MASTER_LOG"
    echo "  [phase $d] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_phase.py "$d" 2>&1 | tee -a "$MASTER_LOG" || true
    conda run -n ecophys python scripts/score_summary.py "$d" --title "$title" 2>&1 | tee -a "$MASTER_LOG" || true
}

run_main() {
    echo "═══ WEEKEND TOURNAMENT — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"
    run_phase_sim      "experiments/109_tail_attack"     "109 tail-attack (Bracket0) n=15 SPX"
    run_phase_sim      "experiments/108_neural_sde_scout" "108 sv_d3 completion (SV Paper-B leg)"
    run_phase_sim      "experiments/110_moe_tournament"  "110 MoE (A2) n=30 SPX"
    run_phase_baseline "experiments/111_diffusion"       "111 diffusion (A3) n=30 SPX"
    conda run -n ecophys python -m ecomd.data.checkpoint_sync sync --delete-local 2>&1 | tee -a "$MASTER_LOG" || true
    echo "═══ TOURNAMENT DONE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  Next (Mac): per-fact gate (hill #2 / agg #4 / DFA #8 in-band rate, NOT just n/11)" | tee -a "$MASTER_LOG"
    echo "  vs baseline_mmd; assemble 3-paradigm ceiling map (+ ABIDES fair re-run); champion→5-asset." | tee -a "$MASTER_LOG"
}

case "${1:-}" in
    --probe) probe; exit $? ;;
esac
if [[ "$DAEMON" == "1" ]]; then
    (run_main) >> "$MASTER_LOG" 2>&1 < /dev/null &
    echo "Started weekend tournament in background (PID $!) — log: $MASTER_LOG"; echo "  tail -f $MASTER_LOG"
else
    run_main
fi
