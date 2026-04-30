"""065 — long training (n_iters >> 200) on 4.2 + 2.1 winner.

200 iters is the historical default. Is the model under-trained at the
new architecture? This dir runs 4 long-training cells × 6 seeds = 24
configs. Each n_iters=400 takes ~2× wall time, n_iters=800 takes ~4×.

Cells:
- ``long_n400`` — 2× iters, lr unchanged
- ``long_n800`` — 4× iters, lr unchanged
- ``long_n400_lr5e4`` — 2× iters with halved lr (anneal-friendly)
- ``long_n800_lr5e4`` — 4× iters with halved lr

Cell name: ``long_n{n}{_lr_tag}``.

Run on Mac:
    conda run -n ecophys python experiments/065_long_training/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import deep_merge, emit_seeded, stack_overrides  # noqa: E402


CELLS = [
    ("long_n400",       400, 1.0e-3, "n_iters=400, lr unchanged"),
    ("long_n800",       800, 1.0e-3, "n_iters=800, lr unchanged"),
    ("long_n400_lr5e4", 400, 5.0e-4, "n_iters=400, lr halved"),
    ("long_n800_lr5e4", 800, 5.0e-4, "n_iters=800, lr halved"),
]


def main() -> None:
    base = stack_overrides("tier_4_2_dyngraph", "tier_2_1_jumps")
    total = 0
    for cell, n_iters, lr, comment in CELLS:
        ov = deep_merge(base, {"training": {
            "n_iters": n_iters, "lr": lr,
        }})
        n = emit_seeded(HERE, cell, ov, n_seeds=6,
                        comment_prefix=f"Long training — {comment}")
        total += n
        print(f"  {cell:18s} (n={n_iters}, lr={lr})  → {n} configs")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
