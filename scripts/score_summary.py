#!/usr/bin/env python3
"""Generate a copy-paste-ready commit-message body summarising experiment
results across one or more dirs.

Background: the H20 commit `8928237` for Branch E reported "083 a07 mean=7.1 /
081 btc_v4combo mean=6.8 / combo_full mean=6.2 (Case 2)" which on Mac re-scoring
turned out to be cherry-picked subsets (mean of seeds with n_pass≥6, NOT cell
mean) and one cell label was wrong (a04 reported as a07). That happened
because there was no standardized summary tool — whoever wrote the commit
eyeballed `scoreboard.md` Top-10 and inflated.

This script exists so commit messages on H20 can be generated mechanically
instead of by hand. Use it like:

    bash scripts/h20_branch_X.sh
    # When done, capture the summary:
    python scripts/score_summary.py experiments/088_pairs_and_confirmation > /tmp/summary.txt
    git add ...
    git commit -m "$(cat /tmp/summary.txt)"

The output uses the SAME stability filter as `score_phase.py`
(`instability_reason`), so the numbers in the commit message will match
the per-cell table in `scoreboard.md` exactly. No more cherry-picking.

Output format (one line per cell, sorted by mean descending):

    Branch X: <dir1>, <dir2>, ...
      cell_name              n=NN/MM rej=K  mean=M.MM ± S.SS  max=N  #(≥8)=N

    Headline: best 3 cells with mean ≥ THRESHOLD; flag if any cell ties or
    beats the previous SOTA reference.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent

# Same constants as score_phase.py — keep in sync if BANDS or thresholds change.
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

# Reference SOTA the script flags against. Update as new records land.
SOTA_MEAN = 5.39   # Branch E btc_v4combo (n=23 after filter)
SOTA_MAX = 9       # Branch D 9/11 ×3 in asymdrag_a06


def is_unstable(agg: dict) -> str | None:
    for k in BANDS:
        v = agg.get(k, {}).get("mean")
        if v is None or not np.isfinite(v):
            return f"{k}=NaN/inf"
    for k, lim in INSTABILITY_LIMITS.items():
        v = agg.get(k, {}).get("mean")
        if v is not None and abs(v) > lim:
            return f"{k}={v:.1f}"
    return None


def n_pass(agg: dict) -> int:
    return sum(
        1 for k, (lo, hi) in BANDS.items()
        if k in agg and lo <= agg[k]["mean"] <= hi
    )


def cell_label(result_dir: Path) -> str:
    name = result_dir.name.removeprefix("results_")
    if "_seed" in name:
        name = name.rsplit("_seed", 1)[0]
    return name


def summarise_dir(exp_dir: Path) -> tuple[str, list[dict]]:
    """Return (header, [per-cell summary rows]) for a single experiment dir."""
    cells: dict[str, list[int]] = defaultdict(list)
    rejected: dict[str, int] = defaultdict(int)
    total: dict[str, int] = defaultdict(int)
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
        total[cell] += 1
        reason = is_unstable(agg)
        if reason is not None:
            rejected[cell] += 1
        else:
            cells[cell].append(n_pass(agg))

    rows = []
    for cell, scores in cells.items():
        mean = float(np.mean(scores))
        std = float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0
        rows.append({
            "cell": cell,
            "n_eval": len(scores),
            "n_total": total[cell],
            "rejected": rejected.get(cell, 0),
            "mean": mean,
            "std": std,
            "max": max(scores),
            "n_ge8": sum(1 for s in scores if s >= 8),
        })
    rows.sort(key=lambda r: -r["mean"])
    return exp_dir.name, rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Standardised commit-message body generator for experiment dirs."
    )
    parser.add_argument("dirs", nargs="+", help="experiment dirs to summarise")
    parser.add_argument("--title", default=None,
                        help="commit-message first line (e.g. 'Branch F (088): pair sweep')")
    args = parser.parse_args()

    out_lines: list[str] = []
    if args.title:
        out_lines.append(args.title)
        out_lines.append("")

    all_summaries = []
    grand_max_mean = 0.0
    grand_max_max = 0
    best_cell_overall = None

    for d in args.dirs:
        path = (REPO / d).resolve() if not Path(d).is_absolute() else Path(d)
        if not path.exists():
            out_lines.append(f"  [warn] {path} does not exist")
            continue
        name, rows = summarise_dir(path)
        if not rows:
            out_lines.append(f"  [warn] {name}: no eval results found")
            continue
        out_lines.append(f"{name}:")
        for r in rows:
            line = (f"  {r['cell']:30s}  n={r['n_eval']:2d}/{r['n_total']:2d}"
                    f"  rej={r['rejected']:2d}"
                    f"  mean={r['mean']:.2f} ± {r['std']:.2f}"
                    f"  max={r['max']}"
                    f"  #(≥8)={r['n_ge8']}")
            out_lines.append(line)
            if r["mean"] > grand_max_mean:
                grand_max_mean = r["mean"]
                best_cell_overall = (name, r)
            grand_max_max = max(grand_max_max, r["max"])
        all_summaries.append((name, rows))
        out_lines.append("")

    # Headline
    if best_cell_overall:
        name, r = best_cell_overall
        sota_mean_flag = " (NEW SOTA mean!)" if r["mean"] > SOTA_MEAN else ""
        sota_max_flag = " (NEW SOTA max!)" if r["max"] > SOTA_MAX else ""
        out_lines.append(f"Best cell: {name}/{r['cell']} mean={r['mean']:.2f}"
                         f" max={r['max']}{sota_mean_flag}{sota_max_flag}")
        out_lines.append(f"(reference SOTA: mean={SOTA_MEAN:.2f} from btc_v4combo,"
                         f" max={SOTA_MAX} from asymdrag_a06)")

    print("\n".join(out_lines))


if __name__ == "__main__":
    main()
