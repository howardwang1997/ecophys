"""066 — bf16 + larger N for paper-grade SF estimate quality.

Larger N reduces SF estimate noise (excess demand averages over more
agents). With bf16 cutting memory ~2×, we can try N=15K and N=20K
(was N=10K previously) at chunk=24 single card.

Grid (3 × 8 seeds = 24 configs):
- (N=10K, bf16) — control: same N as winner, just bf16 (overlap with 058)
- (N=15K, bf16) — 1.5× agents, expect lower SF noise → tighter mean
- (N=20K, bf16) — 2× agents, paper-figure-grade

If 20K OOMs, the SKIP_DONE flag means partial completion still leaves
useful 10K/15K data.

Cell name: ``bigN_n{N}_bf16``.

Run on Mac:
    conda run -n ecophys python experiments/066_bigN_bf16/generate_configs.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _arch_base import deep_merge, emit_seeded, stack_overrides  # noqa: E402


CELLS = [
    (10000, "bigN_n10k_bf16",  "N=10K + bf16 (control vs 058)"),
    (15000, "bigN_n15k_bf16",  "N=15K + bf16 (1.5× agents)"),
    (20000, "bigN_n20k_bf16",  "N=20K + bf16 (paper-grade)"),
]


def main() -> None:
    base = stack_overrides("tier_4_2_dyngraph", "tier_2_1_jumps")
    total = 0
    for n_agents, cell, comment in CELLS:
        ov = deep_merge(base, {
            "simulator": {"n_agents": n_agents},
            "training": {"mixed_precision": "bf16"},
        })
        n = emit_seeded(HERE, cell, ov, n_seeds=8, comment_prefix=comment)
        total += n
        print(f"  {cell:18s} (N={n_agents:>5d})  → {n} configs")
    print(f"\nwrote {total} configs to {HERE}/")


if __name__ == "__main__":
    main()
