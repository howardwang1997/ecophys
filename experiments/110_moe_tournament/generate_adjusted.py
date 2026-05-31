"""Exp 110 adjusted — extra MoE cells informed by exp 109 tail-attack results.

109 showed normal_j00 is best (5.20/11) but hill=1.30 still far below [2,4].
The tail source is dynamical, not distributional. Add MoE cells with t10_j01
noise (2nd best in 109, hill=1.61) and t10_j00 (lighter tail) to see if
MoE heterogeneity composes better with intermediate tail settings.
Also add moe_k4 with sv_d3 (MoE + learned vol) and moe_k4_tamed with lower
load_balance_w to test sensitivity.

Additional cells (5 × 30 = 150 cfg), appended to the existing 110 directory.
Run after the fixed 110 configs.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "110_moe_tournament"

N_SEEDS = 30
REG_EVERY = 4

SV_D3 = {"sv_price_enabled": True, "sv_d": 3, "sv_leverage": True,
         "sv_state_dep": False, "sv_v_clip": 3.0, "sv_gain_init": 0.5}

def moe(k: int, info: bool = False, lbw: float = 0.01) -> dict:
    return {"moe_enabled": True, "moe_n_experts": k, "moe_load_balance_w": lbw,
            "info_asym_enabled": info, "info_asym_frac": 0.3}

CELLS: dict[str, tuple[str, float, dict | None]] = {
    "moe_k4_t10j01":       ("t", 0.1, moe(4)),
    "moe_k4_t10j00":       ("t", 0.0, moe(4)),
    "moe_k4_tamed_lbw001": ("normal", 0.0, moe(4, lbw=0.001)),
    "moe_k4_tamed_sv":     ("normal", 0.0, moe(4)),
    "moe_k8_t10j01":       ("t", 0.1, moe(8)),
}


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())

    n = 0
    for tag, (ndist, jlam, mk) in CELLS.items():
        for seed in range(N_SEEDS):
            cfg = copy.deepcopy(base)
            cfg["training"]["seed"] = seed
            cfg["training"]["rollout_reg_every"] = REG_EVERY
            cfg["simulator"]["noise_dist"] = ndist
            cfg["simulator"]["jump_lambda"] = jlam
            if mk:
                cfg["simulator"].update(mk)
            if tag.endswith("_sv"):
                pfk = dict(cfg["simulator"].get("price_formation_kwargs", {}))
                pfk.update(SV_D3)
                cfg["simulator"]["price_formation_kwargs"] = pfk
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1

    print(f"wrote {n} ADJUSTED configs ({len(CELLS)} cells × {N_SEEDS} seeds) to {OUT}")
    print("  cells:", ", ".join(CELLS))


if __name__ == "__main__":
    main()
