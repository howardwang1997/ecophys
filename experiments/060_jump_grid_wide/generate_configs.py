"""060 — jump (λ, σ) grid widening, the key Tier 2.1 hyperparameter.

Currently 053 tests a 3×3 grid centered on (λ=0.5, σ=0.01). This dir
extends to a 5×5 grid covering 2 orders of magnitude in each direction,
to find the actual basin shape.

Grid (5 × 5 × 3 seeds = 75 configs):
- λ ∈ {0.1, 0.3, 0.5, 1.0, 2.0}
- σ ∈ {0.002, 0.005, 0.01, 0.02, 0.05}

Cell name: ``j_l{lam}_s{sig}`` with no decimal points (e.g., 03 = 0.3).

Run on Mac:
    conda run -n ecophys python experiments/060_jump_grid_wide/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import deep_merge, emit_seeded, stack_overrides  # noqa: E402


LAMBDAS = [0.1, 0.3, 0.5, 1.0, 2.0]
SIGMAS = [0.002, 0.005, 0.01, 0.02, 0.05]


def lam_tag(lam: float) -> str:
    return f"{lam:.1f}".replace(".", "")  # 0.3 → "03", 1.0 → "10", 2.0 → "20"


def sig_tag(sig: float) -> str:
    # 0.002 → "002", 0.005 → "005", 0.01 → "010", 0.02 → "020", 0.05 → "050"
    return f"{int(round(sig * 1000)):03d}"


def main() -> None:
    base = stack_overrides("tier_4_2_dyngraph", "tier_2_1_jumps")
    total = 0
    for lam in LAMBDAS:
        for sig in SIGMAS:
            ov = deep_merge(base, {"simulator": {
                "jump_lambda": lam, "jump_scale": sig,
            }})
            cell = f"j_l{lam_tag(lam)}_s{sig_tag(sig)}"
            n = emit_seeded(
                HERE, cell, ov, n_seeds=3,
                comment_prefix=f"Jump grid wide — λ={lam}, σ={sig}",
            )
            total += n
    print(f"  emitted {len(LAMBDAS)}×{len(SIGMAS)} cells × 3 seeds")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
