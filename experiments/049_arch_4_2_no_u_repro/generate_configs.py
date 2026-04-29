"""Tier 4.2 reproducibility: 30 more seeds of t42_dyngraph_no_u.

Initial 047 cell ``t42_dyngraph_no_u`` (10 seeds) hit mean **6.10/11**
with top 9/11 — the highest result of the whole arch-extensions sprint.
But 10 seeds is too few for a tight CI; this dir extends to seeds
10-39 (30 more), bringing total to 40 seeds across 047 + 049.

Cell name same as 047 so per-fact analysis treats it as one
population: ``t42_dyngraph_no_u_seed{10..39}``.

Run on Mac:
    conda run -n ecophys python experiments/049_arch_4_2_no_u_repro/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import TIER_OVERRIDES, deep_merge, write_config  # noqa: E402


def main() -> None:
    cell_overrides = TIER_OVERRIDES["tier_4_2_dyngraph_no_u"]
    n = 0
    for seed in range(10, 40):  # extend 047 (which used seeds 0-9)
        seeded = deep_merge(cell_overrides, {"training": {"seed": seed}})
        write_config(
            HERE,
            f"t42_dyngraph_no_u_seed{seed}",
            f"Tier 4.2 reproducibility — gate without u, seed={seed}",
            seeded,
        )
        n += 1
    print(f"wrote {n} configs to {HERE}/")


if __name__ == "__main__":
    main()
