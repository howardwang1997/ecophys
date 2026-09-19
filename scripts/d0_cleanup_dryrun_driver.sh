#!/usr/bin/env bash
# Pre-D0 dry-run driver for d0_cleanup_archive.py (OPS §3 item 1; runs ON THE
# NODES per the 2026-09-19 PI compute rule: no experiment of any size on the
# MacBook). Discovers every <root>/experiments/constraint_attribution_iclr/
# deployment copy under /root, /data, /data2 on this node and emits one plan
# JSON per root (listing + hashes only; no mutation, no network).
#
# Snapshot copies of the same manifest set get distinct output files; the
# plan's r2_prefix field disambiguates their upload keys at D0-S1 (identical
# rel_paths across copies must not clobber each other in R2).
#
# Policy: the plan subcommand runs its default strict-literal manifest
# authority (*.files + *.sha256s, ops plan Part B §3 item 1). The inclusive
# singular-.sha256 reading stays opt-in (--include-singular-sha256), not used
# by this driver.
#
# Usage: bash d0_cleanup_dryrun_driver.sh <node-name> <outdir>
#   assumes d0_cleanup_archive.py sits next to this driver.
set -euo pipefail

NODE=$1
OUT=$2
HERE="$(cd "$(dirname "$0")" && pwd)"
PY_SCRIPT="$HERE/d0_cleanup_archive.py"
[ -f "$PY_SCRIPT" ] || { echo "missing $PY_SCRIPT" >&2; exit 2; }
mkdir -p "$OUT"

DEP_REL="experiments/constraint_attribution_iclr/deployment"
n=0
while IFS= read -r dep; do
  root="${dep%"$DEP_REL"}"
  root="${root%/}"
  n=$((n + 1))
  slug=$(printf '%s' "$root" | sed 's#^/##; s#/#_#g')
  plan_out="$OUT/plan_${NODE}__${slug}.json"
  echo "== $root"
  python3 "$PY_SCRIPT" plan --root "$root" \
    --r2-prefix "paper_d_archive/${NODE}/${slug}" --out "$plan_out"
done < <(find /root /data /data2 -xdev -maxdepth 6 -type d \
           -path "*/$DEP_REL" 2>/dev/null | sort)

echo "SEP"
echo "node=$NODE plans=$n"
for f in "$OUT"/plan_"${NODE}"__*.json; do
  python3 - "$f" <<'PY'
import json, sys
p = json.loads(open(sys.argv[1]).read())
t = p["totals"]
print(f"{sys.argv[1]}: eligible={t['eligible']}/{t['artifacts']} "
      f"eligible_bytes={t['eligible_bytes']} "
      f"unmanifested={t['unmanifested_tarballs']} "
      f"manifest_errors={len(p['manifest_errors'])}")
PY
done
