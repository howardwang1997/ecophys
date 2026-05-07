"""079 — V4 mechanism 3: memory kernel.

Hypothesis: zumbach_asymmetry pass rate (~10%) is the bottleneck because
v3 has no path-dependent noise — past large |Δs| does not amplify
future noise. The memory kernel adds an EMA(|Δs|, λ) modulation:

    σ_eff = σ · (1 + strength · EMA_λ(|Δs|))

so realised volatility echoes through the rollout. Targets zumbach AND
acf_squared_returns (already 69%, but tightens band placement).

Trade-off: strong kernels can self-reinforce → exploding vol. λ=0.95
gives ~20-step memory; strength=2 doubles σ at 1× the historical
average |Δs|.

3 cells × 30 seeds = 90 configs.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "079_memory_kernel_30seed"
OUT.mkdir(parents=True, exist_ok=True)

CELLS = [
    # (lambda, strength, tag)
    (0.90, 1.0,  "memk_l090_s10"),
    (0.95, 1.0,  "memk_l095_s10"),
    (0.95, 2.0,  "memk_l095_s20"),
]
SEEDS = list(range(30))


def main() -> None:
    base = yaml.safe_load(BASE.read_text())
    n = 0
    for lam, strength, tag in CELLS:
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            cfg["simulator"]["memory_kernel_lambda"] = lam
            cfg["simulator"]["memory_kernel_strength"] = strength
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
