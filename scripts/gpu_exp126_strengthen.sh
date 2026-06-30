#!/usr/bin/env bash
# exp 126 — workshop-strengthening suite, FULL scope (DESIGN.md / PREREG.md). NO data buy.
# Sized for a week on 4 cards (two 2-card boxes; one is the orchestrator). Reuses concave_d050 + baseline
# checkpoints (pulled from R2) for all inference; TRAINS only the G-D1b Lévy Pareto.
# All steady-state numbers use a warm-up discard downstream (burn-in fix, exp 125 PREREG).
#
# MODES (env-driven; see each fn header)
#   train   : G-D1b — train every config_levy*_spx_seed*.yaml in this exp dir (1 card/train)
#   score   : roll out the t(df5) baseline + every trained Lévy ckpt (NO shock) -> 11 facts + windowed
#   worker  : shock arms control/kickM/jumpM/tempM/liqD for $ASSET (atlas + dose). temp/liq encode the
#             duration into the result-arm name (results_<asset>_<arm>_d<DUR>) so each mag x dur is clean.
#   ablate  : nscanN arms (NO shock, save-trajectory) for $ASSET — return self-averaging / alpha_ED(N)
#   noshock : generic NO-shock rollout of an explicit CKPT+CONFIG into results_<RARM>/<OUT_TAG>
#             (baseline-family warm-up arms, 2nd-generator scoring)
#   eval    : windowed alpha(t) per arm-dir + the 4 analysis scripts + commit/push
#
# PER-NODE EXAMPLES (Option B — robust, no driver SSH)
#   bash scripts/gpu_exp126_strengthen.sh train          # all Lévy configs, 1 card each
#   N_REAL=16 bash scripts/gpu_exp126_strengthen.sh score
#   ASSET=spx ARMS="control kick0.05 kick0.1 kick0.2 kick0.5 kick1 kick2 kick6 kick12" NPROC=2 N_REAL=12 SEED_BASE=62000 OUT_TAG=dose bash scripts/gpu_exp126_strengthen.sh worker
#   ASSET=spx ARMS="temp3 temp5 temp8 liq3 liq5 liq10" DUR=20 NPROC=2 N_REAL=12 SEED_BASE=60000 OUT_TAG=atlas bash scripts/gpu_exp126_strengthen.sh worker
#   ASSET=spx ABLATE="nscan100 nscan300 nscan1000 nscan3000 nscan10000 nscan30000 nscan60000 nscan100000" NPROC=2 N_REAL=16 SEED_BASE=63000 OUT_TAG=selfavg bash scripts/gpu_exp126_strengthen.sh ablate
#   CKPT=experiments/113_gabaix_solve/results_baseline_seed0/checkpoint.pt CONFIG=experiments/113_gabaix_solve/config_baseline_seed0.yaml RARM=spx_warmup_baseline OUT_TAG=score N_REAL=20 bash scripts/gpu_exp126_strengthen.sh noshock
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$REPO_ROOT"
export PATH=/root/miniconda3/bin:${PATH:-}
ENV="${ECOPHYS_ENV:-ecophys}"
EXP="experiments/126_strengthen_workshops"
N_STEPS="${N_STEPS:-8000}"; T_SHOCK="${T_SHOCK:-3000}"; FRAC="${FRAC:-0.1}"; DUR="${DUR:-20}"
W="${W:-500}"; STRIDE="${STRIDE:-100}"; KFRAC="${KFRAC:-0.1}"
NPROC="${NPROC:-$(nvidia-smi -L 2>/dev/null | wc -l)}"; NPROC="${NPROC:-2}"
N_REAL="${N_REAL:-12}"; SEED="${SEED:-0}"; SEED_BASE="${SEED_BASE:-60000}"
TRAIN_TIMEOUT="${TRAIN_TIMEOUT:-21600}"             # 6 h/card cap
DRY_RUN="${DRY_RUN:-0}"
TS="$(date +%Y%m%d_%H%M%S)"; LOG="${EXP}/_run_${TS}.log"; mkdir -p "$EXP"
say(){ echo "[exp126 $(date +%H:%M:%S)] $*" | tee -a "$LOG" >&2; }
run(){ if [[ "$DRY_RUN" == "1" ]]; then say "DRY: $*"; else "$@" 2>&1 | tee -a "$LOG"; fi; }

# t(df5) baseline ckpt + its config (architecture-matched) per asset, for the score / warm-up arms
baseline_ckpt(){ case "$1" in
  spx) echo "experiments/113_gabaix_solve/results_concave_d050_seed0/checkpoint.pt experiments/113_gabaix_solve/config_concave_d050_seed0.yaml" ;;
  *)   echo "experiments/114_concave_confirm/results_${1}_concave_d050_seed0/checkpoint.pt experiments/123_driven_transient/config_${1}.yaml" ;;
esac; }

ensure_ckpt(){  # sets CKPT = concave_d050 ckpt for ASSET (inference arms); pull from R2 if absent
  local asset="$1" ckdir
  case "$asset" in
    spx) ckdir="experiments/113_gabaix_solve/results_concave_d050_seed${SEED}" ;;
    *)   ckdir="experiments/114_concave_confirm/results_${asset}_concave_d050_seed${SEED}" ;;
  esac
  CKPT="${ckdir}/checkpoint.pt"
  [[ -f "$CKPT" ]] || say "WARN: $CKPT missing — run scripts/h20_pull_from_r2.sh first"
}

shock_flags(){  # shock arm -> run_large flags
  case "$1" in
    control) ;;
    kick*) echo "--shock-step $T_SHOCK --shock-type state_kick --shock-mag ${1#kick} --shock-frac $FRAC" ;;
    temp*) echo "--shock-step $T_SHOCK --shock-type temperature_spike --shock-mag ${1#temp} --shock-dur $DUR" ;;
    liq*)  echo "--shock-step $T_SHOCK --shock-type liquidity_drop --shock-mag ${1#liq} --shock-dur $DUR" ;;
    jump*) echo "--shock-step $T_SHOCK --shock-type price_jump --shock-mag ${1#jump}" ;;
    *) say "ERROR: unknown shock arm '$1'"; exit 2 ;;
  esac
}
result_arm(){ case "$1" in temp*|liq*) echo "${1}_d${DUR}" ;; *) echo "$1" ;; esac; }  # dur in name

infer_one(){  # ckpt cfg outdir nproc n_real seed_base extra_flags...
  local ckpt="$1" cfg="$2" out="$3" nproc="$4" n_real="$5" seed_base="$6"; shift 6
  mkdir -p "$out"; say "infer $((nproc*n_real)) rollouts -> $out"
  run conda run --no-capture-output -n "$ENV" torchrun --nproc_per_node="$nproc" --standalone \
    -m ecomd.inference.run_large --ckpt "$ckpt" --config "$cfg" --out-dir "$out" \
    --save-trajectory --n-steps "$N_STEPS" --n-realizations-per-rank "$n_real" --seed-base "$seed_base" "$@"
}

train(){  # train every config_levy*.yaml in $EXP, 1 card/train, parallel up to NPROC, then wait
  local cfgs; cfgs=$(ls "$EXP"/config_levy*.yaml 2>/dev/null)
  [[ -n "$cfgs" ]] || { say "ERROR: no $EXP/config_levy*.yaml"; exit 1; }
  say "═══ TRAIN G-D1b Pareto — $(echo "$cfgs" | wc -l | tr -d ' ') configs on ${NPROC} cards (timeout=${TRAIN_TIMEOUT}s) ═══"
  local i=0 cfg
  for cfg in $cfgs; do
    local out="${EXP}/results_$(basename "${cfg%.yaml}" | sed 's/^config_//')"; mkdir -p "$out"
    local card=$(( i % NPROC )); i=$((i+1))
    say "→ train $(basename "$cfg") on card $card → $out"
    if [[ "$DRY_RUN" == "1" ]]; then say "DRY: CUDA_VISIBLE_DEVICES=$card torchrun ... --config $cfg --out-dir $out"; continue; fi
    CUDA_VISIBLE_DEVICES=$card timeout "$TRAIN_TIMEOUT" conda run --no-capture-output -n "$ENV" \
      torchrun --nproc_per_node=1 --standalone -m ecomd.training.train_distributed \
      --config "$cfg" --out-dir "$out" --resume > "${out}/_train_${TS}.log" 2>&1 &
    (( i % NPROC == 0 )) && { say "  …batch of $NPROC launched, waiting"; wait; }
  done
  [[ "$DRY_RUN" == "1" ]] || wait
  say "✓ train done (results_levy*/checkpoint.pt)"
}

score(){  # baseline t(df5) + every trained Lévy ckpt, NO shock, save-trajectory
  say "═══ SCORE (NO shock) — Pareto point: tail vs clustering ═══"
  read -r bck bcfg < <(baseline_ckpt spx)
  infer_one "$bck" "$bcfg" "${EXP}/results_baseline_tdf5/score" "$NPROC" "$N_REAL" 70000
  local d
  for d in "$EXP"/results_levy*; do
    [[ -f "$d/checkpoint.pt" ]] || { say "WARN: $d/checkpoint.pt missing (train unfinished?) — skip"; continue; }
    infer_one "$d/checkpoint.pt" "${EXP}/config_$(basename "$d").yaml" "$d/score" "$NPROC" "$N_REAL" 70100
  done
  say "✓ score done"
}

worker(){  # env: ASSET ARMS NPROC N_REAL SEED_BASE OUT_TAG [DUR]
  local asset="${ASSET:?set ASSET}" cfg="experiments/123_driven_transient/config_${ASSET}.yaml"
  [[ -f "$cfg" ]] || { say "ERROR: $cfg missing"; exit 1; }
  ensure_ckpt "$asset"; local arm rarm
  say "═══ WORKER $asset arms='${ARMS}' NPROC=${NPROC} N_REAL=${N_REAL} DUR=${DUR} tag=${OUT_TAG} ═══"
  for arm in ${ARMS}; do
    rarm="$(result_arm "$arm")"
    infer_one "$CKPT" "$cfg" "${EXP}/results_${asset}_${rarm}/${OUT_TAG}" "$NPROC" "$N_REAL" "$SEED_BASE" $(shock_flags "$arm")
  done
  say "✓ worker $asset done"
}

ablate(){  # env: ASSET ABLATE NPROC N_REAL SEED_BASE OUT_TAG  (nscan)
  local asset="${ASSET:?set ASSET}" cfg="experiments/123_driven_transient/config_${ASSET}.yaml"
  [[ -f "$cfg" ]] || { say "ERROR: $cfg missing"; exit 1; }
  ensure_ckpt "$asset"; local arm
  say "═══ ABLATE $asset arms='${ABLATE}' NPROC=${NPROC} N_REAL=${N_REAL} tag=${OUT_TAG} ═══"
  for arm in ${ABLATE}; do
    case "$arm" in nscan*) : ;; *) say "ERROR: ablate arm '$arm' not nscan*"; exit 2 ;; esac
    infer_one "$CKPT" "$cfg" "${EXP}/results_${asset}_${arm}/${OUT_TAG}" "$NPROC" "$N_REAL" "$SEED_BASE" --n-agents "${arm#nscan}"
  done
  say "✓ ablate $asset done"
}

noshock(){  # env: CKPT CONFIG RARM OUT_TAG [N_REAL]  — generic no-shock rollout (warm-up baseline, 2nd-gen)
  : "${CKPT:?set CKPT}" "${CONFIG:?set CONFIG}" "${RARM:?set RARM}"
  [[ -f "$CKPT" ]] || { say "WARN: $CKPT missing — skip"; return 0; }
  infer_one "$CKPT" "$CONFIG" "${EXP}/results_${RARM}/${OUT_TAG:-score}" "$NPROC" "$N_REAL" "${SEED_BASE:-72000}"
}

eval_all(){
  say "═══ EVAL — windowed α(t) per arm-dir + analysis scripts ═══"
  local d
  for d in "$EXP"/results_*; do
    [[ -d "$d" ]] || continue
    ls "$d"/*/trajectory_*.npz >/dev/null 2>&1 || continue
    say "── windowed: $(basename "$d") ──"
    run conda run --no-capture-output -n "$ENV" python scripts/score_transfer_law.py \
      --windows "$d" --window "$W" --stride "$STRIDE" --k-frac "$KFRAC" --shock-step "$T_SHOCK" || true
  done
  # self-contained on exp126 (avoids spx_kick6-style cross-exp arm collisions; output lands in exp126):
  local E125="experiments/125_rootcause_controllability"
  for s in aggregate_atlas_cis fit_tau_dose_law analyze_return_self_averaging; do
    [[ -f "scripts/$s.py" ]] && { say "── analysis: $s (exp126) ──"; run conda run --no-capture-output -n "$ENV" python "scripts/$s.py" --exp "$EXP" || true; }
  done
  # noise ablation: exp126 first (G-D1b trained, output here) + exp125 (G-D1a inference noise, no overlap):
  [[ -f scripts/score_noise_ablation.py ]] && { say "── analysis: score_noise_ablation (exp126+exp125) ──"; run conda run --no-capture-output -n "$ENV" python scripts/score_noise_ablation.py --exp "$EXP" "$E125" || true; }
  say "push reports:"; local BR; BR="$(git rev-parse --abbrev-ref HEAD)"
  git add "$EXP"/*.json "$EXP"/results_*/checkpoint.pt 2>/dev/null || true
  git add "$EXP"/results_*/windowed_hill_report.json "$EXP"/results_*/*/inference_*.json 2>/dev/null || true
  if git diff --cached --quiet; then say "(nothing to commit)"; else
    git commit -q -m "exp 126: full strengthening results (G-D1b Pareto + atlas/dose/warm-up + self-averaging)" \
      && { git push origin "$BR" 2>&1 | tee -a "$LOG" \
           || { git pull --rebase -q origin "$BR" && git push origin "$BR" 2>&1 | tee -a "$LOG"; }; }
  fi
}

case "${1:-}" in
  train)  train ;;
  score)  score ;;
  worker) worker ;;
  ablate) ablate ;;
  noshock) noshock ;;
  eval)   eval_all ;;
  *) echo "usage: $0 {train|score|worker|ablate|noshock|eval}  (see header; DRY_RUN=1 to preview)"; exit 2 ;;
esac
