#!/usr/bin/env bash
# Branch F (088) — Pair-mechanism sweep + high-seed confirmation + B3 tuning
#                  + BTC pairs.
#
# Single experiment dir, 460 cfgs ~8.4h on 8-card H20.
#
# Why this batch exists
# ─────────────────────
# Branch E showed 4-mechanism stacking is anti-additive: combo_full
# mean=4.62 < single-best asymdrag_a06 mean=5.10. Leave-one-out localised
# adiabatic as one bad component, but combo_no_inner (3 mech) at 4.74 is
# still below 5.10 — the interference is pairwise, not just adiabatic.
# 088 fills the gap by testing all 6 unordered pairs of 4 candidates
# (Lévy, asym, memk, B3 discrete regime) plus high-seed (n=50)
# confirmation of the two strongest single mechanisms.
#
# Cells (14 total, 460 configs):
#   conf_*    high-seed confirmation (50 seeds × 2 cells)
#   pair_*    SPX pair sweep (30 seeds × 6 cells)
#   b3_*      B3 hyperparam tuning (30 seeds × 3 cells)
#   btc_*     BTC pair tests (30 seeds × 2 cells)
#   triple_*  3-mech sanity replicate (30 seeds × 1 cell)
#
# Pre-launch verification
# ───────────────────────
# - 14 cells × correct seed counts (verified locally before launch)
# - pair_AB combines asym+B3 only (no Lévy, no memk, no inner)
# - btc_pair_AB has target_dataset:btcusdt + target_period:2024Q1_1m
# - conf_b3_k3_pure has only B3 active
# - Mac smoke: pair_AB n=256 200-step run finite, std=0.0069
#
# Usage (on H20):
#   ssh h20
#   cd ecophys
#   git fetch --all && git checkout feature/paper-a-v4-mechanisms && git pull
#   unset NPROC && bash scripts/h20_refresh_deps.sh
#   bash scripts/h20_branch_f_088.sh --dry-run    # preflight + estimate
#   DAEMON=1 bash scripts/h20_branch_f_088.sh
#   tail -f experiments/_branch_f_*.log

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

GPU_DIRS=(
    "experiments/088_pairs_and_confirmation"
)

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_branch_f_${TIMESTAMP}.log"

# ──────────────────────────────────────────────────────────────────────────
# Pre-launch sanity checks
# ──────────────────────────────────────────────────────────────────────────

preflight() {
    local fail=0
    echo "── preflight checks ──" | tee -a "$MASTER_LOG"

    # 1. 088 has 460 configs total
    local n=$(ls experiments/088_pairs_and_confirmation/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$n" != "460" ]]; then
        echo "  ✗ 088 expects 460 configs, found $n" | tee -a "$MASTER_LOG"
        fail=1
    else
        echo "  ✓ 088 has 460 configs" | tee -a "$MASTER_LOG"
    fi

    # 2. Confirmation cells have 50 seeds each
    for c in conf_asymdrag_a06 conf_b3_k3_pure; do
        local n_c=$(ls experiments/088_pairs_and_confirmation/config_${c}_seed*.yaml 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$n_c" != "50" ]]; then
            echo "  ✗ $c expects 50 seeds, found $n_c" | tee -a "$MASTER_LOG"
            fail=1
        else
            echo "  ✓ $c has 50 seeds" | tee -a "$MASTER_LOG"
        fi
    done

    # 3. pair_AB schema (asym + B3, neither Lévy nor memk nor inner_steps>1)
    local pab="experiments/088_pairs_and_confirmation/config_pair_AB_seed0.yaml"
    if [[ -f "$pab" ]]; then
        if grep -q "asym_drag_alpha: 0.6" "$pab" \
           && grep -q "regime_discrete_enabled: true" "$pab" \
           && grep -q "noise_dist: t" "$pab"; then
            echo "  ✓ pair_AB: asym + B3 only (Lévy disabled)" | tee -a "$MASTER_LOG"
        else
            echo "  ✗ pair_AB: schema unexpected" | tee -a "$MASTER_LOG"
            fail=1
        fi
    fi

    # 4. BTC pair has correct dataset key
    local btca="experiments/088_pairs_and_confirmation/config_btc_pair_AB_seed0.yaml"
    if [[ -f "$btca" ]]; then
        if grep -q "target_dataset: btcusdt" "$btca" && grep -q "target_period: 2024Q1_1m" "$btca"; then
            echo "  ✓ btc_pair_AB: BTC dataset key correct" | tee -a "$MASTER_LOG"
        else
            echo "  ✗ btc_pair_AB: dataset key wrong (would silently fall back to SPX)" | tee -a "$MASTER_LOG"
            fail=1
        fi
    fi

    # 5. Disk free
    local free_gb
    if df -BG "$REPO_ROOT" >/dev/null 2>&1; then
        free_gb=$(df -BG "$REPO_ROOT" | awk 'NR==2 {gsub("G","",$4); print $4}')
    else
        free_gb=$(df -k "$REPO_ROOT" | awk 'NR==2 {printf "%d", $4/1024/1024}')
    fi
    if [[ -n "$free_gb" && "$free_gb" -lt 50 ]]; then
        echo "  ✗ disk free $free_gb GB; need ≥ 50 GB for 460 results" | tee -a "$MASTER_LOG"
        fail=1
    else
        echo "  ✓ disk free ${free_gb} GB" | tee -a "$MASTER_LOG"
    fi

    # 6. No orphan torchrun (Branch D had stuck procs)
    local n_orphan=$(pgrep -f "torchrun.*ecomd" 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$n_orphan" -gt 0 ]]; then
        echo "  ✗ found $n_orphan orphan torchrun processes; kill before launch" | tee -a "$MASTER_LOG"
        pgrep -f "torchrun.*ecomd" | tee -a "$MASTER_LOG"
        fail=1
    else
        echo "  ✓ no orphan torchrun" | tee -a "$MASTER_LOG"
    fi

    # 7. GPU presence
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
    echo "═══ BRANCH F (088) — PAIRS + CONFIRMATION — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"

    if [[ "${1:-}" == "--dry-run" ]]; then
        echo "DRY RUN — listing configs only" | tee -a "$MASTER_LOG"
        local total=0 effective=0
        for d in "${GPU_DIRS[@]}"; do
            local n=$(ls "$d"/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
            local n_done=$(find "$d" -maxdepth 2 -name "inference_merged.json" 2>/dev/null | wc -l | tr -d ' ')
            local eff=$((n - n_done))
            total=$((total + n))
            effective=$((effective + eff))
            echo "  $d: $n configs ($n_done done, $eff effective)" | tee -a "$MASTER_LOG"
        done
        echo "  GPU total: $total configs (effective with SKIP_DONE: $effective)" | tee -a "$MASTER_LOG"
        local mins=$(( effective * 88 / 80 ))
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
        if ! DAEMON=0 bash scripts/h20_run_phase.sh "$d" 2>&1 | tee -a "$MASTER_LOG"; then
            echo "  [WARN] phase $d returned non-zero; continuing" | tee -a "$MASTER_LOG"
        fi
        echo "  [phase $d] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"

        echo "  scoring $d ..." | tee -a "$MASTER_LOG"
        conda run -n ecophys python scripts/score_phase.py "$d" 2>&1 | tee -a "$MASTER_LOG" || \
            echo "  [WARN] scoreboard failed for $d" | tee -a "$MASTER_LOG"
    done

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ CONTINUOUS SCORING — $(date) ═══" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_continuous.py \
        "${GPU_DIRS[@]}" \
        --csv "experiments/_branch_f_continuous_${TIMESTAMP}.csv" \
        --target-dataset spx --target-period 2015-2026_daily \
        2>&1 | tee -a "$MASTER_LOG" || \
        echo "  [WARN] continuous scoring failed" | tee -a "$MASTER_LOG"

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ BRANCH F DONE — $(date) ═══" | tee -a "$MASTER_LOG"
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
