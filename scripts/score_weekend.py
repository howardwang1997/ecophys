#!/usr/bin/env python
"""Weekend batch scoring — auto-discover all results_*/inference_merged.json
under experiments/023_weekend/, score the 10 stylized facts, write a
matrix scoreboard.md grouped by phase.

Run on Mac after H20 push:
    git pull
    conda run -n ecophys python scripts/score_weekend.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WEEKEND_DIR = REPO / "experiments/023_weekend"

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
    "conditional_kurtosis":       (-1.0, 3.0),
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


def main() -> None:
    out_path = WEEKEND_DIR / "scoreboard.md"
    results: list[tuple[str, dict | None]] = []

    # Discover all result dirs sorted by phase
    rds = sorted(WEEKEND_DIR.glob("results_*/inference_merged.json"))
    for p in rds:
        label = p.parent.name.replace("results_", "")
        results.append((label, score_one(p)))

    # Group by leading letter
    phases: dict[str, list] = {}
    for label, s in results:
        ph = label[0].upper()
        phases.setdefault(ph, []).append((label, s))

    lines = ["# Weekend batch scoreboard", "", "Discovered "
             f"{len(results)} runs from `experiments/023_weekend/`.", ""]

    # Top-of-page summary: best of each phase + overall best
    overall_best = sorted(
        [(lbl, s) for lbl, s in results if s is not None],
        key=lambda x: -x[1]["n_pass"],
    )
    lines.append("## Top 10 across all phases")
    lines.append("")
    lines.append("| rank | variant | n/N | n_realiz |")
    lines.append("|---:|---|---:|---:|")
    for i, (lbl, s) in enumerate(overall_best[:10]):
        lines.append(f"| {i+1} | `{lbl}` | **{s['n_pass']}/{s['n_total']}** | {s['n_realiz']} |")
    lines.append("")

    # Per-phase
    for ph in sorted(phases.keys()):
        items = phases[ph]
        lines.append(f"## Phase {ph} ({len(items)} runs)")
        lines.append("")
        lines.append("| variant | n/N | acf(r²) | hill | leverage | zumbach | aggr_g | autocorr_r |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        for lbl, s in sorted(items, key=lambda x: x[0]):
            if s is None:
                lines.append(f"| `{lbl}` | — | (missing inference) | — | — | — | — | — |")
                continue

            def get(name):
                if name in s["rows"]:
                    return f"{s['rows'][name][0]:+.3f}"
                return "—"

            flag = "★" if s["n_pass"] >= 7 else ("+" if s["n_pass"] >= 5 else "")
            lines.append(
                f"| `{lbl}` | **{s['n_pass']}/{s['n_total']}** {flag}"
                f" | {get('acf_squared_returns')} | {get('hill_tail_index')}"
                f" | {get('leverage_effect')} | {get('zumbach_asymmetry')}"
                f" | {get('aggregational_gaussianity')} | {get('autocorr_returns')} |"
            )
        lines.append("")

    out_path.write_text("\n".join(lines))
    print(f"wrote {out_path}")
    print()
    print(f"Total: {len(results)} runs, "
          f"{sum(1 for _, s in results if s and s['n_pass'] >= 7)} ≥ 7/N, "
          f"{sum(1 for _, s in results if s and s['n_pass'] >= 8)} ≥ 8/N")
    print("Top 5:")
    for lbl, s in overall_best[:5]:
        print(f"  {lbl:<28} {s['n_pass']}/{s['n_total']}")


if __name__ == "__main__":
    main()
