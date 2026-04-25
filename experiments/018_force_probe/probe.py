"""Force-magnitude probe across all EcoMD architectures.

Paper A figure: shows quantitatively WHY v1 MACE-lite and v2.0 (gauged)
failed — their pair force magnitudes are 14-190x weaker than v0.x baseline,
drowned by Langevin noise.

Output: results/force_magnitude_table.md (markdown table) + force_data.json
(raw measurements for plotting).

This is a deterministic measurement (no training); reproducible.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.models.ecomd_v2 import EcoMDv2Config, EcoMDv2Potential
from ecomd.models.mace_lite import build_mace_lite
from ecomd.models.potentials import (
    PairwisePotential,
    StochasticPairwisePotential,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "results"


def measure(name: str, build_fn, n: int = 200, d: int = 32, n_repeats: int = 5,
            seed: int = 0) -> dict:
    """Build potential N times, measure init |F| stats."""
    f_means = []
    v_vals = []
    for r in range(n_repeats):
        torch.manual_seed(seed + r * 100)
        pot = build_fn(seed=seed + r * 100)
        pot.eval()
        torch.manual_seed(seed + r * 100 + 1)
        s = torch.randn(n, d) * 0.5
        s.requires_grad_(True)
        v = pot(s)
        if isinstance(v, tuple):
            v = v[0]
        grad = torch.autograd.grad(v, s)[0]
        f_means.append(grad.abs().mean().item())
        v_vals.append(v.item())
    return {
        "name": name,
        "F_mean": float(np.mean(f_means)),
        "F_std": float(np.std(f_means)),
        "V_mean": float(np.mean(v_vals)),
        "V_std": float(np.std(v_vals)),
        "n_repeats": n_repeats,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    n, d = 200, 32

    # Architecture builders
    def b_v0x(seed: int):
        return PairwisePotential(d=d, hidden=48)

    def b_v09(seed: int):
        return StochasticPairwisePotential(d=d, hidden=48, k_random=50,
                                            resample_per_step=True)

    def b_mace_orig(seed: int):
        return build_mace_lite(
            d_state=d, k=32, hidden=48, body_order=4,
            n_classes=4, n_rbf=8, knn_refresh=10,
            use_layernorm=True,
        )

    def b_mace_h_hybrid(seed: int):
        return build_mace_lite(
            d_state=d, k=199, hidden=48, body_order=4,
            n_classes=4, n_rbf=8, knn_refresh=10,
            use_layernorm=True, readout_mode="hybrid",
            readout_multiplier=10.0, readout_init_gain=0.5,
        )

    def b_v2_default(seed: int):
        gen = torch.Generator().manual_seed(seed)
        return EcoMDv2Potential(n, EcoMDv2Config(
            d_state=d, hidden=48, k_types=4, d_type_emb=8, k_random=50, d_pi=4,
            kyle_enabled=True, kyle_lambda_init=0.05,
            gauge_axis=0, gauge_enforce=True, T_init_mode="eye_plus_noise",
            phi_init_gain=0.5,
        ), type_gen=gen)

    def b_v2_phi3(seed: int):
        gen = torch.Generator().manual_seed(seed)
        return EcoMDv2Potential(n, EcoMDv2Config(
            d_state=d, hidden=48, k_types=4, d_type_emb=8, k_random=50, d_pi=4,
            kyle_enabled=True, gauge_enforce=True, T_init_mode="eye_plus_noise",
            phi_init_gain=3.0,
        ), type_gen=gen)

    def b_v21(seed: int):
        gen = torch.Generator().manual_seed(seed)
        return EcoMDv2Potential(n, EcoMDv2Config(
            d_state=d, hidden=48, k_types=4, d_type_emb=8, k_random=50, d_pi=4,
            kyle_enabled=False, gauge_enforce=False, T_init_mode="ones",
            phi_init_gain=1.0,
        ), type_gen=gen)

    arches = [
        ("v0.x PairwisePotential (baseline)", b_v0x),
        ("v0.9 StochasticPairwise (k=50)", b_v09),
        ("v1 MACE-lite (k=32, body=4, default)", b_mace_orig),
        ("v1 MACE H hybrid (k=N-1, mult=10)", b_mace_h_hybrid),
        ("v2.0 default (gauge on, T=eye)", b_v2_default),
        ("v2.0 phi=3.0 (gauge on, T=eye)", b_v2_phi3),
        ("v2.1 (gauge off, T=ones, phi=1.0)", b_v21),
    ]

    results = []
    for name, fn in arches:
        try:
            r = measure(name, fn, n=n, d=d, n_repeats=5, seed=0)
            print(f"{r['name']:<48}  V={r['V_mean']:+10.2f}±{r['V_std']:7.2f}  "
                  f"|F|={r['F_mean']:.4f}±{r['F_std']:.4f}")
            results.append(r)
        except Exception as e:
            print(f"{name:<48}  ERROR: {e}")
            results.append({"name": name, "error": str(e)})

    (OUT / "force_data.json").write_text(json.dumps(results, indent=2))

    # Markdown table
    lines = [
        "# Force-magnitude probe — EcoMD architecture comparison",
        "",
        f"N={n} agents, d={d} state dim, n_repeats=5 (random init seeds).",
        "Untrained: pure init-time forces. Langevin noise per step σ ≈ 0.032.",
        "",
        "Forces below noise σ → simulator dynamics dominated by Langevin noise,",
        "training has no signal to learn meaningful dynamics.",
        "",
        "| architecture | V_init | |F|_init mean ± std | ratio vs v0.x | vs noise (σ=0.032) |",
        "|---|---|---|---|---|",
    ]
    baseline_F = next((r["F_mean"] for r in results if "v0.x" in r["name"]), 1.0)
    for r in results:
        if "error" in r:
            lines.append(f"| {r['name']} | ERROR | ERROR | — | — |")
            continue
        ratio = r["F_mean"] / baseline_F
        s_ratio = r["F_mean"] / 0.032
        lines.append(
            f"| {r['name']} | {r['V_mean']:+.1f}±{r['V_std']:.1f} | "
            f"{r['F_mean']:.4f}±{r['F_std']:.4f} | "
            f"{ratio:.3f}× | {s_ratio:.1f}× |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "- **|F| / σ < 1**: Langevin noise dominates → no learnable structure → 4/11 stylized facts (white noise floor).",
        "- **|F| / σ ≈ 30-50**: signal sufficient for clustering dynamics → 6-7/11 achievable.",
        "- **|F| / σ ≫ 100**: gradient explosion regime; clip=1.0 caps effective lr → again poor training.",
    ]
    (OUT / "force_magnitude_table.md").write_text("\n".join(lines))
    print()
    print(f"wrote {OUT/'force_magnitude_table.md'}")
    print(f"wrote {OUT/'force_data.json'}")


if __name__ == "__main__":
    main()
