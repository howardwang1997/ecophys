#!/usr/bin/env bash
# H20-side: run ABIDES (abides-markets / rmsc04) under a few calibrated variants,
# dump each sim's mid-price path to CSV for scripts/abides_to_returns.py.
#
# Strategic purpose (2026-05-28 D7): ceiling-attribution probe. Score ABIDES with
# the same 11-fact evaluator + daily bands as EcoMD to learn whether 11/11 is
# reachable for the agent-based paradigm. See papers/proposal/plan_v3_addendum_2026-05-28.md.
#
# ── ASSUMPTIONS I COULD NOT VERIFY (H20 not reachable from the dev session) ──
#   * ABIDES is installed as the JPMC public `abides-markets` + `abides-core`
#     packages in conda env $ABIDES_ENV (default: abides).
#   * rmsc04 build_config signature: rmsc04.build_config(seed=..., end_time=...,
#     and variant kwargs like num_noise_agents / num_value_agents). Exact kwarg
#     names depend on the installed abides-markets version — CONFIRM and adjust
#     the VARIANTS array + the inline driver below if your version differs.
#   * Symbol ticker is "ABM" (rmsc04 default).
# If your install differs (e.g. older abides-jpmc, or a custom config module),
# edit the inline python driver — that is the single place the API is touched.
#
# Usage (on H20):
#   ABIDES_ENV=abides bash scripts/h20_run_abides_calibrate.sh
#   N_SEEDS=6 bash scripts/h20_run_abides_calibrate.sh   # override seeds/variant count

set -euo pipefail

ABIDES_ENV="${ABIDES_ENV:-abides}"
N_SEEDS="${N_SEEDS:-6}"
END_TIME="${END_TIME:-16:00:00}"
OUT_DIR="${OUT_DIR:-experiments/105_abides_ceiling/abides_raw}"
mkdir -p "$OUT_DIR"

# variant tag : space-separated "key=value" build_config kwargs (CONFIRM kwarg names)
declare -a VARIANTS=(
  "rmsc04_base:"
  "rmsc04_morenoise:num_noise_agents=5000"
  "rmsc04_fewnoise:num_noise_agents=500"
  "rmsc04_morevalue:num_value_agents=200"
  "rmsc04_fewvalue:num_value_agents=20"
)

echo "[$(date -u +%FT%TZ)] ABIDES calibrate: ${#VARIANTS[@]} variants × ${N_SEEDS} seeds → $OUT_DIR"

for entry in "${VARIANTS[@]}"; do
  cell="${entry%%:*}"
  kwargs="${entry#*:}"
  for seed in $(seq 0 $((N_SEEDS - 1))); do
    csv="${OUT_DIR}/abides_${cell}_seed${seed}.csv"
    if [[ -f "$csv" ]]; then echo "  skip existing $csv"; continue; fi
    echo "  run $cell seed=$seed kwargs='$kwargs'"
    ABIDES_CELL="$cell" ABIDES_SEED="$seed" ABIDES_KWARGS="$kwargs" \
    ABIDES_END="$END_TIME" ABIDES_CSV="$csv" \
    conda run --no-capture-output -n "$ABIDES_ENV" python - <<'PY'
import os, csv
# ── inline ABIDES driver: the ONLY place the abides-markets API is touched ──
seed = int(os.environ["ABIDES_SEED"])
cell = os.environ["ABIDES_CELL"]
end_time = os.environ["ABIDES_END"]
out_csv = os.environ["ABIDES_CSV"]
kwargs = {}
for kv in os.environ.get("ABIDES_KWARGS", "").split():
    if "=" in kv:
        k, v = kv.split("=", 1)
        kwargs[k] = int(v) if v.isdigit() else v

from abides_markets.configs import rmsc04           # TODO: confirm module on H20
from abides_core import abides

config = rmsc04.build_config(seed=seed, end_time=end_time, **kwargs)  # TODO: confirm kwargs
end_state = abides.run(config)

# Extract mid-price path from the ExchangeAgent's order book (symbol "ABM").
exchange = end_state["agents"][0]
ob = exchange.order_books["ABM"]                     # TODO: confirm symbol
L1 = ob.get_L1_snapshots()
bids = L1["best_bids"]; asks = L1["best_asks"]       # arrays of (time, price, qty)
n = min(len(bids), len(asks))
with open(out_csv, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["timestamp", "mid"])
    for i in range(n):
        t = int(bids[i][0])
        mid = (float(bids[i][1]) + float(asks[i][1])) / 2.0
        w.writerow([t, mid])
print(f"wrote {out_csv}: {n} mid-price points")
PY
  done
done

echo "[$(date -u +%FT%TZ)] ABIDES calibrate done → $OUT_DIR"
