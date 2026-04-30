"""Reproduce p_4_2__2_1 (the 048 9/11 winner) at 30 seeds.

048 cell ``p_4_2__2_1`` (full Tier 4.2 dyngraph WITH u + Tier 2.1 jumps)
produced 5-seed mean **7.20/11**, max 9/11 — the project record. But
5 seeds is small; the previous "winner" t42_dyngraph_no_u went from
5-seed mean 6.10 down to 30-seed mean 5.40 (regression to the mean).

This dir extends to seeds 5..34 so we can compute a tight CI on the
7.20 number. Cell name ``p_4_2__2_1`` matches 048 so per-fact analysis
treats both as one population (5 + 30 = 35 seeds total).

Run on Mac:
    conda run -n ecophys python experiments/052_p_4_2__2_1_repro/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import deep_merge, stack_overrides, write_config  # noqa: E402


def main() -> None:
    cell_overrides = stack_overrides("tier_4_2_dyngraph", "tier_2_1_jumps")
    n = 0
    for seed in range(5, 35):  # extend 048 (which used seeds 0-4)
        seeded = deep_merge(cell_overrides, {"training": {"seed": seed}})
        write_config(
            HERE,
            f"p_4_2__2_1_seed{seed}",
            f"Repro 048 winner — full 4.2 + 2.1 jumps, seed={seed}",
            seeded,
        )
        n += 1
    print(f"wrote {n} configs to {HERE}/")


if __name__ == "__main__":
    main()
