"""063 — re-test architectural Tiers (1.1 / 1.2 / 2.2 / 3.1) against the
4.2 + 2.1 winner baseline.

Earlier sprints tested these tiers in isolation (037-042) at the OLD
baseline (no Tier 4.2 dyngraph). Now that 4.2 + 2.1 is the new floor,
we should re-test whether stacking these on top still helps:

1. ``+ 1_1`` (per-agent memory) — already in 054 with 5 seeds; re-run with
   8 seeds for tighter CI
2. ``+ 1_2`` (heterogeneous K² kernels) — already in 054 with 5 seeds
3. ``+ 2_2`` (multi-timescale slow/fast) — NEW: never tested at 4.2
4. ``+ 3_1`` (ISAB attention) — NEW: replaces stochastic_mlp, kept gate
   off because gate is per-edge for sps; 3.1 has different topology

Grid (4 × 8 seeds = 32 configs).

Cell name: ``re_42_21_{tier}``.

Run on Mac:
    conda run -n ecophys python experiments/063_winner_arch_retest/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import deep_merge, emit_seeded, stack_overrides  # noqa: E402


# Note: 3.1 isab uses different pairwise_kind, so the 4.2 dyngraph gating
# (which targets stochastic_mlp's edge sampling) is automatically a no-op
# under isab — we keep the flag on for consistency but the gate isn't
# physically gating anything. Treat 3.1 cell as an "is ISAB-attention
# better than gated stochastic_mlp at all?" test.

CELLS = [
    ("re_42_21_11", ("tier_4_2_dyngraph", "tier_2_1_jumps", "tier_1_1_memory"),
     "Re-test: full 4.2 + 2.1 + 1.1 memory"),
    ("re_42_21_12", ("tier_4_2_dyngraph", "tier_2_1_jumps", "tier_1_2_kernels"),
     "Re-test: full 4.2 + 2.1 + 1.2 K² kernels"),
    ("re_42_21_22", ("tier_4_2_dyngraph", "tier_2_1_jumps", "tier_2_2_multitimescale"),
     "Re-test: full 4.2 + 2.1 + 2.2 multi-timescale (NEW)"),
    ("re_42_21_31", ("tier_4_2_dyngraph", "tier_2_1_jumps", "tier_3_1_isab"),
     "Re-test: full 4.2 + 2.1 + 3.1 ISAB attention (NEW pairwise_kind=isab)"),
]


def main() -> None:
    total = 0
    for cell, keys, comment in CELLS:
        ov = stack_overrides(*keys)
        n = emit_seeded(HERE, cell, ov, n_seeds=8, comment_prefix=comment)
        total += n
        print(f"  {cell:14s} ({'+'.join(keys)})  → {n} configs")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
