#!/usr/bin/env bash
# Weekend 2026-05-22 → 2026-05-26 H20 queue.
#
# Six-phase queue (total ~74h wall-clock on 8-card H20 with PARALLEL=8;
# 96h calendar budget so ~22h buffer for restart / Mac analysis):
#
#   1. 099B  memk refinement       270 cfg  ~5.6h  Track A 决战门
#   2. 098C  zumdn fine-grid       180 cfg  ~3.7h  §4 figure surface
#   3. 095B  WGAN+TrajCast n=30    250 cfg  ~5.2h  §4 baselines
#   4. 098D  Asset×Mode 2×3        180 cfg  ~3.7h  §3 "098B regression diagnose"
#   5. B-β   scheduled-sampling    930 cfg  ~19.4h §5 "solve" pilot (B-β)
#   6. B-α   Hopfield (conditional) ~900 cfg ~18.75h §5 "solve" pilot (B-α)
#
# Order rationale: must-runs and diagnostics FIRST (#1-#4), exploratory
# pilots LAST. If H20 dies past hour 18, the four critical batches are
# already on disk and the Paper A §3+§4+memk-decision-gate are intact.
# Only the "solve" pilots (#5, #6) would need restart.
#
# Phase #6 (B-α) is **conditional**: only fires if the directory
# experiments/track_b_alpha_pilot_n30/ exists. B-α implementation has a
# fail-safe (see plans/ok-pull-099b-095b-lazy-feigenbaum.md §4): if the
# Mac-side implementation doesn't land by Sun 22:00 local, the directory
# won't be populated and this script auto-skips that phase.
#
# Usage on H20:
#   ssh h20
#   cd ecophys
#   git fetch --all && git checkout feature/paper-a-neurips-2027 && git pull
#   bash scripts/h20_pull_from_r2.sh
#   bash scripts/h20_weekend_2026-05-22.sh --dry-run    # preflight + estimate
#   DAEMON=1 bash scripts/h20_weekend_2026-05-22.sh
#   tail -f experiments/_weekend_*.log
#
# Post-run on H20: aggregate, R2-sync, Mac-side analysis.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAEMON="${DAEMON:-0}"
export SKIP_DONE="${SKIP_DONE:-1}"
export PARALLEL="${PARALLEL:-8}"
export NPROC="${NPROC:-1}"

# Phase order — must-runs and diagnostics first, exploratory pilots last.
# B-α pilot is conditional on the dir existing (created by task #9 only
# after the implementation + smoke pass; see plan §4 fail-safe).
PHASES=(
    "experiments/099b_memk_refinement_n30"
    "experiments/098c_zumdn_fine_grid_n30"
    "experiments/095b_baselines_n30"
    "experiments/098d_asset_mode_n30"
    "experiments/track_b_beta_pilot_n30"
    "experiments/track_b_alpha_pilot_n30"   # ← conditional
)

# Expected config counts and summary titles per phase. Using case statements
# instead of associative arrays for portability (Mac default bash is 3.x).
expected_n() {
    case "$1" in
        experiments/099b_memk_refinement_n30)    echo 270 ;;
        experiments/098c_zumdn_fine_grid_n30)    echo 180 ;;
        experiments/095b_baselines_n30)          echo 250 ;;
        experiments/098d_asset_mode_n30)         echo 180 ;;
        experiments/track_b_beta_pilot_n30)      echo 930 ;;
        experiments/track_b_alpha_pilot_n30)     echo 900 ;;
        *)                                       echo 0   ;;
    esac
}

summary_title() {
    case "$1" in
        experiments/099b_memk_refinement_n30)    echo "099b memk refinement n=30" ;;
        experiments/098c_zumdn_fine_grid_n30)    echo "098c zumdn fine-grid n=30" ;;
        experiments/095b_baselines_n30)          echo "095b surrogate baselines n=30" ;;
        experiments/098d_asset_mode_n30)         echo "098d asset x mode ablation n=30" ;;
        experiments/track_b_beta_pilot_n30)      echo "Track B-beta scheduled-sampling pilot n=30" ;;
        experiments/track_b_alpha_pilot_n30)     echo "Track B-alpha Hopfield pilot n=30" ;;
        *)                                       echo "$1" ;;
    esac
}

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_weekend_${TIMESTAMP}.log"

preflight() {
    local fail=0
    echo "── preflight checks ──" | tee -a "$MASTER_LOG"

    for d in "${PHASES[@]}"; do
        local expect="$(expected_n "$d")"
        if [[ ! -d "$d" ]]; then
            if [[ "$d" == "experiments/track_b_alpha_pilot_n30" ]]; then
                echo "  ◌ $d does not exist — B-α phase will be SKIPPED (fail-safe)" \
                    | tee -a "$MASTER_LOG"
                continue
            fi
            echo "  ✗ $d does not exist" | tee -a "$MASTER_LOG"
            fail=1
            continue
        fi
        local n=$(ls "$d"/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$n" != "$expect" ]]; then
            echo "  ✗ $d: expected $expect configs, found $n" | tee -a "$MASTER_LOG"
            fail=1
        else
            echo "  ✓ $d: $n configs" | tee -a "$MASTER_LOG"
        fi
    done

    local free_gb
    if df -BG "$REPO_ROOT" >/dev/null 2>&1; then
        free_gb=$(df -BG "$REPO_ROOT" | awk 'NR==2 {gsub("G","",$4); print $4}')
    else
        free_gb=$(df -k "$REPO_ROOT" | awk 'NR==2 {printf "%d", $4/1024/1024}')
    fi
    # Weekend total est: ~2700 configs × ~6MB results = ~16 GB
    if [[ -n "$free_gb" && "$free_gb" -lt 80 ]]; then
        echo "  ✗ disk free $free_gb GB; need ≥ 80 GB for weekend results" | tee -a "$MASTER_LOG"
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

estimate() {
    local total=0 effective=0
    for d in "${PHASES[@]}"; do
        if [[ ! -d "$d" ]]; then
            echo "  ◌ $d: dir missing (will skip)" | tee -a "$MASTER_LOG"
            continue
        fi
        local n=$(ls "$d"/config_*.yaml 2>/dev/null | wc -l | tr -d ' ')
        local n_done=$(find "$d" -maxdepth 2 -name "inference_merged.json" 2>/dev/null | wc -l | tr -d ' ')
        local eff=$((n - n_done))
        total=$((total + n))
        effective=$((effective + eff))
        local mins=$(( eff * 88 / 80 ))
        echo "  $d: $n configs ($n_done done, $eff effective) ≈ ${mins}m" | tee -a "$MASTER_LOG"
    done
    local total_mins=$(( effective * 88 / 80 ))
    echo "  Weekend total: $total configs (effective: $effective) ≈ $((total_mins/60))h $((total_mins%60))m" \
        | tee -a "$MASTER_LOG"
    echo "  (rule: 8.8 min/config / 8 cards = 1.1 min wall-clock per config)" | tee -a "$MASTER_LOG"
}

run_main() {
    echo "═══ WEEKEND 2026-05-22 — H20 QUEUE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  SKIP_DONE=$SKIP_DONE PARALLEL=$PARALLEL NPROC=$NPROC" | tee -a "$MASTER_LOG"

    if [[ "${1:-}" == "--dry-run" ]]; then
        echo "DRY RUN" | tee -a "$MASTER_LOG"
        estimate
        preflight || echo "  (preflight noted issues; fix before non-dry-run launch)" \
            | tee -a "$MASTER_LOG"
        return 0
    fi

    if ! preflight; then
        echo "ABORT — preflight failed. Fix issues above and re-run." | tee -a "$MASTER_LOG"
        return 1
    fi

    for d in "${PHASES[@]}"; do
        if [[ ! -d "$d" ]]; then
            echo "" | tee -a "$MASTER_LOG"
            echo "◌ SKIP: $d (directory absent — likely B-α fail-safe)" | tee -a "$MASTER_LOG"
            continue
        fi
        echo "" | tee -a "$MASTER_LOG"
        echo "═══ PHASE: $d ═══ $(date) ═══" | tee -a "$MASTER_LOG"
        SECONDS=0
        if ! DAEMON=0 bash scripts/h20_run_phase.sh "$d" 2>&1 | tee -a "$MASTER_LOG"; then
            echo "  [WARN] phase $d returned non-zero; continuing" | tee -a "$MASTER_LOG"
        fi
        echo "  [phase $d] elapsed ${SECONDS}s" | tee -a "$MASTER_LOG"

        echo "  scoring $d ..." | tee -a "$MASTER_LOG"
        local title="$(summary_title "$d")"
        conda run -n ecophys python scripts/score_phase.py "$d" 2>&1 | tee -a "$MASTER_LOG" || \
            echo "  [WARN] score_phase failed for $d" | tee -a "$MASTER_LOG"
        conda run -n ecophys python scripts/score_summary.py "$d" \
            --title "$title" 2>&1 | tee -a "$MASTER_LOG" || \
            echo "  [WARN] score_summary failed for $d" | tee -a "$MASTER_LOG"
    done

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ CHECKPOINT OFFLOAD (R2 sync) — $(date) ═══" | tee -a "$MASTER_LOG"
    conda run -n ecophys python -m ecomd.data.checkpoint_sync sync --delete-local 2>&1 | tee -a "$MASTER_LOG" || \
        echo "  [WARN] checkpoint_sync returned non-zero (likely Supabase key missing; R2 upload still ok)" | tee -a "$MASTER_LOG"

    echo "" | tee -a "$MASTER_LOG"
    echo "═══ WEEKEND DONE — $(date) ═══" | tee -a "$MASTER_LOG"
    echo "  Next step (Mac): scripts/reconcile_r2_to_supabase.py to backfill Supabase catalog" | tee -a "$MASTER_LOG"
    echo "  Then: aggregate analysis per plan §5" | tee -a "$MASTER_LOG"
}

if [[ "${1:-}" == "--dry-run" ]]; then
    run_main --dry-run
    exit 0
fi

if [[ "$DAEMON" == "1" ]]; then
    (run_main) >> "$MASTER_LOG" 2>&1 < /dev/null &
    echo "Started weekend queue in background (PID $!) — log: $MASTER_LOG"
    echo "  tail -f $MASTER_LOG"
else
    run_main
fi
