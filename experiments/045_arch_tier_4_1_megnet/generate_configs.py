"""Tier 4.1 — MEGNet-style global state. 10 seeds × 2 cells.

Two cells per the ablation question "is pair-side injection necessary?":
- ``t41_megnet`` — u feeds BOTH external context AND pair kernel input.
- ``t41_megnet_ext_only`` — u feeds external only (no pair injection).

If both reach the same mean, the pair-side path is null and we can
drop it (cheaper). If pair-side wins, that confirms the orthogonal-basin
mechanism: shaping V via global phase is what matters, not just
modulating per-agent context.

Run on Mac:
    conda run -n ecophys python experiments/045_arch_tier_4_1_megnet/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import TIER_OVERRIDES, emit_seeded  # noqa: E402


def main() -> None:
    n1 = emit_seeded(
        HERE,
        cell_name="t41_megnet",
        cell_overrides=TIER_OVERRIDES["tier_4_1_megnet"],
        n_seeds=10,
        comment_prefix="Tier 4.1 — MEGNet global state, u into pair AND external",
    )
    n2 = emit_seeded(
        HERE,
        cell_name="t41_megnet_ext_only",
        cell_overrides=TIER_OVERRIDES["tier_4_1_megnet_external_only"],
        n_seeds=10,
        comment_prefix="Tier 4.1 ablation — u into external ONLY (pair kernel context-free)",
    )
    print(f"  t41_megnet           → {n1} configs")
    print(f"  t41_megnet_ext_only  → {n2} configs")
    print(f"\nwrote {n1 + n2} configs to {HERE}/")


if __name__ == "__main__":
    main()
