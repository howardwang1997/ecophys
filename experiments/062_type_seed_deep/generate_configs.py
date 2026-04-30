"""062 — v2_type_seed deep CI (paper-grade).

056 uses 4 type_seeds × 3 seeds = 12 cfgs as a quick smoke. This dir
deepens to 8 type_seeds × 5 seeds = 40 cfgs for a paper-quality
robustness claim.

Grid: type_seed ∈ {3, 7, 13, 42, 100, 256, 999, 4242} × 5 training seeds.

Cell name: ``ts{type_seed}``.

Run on Mac:
    conda run -n ecophys python experiments/062_type_seed_deep/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import deep_merge, emit_seeded, stack_overrides  # noqa: E402


TYPE_SEEDS = [3, 7, 13, 42, 100, 256, 999, 4242]


def main() -> None:
    base = stack_overrides("tier_4_2_dyngraph", "tier_2_1_jumps")
    total = 0
    for ts in TYPE_SEEDS:
        ov = deep_merge(base, {"simulator": {"v2_type_seed": ts}})
        cell = f"ts{ts}"
        n = emit_seeded(
            HERE, cell, ov, n_seeds=5,
            comment_prefix=f"type_seed={ts} CI",
        )
        total += n
        print(f"  {cell:8s} (type_seed={ts:>5d})  → {n} configs")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
