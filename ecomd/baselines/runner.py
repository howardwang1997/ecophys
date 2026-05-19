"""Common entry point for non-EcoMD baselines (GBM, GARCH, AR(1)+SV, Lux-Marchesi).

Each baseline runs as a single config (one YAML), produces N realizations
(default 4) of length n_steps each, computes the 11-fact stylized-fact
suite via :mod:`ecomd.eval.stylized_facts`, and writes
``inference_merged.json`` in the SAME schema as
:mod:`ecomd.inference.run_large` so downstream scorers
(``score_phase.py``, ``score_continuous.py``) are model-agnostic.

This is a deliberate inversion: the baseline runners do not train (they
either use ad-hoc params or fit-from-data once), but they produce
output that looks like a trained ECoMD checkpoint's eval. The runner
is intentionally CPU-only and single-process — even Lux-Marchesi at
n_steps=4000, n_agents=500 finishes in <10s on a laptop. Parallelism
comes from running configs concurrently at the shell level.

Config schema (YAML):

    baseline:
      kind: gbm | garch | ar1_sv | lux_marchesi
      fit_from_data: true | false              # if true, fit-from-data; else use defaults below
      target_dataset: spx | btcusdt | ...     # data source for fit
      target_period:  2015-2026_daily | 2024Q1_1m | ...
      params:                                 # fallback / override params
        mu: 0.0
        sigma: 0.01
        ...
    inference:
      n_steps: 4000
      n_realizations: 4
      seed_base: 10000

Usage:

    conda run -n ecophys python scripts/run_baseline.py \\
        --config experiments/077_baselines_30seed/config_garch_seed0.yaml
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from ..baselines.ar1_sv import AR1SV
from ..baselines.garch import GARCH11
from ..baselines.gbm import GBM
from ..baselines.lux_marchesi import LuxMarchesi1999, LuxMarchesiParams
from ..eval.stylized_facts import compute_all

log = logging.getLogger("baseline_runner")


# ─────────────────────────────────────────────────────────────────────────────
# Data loader (mirrors training loader, lifted out to avoid pulling torch)
# ─────────────────────────────────────────────────────────────────────────────


def _load_real_returns(repo_root: Path, dataset: str, period: str) -> np.ndarray:
    """Lightweight clone of train_distributed.load_real_returns — pandas only."""
    import pandas as pd
    from ..eval.stylized_facts import log_returns_from_prices

    yfinance_symbols = {
        "spx":     "^GSPC", "spy":  "SPY",  "qqq": "QQQ", "iwm": "IWM",
        "dax":     "^GDAXI", "stoxx50": "^STOXX50E",
        "hsi":     "^HSI", "nikkei": "^N225",
        "gold":    "GLD", "eurusd": "EURUSD=X", "ndx": "^NDX",
    }
    if dataset in yfinance_symbols:
        symbol = yfinance_symbols[dataset]
        for root in (repo_root / "data" / "raw", repo_root / "data" / "sample"):
            d = root / "yfinance" / "interval=1d" / f"symbol={symbol}"
            if d.exists():
                shards = sorted(d.glob("year=*.parquet"))
                if not shards:
                    continue
                df = pd.concat([pd.read_parquet(p) for p in shards], ignore_index=True)
                df = df.sort_values("timestamp").reset_index(drop=True)
                col = "adjusted_close" if "adjusted_close" in df.columns else "close"
                return log_returns_from_prices(df[col].to_numpy())
        raise FileNotFoundError(f"no {symbol} yfinance data")
    if dataset in ("btcusdt", "ethusdt"):
        sym = "BTCUSDT" if dataset == "btcusdt" else "ETHUSDT"
        for root in (repo_root / "data" / "raw", repo_root / "data" / "sample"):
            d = root / "binance" / "market=spot" / "interval=1m" / f"symbol={sym}" / "year=2024"
            if d.exists():
                shards = sorted(d.glob("month=*.parquet"))
                if not shards:
                    continue
                df = pd.concat([pd.read_parquet(p) for p in shards], ignore_index=True)
                df = df.sort_values("open_time").reset_index(drop=True)
                return log_returns_from_prices(df["close"].to_numpy())
        raise FileNotFoundError(f"no {sym} Binance data")
    raise ValueError(f"unknown dataset: {dataset!r}")


# ─────────────────────────────────────────────────────────────────────────────
# Baseline dispatch
# ─────────────────────────────────────────────────────────────────────────────


def _build_baseline(kind: str, baseline_cfg: dict[str, Any], real_r: np.ndarray | None):
    """Returns a ``simulate(n_steps, seed)`` callable plus a metadata dict."""
    fit_from_data = bool(baseline_cfg.get("fit_from_data", False))
    params_override = dict(baseline_cfg.get("params") or {})

    if kind == "gbm":
        if fit_from_data and real_r is not None:
            model = GBM.fit(real_r)
        else:
            model = GBM(**params_override)
        meta = {"kind": kind, "params": asdict(model.params)}
        return (lambda n, seed: model.simulate(n, seed=seed)), meta

    if kind == "garch":
        if fit_from_data and real_r is not None:
            dist = params_override.get("dist", "t")
            model = GARCH11.fit(real_r, dist=dist)
        else:
            model = GARCH11(**params_override)
        meta = {"kind": kind, "params": asdict(model.params)}
        return (lambda n, seed: model.simulate(n, seed=seed)), meta

    if kind == "ar1_sv":
        if fit_from_data and real_r is not None:
            model = AR1SV.fit(real_r)
        else:
            model = AR1SV(**params_override)
        meta = {"kind": kind, "params": asdict(model.params)}
        return (lambda n, seed: model.simulate(n, seed=seed)), meta

    if kind == "lux_marchesi":
        params = LuxMarchesiParams(**params_override) if params_override else LuxMarchesiParams()
        model = LuxMarchesi1999(params)
        meta = {"kind": kind, "params": {f.name: getattr(params, f.name)
                                          for f in params.__dataclass_fields__.values()}}
        # Lux-Marchesi returns a trajectory; we expose log-returns.
        def _sim(n, seed):
            traj = model.run(n_steps=n + 1, dt=0.01, seed=seed)
            return traj.log_returns
        return _sim, meta

    raise ValueError(f"unknown baseline kind: {kind!r}")


# ─────────────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="YAML config path")
    parser.add_argument("--out-dir", default=None,
                        help="results dir (default: parent_of_config/results_<config_stem>)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    config_path = Path(args.config).resolve()
    cfg = yaml.safe_load(config_path.read_text())
    baseline_cfg = cfg["baseline"]
    inf_cfg = cfg.get("inference", {})

    n_steps = int(inf_cfg.get("n_steps", 4000))
    n_real = int(inf_cfg.get("n_realizations", 4))
    seed_base = int(inf_cfg.get("seed_base", 10_000))
    kind = baseline_cfg["kind"]

    if args.out_dir:
        out_dir = Path(args.out_dir)
    else:
        # Mirror the EcoMD layout: experiments/<dir>/results_<config_stem>/
        out_dir = config_path.parent / f"results_{config_path.stem.replace('config_', '')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Data load (only when fitting from real data)
    real_r = None
    if baseline_cfg.get("fit_from_data", False):
        repo_root = Path(__file__).resolve().parent.parent.parent
        real_r = _load_real_returns(
            repo_root,
            dataset=baseline_cfg.get("target_dataset", "spx"),
            period=baseline_cfg.get("target_period", "2015-2026_daily"),
        )

    sim_fn, meta = _build_baseline(kind, baseline_cfg, real_r)
    log.info(f"baseline={kind} params={meta['params']}")

    realizations: list[dict[str, Any]] = []
    for r_idx in range(n_real):
        seed = seed_base + r_idx
        t0 = time.time()
        returns = sim_fn(n_steps, seed)
        # Volume — these baselines don't model volume. Use |r| as proxy so
        # volume_volatility_corr is well-defined; this is a known limit of
        # the baseline (will likely PASS the band by construction, an
        # honest disclosure in the paper).
        volumes = np.abs(returns)
        facts = compute_all(returns, volume=volumes)
        dt = time.time() - t0
        realizations.append({
            "rank": 0,
            "seed": seed,
            "n_steps": n_steps,
            "rollout_time_s": dt,
            "facts": {k: v.to_dict() for k, v in facts.items()},
        })
        log.info(f"realization {r_idx + 1}/{n_real} seed={seed} took {dt:.1f}s")

    # Aggregate (same schema as run_large.py)
    keys = list(realizations[0]["facts"].keys())
    aggregated: dict[str, dict[str, float]] = {}
    for k in keys:
        vals = [float(r["facts"][k]["estimate"])
                for r in realizations
                if isinstance(r["facts"][k].get("estimate"), (int, float))
                and np.isfinite(r["facts"][k].get("estimate"))]
        if vals:
            aggregated[k] = {"mean": float(np.mean(vals)),
                             "std": float(np.std(vals)),
                             "n": len(vals)}

    merged = {
        "aggregated": aggregated,
        "n_total_rollouts": len(realizations),
        "realizations": realizations,
        "baseline_meta": meta,
    }
    (out_dir / "inference_merged.json").write_text(json.dumps(merged, indent=2))
    (out_dir / "inference_rank_0.json").write_text(json.dumps(realizations, indent=2))
    log.info(f"wrote {out_dir / 'inference_merged.json'}")


if __name__ == "__main__":
    main()
