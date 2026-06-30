#!/usr/bin/env bash
# exp 126 — workshop-strengthening suite (PREREG.md). NO data buy. Fleet: 8card + 2card-b + 2card-orch.
# Completes/strengthens exp 125: the trained-Lévy Route-A point (G-D1b), the atlas + dose law on the
# two missing assets, a dur contrast, and the re-pre-registered return-tail self-averaging control.
#
# Reuses concave_d050 checkpoints (5 assets, pulled from R2) for all INFERENCE arms; TRAINS only G-D1b.
# All steady-state numbers use a warm-up discard downstream (burn-in fix, see exp 125 PREREG).
#
# MODES (set env vars; see each fn header)
#   train   : G-D1b — train spx with Lévy bath from the exp126 config_levy*_spx_seed*.yaml (1 card each)
#   score   : roll out each trained-Lévy ckpt + the t(df5) baseline (NO shock) → 11 facts + windowed α
#   worker  : shock arms (control/kickM/tempM/liqD) for $ASSET — atlas + dose completion (G-B'/G-C')
#   ablate  : root-cause arms (nscanN) NO shock, save-trajectory — return self-averaging (H-D2')
#   eval    : windowed α(t) + the 4 analysis scripts (CIs / τ-law / noise-cost / return-selfavg) + push
#
# PER-NODE EXAMPLES (Option B — one per machine; robust, no driver SSH)
#   # 8-card: G-D1b train (3 configs on 3 cards) then score the 4 models
#   NPROC=8 bash scripts/gpu_exp126_strengthen.sh train
#   bash scripts/gpu_exp126_strengthen.sh score
#   # 8-card or 2-card: atlas completion (dur=20 primary + dur=1 contrast)
#   ASSET=gold  ARMS="temp3 temp5 liq3 liq5" NPROC=8 N_REAL=3 DUR=20 SEED_BASE=60000 OUT_TAG=atlas_dur20 bash scripts/gpu_exp126_strengthen.sh worker
#   ASSET=spx   ARMS="temp3 temp5 liq3 liq5" NPROC=8 N_REAL=3 DUR=1  SEED_BASE=61000 OUT_TAG=atlas_dur1  bash scripts/gpu_exp126_strengthen.sh worker
#   # 2-card: dose law on the missing assets
#   ASSET=gold ARMS="kick0.05 kick0.1 kick0.2 kick0.5 kick1 kick2 kick6 kick12" NPROC=2 N_REAL=10 SEED_BASE=62000 OUT_TAG=dose bash scripts/gpu_exp126_strengthen.sh worker
#   # 2-card: return self-averaging (spx+btc N-scan, save-trajectory for the vol-standardized control)
#   ASSET=spx ABLATE="nscan100 nscan300 nscan1000 nscan3000 nscan10000 nscan30000" NPROC=2 N_REAL=10 SEED_BASE=63000 OUT_TAG=selfavg bash scripts/gpu_exp126_strengthen.sh ablate
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$REPO_ROOT"
export PATH=/root/miniconda3/bin:${PATH:-}          # H20 conda not on non-interactive PATH
ENV="${ECOPHYS_ENV:-ecophys}"
EXP="experiments/126_strengthen_workshops"
N_STEPS="${N_STEPS:-8000}"; T_SHOCK="${T_SHOCK:-3000}"; FRAC="${FRAC:-0.1}"; DUR="${DUR:-20}"
W="${W:-500}"; STRIDE="${STRIDE:-100}"; KFRAC="${KFRAC:-0.1}"
NPROC="${NPROC:-$(nvidia-smi -L 2>/dev/null | wc -l)}"; NPROC="${NPROC:-2}"
TRAIN_TIMEOUT="${TRAIN_TIMEOUT:-14400}"             # 4 h/card, matches scripts/_h20_1_batch.sh
DRY_RUN="${DRY_RUN:-0}"; SEED="${SEED:-0}"
TS="$(date +%Y%m%d_%H%M%S)"; LOG="${EXP}/_run_${TS}.log"; mkdir -p "$EXP"
say(){ echo "[exp126 $(date +%H:%M:%S)] $*" | tee -a "$LOG" >&2; }
run(){ if [[ "$DRY_RUN" == "1" ]]; then say "DRY: $*"; else "$@" 2>&1 | tee -a "$LOG"; fi; }

# the trained-Lévy configs to build (G-D1b). dir name = config name w/o the "config_" prefix.
LEVY_CONFIGS="${LEVY_CONFIGS:-config_levy17_spx_seed0 config_levy17_spx_seed1 config_levy15_spx_seed0}"

ensure_ckpt(){  # sets CKPT = concave_d050 ckpt for ASSET (inference arms); pull from R2 if absent
  local asset="$1" ckdir
  case "$asset" in
    spx) ckdir="experiments/113_gabaix_solve/results_concave_d050_seed${SEED}" ;;
    *)   ckdir="experiments/114_concave_confirm/results_${asset}_concave_d050_seed${SEED}" ;;
  esac
  CKPT="${ckdir}/checkpoint.pt"
  [[ -f "$CKPT" ]] || say "WARN: $CKPT missing — run scripts/h20_pull_from_r2.sh first"
}

shock_flags(){  # shock arm → run_large flags (same mapping as exp 125)
  case "$1" in
    control) ;;
    kick*) echo "--shock-step $T_SHOCK --shock-type state_kick --shock-mag ${1#kick} --shock-frac $FRAC" ;;
    temp*) echo "--shock-step $T_SHOCK --shock-type temperature_spike --shock-mag ${1#temp} --shock-dur $DUR" ;;
    liq*)  echo "--shock-step $T_SHOCK --shock-type liquidity_drop --shock-mag ${1#liq} --shock-dur $DUR" ;;
    jump*) echo "--shock-step $T_SHOCK --shock-type price_jump --shock-mag ${1#jump}" ;;
    *) say "ERROR: unknown shock arm '$1'"; exit 2 ;;
  esac
}
ablate_flags(){ case "$1" in nscan*) echo "--n-agents ${1#nscan}" ;; *) say "ERROR: unknown ablate arm '$1'"; exit 2 ;; esac; }

infer_one(){  # ckpt cfg outdir nproc n_real seed_base extra_flags...
  local ckpt="$1" cfg="$2" out="$3" nproc="$4" n_real="$5" seed_base="$6"; shift 6
  mkdir -p "$out"; say "infer $((nproc*n_real)) rollouts → $out (ckpt=$(basename "$(dirname "$ckpt")"))"
  run conda run --no-capture-output -n "$ENV" torchrun --nproc_per_node="$nproc" --standalone \
    -m ecomd.inference.run_large --ckpt "$ckpt" --config "$cfg" --out-dir "$out" \
    --save-trajectory --n-steps "$N_STEPS" --n-realizations-per-rank "$n_real" --seed-base "$seed_base" "$@"
}

train(){  # G-D1b: train each levy config on its own card (1 card/train), parallel, then wait
  say "═══ TRAIN G-D1b — configs='${LEVY_CONFIGS}' on ${NPROC} cards (1 card/train, timeout=${TRAIN_TIMEOUT}s) ═══"
  local i=0 cfgname
  for cfgname in ${LEVY_CONFIGS}; do
    local cfg="${EXP}/${cfgname}.yaml" out="${EXP}/results_${cfgname#config_}"
    [[ -f "$cfg" ]] || { say "ERROR: $cfg missing"; exit 1; }
    local card=$(( i % NPROC )); i=$((i+1)); mkdir -p "$out"
    say "→ train $cfgname on card $card → $out"
    if [[ "$DRY_RUN" == "1" ]]; then say "DRY: CUDA_VISIBLE_DEVICES=$card torchrun ... train_distributed --config $cfg --out-dir $out"; continue; fi
    CUDA_VISIBLE_DEVICES=$card timeout "$TRAIN_TIMEOUT" conda run --no-capture-output -n "$ENV" \
      torchrun --nproc_per_node=1 --standalone -m ecomd.training.train_distributed \
      --config "$cfg" --out-dir "$out" --resume > "${out}/_train_${TS}.log" 2>&1 &
  done
  [[ "$DRY_RUN" == "1" ]] || { say "waiting for $(jobs -p | wc -l) training jobs…"; wait; }
  say "✓ train done (check results_*/checkpoint.pt + _train_*.log)"
}

score(){  # roll out each trained-Lévy ckpt + the t(df5) baseline, NO shock, save trajectory
  say "═══ SCORE trained models (NO shock) — Pareto point: tail vs clustering ═══"
  # baseline = the as-shipped concave_d050 (Student-t df5), under its own training config
  infer_one "experiments/113_gabaix_solve/results_concave_d050_seed0/checkpoint.pt" \
            "experiments/113_gabaix_solve/config_concave_d050_seed0.yaml" \
            "${EXP}/results_baseline_tdf5/score" "$NPROC" "${N_REAL:-3}" 70000
  local cfgname
  for cfgname in ${LEVY_CONFIGS}; do
    local ck="${EXP}/results_${cfgname#config_}/checkpoint.pt"
    [[ -f "$ck" ]] || { say "WARN: $ck missing (train not finished?) — skip"; continue; }
    infer_one "$ck" "${EXP}/${cfgname}.yaml" "${EXP}/results_${cfgname#config_}/score" "$NPROC" "${N_REAL:-3}" 70100
  done
  say "✓ score done"
}

worker(){  # env: ASSET ARMS NPROC N_REAL SEED_BASE OUT_TAG [DUR]  — atlas + dose completion
  local asset="${ASSET:?set ASSET}" cfg="experiments/123_driven_transient/config_${ASSET}.yaml"
  [[ -f "$cfg" ]] || { say "ERROR: $cfg missing"; exit 1; }
  ensure_ckpt "$asset"; local arm
  say "═══ WORKER $asset arms='${ARMS}' NPROC=${NPROC} N_REAL=${N_REAL} DUR=${DUR} tag=${OUT_TAG} ═══"
  for arm in ${ARMS}; do
    infer_one "$CKPT" "$cfg" "${EXP}/results_${asset}_${arm}/${OUT_TAG}" "$NPROC" "${N_REAL}" "${SEED_BASE}" $(shock_flags "$arm")
  done
  say "✓ worker $asset done"
}

ablate(){  # env: ASSET ABLATE NPROC N_REAL SEED_BASE OUT_TAG  — return self-averaging N-scan
  local asset="${ASSET:?set ASSET}" cfg="experiments/123_driven_transient/config_${ASSET}.yaml"
  [[ -f "$cfg" ]] || { say "ERROR: $cfg missing"; exit 1; }
  ensure_ckpt "$asset"; local arm
  say "═══ ABLATE $asset arms='${ABLATE}' NPROC=${NPROC} N_REAL=${N_REAL} tag=${OUT_TAG} ═══"
  for arm in ${ABLATE}; do
    infer_one "$CKPT" "$cfg" "${EXP}/results_${asset}_${arm}/${OUT_TAG}" "$NPROC" "${N_REAL}" "${SEED_BASE}" $(ablate_flags "$arm")
  done
  say "✓ ablate $asset done"
}

eval_all(){
  say "═══ EVAL — windowed α(t) + analysis scripts ═══"
  local d
  for d in "$EXP"/results_*; do
    [[ -d "$d" ]] || continue
    ls "$d"/*/trajectory_*.npz >/dev/null 2>&1 || continue
    say "── windowed: $(basename "$d") ──"
    run conda run --no-capture-output -n "$ENV" python scripts/score_transfer_law.py \
      --windows "$d" --window "$W" --stride "$STRIDE" --k-frac "$KFRAC" --shock-step "$T_SHOCK" || true
  done
  local s
  for s in aggregate_atlas_cis.py fit_tau_dose_law.py score_noise_ablation.py analyze_return_self_averaging.py; do
    if [[ -f "scripts/$s" ]]; then
      say "── analysis: $s (--exp 125 + 126) ──"
      run conda run --no-capture-output -n "$ENV" python "scripts/$s" --exp experiments/125_rootcause_controllability "$EXP" || true
    else say "  (scripts/$s missing)"; fi
  done
  say "push reports:"; local BR; BR="$(git rev-parse --abbrev-ref HEAD)"
  git add "$EXP"/*.json "$EXP"/results_*/score "$EXP"/results_*/checkpoint.pt 2>/dev/null || true
  git add "$EXP"/results_*/*/windowed_hill_report.json 2>/dev/null || true
  if git diff --cached --quiet; then say "(nothing to commit)"; else
    git commit -q -m "exp 126: workshop-strengthening results (G-D1b trained-Lévy + atlas/dose completion + return self-averaging)" \
      && { git push origin "$BR" 2>&1 | tee -a "$LOG" \
           || { git pull --rebase -q origin "$BR" && git push origin "$BR" 2>&1 | tee -a "$LOG"; }; }
  fi
}

case "${1:-}" in
  train)  train ;;
  score)  score ;;
  worker) worker ;;
  ablate) ablate ;;
  eval)   eval_all ;;
  *) echo "usage: $0 {train|score|worker|ablate|eval}  (see header for env vars; DRY_RUN=1 to preview)"; exit 2 ;;
esac
