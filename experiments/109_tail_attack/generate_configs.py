"""Exp 109 — Bracket-0 TAIL-SHAPE ATTACK (config-only; run first, cheapest).

Diagnosis (exp 108 scout): the dominant unbroken floor is a fat-tail OVERSHOOT —
hill_tail_index ≈ 1.38 with 91% of runs α<2 (infinite-variance regime), band [2,4].
Source: agent-level noise_dist="t" (Student-t df=5) + compound-Poisson jumps
(jump_lambda=0.5). The SV head amplifies it. This bracket attacks the overshoot
directly by taming the agent-level tail SOURCES and asks the pre-registered
question: can hill enter [2,4] WITHOUT collapsing Fano #5 or agg-gauss #4?

This is a fast MECHANISM SCREEN of the return marginal, so rollout-reg/MMD is OFF
(~10 min/cfg vs ~36 with reg) — the tail is set by noise_dist/jumps, not the loss.
The winning tail-taming setting then COMPOSES into the MMD-trained A2/SV cells in
Bracket 1 (turn down the Lévy source, recover tails from mechanism/heterogeneity).

Cells (9 × 15 seeds = 135 cfg, SPX, N=10K fp32, reg OFF):
  anchor_t5_j05        noise t/df5,  jump 0.5  sv off   (= current baseline source)
  t10_j05              noise t/df10, jump 0.5  sv off   (lighter Student-t)
  t30_j05              noise t/df30, jump 0.5  sv off   (near-Gaussian t)
  normal_j05           noise normal, jump 0.5  sv off   (no Student-t tail)
  t10_j01              noise t/df10, jump 0.1  sv off   (fewer jumps)
  t10_j00              noise t/df10, jump 0.0  sv off   (no jumps)
  normal_j00           noise normal, jump 0.0  sv off   (lightest: pure Gaussian source)
  t10_j01_sv           noise t/df10, jump 0.1  sv_d3    (does SV compose with tamed noise?)
  normal_j00_sv        noise normal, jump 0.0  sv_d3    (SV provides the tail from clustering)

Read: hill (→[2,4]) vs Fano #5 (keep ≥ band) vs agg-gauss #4 trade-off. Pick the
setting that lands hill in-band with least collateral; feed it to Bracket 1.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "109_tail_attack"
OUT.mkdir(parents=True, exist_ok=True)

N_SEEDS = 15

SV_D3 = {"sv_price_enabled": True, "sv_d": 3, "sv_leverage": True,
         "sv_state_dep": False, "sv_v_clip": 3.0, "sv_gain_init": 0.5}

# cell -> (noise_dist, noise_df, jump_lambda, sv_kwargs_or_None)
CELLS: dict[str, tuple[str, int, float, dict | None]] = {
    "anchor_t5_j05": ("t", 5, 0.5, None),
    "t10_j05":       ("t", 10, 0.5, None),
    "t30_j05":       ("t", 30, 0.5, None),
    "normal_j05":    ("normal", 5, 0.5, None),   # noise_df ignored for normal
    "t10_j01":       ("t", 10, 0.1, None),
    "t10_j00":       ("t", 10, 0.0, None),
    "normal_j00":    ("normal", 5, 0.0, None),
    "t10_j01_sv":    ("t", 10, 0.1, SV_D3),
    "normal_j00_sv": ("normal", 5, 0.0, SV_D3),
}


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    assert base["training"].get("target_dataset", "spx") == "spx", "109 is SPX-only screen"

    n = 0
    for tag, (ndist, ndf, jlam, sv) in CELLS.items():
        for seed in range(N_SEEDS):
            cfg = copy.deepcopy(base)
            cfg["training"]["seed"] = seed
            cfg["training"]["rollout_reg_enabled"] = False   # fast marginal screen
            cfg["simulator"]["noise_dist"] = ndist
            cfg["simulator"]["noise_df"] = ndf
            cfg["simulator"]["jump_lambda"] = jlam
            pfk = dict(cfg["simulator"].get("price_formation_kwargs", {}))
            if sv is not None:
                pfk.update(sv)
            else:
                # ensure SV off (base baseline_mmd has none, but be explicit)
                pfk.pop("sv_price_enabled", None)
            cfg["simulator"]["price_formation_kwargs"] = pfk
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1

    print(f"wrote {n} configs ({len(CELLS)} cells × {N_SEEDS} seeds) to {OUT}")
    print(f"  N={base['simulator']['n_agents']} {base['training']['mixed_precision']} reg=OFF (fast tail screen)")
    print("  cells:", ", ".join(CELLS))


if __name__ == "__main__":
    main()
