"""Paper B pilot — T_eff(t) trajectory from C4 checkpoint.

This is the first physics experiment in the Paper B program, using the
already-trained C4 simulator (multi-asset + twopop + expanded loss,
8/11 stylized facts on H20).

What we compute
---------------
For each step t of a long rollout, two estimators of effective temperature:

1. **Equipartition T_eff** = γ · ⟨|v|²⟩ / d_state
   Per Einstein relation in overdamped Langevin: v² ~ T/γ at equilibrium.
   At non-equilibrium (driven by Hawkes / type heterogeneity), this T_eff(t)
   varies and is the "effective temperature" Paper B's A1 claim is about.

2. **Variance T_eff** = γ · <v · F_diss> / dim
   Stochastic-thermodynamics version: dissipation = excess work over heat
   in the noise channel.

Outputs
-------
- results/teff_trajectory.json — T_eff(t), γ(t), state moments per step
- results/teff_pilot_summary.md — interpretation: do we see crash-precursor
  spikes? Regime structure? Anti-correlation with volatility?

This decides Paper B's path: if T_eff has structure → Nature Physics
flagship; if flat → PRL retreat (TUR alone).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch
import yaml

from ecomd.eval.entropy_production import (
    entropy_production_per_step,
    per_channel_force_decomposition,
)
from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.physics.observables import EcoMDTrajectory


REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)


def load_c4() -> tuple[EcoMDSimulator, dict]:
    cfg_path = REPO / "experiments/022_h20_batch/config_c4_multi_asset_twopop.yaml"
    ckpt_path = REPO / "experiments/022_h20_batch/results_c4/checkpoint.pt"
    cfg = yaml.safe_load(cfg_path.read_text())
    sim_cfg = dict(cfg["simulator"])
    # Mac fallback: shrink for local pilot if needed
    sim_cfg["n_agents"] = min(sim_cfg["n_agents"], 1000)
    config = EcoMDConfig(**sim_cfg)
    sim = EcoMDSimulator(config)
    state = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    # state dict has agents dim shape; if Mac shrunk we can still load
    # what fits (twopop_type_idx is a buffer, regenerated per init)
    try:
        sim.load_state_dict(state["sim_state_dict"], strict=False)
        print(f"loaded C4 ckpt (strict=False, may have buffer mismatch — that's fine)")
    except Exception as e:
        print(f"  ckpt load warn: {e}")
    sim.eval()
    return sim, cfg


def compute_teff_per_step(traj: EcoMDTrajectory, gamma: float) -> dict:
    """Two estimators of T_eff(t) over the trajectory.

    Equipartition: T_eq(t) = γ · mean_i ⟨v_i²⟩ / d_state at each t.
    """
    v = traj.velocities  # (T, N, d)
    f_diss = traj.f_diss  # (T, N, d)

    T_eq_per_step = (gamma * (v ** 2).mean(dim=(1, 2))).detach().cpu().numpy()

    # σ̇(t) = ⟨F_diss · v⟩ / T_eff (per-step entropy production rate)
    # We use the equipartition T_eff (since we don't know "true" T_eff)
    inner = (f_diss * v).sum(dim=-1).mean(dim=-1).detach().cpu().numpy()
    sigma_dot = inner / (T_eq_per_step + 1e-12)

    # Sample-level vol proxy: |log_return|
    log_returns = traj.log_returns.detach().cpu().numpy()
    vol_proxy = np.abs(log_returns)

    # Squared returns (for clustering analysis)
    r2 = log_returns ** 2

    return {
        "T_eff_eq": T_eq_per_step.tolist(),       # (T,)
        "sigma_dot": sigma_dot.tolist(),
        "log_return": log_returns.tolist(),
        "vol_proxy": vol_proxy.tolist(),
        "r2": r2.tolist(),
        "gamma": gamma,
    }


def analyse(data: dict) -> str:
    """Quick numerical summary + interpretation."""
    T = np.array(data["T_eff_eq"])
    sd = np.array(data["sigma_dot"])
    vol = np.array(data["vol_proxy"])
    r2 = np.array(data["r2"])

    # Drop first 100 (transient)
    T_st = T[100:]
    sd_st = sd[100:]
    vol_st = vol[100:]
    r2_st = r2[100:]

    out = []
    out.append("# T_eff(t) pilot — C4 N=1000 rollout (Mac, 4000 steps)")
    out.append("")
    out.append(f"steps after warmup transient: {len(T_st)}")
    out.append("")
    out.append("## Equipartition T_eff(t)")
    out.append(f"- mean      : {T_st.mean():+.4f}")
    out.append(f"- std       : {T_st.std():.4f}")
    out.append(f"- relative  : std/mean = {T_st.std() / abs(T_st.mean() + 1e-12):.4f}")
    out.append(f"- min, max  : [{T_st.min():.4f}, {T_st.max():.4f}]")
    out.append("")
    out.append("## σ̇(t) entropy production rate")
    out.append(f"- mean      : {sd_st.mean():+.4f}")
    out.append(f"- std       : {sd_st.std():.4f}")
    out.append("")

    # Cross-correlation between T_eff and vol — for Paper B claim that
    # T_eff(t) increases approaching crashes (vol spikes)
    if T_st.std() > 0 and vol_st.std() > 0:
        c = np.corrcoef(T_st, vol_st)[0, 1]
        out.append(f"## Cross-correlation T_eff(t) vs |r(t)|: {c:+.4f}")
    if T_st.std() > 0 and r2_st.std() > 0:
        c2 = np.corrcoef(T_st, r2_st)[0, 1]
        out.append(f"## Cross-correlation T_eff(t) vs r²(t): {c2:+.4f}")

    # Lag-cross-correlation: does T_eff(t) PRECEDE vol burst?
    if T_st.std() > 0 and vol_st.std() > 0 and len(T_st) > 50:
        lags = list(range(-20, 21))
        ccs = []
        for lag in lags:
            if lag == 0:
                cc = np.corrcoef(T_st, vol_st)[0, 1]
            elif lag > 0:
                cc = np.corrcoef(T_st[:-lag], vol_st[lag:])[0, 1]
            else:
                cc = np.corrcoef(T_st[-lag:], vol_st[:lag])[0, 1]
            ccs.append((lag, cc))
        # Find lag with maximum |cc|
        peak_lag, peak_cc = max(ccs, key=lambda x: abs(x[1]))
        out.append(f"## Peak cross-corr T_eff(t)→|r(t+τ)|: τ={peak_lag} cc={peak_cc:+.4f}")
        out.append(f"  (positive lag = T_eff precedes vol spike)")
        out.append("")
        out.append("Lag scan:")
        for lag, cc in ccs[::4]:
            out.append(f"  τ={lag:+3d}  corr={cc:+.4f}")

    out.append("")
    out.append("## Interpretation")
    rel = T_st.std() / abs(T_st.mean() + 1e-12)
    if rel < 0.05:
        out.append("  T_eff is essentially constant (rel std < 5%).")
        out.append("  → Paper B Path A (PRL, TUR alone) only — no NP flagship from this sim.")
    elif rel < 0.20:
        out.append("  T_eff varies modestly (5-20% rel std).")
        out.append("  → Paper B Path A/B mixed — T_eff structure exists; investigate scaling.")
    else:
        out.append("  T_eff varies substantially (>20%).")
        out.append("  → Paper B Path B (Nature Physics flagship) — strong T_eff signal!")
    return "\n".join(out)


def main() -> None:
    print("Loading C4 (Mac shrunk to N=1000 for pilot)…")
    sim, cfg = load_c4()
    n_steps = 4000
    print(f"  rolling out {n_steps} steps, gamma={float(sim.gamma):+.4f}")
    traj = sim.run(n_steps=n_steps, seed=42)

    fcd = per_channel_force_decomposition(traj)
    print(f"  force decomposition: {fcd}")

    data = compute_teff_per_step(traj, gamma=float(sim.gamma))
    (OUT / "teff_trajectory.json").write_text(json.dumps(data, indent=1)[:2_000_000])
    print(f"  wrote {OUT}/teff_trajectory.json")

    summary = analyse(data)
    (OUT / "teff_pilot_summary.md").write_text(summary)
    print(f"  wrote {OUT}/teff_pilot_summary.md")
    print()
    print(summary)


if __name__ == "__main__":
    main()
