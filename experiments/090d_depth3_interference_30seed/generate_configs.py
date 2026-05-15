"""090d — depth-3 interference probe (strengthen Branch F finding).

Branch F (088) showed compositional means peak at depth 2 then decline:
  depth=1: 4.94   depth=2: 5.18   depth=3: 4.79   depth=4: 4.62

This claim is currently single-batch (n=24-30). For paper-grade
"compositional impossibility" we want it replicated at larger n with the
new mechanisms in the mix. 090d adds 6 depth-3 cells × n=30 = 180 cfg.

Cells (6 depth-3 cells × 30 seeds = 180 cfg ≈ ~3h H20):

  Triples built from 089's specialist mechanisms:
    triple_zumdn_b3_asym       — top-3 best singles together
    triple_zumdn_b3_levy       — adding Lévy
    triple_zumdn_b3_memk       — adding memory kernel
    triple_zumdn_b3_powerlaw   — adding power-law

  Triples extending Branch F's pair_AB (asym + b3 + ?):
    triple_pair_AB_zumdn       — pair_AB + Zumbach `dn`
    triple_pair_AB_ar1clip     — pair_AB + clipped AR(1) (newly stable)

Combined with 090's `triple_zumdn_ar1_b3` (3rd-depth mix of new mechs),
this gives 7 depth-3 cells (1 from 090 + 6 here) for the §4 figure
showing depth × mean.

Success criterion: ≤2 of 6 cells beat depth-2 mean of 5.18.
Failure criterion: ≥3 beat 5.18 (would invalidate Branch F's claim).
Either outcome is publishable; we just need defensible numbers.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "090d_depth3_interference_30seed"
OUT.mkdir(parents=True, exist_ok=True)


def apply_levy(cfg, alpha=1.7):
    cfg["simulator"]["noise_dist"] = "levy"
    cfg["simulator"]["noise_levy_alpha"] = alpha
    cfg["simulator"]["noise_levy_clip"] = 50.0


def apply_asym(cfg, alpha=0.6):
    cfg["simulator"]["asym_drag_alpha"] = alpha


def apply_memk(cfg, lam=0.95, strength=1.0):
    cfg["simulator"]["memory_kernel_lambda"] = lam
    cfg["simulator"]["memory_kernel_strength"] = strength


def apply_powerlaw(cfg, alpha=1.5):
    cfg["simulator"]["power_law_external"] = True
    cfg["simulator"]["power_law_alpha"] = alpha
    cfg["simulator"]["power_law_w_pow"] = 0.5
    cfg["simulator"]["power_law_w_mlp"] = 1.0


def apply_b3(cfg, k=3, tau=1.0):
    cfg["simulator"]["regime_enabled"] = True
    cfg["simulator"]["regime_discrete_enabled"] = True
    cfg["simulator"]["regime_n_states"] = k
    cfg["simulator"]["regime_gumbel_tau"] = tau


def apply_ar1_clip(cfg, lam=0.9, strength=0.5, clip=1.0):
    cfg["simulator"]["ar1_whiten_lambda"] = lam
    cfg["simulator"]["ar1_whiten_strength"] = strength
    cfg["simulator"]["ar1_whiten_clip"] = clip


def apply_zumbach_dn(cfg):
    cfg["simulator"]["zumbach_feedback_lambda"] = 0.95
    cfg["simulator"]["zumbach_feedback_strength"] = 1.0
    cfg["simulator"]["zumbach_feedback_mode"] = "downside"


CELLS = [
    ("triple_zumdn_b3_asym",     30, [apply_zumbach_dn, apply_b3, apply_asym]),
    ("triple_zumdn_b3_levy",     30, [apply_zumbach_dn, apply_b3, apply_levy]),
    ("triple_zumdn_b3_memk",     30, [apply_zumbach_dn, apply_b3, apply_memk]),
    ("triple_zumdn_b3_powerlaw", 30, [apply_zumbach_dn, apply_b3, apply_powerlaw]),
    ("triple_pair_AB_zumdn",     30, [apply_asym, apply_b3, apply_zumbach_dn]),
    ("triple_pair_AB_ar1clip",   30, [apply_asym, apply_b3, apply_ar1_clip]),
]


def main() -> None:
    base_spx = yaml.safe_load(BASE_SPX.read_text())
    n = 0
    for tag, n_seeds, mods in CELLS:
        for seed in range(n_seeds):
            cfg = copy.deepcopy(base_spx)
            for fn in mods:
                fn(cfg)
            cfg["training"]["seed"] = seed
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs across {len(CELLS)} cells to {OUT}")


if __name__ == "__main__":
    main()
