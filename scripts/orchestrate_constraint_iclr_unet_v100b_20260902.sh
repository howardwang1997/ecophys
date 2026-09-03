#!/usr/bin/env bash
set -euo pipefail

ROOT=/root/ecophys_constraint_iclr_unet_20260902
DATA=/data/ecophys_pdebench_v2/1D_Advection_Sols_beta0.4.hdf5
EXPECTED_BYTES=8232966952
EXPECTED_SHA=d973ff2bb3c2a5edf42957ff029b78672451532ebd6bf475848ff23cfd3ee3b6

while [[ ! -f "$DATA" ]] || [[ "$(stat -c %s "$DATA")" -ne "$EXPECTED_BYTES" ]]; do
  sleep 60
done
[[ "$(sha256sum "$DATA" | awk '{print $1}')" == "$EXPECTED_SHA" ]]
while [[ -n "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits)" ]]; do
  sleep 60
done
mkdir -p "$ROOT/data/pdebench"
ln -s "$DATA" "$ROOT/data/pdebench/1D_Advection_Sols_beta0.4.hdf5"
cd "$ROOT"
export ECOPHYS_GIT_HEAD=86dd76ee0127c5eb7945a5806bdad74548c62459
export ECOPHYS_DIRTY=1
exec /root/miniconda3/bin/conda run --no-capture-output \
  -p /data/ecophys_workshop/conda_env python \
  scripts/run_constraint_iclr_pdebench_fno.py \
  --config-name pdebench_advection_unet_factorial_20260902 \
  worker_id=v100b \
  'seeds=[7015,7016,7017,7018,7019,7020,7021,7022,7023,7024,7025,7026,7027,7028,7029]' \
  output=experiments/constraint_attribution_iclr/pdebench/unet_factorial_v100b_20260902.jsonl \
  checkpoint_dir=experiments/constraint_attribution_iclr/pdebench/unet_factorial_checkpoints_v100b_20260902
