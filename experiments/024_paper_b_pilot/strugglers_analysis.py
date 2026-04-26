"""C4 three-strugglers deep analysis.

C4 fails on: autocorr_returns +0.272, volume_volatility_corr -0.381,
zumbach_asymmetry -0.067. Let's investigate WHY at the trajectory level.

For each: pull existing inference traces, look at why metric is wrong.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch
import yaml

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator


REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
OUT.mkdir(exist_ok=True, parents=True)


def main() -> None:
    cfg_path = REPO / "experiments/022_h20_batch/config_c4_multi_asset_twopop.yaml"
    ckpt_path = REPO / "experiments/022_h20_batch/results_c4/checkpoint.pt"
    cfg = yaml.safe_load(cfg_path.read_text())
    sim_cfg = dict(cfg["simulator"])
    sim_cfg["n_agents"] = 1000  # Mac
    sim = EcoMDSimulator(EcoMDConfig(**sim_cfg))
    state = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    sim.load_state_dict(state["sim_state_dict"], strict=False)
    sim.eval()

    print("Rolling out C4 N=1000 × 4000 steps…")
    traj = sim.run(n_steps=4000, seed=42)
    r = traj.log_returns_np()[100:]   # drop transient
    vol = traj.volumes_np()[100:]
    s = traj.states[100:].detach().cpu().numpy()  # (T, N, d)
    f_cons = traj.f_cons[100:].detach().cpu().numpy()
    log_p = traj.log_prices.detach().cpu().numpy()[100:]
    n = len(r)
    print(f"  T={n}  return mean={r.mean():+.5f} std={r.std():.5f}")

    findings = []

    # ─── Strugger 1: autocorr_returns +0.27 ─────────────────────────────
    # Real markets ≈ 0. We have positive autocorr.
    findings.append("# C4 stragglers — root cause analysis\n")
    findings.append("## #1 autocorr_returns +0.27 (target ≤ 0.20)\n")

    r_centered = r - r.mean()
    rho_lag1 = (r_centered[:-1] * r_centered[1:]).mean() / (r_centered**2).mean()
    rho_lag2 = (r_centered[:-2] * r_centered[2:]).mean() / (r_centered**2).mean()
    rho_lag5 = (r_centered[:-5] * r_centered[5:]).mean() / (r_centered**2).mean()
    findings.append(f"- ρ(1) = {rho_lag1:+.4f}")
    findings.append(f"- ρ(2) = {rho_lag2:+.4f}")
    findings.append(f"- ρ(5) = {rho_lag5:+.4f}")
    findings.append("")
    if rho_lag1 > 0.05:
        findings.append("**Diagnosis**: positive ρ(1) means returns auto-correlate.")
        findings.append("Common causes: (a) market-maker β too small → price not")
        findings.append("fully responsive to demand → systematic drift; (b) Hawkes")
        findings.append("excitation correlated across consecutive steps via shared")
        findings.append("memory; (c) twopop γ_eff makes some agents lazy → drift.")
    findings.append("")

    # Where does the auto-correlation come from? Decompose:
    # log_ret_t = β·ED_t - 0.5σ² + σ·η_t + κ·mem_t·sign(ret_t)
    # The Hawkes term mem_t·sign(ret_t) IS auto-correlated by construction.
    # If sign(ret_t) is constant → memory accumulates same sign → drift.

    # Sign run analysis
    signs = np.sign(r)
    sign_runs = []
    cur = 1
    cur_sign = signs[0]
    for s_i in signs[1:]:
        if s_i == cur_sign and s_i != 0:
            cur += 1
        else:
            sign_runs.append(cur)
            cur = 1
            cur_sign = s_i
    sign_runs.append(cur)
    findings.append(f"- mean sign-run length = {np.mean(sign_runs):.2f} (random ≈ 2.0)")
    findings.append(f"- max sign-run = {np.max(sign_runs)}")
    findings.append("")
    if np.mean(sign_runs) > 3.0:
        findings.append("**Hypothesis confirmed**: returns sign-cluster (mean run > 3),")
        findings.append("which means Hawkes excitation amplifies same-sign streaks.")
        findings.append("**Fix**: reduce hawkes_kappa OR add anti-streak penalty.")

    # ─── Struggler 2: volume_volatility_corr -0.38 ─────────────────────
    findings.append("\n## #2 volume_volatility_corr -0.38 (target +0.30 to +0.80)\n")
    findings.append("Real markets: high vol days → high volume. We have NEGATIVE.\n")

    # Compute sim's vol-volume corr directly
    # vol = |r|, volume from traj.volumes
    abs_r = np.abs(r)
    # Filter zero-volume steps
    mask = vol > 1e-6
    if mask.sum() > 100:
        c_vv = np.corrcoef(abs_r[mask], vol[mask])[0, 1]
        findings.append(f"- corr(|r|, volume) = {c_vv:+.4f}")
    findings.append(f"- vol range: [{vol.min():.4f}, {vol.max():.4f}]")
    findings.append(f"- vol mean: {vol.mean():.4f}, std: {vol.std():.4f}")
    findings.append("")

    # Volume = Σ |Δpos_i| in the model (s_i[0] is treated as position)
    # If twopop has γ heterogeneity, low-γ agents move less → less volume
    # AND that's correlated with calm periods. So vol clusters with calm,
    # which gives NEGATIVE vol-volume correlation!
    findings.append("**Hypothesis**: with twopop γ-heterogeneity (0.7-1.5), low-γ")
    findings.append("agents (γ=0.5) move LESS → contribute LESS volume. During calm")
    findings.append("periods, low-γ agents dominate → low volume during calm. But")
    findings.append("during bursts (high vol), Hawkes excites the price layer not")
    findings.append("the agent layer; agent positions don't move proportionally.")
    findings.append("")
    findings.append("**Fix candidates**:")
    findings.append("- (a) Connect Hawkes excitation BACK to agent forcing (not just price)")
    findings.append("- (b) Make volume = Σ |Δlog_p|·shares_i instead of Σ|Δpos_i|")
    findings.append("- (c) Drop twopop γ-heterogeneity (use only T-heterogeneity)")

    # ─── Struggler 3: zumbach -0.067 ─────────────────────────────────
    findings.append("\n## #3 zumbach_asymmetry -0.067 (target > 0)\n")
    findings.append("Real markets: past coarse vol predicts future fine vol better")
    findings.append("than the reverse. We have OPPOSITE.\n")

    # Compute D̄ directly to confirm
    coarse_window = 30
    max_lag = 20
    fine = r ** 2
    gap = max_lag + 1
    cw = coarse_window
    t_lo = gap + cw - 1
    t_hi = n - 1 - max_lag
    m_count = t_hi - t_lo + 1
    if m_count > 100:
        csum = np.concatenate([[0.0], np.cumsum(fine)])
        ts = np.arange(t_lo, t_hi + 1)
        coarse = (csum[ts - gap + 1] - csum[ts - gap - cw + 1]) / cw
        D_pos = []
        for k in range(1, 11):
            f_pos = fine[ts + k]
            f_neg = fine[ts - k]
            if coarse.std() > 0:
                a_pos = np.corrcoef(coarse, f_pos)[0, 1]
                a_neg = np.corrcoef(coarse, f_neg)[0, 1]
                D_pos.append(a_pos - a_neg)
        D_mean = np.mean(D_pos)
        findings.append(f"- D̄ over τ=1..10: {D_mean:+.4f}  (real ≈ +0.05)")
        findings.append(f"- D(τ) trajectory: {[f'{d:+.3f}' for d in D_pos]}")
        findings.append("")
    findings.append("**Hypothesis**: Hawkes excitation runs through ONE EMA channel")
    findings.append("with α=0.1 (~10-step time scale). This makes 'past fine vol")
    findings.append("predicts future fine vol' (α-step memory) the dominant correlation")
    findings.append("structure, NOT 'past coarse → future fine'. The architecture")
    findings.append("naturally produces ANTI-Zumbach behavior.")
    findings.append("")
    findings.append("**Fix**: multi-scale Hawkes (already exists as P2!) — add a SLOW")
    findings.append("EMA channel (α=0.005, ~200 step) so past coarse memory exists.")
    findings.append("Weekend B2/F1/F2/F3 configs test this directly.")

    # Final summary
    findings.append("\n## Summary table\n")
    findings.append("| fact | sim | target | root cause | fix |")
    findings.append("|---|---:|---:|---|---|")
    findings.append("| autocorr_returns | +0.27 | ≤0.20 | Hawkes amplifies same-sign streaks | reduce κ OR anti-streak penalty |")
    findings.append("| volume_vol_corr | -0.38 | +0.30..+0.80 | twopop γ heterogeneity decouples Δpos from price burst | connect Hawkes to agent OR redefine volume |")
    findings.append("| zumbach | -0.067 | >0 | single-scale Hawkes EMA → anti-Zumbach | multi-scale Hawkes (α_long=0.005) |")

    txt = "\n".join(findings)
    (OUT / "stragglers_analysis.md").write_text(txt)
    print()
    print(txt)


if __name__ == "__main__":
    main()
