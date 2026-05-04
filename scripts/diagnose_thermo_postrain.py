"""E2: Extract post-training T_eff and gamma_eff from each EcoMD checkpoint.

For experiments/064_winner_50seed_repro (50 seeds × p_4_2__2_1, init T=0.05, gamma=1.0,
both learnable), determine whether the model cheated by suppressing noise. Output:
  - per-seed CSV (seed, T_eff, gamma_eff, noise_scale_per_step, drift_per_step_estimate)
  - markdown summary with distribution stats

Per-step noise std = sqrt(2 * T * dt / gamma)
Init: sqrt(2 * 0.05 * 0.01 / 1.0) = 0.0316

Run:
  conda run -n ecophys python scripts/diagnose_thermo_postrain.py
"""

from __future__ import annotations

import csv
import json
import math
import re
import statistics
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "experiments" / "064_winner_50seed_repro"
OUT = REPO / "experiments" / "067_ar1_diagnostics"
OUT.mkdir(exist_ok=True)

DT = 0.01
T_INIT = 0.05
GAMMA_INIT = 1.0


def load_score(d: Path) -> int | None:
    p = d / "inference_merged.json"
    if not p.exists():
        return None
    BANDS = {
        "autocorr_returns": (-0.1, 0.20),
        "hill_tail_index": (2.0, 4.0),
        "gain_loss_asymmetry": (-30.0, -3.0),
        "aggregational_gaussianity": (10, 200),
        "intermittency_fano": (5, 100),
        "acf_squared_returns": (0.15, 0.55),
        "conditional_kurtosis": (-1.0, 3.0),
        "dfa_hurst_abs_r": (0.6, 0.9),
        "leverage_effect": (-6.0, -0.5),
        "volume_volatility_corr": (0.3, 0.8),
        "zumbach_asymmetry": (0.001, 0.5),
    }
    agg = json.loads(p.read_text()).get("aggregated", {})
    return sum(1 for k, (lo, hi) in BANDS.items() if k in agg and lo <= agg[k]["mean"] <= hi)


def main() -> None:
    rows = []
    dirs = sorted(SRC.glob("results_p_4_2__2_1_seed*"))
    for d in dirs:
        m = re.search(r"seed(\d+)$", d.name)
        if not m:
            continue
        seed = int(m.group(1))
        ckpt_path = d / "checkpoint.pt"
        if not ckpt_path.exists():
            continue
        try:
            ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        except Exception as e:
            print(f"skip {d.name}: {e}")
            continue
        sd = ck["sim_state_dict"]
        log_T = sd.get("log_temperature")
        log_gamma = sd.get("log_gamma")
        if log_T is None or log_gamma is None:
            print(f"skip {d.name}: missing log_T/log_gamma")
            continue
        T_eff = math.exp(float(log_T.flatten()[0]))
        gamma_eff = math.exp(float(log_gamma.flatten()[0]))
        noise = math.sqrt(2 * T_eff * DT / gamma_eff)
        score = load_score(d)
        rows.append(dict(
            seed=seed,
            score=score,
            T_eff=T_eff,
            gamma_eff=gamma_eff,
            noise_per_step=noise,
            T_ratio=T_eff / T_INIT,
            gamma_ratio=gamma_eff / GAMMA_INIT,
            iter_idx=ck.get("iter_idx", -1),
        ))

    rows.sort(key=lambda r: r["seed"])

    # CSV
    csv_path = OUT / "thermo_params.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Markdown summary
    Ts = [r["T_eff"] for r in rows]
    Gs = [r["gamma_eff"] for r in rows]
    Ns = [r["noise_per_step"] for r in rows]
    init_noise = math.sqrt(2 * T_INIT * DT / GAMMA_INIT)

    def stats(xs):
        return f"mean={statistics.mean(xs):.4f}  median={statistics.median(xs):.4f}  min={min(xs):.4f}  max={max(xs):.4f}  sd={statistics.stdev(xs):.4f}"

    md = []
    md.append("# E2 — Post-training thermodynamic parameters (064 winner_50seed_repro)\n")
    md.append("## Hypothesis to test")
    md.append("Did the model 'cheat' by driving T → 0 to suppress stochasticity?")
    md.append(f"Init values: T={T_INIT}, γ={GAMMA_INIT}, dt={DT}")
    md.append(f"Init per-step noise std σ_init = sqrt(2·T·dt/γ) = **{init_noise:.4f}**\n")
    md.append("## Distribution across 50 seeds\n")
    md.append("| param | stats |")
    md.append("|---|---|")
    md.append(f"| T_eff | {stats(Ts)} |")
    md.append(f"| gamma_eff | {stats(Gs)} |")
    md.append(f"| noise_per_step | {stats(Ns)} |")
    md.append(f"| T_eff / T_init | {stats([r['T_ratio'] for r in rows])} |")
    md.append(f"| gamma_eff / gamma_init | {stats([r['gamma_ratio'] for r in rows])} |")

    n_low_T = sum(1 for t in Ts if t < 0.5 * T_INIT)
    n_high_G = sum(1 for g in Gs if g > 2 * GAMMA_INIT)
    n_low_noise = sum(1 for n in Ns if n < 0.5 * init_noise)
    md.append(f"\n**T_eff < 0.5·T_init**: {n_low_T}/50 seeds (cheat indicator)")
    md.append(f"**γ_eff > 2·γ_init**: {n_high_G}/50 seeds (alt cheat indicator)")
    md.append(f"**noise_per_step < 0.5·σ_init**: {n_low_noise}/50 seeds (composite)\n")

    # Correlate with score
    md.append("## Score vs T_eff / γ_eff (does cheating correlate with high score?)\n")
    md.append("| score | n | mean_T | mean_γ | mean_noise |")
    md.append("|---:|---:|---:|---:|---:|")
    by_score: dict[int, list] = {}
    for r in rows:
        if r["score"] is None:
            continue
        by_score.setdefault(r["score"], []).append(r)
    for s in sorted(by_score):
        lst = by_score[s]
        md.append(f"| {s}/11 | {len(lst)} | {statistics.mean([r['T_eff'] for r in lst]):.4f} | "
                  f"{statistics.mean([r['gamma_eff'] for r in lst]):.4f} | "
                  f"{statistics.mean([r['noise_per_step'] for r in lst]):.4f} |")

    md.append("\n## Per-seed (top 10 by score)\n")
    md.append("| seed | score | T_eff | γ_eff | noise/step | iter |")
    md.append("|---:|---:|---:|---:|---:|---:|")
    for r in sorted(rows, key=lambda x: -(x["score"] or 0))[:10]:
        md.append(f"| {r['seed']} | {r['score']}/11 | {r['T_eff']:.4f} | {r['gamma_eff']:.4f} | "
                  f"{r['noise_per_step']:.4f} | {r['iter_idx']} |")

    md.append("\n## Per-seed (bottom 10 by score)\n")
    md.append("| seed | score | T_eff | γ_eff | noise/step | iter |")
    md.append("|---:|---:|---:|---:|---:|---:|")
    for r in sorted(rows, key=lambda x: (x["score"] or 0))[:10]:
        md.append(f"| {r['seed']} | {r['score']}/11 | {r['T_eff']:.4f} | {r['gamma_eff']:.4f} | "
                  f"{r['noise_per_step']:.4f} | {r['iter_idx']} |")

    md.append("\n## Verdict (auto)\n")
    if n_low_noise > 25:
        md.append(f"**CHEAT CONFIRMED**: ≥half of seeds drove noise to <50% of init. T-suppression hypothesis holds.")
    elif n_low_noise > 5:
        md.append(f"**PARTIAL CHEAT**: {n_low_noise}/50 seeds reduced noise. Cheat is opportunistic, not universal.")
    else:
        md.append(f"**CHEAT REJECTED**: only {n_low_noise}/50 seeds reduced noise meaningfully. "
                  f"The autocorr problem is NOT due to T-suppression — it's structural "
                  f"(force field too smooth across one dt, or per-step relaxation γ·dt={GAMMA_INIT*DT} "
                  f"too small to decorrelate velocity).")

    md_path = OUT / "thermo_params.md"
    md_path.write_text("\n".join(md) + "\n")
    print(f"wrote {csv_path}")
    print(f"wrote {md_path}")
    print()
    print("\n".join(md))


if __name__ == "__main__":
    main()
