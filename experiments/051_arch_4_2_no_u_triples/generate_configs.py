"""Tier 4.2_no_u + 1.3 + (third tier) — triple stacks of the top winners.

If 050's pairs show 4.2_no_u + 1.3 doesn't NaN (LN on both), then
stacking a third winner could push above the 6.10 baseline. Picks the
three most-promising third tiers based on today's 045-048 data.

Triples (4 cells × 5 seeds = 20 configs):
1. ``tri_42nu_1_3_1_1`` — gate + features + memory  (top 3 single tiers)
2. ``tri_42nu_1_3_1_2`` — gate + features + het kernels
3. ``tri_42nu_1_3_2_1`` — gate + features + jumps
4. ``tri_42nu_1_1_2_1`` — gate + memory + jumps  (alternate, no 1.3)

Run on Mac:
    conda run -n ecophys python experiments/051_arch_4_2_no_u_triples/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import emit_seeded, stack_overrides  # noqa: E402


TRIPLES = [
    ("tri_42nu_1_3_1_1",
     ("tier_4_2_dyngraph_no_u", "tier_1_3_features_all", "tier_1_1_memory"),
     "Triple: gate + features + memory"),
    ("tri_42nu_1_3_1_2",
     ("tier_4_2_dyngraph_no_u", "tier_1_3_features_all", "tier_1_2_kernels"),
     "Triple: gate + features + het kernels"),
    ("tri_42nu_1_3_2_1",
     ("tier_4_2_dyngraph_no_u", "tier_1_3_features_all", "tier_2_1_jumps"),
     "Triple: gate + features + jumps"),
    ("tri_42nu_1_1_2_1",
     ("tier_4_2_dyngraph_no_u", "tier_1_1_memory", "tier_2_1_jumps"),
     "Triple: gate + memory + jumps"),
]


def main() -> None:
    total = 0
    for cell, keys, comment in TRIPLES:
        ov = stack_overrides(*keys)
        n = emit_seeded(HERE, cell, ov, n_seeds=5, comment_prefix=comment)
        total += n
        print(f"  {cell:20s} ({'+'.join(keys)})  → {n} configs")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
