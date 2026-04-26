#!/usr/bin/env python
"""Paper A solidify scorer — bootstrap CI + Welch t-test for L series.

Auto-discovers all results_*/inference_merged.json under
experiments/025_paper_a_solidify/, scores 11 stylized facts, writes
scoreboard.md grouped by phase.

Adds (vs score_weekend.py):
- For L series (multi-seed): mean ± 95% bootstrap CI of n/11 across 5 seeds
- Welch t-test between L0 (v0.8) vs L2 (C4) on n/11 — claim significance

Run on Mac after H20 push:
    git pull
    conda run -n ecophys python scripts/score_paper_a_solidify.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
SOLIDIFY_DIR = REPO / "experiments/025_paper_a_solidify"

BANDS = {
    "autocorr_returns":           (-0.1, 0.20),
    "hill_tail_index":            (2.0, 4.0),
    "gain_loss_asymmetry":        (-30.0, -3.0),
    "aggregational_gaussianity":  (10, 200),
    "intermittency_fano":         (5, 100),
    "acf_squared_returns":        (0.15, 0.55),
    "conditional_kurtosis":       (-1.0, 3.0),
    "dfa_hurst_abs_r":            (0.6, 0.9),
    "leverage_effect":            (-6.0, -0.5),
    "volume_volatility_corr":     (0.3, 0.8),
    "zumbach_asymmetry":          (0.001, 0.5),
}


def score_one(p: Path) -> dict | None:
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    agg = d["aggregated"]
    n_pass = 0
    n_total = 0
    rows: dict[str, tuple[float, bool]] = {}
    for k, (lo, hi) in BANDS.items():
        if k not in agg:
            continue
        n_total += 1
        v = agg[k]["mean"]
        passed = lo <= v <= hi
        if passed:
            n_pass += 1
        rows[k] = (v, passed)
    return {
        "n_pass": n_pass, "n_total": n_total, "rows": rows,
        "n_realiz": d.get("n_total_rollouts", 0),
    }


def bootstrap_ci(values: list[int], n_boot: int = 10_000, ci: float = 95) -> tuple[float, float, float]:
    """Bootstrap mean and CI for a list of n_pass scores."""
    if len(values) == 0:
        return float("nan"), float("nan"), float("nan")
    arr = np.array(values, dtype=float)
    rng = np.random.default_rng(seed=0)
    boots = rng.choice(arr, size=(n_boot, len(arr)), replace=True).mean(axis=1)
    lo = np.percentile(boots, (100 - ci) / 2)
    hi = np.percentile(boots, 100 - (100 - ci) / 2)
    return float(arr.mean()), float(lo), float(hi)


def welch_t(a: list[int], b: list[int]) -> tuple[float, float]:
    """Welch's t-test: returns (t, two-sided p) approximated via numpy."""
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    if len(a) < 2 or len(b) < 2:
        return float("nan"), float("nan")
    mean_a, mean_b = a.mean(), b.mean()
    var_a, var_b = a.var(ddof=1), b.var(ddof=1)
    se = np.sqrt(var_a / len(a) + var_b / len(b))
    if se == 0:
        return float("inf") if mean_a != mean_b else 0.0, 0.0
    t = (mean_a - mean_b) / se
    # Welch-Satterthwaite df + normal approximation for p (good enough at n=5)
    df_num = (var_a / len(a) + var_b / len(b)) ** 2
    df_den = (var_a / len(a)) ** 2 / (len(a) - 1) + (var_b / len(b)) ** 2 / (len(b) - 1)
    df = df_num / df_den if df_den > 0 else 1.0
    # Two-sided p via scipy if available, else normal approx
    try:
        from scipy import stats
        p = float(2 * (1 - stats.t.cdf(abs(t), df=df)))
    except ImportError:
        from math import erf, sqrt
        p = float(2 * (1 - 0.5 * (1 + erf(abs(t) / sqrt(2)))))
    return float(t), p


def main() -> None:
    out_path = SOLIDIFY_DIR / "scoreboard.md"
    results: list[tuple[str, dict | None]] = []
    rds = sorted(SOLIDIFY_DIR.glob("results_*/inference_merged.json"))
    for p in rds:
        label = p.parent.name.replace("results_", "")
        results.append((label, score_one(p)))

    phases: dict[str, list] = {}
    for label, s in results:
        ph = label[0].upper()
        phases.setdefault(ph, []).append((label, s))

    lines = ["# Paper A solidify scoreboard", "",
             f"Discovered {len(results)} runs.", ""]

    # ─── L series — multi-seed CI summary ────────────────────────────
    if "L" in phases:
        lines.append("## L series — multi-seed CI (5 seeds × 3 architectures)")
        lines.append("")
        groups = {"L0_v08": [], "L1_v10hawkes": [], "L2_c4": []}
        for label, s in phases["L"]:
            if s is None:
                continue
            if label.startswith("l0"):
                groups["L0_v08"].append(s["n_pass"])
            elif label.startswith("l1"):
                groups["L1_v10hawkes"].append(s["n_pass"])
            elif label.startswith("l2"):
                groups["L2_c4"].append(s["n_pass"])
        lines.append("| Architecture | n_seeds | mean n/11 | 95% CI |")
        lines.append("|---|---:|---:|---|")
        for arch, scores in groups.items():
            if not scores:
                continue
            m, lo, hi = bootstrap_ci(scores)
            lines.append(f"| {arch} | {len(scores)} | **{m:.2f}** | [{lo:.2f}, {hi:.2f}] |")
        lines.append("")
        # Welch t between L0 and L2 (v0.8 vs C4)
        if groups["L0_v08"] and groups["L2_c4"]:
            t, p = welch_t(groups["L2_c4"], groups["L0_v08"])
            lines.append(f"**Welch t-test L2 (C4) vs L0 (v0.8)**: t={t:+.3f}, p={p:.4f}")
            if p < 0.05:
                lines.append("→ **C4 > v0.8 with statistical significance (p < 0.05)**")
            else:
                lines.append(f"→ Not significant at 5% (p={p:.3f})")
            lines.append("")
        if groups["L1_v10hawkes"] and groups["L2_c4"]:
            t, p = welch_t(groups["L2_c4"], groups["L1_v10hawkes"])
            lines.append(f"**Welch t-test L2 (C4) vs L1 (v1.0 Hawkes)**: t={t:+.3f}, p={p:.4f}")
            if p < 0.05:
                lines.append("→ **C4 > v1.0 with statistical significance (p < 0.05)**")
            else:
                lines.append(f"→ Not significant at 5% (p={p:.3f})")
            lines.append("")

    # ─── Top 10 across all ─────────────────────────────────────────
    overall = sorted(
        [(lbl, s) for lbl, s in results if s is not None],
        key=lambda x: -x[1]["n_pass"],
    )
    lines.append("## Top 10 across all phases")
    lines.append("")
    lines.append("| rank | variant | n/N | n_realiz |")
    lines.append("|---:|---|---:|---:|")
    for i, (lbl, s) in enumerate(overall[:10]):
        lines.append(f"| {i+1} | `{lbl}` | **{s['n_pass']}/{s['n_total']}** | {s['n_realiz']} |")
    lines.append("")

    # ─── Per-phase tables ───────────────────────────────────────────
    for ph in sorted(phases.keys()):
        items = phases[ph]
        lines.append(f"## Phase {ph} ({len(items)} runs)")
        lines.append("")
        lines.append("| variant | n/N | acf(r²) | hill | leverage | zumbach | autocorr_r | vol_corr |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        for lbl, s in sorted(items, key=lambda x: x[0]):
            if s is None:
                lines.append(f"| `{lbl}` | — | (missing) | — | — | — | — | — |")
                continue

            def get(name):
                if name in s["rows"]:
                    return f"{s['rows'][name][0]:+.3f}"
                return "—"

            flag = "★" if s["n_pass"] >= 8 else ("+" if s["n_pass"] >= 6 else "")
            lines.append(
                f"| `{lbl}` | **{s['n_pass']}/{s['n_total']}** {flag}"
                f" | {get('acf_squared_returns')} | {get('hill_tail_index')}"
                f" | {get('leverage_effect')} | {get('zumbach_asymmetry')}"
                f" | {get('autocorr_returns')} | {get('volume_volatility_corr')} |"
            )
        lines.append("")

    out_path.write_text("\n".join(lines))
    print(f"wrote {out_path}")
    print()
    print(f"Total: {len(results)} runs, "
          f"{sum(1 for _, s in results if s and s['n_pass'] >= 8)} ≥ 8/11, "
          f"{sum(1 for _, s in results if s and s['n_pass'] >= 9)} ≥ 9/11, "
          f"{sum(1 for _, s in results if s and s['n_pass'] >= 10)} ≥ 10/11")
    print("Top 5:")
    for lbl, s in overall[:5]:
        print(f"  {lbl:<28} {s['n_pass']}/{s['n_total']}")


if __name__ == "__main__":
    main()
