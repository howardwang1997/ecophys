#!/usr/bin/env bash
# Paper A NeurIPS 2027 — weekend batch launcher (2026-05-15 PM → 2026-05-17 PM).
#
# Sequences five sub-batches based on 089 attribution findings:
#   090   patch composition (top priority, ~3.5h)         240 cfg ECoMD
#   090b  AR(1) stability grid (fix the 70% rej)          120 cfg ECoMD
#   094   VaR holdout training (clean train-test split)    96 cfg ECoMD
#   091   calibration speed shootout (ECoMD leg only)      30 cfg ECoMD
#   095   WGAN-LP + TrajCast-lite baselines (5 assets)     50 cfg baselines
#
# Total: 486 ECoMD cfg + 50 baseline fits ≈ 17h on 8-card H20.
#
# Why these five in this order
# ────────────────────────────
# 089 (LANDED 2026-05-15) identified `attr_zumbach_dn_s10` as the safest
# patch seed (mean 5.12, no fact dropped ≥-13pp) and showed both
# architectural floors are LIFT-able by single mechanisms but with
# Pareto-frontier tradeoffs (acceptance probability story reframes from
# "absolute floor" to "compositional impossibility").
#
# 090 chases the first mean ≥ 5.5 hero cell by composing the safe Zumbach
# patch with existing best singles + the two new mechs together.
# 090b parameter-envelope-searches AR(1) low-strength (089 found
# s03 lifts autocorr +62pp but 35/50 seeds blow up).
# 094 lays a clean train-test split for M1.4 paper-quality VaR.
# 091 records ECoMD calibration wall-clock × coverage (headline downstream).
# 095 trains WGAN-LP + TrajCast-lite on 5 assets for the §5 baseline table.
#
# Usage on H20
# ────────────
#   ssh h20
#   cd ecophys
#   git fetch --all
#   git checkout feature/paper-a-neurips-2027
#   git pull
#   unset NPROC && bash scripts/h20_refresh_deps.sh
#   bash scripts/h20_weekend_2026-05-15.sh --dry-run    # preflight + wall estimate
#   DAEMON=1 bash scripts/h20_weekend_2026-05-15.sh
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

# Per-phase priority ordering. Bash 3.2 compat: function lookup rather than
# associative array (H20 environments still ship 3.2; declare -A + set -u
# combo fails there).
phase_order_for() {
    case "$1" in
        experiments/090_patch_composition_30seed)
            echo "pair_zumdn_,pair_ar1_,triple_,pair_AB_,zumdn_solo_" ;;
        experiments/090b_ar1_stability_grid)
            echo "ar1_s025_,ar1_s03_clip,ar1_s05_clip,ar1_s02_" ;;
        experiments/094_var_holdout_12seed)
            echo "var_baseline_,var_zumdn_,var_b3_,var_asymdrag_,var_ar1_,var_powerlaw_,var_pair_" ;;
        experiments/091_calibration_ecomd_5asset)
            echo "calib_spx_b40_,calib_spx_b80_,calib_spx_b160_,calib_btcusdt_,calib_eurusd_,calib_gold_,calib_ndx_" ;;
        experiments/095_baseline_5asset_5seed)
            echo "baseline_wgan_spx,baseline_trajcast_spx,baseline_wgan_,baseline_trajcast_" ;;
        *) echo "" ;;
    esac
}

# (phase_dir, runner, expected_n, schema_key_check_file, schema_key_check_pattern)
# schema_key_check_pattern is a substring expected in the named cfg file
ECOMD_PHASES=(
    "experiments/090_patch_composition_30seed:240:experiments/090_patch_composition_30seed/config_pair_zumdn_b3_seed0.yaml:zumbach_feedback_mode: downside"
    "experiments/090b_ar1_stability_grid:120:experiments/090b_ar1_stability_grid/config_ar1_s03_clip_seed0.yaml:ar1_whiten_clip: 1.0"
    "experiments/094_var_holdout_12seed:96:experiments/094_var_holdout_12seed/config_var_baseline_v3_seed0.yaml:target_period: 2010-2017_daily"
    "experiments/091_calibration_ecomd_5asset:30:experiments/091_calibration_ecomd_5asset/config_calib_spx_b40_seed0.yaml:n_iters: 40"
)
BASELINE_PHASES=(
    "experiments/095_baseline_5asset_5seed:50:experiments/095_baseline_5asset_5seed/config_baseline_wgan_spx_seed0.yaml:model: wgan_lp"
)

# ──────────────────────────────────────────────────────────────────────────
# Pre-launch sanity checks
# ──────────────────────────────────────────────────────────────────────────

preflight() {
    local fail=0
    echo "── preflight checks ──" | tee -a "$MASTER_LOG"

    # 1. Each phase has expected number of configs
    for p in "${ECOMD_PHASES[@]}" "${BASELINE_PHASES[@]}"; do
        local dir=$(echo "$p" | cut -d: -f1)
        local expected=$(echo "$p" | cut -d: -f2)
        local cfgkey=$(echo "$p" | cut -d: -f3)
        local kpattern=$(echo "$p" | cut -d: -f4-)
        local n=$(ls "$dir"/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$n" != "$expected" ]]; then
            echo "  ✗ $dir expects $expected configs, found $n" | tee -a "$MASTER_LOG"
            fail=1
        else
            echo "  ✓ $dir has $n configs" | tee -a "$MASTER_LOG"
        fi
        # Schema check
        if [[ -f "$cfgkey" ]] && grep -q "$kpattern" "$cfgkey"; then
            echo "  ✓ $(basename "$dir") schema sane ('$kpattern')" | tee -a "$MASTER_LOG"
        elif [[ -f "$cfgkey" ]]; then
            echo "  ✗ $(basename "$dir") schema missing '$kpattern' in $(basename "$cfgkey")" | tee -a "$MASTER_LOG"
            fail=1
        fi
    done

    # 2. Disk free ≥ 80 GB (5 phases worth of results)
    local free_gb
    if df -BG "$REPO_ROOT" >/dev/null 2>&1; then
        free_gb=$(df -BG "$REPO_ROOT" | awk 'NR==2 {gsub("G","",$4); print $4}')
    else
        free_gb=$(df -k "$REPO_ROOT" | awk 'NR==2 {printf "%d", $4/1024/1024}')
    fi
    if [[ -n "$free_gb" && "$free_gb" -lt 80 ]]; then
        echo "  ✗ disk free $free_gb GB; need ≥ 80 GB for weekend batch" | tee -a "$MASTER_LOG"
        fail=1
    else
        echo "  ✓ disk free ${free_gb} GB" | tee -a "$MASTER_LOG"
    fi

    # 3. No orphan torchrun
    local n_orphan=$(pgrep -f "torchrun.*ecomd" 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$n_orphan" -gt 0 ]]; then
        echo "  ✗ found $n_orphan orphan torchrun processes; kill before launch" | tee -a "$MASTER_LOG"
        pgrep -f "torchrun.*ecomd" | tee -a "$MASTER_LOG"
        fail=1
    else
        echo "  ✓ no orphan torchrun" | tee -a "$MASTER_LOG"
    fi

    # 4. GPU presence
    if command -v nvidia-smi >/dev/null 2>&1; then
        local n_gpu=$(nvidia-smi -L 2>/dev/null | wc -l | tr -d ' ')
        echo "  ✓ visible GPUs: $n_gpu" | tee -a "$MASTER_LOG"
    fi

    # 5. Unit tests — all relevant
    local pytest_out
    pytest_out=$(conda run -n ecophys python -m pytest \
        tests/test_ar1_whitening.py tests/test_zumbach_feedback.py \
        tests/test_var_backtest.py tests/test_distributional_metrics.py \
        -x 2>&1 | tail -3)
    echo "$pytest_out" | tee -a "$MASTER_LOG"
    if echo "$pytest_out" | grep -qE "[0-9]+ passed"; then
        echo "  ✓ unit tests pass" | tee -a "$MASTER_LOG"
    else
        echo "  ✗ unit tests failed" | tee -a "$MASTER_LOG"
        fail=1
    fi

    # 6. Baseline runner imports cleanly
    if conda run -n ecophys python -c "
import sys; sys.path.insert(0, '.')
from ecomd.baselines.wgan_lp import WGANLPSimulator
from ecomd.baselines.trajcast_lite import TrajCastLiteSimulator
from ecomd.calibration.wallclock_harness import analyze_calibration_dir
" >/dev/null 2>&1; then
        echo "  ✓ M1.5/M1.6 imports OK" | tee -a "$MASTER_LOG"
    else
        echo "  ✗ M1.5/M1.6 imports FAILED" | tee -a "$MASTER_LOG"
        fail=1
    fi

    if [[ $fail -eq 1 ]]; then
        echo "── PREFLIGHT FAILED ──" | tee -a "$MASTER_LOG"
        return 1
    fi
    echo "── preflight OK ──" | tee -a "$MASTER_LOG"
    return 0
}

# ──────────────────────────────────────────────────────────────────────────
# Phase runners
# ──────────────────────────────────────────────────────────────────────────

run_ecomd_phase() {
    local d="$1"
    echo "" | tee -a "$MASTER_LOG"
    echo "═══ ECoMD PHASE: $d ═══ $(date) ═══" | tee -a "$MASTER_LOG"
    export CONFIG_ORDER_PREFIXES="$(phase_order_for "$d")"
    SECONDS=0
    if ! DAEMON=0 bash scripts/h20_run_phase.sh "$d" 2>&1 | tee -a "$MASTER_LOG"; then
        echo "  [WARN] phase $d returned non-zero; continuing" | tee -a "$MASTER_LOG"
    fi
    echo "  [phase $d] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_phase.py "$d" 2>&1 | tee -a "$MASTER_LOG" || \
        echo "  [WARN] scoreboard failed for $d" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_summary.py "$d" \
        --title "$(basename "$d")" 2>&1 | tee -a "$MASTER_LOG" || \
        echo "  [WARN] score_summary failed for $d" | tee -a "$MASTER_LOG"
}

run_baseline_phase() {
    local d="$1"
    echo "" | tee -a "$MASTER_LOG"
    echo "═══ BASELINE PHASE: $d ═══ $(date) ═══" | tee -a "$MASTER_LOG"
    export CONFIG_ORDER_PREFIXES="$(phase_order_for "$d")"
    SECONDS=0
    if ! bash scripts/h20_run_baseline_phase.sh "$d" 2>&1 | tee -a "$MASTER_LOG"; then
        echo "  [WARN] baseline phase $d returned non-zero; continuing" | tee -a "$MASTER_LOG"
    fi
    echo "  [baseline phase $d] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_phase.py "$d" 2>&1 | tee -a "$MASTER_LOG" || \
        echo "  [WARN] scoreboard failed for $d" | tee -a "$MASTER_LOG"
    conda run -n ecophys python scripts/score_summary.py "$d" \
        --title "$(basename "$d")" 2>&1 | tee -a "$MASTER_LOG" || \
        echo "  [WARN] score_summary failed for $d" | tee -a "$MASTER_LOG"
}

# ──────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────

run_main() {
    echo "═══ PAPER A NEURIPS 2027 — WEEKEND BATCH — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"

    if [[ "${1:-}" == "--dry-run" ]]; then
        echo "DRY RUN — listing configs only" | tee -a "$MASTER_LOG"
        local total=0 effective=0
        for p in "${ECOMD_PHASES[@]}" "${BASELINE_PHASES[@]}"; do
            local d=$(echo "$p" | cut -d: -f1)
            local n=$(ls "$d"/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
            local n_done=$(find "$d" -maxdepth 2 -name "inference_merged.json" 2>/dev/null | wc -l | tr -d ' ')
            local eff=$((n - n_done))
            total=$((total + n))
            effective=$((effective + eff))
            echo "  $d: $n cfgs ($n_done done, $eff effective)" | tee -a "$MASTER_LOG"
        done
        echo "  GRAND TOTAL: $total cfgs (effective with SKIP_DONE: $effective)" | tee -a "$MASTER_LOG"
        # Estimate: ECoMD ~8.8min/cfg, baselines ~10min/cfg, both at 8-way parallel
        local mins=$(( effective * 88 / 80 ))
        echo "  Estimated H20 wall: ~$((mins / 60))h $((mins % 60))m" | tee -a "$MASTER_LOG"
        preflight || echo "  (preflight noted issues; fix before non-dry-run launch)" | tee -a "$MASTER_LOG"
        return 0
    fi

    if ! preflight; then
        echo "ABORT — preflight failed. Fix issues above and re-run." | tee -a "$MASTER_LOG"
        return 1
    fi

    # ECoMD phases first (uses torchrun + train_distributed)
    for p in "${ECOMD_PHASES[@]}"; do
        local d=$(echo "$p" | cut -d: -f1)
        run_ecomd_phase "$d"
    done

    # Baseline phases (uses run_baseline_fit_eval.py directly, no torchrun)
    for p in "${BASELINE_PHASES[@]}"; do
        local d=$(echo "$p" | cut -d: -f1)
        run_baseline_phase "$d"
    done

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ WEEKEND BATCH DONE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  scoreboards: experiments/{090,090b,094,091,095}_*/scoreboard.md" | tee -a "$MASTER_LOG"
    echo "  Mac-side analysis:" | tee -a "$MASTER_LOG"
    echo "    python scripts/score_attribution.py experiments/090_patch_composition_30seed" | tee -a "$MASTER_LOG"
    echo "    python -m ecomd.calibration.wallclock_harness --report experiments/091_calibration_ecomd_5asset" | tee -a "$MASTER_LOG"
    echo "    python -m ecomd.risk.var_backtest --asset spx --period 2018-2026 --checkpoint <var_*>/checkpoint.pt" | tee -a "$MASTER_LOG"
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
