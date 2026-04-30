"""064 — 50-seed reproduction of the current winner (`p_4_2__2_1`).

After 052 (35 seeds, mean 5.40) we have honest CI for the canonical
winner. This dir bumps to 50 seeds (with seeds 35..84, non-overlapping
with 048+052) to get the tightest possible single-cell CI.

Cell name: ``p_4_2__2_1`` (matches 048+052 so per-fact analysis treats
the merged 85-seed population as one cell).

Run on Mac:
    conda run -n ecophys python experiments/064_winner_50seed_repro/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import deep_merge, stack_overrides, write_config  # noqa: E402


def main() -> None:
    cell_overrides = stack_overrides("tier_4_2_dyngraph", "tier_2_1_jumps")
    n = 0
    for seed in range(35, 85):  # seeds non-overlapping with 048 (0-4) + 052 (5-34)
        seeded = deep_merge(cell_overrides, {"training": {"seed": seed}})
        write_config(
            HERE,
            f"p_4_2__2_1_seed{seed}",
            f"Winner 50-seed deep repro — full 4.2 + 2.1 jumps, seed={seed}",
            seeded,
        )
        n += 1
    print(f"wrote {n} configs to {HERE}/")


if __name__ == "__main__":
    main()
