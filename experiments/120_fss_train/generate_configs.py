"""Exp 120 — train-at-N control for the exp-116 finite-size-scaling criticality claim.

116 sweeps system size N at INFERENCE on a model trained at N=10000. The #1 reviewer attack on
the resulting hill(N) curve: "you changed N only at test time — the curve is train/test mismatch
(extrapolation error), not emergent criticality." This control kills that attack: TRAIN a fresh
baseline AT each N, then measure its tail index at its OWN training N. If the trained-at-N hill(N)
curve agrees with the inference-swept hill(N) (exp 116), the N-scaling is a genuine property of the
learned dynamics, not an artifact. (scripts/score_fss_train.py overlays the two.)

Pure baseline recipe (108 baseline_mmd base, rollout_reg, ed_normalize=False = overshoot regime,
hawkes_kappa=0.3 as in base) — only n_agents varies. Capped at N=10000: chunk_steps=24 is the
single-card OOM ceiling at N=10⁴ ([[project_chunk_oom_constraint]]); larger N is inference-only
(116, lightweight recorder).

Layout: experiments/120_fss_train/<asset>/config_N<N>_seed<s>.yaml — per-asset subdir (so
H20-1 runs .../spx and H20-3 runs .../btcusdt without collision), each under
scripts/h20_run_phase.sh (train+eval each; eval's run_large gives hill at the training N).

Usage:
  python experiments/120_fss_train/generate_configs.py --asset spx     --seeds 0-5   # H20-1
  python experiments/120_fss_train/generate_configs.py --asset btcusdt --seeds 0-3   # H20-3
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "120_fss_train"

REG_EVERY = 8
N_VALUES = [1000, 2000, 4000, 8000, 10000]   # ≤10k: chunk_steps=24 single-card OOM ceiling

ASSETS = {
    "spx":     ("spx", "2015-2026_daily"),
    "ndx":     ("ndx", "2015-2026_daily"),
    "gold":    ("gold", "2015-2026_daily"),
    "eurusd":  ("eurusd", "2015-2026_daily"),
    "btcusdt": ("btcusdt", "2024Q1_1m"),
}


def _parse_seeds(spec: str) -> list[int]:
    if "-" in spec:
        a, b = spec.split("-"); return list(range(int(a), int(b) + 1))
    return [int(x) for x in spec.split(",")]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--asset", required=True, choices=list(ASSETS))
    ap.add_argument("--seeds", default="0-5", help="e.g. 0-5 or 0,1,2")
    ap.add_argument("--n-values", default=None, help="comma list to override N ladder")
    args = ap.parse_args()

    adir = OUT / args.asset
    adir.mkdir(parents=True, exist_ok=True)
    base = yaml.safe_load(BASE_PATH.read_text())
    dataset, period = ASSETS[args.asset]
    seeds = _parse_seeds(args.seeds)
    nvals = [int(x) for x in args.n_values.split(",")] if args.n_values else N_VALUES

    n = 0
    for N in nvals:
        for seed in seeds:
            cfg = copy.deepcopy(base)
            cfg["simulator"]["n_agents"] = N
            cfg["simulator"]["price_formation_kwargs"]["ed_normalize"] = False  # match 116 regime
            cfg["training"]["seed"] = seed
            cfg["training"]["target_dataset"] = dataset
            cfg["training"]["target_period"] = period
            cfg["training"]["rollout_reg_every"] = REG_EVERY
            (adir / f"config_N{N}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1

    est_h = n * 62 / 60
    print(f"wrote {n} configs to {OUT}  asset={args.asset}  N∈{nvals}  seeds={seeds}")
    print(f"  baseline recipe (ed_normalize=False, κ=0.3), train+eval at each N")
    print(f"  ≈ {est_h:.0f} card-hours ({est_h/8:.1f}h on 8 cards, {est_h/2:.1f}h on 2 cards)")


if __name__ == "__main__":
    main()
