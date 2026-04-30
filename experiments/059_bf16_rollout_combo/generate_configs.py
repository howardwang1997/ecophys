"""059 — bf16 + rollout_reg combinations.

After 057 measures the rollout_reg effect alone and 058 measures bf16
effect alone, this dir tests the interaction. Hypothesis: bf16's
larger-chunk ability + rollout_reg's longer-horizon supervision may
compose constructively.

Grid (4 cells × 8 seeds = 32 configs):
- (chunk=48, no rr)        — bf16 alone control (also in 058)
- (chunk=48, rr_120_w10)   — chunk + medium rollout
- (chunk=48, rr_240_w10)   — chunk + long rollout
- (chunk=24, rr_240_w20)   — bf16 speed-up but keep small chunk + heavy rr

Cell name: ``bf16_c{chunk}_rr{steps}_{w}``.

Run on Mac:
    conda run -n ecophys python experiments/059_bf16_rollout_combo/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import deep_merge, emit_seeded, stack_overrides  # noqa: E402


GRID = [
    # (chunk, rr_steps, rr_weight, rr_every, cell_name, comment)
    (48,   0, 0.0,  5, "bf16_c48_norr",     "bf16 chunk=48 only (control)"),
    (48, 120, 0.10, 5, "bf16_c48_rr120_w10","bf16 chunk=48 + medium rollout"),
    (48, 240, 0.10, 5, "bf16_c48_rr240_w10","bf16 chunk=48 + long rollout"),
    (24, 240, 0.20, 5, "bf16_c24_rr240_w20","bf16 chunk=24 + heavy long rollout"),
]


def main() -> None:
    base = stack_overrides("tier_4_2_dyngraph", "tier_2_1_jumps")
    total = 0
    for chunk, rr_steps, rr_weight, rr_every, cell, comment in GRID:
        train_ov: dict = {
            "chunk_steps": chunk,
            "warmup_steps": max(4, chunk - 8),
            "mixed_precision": "bf16",
        }
        if rr_steps > 0:
            train_ov.update({
                "rollout_reg_enabled": True,
                "rollout_reg_steps": rr_steps,
                "rollout_reg_chunk": 24,
                "rollout_reg_weight": rr_weight,
                "rollout_reg_every": rr_every,
            })
        ov = deep_merge(base, {"training": train_ov})
        n = emit_seeded(HERE, cell, ov, n_seeds=8, comment_prefix=comment)
        total += n
        print(f"  {cell:22s}  → {n} configs")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
