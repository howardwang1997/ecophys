"""Exp 103 — Thread 3: advanced architecture × expanded loss (SPX screen, n=30).

Key correction from in-repo recon (2026-05-26): baseline_v3 ALREADY enables
global_state (+into_pair), edge_gating, twopop, stochastic_mlp (SPS) pairwise and
t-noise. So "turn on global state" is NOT an untested lever. The genuinely untested
*config-only* expressivity levers are:
  - isab attention pairwise (baseline = stochastic_mlp)  — the GASim-transferable seed
  - inner_steps_per_price > 1 (baseline = 1)             — adiabatic AR(1)-drift fix
  - agent_memory (baseline = off)                        — per-agent GRU latent

Critical design rule: never sweep architecture against the 3-moment loss again
(that conflated capacity with objective). Every 103 cell runs on the EXPANDED loss
(mf_all_mse: the 4 multi-fact surrogates + mse distance) so capacity is tested where
it can actually be used. Also a global_state-OFF ablation, to ask whether the
already-on global_state matters under the expanded objective.

Learned state-dependent diffusion (neural-SDE, 3c) needs an integrator code change
and is deferred to Batch 2 to avoid rushing a code change into the 2-day batch.

Grid (~12 cells + baseline ref = 13 × 30 = 390 cfg, SPX only). Decision gate as 102:
SPX cells beating baseline_v3 promote to the 5-asset confirmation (exp 106).
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "099b_memk_refinement_n30" / "config_baseline_v3_seed0.yaml"
OUT = REPO / "experiments" / "103_arch_expanded_loss_n30"
OUT.mkdir(parents=True, exist_ok=True)

N_SEEDS = 30

# Expanded loss applied to ALL 103 cells (multi-fact + mse distance).
EXPANDED_LOSS = {
    "distance_mode": "mse",
    "w_gain_loss": 0.3, "w_agg_gauss": 0.3, "w_fano": 0.3, "w_dfa_hurst": 0.2,
}

# Architecture overrides (simulator section). The reference cell `exploss_base`
# is baseline_v3 arch + expanded loss → isolates "expanded loss alone".
CELLS: dict[str, dict] = {
    "exploss_base": {},
    "isab": {"pairwise_kind": "isab"},
    "isab_m32": {"pairwise_kind": "isab", "isab_m_inducing": 32},
    "isab_m128": {"pairwise_kind": "isab", "isab_m_inducing": 128},
    "inner2": {"inner_steps_per_price": 2},
    "inner4": {"inner_steps_per_price": 4},
    "inner8": {"inner_steps_per_price": 8},
    "agentmem": {"agent_memory_enabled": True},
    "gstate_off": {"global_state_enabled": False},  # ablation of an already-on mechanism
    "isab_inner4": {"pairwise_kind": "isab", "inner_steps_per_price": 4},
    "agentmem_inner4": {"agent_memory_enabled": True, "inner_steps_per_price": 4},
    "isab_agentmem": {"pairwise_kind": "isab", "agent_memory_enabled": True},
}


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    assert base["training"].get("target_dataset", "spx") == "spx", "103 is SPX-only screen"

    n = 0
    # reference: baseline arch on the LEGACY moments loss (so 103 has a same-batch
    # baseline_v3 anchor identical to other experiments' reference cell).
    for seed in range(N_SEEDS):
        cfg = copy.deepcopy(base)
        cfg["training"]["seed"] = seed
        (OUT / f"config_baseline_v3_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
        n += 1

    for tag, sim_ov in CELLS.items():
        for seed in range(N_SEEDS):
            cfg = copy.deepcopy(base)
            cfg["training"]["loss_weights"].update(EXPANDED_LOSS)
            cfg["simulator"].update(sim_ov)
            cfg["training"]["seed"] = seed
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1

    print(f"wrote {n} configs ({len(CELLS)} cells + baseline) × {N_SEEDS} seeds to {OUT}")


if __name__ == "__main__":
    main()
