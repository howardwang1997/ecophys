"""Tune jump hyperparameters around the 9/11 winner.

The 048 winner uses ``jump_lambda=0.5, jump_scale=0.01`` (tier_2_1_jumps
defaults). This dir sweeps 3×3 around those values to test whether
the basin is sharp or wide:

    λ ∈ {0.3, 0.5, 1.0}
    σ ∈ {0.005, 0.01, 0.02}
    → 9 combos × 2 seeds = 18 configs

Cell name encodes the params: ``j_l03_s005`` means λ=0.3, σ=0.005.

Run on Mac:
    conda run -n ecophys python experiments/053_p_4_2__2_1_jump_tune/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import deep_merge, emit_seeded, stack_overrides  # noqa: E402


# (λ, σ) grid. Centered on (0.5, 0.01) which is the 048 winner.
GRID = [
    (0.3, 0.005),
    (0.3, 0.01),
    (0.3, 0.02),
    (0.5, 0.005),
    (0.5, 0.01),   # = 048 winner (gives baseline within this dir)
    (0.5, 0.02),
    (1.0, 0.005),
    (1.0, 0.01),
    (1.0, 0.02),
]


def lam_tag(lam: float) -> str:
    return str(lam).replace(".", "")  # 0.3 → "03", 1.0 → "10"


def sig_tag(sig: float) -> str:
    return str(sig).replace(".", "").lstrip("0") or "0"  # 0.005 → "005"


def main() -> None:
    base = stack_overrides("tier_4_2_dyngraph", "tier_2_1_jumps")
    total = 0
    for lam, sig in GRID:
        ov = deep_merge(base, {"simulator": {"jump_lambda": lam, "jump_scale": sig}})
        cell = f"j_l{lam_tag(lam)}_s{sig_tag(sig)}"
        n = emit_seeded(
            HERE,
            cell,
            ov,
            n_seeds=2,
            comment_prefix=f"Jump tune — λ={lam}, σ={sig}",
        )
        total += n
        print(f"  {cell:14s} (λ={lam}, σ={sig})  → {n} configs")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
