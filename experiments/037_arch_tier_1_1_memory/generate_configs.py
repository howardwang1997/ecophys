"""Tier 1.1 — Per-agent GRU memory. 10 seeds.

Hypothesis: short-term per-agent memory helps DFA Hurst, zumbach
asymmetry, autocorr-of-returns. Base = abl_no_chunk128 (mean 3.20).

Run on Mac:
    conda run -n ecophys python experiments/037_arch_tier_1_1_memory/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import TIER_OVERRIDES, emit_seeded  # noqa: E402


def main() -> None:
    n = emit_seeded(
        HERE,
        cell_name="t11_memory",
        cell_overrides=TIER_OVERRIDES["tier_1_1_memory"],
        n_seeds=10,
        comment_prefix="Tier 1.1 — per-agent GRU memory (d_memory=16)",
    )
    print(f"wrote {n} configs to {HERE}/")


if __name__ == "__main__":
    main()
