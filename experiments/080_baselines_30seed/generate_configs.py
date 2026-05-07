"""080 — statistical baselines (GBM, GARCH, AR(1)+SV, Lux-Marchesi).

Each baseline runs 30 seeds × 4 realizations per seed = 120 rollouts
total per baseline. All fit from SPX 2015-2026 daily data (same target
as EcoMD training). Baselines are CPU-only and fast (~2s per config),
so we run them via scripts/run_baseline.py rather than the GPU trainer.

4 baselines × 30 seeds = 120 configs.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "experiments" / "080_baselines_30seed"
OUT.mkdir(parents=True, exist_ok=True)

BASELINES = ["gbm", "garch", "ar1_sv", "lux_marchesi"]
SEEDS = list(range(30))


def main() -> None:
    n = 0
    for kind in BASELINES:
        for s in SEEDS:
            cfg = {
                "baseline": {
                    "kind": kind,
                    "fit_from_data": True,
                    "target_dataset": "spx",
                    "target_period": "2015-2026_daily",
                },
                "inference": {
                    "n_steps": 4000,
                    "n_realizations": 4,
                    "seed_base": 10_000 + s * 1000,
                },
            }
            if kind == "garch":
                cfg["baseline"]["params"] = {"dist": "t"}
            if kind == "lux_marchesi":
                cfg["baseline"]["params"] = {"n_agents": 500}
            (OUT / f"config_{kind}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
