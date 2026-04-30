"""058 — bf16 mixed-precision chunk_steps sweep on the 4.2 + 2.1 arch.

Hypothesis: bf16 cuts activation memory ~2× and on H20 SXM5 also ~2×
compute throughput. If our chunk>24 OOM is purely activation-memory
limited, bf16 should let chunk=48 fit. (chunk=64 is borderline.)

Grid (3 cells × 10 seeds = 30 configs):
- (chunk=24, bf16) — control: same horizon as fp32 baseline, just faster
- (chunk=48, bf16) — KEY: 2× horizon, similar memory to fp32 chunk=24
- (chunk=64, bf16) — stretch: 2.7× horizon, may OOM but worth trying

Each cell uses warmup = chunk - 8 (keep supervision tail = 8 steps).

Cell name: ``bf16_c{chunk}``.

Run on Mac:
    conda run -n ecophys python experiments/058_bf16_chunk_sweep/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import deep_merge, emit_seeded, stack_overrides  # noqa: E402


GRID = [
    (24, "bf16_c24", "control: bf16 + chunk=24 (faster, same horizon)"),
    (48, "bf16_c48", "KEY: bf16 + chunk=48 (2× horizon)"),
    (64, "bf16_c64", "stretch: bf16 + chunk=64 (may OOM)"),
]


def main() -> None:
    base = stack_overrides("tier_4_2_dyngraph", "tier_2_1_jumps")
    total = 0
    for chunk, cell, comment in GRID:
        ov = deep_merge(base, {
            "training": {
                "chunk_steps": chunk,
                "warmup_steps": max(4, chunk - 8),
                "mixed_precision": "bf16",
            },
        })
        n = emit_seeded(HERE, cell, ov, n_seeds=10, comment_prefix=comment)
        total += n
        print(f"  {cell:10s} (chunk={chunk})  → {n} configs")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
