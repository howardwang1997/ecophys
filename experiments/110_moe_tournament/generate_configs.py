"""Exp 110 — A2 heterogeneous-node MoE entrant (Bracket-1 solve).

Hypothesis (exp 108 diagnosis): the fat-tail floor is an OVERSHOOT to α<2 from
agent-level Student-t + jumps. A learned soft mixture over K (gamma,temp) experts
(ecomd/models/moe_router.py) makes a finite-variance mixture-of-normals — leptokurtic
with FINITE variance → hill into [2,4] — letting us turn DOWN noise_df/jumps.

Built on the 108 baseline_mmd sim cfg (N=10K fp32, hybrid+MMD, custom-fn BPTT),
rollout_reg_every=4 (weekend). MoE load-balance reg (anti-collapse) is added by the
trainer hook. NOTE (Mac N=500 smoke): taming noise alone did NOT fix hill — there is
a dynamical tail source too; this experiment quantifies how far mixture+tamed-noise
gets at N=10K with real training (compose with the Bracket-0 109 tail-attack finding).

Cells (5 × 30 seeds = 150 cfg, SPX, N=10K fp32, MMD long-rollout every=4):
  baseline_tamed     normal noise, jump 0, NO moe        -> control: does taming noise alone do it?
  moe_k4_tamed       normal noise, jump 0, moe K=4       -> mixture fat-tails from heterogeneity
  moe_k4_t5          t/df5, jump 0.5, moe K=4            -> moe on top of the existing noise source
  moe_k8_tamed       normal noise, jump 0, moe K=8       -> more mixture components
  moe_k4_tamed_info  normal, jump 0, moe K=4 + info-asym -> NESS channel (Paper B)

Attribution: (moe_k4_tamed - baseline_tamed) = mixture effect; (moe_k8 - moe_k4) =
#experts; (moe_k4_tamed_info - moe_k4_tamed) = information-asymmetry channel.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "110_moe_tournament"
OUT.mkdir(parents=True, exist_ok=True)

N_SEEDS = 30
REG_EVERY = 4

# cell -> (noise_dist, jump_lambda, moe_kwargs_or_None)
def moe(k: int, info: bool = False) -> dict:
    return {"moe_enabled": True, "moe_n_experts": k, "moe_load_balance_w": 0.01,
            "info_asym_enabled": info, "info_asym_frac": 0.3}

CELLS: dict[str, tuple[str, float, dict | None]] = {
    "baseline_tamed":    ("normal", 0.0, None),
    "moe_k4_tamed":      ("normal", 0.0, moe(4)),
    "moe_k4_t5":         ("t", 0.5, moe(4)),
    "moe_k8_tamed":      ("normal", 0.0, moe(8)),
    "moe_k4_tamed_info": ("normal", 0.0, moe(4, info=True)),
}


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    assert base["training"].get("target_dataset", "spx") == "spx", "110 is SPX-only"

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
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1

    print(f"wrote {n} configs ({len(CELLS)} cells × {N_SEEDS} seeds) to {OUT}")
    print(f"  N={base['simulator']['n_agents']} {base['training']['mixed_precision']} "
          f"reg_every={REG_EVERY}  cells:", ", ".join(CELLS))


if __name__ == "__main__":
    main()
