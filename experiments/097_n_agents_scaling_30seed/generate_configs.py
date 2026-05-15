"""097 — n_agents scaling ablation (reviewer-2 anticipated question).

Reviewer-2 will ask: "is the depth-2 compositional ceiling N_agents-
dependent? Maybe with 5× the agents the swarm exits the Pareto frontier."

Answer: run the projected hero pair (pair_zumdn_b3) at 3 swarm sizes ×
n=30 seeds. If mean is N-independent (within 1 std), the ceiling is
architectural, not statistical. If mean rises monotonically with N,
the falsification claim weakens.

Cells (3 swarm sizes × 30 seeds = 90 cfg ≈ ~2h H20):
  scale_n500_pair_zumdn_b3      — N = 500   (small swarm)
  scale_n1000_pair_zumdn_b3     — N = 1000  (mid)
  scale_n5000_pair_zumdn_b3     — N = 5000  (large)

The 089 baseline used N=10000 (default in 069 config), so 10000 is the
canonical reference. We choose 500, 1000, 5000 as three log-spaced
points below the default — testing the SMALLER end. The "is bigger
better?" question is partly answered by 089 baseline using N=10000 and
mean=4.82, and pair_zumdn_b3 at N=10000 being run in 090.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "097_n_agents_scaling_30seed"
OUT.mkdir(parents=True, exist_ok=True)


def apply_zumdn(cfg):
    cfg["simulator"]["zumbach_feedback_lambda"] = 0.95
    cfg["simulator"]["zumbach_feedback_strength"] = 1.0
    cfg["simulator"]["zumbach_feedback_mode"] = "downside"


def apply_b3(cfg):
    cfg["simulator"]["regime_enabled"] = True
    cfg["simulator"]["regime_discrete_enabled"] = True
    cfg["simulator"]["regime_n_states"] = 3
    cfg["simulator"]["regime_gumbel_tau"] = 1.0


N_AGENTS_VALUES = [500, 1000, 5000]


def main() -> None:
    base_spx = yaml.safe_load(BASE_SPX.read_text())
    n = 0
    for n_agents in N_AGENTS_VALUES:
        tag = f"scale_n{n_agents}_pair_zumdn_b3"
        for seed in range(30):
            cfg = copy.deepcopy(base_spx)
            apply_zumdn(cfg)
            apply_b3(cfg)
            cfg["simulator"]["n_agents"] = n_agents
            cfg["training"]["seed"] = seed
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs across {len(N_AGENTS_VALUES)} N-values to {OUT}")


if __name__ == "__main__":
    main()
