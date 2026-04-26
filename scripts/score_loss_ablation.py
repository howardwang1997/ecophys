#!/usr/bin/env python3
"""Score loss-redesign ablation runs.

Reads experiments/027_loss_redesign/results_phase{1,2,4,5}/<run>/inference_merged.json,
applies the canonical 11-fact bands from score_paper_a_solidify.py, and writes
``experiments/027_loss_redesign/scoreboard.md``.

Outputs:
- Phase 1: per-axis comparison tables (loss_family, tail_estimator, etc.)
  showing mean / std n_pass per variant across 3 seeds.
- Phase 2: multi-seed CI per (winner × arch) cell — 5 seeds with bootstrap.
- Phase 4: scale validation — does N=20K / N=50K reduce CI?
- Phase 5: universality — multi-asset cells with 3 seeds.

Run on Mac:
    conda run -n ecophys python scripts/score_loss_ablation.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
EXP_DIR = REPO / "experiments/027_loss_redesign"

# Canonical 11-fact bands (must match score_paper_a_solidify.py)
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
    agg = d.get("aggregated", {})
    n_pass = 0
    n_total = 0
    rows = {}
    for k, (lo, hi) in BANDS.items():
        if k not in agg:
            continue
        n_total += 1
        v = agg[k]["mean"]
        passed = lo <= v <= hi
        if passed:
            n_pass += 1
        rows[k] = (v, passed)
    return {"n_pass": n_pass, "n_total": n_total, "rows": rows,
            "n_realiz": d.get("n_total_rollouts", 0)}


def bootstrap_ci(values: list[int], n_boot: int = 10_000) -> tuple[float, float, float]:
    if not values:
        return float("nan"), float("nan"), float("nan")
    arr = np.array(values, dtype=float)
    rng = np.random.default_rng(seed=0)
    boots = rng.choice(arr, size=(n_boot, len(arr)), replace=True).mean(axis=1)
    return float(arr.mean()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def welch_t(a: list[int], b: list[int]) -> tuple[float, float]:
    if len(a) < 2 or len(b) < 2:
        return float("nan"), float("nan")
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    mean_a, mean_b = a.mean(), b.mean()
    var_a, var_b = a.var(ddof=1), b.var(ddof=1)
    se = np.sqrt(var_a / len(a) + var_b / len(b))
    if se == 0:
        return float("inf") if mean_a != mean_b else 0.0, 0.0
    t = (mean_a - mean_b) / se
    df_num = (var_a / len(a) + var_b / len(b)) ** 2
    df_den = (var_a / len(a)) ** 2 / (len(a) - 1) + (var_b / len(b)) ** 2 / (len(b) - 1)
    df = df_num / df_den if df_den > 0 else 1.0
    try:
        from scipy import stats
        p = float(2 * (1 - stats.t.cdf(abs(t), df=df)))
    except ImportError:
        from math import erf, sqrt
        p = float(2 * (1 - 0.5 * (1 + erf(abs(t) / sqrt(2)))))
    return float(t), p


def collect_phase(phase: int) -> list[tuple[str, dict | None]]:
    results = []
    base = EXP_DIR / f"results_phase{phase}"
    if not base.exists():
        return results
    for d in sorted(base.iterdir()):
        if not d.is_dir():
            continue
        p = d / "inference_merged.json"
        results.append((d.name, score_one(p)))
    return results


def parse_p1_axis(label: str) -> tuple[str | None, str | None]:
    """Extract (axis, variant) from a Phase 1 label like
    ``p1_lf_w2_only_seed0`` → (``lf``, ``w2_only``)."""
    parts = label.split("_")
    if len(parts) < 4 or parts[0] != "p1":
        return None, None
    axis = parts[1]
    # Trim seed suffix
    if parts[-1].startswith("seed"):
        variant = "_".join(parts[2:-1])
    else:
        variant = "_".join(parts[2:])
    return axis, variant


def main() -> None:
    lines = ["# Loss Redesign Ablation — Scoreboard", ""]

    # ─── Phase 1: per-axis comparison ────────────────────────────────
    p1 = collect_phase(1)
    if p1:
        lines.append(f"## Phase 1 — Single-axis sweeps ({len(p1)} runs)")
        lines.append("")
        # Group by axis, then variant → list of n_pass across seeds
        axis_groups: dict[str, dict[str, list[int]]] = {}
        for label, s in p1:
            if s is None:
                continue
            axis, variant = parse_p1_axis(label)
            if not axis or not variant:
                continue
            axis_groups.setdefault(axis, {}).setdefault(variant, []).append(s["n_pass"])

        AXIS_NAMES = {
            "lf": "loss_family",
            "te": "tail_estimator",
            "dm": "distance_mode",
            "ch": "chunk × BPTT",
            "bal": "balance_mode",
        }
        for axis_id, groups in axis_groups.items():
            lines.append(f"### Axis {axis_id} — {AXIS_NAMES.get(axis_id, axis_id)}")
            lines.append("")
            lines.append("| variant | n_seeds | mean n/11 | 95% CI |")
            lines.append("|---|---:|---:|---|")
            for variant, scores in sorted(groups.items()):
                m, lo, hi = bootstrap_ci(scores)
                lines.append(f"| `{variant}` | {len(scores)} | **{m:.2f}** | [{lo:.2f}, {hi:.2f}] |")
            lines.append("")

        # Top 5 individual runs
        lines.append("### Top 5 individual Phase 1 runs")
        lines.append("")
        ranked = sorted([(lbl, s) for lbl, s in p1 if s is not None],
                        key=lambda x: -x[1]["n_pass"])[:5]
        lines.append("| run | n/11 |")
        lines.append("|---|---:|")
        for lbl, s in ranked:
            lines.append(f"| `{lbl}` | **{s['n_pass']}/11** |")
        lines.append("")

    # ─── Phase 2: top winners × arch × multi-seed CI ─────────────────
    p2 = collect_phase(2)
    if p2:
        lines.append(f"## Phase 2 — Multi-seed CI on winners ({len(p2)} runs)")
        lines.append("")
        # Parse label like p2_w1_c4_seed0 → (winner, arch)
        cells: dict[tuple[str, str], list[int]] = {}
        for label, s in p2:
            if s is None:
                continue
            parts = label.split("_")
            if len(parts) >= 4 and parts[0] == "p2":
                winner, arch = parts[1], parts[2]
                cells.setdefault((winner, arch), []).append(s["n_pass"])
        lines.append("| winner | arch | n_seeds | mean n/11 | 95% CI |")
        lines.append("|---|---|---:|---:|---|")
        for (winner, arch), scores in sorted(cells.items()):
            m, lo, hi = bootstrap_ci(scores)
            lines.append(f"| `{winner}` | `{arch}` | {len(scores)} | "
                         f"**{m:.2f}** | [{lo:.2f}, {hi:.2f}] |")
        lines.append("")

        # Welch t: w1-c4 vs w2-c4 (or compare to baseline GARCH point estimate ~6/11)
        # left as exercise for whoever reads this scoreboard

    # ─── Phase 4: scale validation ───────────────────────────────────
    p4 = collect_phase(4)
    if p4:
        lines.append(f"## Phase 4 — N-scale validation ({len(p4)} runs)")
        lines.append("")
        scale_groups: dict[str, list[int]] = {}
        for label, s in p4:
            if s is None:
                continue
            # p4_n20k_seed0 / p4_n50k_seed0
            parts = label.split("_")
            if len(parts) >= 3:
                scale_groups.setdefault(parts[1], []).append(s["n_pass"])
        lines.append("| N | n_seeds | mean n/11 | 95% CI |")
        lines.append("|---|---:|---:|---|")
        for n, scores in sorted(scale_groups.items()):
            m, lo, hi = bootstrap_ci(scores)
            lines.append(f"| `{n}` | {len(scores)} | **{m:.2f}** | [{lo:.2f}, {hi:.2f}] |")
        lines.append("")

    # ─── Phase 5: universality ───────────────────────────────────────
    p5 = collect_phase(5)
    if p5:
        lines.append(f"## Phase 5 — Universality re-check ({len(p5)} runs)")
        lines.append("")
        cells5: dict[str, list[int]] = {}
        for label, s in p5:
            if s is None:
                continue
            parts = label.split("_")
            if len(parts) >= 3:
                cells5.setdefault(parts[1], []).append(s["n_pass"])
        lines.append("| asset_set | n_seeds | mean n/11 | 95% CI |")
        lines.append("|---|---:|---:|---|")
        for k, scores in sorted(cells5.items()):
            m, lo, hi = bootstrap_ci(scores)
            lines.append(f"| `{k}` | {len(scores)} | **{m:.2f}** | [{lo:.2f}, {hi:.2f}] |")
        lines.append("")

    # ─── Baseline references for context ─────────────────────────────
    lines.append("## Baseline references (for §5 paper table)")
    lines.append("")
    lines.append("- GARCH(1,1)-t fitted (per-asset, deterministic): see "
                 "`experiments/002_garch_baseline/results/three_way_comparison.md`. "
                 "Approximately **5-7/11** under strict bands.")
    lines.append("- LM99 ABM (asset-agnostic): **5/11** under strict bands.")
    lines.append("- Shi 2024 Neural Hawkes: TODO if Phase C implementation lands.")
    lines.append("")

    out = EXP_DIR / "scoreboard.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out}")
    if p1:
        print(f"  Phase 1: {len(p1)} runs across {len(axis_groups)} axes")
    if p2:
        print(f"  Phase 2: {len(p2)} runs")
    if p4:
        print(f"  Phase 4: {len(p4)} runs")
    if p5:
        print(f"  Phase 5: {len(p5)} runs")


if __name__ == "__main__":
    main()
