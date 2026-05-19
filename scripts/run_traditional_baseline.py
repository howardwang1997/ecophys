"""Traditional baseline driver — 093 batch component.

Wraps GARCH(1,1), AR1+SV, GBM, and Lux-Marchesi behind a uniform
fit/sample interface, scores n_paths × n_steps samples on the 11 Cont
stylized facts, and writes inference_merged.json in the same schema as
ECoMD and run_baseline_fit_eval.py.

Config schema (under `traditional:` key):
  traditional:
    model: garch | gbm | ar1sv | lux_marchesi
    asset: spx | btcusdt | eurusd | gold | ndx
    period: daily | 2024Q1_1m | ...
    n_paths: 4
    n_steps_per_path: 2520
    fit_kwargs: {...}    # passed to fitter (GARCH/GBM/AR1SV only)
    model_kwargs: {...}  # passed to forward simulator (LM only)
  training:
    seed: int

Output: <out_dir>/inference_merged.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from ecomd.eval.stylized_facts import compute_all  # noqa: E402
from ecomd.training.train_distributed import load_real_returns  # noqa: E402


def _facts_to_dict(facts) -> dict:
    out = {}
    for name, r in facts.items():
        rec = {"estimate": float(r.estimate) if r.estimate is not None else None}
        meta = getattr(r, "meta", None) or {}
        for k, v in meta.items():
            if isinstance(v, (int, float, np.floating, np.integer)):
                rec[k] = float(v)
            else:
                rec[k] = v
        out[name] = rec
    return out


def _sample_garch(real_r, n_paths, n_steps, seed, fit_kwargs):
    from ecomd.baselines.garch import GARCH11
    model = GARCH11.fit(real_r, **(fit_kwargs or {}))
    paths = np.empty((n_paths, n_steps), dtype=np.float64)
    for k in range(n_paths):
        paths[k] = model.simulate(n_steps=n_steps, seed=seed * 1000 + k)
    return paths


def _sample_gbm(real_r, n_paths, n_steps, seed, fit_kwargs):
    from ecomd.baselines.gbm import GBM
    model = GBM.fit(real_r)
    paths = np.empty((n_paths, n_steps), dtype=np.float64)
    for k in range(n_paths):
        paths[k] = model.simulate(n_steps=n_steps, seed=seed * 1000 + k)
    return paths


def _sample_ar1sv(real_r, n_paths, n_steps, seed, fit_kwargs):
    from ecomd.baselines.ar1_sv import AR1SV
    model = AR1SV.fit(real_r)
    paths = np.empty((n_paths, n_steps), dtype=np.float64)
    for k in range(n_paths):
        paths[k] = model.simulate(n_steps=n_steps, seed=seed * 1000 + k)
    return paths


def _sample_lux_marchesi(real_r, n_paths, n_steps, seed, model_kwargs):
    from ecomd.baselines.lux_marchesi import LuxMarchesi1999, LuxMarchesiParams
    # LM is parametric (no data fit); use defaults unless overridden.
    pkwargs = model_kwargs or {}
    params = LuxMarchesiParams(**pkwargs) if pkwargs else LuxMarchesiParams()
    model = LuxMarchesi1999(params=params)
    paths = np.empty((n_paths, n_steps), dtype=np.float64)
    for k in range(n_paths):
        traj = model.run(n_steps=n_steps + 1, seed=seed * 1000 + k)
        paths[k] = traj.log_returns
    return paths


SAMPLERS = {
    "garch":         _sample_garch,
    "gbm":           _sample_gbm,
    "ar1sv":         _sample_ar1sv,
    "lux_marchesi":  _sample_lux_marchesi,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    cfg = yaml.safe_load(args.config.read_text())
    tr = cfg.get("traditional")
    if not tr:
        raise ValueError(f"config {args.config} missing `traditional:` section")
    model = tr["model"]
    asset = tr["asset"]
    period = tr.get("period") or "daily"
    seed = int(cfg.get("training", {}).get("seed", 0))
    n_paths = int(tr.get("n_paths", 4))
    n_steps = int(tr.get("n_steps_per_path", 2520))
    fit_kwargs = dict(tr.get("fit_kwargs", {}))
    model_kwargs = dict(tr.get("model_kwargs", {}))

    args.out_dir.mkdir(parents=True, exist_ok=True)

    # LM doesn't fit, but the runner uniformly loads real returns for
    # reference reporting (n_real recorded in meta).
    try:
        r_real = load_real_returns(REPO, asset, period)
    except Exception as e:
        print(f"[run_traditional] could not load real returns for {asset}/{period}: {e}")
        r_real = np.zeros(0, dtype=np.float64)
    print(f"[run_traditional] model={model} asset={asset} period={period} seed={seed} n_real={r_real.size:,}")

    t0 = time.time()
    sampler = SAMPLERS[model]
    extra = fit_kwargs if model != "lux_marchesi" else model_kwargs
    paths = sampler(r_real, n_paths, n_steps, seed, extra)
    t_fit_sample = time.time() - t0
    print(f"[run_traditional] fit+sample {n_paths}×{n_steps} in {t_fit_sample:.1f}s")

    realizations = []
    all_facts_per_path = []
    for k in range(n_paths):
        facts = compute_all(np.asarray(paths[k], dtype=np.float64))
        all_facts_per_path.append(facts)
        realizations.append({
            "rank": 0,
            "seed": seed * 1000 + k,
            "n_steps": n_steps,
            "rollout_time_s": float(t_fit_sample / n_paths),
            "facts": _facts_to_dict(facts),
        })

    aggregated = {}
    fact_names = list(all_facts_per_path[0].keys())
    for name in fact_names:
        vals = [
            f[name].estimate
            for f in all_facts_per_path
            if f[name].estimate is not None and np.isfinite(f[name].estimate)
        ]
        aggregated[name] = {
            "mean": float(np.mean(vals)) if vals else None,
            "std": float(np.std(vals)) if vals else None,
            "n": len(vals),
        }

    out = {
        "aggregated": aggregated,
        "n_total_rollouts": n_paths,
        "realizations": realizations,
        "traditional_meta": {
            "model": model,
            "asset": asset,
            "period": period,
            "fit_sample_seconds": float(t_fit_sample),
        },
    }
    out_path = args.out_dir / "inference_merged.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"[run_traditional] wrote {out_path}")


if __name__ == "__main__":
    main()
