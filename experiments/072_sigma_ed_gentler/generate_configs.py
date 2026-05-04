"""072 — gentler σ_ed probe.

068 found σ_ed=1.0 cuts ac_r 0.74→0.30 BUT trashes leverage/zumbach/hill
(flips signs, breaks fat tails). Was the σ_ed too aggressive? Probe smaller
values 0.05–0.30 to find a regime that helps autocorr without breaking other facts.

Cells (8 seeds each — probe before scaling):
  sigmaed_005   σ_ed = 0.05
  sigmaed_01    σ_ed = 0.10
  sigmaed_02    σ_ed = 0.20
  sigmaed_03    σ_ed = 0.30

Keeps Hawkes coherent (068 baseline default) and ed_normalize=False.
Uses learnable T/γ (not frozen) so this is orthogonal to 069.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "068_autocorr_fix" / "config_C_sigma_ed1_seed0.yaml"
OUT = REPO / "experiments" / "072_sigma_ed_gentler"
OUT.mkdir(parents=True, exist_ok=True)

CELLS = [
    ("sigmaed_005", 0.05),
    ("sigmaed_01",  0.10),
    ("sigmaed_02",  0.20),
    ("sigmaed_03",  0.30),
]
SEEDS = list(range(8))


def main() -> None:
    base = yaml.safe_load(BASE.read_text())
    n = 0
    for tag, sigma in CELLS:
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            cfg["simulator"]["price_formation_kwargs"]["sigma_ed"] = float(sigma)
            cfg["simulator"]["price_formation_kwargs"]["hawkes_sign_mode"] = "coherent"
            cfg["simulator"]["price_formation_kwargs"]["ed_normalize"] = False
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(
                yaml.safe_dump(cfg, sort_keys=False)
            )
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
