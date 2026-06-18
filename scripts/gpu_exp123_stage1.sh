#!/usr/bin/env bash
# exp 123 driven-transient — Stage-1 earns-or-kills run on the 12-card fleet (8 + 2 + 2).
#
# Question (PREREG_2026-06-18.md): is the heavy tail a non-equilibrium DRIVEN TRANSIENT (P, a
# publishable frontier result) or a t=0 STARTUP ARTIFACT (A)? We drive a steady-state model out
# of equilibrium with a controlled state_kick at T_SHOCK and ask whether the cube-law tail revives
# then relaxes — with the same ζ_ED signature as the t=0 burn-in template.
#
# Fleet allocation (all 12 cards, complementary jobs, ~1–3 h):
#   h20_1 (8 cards): WORKER spx FULL   — control + kick{3,6,12}, n≈32          → the DECISION
#   h20_2 (2 cards): WORKER ndx REPLIC — control + kick6,        n=30          → asset-general?
#   h20_3 (2 cards): R1 magnitude      — 114 baseline+concave, --save-trajectory → honest write-up
#
# Inference is cheap (~6 min / 4 rollouts at n_steps=8000 on 2 cards). Checkpoints were synced to
# R2 + deleted locally → reuse-or-retrain (1 seed) like gpu_zeta_ed_2card.sh.
#
# USAGE
#   Mac dry-run (echo only, no GPU):   DRY_RUN=1 bash scripts/gpu_exp123_stage1.sh fanout
#   ── Option A: one command on h20_1 (needs scripts/machines.local.json filled) ──
#     bash scripts/gpu_exp123_stage1.sh fanout
#   ── Option B: run one command per machine yourself (robust; no driver SSH) ──
#     # on the 8-card box:
#     ASSET=spx ARMS="control kick3 kick6 kick12" NPROC=8 N_REAL=4 SEED_BASE=10000 OUT_TAG=m1 \
#       bash scripts/gpu_exp123_stage1.sh worker
#     # on 2-card box #1:
#     ASSET=ndx ARMS="control kick6" NPROC=2 N_REAL=15 SEED_BASE=20000 OUT_TAG=m2 \
#       bash scripts/gpu_exp123_stage1.sh worker
#     # on 2-card box #2:
#     NPROC=2 bash scripts/gpu_exp123_stage1.sh r1
#   ── then, after all finish (on any box / Mac): ──
#     bash scripts/gpu_exp123_stage1.sh eval         # windowed Hill per arm + the H1–H4 verdict

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$REPO_ROOT"

ENV="${ECOPHYS_ENV:-ecophys}"
EXP="experiments/123_driven_transient"
N_STEPS="${N_STEPS:-8000}"          # rollout length (PREREG)
T_SHOCK="${T_SHOCK:-3000}"          # shock step (PREREG; burn-in [0,500) discarded, control [500,3000))
FRAC="${FRAC:-0.1}"                 # state_kick fraction of agents
W="${W:-500}"; STRIDE="${STRIDE:-100}"; KFRAC="${KFRAC:-0.1}"   # windowed estimator (PREREG)
DRY_RUN="${DRY_RUN:-0}"
SEED="${SEED:-0}"                   # which trained seed to reuse/retrain
MACH_FILE="scripts/machines.local.json"
TS="$(date +%Y%m%d_%H%M%S)"; LOG="${EXP}/_stage1_${TS}.log"; mkdir -p "$EXP"

# say → stderr so it never pollutes a $(…) capture (ensure_ckpt etc.); still tee'd to the log.
say() { echo "[exp123 $(date +%H:%M:%S)] $*" | tee -a "$LOG" >&2; }
run() { if [[ "$DRY_RUN" == "1" ]]; then say "DRY: $*"; else "$@" 2>&1 | tee -a "$LOG"; fi; }
mach(){ python3 -c "import json;print(json.load(open('$MACH_FILE'))['$1'].get('$2',''))" 2>/dev/null; }

# reuse-or-retrain the concave_d050 checkpoint for ASSET; sets global CKPT (no $(…) capture).
ensure_ckpt() {
  local asset="$1" cfg="$2" ckdir ckpt
  case "$asset" in
    spx) ckdir="experiments/113_gabaix_solve/results_concave_d050_seed${SEED}" ;;
    *)   ckdir="experiments/114_concave_confirm/results_${asset}_concave_d050_seed${SEED}" ;;
  esac
  ckpt="${ckdir}/checkpoint.pt"
  if [[ "${FORCE_RETRAIN:-0}" == "1" || ! -f "$ckpt" ]]; then
    local out="${EXP}/_ckpt_${asset}"; mkdir -p "$out"
    say "no local ckpt ($ckpt) → retraining 1 seed (concave_d050) → $out"
    run conda run --no-capture-output -n "$ENV" torchrun --nproc_per_node="${NPROC:-2}" --standalone \
      -m ecomd.training.train_distributed --config "$cfg" --out-dir "$out"
    ckpt="${out}/checkpoint.pt"
  fi
  CKPT="$ckpt"
}

# one arm of one asset on THIS machine → results_<asset>_<arm>/<OUT_TAG>/trajectory_*.npz
run_arm() {
  local asset="$1" arm="$2" cfg="$3" ckpt="$4" nproc="$5" n_real="$6" seed_base="$7" tag="$8"
  local out="${EXP}/results_${asset}_${arm}/${tag}"; mkdir -p "$out"
  local shock=()
  if [[ "$arm" != "control" ]]; then
    local mag="${arm#kick}"
    shock=(--shock-step "$T_SHOCK" --shock-type state_kick --shock-mag "$mag" --shock-frac "$FRAC")
  fi
  say "$asset/$arm: n_steps=$N_STEPS × $((nproc*n_real)) rollouts (seed_base=$seed_base) → $out"
  # "${shock[@]+...}" expands only when set → safe under set -u on bash 3.2 (macOS) with empty array.
  run conda run --no-capture-output -n "$ENV" torchrun --nproc_per_node="$nproc" --standalone \
    -m ecomd.inference.run_large --ckpt "$ckpt" --config "$cfg" --out-dir "$out" \
    --save-trajectory --n-steps "$N_STEPS" --n-realizations-per-rank "$n_real" \
    --seed-base "$seed_base" "${shock[@]+"${shock[@]}"}"
}

worker() {  # env: ASSET ARMS NPROC N_REAL SEED_BASE OUT_TAG
  local asset="${ASSET:?set ASSET}" cfg="${EXP}/config_${ASSET}.yaml"
  [[ -f "$cfg" ]] || { say "ERROR: $cfg missing — run generate_configs.py"; exit 1; }
  ensure_ckpt "$asset" "$cfg"; local ckpt="$CKPT"
  [[ "$DRY_RUN" == "1" || -f "$ckpt" ]] || { say "ERROR: no ckpt for $asset"; exit 1; }
  say "═══ WORKER $asset arms='${ARMS}' NPROC=${NPROC} N_REAL=${N_REAL} tag=${OUT_TAG} ═══"
  local arm
  for arm in ${ARMS}; do
    run_arm "$asset" "$arm" "$cfg" "$ckpt" "${NPROC}" "${N_REAL}" "${SEED_BASE}" "${OUT_TAG}"
  done
  say "✓ worker $asset done"
}

r1() {  # R1 magnitude: 114 baseline + concave_d050, --save-trajectory (no shock); CPU-scored later
  say "═══ R1 magnitude (warmup-discard) — 114 baseline + concave_d050, spx ═══"
  local nproc="${NPROC:-2}" out cfg ckpt cell
  for cell in baseline concave_d050; do
    cfg="experiments/113_gabaix_solve/config_${cell}_seed${SEED}.yaml"
    [[ -f "$cfg" ]] || cfg="experiments/114_concave_confirm/config_spx_${cell}_seed${SEED}.yaml"
    [[ -f "$cfg" ]] || { say "  [skip] no config for spx/$cell"; continue; }
    ckpt="${cfg%/*}/results_$(basename "${cfg%.yaml}" | sed 's/config_//')/checkpoint.pt"
    [[ -f "$ckpt" || "$DRY_RUN" == "1" ]] || { say "  [skip] no ckpt $ckpt (place from R2 to use exact seed)"; continue; }
    out="${EXP}/r1_spx_${cell}"; mkdir -p "$out"
    run conda run --no-capture-output -n "$ENV" torchrun --nproc_per_node="$nproc" --standalone \
      -m ecomd.inference.run_large --ckpt "$ckpt" --config "$cfg" --out-dir "$out" \
      --save-trajectory --n-steps "$N_STEPS" --n-realizations-per-rank 8
  done
  say "✓ R1 trajectories written → score with --windows (drop the [0,500) window = warmup discard)"
}

eval_stage1() {  # windowed Hill α(t) per arm + the H1–H4 verdict scaffold
  say "═══ EVAL — windowed Hill α(t) per arm ═══"
  local d
  for d in "$EXP"/results_*; do
    [[ -d "$d" ]] || continue
    ls "$d"/**/trajectory_*.npz >/dev/null 2>&1 || ls "$d"/*/trajectory_*.npz >/dev/null 2>&1 || continue
    say "── $(basename "$d") ──"
    run conda run --no-capture-output -n "$ENV" python scripts/score_transfer_law.py \
      --windows "$d" --window "$W" --stride "$STRIDE" --k-frac "$KFRAC" --shock-step "$T_SHOCK"
  done
  say "VERDICT (read the windowed_hill_report.json per arm; thresholds in PREREG_2026-06-18.md):"
  say "  H1 control α_ED ≥4 in [500,3000)?  H2 kick* α_ED ≤2 post-shock, deepening with dose?"
  say "  H3 recovers to ≥4 by step ~7000?   H4 post-shock min α matches the t<500 burn-in template?"
  say "  H1∧H2∧H3∧H4 ⇒ PHYSICS (paper earned).  H2 fails ⇒ artifact (fallback)."
  # R1 magnitude — standard hill with/without warmup discard (only if r1_* trajectories exist)
  if ls "$EXP"/r1_*/**/trajectory_*.npz "$EXP"/r1_*/trajectory_*.npz >/dev/null 2>&1; then
    say "── R1 magnitude (standard hill vs warmup discard) ──"
    run conda run --no-capture-output -n "$ENV" python scripts/score_transfer_law.py --r1-warmup "$EXP"
  fi
}

fanout() {  # on h20_1: local spx (8) + SSH ndx (2) + SSH R1 (2)
  [[ -f "$MACH_FILE" || "$DRY_RUN" == "1" ]] || { say "ERROR: $MACH_FILE missing (cp machines.example.json …)"; exit 1; }
  say "═══ FANOUT: spx@h20_1(8) + ndx@h20_2(2) + R1@h20_3(2) ═══"
  local h2 u2 r2 e2 h3 u3 r3 e3
  h2="$(mach h20_2 host)"; u2="$(mach h20_2 user)"; r2="$(mach h20_2 root)"; e2="$(mach h20_2 env)"
  h3="$(mach h20_3 host)"; u3="$(mach h20_3 user)"; r3="$(mach h20_3 root)"; e3="$(mach h20_3 env)"
  # side machines first (background), then the local 8-card worker
  run ssh "${u2}@${h2}" "cd ${r2} && git pull -q && ASSET=ndx ARMS='control kick6' NPROC=2 N_REAL=15 SEED_BASE=20000 OUT_TAG=m2 ECOPHYS_ENV=${e2} N_STEPS=${N_STEPS} T_SHOCK=${T_SHOCK} DAEMON=1 nohup bash scripts/gpu_exp123_stage1.sh worker >${r2}/${EXP}/_m2.log 2>&1 &"
  run ssh "${u3}@${h3}" "cd ${r3} && git pull -q && NPROC=2 ECOPHYS_ENV=${e3} N_STEPS=${N_STEPS} nohup bash scripts/gpu_exp123_stage1.sh r1 >${r3}/${EXP}/_m3.log 2>&1 &"
  ASSET=spx ARMS="control kick3 kick6 kick12" NPROC=8 N_REAL=4 SEED_BASE=10000 OUT_TAG=m1 worker
  say "local spx done; fetch side results (rsync the side ${EXP}/results_* dirs here) then: bash $0 eval"
}

case "${1:-fanout}" in
  worker) worker ;;
  r1)     r1 ;;
  eval)   eval_stage1 ;;
  fanout) fanout ;;
  *) echo "usage: $0 {fanout|worker|r1|eval}   (worker needs ASSET/ARMS/NPROC/N_REAL/SEED_BASE/OUT_TAG)"; exit 2 ;;
esac
