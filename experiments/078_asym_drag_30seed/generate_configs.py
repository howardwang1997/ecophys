"""078 — V4 mechanism 2: asymmetric drag γ(Δp).

Hypothesis: leverage_effect pass rate (~30%) is bottlenecked by the
symmetric γ. When γ_eff = γ · (1 + α·sign(Δp)), down-moves shrink γ →
larger noise → strong negative corr(r_t, r²_{t+k}). Targets the band
[-6, -0.5] directly.

Trade-off: large α may cause runaway dynamics (γ floor at 0.05
prevents it), or break stationarity. We test α ∈ {0.3, 0.6, 0.9} and
a no-drag control already at α=0 (matches 069 T05_g10).

3 cells × 30 seeds = 90 configs.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "078_asym_drag_30seed"
OUT.mkdir(parents=True, exist_ok=True)

ALPHAS = [0.3, 0.6, 0.9]
SEEDS = list(range(30))


def main() -> None:
    base = yaml.safe_load(BASE.read_text())
    n = 0
    for alpha in ALPHAS:
        tag = f"asymdrag_a{int(alpha * 10):02d}"
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            cfg["simulator"]["asym_drag_alpha"] = alpha
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
