#!/usr/bin/env bash
# Batch 1 — 2026-05-26 → review morning 2026-05-28 (the "2-day batch").
#
# SPX-only screening of the two highest-value ceiling-break levers, on n=30.
# The 5-28 review promotes any SPX cell that beats baseline_v3 to the 5-asset
# n=30 confirmation (exp 106), where the significance gate (Δ>0 vs baseline,
# Bonferroni p<0.05) is applied — NOT best-of-N.
#
#   1. 102  multifact loss        420 cfg  ~8h   Thread 1 (PRIMARY): put facts
#                                                 #3/#4/#5/#8 in the gradient +
#                                                 never-tried mse/huber distance
#   2. 103  arch × expanded loss  390 cfg  ~14h  Thread 3: isab / inner_steps /
#                                                 agent_memory / gstate-ablation,
#                                                 all on the expanded loss
#
# Total ~810 cfg ≈ 22h wall (8-card, arch cells ~2× cost) — fits the 2-day
# window with buffer. Track D (105 calibration) + MMD (104) are NOT in this
# bundle: 104 deferred (exp 085 showed return-marginal matching loses to
# baseline; mse/huber in 102 captures the cheap distributional win), and Track D
# is run separately (needs the ABIDES env install — see handback).
#
# Usage on H20:
#   ssh h20 && cd ecophys
#   git fetch --all && git checkout feature/paper-a-neurips-2027 && git pull
#   bash scripts/h20_pull_from_r2.sh
#   conda run -n ecophys python experiments/102_multifact_loss_n30/generate_configs.py
#   conda run -n ecophys python experiments/103_arch_expanded_loss_n30/generate_configs.py
#   bash scripts/h20_batch1_2026-05-26.sh --dry-run     # preflight + estimate
#   DAEMON=1 bash scripts/h20_batch1_2026-05-26.sh
#   tail -f experiments/_batch1_*.log

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

PHASES=(
    "experiments/102_multifact_loss_n30"
    "experiments/103_arch_expanded_loss_n30"
)

expected_n() {
    case "$1" in
        experiments/102_multifact_loss_n30)      echo 420 ;;
        experiments/103_arch_expanded_loss_n30)  echo 390 ;;
        *)                                       echo 0   ;;
    esac
}

summary_title() {
    case "$1" in
        experiments/102_multifact_loss_n30)      echo "102 multi-fact loss (Thread 1) n=30 SPX" ;;
        experiments/103_arch_expanded_loss_n30)  echo "103 arch x expanded loss (Thread 3) n=30 SPX" ;;
        *)                                       echo "$1" ;;
    esac
}

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_batch1_${TIMESTAMP}.log"

preflight() {
    local fail=0
    echo "── preflight checks ──" | tee -a "$MASTER_LOG"
    for d in "${PHASES[@]}"; do
        local expect="$(expected_n "$d")"
        if [[ ! -d "$d" ]]; then
            echo "  ✗ $d does not exist — run its generate_configs.py first" | tee -a "$MASTER_LOG"
            fail=1; continue
        fi
        local n=$(ls "$d"/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$n" != "$expect" ]]; then
            echo "  ✗ $d: expected $expect configs, found $n" | tee -a "$MASTER_LOG"; fail=1
        else
            echo "  ✓ $d: $n configs" | tee -a "$MASTER_LOG"
        fi
    done
    local n_orphan=$(pgrep -f "torchrun.*ecomd" 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$n_orphan" -gt 0 ]]; then
        echo "  ✗ $n_orphan orphan torchrun processes; kill before launch" | tee -a "$MASTER_LOG"; fail=1
    else
        echo "  ✓ no orphan torchrun" | tee -a "$MASTER_LOG"
    fi
    if command -v nvidia-smi >/dev/null 2>&1; then
        echo "  ✓ visible GPUs: $(nvidia-smi -L 2>/dev/null | wc -l | tr -d ' ')" | tee -a "$MASTER_LOG"
    fi
    [[ $fail -eq 0 ]] && { echo "── preflight OK ──" | tee -a "$MASTER_LOG"; return 0; }
    echo "── PREFLIGHT FAILED ──" | tee -a "$MASTER_LOG"; return 1
}

estimate() {
    local total=0 effective=0
    for d in "${PHASES[@]}"; do
        [[ -d "$d" ]] || { echo "  ◌ $d: dir missing" | tee -a "$MASTER_LOG"; continue; }
        local n=$(ls "$d"/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
        local n_done=$(find "$d" -maxdepth 2 -name "inference_merged.json" 2>/dev/null | wc -l | tr -d ' ')
        local eff=$((n - n_done))
        total=$((total + n)); effective=$((effective + eff))
        echo "  $d: $n cfg ($n_done done, $eff effective) ≈ $(( eff * 88 / 80 ))m" | tee -a "$MASTER_LOG"
    done
    local total_mins=$(( effective * 88 / 80 ))
    echo "  Batch1 total: $total cfg (effective $effective) ≈ $((total_mins/60))h $((total_mins%60))m" | tee -a "$MASTER_LOG"
    echo "  (baseline rate 1.1 min/cfg on 8 cards; 103 arch cells run ~2× slower)" | tee -a "$MASTER_LOG"
}

run_main() {
    echo "═══ BATCH 1 2026-05-26 — H20 QUEUE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"
    if [[ "${1:-}" == "--dry-run" ]]; then
        echo "DRY RUN" | tee -a "$MASTER_LOG"; estimate
        preflight || echo "  (preflight noted issues; fix before launch)" | tee -a "$MASTER_LOG"
        return 0
    fi
    preflight || { echo "ABORT — preflight failed." | tee -a "$MASTER_LOG"; return 1; }
    for d in "${PHASES[@]}"; do
        echo "" | tee -a "$MASTER_LOG"
        echo "═══ PHASE: $d ═══ $(date) ═══" | tee -a "$MASTER_LOG"
        SECONDS=0
        if ! DAEMON=0 bash scripts/h20_run_phase.sh "$d" 2>&1 | tee -a "$MASTER_LOG"; then
            echo "  [WARN] phase $d returned non-zero; continuing" | tee -a "$MASTER_LOG"
        fi
        echo "  [phase $d] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
        local title="$(summary_title "$d")"
        conda run -n ecophys python scripts/score_phase.py "$d" 2>&1 | tee -a "$MASTER_LOG" || true
        conda run -n ecophys python scripts/score_summary.py "$d" --title "$title" 2>&1 | tee -a "$MASTER_LOG" || true
    done
    echo "" | tee -a "$MASTER_LOG"
    echo "═══ CHECKPOINT OFFLOAD (R2 sync) — $(date) ═══" | tee -a "$MASTER_LOG"
    conda run -n ecophys python -m ecomd.data.checkpoint_sync sync --delete-local 2>&1 | tee -a "$MASTER_LOG" || \
        echo "  [WARN] checkpoint_sync non-zero (R2 upload likely still ok)" | tee -a "$MASTER_LOG"
    echo "═══ BATCH 1 DONE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  Next (Mac, 2026-05-28): re-score, apply significance gate vs baseline_v3, decide exp-106 promotions." | tee -a "$MASTER_LOG"
}

if [[ "${1:-}" == "--dry-run" ]]; then
    run_main --dry-run; exit 0
fi
if [[ "$DAEMON" == "1" ]]; then
    (run_main) >> "$MASTER_LOG" 2>&1 < /dev/null &
    echo "Started batch1 queue in background (PID $!) — log: $MASTER_LOG"
    echo "  tail -f $MASTER_LOG"
else
    run_main
fi
