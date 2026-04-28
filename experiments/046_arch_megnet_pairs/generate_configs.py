"""MEGNet pairs — Tier 4.1 × {1.1, 3.1, 2.1} × 5 seeds.

The most actionable composability questions for u:

1. ``4_1+1_1`` — global state + per-agent memory. u consumes ⟨h_agent⟩
   in its update, and pair kernel sees u; agent memory feeds external
   context. Tightest "memory hierarchy" combo.
2. ``4_1+3_1`` — global state + ISAB attention. Both make pair kernel
   global-aware via different mechanisms (concat u vs. attention
   bottleneck). Direct comparison + composition.
3. ``4_1+2_1`` — global state + jumps. u shapes the V surface; jumps
   add discrete events. Orthogonal axes that should compose if either
   matters.

Run on Mac:
    conda run -n ecophys python experiments/046_arch_megnet_pairs/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import emit_seeded, stack_overrides  # noqa: E402


PAIRS = [
    ("p_4_1__1_1", ("tier_4_1_megnet", "tier_1_1_memory"),
     "Pair: MEGNet global state + per-agent GRU memory"),
    ("p_4_1__3_1", ("tier_4_1_megnet", "tier_3_1_isab"),
     "Pair: MEGNet global state + ISAB attention pairwise"),
    ("p_4_1__2_1", ("tier_4_1_megnet", "tier_2_1_jumps"),
     "Pair: MEGNet global state + compound-Poisson jumps"),
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
