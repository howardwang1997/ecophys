"""Track B-α Hopfield regime pilot at n=30 (Paper A "solve" half).

B-α rationale (paper_a_next_steps_2026-05-21.md §5): Modern-Hopfield attention
over K learnable prototypes replaces the v3 RegimeGRU. K prototypes act as
attractors of an energy landscape; sharp attention (large β) lets each regime
use a near-pure mechanism subset via the same RegimeReadHead plumbing
(γ_mult(h), T_mult(h), κ_mult(h)). Implemented as drop-in via
``regime_kind="hopfield"`` in EcoMDConfig; force-pipeline unchanged — the
"K mechanism mixes" claim from the spec emerges implicitly from the K
prototype embeddings + non-linear read heads.

Pilot grid (24 cells = 3 K × 4 β × 2 update_every + 1 baseline):

    hopfield_n_prototypes ∈ {4, 6, 8}              (3 values)
    hopfield_beta        ∈ {4, 8, 16, 32}          (4 values)
    regime_update_every  ∈ {4, 8}                  (2 values)

Other hyperparams fixed:
    hopfield_query_hidden = 16
    hopfield_collapse_reg = 0.0  (diagnostic only; aux loss not wired in
                                  training_loop yet)
    regime_d = 16 (matches v3 RegimeGRU default)

Plus baseline_v3 reference (regime_kind='gru', identical otherwise).

25 cells × 30 seeds = 750 configs ≈ 15.6h on 8-card H20.

Decision gates (Paper A §5.2 contribution criteria, per spec §5.4):
- IF best cell n=30 mean ≥ 5.5 AND prototype mean cosine sim < 0.7
  → B-α confirmed, fund full 900-cfg 5-asset sweep (paper_a_next_steps §5.3 plan)
- IF any cell has prototype mean cos sim > 0.9 across most seeds
  → prototypes collapse — re-design attention (+1 wk) before expanding
- IF best cell mean ≥ 6.5 on this single-asset SPX pilot
  → §6 paper headline candidate; promote to NeurIPS abstract bullet
- IF best < 5.2
  → demote to §5.4 future-work footnote
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "099b_memk_refinement_n30" / "config_baseline_v3_seed0.yaml"
OUT = REPO / "experiments" / "track_b_alpha_pilot_n30"
OUT.mkdir(parents=True, exist_ok=True)


N_PROTOTYPES = [4, 6, 8]
BETAS = [4.0, 8.0, 16.0, 32.0]
UPDATE_EVERY = [4, 8]

N_SEEDS = 30


def _apply_bbalpha(cfg: dict, K: int, beta: float, update_every: int) -> None:
    sim = cfg["simulator"]
    # Ensure regime infrastructure is active (the base config has it on).
    sim["regime_enabled"] = True
    sim["regime_kind"] = "hopfield"
    sim["regime_d"] = 16
    sim["regime_update_every"] = int(update_every)
    sim["regime_modulate_gamma"] = True
    sim["regime_modulate_temp"] = True
    sim["regime_modulate_kappa"] = True
    sim["hopfield_n_prototypes"] = int(K)
    sim["hopfield_beta"] = float(beta)
    sim["hopfield_query_hidden"] = 16


def _cell_tag(K: int, beta: float, ue: int) -> str:
    return f"ha_K{K:02d}_b{int(round(beta)):03d}_u{ue:02d}"


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())

    # Sanity: confirm base has regime_enabled=true (v3 default for 099b).
    if not base.get("simulator", {}).get("regime_enabled", False):
        print("[WARN] base config does not have regime_enabled=true; setting it")

    n = 0
    for K in N_PROTOTYPES:
        for beta in BETAS:
            for ue in UPDATE_EVERY:
                tag = _cell_tag(K, beta, ue)
                for seed in range(N_SEEDS):
                    cfg = copy.deepcopy(base)
                    _apply_bbalpha(cfg, K, beta, ue)
                    cfg["training"]["seed"] = seed
                    (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
                    n += 1

    # baseline reference (legacy RegimeGRU — explicit regime_kind='gru')
    for seed in range(N_SEEDS):
        cfg = copy.deepcopy(base)
        cfg["simulator"]["regime_kind"] = "gru"  # explicit, matches 'auto' default
        cfg["training"]["seed"] = seed
        (OUT / f"config_baseline_v3_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
        n += 1

    print(f"wrote {n} configs ({len(N_PROTOTYPES)}*{len(BETAS)}*{len(UPDATE_EVERY)} = "
          f"{len(N_PROTOTYPES)*len(BETAS)*len(UPDATE_EVERY)} grid + 1 baseline) × {N_SEEDS} seeds to {OUT}")


if __name__ == "__main__":
    main()
