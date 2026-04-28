"""Tier 1.3 — Pair feature redesign (distance + inner_prod + signed_diff).
10 seeds.

Hypothesis: richer pair inputs (||Δs|| + ⟨s_i,s_j⟩ + signed Δs) let the
pair MLP express asymmetric force kernels that the |Δs| baseline cannot.

Run on Mac:
    conda run -n ecophys python experiments/039_arch_tier_1_3_features/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import TIER_OVERRIDES, emit_seeded  # noqa: E402


def main() -> None:
    n = emit_seeded(
        HERE,
        cell_name="t13_features_all",
        cell_overrides=TIER_OVERRIDES["tier_1_3_features_all"],
        n_seeds=10,
        comment_prefix="Tier 1.3 — pair_features_extra='all' (distance+innerprod+signed)",
    )
    print(f"wrote {n} configs to {HERE}/")


if __name__ == "__main__":
    main()
