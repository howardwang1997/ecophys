"""Pair combinations — 6 hand-picked tier pairs × 5 seeds = 30 configs.

After single-tier results land in 037-042, the pairs test whether any
two tiers compose CONSTRUCTIVELY (vs. the destructive composition we
saw in 035 stacked-winner where mean dropped to 2.40 from 5.00 single).

Pair selection rationale:
1. ``1_1+1_2`` — agent memory + heterogeneous kernels (depth + diversity)
2. ``1_1+2_1`` — agent memory + jumps (memory remembers regime, jumps cover extremes)
3. ``1_2+1_3`` — heterogeneous + pair features (richer kernels)
4. ``2_1+2_2`` — jumps + multi-timescale (both temporal-structure tiers)
5. ``1_1+1_3`` — agent memory + pair features
6. ``3_1+1_3`` — ISAB + pair features (global context + rich edges).
   NOTE: 1_3 is ignored under pairwise_kind=isab; this pair effectively
   degenerates to 3_1 alone. Kept for symmetry, will be deduped in scoring.

Run on Mac:
    conda run -n ecophys python experiments/043_arch_pairs/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import emit_seeded, stack_overrides  # noqa: E402


PAIRS = [
    ("p_1_1__1_2", ("tier_1_1_memory", "tier_1_2_kernels"),
     "Pair: agent memory + heterogeneous kernels"),
    ("p_1_1__2_1", ("tier_1_1_memory", "tier_2_1_jumps"),
     "Pair: agent memory + jumps"),
    ("p_1_2__1_3", ("tier_1_2_kernels", "tier_1_3_features_all"),
     "Pair: heterogeneous kernels + pair features"),
    ("p_2_1__2_2", ("tier_2_1_jumps", "tier_2_2_multitimescale"),
     "Pair: jumps + multi-timescale"),
    ("p_1_1__1_3", ("tier_1_1_memory", "tier_1_3_features_all"),
     "Pair: agent memory + pair features"),
    ("p_3_1__1_3", ("tier_3_1_isab", "tier_1_3_features_all"),
     "Pair: ISAB + pair features (1_3 ignored under isab)"),
]


def main() -> None:
    total = 0
    for cell, keys, comment in PAIRS:
        ov = stack_overrides(*keys)
        n = emit_seeded(HERE, cell, ov, n_seeds=5, comment_prefix=comment)
        total += n
        print(f"  {cell:20s} ({'+'.join(keys)})  → {n} configs")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
