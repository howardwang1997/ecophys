"""Triples extending the 048 9/11 winner — full 4.2 + 2.1 jumps + (X).

Building on ``p_4_2__2_1`` (mean 7.20/11, max 9/11), test whether
adding a third tier pushes us to 8+/11 reproducibly:

1. ``+ 1_1`` (per-agent memory) — local regime memory might stabilize
   the gate's edge selection across timesteps.
2. ``+ 1_2`` (heterogeneous K² kernels) — let buyer-buyer vs buyer-seller
   pairs use different MLPs even after gating.
3. ``+ 1_3`` (extra pair features) — distance + inner-prod might be the
   info the gate needs to be more selective.

5 seeds each = 15 configs.

Run on Mac:
    conda run -n ecophys python experiments/054_p_4_2__2_1_triples/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import emit_seeded, stack_overrides  # noqa: E402


TRIPLES = [
    ("tri_42_21_11", ("tier_4_2_dyngraph", "tier_2_1_jumps", "tier_1_1_memory"),
     "Triple: 4.2 dyngraph + 2.1 jumps + 1.1 memory"),
    ("tri_42_21_12", ("tier_4_2_dyngraph", "tier_2_1_jumps", "tier_1_2_kernels"),
     "Triple: 4.2 dyngraph + 2.1 jumps + 1.2 K² kernels"),
    ("tri_42_21_13", ("tier_4_2_dyngraph", "tier_2_1_jumps", "tier_1_3_features_all"),
     "Triple: 4.2 dyngraph + 2.1 jumps + 1.3 pair features"),
]


def main() -> None:
    total = 0
    for cell, keys, comment in TRIPLES:
        ov = stack_overrides(*keys)
        n = emit_seeded(HERE, cell, ov, n_seeds=5, comment_prefix=comment)
        total += n
        print(f"  {cell:18s} ({'+'.join(keys)})  → {n} configs")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
