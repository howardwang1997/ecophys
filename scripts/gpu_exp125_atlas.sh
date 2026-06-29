#!/usr/bin/env bash
# exp 125 — root-cause ablations + controllability atlas + rigor (PREREG.md).
# Reuses the concave_d050 checkpoints (5 assets). Inference-only except G-D1b/G-E.
# All steady-state numbers use a warm-up discard downstream (burn-in fix).
#
# MODES
#   worker  : shock arms (control/kickM/jumpM/tempM/liqD) for $ASSET     (G-A,G-B,G-C)
#   ablate  : root-cause arms (normal/tDF/levyXY/nscanN), NO shock        (G-D1a,G-D2)
#   eval    : windowed α(t) + OFI signature + 11-fact + CI aggregation
#   fanout  : distribute across the 2+2+4+8 fleet (needs scripts/machines.local.json)
#
# PER-NODE EXAMPLES (Option B — run one per machine; robust, no driver SSH)
#   # 8-card: controllability atlas (dur=20 primary)
#   ASSET=spx ARMS="control kick6 temp3 temp5 liq3 liq5" NPROC=8 N_REAL=3 \
#     DUR=20 SEED_BASE=50000 OUT_TAG=atlas bash scripts/gpu_exp125_atlas.sh worker
#   # 4-card: rigor (n=30: 8 cards would be N_REAL=4; on 4 cards N_REAL=8)
#   ASSET=spx ARMS="control kick6" NPROC=4 N_REAL=8 SEED_BASE=51000 OUT_TAG=rigor \
#     bash scripts/gpu_exp125_atlas.sh worker
#   # 2-card #1: dose law
#   ASSET=spx ARMS="kick0.05 kick0.1 kick0.2 kick0.5 kick1 kick2 kick6 kick12" \
#     NPROC=2 N_REAL=10 SEED_BASE=52000 OUT_TAG=dose bash scripts/gpu_exp125_atlas.sh worker
#   # 2-card #2: root-cause ablations (G-D1a noise + G-D2 N-scan)
#   ASSET=spx ABLATE="normal t5 t3 levy19 levy17 levy15 nscan100 nscan300 nscan1000 nscan3000 nscan10000 nscan30000" \
#     NPROC=2 N_REAL=10 SEED_BASE=53000 OUT_TAG=root bash scripts/gpu_exp125_atlas.sh ablate
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$REPO_ROOT"
export PATH=/root/miniconda3/bin:${PATH:-}          # H20 conda not on non-interactive PATH
ENV="${ECOPHYS_ENV:-ecophys}"
EXP="experiments/125_rootcause_controllability"
N_STEPS="${N_STEPS:-8000}"; T_SHOCK="${T_SHOCK:-3000}"; FRAC="${FRAC:-0.1}"; DUR="${DUR:-20}"
W="${W:-500}"; STRIDE="${STRIDE:-100}"; KFRAC="${KFRAC:-0.1}"
DRY_RUN="${DRY_RUN:-0}"; SEED="${SEED:-0}"; MACH_FILE="scripts/machines.local.json"
TS="$(date +%Y%m%d_%H%M%S)"; LOG="${EXP}/_run_${TS}.log"; mkdir -p "$EXP"
say(){ echo "[exp125 $(date +%H:%M:%S)] $*" | tee -a "$LOG" >&2; }
run(){ if [[ "$DRY_RUN" == "1" ]]; then say "DRY: $*"; else "$@" 2>&1 | tee -a "$LOG"; fi; }
mach(){ python3 -c "import json;print(json.load(open('$MACH_FILE'))['$1'].get('$2',''))" 2>/dev/null; }

ensure_ckpt(){  # sets global CKPT (concave_d050 for ASSET); pull from R2 if absent
  local asset="$1" ckdir ckpt
  case "$asset" in
    spx) ckdir="experiments/113_gabaix_solve/results_concave_d050_seed${SEED}" ;;
    *)   ckdir="experiments/114_concave_confirm/results_${asset}_concave_d050_seed${SEED}" ;;
  esac
  ckpt="${ckdir}/checkpoint.pt"
  [[ -f "$ckpt" ]] || say "WARN: $ckpt missing — run scripts/h20_pull_from_r2.sh first"
  CKPT="$ckpt"
}

# shock arm → run_large flags (echoed)
shock_flags(){
  local arm="$1"
  case "$arm" in
    control) ;;
    kick*) echo "--shock-step $T_SHOCK --shock-type state_kick --shock-mag ${arm#kick} --shock-frac $FRAC" ;;
    jump*) echo "--shock-step $T_SHOCK --shock-type price_jump --shock-mag ${arm#jump}" ;;
    temp*) echo "--shock-step $T_SHOCK --shock-type temperature_spike --shock-mag ${arm#temp} --shock-dur $DUR" ;;
    liq*)  echo "--shock-step $T_SHOCK --shock-type liquidity_drop --shock-mag ${arm#liq} --shock-dur $DUR" ;;
    *) say "ERROR: unknown shock arm '$arm'"; exit 2 ;;
  esac
}

# ablate arm → run_large overrides (no shock)
ablate_flags(){
  local arm="$1" a
  case "$arm" in
    normal) echo "--noise-dist normal" ;;
    t*)     echo "--noise-dist t --noise-df ${arm#t}" ;;
    levy*)  a="${arm#levy}"; echo "--noise-dist levy --noise-levy-alpha ${a:0:1}.${a:1}" ;;
    nscan*) echo "--n-agents ${arm#nscan}" ;;
    *) say "ERROR: unknown ablate arm '$arm'"; exit 2 ;;
  esac
}

run_one(){  # asset arm cfg ckpt nproc n_real seed_base tag extra_flags...
  local asset="$1" arm="$2" cfg="$3" ckpt="$4" nproc="$5" n_real="$6" seed_base="$7" tag="$8"; shift 8
  local out="${EXP}/results_${asset}_${arm}/${tag}"; mkdir -p "$out"
  say "$asset/$arm: $((nproc*n_real)) rollouts (seed_base=$seed_base) → $out"
  run conda run --no-capture-output -n "$ENV" torchrun --nproc_per_node="$nproc" --standalone \
    -m ecomd.inference.run_large --ckpt "$ckpt" --config "$cfg" --out-dir "$out" \
    --save-trajectory --n-steps "$N_STEPS" --n-realizations-per-rank "$n_real" \
    --seed-base "$seed_base" "$@"
}

worker(){  # env: ASSET ARMS NPROC N_REAL SEED_BASE OUT_TAG [DUR]
  local asset="${ASSET:?set ASSET}" cfg="experiments/123_driven_transient/config_${ASSET}.yaml"
  [[ -f "$cfg" ]] || { say "ERROR: $cfg missing"; exit 1; }
  ensure_ckpt "$asset"; local arm
  say "═══ WORKER $asset arms='${ARMS}' NPROC=${NPROC} N_REAL=${N_REAL} DUR=${DUR} tag=${OUT_TAG} ═══"
  for arm in ${ARMS}; do
    run_one "$asset" "$arm" "$cfg" "$CKPT" "$NPROC" "$N_REAL" "$SEED_BASE" "$OUT_TAG" $(shock_flags "$arm")
  done
  say "✓ worker $asset done"
}

ablate(){  # env: ASSET ABLATE NPROC N_REAL SEED_BASE OUT_TAG
  local asset="${ASSET:?set ASSET}" cfg="experiments/123_driven_transient/config_${ASSET}.yaml"
  [[ -f "$cfg" ]] || { say "ERROR: $cfg missing"; exit 1; }
  ensure_ckpt "$asset"; local arm
  say "═══ ABLATE $asset arms='${ABLATE}' NPROC=${NPROC} N_REAL=${N_REAL} tag=${OUT_TAG} ═══"
  for arm in ${ABLATE}; do
    run_one "$asset" "$arm" "$cfg" "$CKPT" "$NPROC" "$N_REAL" "$SEED_BASE" "$OUT_TAG" $(ablate_flags "$arm")
  done
  say "✓ ablate $asset done"
}

eval_all(){
  say "═══ EVAL — windowed α(t) + signature CIs + 11-fact ═══"
  local d
  for d in "$EXP"/results_*; do
    [[ -d "$d" ]] || continue
    ls "$d"/*/trajectory_*.npz >/dev/null 2>&1 || continue
    say "── $(basename "$d") ──"
    run conda run --no-capture-output -n "$ENV" python scripts/score_transfer_law.py \
      --windows "$d" --window "$W" --stride "$STRIDE" --k-frac "$KFRAC" --shock-step "$T_SHOCK" || true
  done
  # CI aggregation across seeds (G-A) + τ(dose) law (G-C) — analysis scripts (see DESIGN.md §Launch)
  for s in aggregate_atlas_cis.py fit_tau_dose_law.py score_noise_ablation.py; do
    [[ -f "scripts/$s" ]] && run conda run --no-capture-output -n "$ENV" python "scripts/$s" --exp "$EXP" || \
      say "  (scripts/$s not present yet — write per DESIGN.md before final eval)"
  done
  say "push reports:"; BR="$(git rev-parse --abbrev-ref HEAD)"
  git add "$EXP"/*.json 2>/dev/null || true
  if git diff --cached --quiet; then say "(nothing to commit)"; else
    git commit -q -m "exp 125: root-cause + atlas + rigor reports" \
      && { git push origin "$BR" 2>&1 | tee -a "$LOG" \
           || { git pull --rebase -q origin "$BR" && git push origin "$BR" 2>&1 | tee -a "$LOG"; }; }
  fi
}

fanout(){
  [[ -f "$MACH_FILE" || "$DRY_RUN" == "1" ]] || { say "ERROR: $MACH_FILE missing"; exit 1; }
  say "═══ FANOUT across 8+4+2+2 ═══ (edit node→job map below to taste)"
  say "(this is a template — verify machines.local.json has h20_1..h20_4 with gpus 8/4/2/2)"
  # 8-card local: atlas; side nodes via SSH. Fill per your machines.local.json roles.
  say "Run the per-node Option-B commands in this script's header on each box (recommended)."
}

case "${1:-}" in
  worker) worker ;;
  ablate) ablate ;;
  eval)   eval_all ;;
  fanout) fanout ;;
  *) echo "usage: $0 {worker|ablate|eval|fanout}  (see header for env vars)"; exit 2 ;;
esac
