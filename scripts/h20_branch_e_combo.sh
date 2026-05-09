#!/usr/bin/env bash
# Branch E — Paper A v4 combo + leftover.
#
# Three experiment dirs (~5h H20 estimated, after SKIP_DONE filtering):
#   082 v4 combo leave-one-out + dose-response   180 cfgs (~2.6h)
#   075 adiabatic inner_{3,10,20} leftover        90 cfgs effective (~1.3h)
#                                                 (150 total, 60 done from Branch D)
#   081 BTC cross-asset (regen w/ correct schema) 60 cfgs (~0.9h)
#
# This batch runs after Branch D (077-081) and addresses two issues:
#   (a) 081 v4combo configs were buggy: Lévy not enabled (wrong field name)
#       AND target_dataset:btc silently fell back to SPX (trainer recognises
#       only btcusdt/2024Q1_1m). The 60 configs (30 baseline + 30 v4combo)
#       have been regenerated with the correct schema.
#   (b) 082 tests whether v4 mechanisms compose. Flagship cell `combo_full`
#       runs all four (Lévy + asym + memk + adiabatic); 3 leave-one-out
#       cells quantify each mechanism's marginal contribution; 2 dose-
#       response cells (asym=0.5, levy=1.7) provide grid finesse.
#
# The launcher hardens against three Branch-D failure modes:
#   - Pre-launch schema verification (catches the 081 bug class)
#   - Pre-launch process probe (Branch D had orphan train procs)
#   - Per-phase scoreboard auto-emit (so partial results visible)
#
# Usage (on H20):
#   ssh h20
#   cd ecophys
#   git fetch --all && git checkout feature/paper-a-v4-mechanisms && git pull
#   unset NPROC && bash scripts/h20_refresh_deps.sh
#   bash scripts/h20_branch_e_combo.sh --dry-run    # preflight
#   DAEMON=1 bash scripts/h20_branch_e_combo.sh
#   tail -f experiments/_branch_e_*.log

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

# Phase order: 082 first (most impactful + longest), then leftovers.
GPU_DIRS=(
    "experiments/082_v4_combo_30seed"
    "experiments/075_adiabatic_30seed"
    "experiments/081_btc_30seed"
)

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_branch_e_${TIMESTAMP}.log"

# ──────────────────────────────────────────────────────────────────────────
# Pre-launch sanity checks
# ──────────────────────────────────────────────────────────────────────────

preflight() {
    local fail=0

    echo "── preflight checks ──" | tee -a "$MASTER_LOG"

    # 1. Verify 081 v4combo schema (the bug from Branch D)
    if [[ -f "experiments/081_btc_30seed/config_btc_v4combo_seed0.yaml" ]]; then
        if ! grep -q "noise_dist: levy" "experiments/081_btc_30seed/config_btc_v4combo_seed0.yaml"; then
            echo "  ✗ 081 v4combo missing noise_dist: levy — schema bug returned" | tee -a "$MASTER_LOG"
            fail=1
        else
            echo "  ✓ 081 v4combo: noise_dist:levy present" | tee -a "$MASTER_LOG"
        fi
        if ! grep -q "target_dataset: btcusdt" "experiments/081_btc_30seed/config_btc_v4combo_seed0.yaml"; then
            echo "  ✗ 081 v4combo: target_dataset != btcusdt; trainer will fall back to SPX" | tee -a "$MASTER_LOG"
            fail=1
        else
            echo "  ✓ 081 v4combo: target_dataset:btcusdt" | tee -a "$MASTER_LOG"
        fi
    fi

    # 2. Verify 082 has 180 configs
    local n82=$(ls experiments/082_v4_combo_30seed/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$n82" != "180" ]]; then
        echo "  ✗ 082 expects 180 configs, found $n82" | tee -a "$MASTER_LOG"
        fail=1
    else
        echo "  ✓ 082 has 180 configs" | tee -a "$MASTER_LOG"
    fi

    # 3. Verify 082 combo_full has all 4 mechanisms wired
    local cf="experiments/082_v4_combo_30seed/config_combo_full_seed0.yaml"
    if [[ -f "$cf" ]]; then
        for key in "noise_dist: levy" "asym_drag_alpha:" "memory_kernel_lambda:" "inner_steps_per_price: 3"; do
            if ! grep -q "$key" "$cf"; then
                echo "  ✗ combo_full missing key '$key'" | tee -a "$MASTER_LOG"
                fail=1
            fi
        done
        echo "  ✓ combo_full schema verified (4 mechanisms wired)" | tee -a "$MASTER_LOG"
    fi

    # 4. Disk space (each H20 run writes ~80MB of result files).
    # df flag varies (BSD on Mac uses -g for GB blocks; GNU on Linux uses -BG).
    local free_gb
    if df -BG "$REPO_ROOT" >/dev/null 2>&1; then
        free_gb=$(df -BG "$REPO_ROOT" | awk 'NR==2 {gsub("G","",$4); print $4}')
    else
        # BSD df: 1024-blocks; convert to GB
        free_gb=$(df -k "$REPO_ROOT" | awk 'NR==2 {printf "%d", $4/1024/1024}')
    fi
    if [[ -n "$free_gb" && "$free_gb" -lt 50 ]]; then
        echo "  ✗ disk free $free_gb GB; need ≥ 50 GB for 270 results" | tee -a "$MASTER_LOG"
        fail=1
    else
        echo "  ✓ disk free ${free_gb} GB" | tee -a "$MASTER_LOG"
    fi

    # 5. No orphan torchrun (Branch D had stuck procs)
    local n_orphan=$(pgrep -f "torchrun.*ecomd" | wc -l | tr -d ' ')
    if [[ "$n_orphan" -gt 0 ]]; then
        echo "  ✗ found $n_orphan orphan torchrun processes; kill before launch" | tee -a "$MASTER_LOG"
        pgrep -f "torchrun.*ecomd" | tee -a "$MASTER_LOG"
        fail=1
    else
        echo "  ✓ no orphan torchrun" | tee -a "$MASTER_LOG"
    fi

    # 6. GPU presence + memory clean
    if command -v nvidia-smi >/dev/null 2>&1; then
        local n_gpu=$(nvidia-smi -L 2>/dev/null | wc -l | tr -d ' ')
        echo "  ✓ visible GPUs: $n_gpu" | tee -a "$MASTER_LOG"
    fi

    if [[ $fail -eq 1 ]]; then
        echo "── PREFLIGHT FAILED ──" | tee -a "$MASTER_LOG"
        return 1
    fi
    echo "── preflight OK ──" | tee -a "$MASTER_LOG"
    return 0
}

# ──────────────────────────────────────────────────────────────────────────
# Main runner
# ──────────────────────────────────────────────────────────────────────────

run_main() {
    echo "═══ BRANCH E — PAPER A V4 COMBO — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"

    if [[ "${1:-}" == "--dry-run" ]]; then
        echo "DRY RUN — listing configs only" | tee -a "$MASTER_LOG"
        local total=0 effective=0
        for d in "${GPU_DIRS[@]}"; do
            n=$(ls "$d"/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
            # Effective = configs without an existing inference_merged.json
            # (SKIP_DONE=1 will skip those during the actual run).
            local n_done=$(find "$d" -maxdepth 2 -name "inference_merged.json" 2>/dev/null | wc -l | tr -d ' ')
            local eff=$((n - n_done))
            total=$((total + n))
            effective=$((effective + eff))
            echo "  $d: $n configs ($n_done done, $eff effective)" | tee -a "$MASTER_LOG"
        done
        echo "  GPU total: $total configs (effective with SKIP_DONE: $effective)" | tee -a "$MASTER_LOG"
        local mins=$(( effective * 88 / 80 ))   # 8.8 min/cfg / 8 cards = 1.1 min/cfg avg
        echo "  Estimated H20 wall: ~$((mins / 60))h $((mins % 60))m ($effective cfgs × 8.8min / 8 cards)" | tee -a "$MASTER_LOG"
        preflight || echo "  (preflight noted issues; fix before non-dry-run launch)" | tee -a "$MASTER_LOG"
        return 0
    fi

    if ! preflight; then
        echo "ABORT — preflight failed. Fix issues above and re-run." | tee -a "$MASTER_LOG"
        return 1
    fi

    for d in "${GPU_DIRS[@]}"; do
        echo "" | tee -a "$MASTER_LOG"
        echo "═══ PHASE: $d ═══ $(date) ═══" | tee -a "$MASTER_LOG"
        SECONDS=0
        if ! bash scripts/h20_run_phase.sh "$d" 2>&1 | tee -a "$MASTER_LOG"; then
            echo "  [WARN] phase $d returned non-zero; continuing" | tee -a "$MASTER_LOG"
        fi
        echo "  [phase $d] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"

        # Per-phase scoreboard (so partial results visible during long runs)
        echo "  scoring $d ..." | tee -a "$MASTER_LOG"
        conda run -n ecophys python scripts/score_phase.py "$d" 2>&1 | tee -a "$MASTER_LOG" || \
            echo "  [WARN] scoreboard failed for $d" | tee -a "$MASTER_LOG"
    done

    # Continuous scoring across all dirs (z-distance, KS) — nice-to-have
    echo "" | tee -a "$MASTER_LOG"
    echo "═══ CONTINUOUS SCORING — $(date) ═══" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_continuous.py \
        "${GPU_DIRS[@]}" \
        --csv "experiments/_branch_e_continuous_${TIMESTAMP}.csv" \
        --target-dataset spx --target-period 2015-2026_daily \
        2>&1 | tee -a "$MASTER_LOG" || \
        echo "  [WARN] continuous scoring failed" | tee -a "$MASTER_LOG"

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ BRANCH E DONE — $(date) ═══" | tee -a "$MASTER_LOG"
}

if [[ "${1:-}" == "--dry-run" ]]; then
    run_main --dry-run
    exit 0
fi

if [[ "$DAEMON" == "1" ]]; then
    (run_main) >> "$MASTER_LOG" 2>&1 < /dev/null &
    pid=$!
    disown "$pid" 2>/dev/null || true
    echo "$pid" > "${MASTER_LOG}.pid"
    echo "started PID $pid; tail -f $MASTER_LOG"
else
    run_main
fi
