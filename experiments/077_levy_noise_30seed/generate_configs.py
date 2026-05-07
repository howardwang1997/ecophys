"""077 — V4 mechanism 1: Lévy / α-stable noise.

Hypothesis: hill_tail_index pass rate (5%) is the worst fact in v3 because
Gaussian/Student-t noise gives lighter tails than empirical SPX (α≈2.7).
Replacing the noise distribution with a symmetric α-stable (Lévy)
variate at α∈{1.5, 1.7, 1.9} should push hill_tail directly into the
target band [2, 4].

Trade-off to watch: heavy tails may break GARCH-residual fits
(conditional_kurtosis) or blow up extreme realisations. levy_clip=50
is the safety net; if a cell still produces NaNs, increase clip floor.

3 cells × 30 seeds = 90 configs.

Base: 069 T05_g10 (the best v3 cell so far).
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "077_levy_noise_30seed"
OUT.mkdir(parents=True, exist_ok=True)

ALPHAS = [1.5, 1.7, 1.9]
SEEDS = list(range(30))


def main() -> None:
    base = yaml.safe_load(BASE.read_text())
    n = 0
    for alpha in ALPHAS:
        tag = f"levy_a{int(alpha * 10):02d}"
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            cfg["simulator"]["noise_dist"] = "levy"
            cfg["simulator"]["noise_levy_alpha"] = alpha
            cfg["simulator"]["noise_levy_clip"] = 50.0
            # Keep noise_df field but it's unused under levy.
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
