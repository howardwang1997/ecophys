#!/usr/bin/env bash
# Overnight H20 batch — 2026-05-20
#
# Two sub-batches, sequenced on the same 8-card H20:
#   099b_memk_refinement_n30  — 270 cfg, ~5-6h  (paper §4 memk dose-response)
#   095b_baselines_n30        — 250 cfg, ~3-4h  (paper §5 baseline table C3b)
#
# Total estimated wall: 8-10h. Launch ~21:00 local, finishes ~07:00 next day.
# Score + sync after each sub-batch so partial progress is salvageable.
#
# Why this batch exists
# ─────────────────────
# Day-shift Mac rescore + 098b zumdn n=30 will land mid-afternoon today.
# Two open questions remain for Paper A §4-§5 to be confidently drafted:
#
# 1. Does memk have an operating point we missed? 099 (n=5) had four cells
#    tied at mean 5.80 — pure seed-count lottery, can't cite. 099b at n=30
#    settles it: either reveals a real hidden operating point (paper § risk-
#    register R2 fallback activated) or properly disqualifies memk as a
#    constructive mechanism for §4 final.
#
# 2. Is C3b "ECoMD ≥ modern surrogates" statistically firm? 095 had n=5,
#    max ≤ 6 on every cell vs ECoMD's 9. 095b adds seeds 5-29 so every cell
#    is n=30, putting the baseline-table claim above lottery threshold.
#
# Usage (on H20, after day-shift batch 098b finishes):
#   ssh h20
#   cd ecophys
#   git fetch --all && git pull origin feature/paper-a-neurips-2027
#   bash scripts/h20_overnight_2026-05-20.sh --dry-run    # preflight
#   DAEMON=1 bash scripts/h20_overnight_2026-05-20.sh
#   tail -f experiments/_overnight_2026-05-20_*.log
#
# Post-run (auto-runs at end of each sub-batch):
#   conda run -n ecophys python -m ecomd.data.checkpoint_sync sync --delete-local
#   conda run -n ecophys python scripts/score_phase.py + score_summary.py
#   git add experiments/099b_*/scoreboard.md experiments/095b_*/scoreboard.md
#   git commit + push to origin

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

GPU_DIRS=(
    "experiments/099b_memk_refinement_n30"
    "experiments/095b_baselines_n30"
)

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_overnight_2026-05-20_${TIMESTAMP}.log"

preflight() {
    local fail=0
    echo "── preflight checks ──" | tee -a "$MASTER_LOG"

    local n_099b=$(ls experiments/099b_memk_refinement_n30/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$n_099b" != "270" ]]; then
        echo "  ✗ 099b expects 270 configs, found $n_099b" | tee -a "$MASTER_LOG"
        fail=1
    else
        echo "  ✓ 099b has 270 configs" | tee -a "$MASTER_LOG"
    fi

    local n_095b=$(ls experiments/095b_baselines_n30/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$n_095b" != "250" ]]; then
        echo "  ✗ 095b expects 250 configs, found $n_095b" | tee -a "$MASTER_LOG"
        fail=1
    else
        echo "  ✓ 095b has 250 configs" | tee -a "$MASTER_LOG"
    fi

    local m1="experiments/099b_memk_refinement_n30/config_memk_s075_lam095_seed0.yaml"
    if [[ -f "$m1" ]]; then
        if grep -q "memory_kernel_lambda: 0.95" "$m1" && grep -q "memory_kernel_strength: 0.75" "$m1"; then
            echo "  ✓ memk_s075_lam095: (s, λ) = (0.75, 0.95)" | tee -a "$MASTER_LOG"
        else
            echo "  ✗ memk_s075_lam095: schema unexpected" | tee -a "$MASTER_LOG"
            fail=1
        fi
    fi

    local b1="experiments/099b_memk_refinement_n30/config_baseline_v3_seed0.yaml"
    if [[ -f "$b1" ]]; then
        if grep -q "memory_kernel" "$b1"; then
            echo "  ✗ baseline_v3: should NOT have memk keys" | tee -a "$MASTER_LOG"
            fail=1
        else
            echo "  ✓ baseline_v3: memk disabled" | tee -a "$MASTER_LOG"
        fi
    fi

    local w1="experiments/095b_baselines_n30/config_baseline_wgan_eurusd_seed5.yaml"
    if [[ -f "$w1" ]]; then
        if grep -q "model: wgan_lp" "$w1" && grep -q "asset: eurusd" "$w1"; then
            echo "  ✓ baseline_wgan_eurusd_seed5: (model, asset) = (wgan_lp, eurusd)" | tee -a "$MASTER_LOG"
        else
            echo "  ✗ baseline_wgan_eurusd_seed5: schema unexpected" | tee -a "$MASTER_LOG"
            fail=1
        fi
    fi

    local free_gb
    if df -BG "$REPO_ROOT" >/dev/null 2>&1; then
        free_gb=$(df -BG "$REPO_ROOT" | awk 'NR==2 {gsub("G","",$4); print $4}')
    else
        free_gb=$(df -k "$REPO_ROOT" | awk 'NR==2 {printf "%d", $4/1024/1024}')
    fi
    if [[ -n "$free_gb" && "$free_gb" -lt 60 ]]; then
        echo "  ✗ disk free $free_gb GB; need ≥ 60 GB for 520 results" | tee -a "$MASTER_LOG"
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

run_phase() {
    local d="$1"
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
    conda run -n ecophys python scripts/score_summary.py "$d" 2>&1 | tee -a "$MASTER_LOG" || \
        echo "  [WARN] score_summary failed for $d" | tee -a "$MASTER_LOG"

    echo "  R2 sync ..." | tee -a "$MASTER_LOG"
    conda run -n ecophys python -m ecomd.data.checkpoint_sync --root "$d" sync --delete-local 2>&1 | tee -a "$MASTER_LOG" || \
        echo "  [WARN] checkpoint_sync returned non-zero (Supabase key missing on H20; R2 upload should still ok)" | tee -a "$MASTER_LOG"
}

run_main() {
    echo "═══ OVERNIGHT 2026-05-20 — 099b + 095b — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"

    if [[ "${1:-}" == "--dry-run" ]]; then
        echo "DRY RUN — listing configs only" | tee -a "$MASTER_LOG"
        local grand_total=0 grand_effective=0
        for d in "${GPU_DIRS[@]}"; do
            local n=$(ls "$d"/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
            local n_done=$(find "$d" -maxdepth 2 -name "inference_merged.json" 2>/dev/null | wc -l | tr -d ' ')
            local eff=$((n - n_done))
            grand_total=$((grand_total + n))
            grand_effective=$((grand_effective + eff))
            echo "  $d: $n configs ($n_done done, $eff effective)" | tee -a "$MASTER_LOG"
        done
        echo "  GPU grand total: $grand_total configs (effective with SKIP_DONE: $grand_effective)" | tee -a "$MASTER_LOG"
        local mins=$(( grand_effective * 88 / 80 ))
        echo "  Estimated H20 wall: ~$((mins / 60))h $((mins % 60))m" | tee -a "$MASTER_LOG"
        preflight || echo "  (preflight noted issues; fix before non-dry-run launch)" | tee -a "$MASTER_LOG"
        return 0
    fi

    if ! preflight; then
        echo "ABORT — preflight failed. Fix issues above and re-run." | tee -a "$MASTER_LOG"
        return 1
    fi

    for d in "${GPU_DIRS[@]}"; do
        run_phase "$d"
    done

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ OVERNIGHT DONE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  Mac next step: pull + rescore + run scripts/reconcile_r2_to_supabase.py" | tee -a "$MASTER_LOG"
}

if [[ "${1:-}" == "--dry-run" ]]; then
    run_main --dry-run
    exit 0
fi

if [[ "$DAEMON" == "1" ]]; then
    (run_main) >> "$MASTER_LOG" 2>&1 < /dev/null &
    echo "Started overnight batch in background (PID $!) — log: $MASTER_LOG"
    echo "  tail -f $MASTER_LOG"
else
    run_main
fi
