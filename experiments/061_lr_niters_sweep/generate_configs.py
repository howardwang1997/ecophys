"""061 — learning-rate × n_iters sweep on 4.2 + 2.1 winner.

052's 35-seed mean (5.40) might be partly under-trained: 200 iters with
lr=1e-3 may not converge for the full 4.2 architecture. This dir
sweeps both axes to find the convergence sweet spot.

Grid (4 × 3 × 4 seeds = 48 configs):
- lr ∈ {3e-4, 1e-3, 3e-3, 1e-2}
- n_iters ∈ {200, 400, 800}
- 4 seeds each

Cell name: ``lr{lr_tag}_n{n_iters}``.

Run on Mac:
    conda run -n ecophys python experiments/061_lr_niters_sweep/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import deep_merge, emit_seeded, stack_overrides  # noqa: E402


LRS = [3e-4, 1e-3, 3e-3, 1e-2]
N_ITERS = [200, 400, 800]


def lr_tag(lr: float) -> str:
    if lr == 3e-4: return "3e4"
    if lr == 1e-3: return "1e3"
    if lr == 3e-3: return "3e3"
    if lr == 1e-2: return "1e2"
    return f"{lr:.0e}".replace("-", "").replace("0", "")


def main() -> None:
    base = stack_overrides("tier_4_2_dyngraph", "tier_2_1_jumps")
    total = 0
    for lr in LRS:
        for n_iters in N_ITERS:
            ov = deep_merge(base, {"training": {
                "lr": lr,
                "n_iters": n_iters,
            }})
            cell = f"lr{lr_tag(lr)}_n{n_iters}"
            n = emit_seeded(
                HERE, cell, ov, n_seeds=4,
                comment_prefix=f"lr={lr}, n_iters={n_iters}",
            )
            total += n
    print(f"  emitted {len(LRS)}×{len(N_ITERS)} cells × 4 seeds")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
