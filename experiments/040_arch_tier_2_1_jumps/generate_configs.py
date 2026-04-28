"""Tier 2.1 — Compound-Poisson jumps (drift correction Option C). 10 seeds.

Training: deterministic drift correction λ·jump_scale·tanh(s)·dt makes
the jump structure backprop-trainable without sampling. Inference:
samples K~Poisson(λ·dt) jumps per agent per dim.

Hypothesis: heavy tails (hill) + gain_loss asymmetry need discrete
jump events that continuous SDE can't reach.

Run on Mac:
    conda run -n ecophys python experiments/040_arch_tier_2_1_jumps/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import TIER_OVERRIDES, emit_seeded  # noqa: E402


def main() -> None:
    n = emit_seeded(
        HERE,
        cell_name="t21_jumps",
        cell_overrides=TIER_OVERRIDES["tier_2_1_jumps"],
        n_seeds=10,
        comment_prefix="Tier 2.1 — compound-Poisson jumps (lambda=0.5, scale=0.01)",
    )
    print(f"wrote {n} configs to {HERE}/")


if __name__ == "__main__":
    main()
