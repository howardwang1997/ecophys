"""Tier 1.2 — Heterogeneous (type-aware) pair kernel heads. 10 seeds.

Hypothesis: K² last-layer heads routed by (type_src, type_dst) make
fund/MM/HFT/retail mixing produce richer dynamics — expect to help
volume_corr, gain_loss. Base = abl_no_chunk128 (mean 3.20). Reuses
twopop type assignment (4 types).

Run on Mac:
    conda run -n ecophys python experiments/038_arch_tier_1_2_kernels/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import TIER_OVERRIDES, emit_seeded  # noqa: E402


def main() -> None:
    n = emit_seeded(
        HERE,
        cell_name="t12_kernels",
        cell_overrides=TIER_OVERRIDES["tier_1_2_kernels"],
        n_seeds=10,
        comment_prefix="Tier 1.2 — heterogeneous pair-kernel heads (K=4 → 16 heads)",
    )
    print(f"wrote {n} configs to {HERE}/")


if __name__ == "__main__":
    main()
