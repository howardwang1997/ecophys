"""Generic baseline fit/sample/score driver — 095 batch component.

Reads a YAML config describing one (asset, model, seed) cell, fits the
chosen baseline (WGAN-LP or TrajCast-lite) on real returns for the asset,
samples N rollouts, scores each rollout on the 11 Cont stylized facts,
and writes `inference_merged.json` in the same schema as ECoMD output —
so `scripts/score_phase.py` and `scripts/score_attribution.py` work
unchanged.

Config schema (under `baseline:` key):
  baseline:
    model: wgan_lp | trajcast_lite
    asset: spx | btcusdt | eurusd | gold | ndx
    n_rollouts: int        # default 4
    n_steps_per_rollout: int  # default 2520 (~10y daily)
    fit_kwargs: dict       # passed to model.fit()
    model_kwargs: dict     # passed to model.__init__()
  training:
    seed: int

Output: <out_dir>/inference_merged.json with schema:
  {"aggregated": {...}, "n_total_rollouts": int, "realizations": [...]}
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

MODELS = {}


def _load_model(name: str):
    if name not in MODELS:
        if name == "wgan_lp":
            from ecomd.baselines.wgan_lp import WGANLPSimulator
            MODELS[name] = WGANLPSimulator
        elif name == "trajcast_lite":
            from ecomd.baselines.trajcast_lite import TrajCastLiteSimulator
            MODELS[name] = TrajCastLiteSimulator
        else:
            raise ValueError(f"unknown baseline model {name!r}; expected wgan_lp|trajcast_lite")
    return MODELS[name]


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    cfg = yaml.safe_load(args.config.read_text())
    bl = cfg.get("baseline")
    if not bl:
        raise ValueError(f"config {args.config} missing `baseline:` section")
    model_name = bl["model"]
    asset = bl["asset"]
    seed = int(cfg.get("training", {}).get("seed", 0))
    n_rollouts = int(bl.get("n_rollouts", 4))
    n_steps = int(bl.get("n_steps_per_rollout", 2520))
    fit_kwargs = dict(bl.get("fit_kwargs", {}))
    model_kwargs = dict(bl.get("model_kwargs", {}))

    args.out_dir.mkdir(parents=True, exist_ok=True)

    # Real returns
    period = bl.get("period") or "daily"
    r_real = load_real_returns(REPO, asset, period)
    print(f"[run_baseline] asset={asset} period={period} n_real={len(r_real):,}")

    Model = _load_model(model_name)
    print(f"[run_baseline] model={model_name} seed={seed} kwargs={model_kwargs}")

    t0 = time.time()
    model = Model(**model_kwargs)
    fit_kwargs.setdefault("seed", seed)
    model.fit(r_real, **fit_kwargs)
    t_fit = time.time() - t0
    print(f"[run_baseline] fit done in {t_fit:.1f}s")

    realizations = []
    all_facts_per_rollout = []
    for k in range(n_rollouts):
        t1 = time.time()
        synth = model.sample(n_steps=n_steps, seed=seed * 1000 + k)
        t_roll = time.time() - t1
        facts = compute_all(np.asarray(synth, dtype=np.float64))
        all_facts_per_rollout.append(facts)
        realizations.append({
            "rank": 0,
            "seed": seed * 1000 + k,
            "n_steps": n_steps,
            "rollout_time_s": float(t_roll),
            "facts": _facts_to_dict(facts),
        })

    aggregated = {}
    fact_names = list(all_facts_per_rollout[0].keys())
    for name in fact_names:
        vals = [
            f[name].estimate
            for f in all_facts_per_rollout
            if f[name].estimate is not None and np.isfinite(f[name].estimate)
        ]
        aggregated[name] = {
            "mean": float(np.mean(vals)) if vals else None,
            "std": float(np.std(vals)) if vals else None,
            "n": len(vals),
        }

    out = {
        "aggregated": aggregated,
        "n_total_rollouts": n_rollouts,
        "realizations": realizations,
        "baseline_meta": {
            "model": model_name,
            "asset": asset,
            "fit_seconds": float(t_fit),
            "n_steps_per_rollout": n_steps,
        },
    }
    out_path = args.out_dir / "inference_merged.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"[run_baseline] wrote {out_path}")


if __name__ == "__main__":
    main()
