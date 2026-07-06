#!/usr/bin/env bash
# =============================================================================
# G-D1b SALVAGE — score the 12 trained Lévy ckpts, emit the Pareto result as
# PURE TEXT for air-gap exfiltration (公网+SSH permanently down; console-only;
# only text can leave the machine room).
#
# WHY: the 12 results_levy{13,15,17,19}_spx_seed{0,1,2} models TRAINED (see
# training_log.json) but were never scored — gpu_exp125_atlas.sh eval_all skips
# dirs with no trajectory_*.npz. This script runs the missing inference+hill step,
# folds everything into noise_ablation_cost.json, then prints the result + a CRC
# to stdout so the operator can transcribe the TEXT out of the machine room.
#
# SELF-CONTAINED — no network needed. Run on H20 from the repo root:
#   cd /AI4S/Users/howardwang/h204/ecophys
#   bash scripts/gd1b_score_and_emit.sh            # ~2h on 8 cards
#   # then read everything between the ███ markers off the screen / save stdout
#
# Resilience: a missing/failed ckpt is logged and SKIPPED — the Pareto curve is
# still emitted with whatever points survived. Partial result > no result.
# =============================================================================
set -uo pipefail
ENV="${ECOPHYS_ENV:-ecophys}"
EXP="experiments/126_strengthen_workshops"
W="${W:-500}"; STRIDE="${STRIDE:-100}"; KFRAC="${KFRAC:-0.1}"; T_SHOCK="${T_SHOCK:-3000}"
N_STEPS="${N_STEPS:-8000}"; N_REAL="${N_REAL:-4}"; NPROC="${NPROC:-8}"
SEED_BASE=60000

# repo root
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

say(){ printf '\n── %s ──\n' "$*"; }

score_one(){  # <model_dir> <config_yaml>
  local d="$1" cfg="$2" name ckpt
  name="$(basename "$d")"
  ckpt="$(ls "$d"/checkpoint*.pt 2>/dev/null | head -1)"
  if [[ -z "$ckpt" ]]; then say "[$name] NO ckpt — SKIP"; echo "SKIP no_ckpt $name" >>"$EXP/_gd1b_skip.log"; return; fi
  if [[ -f "$d/windowed_hill_report.json" ]]; then say "[$name] already scored — reuse"; return; fi
  say "[$name] infer  ckpt=$ckpt  (nproc=$NPROC n_real=$N_REAL steps=$N_STEPS)"
  conda run --no-capture-output -n "$ENV" torchrun --nproc_per_node="$NPROC" \
    -m ecomd.inference.run_large --ckpt "$ckpt" --config "$cfg" \
    --out-dir "$d/score" --save-trajectory --n-steps "$N_STEPS" \
    --n-realizations-per-rank "$N_REAL" --seed-base "$SEED_BASE" \
    || { say "[$name] infer FAILED — SKIP"; echo "FAIL infer $name" >>"$EXP/_gd1b_skip.log"; return; }
  say "[$name] windowed-hill"
  conda run --no-capture-output -n "$ENV" python scripts/score_transfer_law.py \
    --windows "$d" --window "$W" --stride "$STRIDE" --k-frac "$KFRAC" --shock-step "$T_SHOCK" \
    || { say "[$name] hill FAILED — SKIP"; echo "FAIL hill $name" >>"$EXP/_gd1b_skip.log"; return; }
  SEED_BASE=$((SEED_BASE+100))
}

say "═══ G-D1b SALVAGE — git=$(git rev-parse --short HEAD 2>/dev/null) env=$ENV nproc=$NPROC ═══"
: > "$EXP/_gd1b_skip.log"

# 12 trained Lévy models (config carries noise_dist=levy + α; scoring uses the
# trained dynamics under their own training-noise regime — the G-D1b test).
for a in 13 15 17 19; do for s in 0 1 2; do
  score_one "$EXP/results_levy${a}_spx_seed${s}" "$EXP/config_levy${a}_spx_seed${s}.yaml"
done; done

# baseline_tdf5 is the Pareto anchor (already scored in the prior run; reused if present).
if [[ ! -f "$EXP/results_baseline_tdf5/windowed_hill_report.json" ]]; then
  say "baseline_tdf5 not scored — attempting (needs config_baseline_tdf5.yaml + ckpt)"
  [[ -f "$EXP/config_baseline_tdf5.yaml" ]] && score_one "$EXP/results_baseline_tdf5" "$EXP/config_baseline_tdf5.yaml"
fi

# Fold all windowed_hill_report.json + inference_rank_*.json into the Pareto curve.
say "═══ aggregate → noise_ablation_cost.json ═══"
conda run --no-capture-output -n "$ENV" python scripts/score_noise_ablation.py --exp "$EXP" \
  || say "aggregate FAILED (will still try to emit whatever exists)"

# =============================================================================
# EMIT AS PURE TEXT + CRC32 — this is the air-gap exfil payload.
# Operator: copy EVERYTHING between the ▛▀▜ ... ▙▀▟ markers off the screen.
# =============================================================================
PAYLOAD="$EXP/noise_ablation_cost.json"
if [[ ! -f "$PAYLOAD" ]]; then
  say "!!! $PAYLOAD missing — nothing to emit"; exit 1
fi

emit_text(){
  echo "### HEADER  git=$(git rev-parse --short HEAD 2>/dev/null)  date=$(date -u +%FT%TZ 2>/dev/null || echo NA)"
  echo "### COMPACT PARETO TABLE (the actual result — 13 lines):"
  conda run --no-capture-output -n "$ENV" python - <<'PY'
import json
d=json.load(open("experiments/126_strengthen_workshops/noise_ablation_cost.json"))
def row(n,r):
    if not r: return f"{n:16s} MISSING"
    return (f"{n:16s} aED={r.get('steady_alphaED')}  hill={r.get('hill_tail_index')}  "
            f"acf2={r.get('acf_squared_returns')}  lev={r.get('leverage_effect')}  n={r.get('n_seeds')}")
tm=d.get("G-D1b_trained_models",{})
print(row("baseline_tdf5", tm.get("baseline_tdf5")))
for k,v in sorted(d.get("G-D1b_pareto_curve_by_alpha",{}).items()):
    print(row(k,v))
PY
  echo "### FULL JSON:"
  cat "$PAYLOAD"
  echo "### CRC32 (verify on Mac):"
  conda run --no-capture-output -n "$ENV" python -c "import zlib;print(format(zlib.crc32(open('$PAYLOAD','rb').read())&0xffffffff,'08x'))"
}

{
  echo "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜"
  echo "▌ G-D1b PARETO PAYLOAD — copy everything between the markers ▐"
  echo "▙▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▟"
  emit_text
  echo "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀ END PAYLOAD ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜"
} | tee "$EXP/_gd1b_payload.txt"

say "DONE. Exfil: copy _gd1b_payload.txt text out. Skips logged in $EXP/_gd1b_skip.log"
