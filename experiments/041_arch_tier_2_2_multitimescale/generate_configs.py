"""Tier 2.2 — Multi-timescale per-agent mask. 10 seeds.

80% of agents update every step (fast); the other 20% update only every
4th step (slow). All agents always contribute to forces. Hypothesis:
multi-scale temporal structure helps DFA Hurst, zumbach asymmetry.

Run on Mac:
    conda run -n ecophys python experiments/041_arch_tier_2_2_multitimescale/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import TIER_OVERRIDES, emit_seeded  # noqa: E402


def main() -> None:
    n = emit_seeded(
        HERE,
        cell_name="t22_multitimescale",
        cell_overrides=TIER_OVERRIDES["tier_2_2_multitimescale"],
        n_seeds=10,
        comment_prefix="Tier 2.2 — multi-timescale (fast_frac=0.8, slow_freq=4)",
    )
    print(f"wrote {n} configs to {HERE}/")


if __name__ == "__main__":
    main()
