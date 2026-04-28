#!/usr/bin/env python3
"""Per-fact analysis across all of today's runs.

Aggregates inference_merged.json from every results_* dir under
experiments/{027,031,032,033,034,035,036}/ and answers:

1. Which facts have HIGH pass rate (easy)?
2. Which facts have LOW pass rate (hard / permanent failures)?
3. In high-scoring runs (≥5/11), which facts ARE they passing that
   low-scoring runs aren't? (the "frontier")
4. Are there facts that NEVER pass even in best runs? (the ceiling)

Output: stdout markdown table.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

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

EXP_DIRS = [
    "experiments/027_loss_redesign/results_phase1",
    "experiments/031_chunk_effect",
    "experiments/032_arch_regime_sweep",
    "experiments/033_loss_noise_fix",
    "experiments/034_contamination_paired",
    "experiments/035_stacked_winner",
    "experiments/036_stacked_ablation",
]


def score_one(p: Path) -> tuple[int, dict[str, bool]]:
    if not p.exists():
        return 0, {}
    try:
        d = json.loads(p.read_text())
    except Exception:
        return 0, {}
    agg = d.get("aggregated", {})
    n_pass = 0
    per_fact = {}
    for k, (lo, hi) in BANDS.items():
        if k not in agg:
            per_fact[k] = False
            continue
        v = agg[k]["mean"]
        passed = lo <= v <= hi
        per_fact[k] = passed
        if passed:
            n_pass += 1
    return n_pass, per_fact


def main() -> None:
    rows = []
    for exp_glob in EXP_DIRS:
        # The 027 case is "results_phase1" subdir directly with subdirs underneath
        if "027_loss_redesign" in exp_glob:
            base = REPO / exp_glob
            if not base.exists():
                continue
            for run_dir in sorted(base.iterdir()):
                if not run_dir.is_dir():
                    continue
                p = run_dir / "inference_merged.json"
                score, per_fact = score_one(p)
                if per_fact:
                    rows.append({
                        "exp": "027_phase1",
                        "label": run_dir.name,
                        "score": score,
                        "facts": per_fact,
                    })
        else:
            base = REPO / exp_glob
            if not base.exists():
                continue
            for run_dir in sorted(base.glob("results_*")):
                if not run_dir.is_dir():
                    continue
                label = run_dir.name.replace("results_", "")
                p = run_dir / "inference_merged.json"
                score, per_fact = score_one(p)
                if per_fact:
                    rows.append({
                        "exp": exp_glob.split("/")[1],
                        "label": label,
                        "score": score,
                        "facts": per_fact,
                    })

    print(f"# Per-fact analysis across {len(rows)} runs")
    print()

    # ── 1. Overall pass rate per fact
    print("## 1. Overall pass rate per fact (all runs)")
    print()
    print("| fact | passes | total | rate |")
    print("|---|---:|---:|---:|")
    fact_pass: dict[str, int] = defaultdict(int)
    fact_total = len(rows)
    for r in rows:
        for k, p in r["facts"].items():
            if p:
                fact_pass[k] += 1
    facts_sorted = sorted(BANDS.keys(), key=lambda k: -fact_pass[k])
    for fact in facts_sorted:
        n = fact_pass[fact]
        rate = n / fact_total * 100 if fact_total > 0 else 0
        print(f"| {fact} | {n} | {fact_total} | {rate:.0f}% |")
    print()

    # ── 2. Pass rate among high-scoring runs (≥5/11)
    high_runs = [r for r in rows if r["score"] >= 5]
    low_runs = [r for r in rows if r["score"] <= 2]
    print(f"## 2. Pass rate: high-score runs (≥5/11, n={len(high_runs)}) vs "
          f"low-score (≤2/11, n={len(low_runs)})")
    print()
    print("| fact | high pass% | low pass% | gap |")
    print("|---|---:|---:|---:|")
    for fact in facts_sorted:
        high_n = sum(1 for r in high_runs if r["facts"].get(fact, False))
        low_n = sum(1 for r in low_runs if r["facts"].get(fact, False))
        high_rate = high_n / len(high_runs) * 100 if high_runs else 0
        low_rate = low_n / len(low_runs) * 100 if low_runs else 0
        gap = high_rate - low_rate
        gap_str = f"+{gap:.0f}%" if gap > 0 else f"{gap:.0f}%"
        print(f"| {fact} | {high_rate:.0f}% | {low_rate:.0f}% | {gap_str} |")
    print()
    print("**Reading**:")
    print("- Large `gap` → fact is the *differentiator* between good and bad runs (lever)")
    print("- Small `gap` → fact is either always-pass (easy) or always-fail (perma-broken)")
    print()

    # ── 3. Top runs detailed
    high_runs_sorted = sorted(high_runs, key=lambda x: -x["score"])
    print(f"## 3. All {len(high_runs)} runs ≥ 5/11 — exact pass pattern")
    print()
    fact_short = {
        "autocorr_returns": "ar",
        "hill_tail_index": "hl",
        "gain_loss_asymmetry": "gl",
        "aggregational_gaussianity": "ag",
        "intermittency_fano": "fa",
        "acf_squared_returns": "ac²",
        "conditional_kurtosis": "ck",
        "dfa_hurst_abs_r": "df",
        "leverage_effect": "lv",
        "volume_volatility_corr": "vc",
        "zumbach_asymmetry": "zb",
    }
    header = "| run (exp) | n/11 | " + " | ".join(fact_short[f] for f in BANDS) + " |"
    sep = "|---|---:|" + "|".join([":---:"] * len(BANDS)) + "|"
    print(header)
    print(sep)
    for r in high_runs_sorted[:30]:
        cells = [("✓" if r["facts"].get(f, False) else "·") for f in BANDS]
        print(f"| `{r['label']}` ({r['exp']}) | **{r['score']}/11** | "
              + " | ".join(cells) + " |")
    print()
    print(f"Legend: ar=autocorr_r hl=hill gl=gain_loss ag=aggreg fa=fano "
          f"ac²=acf² ck=cond_kurt df=dfa lv=leverage vc=vol_corr zb=zumbach")
    print()

    # ── 4. Permanent failures (facts that never pass in ANY run)
    print("## 4. Frontier and permanent failures")
    print()
    perma_fail = [f for f in BANDS if fact_pass[f] == 0]
    perma_pass = [f for f in BANDS if fact_pass[f] == fact_total]
    print(f"- **Always pass** (≥99% of runs): {[f for f in BANDS if fact_pass[f] >= fact_total*0.99]}")
    print(f"- **Always fail** (0 runs ever pass): {perma_fail}")
    print(f"- **Best run scores at most {max(r['score'] for r in rows)}/11 of 11 facts**")
    print()
    # Among the top 5/11+ runs, which facts NEVER pass?
    if high_runs:
        never_in_top = [f for f in BANDS
                       if all(not r["facts"].get(f, False) for r in high_runs)]
        print(f"- Facts that fail even in ALL ≥5/11 runs (n={len(high_runs)}): {never_in_top}")
        print()
        print("**These last items are the actual ceiling — improving them requires "
              "architectural changes, not loss/regime tweaks.**")


if __name__ == "__main__":
    main()
