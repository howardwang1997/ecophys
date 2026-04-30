"""v2_type_seed sweep — test whether p_4_2__2_1's 5.40 mean is robust
to agent-type assignment.

All prior experiments fix ``v2_type_seed=42``. The 11-fact CI we report
(35-seed [4.86, 5.97]) is conditional on this single type assignment.
A reviewer would ask: "does the result hold when type_seed varies?"
This dir answers that: 4 type seeds × 3 training seeds = 12 configs.

Cell name: ``ts{type_seed}`` — e.g. ``ts7_seed0`` is type_seed=7,
training seed=0.

Run on Mac:
    conda run -n ecophys python experiments/056_v2_type_seed_sweep/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import deep_merge, emit_seeded, stack_overrides  # noqa: E402


TYPE_SEEDS = [7, 13, 100, 999]


def main() -> None:
    base = stack_overrides("tier_4_2_dyngraph", "tier_2_1_jumps")
    total = 0
    for ts in TYPE_SEEDS:
        ov = deep_merge(base, {"simulator": {"v2_type_seed": ts}})
        cell = f"ts{ts}"
        k = emit_seeded(
            HERE,
            cell,
            ov,
            n_seeds=3,
            comment_prefix=f"v2_type_seed={ts} CI test",
        )
        total += k
        print(f"  {cell:8s} (v2_type_seed={ts:>4d})  → {k} configs")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
