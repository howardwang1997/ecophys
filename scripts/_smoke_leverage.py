"""Scratch smoke (2026-06-09) — does the leverage mechanism (asym_drag / zumbach-downside) move
leverage_effect toward the band [-6,-0.5] and run clean? UNTRAINED sim → absolute facts are not
in band; this checks (a) the mechanism is wired & error-free, (b) the SIGN/direction of its effect
on leverage_effect, with hill/acf² as collateral guards. The collateral-free in-band test is the
H20 sweep (experiments/117_leverage). Mac: torch.set_num_threads(1) for BLAS determinism.
"""
from __future__ import annotations
import sys, time
import numpy as np, torch, yaml
torch.set_num_threads(1)
from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.eval.stylized_facts import compute_all

BASE = yaml.safe_load(open("experiments/108_neural_sde_scout/config_baseline_mmd_seed0.yaml"))
SIM = dict(BASE["simulator"]); SIM["n_agents"] = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
N_STEPS = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
SEEDS = [10_000, 10_001]

CELLS = {
    "baseline":   {},
    "asym_0.4":   {"asym_drag_alpha": 0.4},
    "asym_0.7":   {"asym_drag_alpha": 0.7},
    "zumb_down":  {"zumbach_feedback_lambda": 0.92, "zumbach_feedback_strength": 0.6,
                   "zumbach_feedback_mode": "downside"},
    "asym+zumb":  {"asym_drag_alpha": 0.5, "zumbach_feedback_lambda": 0.92,
                   "zumbach_feedback_strength": 0.4, "zumbach_feedback_mode": "downside"},
}

def _est(facts, key):
    v = facts[key].to_dict()
    return v.get("estimate", v.get("value"))

print(f"# leverage smoke  N={SIM['n_agents']} T={N_STEPS} seeds={SEEDS}  (UNTRAINED — direction only)")
print(f"# leverage_effect target band [-6,-0.5]; hill [2,4]; acf² [0.15,0.55]\n")
print(f"{'cell':12}{'leverage':>11}{'hill':>8}{'acf2':>8}{'sec':>7}")
base_lev = None
for name, ov in CELLS.items():
    levs, hills, acfs = [], [], []
    t0 = time.time()
    for sd in SEEDS:
        cfg = dict(SIM); cfg.update(ov)
        sim = EcoMDSimulator(EcoMDConfig(**cfg)); sim.eval()
        traj = sim.run(n_steps=N_STEPS, seed=sd, lightweight=True)
        r = traj.log_returns_np()[1:]
        del traj
        f = compute_all(r)
        levs.append(_est(f, "leverage_effect")); hills.append(_est(f, "hill_tail_index"))
        acfs.append(_est(f, "acf_squared_returns"))
    lev, hill, acf = np.nanmean(levs), np.nanmean(hills), np.nanmean(acfs)
    if name == "baseline":
        base_lev = lev
    dlt = "" if base_lev is None else f"  (Δlev {lev - base_lev:+.2f})"
    print(f"{name:12}{lev:>11.2f}{hill:>8.2f}{acf:>8.2f}{time.time()-t0:>7.1f}{dlt}")
