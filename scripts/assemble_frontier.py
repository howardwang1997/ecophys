"""Assemble the Paper A 3-paradigm Pareto frontier — the "tails XOR dynamics" ceiling figure.

Reads each paradigm's representative best cell (cached scored JSON, same compute_all pipeline),
scores the 11 Cont facts vs the canonical bands, and shows that each paradigm passes a DIFFERENT
subset (distributional/tail facts XOR temporal/dynamics facts) — none clears the joint ceiling.

SOURCES is the single edit point: as H20 results land (ABIDES daily re-run → results_*_daily/, the
concave solve cross-asset, new champion cells), update the globs and re-run; the figure regenerates.

Emits: a text scoreboard + (best-effort) papers/paper_a_methods/figures/fig_frontier_3paradigm.{pdf,png}.
Read-only on data. Usage: python scripts/assemble_frontier.py
"""
from __future__ import annotations

import glob
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent

BANDS = {
    "hill_tail_index": (2.0, 4.0), "aggregational_gaussianity": (10, 200),
    "gain_loss_asymmetry": (-30.0, -3.0), "conditional_kurtosis": (-1.0, 3.0),
    "intermittency_fano": (5, 100),
    "acf_squared_returns": (0.15, 0.55), "leverage_effect": (-6.0, -0.5),
    "zumbach_asymmetry": (0.001, 0.5), "dfa_hurst_abs_r": (0.6, 0.9),
    "autocorr_returns": (-0.1, 0.20), "volume_volatility_corr": (0.3, 0.8),
}
TAIL = ["hill_tail_index", "aggregational_gaussianity", "gain_loss_asymmetry",
        "conditional_kurtosis", "intermittency_fano"]
DYN = ["acf_squared_returns", "leverage_effect", "zumbach_asymmetry", "dfa_hurst_abs_r",
       "autocorr_returns", "volume_volatility_corr"]

# paradigm -> (label, dir-glob, note). ABIDES prefers the daily re-run if present.
_abides_daily = list((REPO / "experiments/105_abides_ceiling").glob("results_rmsc03_base_daily"))
SOURCES = [
    ("EcoMD", "EcoMD concave√ (spx)", "experiments/113_gabaix_solve/results_concave_d050_seed*", "the solve"),
    ("EcoMD", "EcoMD zumdn (best net)", "experiments/098c_zumdn_fine_grid_n30/results_zumdn_s100_lam092_seed*", "SOTA-net cell"),
    ("Neural", "WGAN-LP (spx)", "experiments/095b_baselines_n30/results_baseline_wgan_spx_seed*", ""),
    ("Neural", "TrajCast (spx)", "experiments/095b_baselines_n30/results_baseline_trajcast_spx_seed*", ""),
    ("Neural", "Diffusion-cond", "experiments/111_diffusion/results_diffusion_cond_seed*", ""),
    ("Agent", "ABIDES rmsc03",
     "experiments/105_abides_ceiling/results_rmsc03_base_daily" if _abides_daily
     else "experiments/105_abides_ceiling/results_rmsc03_base",
     "DAILY (fair)" if _abides_daily else "intraday — DAILY re-run PENDING"),
]


def means(pat: str) -> tuple[dict, int]:
    facts: dict[str, list[float]] = defaultdict(list)
    n = 0
    for d in glob.glob(str(REPO / pat)) if not pat.startswith("/") else glob.glob(pat):
        mj = Path(d) / "inference_merged.json"
        if not mj.exists():
            continue
        n += 1
        agg = json.loads(mj.read_text()).get("aggregated", {})
        for f in BANDS:
            m = agg.get(f, {}).get("mean")
            if isinstance(m, (int, float)) and np.isfinite(m):
                facts[f].append(float(m))
    return {f: float(np.mean(v)) for f, v in facts.items() if v}, n


def ok(f: str, v) -> bool:
    if v is None:
        return False
    lo, hi = BANDS[f]
    return lo <= v <= hi


def main() -> None:
    rows = [(par, lab, *means(pat), note) for par, lab, pat, note in SOURCES]
    facts = TAIL + DYN
    print("# Paper A — 3-paradigm Pareto frontier (tails XOR dynamics)\n")
    print(f"{'paradigm / cell':26}" + "".join(f"{f[:9]:>11}" for f in facts) + f"{'TAIL':>7}{'DYN':>5}{'NET':>5}")
    for par, lab, m, n, note in rows:
        line = f"{lab:26}"
        for f in facts:
            v = m.get(f)
            line += f"{((f'{v:.1f}' if v is not None else 'NA') + ('✓' if ok(f, v) else '·')):>11}"
        t = sum(ok(f, m.get(f)) for f in TAIL); dy = sum(ok(f, m.get(f)) for f in DYN)
        line += f"{t:>7}{dy:>5}{t+dy:>5}"
        print(line + (f"   [{note}]" if note else ""))
    print(f"\n  facts: TAIL={TAIL}\n         DYN ={DYN}")
    print("  n seeds: " + ", ".join(f"{lab}={n}" for _, lab, _, n, _ in rows))
    print("\n# reading: EcoMD passes DYN but overshoots TAIL (hill); neural/diffusion pass TAIL but")
    print("#          lose DYN (acf²/clustering); ABIDES passes few — no paradigm clears the joint.")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        labels = [lab for _, lab, _, _, _ in rows]
        M = np.array([[1.0 if ok(f, m.get(f)) else 0.0 for f in facts] for _, _, m, _, _ in rows])
        fig, ax = plt.subplots(figsize=(11, 0.6 * len(rows) + 2))
        ax.imshow(M, aspect="auto", cmap="Greens", vmin=0, vmax=1)
        ax.set_xticks(range(len(facts))); ax.set_xticklabels(facts, rotation=45, ha="right", fontsize=7)
        ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=8)
        ax.axvline(len(TAIL) - 0.5, color="k", lw=1.5)
        ax.set_title("3-paradigm frontier: TAIL (left) XOR DYNAMICS (right) — none clears the joint", fontsize=9)
        for i in range(len(rows)):
            for j, f in enumerate(facts):
                v = rows[i][2].get(f)
                ax.text(j, i, "✓" if ok(f, v) else "", ha="center", va="center", fontsize=8)
        fig.tight_layout()
        out = REPO / "papers/paper_a_methods/figures/fig_frontier_3paradigm"
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out.with_suffix(".pdf")); fig.savefig(out.with_suffix(".png"), dpi=150)
        print(f"\n  figure → {out.with_suffix('.png').relative_to(REPO)}")
    except Exception as e:
        print(f"\n  [figure skipped: {e}]")


if __name__ == "__main__":
    main()
