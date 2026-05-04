"""076 — collective coordinate price formation 30-seed sweep.

Hypothesis: the hand-crafted ``ED = κ·Σ(Δs[:,0])`` price formation has no
physical motivation (just uses the FIRST state coord as "position"). A
collective coordinate p = soft-aggregate(intent(s_i)) over the FULL agent
state is the standard non-equilibrium statistical-mechanics treatment of
slow observables (Mori-Zwanzig). Should give cleaner FDT/Jarzynski.

Empirical question: does swapping ExcessDemand → Collective fix or break
the stylized facts?

Cells (cross with E1's γ=10 fix and adiabatic):
  collective_g1          — collective price + γ=1 baseline (matched 064)
  collective_g10         — collective price + γ=10 (E1 fix)
  collective_g10_inner5  — collective price + γ=10 + adiabatic inner=5

3 cells × 30 seeds = 90 configs.

Note: CollectivePrice has NO Hawkes self-excitation by design (kept clean
for FDT/Jarzynski). For matched comparison vs baseline excess_demand which
has hawkes_kappa=0.3, expect some difference attributable to that alone.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "064_winner_50seed_repro" / "config_p_4_2__2_1_seed51.yaml"
OUT = REPO / "experiments" / "076_collective_price_30seed"
OUT.mkdir(parents=True, exist_ok=True)

# CollectiveParams keys — must match dataclass fields exactly.
COLLECTIVE_KWARGS = {
    "beta": 0.5,
    "sigma_price": 0.005,
    "ewma_alpha": 0.05,
    "initial_log_price": 0.0,
    "intent_hidden": 16,
    "learnable_weight": False,
    "sigma_ed": 0.0,
}


def _make_collective_base(base: dict) -> dict:
    cfg = copy.deepcopy(base)
    cfg["simulator"]["price_formation"] = "collective"
    cfg["simulator"]["price_formation_kwargs"] = dict(COLLECTIVE_KWARGS)
    return cfg


def _make_g1(base: dict) -> dict:
    cfg = _make_collective_base(base)
    cfg["simulator"]["temperature_init"] = 0.05
    cfg["simulator"]["gamma_init"] = 1.0
    cfg["simulator"]["learn_temperature"] = False
    cfg["simulator"]["learn_gamma"] = False
    return cfg


def _make_g10(base: dict) -> dict:
    cfg = _make_collective_base(base)
    cfg["simulator"]["temperature_init"] = 0.05
    cfg["simulator"]["gamma_init"] = 10.0
    cfg["simulator"]["learn_temperature"] = False
    cfg["simulator"]["learn_gamma"] = False
    return cfg


def _make_g10_inner5(base: dict) -> dict:
    cfg = _make_g10(base)
    cfg["simulator"]["inner_steps_per_price"] = 5
    return cfg


CELLS = [
    ("collective_g1",          _make_g1),
    ("collective_g10",         _make_g10),
    ("collective_g10_inner5",  _make_g10_inner5),
]
SEEDS = list(range(30))


def main() -> None:
    base = yaml.safe_load(BASE.read_text())
    n = 0
    for tag, builder in CELLS:
        for s in SEEDS:
            cfg = builder(base)
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(
                yaml.safe_dump(cfg, sort_keys=False)
            )
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
