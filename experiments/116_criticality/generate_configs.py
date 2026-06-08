"""Exp 116 v2 — finite-size-scaling (FSS) of the fat-tail overshoot in system size N.

REFRAMED 2026-06-08 after the v1 partial run (N=2000 only; N=10k OOM'd — fixed via the
lightweight trajectory recorder, see ecomd/inference/run_large.py). v1's N=2000 readout showed
hill(κ) is FLAT (~3.7–4.2 across κ∈[0,1.2], never crossing 2) — so κ (Hawkes self-excitation) is
NOT the control parameter. The control parameter is **N**: the overshoot (hill→1.3, α<2 infinite
variance) emerges between N=2000 (hill~4) and N=10000 (hill~1.3), consistent with the diagnosed
aggregate-flow-SNR ~ N mechanism ([[project_neural_sde_tournament]]).

So this probes the right axis: hill(N) at fixed learned dynamics. The physics question —
  is there a critical N_c where the tail index crosses α=2 (hill=2), and does the crossover
  show finite-size scaling (a rounded step sharpening toward a true transition in N→∞),
  or is it a smooth crossover (no critical point)?
A scaling collapse hill(N) = f((N−N_c)/N_c · N^{1/ν}) would be a genuine non-equilibrium
emergent-criticality result; a smooth logistic crossover keeps the honest "aggregate-flow
crossover" reading. Either way it is the load-bearing readout for the Paper B fork.

Pure inference (run_large, lightweight) from frozen baseline checkpoints — NO retraining.

Grid (emitted as config OVERRIDES; the launcher applies each to N_CKPT anchor checkpoints,
with N_REALIZATIONS seeds each for hill CIs):
  N ∈ {1000, 2000, 3000, 4000, 6000, 8000, 10000, 14000}   (8 sizes, dense in the crossover)
  κ ∈ {0.0, 0.4, 0.8, 1.2}                                  (4; κ=0 is the main FSS line, others
                                                              test whether κ shifts N_c)
  = 32 scan configs × N_CKPT anchors × N_REALIZATIONS seeds.
ed_normalize=False (the overshoot regime). With the lightweight recorder, N=14000 × T=8000
inference is ~O(T) memory — fits a single card.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "116_criticality"
OUT.mkdir(parents=True, exist_ok=True)

N_SIZES = [1000, 2000, 3000, 4000, 6000, 8000, 10000, 14000]   # FSS ladder
KAPPAS = [0.0, 0.4, 0.8, 1.2]                                  # κ=0 primary; others = shift test


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    n = 0
    for N in N_SIZES:
        for kap in KAPPAS:
            cfg = yaml.safe_load(yaml.safe_dump(base))  # deep copy
            cfg["simulator"]["n_agents"] = N
            cfg["simulator"]["price_formation_kwargs"]["hawkes_kappa"] = kap
            cfg["simulator"]["price_formation_kwargs"]["ed_normalize"] = False
            ktag = f"{kap:.1f}".replace(".", "")
            (OUT / f"config_N{N}_k{ktag}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} scan configs ({len(N_SIZES)} N × {len(KAPPAS)} κ) to {OUT}")
    print(f"  N ∈ {N_SIZES}")
    print(f"  κ ∈ {KAPPAS}  ed_normalize=False (overshoot regime)")
    print("  launcher: × N_CKPT anchors × N_REALIZATIONS seeds, lightweight run_large (no OOM).")


if __name__ == "__main__":
    main()
