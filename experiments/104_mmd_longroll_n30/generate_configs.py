"""Exp 104 — Path B0: a FAIR test of distribution-matching (MMD) on a long rollout.

Why this exists (2026-05-29 review of exp 107):
  Path A (hand-built per-fact surrogates, exp 107) was FALSIFIED at the
  pre-registered Bonferroni gate (mf_all_mse_longroll +0.13 over baseline,
  p=0.81). Per the no-downgrade ladder we escalate to Path B; B0 is the
  cheapest move AND it re-tests a suspect prior negative: exp 085 concluded
  "marginal/distribution matching loses" (Wasserstein 4.46 < 4.64), but 085
  ran at chunk_steps=24 (~7 sim returns), so its distribution distance was
  estimated on ~7 samples — the same rollout-length trap that killed exp 102.
  See project_surrogate_rolloutlen_trap.

  Two things made the distribution-distance families untestable before now:
  (1) they were UNWIRED — train_distributed passed target_returns=None to
      compute_loss, so mmd/wasserstein/sinkhorn raised. Fixed 2026-05-29:
      the real return series is threaded as target_returns into the long
      rollout-reg path ONLY (the ~7-return main loop stays None, structural
      facts alone train fast dynamics there — MMD on 7 samples is meaningless).
  (2) exp 107 also surfaced that the N=2000 + bf16 budget regime is UNSTABLE:
      even baseline_v3 lost 8/30 seeds to aggregational_gaussianity blowup
      (vs 2/30 at the old N=10K/fp32), inflating the noise floor so nothing
      could pass a gate. rollout-reg is truncated BPTT (peak mem ~ one chunk),
      so N=10K/fp32 costs the SAME peak memory as the stable 099b baseline —
      the N cut was a throughput choice, not a memory requirement. So exp 104
      runs in the PROVEN-STABLE N=10K / fp32 regime.

MMD fires only on the 512-return rollout-reg rollout (enough samples for a
low-variance kernel estimate), against the full real SPX return series.

Deconfounded ladder (SPX, n=30 seeds), N=10K, fp32 (5 cells = 150 configs):
  baseline_v3           moments fast-path, NO reg      -> stable anchor (~4.64)
  hybrid_nomm_longroll  hybrid family, w_mmd=0, reg    -> hybrid-structural + long-rollout, NO MMD
  mmd_w{20,50,100}_longroll  hybrid, w_mmd in sweep, reg -> + MMD on 512-return rollout

Attribution:
  (best mmd_w* - hybrid_nomm_longroll) = PURE MMD effect (cells identical
    except w_mmd) -> the clean, isolated MMD test, across a 5x weight range.
  (hybrid_nomm_longroll - baseline_v3) = hybrid-structural switch + long-rollout.

PRE-REGISTERED FAILURE (binds the next move, no downgrade):
  if NO mmd_w* cell beats hybrid_nomm_longroll at Bonferroni p<0.05/3 (the
  isolated MMD comparison, corrected over the 3 sweep values) AND none exceeds
  baseline_v3 -> distribution-matching is FALSIFIED across a negligible->
  dominant weight range -> trigger Path B2 (heterogeneous-node MoE). If a
  w_mmd cell beats both -> promote THAT w_mmd to the 5-asset n=30 confirmation
  (exp 106) before any paper claim (no best-of-N claim off this screen).
  See papers/proposal/plan_v3_addendum_2026-05-28.md.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "099b_memk_refinement_n30" / "config_baseline_v3_seed0.yaml"
OUT = REPO / "experiments" / "104_mmd_longroll_n30"
OUT.mkdir(parents=True, exist_ok=True)

N_SEEDS = 30
N_AGENTS = 10000          # proven-stable regime (107's N=2000 destabilised agg-gaussianity)
PRECISION = "fp32"        # fp32 matches the stable 099b baseline

# Long-rollout regularization: SF + (for the MMD cell) distribution loss on a
# 512-return truncated-BPTT rollout. every=2 keeps the fp32/N=10K budget sane
# (~12x baseline compute on reg cells); H20 pre-flight confirms wall-clock.
REG = {
    "rollout_reg_enabled": True,
    "rollout_reg_steps": 512,
    "rollout_reg_chunk": 24,
    "rollout_reg_weight": 1.0,
    "rollout_reg_every": 2,
}

# Hybrid family keeps all structural weights from baseline_v3 (acf_sq, leverage,
# hill, hill_max, autocorr_r) and adds the MMD term. w_mmd=0 -> identical to the
# no-MMD control; w_mmd>0 -> MMD active on the long rollout. mmd_bandwidths
# default (0.005,0.01,0.02,0.05) span SPX daily-return scale (std ~0.01).
HYBRID = {"loss_family": "hybrid"}

# w_mmd CALIBRATION (scripts/_mmd_probe.py, untrained sim): raw MMD term ~0.012
# vs structural (acf_sq+lev) ~1.16, so w_mmd=1 makes MMD ~1% of the loss —
# negligible, an invalid test (same failure shape as the dead surrogates, new
# cause). w_mmd~50 makes MMD ~50% of structural. We SWEEP {20,50,100} (spanning
# negligible -> dominant) so a bad single guess can't invalidate the MMD test.
W_MMD_SWEEP = (20.0, 50.0, 100.0)

# cell -> (rollout-reg on?, loss_weights overrides)
CELLS: dict[str, tuple[bool, dict]] = {
    "baseline_v3":          (False, {}),
    "hybrid_nomm_longroll": (True, {**HYBRID, "w_mmd": 0.0}),
    **{f"mmd_w{int(w)}_longroll": (True, {**HYBRID, "w_mmd": w}) for w in W_MMD_SWEEP},
}


def _apply_common(cfg: dict) -> None:
    cfg["simulator"]["n_agents"] = N_AGENTS
    cfg["training"]["mixed_precision"] = PRECISION


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
    print(f"  N_AGENTS={N_AGENTS}  {PRECISION}  rollout_reg_steps={REG['rollout_reg_steps']} "
          f"every={REG['rollout_reg_every']}")
    print("  cells:", ", ".join(CELLS))


if __name__ == "__main__":
    main()
