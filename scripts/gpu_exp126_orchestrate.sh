#!/usr/bin/env bash
# exp 126 — ORCHESTRATOR. Run this ON THE 2-CARD ORCHESTRATOR BOX. It SSHes to the 8-card box and the
# other 2-card box, syncs code+ckpts, launches their batches detached (nohup), runs its own local
# batch, then gathers + evals. Same topology/skeleton as scripts/gpu_exp125_orchestrate.sh.
# (The 4-card box is still DOWN; this suite is sized for 8 + 2 + 2 = 12 cards.)
#
# Node map is read from scripts/machines.local.json. Required keys per node: host/user/root[/ssh_port].
#   - the box you run this on        = "localhost" (2 cards; orchestrator + spx return-selfavg)
#   - NODE_8CARD  (default: gpu8)    = the 8-card box (G-D1b train+score + atlas dur completion)
#   - NODE_2CARD  (default: gpu2b)   = the other 2-card box (gold/eurusd dose + btc return-selfavg)
# Override: NODE_8CARD=h20_1 NODE_2CARD=h20_3 bash scripts/gpu_exp126_orchestrate.sh launch
#
# USAGE
#   DRY=1 bash scripts/gpu_exp126_orchestrate.sh launch   # echo every action, no SSH/GPU
#   bash scripts/gpu_exp126_orchestrate.sh launch         # sync + launch all 3 nodes
#   bash scripts/gpu_exp126_orchestrate.sh status         # tail logs + count ckpts/npz on each node
#   bash scripts/gpu_exp126_orchestrate.sh gather         # rsync remote results back here
#   bash scripts/gpu_exp126_orchestrate.sh eval           # windowed + analysis scripts + push
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$REPO_ROOT"
export PATH=/root/miniconda3/bin:${PATH:-}
ENV="${ECOPHYS_ENV:-ecophys}"
EXP="experiments/126_strengthen_workshops"
BR="${BR:-$(git rev-parse --abbrev-ref HEAD)}"
DRY="${DRY:-0}"
MACH_FILE="scripts/machines.local.json"
NODE_8CARD="${NODE_8CARD:-gpu8}"; NODE_2CARD="${NODE_2CARD:-gpu2b}"
TS="$(date +%Y%m%d_%H%M%S)"; LOG="${EXP}/_orch_${TS}.log"; mkdir -p "$EXP"
say(){ echo "[orch126 $(date +%H:%M:%S)] $*" | tee -a "$LOG" >&2; }
mach(){ python3 -c "import json;print(json.load(open('$MACH_FILE'))['$1'].get('$2',''))" 2>/dev/null; }
do_(){ if [[ "$DRY" == "1" ]]; then say "DRY: $*"; else eval "$*" 2>&1 | tee -a "$LOG"; fi; }
D="scripts/gpu_exp126_strengthen.sh"

# ── 8-card: G-D1b train+score (long pole) + atlas dur completion (dur=20 missing assets, dur=1 contrast)
batch_8card(){ cat <<EOF
set -e; export PATH=/root/miniconda3/bin:\$PATH; cd "$1";
git pull -q origin $BR || true; bash scripts/h20_pull_from_r2.sh || true;
NPROC=8 ECOPHYS_ENV=$ENV bash $D train;
N_REAL=3 NPROC=8 ECOPHYS_ENV=$ENV bash $D score;
for A in gold eurusd; do ASSET=\$A ARMS="control kick6 temp3 temp5 liq3 liq5" NPROC=8 N_REAL=3 DUR=20 SEED_BASE=60000 OUT_TAG=atlas_dur20 ECOPHYS_ENV=$ENV bash $D worker; done;
for A in spx ndx btcusdt gold eurusd; do ASSET=\$A ARMS="temp3 temp5 liq3 liq5" NPROC=8 N_REAL=3 DUR=1 SEED_BASE=61000 OUT_TAG=atlas_dur1 ECOPHYS_ENV=$ENV bash $D worker; done;
echo EXP126_8CARD_DONE
EOF
}
# ── other 2-card: dose law on the two missing assets + btc return self-averaging
batch_2card_b(){ cat <<EOF
set -e; export PATH=/root/miniconda3/bin:\$PATH; cd "$1";
git pull -q origin $BR || true; bash scripts/h20_pull_from_r2.sh || true;
for A in gold eurusd; do ASSET=\$A ARMS="kick0.05 kick0.1 kick0.2 kick0.5 kick1 kick2 kick6 kick12" NPROC=2 N_REAL=10 SEED_BASE=62000 OUT_TAG=dose ECOPHYS_ENV=$ENV bash $D worker; done;
ASSET=btcusdt ABLATE="nscan100 nscan300 nscan1000 nscan3000 nscan10000 nscan30000" NPROC=2 N_REAL=12 SEED_BASE=63000 OUT_TAG=selfavg ECOPHYS_ENV=$ENV bash $D ablate;
echo EXP126_2CARDB_DONE
EOF
}
# ── orchestrator's OWN 2 cards: spx return self-averaging (save-trajectory for the vol-standardized control)
batch_local(){
  do_ "ASSET=spx ABLATE='nscan100 nscan300 nscan1000 nscan3000 nscan10000 nscan30000' NPROC=2 N_REAL=12 SEED_BASE=64000 OUT_TAG=selfavg ECOPHYS_ENV=$ENV bash $D ablate"
}

ssh_to(){  # $1 = node key; runs stdin batch detached with nohup
  local key="$1" h u r p; h="$(mach "$key" host)"; u="$(mach "$key" user)"
  r="$(mach "$key" root)"; p="$(mach "$key" ssh_port)"; p="${p:-22}"
  [[ -n "$h" && -n "$u" && -n "$r" ]] || { say "ERROR: machines.local.json['$key'] missing host/user/root"; return 1; }
  local cmd; cmd="$(cat)"
  local rlog="${r}/${EXP}/_node_${key}_${TS}.log"
  say "→ launch on $key ($u@$h:$p), repo=$r, log=$rlog"
  if [[ "$DRY" == "1" ]]; then say "DRY ssh $u@$h -p $p \"nohup bash -lc '<batch>' >$rlog 2>&1 &\""; return 0; fi
  ssh -p "$p" -o StrictHostKeyChecking=accept-new "$u@$h" \
    "mkdir -p ${r}/${EXP}; nohup bash -lc $(printf '%q' "$cmd") >'$rlog' 2>&1 & echo launched PID \$! on \$(hostname)" \
    2>&1 | tee -a "$LOG"
}

launch(){
  [[ -f "$MACH_FILE" || "$DRY" == "1" ]] || { say "ERROR: $MACH_FILE missing on the orchestrator"; exit 1; }
  say "═══ exp126 LAUNCH (branch $BR) — 8card=$NODE_8CARD  2card-b=$NODE_2CARD  local=2card-orch ═══"
  say "1) sync orchestrator code/ckpts"
  do_ "git pull -q origin $BR || true; bash scripts/h20_pull_from_r2.sh || true"
  say "2) launch 8-card batch (G-D1b train+score + atlas dur completion) — detached"
  batch_8card "$(mach "$NODE_8CARD" root)" | ssh_to "$NODE_8CARD"
  say "3) launch other-2-card batch (gold/eurusd dose + btc return-selfavg) — detached"
  batch_2card_b "$(mach "$NODE_2CARD" root)" | ssh_to "$NODE_2CARD"
  say "4) run orchestrator-local batch (spx return-selfavg) on these 2 cards"
  batch_local
  say "✓ all batches launched. Poll with: bash $0 status   (remote runs are detached/nohup)"
  say "  NB: G-D1b training (8-card) is the long pole (~4-5 h); gather only after EXP126_8CARD_DONE."
}

status(){
  say "═══ STATUS ═══"; local key r h u p
  for key in "$NODE_8CARD" "$NODE_2CARD"; do
    h="$(mach "$key" host)"; u="$(mach "$key" user)"; r="$(mach "$key" root)"; p="$(mach "$key" ssh_port)"; p="${p:-22}"
    say "── $key ($u@$h) ──"
    do_ "ssh -p $p $u@$h 'cd $r; echo -n \"  ckpts: \"; ls ${EXP}/results_levy*/checkpoint.pt 2>/dev/null | wc -l; echo -n \"  npz: \"; ls ${EXP}/results_*/*/trajectory_*.npz 2>/dev/null | wc -l; tail -2 ${EXP}/_node_${key}_*.log 2>/dev/null'"
  done
  say "── local (orchestrator) ──"
  do_ "ls ${EXP}/results_*/*/trajectory_*.npz 2>/dev/null | wc -l | sed 's/^/  local npz: /'"
}

gather(){
  say "═══ GATHER remote results → orchestrator ═══"; local key h u r p
  for key in "$NODE_8CARD" "$NODE_2CARD"; do
    h="$(mach "$key" host)"; u="$(mach "$key" user)"; r="$(mach "$key" root)"; p="$(mach "$key" ssh_port)"; p="${p:-22}"
    do_ "rsync -az -e 'ssh -p $p' '$u@$h:$r/${EXP}/results_*' '${EXP}/'"
  done
  say "✓ gathered. Now: bash $0 eval"
}

eval_all(){ do_ "bash $D eval"; }

case "${1:-}" in
  launch) launch ;;
  status) status ;;
  gather) gather ;;
  eval)   eval_all ;;
  *) echo "usage: $0 {launch|status|gather|eval}   (run ON the 2-card orchestrator; DRY=1 to preview)"; exit 2 ;;
esac
