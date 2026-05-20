#!/usr/bin/env bash
# 098b — Zumbach `dn` day-shift refinement at n=30
#
# Trim of the 098 (s, λ) grid to 8 paper-critical cells × 30 seeds = 240 cfg.
# Estimated wall: ~2.5-3h on 8-card H20.
#
# Why this batch exists
# ─────────────────────
# 098 was the original (5 strengths × 4 λ) refinement at n=5. Many cells
# had rejections (n=3 effective), so dose-response surface is too noisy to
# cite. The headline 098 result `zumdn_s075_lam095=6.67 at n=3` is exactly
# the "seed-count lottery" pattern we have a memory entry for.
#
# 098b takes 8 best-bet cells from 098 + a `baseline_v3` reference and
# runs each at n=30 to (a) confirm or supersede the noisy 098 SOTA, and
# (b) firm up the Pareto-attribution Figure 1 caption with a clean
# zumdn dose-response panel.
#
# Cells (8 × 30 = 240 cfg, with `baseline_v3` first for delta calc):
#   baseline_v3           reference (no zumbach feedback)
#   zumdn_s100_lam095     089 production reference (mean 5.12 at n=48)
#   zumdn_s075_lam095     CURRENT 098 NOISY TOP (mean 6.67 at n=3) — confirm or kill
#   zumdn_s050_lam099     098 mean 5.20 at n=5
#   zumdn_s075_lam099     (s075) lam neighbour
#   zumdn_s100_lam099     098 mean 5.00 at n=5
#   zumdn_s150_lam095     098 mean 5.00 at n=5
#   zumdn_s100_lam090     098 mean 5.20 at n=5
#
# Usage (on H20):
#   ssh h20
#   cd ecophys
#   git fetch --all && git checkout feature/paper-a-neurips-2027 && git pull
#   bash scripts/h20_pull_from_r2.sh
#   bash scripts/h20_098b_dayshift.sh --dry-run    # preflight + estimate
#   DAEMON=1 bash scripts/h20_098b_dayshift.sh
#   tail -f experiments/_098b_*.log
#
# Post-run on H20:
#   conda run -n ecophys python -m ecomd.data.checkpoint_sync sync --delete-local
#     # uploads checkpoints to R2; Supabase upsert will skip because key missing
#     # Mac runs scripts/reconcile_r2_to_supabase.py to catch up Supabase
#   conda run -n ecophys python scripts/score_phase.py experiments/098b_zumdn_dayshift_n30
#   conda run -n ecophys python scripts/score_summary.py experiments/098b_zumdn_dayshift_n30 \
#       --title "098b zumdn day-shift n=30"
#   git add experiments/098b_zumdn_dayshift_n30/scoreboard.md scripts/h20_098b_dayshift.sh
#   git commit -m "098b: zumdn day-shift n=30 results (8 cells × 30 seeds)"
#   git push origin feature/paper-a-neurips-2027

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

# Baseline first so delta calc has its reference. Then 089 production
# reference (s100_lam095) — if H20 dies past ~1h, the most-citable cells
# are already on disk. Then noisy 098 top to confirm. Then rest.
export CONFIG_ORDER_PREFIXES="baseline_v3_,zumdn_s100_lam095_,zumdn_s075_lam095_,zumdn_s050_lam099_,zumdn_s100_lam099_,zumdn_s075_lam099_,zumdn_s150_lam095_,zumdn_s100_lam090_"

GPU_DIRS=(
    "experiments/098b_zumdn_dayshift_n30"
)

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_098b_${TIMESTAMP}.log"

preflight() {
    local fail=0
    echo "── preflight checks ──" | tee -a "$MASTER_LOG"

    local n=$(ls experiments/098b_zumdn_dayshift_n30/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$n" != "240" ]]; then
        echo "  ✗ 098b expects 240 configs, found $n" | tee -a "$MASTER_LOG"
        fail=1
    else
        echo "  ✓ 098b has 240 configs" | tee -a "$MASTER_LOG"
    fi

    for c in baseline_v3 zumdn_s100_lam095 zumdn_s075_lam095 zumdn_s050_lam099 \
             zumdn_s075_lam099 zumdn_s100_lam099 zumdn_s150_lam095 zumdn_s100_lam090; do
        local n_c=$(ls experiments/098b_zumdn_dayshift_n30/config_${c}_seed*.yaml 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$n_c" != "30" ]]; then
            echo "  ✗ cell $c expects 30 seeds, found $n_c" | tee -a "$MASTER_LOG"
            fail=1
        else
            echo "  ✓ cell $c has 30 seeds" | tee -a "$MASTER_LOG"
        fi
    done

    local s075="experiments/098b_zumdn_dayshift_n30/config_zumdn_s075_lam095_seed0.yaml"
    if [[ -f "$s075" ]]; then
        if grep -q "zumbach_feedback_strength: 0.75" "$s075" \
           && grep -q "zumbach_feedback_lambda: 0.95" "$s075" \
           && grep -q "zumbach_feedback_mode: downside" "$s075"; then
            echo "  ✓ zumdn_s075_lam095: (s, λ, mode) = (0.75, 0.95, downside)" | tee -a "$MASTER_LOG"
        else
            echo "  ✗ zumdn_s075_lam095: schema unexpected" | tee -a "$MASTER_LOG"
            fail=1
        fi
    fi

    local base="experiments/098b_zumdn_dayshift_n30/config_baseline_v3_seed0.yaml"
    if [[ -f "$base" ]]; then
        if grep -q "zumbach" "$base"; then
            echo "  ✗ baseline_v3: should NOT have zumbach keys" | tee -a "$MASTER_LOG"
            fail=1
        else
            echo "  ✓ baseline_v3: zumbach disabled (no keys)" | tee -a "$MASTER_LOG"
        fi
    fi

    local free_gb
    if df -BG "$REPO_ROOT" >/dev/null 2>&1; then
        free_gb=$(df -BG "$REPO_ROOT" | awk 'NR==2 {gsub("G","",$4); print $4}')
    else
        free_gb=$(df -k "$REPO_ROOT" | awk 'NR==2 {printf "%d", $4/1024/1024}')
    fi
    if [[ -n "$free_gb" && "$free_gb" -lt 30 ]]; then
        echo "  ✗ disk free $free_gb GB; need ≥ 30 GB for 240 results" | tee -a "$MASTER_LOG"
        fail=1
    else
        echo "  ✓ disk free ${free_gb} GB" | tee -a "$MASTER_LOG"
    fi

    local n_orphan=$(pgrep -f "torchrun.*ecomd" 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$n_orphan" -gt 0 ]]; then
        echo "  ✗ found $n_orphan orphan torchrun processes; kill before launch" | tee -a "$MASTER_LOG"
        pgrep -f "torchrun.*ecomd" | tee -a "$MASTER_LOG"
        fail=1
    else
        echo "  ✓ no orphan torchrun" | tee -a "$MASTER_LOG"
    fi

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

run_main() {
    echo "═══ 098b — ZUMDN DAY-SHIFT n=30 — $(date) ═══" | tee -a "$MASTER_LOG"
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
            echo "  [WARN] score_phase failed for $d" | tee -a "$MASTER_LOG"
        conda run -n ecophys python scripts/score_summary.py "$d" \
            --title "098b zumdn day-shift n=30" 2>&1 | tee -a "$MASTER_LOG" || \
            echo "  [WARN] score_summary failed for $d" | tee -a "$MASTER_LOG"
    done

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ CHECKPOINT OFFLOAD (R2 sync, Supabase will skip without key) — $(date) ═══" | tee -a "$MASTER_LOG"
    conda run -n ecophys python -m ecomd.data.checkpoint_sync sync --delete-local 2>&1 | tee -a "$MASTER_LOG" || \
        echo "  [WARN] checkpoint_sync returned non-zero (likely Supabase key missing; R2 upload still ok)" | tee -a "$MASTER_LOG"

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ 098b DONE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  Next step (Mac): scripts/reconcile_r2_to_supabase.py to backfill Supabase catalog" | tee -a "$MASTER_LOG"
}

if [[ "${1:-}" == "--dry-run" ]]; then
    run_main --dry-run
    exit 0
fi

if [[ "$DAEMON" == "1" ]]; then
    (run_main) >> "$MASTER_LOG" 2>&1 < /dev/null &
    echo "Started 098b day-shift in background (PID $!) — log: $MASTER_LOG"
    echo "  tail -f $MASTER_LOG"
else
    run_main
fi
