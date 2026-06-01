"""Exp 112 Part B — α scaling-curve diagnose (pure inference, no retraining).

Tests the conjecture behind the fat-tail overshoot (why hill<2, infinite variance):
the heavy tail is an emergent COLLECTIVE property of the coupled-agent dynamics, and
its exponent is set by (i) system size N and (ii) the self-excitation feedback
strength. These configs are run by run_large from the TRAINED baseline checkpoints
(Part A) — same learned potential, only the control parameter varies.

Why these knobs (and not temperature): log_gamma/log_temperature are nn.Parameters
→ a loaded checkpoint OVERRIDES any config temperature_init, so temperature is NOT
scannable this way. beta/kappa/hawkes_kappa/ed_normalize live in ExcessDemandParams
(plain floats, not in the state_dict) → they DO bite under a loaded checkpoint. N is
free (the N-sized buffers are persistent=False, rebuilt deterministically).

THREE scan families (each run from 3 baseline checkpoints, n_steps=8000):

  B1  N-sweep            n_agents ∈ {250..20000}, ed_normalize=False (baseline)
        -> hill(N): does the tail fatten with system size? (smoke: 3.06@400 → 1.39@10K)
  B1n N-sweep CONTROL    same N-sweep, ed_normalize=True (÷√N on excess demand)
        -> prediction: hill(N) FLATTENS → isolates unnormalized aggregate-flow SNR
           as THE mechanism (the collective mode ~N vs idiosyncratic noise ~√N).
  B2  hawkes_kappa-sweep self-excitation feedback ∈ {0..1.2} at N=10K
        -> hill(κ) AND acf2(κ) jointly: the feedback is the SHARED source of fat
           tails (#2) and clustering (#6/#8) — this maps the Pareto coupling against
           the actual control parameter.

PRE-REGISTERED analysis (score_scaling.py):
  B1:  fit hill(N) = α_inf + c·N^(-ν); report α_inf (CI) + the N where hill crosses 2.
       α_inf < 2 ⇒ the trained dynamics are intrinsically infinite-variance in the
       thermodynamic limit (a strong, falsifiable physics claim). B1n flat confirms
       the SNR mechanism.
  B2:  κ* where hill enters [2,4]; the κ-window where acf2 stays in band. DISJOINT ⇒
       Pareto coupling confirmed vs the control parameter (strongest diagnose form).
       OVERLAP ⇒ a coupling-tuned operating point exists (a knob-solve) → 5-asset.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "112_tail_clamp" / "scaling"
OUT.mkdir(parents=True, exist_ok=True)

N_SWEEP = [250, 500, 1000, 2000, 5000, 10000, 20000]
HAWKES_SWEEP = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.2]


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    configs: dict[str, dict] = {}

    # B1 — N-sweep (baseline ed_normalize=False) and B1n control (ed_normalize=True)
    for ednorm, fam in [(False, "B1_N"), (True, "B1n_Nnorm")]:
        for n in N_SWEEP:
            cfg = copy.deepcopy(base)
            cfg["simulator"]["n_agents"] = n
            cfg["simulator"]["price_formation_kwargs"]["ed_normalize"] = ednorm
            configs[f"{fam}_n{n}"] = cfg

    # B2 — self-excitation feedback sweep at N=10K (baseline N)
    for hk in HAWKES_SWEEP:
        cfg = copy.deepcopy(base)
        cfg["simulator"]["price_formation_kwargs"]["hawkes_kappa"] = hk
        configs[f"B2_hk{hk:g}"] = cfg

    for tag, cfg in configs.items():
        (OUT / f"config_{tag}.yaml").write_text(yaml.safe_dump(cfg))

    print(f"wrote {len(configs)} scaling configs to {OUT}")
    print(f"  B1  N-sweep (ed_norm=False): {N_SWEEP}")
    print(f"  B1n N-sweep (ed_norm=True ): {N_SWEEP}  [control: should flatten hill(N)]")
    print(f"  B2  hawkes_kappa-sweep @N=10K: {HAWKES_SWEEP}")
    print("  run via scripts/h20_112_scaling.sh (run_large from 3 baseline checkpoints).")


if __name__ == "__main__":
    main()
