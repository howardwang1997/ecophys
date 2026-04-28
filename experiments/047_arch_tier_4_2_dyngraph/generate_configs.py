"""Tier 4.2 — Soft edge gating (dynamic graph). 2 cells × 10 seeds.

- ``t42_dyngraph_no_u`` — gate uses only (s_i, s_j, |Δs|). Tests whether
  pure state-conditioned topology dynamics break the basin ceiling
  WITHOUT regime conditioning.
- ``t42_dyngraph`` — full dynamic graph: gate sees u; u also feeds pair
  kernel + external context (Tier 4.1 active). Topology + phase coupling.

Compare these two cells to isolate the value of regime conditioning on
the gate (i.e., does u inside the gate matter, or is plain state-aware
gating enough?).

Run on Mac:
    conda run -n ecophys python experiments/047_arch_tier_4_2_dyngraph/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import TIER_OVERRIDES, emit_seeded  # noqa: E402


def main() -> None:
    n1 = emit_seeded(
        HERE,
        cell_name="t42_dyngraph_no_u",
        cell_overrides=TIER_OVERRIDES["tier_4_2_dyngraph_no_u"],
        n_seeds=10,
        comment_prefix="Tier 4.2 — soft edge gating (gate sees s only, no u)",
    )
    n2 = emit_seeded(
        HERE,
        cell_name="t42_dyngraph",
        cell_overrides=TIER_OVERRIDES["tier_4_2_dyngraph"],
        n_seeds=10,
        comment_prefix="Tier 4.2 — soft edge gating + Tier 4.1 u (gate sees u)",
    )
    print(f"  t42_dyngraph_no_u  → {n1} configs")
    print(f"  t42_dyngraph       → {n2} configs")
    print(f"\nwrote {n1 + n2} configs to {HERE}/")


if __name__ == "__main__":
    main()
