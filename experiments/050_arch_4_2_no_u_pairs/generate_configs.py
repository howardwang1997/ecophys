"""Tier 4.2_no_u (the 6.10/11 winner) paired with other tiers.

The breakthrough was ``t42_dyngraph_no_u`` alone at mean 6.10/11. This
dir tests which OTHER tiers compose constructively with the gate.
We deliberately use the ``no_u`` variant (gate doesn't see u) since
adding u to the gate empirically HURTS (047: dyngraph 6.10 → 4.60 with
u). Same reason for skipping ``+ 4.1 megnet`` here — that was 4.60 in
047 already.

Pairs (4 cells × 10 seeds = 40 configs):
1. ``p_42nu__1_1`` — gate + per-agent memory
2. ``p_42nu__1_2`` — gate + heterogeneous K² kernel heads
3. ``p_42nu__1_3`` — gate + extra pair features (both LN on)
4. ``p_42nu__2_1`` — gate + compound-Poisson jumps

Skipped: ``+ 3.1 ISAB`` (changes pairwise_kind so gate is silently
inert).

Run on Mac:
    conda run -n ecophys python experiments/050_arch_4_2_no_u_pairs/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import emit_seeded, stack_overrides  # noqa: E402


PAIRS = [
    ("p_42nu__1_1", ("tier_4_2_dyngraph_no_u", "tier_1_1_memory"),
     "Pair: gate (no u) + per-agent memory"),
    ("p_42nu__1_2", ("tier_4_2_dyngraph_no_u", "tier_1_2_kernels"),
     "Pair: gate (no u) + heterogeneous kernel heads"),
    ("p_42nu__1_3", ("tier_4_2_dyngraph_no_u", "tier_1_3_features_all"),
     "Pair: gate (no u) + extra pair features (LN on both)"),
    ("p_42nu__2_1", ("tier_4_2_dyngraph_no_u", "tier_2_1_jumps"),
     "Pair: gate (no u) + compound-Poisson jumps"),
]


def main() -> None:
    total = 0
    for cell, keys, comment in PAIRS:
        ov = stack_overrides(*keys)
        n = emit_seeded(HERE, cell, ov, n_seeds=10, comment_prefix=comment)
        total += n
        print(f"  {cell:18s} ({'+'.join(keys)})  → {n} configs")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
