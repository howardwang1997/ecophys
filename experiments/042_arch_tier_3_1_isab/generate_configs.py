"""Tier 3.1 — ISAB attention pairwise potential. 10 seeds.

Replaces the random-pair MLP (stochastic_mlp) with O(N·M) Induced Set
Attention via M=64 learnable inducing points. Two cross-attention layers
let every agent's force depend on global context, not just k=50 random
neighbours. Manual attention (einsum + softmax) so create_graph=True
double-backward works.

Hypothesis: long-range structure — DFA, zumbach, vol clustering across
timescales — needs global information flow per step.

Run on Mac:
    conda run -n ecophys python experiments/042_arch_tier_3_1_isab/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import TIER_OVERRIDES, emit_seeded  # noqa: E402


def main() -> None:
    n = emit_seeded(
        HERE,
        cell_name="t31_isab",
        cell_overrides=TIER_OVERRIDES["tier_3_1_isab"],
        n_seeds=10,
        comment_prefix="Tier 3.1 — ISAB attention pairwise (M=64, n_heads=4)",
    )
    print(f"wrote {n} configs to {HERE}/")


if __name__ == "__main__":
    main()
