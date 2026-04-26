#!/usr/bin/env python3
"""Phase 0 — Loss diagnostic profiler.

For the l2a winner checkpoint (8/11 winner from paper-a-solidify), measure:

1. **Rollout-length × estimator-variance scan**: each fact's
   sample-stderr as a function of how many returns we feed it. Identifies
   the minimum rollout length to get each fact stable to <10% relative
   error.
2. **Per-loss-term value + gradient variance**: for each candidate loss
   component (legacy + new), compute K=20 independent estimates;
   characterise mean / std / rel_noise. Identifies dominant noise source.
3. **Cross-correlation matrix**: which loss terms move together vs in
   conflict during training (diagnostic for Pareto issues).

Output: `experiments/026_loss_diagnostic/report.md`.

Usage on Mac:
    conda run -n ecophys python experiments/026_loss_diagnostic/profile.py

Runtime: ~15-30 min (K=20 rollouts × 5 lengths + per-component grad backward).
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch

# Add repo root to path
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.training.losses import (
    LossWeights, MomentTargets,
    acf_sq_mean, leverage_effect_sum, soft_hill_tail_index,
    autocorr_returns_lag1, zumbach_asymmetry_diff,
    quantile_tail_alpha, kurtosis_proxy,
    wasserstein1d, wasserstein_multi_scale,
    mmd_gaussian_multi_bandwidth,
)

CKPT_PATH = REPO / "experiments/025_paper_a_solidify/results_l2a_c4_seed0/checkpoint.pt"
OUT_DIR = REPO / "experiments/026_loss_diagnostic"
OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = OUT_DIR / "report.md"


def load_l2a_simulator() -> tuple[EcoMDSimulator, MomentTargets]:
    """Load the l2a checkpoint into a fresh simulator."""
    if not CKPT_PATH.exists():
        raise SystemExit(f"checkpoint not found: {CKPT_PATH}")
    ckpt = torch.load(CKPT_PATH, map_location="cpu", weights_only=False)
    sim_cfg_dict = ckpt.get("sim_config") or {}
    if not sim_cfg_dict:
        # Fall back to inferring from the YAML
        import yaml
        cfg_yaml = REPO / "experiments/025_paper_a_solidify/config_l2a_c4_seed0.yaml"
        cfg_full = yaml.safe_load(cfg_yaml.read_text())
        sim_cfg_dict = cfg_full["simulator"]
    # Drop bptt_checkpoint_every (not in older configs)
    sim_cfg_dict.setdefault("bptt_checkpoint_every", 0)
    sim_cfg = EcoMDConfig(**sim_cfg_dict)
    sim = EcoMDSimulator(sim_cfg)
    sim.load_state_dict(ckpt["sim_state_dict"])
    sim.eval()  # we want forward + manual grads, no train-only state changes

    # Targets: load the multi-asset targets the original used
    targets_obj = ckpt.get("targets")
    if isinstance(targets_obj, list) and len(targets_obj) > 0:
        first = targets_obj[0]
        if isinstance(first, dict) and "targets" in first:
            t = first["targets"]
            targets = MomentTargets(**t)
        else:
            targets = MomentTargets(0.2, -0.5, 3.0)
    elif isinstance(targets_obj, dict):
        # Maybe single MomentTargets serialised
        targets = MomentTargets(
            acf_sq_mean=float(targets_obj.get("acf_sq_mean", 0.2)),
            leverage_sum=float(targets_obj.get("leverage_sum", -0.5)),
            hill_alpha=float(targets_obj.get("hill_alpha", 3.0)),
        )
    else:
        targets = MomentTargets(0.2, -0.5, 3.0)
    return sim, targets


def load_real_returns_spx() -> torch.Tensor:
    """Load SPX 2015-2026 daily returns as a torch tensor."""
    from ecomd.data.yfinance_ingest import compute_log_returns
    import pyarrow.parquet as pq
    base = REPO / "data/raw/yfinance/interval=1d/symbol=^GSPC"
    if not base.exists():
        # Fall back to whatever is in data/sample
        base = REPO / "data/sample"
    closes = []
    for shard in sorted(base.glob("year=*.parquet")):
        df = pq.read_table(shard).to_pandas()
        if "close" in df.columns:
            closes.extend(df["close"].dropna().tolist())
    closes_np = np.array(closes, dtype=np.float64)
    log_p = np.log(closes_np)
    rets = np.diff(log_p)
    return torch.from_numpy(rets.astype(np.float32))


def generate_rollouts(sim: EcoMDSimulator, n_rollouts: int = 20,
                     n_steps: int = 256, base_seed: int = 1000) -> torch.Tensor:
    """Generate K=n_rollouts independent rollouts of length n_steps.
    Returns a (K, n_steps) tensor of log-returns."""
    rollouts = []
    for k in range(n_rollouts):
        gen = torch.Generator().manual_seed(base_seed + k)
        ig = torch.Generator().manual_seed(base_seed + k * 7)
        s = sim.init_state(generator=ig)
        s_prev = s.detach().clone()
        ps = sim.init_price()
        with torch.no_grad():
            _, _, traj, _ = sim.rollout_chunk(
                s, s_prev, ps,
                n_steps=n_steps, generator=gen,
                create_graph=False,
            )
        rollouts.append(traj.log_returns.cpu().detach())
    return torch.stack(rollouts)  # (K, T)


# ─── 1. Rollout-length × estimator-variance scan ──────────────────────


def scan_rollout_lengths(sim: EcoMDSimulator, real_rets: torch.Tensor,
                          lengths=(16, 32, 64, 128, 256), n_rollouts: int = 20):
    """For each length, compute each fact on K rollouts; report std/mean."""
    print("[1/3] Rollout-length × estimator-variance scan...")
    # Run the longest required rollout once; subset for shorter lengths.
    big = generate_rollouts(sim, n_rollouts=n_rollouts, n_steps=max(lengths))
    print(f"  generated K={n_rollouts} rollouts of length {max(lengths)}")

    facts = {
        "hill (soft, k_frac=0.05)": lambda r: soft_hill_tail_index(r, k_frac=0.05).item(),
        "quantile_tail_alpha (q=0.90)": lambda r: quantile_tail_alpha(r, q_low=0.90).item(),
        "kurtosis_proxy": lambda r: kurtosis_proxy(r).item(),
        "acf_sq_mean (max_lag=8)": lambda r: acf_sq_mean(r, max_lag=8).item(),
        "leverage_sum (max_lag=8)": lambda r: leverage_effect_sum(r, max_lag=8).item(),
        "autocorr_r_lag1": lambda r: autocorr_returns_lag1(r).item(),
        "zumbach (cw=30)": lambda r: zumbach_asymmetry_diff(
            r, coarse_window=30, max_lag=8, avg_lags=8).item(),
        "W1 vs real (scale=1)": lambda r: wasserstein1d(r, real_rets).item(),
        "W1 vs real (scale=5)": lambda r: wasserstein1d(
            r[:(r.shape[0] // 5) * 5].view(-1, 5).sum(dim=1), real_rets).item(),
        "MMD vs real": lambda r: mmd_gaussian_multi_bandwidth(r, real_rets).item(),
    }

    rows = {}
    for L in lengths:
        for fname, fn in facts.items():
            try:
                vals = [fn(big[k, :L]) for k in range(n_rollouts)]
            except Exception as e:
                vals = [float("nan")] * n_rollouts
                print(f"  WARN: fact={fname!r} L={L}: {e}")
            arr = np.array(vals, dtype=float)
            arr = arr[np.isfinite(arr)]
            if len(arr) == 0:
                rows[(fname, L)] = (float("nan"), float("nan"), float("nan"))
                continue
            mean = float(arr.mean())
            std = float(arr.std(ddof=1)) if len(arr) > 1 else 0.0
            rel_noise = std / max(abs(mean), 1e-10)
            rows[(fname, L)] = (mean, std, rel_noise)
        print(f"  L={L}: ✓")
    return rows


# ─── 2. Per-component loss/grad variance ──────────────────────────────


def per_component_grad_profile(sim: EcoMDSimulator, real_rets: torch.Tensor,
                                targets: MomentTargets, n_rollouts: int = 20,
                                n_steps: int = 64):
    """For each loss component, compute K=20 independent (loss_value,
    grad_norm) and report variance."""
    print("[2/3] Per-component loss + grad variance profile...")
    components = {
        "L1(acf_sq)": ("acf_sq_mean", lambda r: (acf_sq_mean(r, max_lag=8) - targets.acf_sq_mean).abs()),
        "MSE(acf_sq)": ("acf_sq_mean", lambda r: (acf_sq_mean(r, max_lag=8) - targets.acf_sq_mean) ** 2),
        "L1(leverage)": ("leverage_sum", lambda r: (leverage_effect_sum(r, max_lag=8) - targets.leverage_sum).abs()),
        "MSE(leverage)": ("leverage_sum", lambda r: (leverage_effect_sum(r, max_lag=8) - targets.leverage_sum) ** 2),
        "L1(soft_hill)": ("hill", lambda r: (soft_hill_tail_index(r, k_frac=0.05) - targets.hill_alpha).abs()),
        "MSE(soft_hill)": ("hill", lambda r: (soft_hill_tail_index(r, k_frac=0.05) - targets.hill_alpha) ** 2),
        "MSE(quantile_tail)": ("hill", lambda r: (quantile_tail_alpha(r) - targets.hill_alpha) ** 2),
        "MSE(kurtosis)": ("hill", lambda r: (kurtosis_proxy(r) - 5.0) ** 2),
        "L1(autocorr_r)": ("autocorr_r", lambda r: autocorr_returns_lag1(r).abs()),
        "W2 multi-scale (vs real)": ("dist", lambda r: wasserstein_multi_scale(r, real_rets, scales=(1, 5, 20))),
        "MMD multi-bw (vs real)": ("dist", lambda r: mmd_gaussian_multi_bandwidth(r, real_rets)),
    }

    rows = {}
    for cname, (fact, fn) in components.items():
        loss_vals = []
        grad_norms = []
        for k in range(n_rollouts):
            sim.zero_grad(set_to_none=True)
            gen = torch.Generator().manual_seed(2000 + k)
            ig = torch.Generator().manual_seed(3000 + k)
            s = sim.init_state(generator=ig)
            s_prev = s.detach().clone()
            ps = sim.init_price()
            _, _, traj, _ = sim.rollout_chunk(
                s, s_prev, ps,
                n_steps=n_steps, generator=gen,
                create_graph=True,
            )
            sim_returns = traj.log_returns
            loss = fn(sim_returns)
            loss_vals.append(float(loss.detach().item()))
            try:
                loss.backward()
                gn_sq = 0.0
                for p in sim.parameters():
                    if p.grad is not None:
                        gn_sq += float(p.grad.detach().pow(2).sum())
                grad_norms.append(np.sqrt(gn_sq))
            except RuntimeError as e:
                grad_norms.append(float("nan"))
                print(f"  WARN backward failed for {cname}: {e}")
        loss_arr = np.array(loss_vals)
        gn_arr = np.array(grad_norms)
        rows[cname] = {
            "loss_mean": float(loss_arr.mean()),
            "loss_std": float(loss_arr.std(ddof=1)) if len(loss_arr) > 1 else 0.0,
            "loss_rel_noise": float(loss_arr.std(ddof=1) / max(abs(loss_arr.mean()), 1e-10))
                              if len(loss_arr) > 1 else 0.0,
            "grad_mean": float(np.nanmean(gn_arr)),
            "grad_std": float(np.nanstd(gn_arr, ddof=1)) if len(gn_arr) > 1 else 0.0,
        }
        print(f"  {cname:<28} loss={rows[cname]['loss_mean']:.3e} "
              f"loss_rel_noise={rows[cname]['loss_rel_noise']*100:.0f}% "
              f"grad_norm={rows[cname]['grad_mean']:.2e}")
    return rows


# ─── 3. Cross-correlation between loss terms ──────────────────────────


def cross_correlation(sim: EcoMDSimulator, real_rets: torch.Tensor,
                       targets: MomentTargets, n_rollouts: int = 30,
                       n_steps: int = 64) -> dict:
    """Compute per-rollout values of all loss terms; report Pearson
    correlation matrix between them."""
    print("[3/3] Cross-correlation between loss terms...")
    components = {
        "acf_sq": lambda r: (acf_sq_mean(r, max_lag=8) - targets.acf_sq_mean).abs().item(),
        "leverage": lambda r: (leverage_effect_sum(r, max_lag=8) - targets.leverage_sum).abs().item(),
        "soft_hill": lambda r: (soft_hill_tail_index(r, k_frac=0.05) - targets.hill_alpha).abs().item(),
        "quantile_tail": lambda r: (quantile_tail_alpha(r) - targets.hill_alpha).abs().item(),
        "kurtosis": lambda r: (kurtosis_proxy(r) - 5.0).abs().item(),
        "autocorr_r": lambda r: autocorr_returns_lag1(r).abs().item(),
        "W1": lambda r: wasserstein1d(r, real_rets).item(),
    }
    K = list(components.keys())
    matrix = np.zeros((len(K), n_rollouts), dtype=float)
    for k in range(n_rollouts):
        gen = torch.Generator().manual_seed(4000 + k)
        ig = torch.Generator().manual_seed(5000 + k)
        s = sim.init_state(generator=ig)
        sp = s.detach().clone()
        ps = sim.init_price()
        with torch.no_grad():
            _, _, traj, _ = sim.rollout_chunk(s, sp, ps, n_steps=n_steps,
                                              generator=gen, create_graph=False)
        for i, name in enumerate(K):
            try:
                matrix[i, k] = components[name](traj.log_returns)
            except Exception:
                matrix[i, k] = float("nan")
    # Pearson correlation
    corr = np.corrcoef(matrix)
    return {"keys": K, "corr": corr}


def write_report(scan_rows, comp_rows, corr_data) -> None:
    print(f"Writing report to {REPORT_PATH}")
    lines = ["# Phase 0 — Loss Diagnostic Profiler", "",
             "Run on the l2a (8/11 winner) checkpoint from paper-a-solidify.",
             ""]

    # Scan section
    lines.append("## 1. Rollout-length × estimator variance")
    lines.append("")
    lines.append("Relative noise = std / |mean| over K=20 independent rollouts.")
    lines.append("")
    facts = sorted({k[0] for k in scan_rows})
    lengths = sorted({k[1] for k in scan_rows})
    header = "| fact | " + " | ".join(f"L={L} (rel%)" for L in lengths) + " |"
    lines.append(header)
    lines.append("|---" + "|---:" * len(lengths) + "|")
    for fact in facts:
        cells = []
        for L in lengths:
            mean, std, rel = scan_rows.get((fact, L), (float("nan"),) * 3)
            cells.append(f"{rel*100:.0f}%" if np.isfinite(rel) else "—")
        lines.append(f"| {fact} | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("**Key**: facts with rel_noise > 30% are unreliable as training "
                 "targets. Anything chunk_steps × warmup_steps gives sim_returns "
                 "shorter than the column where rel<10% is *not* a usable signal.")
    lines.append("")

    # Component section
    lines.append("## 2. Per-component loss + grad variance (K=20, length=64)")
    lines.append("")
    lines.append("| component | loss mean | loss rel_noise | grad mean | grad std |")
    lines.append("|---|---:|---:|---:|---:|")
    # Sort by descending rel_noise
    items = sorted(comp_rows.items(), key=lambda x: -x[1]["loss_rel_noise"])
    for name, row in items:
        lines.append(
            f"| {name} | {row['loss_mean']:.3e} | "
            f"{row['loss_rel_noise']*100:.0f}% | "
            f"{row['grad_mean']:.2e} | {row['grad_std']:.2e} |"
        )
    lines.append("")
    # Top suspects
    lines.append("**Top 3 most-noisy components** (likely main optimisation noise sources):")
    for name, row in items[:3]:
        lines.append(f"- `{name}`: rel_noise = {row['loss_rel_noise']*100:.0f}%, "
                     f"grad_std = {row['grad_std']:.2e}")
    lines.append("")

    # Cross-correlation section
    lines.append("## 3. Cross-correlation between loss terms")
    lines.append("")
    lines.append("Pearson correlation across 30 independent rollouts.")
    lines.append("")
    K = corr_data["keys"]
    corr = corr_data["corr"]
    lines.append("| | " + " | ".join(K) + " |")
    lines.append("|---" + "|---:" * len(K) + "|")
    for i, name in enumerate(K):
        cells = [f"{corr[i, j]:+.2f}" for j in range(len(K))]
        lines.append(f"| **{name}** | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("**Strong negative correlations** (|ρ| > 0.5) indicate "
                 "loss terms in Pareto conflict — optimising one degrades the "
                 "other.")
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines) + "\n")


def main() -> None:
    print(f"Phase 0 diagnostic — output → {REPORT_PATH}")
    print(f"Loading l2a checkpoint from {CKPT_PATH}")
    sim, targets = load_l2a_simulator()
    print(f"Sim built: N={sim.cfg.n_agents}, d_state={sim.cfg.d_state}")
    print(f"Targets: {asdict(targets)}")

    real_rets = load_real_returns_spx()
    print(f"Real SPX returns: shape={real_rets.shape}, "
          f"mean={real_rets.mean():.4f}, std={real_rets.std():.4f}")
    print()

    # 1. Rollout-length scan
    scan_rows = scan_rollout_lengths(sim, real_rets,
                                     lengths=(16, 32, 64, 128, 256),
                                     n_rollouts=20)
    print()

    # 2. Per-component grad variance
    comp_rows = per_component_grad_profile(sim, real_rets, targets,
                                            n_rollouts=20, n_steps=64)
    print()

    # 3. Cross-correlation
    corr = cross_correlation(sim, real_rets, targets, n_rollouts=30, n_steps=64)
    print()

    write_report(scan_rows, comp_rows, corr)
    print(f"\n✓ Phase 0 done — see {REPORT_PATH}")


if __name__ == "__main__":
    main()
