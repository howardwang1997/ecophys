"""Trade per-card memory between N (agents), chunk_steps (BPTT horizon),
and hidden (model width) — without writing any new code.

Memory of pair-MLP activations ~ N × chunk × hidden². Current winner
``p_4_2__2_1`` runs at (N=10K, chunk=24, h=96). The OOM observation
that chunk>24 fails motivates trading N or h to free chunk budget.

5 cells × 5 seeds = 25 configs. All keep the 4.2 + 2.1 architecture
(gate + u + LN + jumps λ=0.5 σ=0.01).

If ``nh_n5k_c48`` matches ``p_4_2__2_1`` mean (5.40) or beats it,
**chunk is the real bottleneck** and N=5K is a free win. If it
underperforms, the train/eval mismatch is not chunk-limited.

Run on Mac:
    conda run -n ecophys python experiments/055_chunk_n_tradeoff/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import deep_merge, emit_seeded, stack_overrides  # noqa: E402


# (N, chunk_steps, hidden, comment)
CELLS = [
    ("nh_n5k_c24",   5000,  24,  96,  "Half N, same chunk — isolate N effect"),
    ("nh_n5k_c48",   5000,  48,  96,  "Half N, double chunk — KEY: chunk vs N tradeoff"),
    ("nh_n2k5_c96",  2500,  96,  96,  "Quarter N, 4× chunk — KEY: aggressive chunk push"),
    ("nh_n10k_h64",  10000, 24,  64,  "Smaller hidden, same N+chunk — hidden ablation"),
    ("nh_n10k_h128", 10000, 24,  128, "Bigger hidden, same N+chunk — does capacity help?"),
]


def main() -> None:
    base = stack_overrides("tier_4_2_dyngraph", "tier_2_1_jumps")
    total = 0
    for cell, n, chunk, hidden, comment in CELLS:
        ov = deep_merge(base, {
            "simulator": {
                "n_agents": n,
                "hidden": hidden,
            },
            "training": {
                "chunk_steps": chunk,
                # warmup_steps was 16 at chunk=24. Scale proportionally so
                # supervision-tail length stays = chunk - warmup = 8.
                "warmup_steps": max(4, chunk - 8),
            },
        })
        k = emit_seeded(HERE, cell, ov, n_seeds=5, comment_prefix=comment)
        total += k
        print(f"  {cell:14s} (N={n:>5d} chunk={chunk:>3d} h={hidden:>3d})  → {k} configs")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
