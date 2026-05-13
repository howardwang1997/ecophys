#!/usr/bin/env bash
# Paper A NeurIPS 2027 — main launcher (M2 batches: 089 → 090 → 091 → ...).
#
# This launcher drives the H20 batches that produce Paper A's empirical
# core. Today (2026-05-13) the only batch ready to run is 089 (clean
# leave-one-in mechanism-fact attribution). 090/091/etc. will be added
# as their generators land.
#
# 089 = 800 cfg, ~7h on 8-card H20.
#
# Why this batch
# ──────────────
# Branch F (088) showed that pair compositions plateau at mean=5.18/11
# and that two facts (autocorr_returns, zumbach_asymmetry) are
# architectural floors for v3 + V4 + B-round. The NeurIPS 2027 plan
# (~/.claude/plans/curried-cuddling-cloud.md) reframes Paper A as a
# falsification tool: gradient-based mechanism-space search across
# 10 mechanisms × 11 facts shows no Markovian latent-state composition
# clears 9/11.
#
# 089 produces the 10 × 11 matrix that becomes Figure 1 of the paper:
# every mechanism leave-one-in at a headline strength + 50-seed CIs +
# dose-response for the two new mechanisms (AR(1) whitening, Zumbach
# feedback) so we can see where their effective range is.
#
# 50 seeds is mandatory: Branch F showed n=30 inflated means by ~0.16.
#
# Usage on H20
# ────────────
#   ssh h20
#   cd ecophys
#   git fetch --all
#   git checkout feature/paper-a-neurips-2027
#   git pull
#   unset NPROC && bash scripts/h20_refresh_deps.sh
#   bash scripts/h20_paper_a_neurips_2027.sh --dry-run    # preflight + estimate
#   DAEMON=1 bash scripts/h20_paper_a_neurips_2027.sh
#   tail -f experiments/_paper_a_neurips_*.log

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

# Cell priority: run dose-response + new mechanisms first (highest paper
# value), then existing single-mechanism cells, then control. If the H20
# process dies past ~10h, the most-impactful results are already on disk.
export CONFIG_ORDER_PREFIXES="attr_baseline_,attr_ar1_,attr_zumbach_,attr_b3_,attr_asymdrag_,attr_levy_,attr_memk_,attr_powerlaw_,attr_microstructure_,attr_inner_,attr_jump_"

GPU_DIRS=(
    "experiments/089_attribution_50seed"
)

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_paper_a_neurips_${TIMESTAMP}.log"

# ──────────────────────────────────────────────────────────────────────────
# Pre-launch sanity checks
# ──────────────────────────────────────────────────────────────────────────

preflight() {
    local fail=0
    echo "── preflight checks ──" | tee -a "$MASTER_LOG"

    # 1. 089 has 800 configs total
    local n=$(ls experiments/089_attribution_50seed/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$n" != "800" ]]; then
        echo "  ✗ 089 expects 800 configs, found $n" | tee -a "$MASTER_LOG"
        fail=1
    else
        echo "  ✓ 089 has 800 configs" | tee -a "$MASTER_LOG"
    fi

    # 2. Each cell has 50 seeds
    for c in attr_baseline_v3 attr_levy_a17 attr_asymdrag_a06 attr_b3_k3 attr_ar1_s05 attr_zumbach_s10 attr_zumbach_dn_s10; do
        local n_c=$(ls experiments/089_attribution_50seed/config_${c}_seed*.yaml 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$n_c" != "50" ]]; then
            echo "  ✗ $c expects 50 seeds, found $n_c" | tee -a "$MASTER_LOG"
            fail=1
        else
            echo "  ✓ $c has 50 seeds" | tee -a "$MASTER_LOG"
        fi
    done

    # 3. Schema check: AR(1) cell carries new keys
    local ar1="experiments/089_attribution_50seed/config_attr_ar1_s05_seed0.yaml"
    if [[ -f "$ar1" ]]; then
        if grep -q "ar1_whiten_lambda: 0.9" "$ar1" \
           && grep -q "ar1_whiten_strength: 0.5" "$ar1"; then
            echo "  ✓ AR(1) cell has new mechanism keys" | tee -a "$MASTER_LOG"
        else
            echo "  ✗ AR(1) cell schema unexpected" | tee -a "$MASTER_LOG"
            fail=1
        fi
    fi

    # 4. Schema check: Zumbach downside variant carries mode key
    local zdn="experiments/089_attribution_50seed/config_attr_zumbach_dn_s10_seed0.yaml"
    if [[ -f "$zdn" ]]; then
        if grep -q "zumbach_feedback_mode: downside" "$zdn" \
           && grep -q "zumbach_feedback_strength: 1.0" "$zdn"; then
            echo "  ✓ Zumbach downside cell has new mechanism keys" | tee -a "$MASTER_LOG"
        else
            echo "  ✗ Zumbach downside cell schema unexpected" | tee -a "$MASTER_LOG"
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
        echo "  ✗ disk free $free_gb GB; need ≥ 50 GB for 800 results" | tee -a "$MASTER_LOG"
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

    # 8. New-mechanism unit tests pass (cheap; catches deps drift)
    local pytest_out
    pytest_out=$(conda run -n ecophys python -m pytest tests/test_ar1_whitening.py tests/test_zumbach_feedback.py -x 2>&1 | tail -3)
    echo "$pytest_out" | tee -a "$MASTER_LOG"
    if echo "$pytest_out" | grep -qE "[0-9]+ passed"; then
        echo "  ✓ new-mechanism unit tests pass" | tee -a "$MASTER_LOG"
    else
        echo "  ✗ new-mechanism unit tests failed" | tee -a "$MASTER_LOG"
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
# Main runner
# ──────────────────────────────────────────────────────────────────────────

run_main() {
    echo "═══ PAPER A NEURIPS 2027 — 089 ATTRIBUTION — $(date) ═══" | tee -a "$MASTER_LOG"
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
        conda run -n ecophys python scripts/score_summary.py "$d" \
            --title "089 attribution batch (Paper A NeurIPS 2027 M2.1)" 2>&1 | tee -a "$MASTER_LOG" || \
            echo "  [WARN] score_summary failed for $d" | tee -a "$MASTER_LOG"
    done

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ PAPER A NEURIPS 2027 — 089 DONE — $(date) ═══" | tee -a "$MASTER_LOG"
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
