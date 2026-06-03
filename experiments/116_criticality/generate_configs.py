"""Exp 116 — criticality probe: is the fat-tail overshoot a non-equilibrium PHASE TRANSITION?

The diagnose (109/112) says the overshoot is DYNAMICAL and driven by SYNCHRONIZED aggregate order
flow (aggregate-flow SNR ~N). That smells like a collective/critical phenomenon: a control parameter
(self-excitation coupling κ = hawkes_kappa) where the tail exponent crosses α=2 (hill crosses 2)
as the market synchronizes. This probe sweeps κ finely at TWO system sizes N for a finite-size-
scaling (FSS) read:
  • a TRUE critical point → the hill(κ) transition SHARPENS with N (the crossover steepens, κ_c
    converges) — a real phase transition.
  • a smooth crossover → no N-dependence in sharpness.

Dual purpose:
  - Paper A: mechanistic DEPTH for "why tails overshoot" (the diagnose section).
  - Paper B: the GO/NO-GO for the synchronization-transition flagship fork (a critical point with
    scaling = a real non-equilibrium phase transition in markets, not a thermodynamic analogy).

Pure inference (run_large) from existing baseline checkpoints — NO retraining. This is the un-run
112 Part B B2, extended with a 2nd N for FSS and a finer κ grid near the expected transition.

Emits config OVERRIDES (the launcher applies each to every anchor checkpoint via run_large):
  κ ∈ {0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2}  (13 pts, finer can be added near κ_c)
  × N ∈ {2000, 10000}                                       (FSS pair)
  = 26 scan configs × N_CKPT anchor checkpoints.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "116_criticality"
OUT.mkdir(parents=True, exist_ok=True)

KAPPAS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
N_SIZES = [2000, 10000]  # FSS pair


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    n = 0
    for N in N_SIZES:
        for kap in KAPPAS:
            cfg = yaml.safe_load(yaml.safe_dump(base))  # deep copy
            cfg["simulator"]["n_agents"] = N
            cfg["simulator"]["price_formation_kwargs"]["hawkes_kappa"] = kap
            cfg["simulator"]["price_formation_kwargs"]["ed_normalize"] = False  # the overshoot regime
            tag = f"N{N}_k{str(kap).replace('.', '')}"
            (OUT / f"config_{tag}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} scan configs ({len(N_SIZES)} N × {len(KAPPAS)} κ) to {OUT}")
    print(f"  κ ∈ {KAPPAS}")
    print(f"  N ∈ {N_SIZES} (finite-size-scaling pair)  ed_normalize=False (overshoot regime)")
    print("  launcher applies each to N_CKPT baseline checkpoints via run_large (pure inference).")


if __name__ == "__main__":
    main()
