"""084 — B1 microstructure (bid-ask bounce) noise sweep.

The autocorr_returns fact (band [-0.1, 0.20]) is consistently failed by
v3 and v4 cells (mean +0.38 due to AR(0.9) drift artifact). The
microstructure mechanism applies an MA(1) filter to integrator noise:

    ε_eff = ε - rho_micro · ε_{t-1}

This induces lag-1 negative autocorrelation in s_next - s ≈ in returns,
mirroring real-world bid-ask bounce. Hypothesis: rho_micro ∈ [0.3, 0.5]
moves autocorr from +0.38 toward +0.10, into the target band.

3 cells × 30 seeds = 90 cfg.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
COMBO_BASE = REPO / "experiments" / "082_v4_combo_30seed" / "config_combo_full_seed0.yaml"
OUT = REPO / "experiments" / "084_b1_microstructure_30seed"
OUT.mkdir(parents=True, exist_ok=True)

# Cells:
#  - rho03_pure: only B1, otherwise v3 baseline. Tests B1 in isolation.
#  - rho05_pure: stronger filter; expect more autocorr push but possibly
#    over-correction into negative ac territory.
#  - rho03_combo: B1 stacked on combo_full (Lévy + asym + memk + adiabatic).
#    The headline question: does B1 fix the one fact combo_full will likely
#    still fail?
CELLS = [
    ("b1_rho03_pure",  0.3, False),
    ("b1_rho05_pure",  0.5, False),
    ("b1_rho03_combo", 0.3, True),
]
SEEDS = list(range(30))


def main() -> None:
    base_pure = yaml.safe_load(BASE.read_text())
    base_combo = yaml.safe_load(COMBO_BASE.read_text())
    n = 0
    for tag, rho, use_combo in CELLS:
        base = base_combo if use_combo else base_pure
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            cfg["simulator"]["microstructure_rho"] = rho
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
