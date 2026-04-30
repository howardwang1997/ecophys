"""057 — stop-grad rollout regularization (rollout_reg) sweep on the
4.2 + 2.1 winner architecture.

Hypothesis: train(24-step) / eval(4000-step) horizon mismatch is what
caps mean at 5.40/11. A long-horizon SF supervision via multi-chunk
truncated-BPTT rollouts may lift the mean.

Grid (5 cells × 6 seeds = 30 configs):
- (steps=72,  weight=0.05, every=5)   light
- (steps=72,  weight=0.20, every=5)   medium
- (steps=120, weight=0.10, every=5)   moderate horizon
- (steps=240, weight=0.10, every=10)  long horizon, less frequent
- (steps=240, weight=0.30, every=5)   long horizon, heavy

Cell name: ``rr_s{steps}_w{weight*100}_e{every}``.

Run on Mac:
    conda run -n ecophys python experiments/057_rollout_reg_sweep/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import deep_merge, emit_seeded, stack_overrides  # noqa: E402


GRID = [
    ( 72, 0.05,  5, "rr_s72_w5_e5",    "light: short rollout, low weight"),
    ( 72, 0.20,  5, "rr_s72_w20_e5",   "medium: short rollout, mid weight"),
    (120, 0.10,  5, "rr_s120_w10_e5",  "moderate: medium rollout"),
    (240, 0.10, 10, "rr_s240_w10_e10", "long rollout, less frequent"),
    (240, 0.30,  5, "rr_s240_w30_e5",  "long rollout, heavy"),
]


def main() -> None:
    base = stack_overrides("tier_4_2_dyngraph", "tier_2_1_jumps")
    total = 0
    for steps, weight, every, cell, comment in GRID:
        ov = deep_merge(base, {
            "training": {
                "rollout_reg_enabled": True,
                "rollout_reg_steps": int(steps),
                "rollout_reg_chunk": 24,  # match training chunk
                "rollout_reg_weight": float(weight),
                "rollout_reg_every": int(every),
            },
        })
        n = emit_seeded(HERE, cell, ov, n_seeds=6,
                        comment_prefix=f"rollout_reg {comment}")
        total += n
        print(f"  {cell:18s} (steps={steps}, w={weight}, every={every})  → {n} configs")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
