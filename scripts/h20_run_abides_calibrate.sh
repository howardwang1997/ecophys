#!/usr/bin/env bash
# H20-side: run ABIDES (JPMC abides v1, rmsc03-style) under calibrated variants,
# dump each sim's mid-price path to CSV for scripts/abides_to_returns.py.
#
# Strategic purpose (2026-05-28 D7): ceiling-attribution probe. Score ABIDES with
# the same 11-fact evaluator + daily bands as EcoMD.
#
# ADAPTED for old JPMC abides (not abides-markets). Builds rmsc03-style agents
# directly. Uses book_freq="S" + log_dir to dump per-second wide order book,
# then extracts mid-price from the pickle (positive vol = ask, negative = bid).
#
# Usage (on H20):
#   ABIDES_ENV=abides bash scripts/h20_run_abides_calibrate.sh
#   N_SEEDS=6 bash scripts/h20_run_abides_calibrate.sh

set -euo pipefail

ABIDES_ENV="${ABIDES_ENV:-abides}"
N_SEEDS="${N_SEEDS:-6}"
OUT_DIR="${OUT_DIR:-experiments/105_abides_ceiling/abides_raw}"
mkdir -p "$OUT_DIR"

declare -a VARIANTS=(
  "rmsc03_base:"
  "rmsc03_morenoise:num_noise=5000"
  "rmsc03_fewnoise:num_noise=200"
  "rmsc03_morevalue:num_value=200"
  "rmsc03_fewvalue:num_value=20"
)

echo "[$(date -u +%FT%TZ)] ABIDES calibrate (rmsc03-style): ${#VARIANTS[@]} variants × ${N_SEEDS} seeds → $OUT_DIR"

for entry in "${VARIANTS[@]}"; do
  cell="${entry%%:*}"
  kwargs="${entry#*:}"
  for seed in $(seq 0 $((N_SEEDS - 1))); do
    csv="${OUT_DIR}/abides_${cell}_seed${seed}.csv"
    if [[ -f "$csv" ]]; then echo "  skip existing $csv"; continue; fi
    echo "  run $cell seed=$seed kwargs='$kwargs'"
    ABIDES_CELL="$cell" ABIDES_SEED="$seed" ABIDES_KWARGS="$kwargs" \
    ABIDES_CSV="$csv" \
    conda run --no-capture-output -n "$ABIDES_ENV" python - <<'PY'
import os, sys, csv, tempfile, glob, time
import numpy as np
import pandas as pd

# ── pandas 2.x compat: 'closed' → 'inclusive' in date_range ──
import agent.ExchangeAgent as _ea
_orig_logOB = _ea.ExchangeAgent.logOrderBookSnapshots
def _patched_logOB(self, symbol):
    _orig_dr = pd.date_range
    def _dr_fix(*a, **kw):
        if 'closed' in kw:
            kw['inclusive'] = kw.pop('closed')
        return _orig_dr(*a, **kw)
    pd.date_range = _dr_fix
    try:
        _orig_logOB(self, symbol)
    finally:
        pd.date_range = _orig_dr
_ea.ExchangeAgent.logOrderBookSnapshots = _patched_logOB

seed = int(os.environ["ABIDES_SEED"])
cell = os.environ["ABIDES_CELL"]
out_csv = os.environ["ABIDES_CSV"]
kwargs = {}
for kv in os.environ.get("ABIDES_KWARGS", "").split():
    if "=" in kv:
        k, v = kv.split("=", 1)
        kwargs[k] = int(v) if v.isdigit() else v

num_noise = kwargs.get("num_noise", 1000)
num_value = kwargs.get("num_value", 100)

from Kernel import Kernel
from util import util
from util.order import LimitOrder
from util.oracle.SparseMeanRevertingOracle import SparseMeanRevertingOracle
from agent.ExchangeAgent import ExchangeAgent
from agent.NoiseAgent import NoiseAgent
from agent.ValueAgent import ValueAgent
from agent.market_makers.AdaptiveMarketMakerAgent import AdaptiveMarketMakerAgent
from model.LatencyModel import LatencyModel

np.random.seed(seed)
util.silent_mode = True
LimitOrder.silent_mode = True

symbol = "ABM"
historical_date = pd.to_datetime("2020-01-02")
mkt_open = historical_date + pd.to_timedelta("09:30:00")
mkt_close = historical_date + pd.to_timedelta("16:00:00")

starting_cash = 10000000
r_bar = 1e5
sigma_n = r_bar / 10
kappa = 1.67e-15
lambda_a = 7e-11

symbols = {symbol: {"r_bar": r_bar, "kappa": 1.67e-16, "sigma_s": 0,
                     "fund_vol": 1e-8,
                     "megashock_lambda_a": 2.77778e-18, "megashock_mean": 1e3, "megashock_var": 5e4,
                     "random_state": np.random.RandomState(seed=np.random.randint(0, 2**32, dtype="uint64"))}}
oracle = SparseMeanRevertingOracle(mkt_open, mkt_close, symbols)

log_dir = tempfile.mkdtemp(prefix=f"abides_{cell}_s{seed}_")
agents = []
agent_count = 0

agents.append(ExchangeAgent(id=0, name="EXCHANGE_AGENT", type="ExchangeAgent",
                            mkt_open=mkt_open, mkt_close=mkt_close, symbols=[symbol],
                            log_orders=True, pipeline_delay=0, computation_delay=0,
                            stream_history=25000, book_freq="S", wide_book=True,
                            random_state=np.random.RandomState(seed=np.random.randint(0, 2**32, dtype="uint64"))))
agent_types = ["ExchangeAgent"]
agent_count = 1

noise_mkt_open = historical_date + pd.to_timedelta("09:00:00")
noise_mkt_close = historical_date + pd.to_timedelta("16:00:00")
for j in range(agent_count, agent_count + num_noise):
    agents.append(NoiseAgent(id=j, name=f"NoiseAgent {j}", type="NoiseAgent",
                             symbol=symbol, starting_cash=starting_cash,
                             wakeup_time=util.get_wake_time(noise_mkt_open, noise_mkt_close),
                             log_orders=None,
                             random_state=np.random.RandomState(seed=np.random.randint(0, 2**32, dtype="uint64"))))
agent_count += num_noise

for j in range(agent_count, agent_count + num_value):
    agents.append(ValueAgent(id=j, name=f"Value Agent {j}", type="ValueAgent",
                             symbol=symbol, starting_cash=starting_cash,
                             sigma_n=sigma_n, r_bar=r_bar, kappa=kappa, lambda_a=lambda_a,
                             log_orders=None,
                             random_state=np.random.RandomState(seed=np.random.randint(0, 2**32, dtype="uint64"))))
agent_count += num_value

mm_cancel_limit_delay = 50
for idx in range(2):
    agents.append(AdaptiveMarketMakerAgent(
        id=agent_count + idx, name=f"ADAPTIVE_POV_MARKET_MAKER_AGENT_{idx}",
        type="AdaptivePOVMarketMakerAgent", symbol=symbol, starting_cash=starting_cash,
        pov=0.025, min_order_size=1, window_size="adaptive", num_ticks=10,
        wake_up_freq="10S", cancel_limit_delay=mm_cancel_limit_delay,
        skew_beta=0, level_spacing=5, spread_alpha=0.75, backstop_quantity=50000,
        log_orders=None,
        random_state=np.random.RandomState(seed=np.random.randint(0, 2**32, dtype="uint64"))))
agent_count += 2

kernel = Kernel("RMSC03 Kernel", random_state=np.random.RandomState(seed=np.random.randint(0, 2**32, dtype="uint64")))
latency_rstate = np.random.RandomState(seed=np.random.randint(0, 2**32))
nyc_to_seattle_meters = 3866660
pairwise_distances = util.generate_uniform_random_pairwise_dist_on_line(
    0.0, nyc_to_seattle_meters, agent_count, random_state=latency_rstate)
pairwise_latencies = util.meters_to_light_ns(pairwise_distances)
latency_model = LatencyModel(latency_model="deterministic", random_state=latency_rstate,
                             kwargs={"connected": True, "min_latency": pairwise_latencies})

kernel_stop = mkt_close + pd.to_timedelta("00:01:00")

t0 = time.time()
real_stdout = sys.stdout
sys.stdout = open(os.devnull, "w")
kernel.runner(agents=agents, startTime=historical_date, stopTime=kernel_stop,
              agentLatencyModel=latency_model, defaultComputationDelay=50,
              oracle=oracle, log_dir=log_dir)
sys.stdout = real_stdout
dt_sim = time.time() - t0

# Extract mid-price from order book pickle
ob_files = glob.glob(f"{log_dir}/ORDERBOOK_*")
if not ob_files:
    print(f"[ERROR] no ORDERBOOK file in {log_dir}")
    sys.exit(1)

df = pd.read_pickle(ob_files[0])
price_cols = sorted([c for c in df.columns if isinstance(c, (int, float, np.integer, np.floating))])

rows_out = []
for idx, row in df.iterrows():
    best_bid = None
    best_ask = None
    for p in price_cols:
        v = row.get(p)
        if v is None or (isinstance(v, float) and (np.isnan(v) or v == 0)):
            continue
        if v < 0 and (best_bid is None or p > best_bid):
            best_bid = p
        elif v > 0 and (best_ask is None or p < best_ask):
            best_ask = p
    if best_bid is not None and best_ask is not None:
        rows_out.append((str(idx), (best_bid + best_ask) / 2.0))

with open(out_csv, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["timestamp", "mid"])
    w.writerows(rows_out)

# Clean up temp log dir
import shutil
shutil.rmtree(log_dir, ignore_errors=True)

print(f"wrote {out_csv}: {len(rows_out)} pts ({cell} s={seed} noise={num_noise} val={num_value} agents={agent_count} sim={dt_sim:.0f}s)")
PY
  done
done

echo "[$(date -u +%FT%TZ)] ABIDES calibrate done → $OUT_DIR"
