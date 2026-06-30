#!/usr/bin/env bash
# exp 126 — ORCHESTRATOR (2 boxes × 2 cards = 4 cards). Run this ON one 2-card box; it SSHes to the
# OTHER 2-card box. FULL scope, sized for ~a week unattended (no compute/time saving). Both batches run
# detached with nohup, so `launch` returns immediately — poll with `status`.
#
# Node map from scripts/machines.local.json (keys host/user/root[/ssh_port]):
#   - the box you run this on      = "localhost"  (2 cards; OWNS training + its share)
#   - NODE_2CARD (default: gpu2b)  = the other 2-card box (SSH target; atlas + its share)
# Override: NODE_2CARD=h20_3 bash scripts/gpu_exp126_orchestrate_2x2.sh launch
#
# WORK SPLIT (both ~3–3.5 days on 2 cards; finish well within a week)
#   localhost : G-D1b train (12 Lévy cfgs) → score (13 models) → atlas TEMP (5 assets × 3 mag × 3 dur)
#               → dose (5 assets, dense kick) → self-averaging N-scan (spx, ndx)
#   NODE_2CARD: atlas LIQ (5 assets × 3 mag × 3 dur) + price_jump contrast → self-averaging (btc, gold,
#               eurusd) → warm-up baseline-family arms (spx, btc, no-shock)
#   (G-E 2nd-generator is a separate documented block — see WORKPLAN.md — not auto-wired.)
#
# USAGE
#   DRY=1 bash scripts/gpu_exp126_orchestrate_2x2.sh launch   # preview, no SSH/GPU
#   bash scripts/gpu_exp126_orchestrate_2x2.sh launch         # sync + launch both boxes detached
#   bash scripts/gpu_exp126_orchestrate_2x2.sh status         # ckpts/npz counts + log tails
#   bash scripts/gpu_exp126_orchestrate_2x2.sh gather         # rsync remote results back
#   bash scripts/gpu_exp126_orchestrate_2x2.sh eval           # windowed + analysis + push
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$REPO_ROOT"
export PATH=/root/miniconda3/bin:${PATH:-}
ENV="${ECOPHYS_ENV:-ecophys}"
EXP="experiments/126_strengthen_workshops"
BR="${BR:-$(git rev-parse --abbrev-ref HEAD)}"
DRY="${DRY:-0}"
MACH_FILE="scripts/machines.local.json"
NODE_2CARD="${NODE_2CARD:-gpu2b}"
ASSETS="${ASSETS:-spx ndx btcusdt gold eurusd}"
KICKS="kick0.05 kick0.1 kick0.2 kick0.5 kick1 kick2 kick6 kick12"
TS="$(date +%Y%m%d_%H%M%S)"; LOG="${EXP}/_orch_${TS}.log"; mkdir -p "$EXP"
say(){ echo "[orch126 $(date +%H:%M:%S)] $*" | tee -a "$LOG" >&2; }
mach(){ python3 -c "import json;print(json.load(open('$MACH_FILE'))['$1'].get('$2',''))" 2>/dev/null; }
D="scripts/gpu_exp126_strengthen.sh"

# ── localhost batch (this box owns training; ckpts stay local for score) ──
batch_local_str(){ cat <<EOF
set -e; export PATH=/root/miniconda3/bin:\$PATH; cd "$REPO_ROOT";
git pull -q origin $BR || true; bash scripts/h20_pull_from_r2.sh || true;
NPROC=2 ECOPHYS_ENV=$ENV bash $D train;
N_REAL=16 NPROC=2 ECOPHYS_ENV=$ENV bash $D score;
for A in $ASSETS; do for DUR in 1 20 50; do
  ASSET=\$A ARMS="temp3 temp5 temp8" DUR=\$DUR NPROC=2 N_REAL=12 SEED_BASE=60000 OUT_TAG=atlas ECOPHYS_ENV=$ENV bash $D worker;
done; done;
for A in $ASSETS; do
  ASSET=\$A ARMS="control $KICKS" NPROC=2 N_REAL=12 SEED_BASE=62000 OUT_TAG=dose ECOPHYS_ENV=$ENV bash $D worker;
done;
for A in spx ndx; do
  ASSET=\$A ABLATE="nscan100 nscan300 nscan1000 nscan3000 nscan10000 nscan30000 nscan60000 nscan100000" NPROC=2 N_REAL=16 SEED_BASE=63000 OUT_TAG=selfavg ECOPHYS_ENV=$ENV bash $D ablate;
done;
echo EXP126_LOCAL_DONE
EOF
}
# ── remote NODE_2CARD batch ──
batch_remote_str(){ cat <<EOF
set -e; export PATH=/root/miniconda3/bin:\$PATH; cd "$1";
git pull -q origin $BR || true; bash scripts/h20_pull_from_r2.sh || true;
for A in $ASSETS; do for DUR in 1 20 50; do
  ASSET=\$A ARMS="liq3 liq5 liq10" DUR=\$DUR NPROC=2 N_REAL=12 SEED_BASE=61000 OUT_TAG=atlas ECOPHYS_ENV=$ENV bash $D worker;
done; done;
for A in $ASSETS; do
  ASSET=\$A ARMS="jump6" NPROC=2 N_REAL=12 SEED_BASE=61500 OUT_TAG=atlas ECOPHYS_ENV=$ENV bash $D worker;
done;
for A in btcusdt gold eurusd; do
  ASSET=\$A ABLATE="nscan100 nscan300 nscan1000 nscan3000 nscan10000 nscan30000 nscan60000 nscan100000" NPROC=2 N_REAL=16 SEED_BASE=64000 OUT_TAG=selfavg ECOPHYS_ENV=$ENV bash $D ablate;
done;
CKPT=experiments/113_gabaix_solve/results_baseline_seed0/checkpoint.pt CONFIG=experiments/113_gabaix_solve/config_baseline_seed0.yaml RARM=spx_warmup_baseline OUT_TAG=score N_REAL=20 SEED_BASE=72000 NPROC=2 ECOPHYS_ENV=$ENV bash $D noshock || true;
CKPT=experiments/114_concave_confirm/results_btcusdt_baseline_seed0/checkpoint.pt CONFIG=experiments/114_concave_confirm/config_btcusdt_baseline_seed0.yaml RARM=btcusdt_warmup_baseline OUT_TAG=score N_REAL=20 SEED_BASE=72100 NPROC=2 ECOPHYS_ENV=$ENV bash $D noshock || true;
echo EXP126_REMOTE_DONE
EOF
}

launch(){
  [[ -f "$MACH_FILE" || "$DRY" == "1" ]] || { say "ERROR: $MACH_FILE missing on the orchestrator"; exit 1; }
  say "═══ exp126 LAUNCH (branch $BR) — localhost(2c, owns train) + remote=$NODE_2CARD(2c) ═══"
  say "1) sync orchestrator code/ckpts"
  if [[ "$DRY" == "1" ]]; then say "DRY: git pull + h20_pull_from_r2"; else
    { git pull -q origin "$BR" || true; bash scripts/h20_pull_from_r2.sh || true; } 2>&1 | tee -a "$LOG"; fi
  # 2) remote box (SSH, detached)
  local h u r p; h="$(mach "$NODE_2CARD" host)"; u="$(mach "$NODE_2CARD" user)"
  r="$(mach "$NODE_2CARD" root)"; p="$(mach "$NODE_2CARD" ssh_port)"; p="${p:-22}"
  local rlog="${r}/${EXP}/_node_${NODE_2CARD}_${TS}.log"
  say "2) launch remote batch on $NODE_2CARD ($u@$h:$p) — detached → $rlog"
  if [[ "$DRY" == "1" ]]; then say "DRY ssh $u@$h -p $p 'nohup bash -lc <remote-batch> >$rlog 2>&1 &'";
  elif [[ -n "$h" && -n "$u" && -n "$r" ]]; then
    batch_remote_str "$r" | ssh -p "$p" -o StrictHostKeyChecking=accept-new "$u@$h" \
      "mkdir -p ${r}/${EXP}; nohup bash -lc \"\$(cat)\" >'$rlog' 2>&1 & echo launched PID \$! on \$(hostname)" \
      2>&1 | tee -a "$LOG"
  else say "ERROR: machines.local.json['$NODE_2CARD'] missing host/user/root"; fi
  # 3) localhost box (nohup, detached) — owns training
  local llog="${EXP}/_node_localhost_${TS}.log"
  say "3) launch localhost batch (train+score+atlas-temp+dose+selfavg) — detached → $llog"
  if [[ "$DRY" == "1" ]]; then say "DRY nohup bash -lc <local-batch> >$llog 2>&1 &"; say "$(batch_local_str | head -6)";
  else nohup bash -lc "$(batch_local_str)" >"$llog" 2>&1 & say "launched local PID $! on $(hostname)"; fi
  say "✓ both batches launched detached. Poll: bash $0 status"
  say "  NB: ~3–3.5 days/box. gather only after BOTH print *_DONE. G-E is a separate manual block (WORKPLAN)."
}

status(){
  say "═══ STATUS ═══"
  local h u r p; h="$(mach "$NODE_2CARD" host)"; u="$(mach "$NODE_2CARD" user)"
  r="$(mach "$NODE_2CARD" root)"; p="$(mach "$NODE_2CARD" ssh_port)"; p="${p:-22}"
  say "── remote $NODE_2CARD ($u@$h) ──"
  if [[ "$DRY" == "1" ]]; then say "DRY: ssh status"; else
    ssh -p "$p" "$u@$h" "cd $r; echo -n '  npz: '; ls ${EXP}/results_*/*/trajectory_*.npz 2>/dev/null | wc -l; tail -2 ${EXP}/_node_${NODE_2CARD}_*.log 2>/dev/null" 2>&1 | tee -a "$LOG"; fi
  say "── localhost ──"
  echo -n "  Lévy ckpts: "; ls ${EXP}/results_levy*/checkpoint.pt 2>/dev/null | wc -l
  echo -n "  npz: "; ls ${EXP}/results_*/*/trajectory_*.npz 2>/dev/null | wc -l
  tail -2 ${EXP}/_node_localhost_*.log 2>/dev/null
}

gather(){
  say "═══ GATHER remote → orchestrator ═══"
  local h u r p; h="$(mach "$NODE_2CARD" host)"; u="$(mach "$NODE_2CARD" user)"
  r="$(mach "$NODE_2CARD" root)"; p="$(mach "$NODE_2CARD" ssh_port)"; p="${p:-22}"
  if [[ "$DRY" == "1" ]]; then say "DRY: rsync $u@$h:$r/${EXP}/results_* → ${EXP}/"; else
    rsync -az -e "ssh -p $p" "$u@$h:$r/${EXP}/results_*" "${EXP}/" 2>&1 | tee -a "$LOG"; fi
  say "✓ gathered. Now: bash $0 eval"
}

eval_all(){ if [[ "$DRY" == "1" ]]; then say "DRY: bash $D eval"; else bash "$D" eval 2>&1 | tee -a "$LOG"; fi; }

case "${1:-}" in
  launch) launch ;;
  status) status ;;
  gather) gather ;;
  eval)   eval_all ;;
  *) echo "usage: $0 {launch|status|gather|eval}   (run ON one 2-card box; DRY=1 to preview)"; exit 2 ;;
esac
