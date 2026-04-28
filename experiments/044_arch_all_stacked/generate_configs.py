"""All-stacked — every architectural tier ON simultaneously × 10 seeds.

Counterpart of 035_stacked_winner (which stacked hyperparameter knobs
and got mean 2.40 — WORSE than singletons). This 044 stacks
ARCHITECTURAL changes — if architectures compose better than
hyperparameters did, mean here should beat the single-tier means in
037-042. If 044 also degenerates (back near 2-3/11), the composition
problem is fundamental and we'll need to switch to mixture-of-experts
or curriculum strategies.

Combination — all 6 tiers active simultaneously. Note that under
pairwise_kind=isab, the stochastic-mlp-only flags
(pair_heterogeneous_heads, pair_features_extra) are ignored; we still
set them for self-documentation.

Run on Mac:
    conda run -n ecophys python experiments/044_arch_all_stacked/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import emit_seeded, stack_overrides  # noqa: E402


def main() -> None:
    # Two stacked variants: one keeps stochastic_mlp pairwise (so 1_2/1_3
    # actually take effect) — all tiers minus ISAB.
    stack_no_isab = stack_overrides(
        "tier_1_1_memory",
        "tier_1_2_kernels",
        "tier_1_3_features_all",
        "tier_2_1_jumps",
        "tier_2_2_multitimescale",
    )
    n1 = emit_seeded(
        HERE, "stack_no_isab", stack_no_isab, n_seeds=5,
        comment_prefix="All-stacked except ISAB (keeps stochastic_mlp + 1_2 + 1_3)",
    )

    # The other replaces pairwise with ISAB; 1_2/1_3 inactive there.
    stack_with_isab = stack_overrides(
        "tier_1_1_memory",
        "tier_2_1_jumps",
        "tier_2_2_multitimescale",
        "tier_3_1_isab",
    )
    n2 = emit_seeded(
        HERE, "stack_with_isab", stack_with_isab, n_seeds=5,
        comment_prefix="All-stacked with ISAB pairwise (1_2/1_3 inactive)",
    )

    print(f"  stack_no_isab    → {n1} configs")
    print(f"  stack_with_isab  → {n2} configs")
    print(f"\nwrote {n1 + n2} configs to {HERE}/")


if __name__ == "__main__":
    main()
