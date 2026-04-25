#!/usr/bin/env python
"""Score the v3 H20 batch — produces a markdown scoreboard.

Reads each results_a{0..5}/inference_merged.json, applies the 10-fact
band scoring used in run #2 analysis, writes
experiments/022_h20_batch/scoreboard.md.

Run on Mac after H20 push:
    git pull
    conda run -n ecophys python scripts/score_v3_batch.py
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Same band definitions as in _h20_run2_analysis.md
BANDS = {
    "autocorr_returns":           (-0.1, 0.20),
    "hill_tail_index":            (2.0, 4.0),
    "gain_loss_asymmetry":        (-30.0, -3.0),
    "aggregational_gaussianity":  (10, 200),
    "intermittency_fano":         (5, 100),
    "acf_squared_returns":        (0.15, 0.55),
    "dfa_hurst_abs_r":            (0.6, 0.9),
    "leverage_effect":            (-6.0, -0.5),
    "volume_volatility_corr":     (0.3, 0.8),
    "zumbach_asymmetry":          (0.001, 0.5),
}

JOBS = [
    # A series: original v3 architectures
    ("A0_baseline_spx",            "experiments/022_h20_batch/results_a0/inference_merged.json"),
    ("A1_multi_asset",             "experiments/022_h20_batch/results_a1/inference_merged.json"),
    ("A2_+multiscale_hawkes",      "experiments/022_h20_batch/results_a2/inference_merged.json"),
    ("A3_+regime_GRU",             "experiments/022_h20_batch/results_a3/inference_merged.json"),
    ("A4_+twopop_γT",              "experiments/022_h20_batch/results_a4/inference_merged.json"),
    ("A5_all_features",            "experiments/022_h20_batch/results_a5/inference_merged.json"),
    # B series: conservative v3 hyperparams
    ("B0_baseline_redo",           "experiments/022_h20_batch/results_b0/inference_merged.json"),
    ("B1_multi_asset",             "experiments/022_h20_batch/results_b1/inference_merged.json"),
    ("B2_+mshawkes_conservative",  "experiments/022_h20_batch/results_b2/inference_merged.json"),
    ("B3_+regime_conservative",    "experiments/022_h20_batch/results_b3/inference_merged.json"),
    ("B4_+twopop_conservative",    "experiments/022_h20_batch/results_b4/inference_merged.json"),
    ("B5_all_conservative",        "experiments/022_h20_batch/results_b5/inference_merged.json"),
    # C series: A architectures + expanded loss (autocorr_r + hill_max)
    ("C0_baseline_+exploss",       "experiments/022_h20_batch/results_c0/inference_merged.json"),
    ("C1_multi_asset_+exploss",    "experiments/022_h20_batch/results_c1/inference_merged.json"),
    ("C2_+mshawkes_+exploss",      "experiments/022_h20_batch/results_c2/inference_merged.json"),
    ("C3_+regime_+exploss",        "experiments/022_h20_batch/results_c3/inference_merged.json"),
    ("C4_+twopop_+exploss",        "experiments/022_h20_batch/results_c4/inference_merged.json"),
    ("C5_all_+exploss",            "experiments/022_h20_batch/results_c5/inference_merged.json"),
    # D series: longer training (400 iters) on best candidates
    ("D0_a0_long",                 "experiments/022_h20_batch/results_d0/inference_merged.json"),
    ("D1_b0_long",                 "experiments/022_h20_batch/results_d1/inference_merged.json"),
    ("D2_b4_long",                 "experiments/022_h20_batch/results_d2/inference_merged.json"),
    ("D3_c0_long",                 "experiments/022_h20_batch/results_d3/inference_merged.json"),
    ("D4_c4_long",                 "experiments/022_h20_batch/results_d4/inference_merged.json"),
]


def score_one(p: Path) -> dict[str, object] | None:
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
    return {"n_pass": n_pass, "n_total": n_total, "rows": rows, "n_realiz": d.get("n_total_rollouts", 0)}


def main() -> None:
    out_path = REPO / "experiments/022_h20_batch/scoreboard.md"
    lines: list[str] = []
    lines.append("# v3 batch scoreboard")
    lines.append("")
    lines.append("Inference 11-fact (10 actually scored — conditional_kurtosis missing in")
    lines.append("inference module) on the trained ckpt of each batch variant.")
    lines.append("")

    # Summary table
    lines.append("| Variant | n/10 | acf(r²) | hill | leverage | zumbach | aggr_g |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    summary_rows = []
    for label, p_str in JOBS:
        p = REPO / p_str
        s = score_one(p)
        if s is None:
            lines.append(f"| {label} | — | (missing) | — | — | — | — |")
            continue
        rows = s["rows"]
        acf = rows.get("acf_squared_returns", (None, False))[0]
        hill = rows.get("hill_tail_index", (None, False))[0]
        lev = rows.get("leverage_effect", (None, False))[0]
        zum = rows.get("zumbach_asymmetry", (None, False))[0]
        aggr = rows.get("aggregational_gaussianity", (None, False))[0]

        def fmt(v):
            return "—" if v is None else f"{v:+.3f}"

        flag = "★" if s["n_pass"] >= 7 else ("+" if s["n_pass"] >= 5 else "")
        lines.append(
            f"| {label} | **{s['n_pass']}/{s['n_total']}** {flag}"
            f" | {fmt(acf)} | {fmt(hill)} | {fmt(lev)} | {fmt(zum)} | {fmt(aggr)} |"
        )
        summary_rows.append((label, s))
    lines.append("")
    lines.append("Real targets: acf=+0.342, hill=2.68, leverage=−0.79, zumbach>0, aggr 10-200")
    lines.append("")

    # Detailed per-variant
    for label, s in summary_rows:
        lines.append(f"## {label} — {s['n_pass']}/{s['n_total']} (n_realiz={s['n_realiz']})")
        lines.append("")
        lines.append("| fact | value | band | pass |")
        lines.append("|---|---:|---|:-:|")
        for k, (v, passed) in s["rows"].items():
            lo, hi = BANDS[k]
            lines.append(f"| {k} | {v:+.3f} | [{lo:+.2f}, {hi:+.2f}] | "
                         f"{'✓' if passed else '✗'} |")
        lines.append("")

    out_path.write_text("\n".join(lines))
    print(f"wrote {out_path}")
    # Print summary to stdout
    print()
    print("Summary:")
    for label, s in summary_rows:
        flag = " ★" if s["n_pass"] >= 7 else ""
        print(f"  {label:<28} {s['n_pass']:>2}/{s['n_total']}{flag}")


if __name__ == "__main__":
    main()
