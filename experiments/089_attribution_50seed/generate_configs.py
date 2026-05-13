"""089 — clean leave-one-in mechanism-fact attribution batch (50-seed).

Empirical core of the NeurIPS 2027 plan. Each cell activates exactly ONE
mechanism (or one mechanism at one strength setting); v3 baseline is the
control row. Output is a 10 × 11 mechanism-fact attribution matrix that
becomes Figure 1 of the paper.

50-seed CIs are mandatory because Branch F (088) showed that 30-seed
means inflated by ~0.16 (asymdrag 5.10→4.94, b3_k3 5.21→4.94 at n=50).
We will not repeat that mistake.

Cells (16 total, 800 cfg ≈ ~7h H20):

  Control:
    attr_baseline_v3              — pure v3, no V4/B-round (50 seeds)

  V4 + B-round single-mechanism (one knob each, headline strength):
    attr_levy_a17                 — Lévy α=1.7 (mid of 077 sweep)
    attr_asymdrag_a06             — asym α=0.6 (Branch D best)
    attr_memk_l095_s10            — memk λ=0.95 strength=1.0
    attr_microstructure_r03       — microstructure ρ=0.3
    attr_powerlaw_a15             — power-law α=1.5 (B4 default)
    attr_b3_k3                    — B3 K=3 τ=1.0
    attr_inner_3                  — adiabatic inner_steps=3
    attr_jump_l01                 — jumps λ=0.1

  M1.1 AR(1) whitening dose-response (3 strengths):
    attr_ar1_s03                  — λ=0.9 strength=0.3
    attr_ar1_s05                  — λ=0.9 strength=0.5
    attr_ar1_s08                  — λ=0.9 strength=0.8

  M1.2 Zumbach feedback dose-response (3 strengths, 'abs' mode):
    attr_zumbach_s05              — λ=0.95 strength=0.5 mode=abs
    attr_zumbach_s10              — λ=0.95 strength=1.0 mode=abs
    attr_zumbach_s20              — λ=0.95 strength=2.0 mode=abs

  Falsification probe:
    attr_zumbach_dn_s10           — λ=0.95 strength=1.0 mode=downside
                                    (does the leverage-asymmetric variant
                                     do something the symmetric variant doesn't?)

Total: 16 cells × 50 seeds = 800 cfg.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "089_attribution_50seed"
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


def apply_microstructure(cfg, rho=0.3):
    cfg["simulator"]["microstructure_rho"] = rho


def apply_powerlaw(cfg, alpha=1.5, w_pow=0.5, w_mlp=1.0):
    cfg["simulator"]["power_law_external"] = True
    cfg["simulator"]["power_law_alpha"] = alpha
    cfg["simulator"]["power_law_w_pow"] = w_pow
    cfg["simulator"]["power_law_w_mlp"] = w_mlp


def apply_b3(cfg, k=3, tau=1.0):
    cfg["simulator"]["regime_enabled"] = True
    cfg["simulator"]["regime_discrete_enabled"] = True
    cfg["simulator"]["regime_n_states"] = k
    cfg["simulator"]["regime_gumbel_tau"] = tau


def apply_adiabatic(cfg, inner=3):
    cfg["simulator"]["inner_steps_per_price"] = inner


def apply_jump(cfg, lam=0.1, scale=0.05):
    cfg["simulator"]["jump_lambda"] = lam
    cfg["simulator"]["jump_scale"] = scale


def apply_ar1_whiten(cfg, lam=0.9, strength=0.5):
    cfg["simulator"]["ar1_whiten_lambda"] = lam
    cfg["simulator"]["ar1_whiten_strength"] = strength


def apply_zumbach(cfg, lam=0.95, strength=1.0, mode="abs"):
    cfg["simulator"]["zumbach_feedback_lambda"] = lam
    cfg["simulator"]["zumbach_feedback_strength"] = strength
    cfg["simulator"]["zumbach_feedback_mode"] = mode


# (tag, n_seeds, mods)
CELLS = [
    # ── Control (50 seeds) ─────────────────────────────────────────────
    ("attr_baseline_v3",          50, []),
    # ── V4 + B-round single-mechanism (50 seeds each) ──────────────────
    ("attr_levy_a17",             50, [(apply_levy,           {"alpha": 1.7})]),
    ("attr_asymdrag_a06",         50, [(apply_asym,           {"alpha": 0.6})]),
    ("attr_memk_l095_s10",        50, [(apply_memk,           {"lam": 0.95, "strength": 1.0})]),
    ("attr_microstructure_r03",   50, [(apply_microstructure, {"rho": 0.3})]),
    ("attr_powerlaw_a15",         50, [(apply_powerlaw,       {"alpha": 1.5})]),
    ("attr_b3_k3",                50, [(apply_b3,             {"k": 3, "tau": 1.0})]),
    ("attr_inner_3",              50, [(apply_adiabatic,      {"inner": 3})]),
    ("attr_jump_l01",             50, [(apply_jump,           {"lam": 0.1, "scale": 0.05})]),
    # ── M1.1 AR(1) whitening dose-response (50 seeds each) ─────────────
    ("attr_ar1_s03",              50, [(apply_ar1_whiten, {"lam": 0.9, "strength": 0.3})]),
    ("attr_ar1_s05",              50, [(apply_ar1_whiten, {"lam": 0.9, "strength": 0.5})]),
    ("attr_ar1_s08",              50, [(apply_ar1_whiten, {"lam": 0.9, "strength": 0.8})]),
    # ── M1.2 Zumbach feedback dose-response (50 seeds each) ────────────
    ("attr_zumbach_s05",          50, [(apply_zumbach, {"lam": 0.95, "strength": 0.5, "mode": "abs"})]),
    ("attr_zumbach_s10",          50, [(apply_zumbach, {"lam": 0.95, "strength": 1.0, "mode": "abs"})]),
    ("attr_zumbach_s20",          50, [(apply_zumbach, {"lam": 0.95, "strength": 2.0, "mode": "abs"})]),
    # ── Falsification: Zumbach downside-only variant ───────────────────
    ("attr_zumbach_dn_s10",       50, [(apply_zumbach, {"lam": 0.95, "strength": 1.0, "mode": "downside"})]),
]


def main() -> None:
    base_spx = yaml.safe_load(BASE_SPX.read_text())
    n = 0
    for tag, n_seeds, mods in CELLS:
        for s in range(n_seeds):
            cfg = copy.deepcopy(base_spx)
            for fn, kwargs in mods:
                fn(cfg, **kwargs)
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    n_cells = len(CELLS)
    print(f"wrote {n} configs across {n_cells} cells to {OUT}")


if __name__ == "__main__":
    main()
