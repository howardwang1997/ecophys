"""073 — Hawkes & jump ablation: where's the AR(1) drift coming from?

The architecture has two memory-injecting components beyond the base Langevin:
  1. Hawkes self-excitation in price formation:
     dp = β·ED + κ·M, where M_t = κ_alpha · (1-α)·M_{t-1} + α·|r_t|
     This is EXPLICIT memory — past returns drive current price velocity.
  2. Compound-Poisson jumps in agent state (jump_lambda, jump_scale):
     In training mode this is `tanh(s)` drift correction, which is autocorrelated
     across steps because tanh(s_{t+1}) ≈ tanh(s_t) when s changes slowly.

Hypothesis: jumps' tanh correction is the main culprit, not Hawkes (Hawkes
modulates volume but is orthogonal to first-order autocorr in returns).
Ablate each at 6 seeds (probe). 064 baseline: hawkes_kappa=0.3, jump_lambda=0.5.

Cells (12 cells total × 6 seeds = 72 runs, but plan said 48 — trimming):
  hawkes_k0    κ=0    (no Hawkes)
  hawkes_k015  κ=0.15 (half)
  hawkes_k06   κ=0.6  (double)
  jump_l0      λ=0    (no jumps)
  jump_l025    λ=0.25 (half)
  jump_l1      λ=1.0  (double)
  no_hawkes_no_jumps  κ=0, λ=0  (clean Langevin baseline)
  no_hawkes_l1        κ=0, λ=1.0
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "064_winner_50seed_repro" / "config_p_4_2__2_1_seed51.yaml"
OUT = REPO / "experiments" / "073_hawkes_jump_ablation"
OUT.mkdir(parents=True, exist_ok=True)

CELLS = [
    # (tag, hawkes_kappa, jump_lambda)
    ("hawkes_k0",          0.0, 0.5),
    ("hawkes_k015",        0.15, 0.5),
    ("hawkes_k06",         0.6, 0.5),
    ("jump_l0",            0.3, 0.0),
    ("jump_l025",          0.3, 0.25),
    ("jump_l1",            0.3, 1.0),
    ("no_hawkes_no_jumps", 0.0, 0.0),
    ("no_hawkes_l1",       0.0, 1.0),
]
SEEDS = list(range(6))


def main() -> None:
    base = yaml.safe_load(BASE.read_text())
    n = 0
    for tag, kappa, jump_l in CELLS:
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            cfg["simulator"]["price_formation_kwargs"]["hawkes_kappa"] = float(kappa)
            cfg["simulator"]["jump_lambda"] = float(jump_l)
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(
                yaml.safe_dump(cfg, sort_keys=False)
            )
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
