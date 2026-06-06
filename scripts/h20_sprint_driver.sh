#!/usr/bin/env bash
# Paper-A weekend sprint driver — ONE unattended command on H20-1 that orchestrates all four
# machines for the 36–48h window (plan: ~/.claude/plans → papers/proposal/paper_a_sprint_2026-06-03.md,
# compressed per the 2026-06-06 session).
#
#   Phase 0  restore exp-116 anchor ckpts from R2 if needed; SSH-launch H20-2 (116 + δ-grid
#            eurusd), H20-3 (δ-grid ndx → btcusdt), H20-4 (ABIDES timescale-fair re-run)
#   Phase 1  exp 115 probe (hero concave_sv_both seed0, 1 card) — stability gate + measured
#            min/cfg; unstable → hero cells excluded, G1 auto-fails to the δ-grid fallback
#   Phase 2  exp 115 full queue (8 cards, h20_run_phase)
#   Phase 3  score_composition --json → G1 verdict + winner cell (pre-registered criteria)
#   Phase 4  G1 PASS → exp 119 champion: winner × 4 new assets × n=30 (degrade 25/20 if the
#            measured rate says it won't fit; SPX + baselines reused from 115/113/114)
#            G1 FAIL → δ-grid gold (60 cfg); plus hero × 4 assets n=20 as a sub-SOTA
#            *universality* run iff hero kept the tail AND beat the concave-only cell
#   Phase 5  EVAL window (last EVAL_H hours): catch-up eval pass, all scorers, fetch side
#            results, checkpoint_sync, git commit + push
#
# Budget guardrails: BUDGET_H (default 48) and EVAL_H (default 8) ⇒ no new TRAINING config is
# launched after T0 + BUDGET_H − EVAL_H. Rate is re-measured from the probe and each finished
# phase (planning rate: 62 min/cfg/card — exp 114 measured 390 cfg / 50 h on 8 cards).
#
# Usage on H20-1 (branch feature/exp113-gabaix-solve, machines.local.json filled):
#   BUDGET_H=48 EVAL_H=8 DAEMON=1 bash scripts/h20_sprint_driver.sh
#   tail -f experiments/_sprint_*.log
# Smoke on Mac: DRY_RUN=1 BUDGET_H=48 bash scripts/h20_sprint_driver.sh   (and FAKE_G1=pass|fail)

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

BUDGET_H="${BUDGET_H:-48}"
EVAL_H="${EVAL_H:-8}"
DAEMON="${DAEMON:-0}"
DRY_RUN="${DRY_RUN:-0}"
SOTA=5.96
MACH_FILE="scripts/machines.local.json"

T0="$(date +%s)"
CUTOFF_TRAIN=$(( T0 + (BUDGET_H - EVAL_H) * 3600 ))
TS="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="experiments/_sprint_${TS}.log"
MIN_PER_CFG=62          # planning rate; refined by the probe / finished phases

say()    { echo "[sprint $(date +%H:%M:%S)] $*" | tee -a "$MASTER_LOG"; }
left_s() { echo $(( CUTOFF_TRAIN - $(date +%s) )); }

# can_fit N_CFG N_CARDS → 0/1: does N_CFG fit before the training cutoff at the measured rate?
can_fit() {
    local n_cfg="$1" cards="$2"
    local need_s=$(( n_cfg * MIN_PER_CFG * 60 / cards ))
    (( need_s * 100 <= $(left_s) * 95 ))   # 5% safety margin
}

run() {  # heavy command wrapper — echo-only under DRY_RUN
    if [[ "$DRY_RUN" == "1" ]]; then say "DRY: $*"; else "$@" 2>&1 | tee -a "$MASTER_LOG"; fi
}

mach() { python3 -c "import json; print(json.load(open('$MACH_FILE'))['$1'].get('$2', ''))" 2>/dev/null; }

main() {
say "═══ Paper-A sprint driver ═══ BUDGET_H=$BUDGET_H EVAL_H=$EVAL_H DRY_RUN=$DRY_RUN"
say "train cutoff: $(date -r "$CUTOFF_TRAIN" 2>/dev/null || date -d "@$CUTOFF_TRAIN" 2>/dev/null)"
[[ -f "$MACH_FILE" || "$DRY_RUN" == "1" ]] || { say "ERROR: $MACH_FILE missing (cp scripts/machines.example.json … and fill IPs)"; exit 1; }

# ── Phase 0: side machines + ABIDES ─────────────────────────────────────────────
say "── Phase 0: anchors + side machines + ABIDES"
if [[ "$DRY_RUN" != "1" ]]; then
    for s in 0 1 2; do   # exp 116 anchors (delete-synced to R2 after 113)
        d="experiments/113_gabaix_solve/results_baseline_seed$s"
        [[ -f "$d/checkpoint.pt" ]] && continue
        say "restoring anchor $d from R2"
        conda run -n ecophys python -m ecomd.data.r2_sync download \
            "checkpoints/$d" "$d" 2>&1 | tee -a "$MASTER_LOG" || say "WARN: anchor $d restore failed"
    done
fi
CUTOFF_EPOCH="$CUTOFF_TRAIN" run bash scripts/h20_side_queue.sh h20_2 launch || say "WARN: h20_2 launch failed — 116/eurusd lost, continuing"
CUTOFF_EPOCH="$CUTOFF_TRAIN" run bash scripts/h20_side_queue.sh h20_3 launch || say "WARN: h20_3 launch failed — ndx/btc δ-grid lost, continuing"
if [[ "$DRY_RUN" != "1" ]]; then
    ABIDES_HOST="$(mach h20_4 host)" ABIDES_USER="$(mach h20_4 user)" \
    ABIDES_SSH_PORT="$(mach h20_4 ssh_port)" ABIDES_REMOTE_DIR="$(mach h20_4 root)" \
    ABIDES_ENV="$(mach h20_4 env)" bash scripts/h20_abides_remote.sh launch 2>&1 | tee -a "$MASTER_LOG" \
        || say "WARN: ABIDES launch failed — re-run manually (h20_abides_remote.sh)"
else
    say "DRY: abides launch"
fi

# ── Phase 1: 115 probe ──────────────────────────────────────────────────────────
say "── Phase 1: exp 115 probe (hero stability + rate measurement)"
PROBE_OK=1
if [[ "$DRY_RUN" == "1" ]]; then
    say "DRY: probe assumed stable, rate stays ${MIN_PER_CFG}min/cfg"
else
    SECONDS=0
    bash scripts/h20_115_composition.sh --probe 2>&1 | tee -a "$MASTER_LOG"
    probe_min=$(( SECONDS / 60 ))
    if grep -q "✗ BLOWUP" "$MASTER_LOG"; then PROBE_OK=0; fi
    grep -q "✓ stable" "$MASTER_LOG" || PROBE_OK=0
    if (( probe_min > MIN_PER_CFG )); then
        MIN_PER_CFG="$probe_min"
        say "probe measured ${probe_min} min/cfg → planning rate updated"
    fi
fi
if [[ "$PROBE_OK" != "1" ]]; then
    say "probe UNSTABLE → excluding hero cells from 115 (G1 will fail to the δ-grid fallback)"
    mkdir -p experiments/115_composition/_excluded
    run bash -c 'mv experiments/115_composition/config_concave_sv_*.yaml experiments/115_composition/_excluded/ 2>/dev/null || true'
fi

# ── Phase 2: 115 full ───────────────────────────────────────────────────────────
say "── Phase 2: exp 115 full (150 cfg, 8 cards)"
SECONDS=0
DAEMON=0 PARALLEL=8 run bash scripts/h20_run_phase.sh experiments/115_composition
if [[ "$DRY_RUN" != "1" && "$SECONDS" -gt 600 ]]; then
    done_n="$(ls experiments/115_composition/results_*/inference_merged.json 2>/dev/null | wc -l | tr -d ' ')"
    if (( done_n > 0 )); then
        MIN_PER_CFG=$(( SECONDS * 8 / 60 / done_n ))
        (( MIN_PER_CFG < 40 )) && MIN_PER_CFG=40
        say "phase 2: $done_n cfg in $((SECONDS/3600))h → measured ${MIN_PER_CFG} min/cfg"
    fi
fi
run conda run -n ecophys python scripts/score_phase.py experiments/115_composition

# ── Phase 3: G1 verdict ─────────────────────────────────────────────────────────
say "── Phase 3: G1 verdict (score_composition --json)"
G1_JSON="experiments/115_composition/g1_verdict.json"
if [[ "$DRY_RUN" == "1" ]]; then
    if [[ "${FAKE_G1:-pass}" == "pass" ]]; then
        echo '{"g1_pass": true, "winner_cell": "concave_sv_both", "hero_tail_kept": true, "hero_beats_concave": true}' > "$G1_JSON"
    else
        echo '{"g1_pass": false, "winner_cell": null, "hero_tail_kept": true, "hero_beats_concave": true}' > "$G1_JSON"
    fi
else
    conda run -n ecophys python scripts/score_composition.py experiments/115_composition --json \
        > "$G1_JSON" 2>>"$MASTER_LOG" || say "WARN: scorer failed — treating as G1 FAIL"
fi
g1() { python3 -c "import json; v=json.load(open('$G1_JSON')).get('$1'); print({True:'1',False:'0',None:''}.get(v,v))" 2>/dev/null; }
G1_PASS="$(g1 g1_pass)"; WINNER="$(g1 winner_cell)"
say "G1: pass=${G1_PASS:-0} winner=${WINNER:-none} hero_tail_kept=$(g1 hero_tail_kept) hero_beats_concave=$(g1 hero_beats_concave)"

# ── Phase 4: conditional branch ─────────────────────────────────────────────────
if [[ "$G1_PASS" == "1" && -n "$WINNER" ]]; then
    N_SEEDS=30
    can_fit $(( 4 * N_SEEDS )) 8 || N_SEEDS=25
    can_fit $(( 4 * N_SEEDS )) 8 || N_SEEDS=20
    if can_fit $(( 4 * N_SEEDS )) 8; then
        say "── Phase 4 PASS: champion $WINNER × 4 assets × n=$N_SEEDS"
        run conda run -n ecophys python experiments/119_champion_confirm/generate_configs.py \
            --cell "$WINNER" --n-seeds "$N_SEEDS"
        DAEMON=0 PARALLEL=8 run bash scripts/h20_run_phase.sh experiments/119_champion_confirm
        run conda run -n ecophys python scripts/score_phase.py experiments/119_champion_confirm
    else
        say "Phase 4 SKIPPED: not even n=20 champion fits before cutoff (left $(($(left_s)/3600))h)"
    fi
else
    say "── Phase 4 FAIL-branch: δ-grid gold (60 cfg)"
    if can_fit 60 8; then
        DAEMON=0 PARALLEL=8 run bash scripts/h20_run_phase.sh experiments/118_delta_grid/gold
    else
        say "gold δ-grid skipped (no budget)"
    fi
    if [[ "$(g1 hero_tail_kept)" == "1" && "$(g1 hero_beats_concave)" == "1" ]] && can_fit 80 8; then
        say "hero kept tail + beats concave → sub-SOTA hero universality run (4 assets × n=20, NOT a SOTA claim)"
        run conda run -n ecophys python experiments/119_champion_confirm/generate_configs.py \
            --cell concave_sv_both --n-seeds 20
        DAEMON=0 PARALLEL=8 run bash scripts/h20_run_phase.sh experiments/119_champion_confirm
        run conda run -n ecophys python scripts/score_phase.py experiments/119_champion_confirm
    fi
fi

# ── Phase 5: EVAL window ────────────────────────────────────────────────────────
say "── Phase 5: EVAL window (catch-up evals, side fetch, scoreboards, push)"
# side workers stop LAUNCHING at the same cutoff; last jobs need ≤ ~MIN_PER_CFG more
wait_until=$(( CUTOFF_TRAIN + MIN_PER_CFG * 60 + 600 ))
if (( $(date +%s) < wait_until )) && [[ "$DRY_RUN" != "1" ]]; then
    say "waiting for side machines until $(date -r "$wait_until" 2>/dev/null || date -d "@$wait_until")"
    sleep $(( wait_until - $(date +%s) ))
fi
# catch-up: EVAL-ONLY pass on anything trained-but-not-evaled (no training in the EVAL window)
catchup_eval() {
    local dir="$1" i=0
    for out in "$dir"/results_*; do
        [[ -f "$out/checkpoint.pt" && ! -f "$out/inference_merged.json" ]] || continue
        local cfg="$dir/$(basename "$out" | sed 's/^results_/config_/').yaml"
        [[ -f "$cfg" ]] || continue
        say "catch-up eval: $(basename "$out")"
        while (( $(jobs -rp | wc -l) >= 8 )); do wait -n; done
        CUDA_VISIBLE_DEVICES=$(( i % 8 )) timeout 14400 conda run --no-capture-output -n ecophys \
            torchrun --nproc_per_node=1 --standalone -m ecomd.inference.run_large \
            --ckpt "$out/checkpoint.pt" --config "$cfg" --n-steps 4000 --n-realizations-per-rank 4 \
            >> "$out/catchup_eval.log" 2>&1 &
        i=$(( i + 1 ))
    done
    wait
}
for d in experiments/115_composition experiments/119_champion_confirm experiments/118_delta_grid/gold; do
    if [[ -d "$d" && "$DRY_RUN" != "1" ]]; then catchup_eval "$d"; else say "DRY: catchup_eval $d"; fi
done
run bash scripts/h20_side_queue.sh h20_2 fetch
run bash scripts/h20_side_queue.sh h20_3 fetch
run conda run -n ecophys python scripts/score_criticality.py experiments/116_criticality
run conda run -n ecophys python scripts/score_delta_grid.py
run conda run -n ecophys python -m ecomd.data.checkpoint_sync sync --delete-local
if [[ "$DRY_RUN" != "1" ]]; then
    git add experiments/115_composition experiments/116_criticality experiments/118_delta_grid \
            experiments/119_champion_confirm 2>>"$MASTER_LOG"
    git add "$MASTER_LOG" 2>/dev/null || true
    git commit -m "sprint window results: 115 composition (G1=$([[ "$G1_PASS" == "1" ]] && echo PASS || echo FAIL), winner=${WINNER:-none}) + 116 criticality + 118 δ-grid + 119 champion

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>" 2>&1 | tee -a "$MASTER_LOG" || say "WARN: nothing to commit"
    git push 2>&1 | tee -a "$MASTER_LOG" || say "WARN: push failed — push manually"
fi
say "═══ sprint driver DONE ═══ elapsed $(( ($(date +%s) - T0) / 3600 ))h; G1=${G1_PASS:-0} winner=${WINNER:-none}"
say "ABIDES keeps running on H20-4 — fetch later: bash scripts/h20_abides_remote.sh fetch"
}

if [[ "$DAEMON" == "1" ]]; then
    (main) >> "$MASTER_LOG" 2>&1 < /dev/null &
    pid=$!; disown "$pid" 2>/dev/null || true
    echo "$pid" > "${MASTER_LOG}.pid"
    echo "sprint driver started (PID $pid) — tail -f $MASTER_LOG"
else
    main
fi
