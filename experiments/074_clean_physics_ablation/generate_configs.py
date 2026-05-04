"""074 — clean-physics ablation: which arch components inject memory beyond
the base Langevin?

The architecture has gradient-of-potential force (verified — see
potentials.py:502 conservative_forces uses torch.autograd.grad on a scalar
StochasticPairwisePotential). So Tier A1 was already in v0 design. The
autocorr=0.6 problem is from OTHER memory injectors:

  1. Hawkes self-excitation in price formation (memory in price returns)
  2. global_state_into_pair (mean-field ⟨s⟩ feeds back into per-pair force →
     induces collective slow mode)
  3. twopop low-γ sub-population (γ_scale=0.5 → 200-step velocity memory)
  4. pair_input_layernorm (forces U scale-invariant in s → too smooth)
  5. jump_lambda tanh drift correction (autocorrelated across steps because
     tanh(s_{t+1}) ≈ tanh(s_t) when s changes slowly)

Cross with E1 finding: γ damping at γ=10 (γ·dt=0.1) cuts ac_r in half.

5 cells × 30 seeds = 150 runs. All cells freeze T=0.05/γ=10 (E1's overdamped
fix). Each cell strips ONE memory component to attribute the residual ac_r:

  clean_g10_baseline   — γ=10, all v3 features ON  (matched 064 + γ fix)
  clean_g10_no_LN      — γ=10, pair_input_layernorm=False
  clean_g10_no_twopop  — γ=10, twopop_enabled=False
  clean_g10_no_gpair   — γ=10, global_state_into_pair=False (still has u for external)
  clean_g10_minimal    — γ=10 + ALL of the above OFF + jump_lambda=0 + hawkes_kappa=0
                         (cleanest physics, expected lowest ac_r)
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "064_winner_50seed_repro" / "config_p_4_2__2_1_seed51.yaml"
OUT = REPO / "experiments" / "074_clean_physics_ablation"
OUT.mkdir(parents=True, exist_ok=True)

SEEDS = list(range(30))


def _freeze_thermo(cfg: dict, T: float = 0.05, g: float = 10.0) -> None:
    cfg["simulator"]["temperature_init"] = T
    cfg["simulator"]["gamma_init"] = g
    cfg["simulator"]["learn_temperature"] = False
    cfg["simulator"]["learn_gamma"] = False


def _make_baseline(base: dict) -> dict:
    cfg = copy.deepcopy(base)
    _freeze_thermo(cfg)
    return cfg


def _make_no_ln(base: dict) -> dict:
    cfg = _make_baseline(base)
    cfg["simulator"]["pair_input_layernorm"] = False
    return cfg


def _make_no_twopop(base: dict) -> dict:
    cfg = _make_baseline(base)
    cfg["simulator"]["twopop_enabled"] = False
    return cfg


def _make_no_gpair(base: dict) -> dict:
    cfg = _make_baseline(base)
    # Keep global_state ON for external context, but stop feeding u into pair MLP
    cfg["simulator"]["global_state_into_pair"] = False
    return cfg


def _make_minimal(base: dict) -> dict:
    cfg = _make_baseline(base)
    cfg["simulator"]["pair_input_layernorm"] = False
    cfg["simulator"]["twopop_enabled"] = False
    cfg["simulator"]["global_state_into_pair"] = False
    cfg["simulator"]["jump_lambda"] = 0.0
    cfg["simulator"]["price_formation_kwargs"]["hawkes_kappa"] = 0.0
    return cfg


CELLS = [
    ("clean_g10_baseline",  _make_baseline),
    ("clean_g10_no_LN",     _make_no_ln),
    ("clean_g10_no_twopop", _make_no_twopop),
    ("clean_g10_no_gpair",  _make_no_gpair),
    ("clean_g10_minimal",   _make_minimal),
]


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
