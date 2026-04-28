"""Dynamic-graph pair combos — 3 hand-picked × 5 seeds = 15 configs.

Tests whether soft edge gating composes constructively with other tiers:

1. ``4_2 + 1_1`` — dynamic graph + per-agent memory. Gate selects which
   neighbours matter; per-agent memory remembers regime locally.
2. ``4_2 + 2_1`` — dynamic graph + jumps. Gate may concentrate budget
   on cascade-forming pairs during jump events.
3. ``4_2 + 1_3`` — dynamic graph + extra pair features. Richer per-pair
   info should make the gate more selective.

Run on Mac:
    conda run -n ecophys python experiments/048_arch_dyngraph_pairs/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import emit_seeded, stack_overrides  # noqa: E402


PAIRS = [
    ("p_4_2__1_1", ("tier_4_2_dyngraph", "tier_1_1_memory"),
     "Pair: dynamic graph + per-agent GRU memory"),
    ("p_4_2__2_1", ("tier_4_2_dyngraph", "tier_2_1_jumps"),
     "Pair: dynamic graph + compound-Poisson jumps"),
    ("p_4_2__1_3", ("tier_4_2_dyngraph", "tier_1_3_features_all"),
     "Pair: dynamic graph + extra pair features"),
]


def main() -> None:
    total = 0
    for cell, keys, comment in PAIRS:
        ov = stack_overrides(*keys)
        n = emit_seeded(HERE, cell, ov, n_seeds=5, comment_prefix=comment)
        total += n
        print(f"  {cell:18s} ({'+'.join(keys)})  → {n} configs")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
