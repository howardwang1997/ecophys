#!/usr/bin/env python3
"""Build the mechanism-fact attribution matrix from 089 (or any leave-one-in
single-mechanism batch).

Input: an experiments/<dir>/ containing results_<cell>_seedN/inference_merged.json
files where each cell is one (mechanism, strength) cell. Convention: a
cell named ``attr_baseline_*`` is treated as the v3 control row (Δ-vs-
baseline columns are computed against it).

Output (written to <dir>/):
- ``attribution_matrix.md``: markdown table, rows = cells (sorted by mean
  pass-count desc), columns = the 11 stylized facts (per-cell pass-rate
  in %). Plus a "Δ vs baseline" pass-count column.
- ``attribution_matrix.json``: machine-readable {cell: {fact: pass_rate}}
  for downstream figure builders.

Stability filter: same as score_phase.py / score_summary.py
(``conditional_kurtosis>100``, ``aggregational_gaussianity>1000``, NaN/inf).
Cells where the filter rejects > 30% of seeds get a warning row.

Usage:
    conda run -n ecophys python scripts/score_attribution.py experiments/089_attribution_50seed
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent

# Same constants as score_phase.py / score_summary.py — keep in sync.
BANDS = {
    "autocorr_returns":           (-0.1, 0.20),
    "hill_tail_index":            (2.0, 4.0),
    "gain_loss_asymmetry":        (-30.0, -3.0),
    "aggregational_gaussianity": (10.0, 200.0),
    "intermittency_fano":         (5.0, 100.0),
    "acf_squared_returns":        (0.15, 0.55),
    "conditional_kurtosis":       (-1.0, 3.0),
    "dfa_hurst_abs_r":           (0.6, 0.9),
    "leverage_effect":            (-6.0, -0.5),
    "volume_volatility_corr":     (0.3, 0.8),
    "zumbach_asymmetry":          (0.001, 0.5),
}
INSTABILITY_LIMITS = {
    "conditional_kurtosis":      100.0,
    "aggregational_gaussianity": 1000.0,
}

BASELINE_PREFIX = "attr_baseline"


def is_unstable(agg: dict) -> bool:
    for k in BANDS:
        v = agg.get(k, {}).get("mean")
        if v is None or not np.isfinite(v):
            return True
    for k, lim in INSTABILITY_LIMITS.items():
        v = agg.get(k, {}).get("mean")
        if v is not None and abs(v) > lim:
            return True
    return False


def cell_label(result_dir: Path) -> str:
    name = result_dir.name.removeprefix("results_")
    if "_seed" in name:
        name = name.rsplit("_seed", 1)[0]
    return name


def collect(exp_dir: Path) -> tuple[dict[str, dict[str, list[float]]], dict[str, int], dict[str, int]]:
    """Returns (per_fact_values_per_cell, n_total_per_cell, n_rejected_per_cell)."""
    per_fact: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    n_total: dict[str, int] = defaultdict(int)
    n_rej: dict[str, int] = defaultdict(int)
    for d in sorted(exp_dir.glob("results_*")):
        if not d.is_dir():
            continue
        merged = d / "inference_merged.json"
        if not merged.exists():
            continue
        try:
            agg = json.loads(merged.read_text()).get("aggregated", {})
        except Exception:
            continue
        cell = cell_label(d)
        n_total[cell] += 1
        if is_unstable(agg):
            n_rej[cell] += 1
            continue
        for fact in BANDS:
            v = agg.get(fact, {}).get("mean")
            if v is None or not np.isfinite(v):
                continue
            per_fact[cell][fact].append(float(v))
    return per_fact, n_total, n_rej


def compute_pass_rate(values: list[float], band: tuple[float, float]) -> float:
    """Fraction of seeds whose mean falls in band, in percentage points."""
    if not values:
        return float("nan")
    lo, hi = band
    arr = np.array(values)
    return float(100.0 * np.mean((arr >= lo) & (arr <= hi)))


def write_outputs(exp_dir: Path,
                  per_fact: dict[str, dict[str, list[float]]],
                  n_total: dict[str, int],
                  n_rej: dict[str, int]) -> None:
    """Emit attribution_matrix.{md,json} into ``exp_dir``."""
    cells = sorted(per_fact.keys())
    facts = list(BANDS.keys())

    # Per-cell pass rates per fact + sum
    rows: list[dict] = []
    baseline_row: dict | None = None
    for cell in cells:
        row = {"cell": cell, "n_seeds": len(next(iter(per_fact[cell].values()), []))}
        row["n_total"] = n_total[cell]
        row["n_rej"] = n_rej.get(cell, 0)
        row["per_fact_pass_rate"] = {}
        sum_pr = 0.0
        n_facts_present = 0
        for fact in facts:
            pr = compute_pass_rate(per_fact[cell].get(fact, []), BANDS[fact])
            row["per_fact_pass_rate"][fact] = pr
            if not np.isnan(pr):
                sum_pr += pr / 100.0
                n_facts_present += 1
        row["mean_n_pass"] = sum_pr if n_facts_present == 11 else float("nan")
        rows.append(row)
        if cell.startswith(BASELINE_PREFIX):
            baseline_row = row

    rows.sort(key=lambda r: -(r["mean_n_pass"] if not np.isnan(r["mean_n_pass"]) else -1))

    # ── JSON dump (machine-readable) ──────────────────────────────────
    json_out: dict = {
        "experiment_dir": exp_dir.name,
        "facts": facts,
        "bands": {k: list(v) for k, v in BANDS.items()},
        "baseline_cell": baseline_row["cell"] if baseline_row else None,
        "rows": rows,
    }
    (exp_dir / "attribution_matrix.json").write_text(json.dumps(json_out, indent=2))

    # ── Markdown ──────────────────────────────────────────────────────
    lines: list[str] = [f"# Attribution matrix — {exp_dir.name}", ""]
    lines.append(f"Discovered {len(cells)} cells, 11 facts. "
                 f"Pass-rate = % of seeds whose aggregated fact value falls in band. "
                 f"Stability filter applied (same as `score_phase.py`).")
    lines.append("")
    if baseline_row is None:
        lines.append("> ⚠️ no `attr_baseline_*` cell found — Δ vs baseline columns not emitted.")
        lines.append("")

    # Compact column headers (4-letter abbreviations to keep table narrow)
    abbr = {
        "autocorr_returns":          "ac_r",
        "hill_tail_index":           "hill",
        "gain_loss_asymmetry":       "g/l",
        "aggregational_gaussianity": "agg",
        "intermittency_fano":        "fano",
        "acf_squared_returns":       "ac²",
        "conditional_kurtosis":      "ckur",
        "dfa_hurst_abs_r":           "hurs",
        "leverage_effect":           "lev",
        "volume_volatility_corr":    "v·v",
        "zumbach_asymmetry":         "zum",
    }

    header = "| cell | n | rej |" + "".join(f" {abbr[f]} |" for f in facts) + " mean |"
    sep    = "|---|---:|---:|" + "".join("---:|" for _ in facts) + "---:|"
    lines.append("## Per-cell × per-fact pass rate (%)")
    lines.append(header)
    lines.append(sep)
    for r in rows:
        cell_disp = f"**{r['cell']}**" if r["cell"].startswith(BASELINE_PREFIX) else f"`{r['cell']}`"
        cells_pct = "".join(
            f" {r['per_fact_pass_rate'][f]:3.0f} |" if not np.isnan(r["per_fact_pass_rate"][f]) else "  — |"
            for f in facts
        )
        mean_str = f"{r['mean_n_pass']:.2f}" if not np.isnan(r["mean_n_pass"]) else "—"
        lines.append(f"| {cell_disp} | {r['n_seeds']} | {r['n_rej']} |{cells_pct} **{mean_str}** |")
    lines.append("")

    # ── Δ vs baseline (for each non-baseline cell) ────────────────────
    if baseline_row is not None:
        lines.append("## Δ vs baseline (percentage-point change in pass-rate)")
        lines.append("Positive = mechanism PASSES this fact more than v3 baseline. "
                     "Negative = mechanism BREAKS this fact relative to baseline.")
        lines.append("")
        lines.append(header)
        lines.append(sep)
        for r in rows:
            if r["cell"].startswith(BASELINE_PREFIX):
                continue
            deltas = []
            for f in facts:
                base = baseline_row["per_fact_pass_rate"][f]
                cur = r["per_fact_pass_rate"][f]
                if np.isnan(base) or np.isnan(cur):
                    deltas.append("  — |")
                else:
                    d = cur - base
                    deltas.append(f" {d:+3.0f} |")
            d_mean = (
                r["mean_n_pass"] - baseline_row["mean_n_pass"]
                if not (np.isnan(r["mean_n_pass"]) or np.isnan(baseline_row["mean_n_pass"]))
                else float("nan")
            )
            mean_str = f"{d_mean:+.2f}" if not np.isnan(d_mean) else "—"
            lines.append(f"| `{r['cell']}` | {r['n_seeds']} | {r['n_rej']} |{''.join(deltas)} **{mean_str}** |")
        lines.append("")

    # ── Per-fact biggest mover ────────────────────────────────────────
    if baseline_row is not None:
        lines.append("## Per-fact biggest mover (most positive Δ from baseline)")
        lines.append("| fact | best mechanism | Δ pass-rate |")
        lines.append("|---|---|---:|")
        for f in facts:
            base = baseline_row["per_fact_pass_rate"][f]
            if np.isnan(base):
                continue
            best_cell, best_delta = None, -1e9
            for r in rows:
                if r["cell"].startswith(BASELINE_PREFIX):
                    continue
                cur = r["per_fact_pass_rate"][f]
                if np.isnan(cur):
                    continue
                d = cur - base
                if d > best_delta:
                    best_delta, best_cell = d, r["cell"]
            if best_cell is not None:
                lines.append(f"| `{f}` | `{best_cell}` | {best_delta:+.0f} |")
        lines.append("")

    # ── Cells with high rejection rates ───────────────────────────────
    high_rej = [r for r in rows if r["n_rej"] / max(r["n_total"], 1) > 0.3]
    if high_rej:
        lines.append("## ⚠️ Cells with >30% rejection rate (numerical instability)")
        for r in high_rej:
            pct = 100.0 * r["n_rej"] / max(r["n_total"], 1)
            lines.append(f"- `{r['cell']}`: {r['n_rej']}/{r['n_total']} ({pct:.0f}%)")
        lines.append("")

    out_path = exp_dir / "attribution_matrix.md"
    out_path.write_text("\n".join(lines) + "\n")
    print(f"wrote {out_path}")
    print(f"wrote {exp_dir / 'attribution_matrix.json'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build mechanism-fact attribution matrix.")
    parser.add_argument("dir", help="experiment dir (e.g. experiments/089_attribution_50seed)")
    args = parser.parse_args()
    path = (REPO / args.dir).resolve() if not Path(args.dir).is_absolute() else Path(args.dir)
    if not path.exists():
        raise SystemExit(f"no such dir: {path}")
    per_fact, n_total, n_rej = collect(path)
    if not per_fact:
        raise SystemExit(f"no eval results found in {path}")
    write_outputs(path, per_fact, n_total, n_rej)


if __name__ == "__main__":
    main()
