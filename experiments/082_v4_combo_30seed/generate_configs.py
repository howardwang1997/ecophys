"""082 — V4 mechanism leave-one-out + dose-response combo (30 seeds × 6 cells).

Branch D (077-081) validated 3 v4 mechanisms individually:
  - Lévy noise           (077): max 9/11, mean 4.93
  - Asymmetric drag      (078): max 9/11 ×3, mean 5.10 (best so far)
  - Memory kernel        (079): max 8/11, mean 4.77

But 4 of the 9/11 winners ALL fail the same 2-3 facts:
  - autocorr_returns: 3/4 winners fail (AR(1) drift untouched)
  - hill_tail_index:  3/4 winners fail (Lévy alone insufficient)
  - zumbach:          2/4 winners fail (asym=0.6 kills zumbach)

Hypothesis: combining mechanisms breaks the 2/3-fact bottleneck.
Specifically:
  - Adiabatic (inner_steps=3) breaks the AR(1) attractor
  - Lévy (α=1.9) THEN can fix hill_tail because tails aren't AR(1)-contaminated
  - Asym drag (α=0.4) keeps leverage strong; α=0.4 is gentler than a06's
    high-variance regime (a06 had std=2.12 because of cond_kurtosis blowups)
  - Memory kernel keeps zumbach from collapsing

Cells (6 × 30 seeds = 180 cfg):

  Flagship + leave-one-out (4 cells):
    combo_full        : levy=1.9, asym=0.4, memk=(0.95,1.0), inner=3   ← all 4 mechanisms
    combo_no_levy     :           asym=0.4, memk=(0.95,1.0), inner=3   ← does Lévy add?
    combo_no_inner    : levy=1.9, asym=0.4, memk=(0.95,1.0), inner=1   ← does adiabatic add?
    combo_no_memk     : levy=1.9, asym=0.4,                  inner=3   ← does memk add?

  Dose-response (2 cells):
    combo_asym05      : levy=1.9, asym=0.5, memk=(0.95,1.0), inner=3   ← stronger asym
    combo_levy17      : levy=1.7, asym=0.4, memk=(0.95,1.0), inner=3   ← heavier-tail Lévy

The leave-one-out structure is more informative than the original plan's
4 unrelated combos: each cell quantifies one mechanism's MARGINAL
contribution by ablating it from the flagship. This is exactly the
ablation table reviewers expect for ICML submissions.

Success criteria (must satisfy ALL):
  (a) combo_full mean ≥ 5.5  (improves on asymdrag_a06's 5.10)
  (b) combo_full ≥ 4/30 seeds at ≥8/11  (matches a06's stability)
  (c) combo_full max ≥ 10/11  (new project record)

Stretch: combo_full mean ≥ 6.0 AND ≥1 seed at 11/11.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "082_v4_combo_30seed"
OUT.mkdir(parents=True, exist_ok=True)


# (tag, levy_alpha or None, asym_alpha or None, memk(λ, strength) or None, inner_steps)
CELLS = [
    ("combo_full",     1.9,  0.4, (0.95, 1.0), 3),
    ("combo_no_levy",  None, 0.4, (0.95, 1.0), 3),
    ("combo_no_inner", 1.9,  0.4, (0.95, 1.0), 1),
    ("combo_no_memk",  1.9,  0.4, None,        3),
    ("combo_asym05",   1.9,  0.5, (0.95, 1.0), 3),
    ("combo_levy17",   1.7,  0.4, (0.95, 1.0), 3),
]
SEEDS = list(range(30))


def main() -> None:
    base = yaml.safe_load(BASE.read_text())
    n = 0
    for tag, levy_alpha, asym_alpha, memk, inner in CELLS:
        for s in SEEDS:
            cfg = copy.deepcopy(base)

            # Lévy noise (use the field names EcoMDConfig actually reads;
            # see experiments/077_levy_noise_30seed/generate_configs.py for
            # the canonical pattern).
            if levy_alpha is not None:
                cfg["simulator"]["noise_dist"] = "levy"
                cfg["simulator"]["noise_levy_alpha"] = levy_alpha
                cfg["simulator"]["noise_levy_clip"] = 50.0
            # else: keep base's noise_dist=t (default v3 behaviour)

            # Asymmetric drag (default 0.0 means inactive)
            if asym_alpha is not None:
                cfg["simulator"]["asym_drag_alpha"] = asym_alpha

            # Memory kernel (both knobs zero ⇒ inactive)
            if memk is not None:
                cfg["simulator"]["memory_kernel_lambda"] = memk[0]
                cfg["simulator"]["memory_kernel_strength"] = memk[1]

            # Adiabatic (inner=1 reproduces baseline single-step semantics)
            cfg["simulator"]["inner_steps_per_price"] = inner

            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
