"""Exp 104 — Batch 1b: the FIRST fair test of the objective-coverage hypothesis.

Why this exists (2026-05-28 review of exp 102/103):
  exp 102 added per-fact surrogates to the loss but did NOT test the hypothesis —
  the training rollout feeds only ~7 returns (chunk_steps=24, warmup=16), while
  soft_fano needs n>=50, dfa_hurst needs n>=~200, agg_gaussianity needs n>=400
  for the correct (k1-kL) signal. So mf_fano/mf_dfa were bit-identical to baseline
  (zero gradient) and mf_agg optimised a degraded k1-only signal. Only skew was
  live. Diagnostic: scripts/diagnose_surrogate_coverage.py.

The fix is configuration-only (no ecomd/ change): the existing rollout-reg path
(`_compute_rollout_reg_loss`, 057) computes the SF loss on a multi-chunk truncated-
BPTT rollout of `rollout_reg_steps` returns, with peak memory ~one chunk. Setting
rollout_reg_steps=512 puts ALL four surrogates in their live regime while staying
inside the chunk<=24 / N memory envelope (project_chunk_oom_constraint). Verified
on Mac N=500 (scripts/_m2_probe.py): all 4 surrogate terms grad_fn=LIVE, gradient
reaches 25/28 params.

Deconfounded 3-cell ladder (SPX, n=30 seeds; N dropped 10K->2000 per the no-OOM
budget — typical agent-based market sims use N<=1000, so 2000 is generous):
  baseline_v3          N=2000, moments/l1, NO rollout-reg     → new-N baseline
  longroll_moments     N=2000, moments/l1, rollout-reg ON     → isolates long-rollout-alone
  mf_all_mse_longroll  N=2000, moments+4 surrogates/mse, reg  → full objective-coverage test

Attribution: (mf_all_mse_longroll vs longroll_moments) = the surrogate effect with
long rollout held fixed; (longroll_moments vs baseline_v3) = long-rollout-alone.

PRE-REGISTERED FAILURE (binds the next move, no downgrade): if mf_all_mse_longroll
does NOT beat baseline_v3 at Bonferroni p<0.05 (2 comparisons) → objective-coverage
is formally falsified → trigger Path B (heterogeneous-node MoE first). See
papers/proposal/plan_v3_addendum_2026-05-28.md.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "099b_memk_refinement_n30" / "config_baseline_v3_seed0.yaml"
OUT = REPO / "experiments" / "104_multifact_longroll_n30"
OUT.mkdir(parents=True, exist_ok=True)

N_SEEDS = 30
N_AGENTS = 2000

# Multi-fact surrogate weights (same as exp 102 mf_all_* "ALL").
ALL = {"w_gain_loss": 0.3, "w_agg_gauss": 0.3, "w_fano": 0.3, "w_dfa_hurst": 0.2}

# Long-rollout regularization config: surrogate loss computed on 512-return
# truncated-BPTT rollout every iter, so fano/dfa/agg are all live.
REG = {
    "rollout_reg_enabled": True,
    "rollout_reg_steps": 512,
    "rollout_reg_chunk": 24,
    "rollout_reg_weight": 1.0,
    "rollout_reg_every": 1,
}

# cell -> (rollout-reg on?, loss_weights overrides)
CELLS: dict[str, tuple[bool, dict]] = {
    "baseline_v3":         (False, {}),
    "longroll_moments":    (True, {}),
    "mf_all_mse_longroll": (True, {**ALL, "distance_mode": "mse"}),
}


def _apply_common(cfg: dict) -> None:
    cfg["simulator"]["n_agents"] = N_AGENTS
    cfg["training"]["mixed_precision"] = "bf16"


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    assert base["training"].get("target_dataset", "spx") == "spx", "104 is SPX-only screen"

    n = 0
    for tag, (reg_on, loss_over) in CELLS.items():
        for seed in range(N_SEEDS):
            cfg = copy.deepcopy(base)
            _apply_common(cfg)
            cfg["training"]["seed"] = seed
            if reg_on:
                cfg["training"].update(REG)
            if loss_over:
                cfg["training"]["loss_weights"].update(loss_over)
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1

    print(f"wrote {n} configs ({len(CELLS)} cells × {N_SEEDS} seeds) to {OUT}")
    print(f"  N_AGENTS={N_AGENTS}  bf16  rollout_reg_steps={REG['rollout_reg_steps']} every={REG['rollout_reg_every']}")
    print("  cells:", ", ".join(CELLS))


if __name__ == "__main__":
    main()
