#!/usr/bin/env bash
# Reflexive smoke driver (pre-freeze item 10; runs ON THE NODE per the
# 2026-09-19 PI compute rule: no experiment of any size on the MacBook).
# Full reflexive test file, then the smoke matrix {l1,l2} x {R00,R11} x
# {dgp,sim(untrained lineage-matched model)} x 2 seeds at module defaults
# (q=100, 200 rounds, 25 warmup, corpus-scale background). Records land
# under a reflexive/smoke path (firewall 1); stdout carries the per-record
# smoke lines and the descriptive summary JSON.
#
# Usage: bash rfx_smoke_driver_20260919.sh   (from /root/ecophys-remote)
set -euo pipefail

cd /root/ecophys-remote
PY=/root/miniconda3/envs/ecophys-d0v2/bin/python
OUT=/root/rfx_smoke_20260919/reflexive/smoke
rm -rf /root/rfx_smoke_20260919
mkdir -p "$OUT"

echo "== tests"
$PY -m pytest tests/test_reexploration_reflexive.py -q

for lineage in l1 l2; do
  if [ "$lineage" = l1 ]; then seeds=11000,11001; else seeds=12000,12001; fi
  for cell in R00 R11; do
    for arm in dgp sim; do
      if [ "$arm" = dgp ]; then extra=""; else extra="--untrained-model $lineage"; fi
      echo "== $lineage $cell $arm"
      $PY -m ecomd.reexploration.reflexive \
        --lineage "$lineage" --cell "$cell" --arm "$arm" \
        --seeds "$seeds" --smoke --out-dir "$OUT" $extra
    done
  done
done

echo "SEP"
echo "records=$(ls "$OUT" | wc -l)"
sha256sum "$OUT"/*.json
