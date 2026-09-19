#!/usr/bin/env bash
# Regression battery v3 (pre-freeze re-verification of the 2026-09-08 v2
# battery; runs ON THE NODE per the 2026-09-19 PI compute rule). Same
# per-file isolation semantics as v2: one fresh pytest process per
# tests/test_*.py, 1200s timeout, exit codes to summary.tsv; the
# slow-marked bptt checkpoint file runs with -m "not slow" (recorded
# exclusion, unchanged from v2 disposition). Env bin prepended to PATH for
# the conda openssl (keccak) the aave-family tests shell out to.
#
# Usage: bash reg_battery_v3_driver_20260919.sh   (from /root/ecophys-remote)
set -u

cd /root/ecophys-remote
PY=/root/miniconda3/envs/ecophys-d0v2/bin/python
export PATH="/root/miniconda3/envs/ecophys-d0v2/bin:$PATH"
OUT=/root/regv3
rm -rf "$OUT"
mkdir -p "$OUT/logs"

echo "battery v3 start $(date -Is)" | tee "$OUT/summary.tsv"
n=0
for f in tests/test_*.py; do
  n=$((n + 1))
  name=$(basename "$f" .py)
  extra=""
  if [ "$name" = "test_bptt_checkpoint" ]; then extra='-m "not slow"'; fi
  start=$(date +%s)
  if [ "$name" = "test_bptt_checkpoint" ]; then
    timeout 1200 "$PY" -m pytest -q "$f" -m "not slow" \
      > "$OUT/logs/$name.log" 2>&1
  else
    timeout 1200 "$PY" -m pytest -q "$f" \
      > "$OUT/logs/$name.log" 2>&1
  fi
  rc=$?
  end=$(date +%s)
  printf '%s\t%s\t%s\n' "$rc" "$((end - start))" "$f" >> "$OUT/summary.tsv"
  echo "[$n] rc=$rc $((end - start))s $f"
done
echo "battery v3 done $(date -Is); files=$n"
grep -cv "^battery" "$OUT/summary.tsv" > "$OUT/nlines"
echo "records=$(cat "$OUT/nlines")" > "$OUT/COMPLETE"
echo "COMPLETE rc-summary:"
awk -F'\t' 'NR>1 && $1 != 0 {c++} END {print "nonzero_files=" (c+0)}' "$OUT/summary.tsv" || true
awk -F'\t' 'NR>1 {print $1}' "$OUT/summary.tsv" | sort | uniq -c
