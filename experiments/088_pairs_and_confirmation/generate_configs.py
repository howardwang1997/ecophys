"""088 — Pair-mechanism sweep + high-seed confirmation + B3 tuning + BTC pairs.

Branch E showed that 4-mechanism stacking is anti-additive (combo_full
mean=4.62 < asymdrag_a06 mean=5.10). The leave-one-out diagnosed
adiabatic as one bad component, but combo_no_inner (3 mechanisms) is
still mean=4.74 — barely better. The real interaction failure is
between Lévy + memk + asym pairwise.

This experiment fills the gap: **all 6 unordered pairs of 4 candidate
mechanisms**, plus B3 tuning, plus 50-seed confirmation of the two
strongest single-mechanism cells.

4 candidate mechanisms tested pairwise:
  L = Lévy noise (α=1.9)
  A = asymmetric drag (α=0.6 — Branch D's best)
  M = memory kernel (λ=0.95, strength=1.0)
  B = B3 discrete regime (K=3, τ=1.0 — best B-round result)

Cells (16 total, ~440 cfg):

  Confirmation (high-seed, n=50):
    conf_asymdrag_a06       — replicate Branch D's best with tighter CI
    conf_b3_k3_pure         — replicate Branch E's best B-round with tighter CI

  Pairs (n=30):
    pair_LA  — Lévy + asym (no memk)
    pair_LM  — Lévy + memk
    pair_LB  — Lévy + B3
    pair_AM  — asym + memk
    pair_AB  — asym + B3 (most promising — strongest single mechanisms)
    pair_MB  — memk + B3

  B3 tuning (n=30):
    b3_k4_pure              — does more states help?
    b3_k3_tau05_pure        — sharper switching (lower τ)
    b3_k3_tau15_pure        — softer switching (higher τ)

  BTC pairs (n=30):
    btc_pair_AB             — asym + B3 on BTC (best pair × cross-asset)
    btc_pair_LA             — Lévy + asym on BTC

  Sanity (n=30):
    triple_LAM              — Lévy + asym + memk (= combo_no_inner replicated)

Total: 2×50 + 6×30 + 3×30 + 2×30 + 1×30 = 100 + 180 + 90 + 60 + 30 = 460 cfg
Estimated H20 wall: 460 × 8.8min / 8 cards ≈ 8.4h.

Success criteria:
  Primary: any pair cell mean ≥ 5.5 → "X + Y compose, write Paper A"
  Secondary: conf_asymdrag_a06 mean ∈ [4.5, 5.7] → confirms Branch D
  Tertiary: btc_pair_AB mean ≥ btc_baseline + 0.5 → cross-asset pair lift
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
BASE_BTC = REPO / "experiments" / "081_btc_30seed" / "config_btc_baseline_seed0.yaml"
OUT = REPO / "experiments" / "088_pairs_and_confirmation"
OUT.mkdir(parents=True, exist_ok=True)


def apply_levy(cfg, alpha=1.9):
    cfg["simulator"]["noise_dist"] = "levy"
    cfg["simulator"]["noise_levy_alpha"] = alpha
    cfg["simulator"]["noise_levy_clip"] = 50.0


def apply_asym(cfg, alpha=0.6):
    cfg["simulator"]["asym_drag_alpha"] = alpha


def apply_memk(cfg, lam=0.95, strength=1.0):
    cfg["simulator"]["memory_kernel_lambda"] = lam
    cfg["simulator"]["memory_kernel_strength"] = strength


def apply_b3(cfg, k=3, tau=1.0):
    cfg["simulator"]["regime_enabled"] = True
    cfg["simulator"]["regime_discrete_enabled"] = True
    cfg["simulator"]["regime_n_states"] = k
    cfg["simulator"]["regime_gumbel_tau"] = tau


# (tag, base, n_seeds, mods)
# Each mods is a list of (apply_fn, kwargs) pairs
CELLS = [
    # ── Confirmation (50 seeds) ────────────────────────────────────
    ("conf_asymdrag_a06",  "spx", 50, [(apply_asym, {"alpha": 0.6})]),
    ("conf_b3_k3_pure",    "spx", 50, [(apply_b3,   {"k": 3, "tau": 1.0})]),
    # ── Pairs (30 seeds) ───────────────────────────────────────────
    ("pair_LA", "spx", 30, [(apply_levy, {}), (apply_asym, {"alpha": 0.6})]),
    ("pair_LM", "spx", 30, [(apply_levy, {}), (apply_memk, {})]),
    ("pair_LB", "spx", 30, [(apply_levy, {}), (apply_b3,   {})]),
    ("pair_AM", "spx", 30, [(apply_asym, {"alpha": 0.6}), (apply_memk, {})]),
    ("pair_AB", "spx", 30, [(apply_asym, {"alpha": 0.6}), (apply_b3,   {})]),
    ("pair_MB", "spx", 30, [(apply_memk, {}), (apply_b3,   {})]),
    # ── B3 tuning (30 seeds) ───────────────────────────────────────
    ("b3_k4_pure",        "spx", 30, [(apply_b3, {"k": 4, "tau": 1.0})]),
    ("b3_k3_tau05_pure",  "spx", 30, [(apply_b3, {"k": 3, "tau": 0.5})]),
    ("b3_k3_tau15_pure",  "spx", 30, [(apply_b3, {"k": 3, "tau": 1.5})]),
    # ── BTC pairs (30 seeds) ───────────────────────────────────────
    ("btc_pair_AB", "btc", 30, [(apply_asym, {"alpha": 0.6}), (apply_b3, {})]),
    ("btc_pair_LA", "btc", 30, [(apply_levy, {}), (apply_asym, {"alpha": 0.6})]),
    # ── Sanity replicate (3-mech combo without adiabatic) ──────────
    ("triple_LAM", "spx", 30, [(apply_levy, {}), (apply_asym, {"alpha": 0.6}), (apply_memk, {})]),
]


def main() -> None:
    base_spx = yaml.safe_load(BASE_SPX.read_text())
    base_btc = yaml.safe_load(BASE_BTC.read_text())
    n = 0
    for tag, base_kind, n_seeds, mods in CELLS:
        base = base_btc if base_kind == "btc" else base_spx
        for s in range(n_seeds):
            cfg = copy.deepcopy(base)
            for fn, kwargs in mods:
                fn(cfg, **kwargs)
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
