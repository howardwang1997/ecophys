#!/usr/bin/env python3
"""Diagnose whether the exp-102 multi-fact surrogates actually entered the
gradient during training, and (if active) whether they moved their target fact.

Background (2026-05-28 review): exp 102 (`mf_*` cells) was the test of the
"objective-coverage" hypothesis — put facts #3/#4/#5/#8 directly in the loss via
the surrogates in `ecomd/training/fact_surrogates.py`. The score gate found 0/14
cells beat baseline. This script establishes *why*, distinguishing two outcomes:

  (A) hypothesis tested and Pareto-collateral: the surrogate moved its target
      fact but broke others → objective coverage is real but the ceiling is a
      genuine trade-off frontier.
  (B) hypothesis NOT tested: the surrogate contributed zero gradient at training
      time (its length guard fired on the ~7-return training rollout), so the
      cell trained identically to baseline.

Three checks:
  (a) bit-identity: per-seed max-abs-diff of the 11 aggregated facts, cell vs
      baseline_v3. ~0 ⇒ zero training gradient ⇒ (B).
  (b) per-fact attribution: for active cells, did the cell-mean of the *targeted*
      fact move toward its band, and how many other facts went out of band?
  (c) gradient-liveness vs rollout length n: calls each surrogate on random
      returns of length n∈{7,24,50,200,400} and reports whether grad_fn is None
      (the length-guard fallback ⇒ dead) — explains the (a) result mechanically.

Read-only. Usage:
    python scripts/diagnose_surrogate_coverage.py experiments/102_multifact_loss_n30
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent

# Keep in sync with scripts/score_summary.py BANDS.
BANDS: dict[str, tuple[float, float]] = {
    "autocorr_returns":          (-0.1, 0.20),
    "hill_tail_index":           (2.0, 4.0),
    "gain_loss_asymmetry":       (-30.0, -3.0),
    "aggregational_gaussianity": (10.0, 200.0),
    "intermittency_fano":        (5.0, 100.0),
    "acf_squared_returns":       (0.15, 0.55),
    "conditional_kurtosis":      (-1.0, 3.0),
    "dfa_hurst_abs_r":           (0.6, 0.9),
    "leverage_effect":           (-6.0, -0.5),
    "volume_volatility_corr":    (0.3, 0.8),
    "zumbach_asymmetry":         (0.001, 0.5),
}

# Which eval fact each single-fact surrogate cell targets.
CELL_TARGET_FACT: dict[str, str] = {
    "mf_skew": "gain_loss_asymmetry",
    "mf_agg":  "aggregational_gaussianity",
    "mf_fano": "intermittency_fano",
    "mf_dfa":  "dfa_hurst_abs_r",
}
ALL_TARGET_FACTS = list(CELL_TARGET_FACT.values())
BASELINE = "baseline_v3"


def _cell_of(result_dir: Path) -> str:
    name = result_dir.name.removeprefix("results_")
    return name.rsplit("_seed", 1)[0] if "_seed" in name else name


def _seed_of(result_dir: Path) -> str | None:
    name = result_dir.name
    return name.rsplit("_seed", 1)[1] if "_seed" in name else None


def load_aggregated(exp_dir: Path) -> dict[str, dict[str, dict[str, float]]]:
    """{cell: {seed: {fact: mean}}} from each results_*/inference_merged.json."""
    out: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    for d in sorted(exp_dir.glob("results_*")):
        merged = d / "inference_merged.json"
        if not merged.is_dir() and merged.exists():
            seed = _seed_of(d)
            if seed is None:
                continue
            try:
                agg = json.loads(merged.read_text()).get("aggregated", {})
            except Exception:
                continue
            facts = {k: float(v["mean"]) for k, v in agg.items()
                     if isinstance(v, dict) and "mean" in v}
            out[_cell_of(d)][seed] = facts
    return out


def check_bit_identity(data: dict[str, dict[str, dict[str, float]]]) -> list[str]:
    lines = ["## (a) Bit-identity vs baseline_v3 — zero-gradient detector", ""]
    base = data.get(BASELINE, {})
    if not base:
        return lines + ["  [warn] no baseline_v3 results found", ""]
    lines.append("| cell | seeds compared | mean max-abs-diff | seeds bit-identical | verdict |")
    lines.append("|---|---:|---:|---:|---|")
    for cell in sorted(c for c in data if c != BASELINE):
        diffs: list[float] = []
        identical = 0
        shared = sorted(set(data[cell]) & set(base))
        for s in shared:
            facts = set(data[cell][s]) & set(base[s]) & set(BANDS)
            md = max((abs(data[cell][s][f] - base[s][f]) for f in facts), default=float("nan"))
            diffs.append(md)
            if md < 1e-6:
                identical += 1
        if not diffs:
            continue
        mean_d = float(np.nanmean(diffs))
        frac = identical / len(shared)
        verdict = ("**ZERO-GRAD (≡ baseline)**" if frac > 0.9
                   else "active" if mean_d > 1e-3 else "near-baseline")
        lines.append(f"| `{cell}` | {len(shared)} | {mean_d:.4g} | "
                     f"{identical}/{len(shared)} | {verdict} |")
    lines.append("")
    return lines


def _cell_mean(data: dict[str, dict[str, dict[str, float]]], cell: str, fact: str) -> float:
    vals = [s[fact] for s in data.get(cell, {}).values() if fact in s]
    return float(np.mean(vals)) if vals else float("nan")


def _in_band(fact: str, v: float) -> bool:
    lo, hi = BANDS[fact]
    return lo <= v <= hi


def check_attribution(data: dict[str, dict[str, dict[str, float]]]) -> list[str]:
    lines = ["## (b) Per-fact attribution — did the targeted fact move?", ""]
    cells = [c for c in (*CELL_TARGET_FACT, "mf_all_l1", "mf_all_mse", "mf_all_huber") if c in data]
    for cell in cells:
        targets = (ALL_TARGET_FACTS if cell.startswith("mf_all")
                   else [CELL_TARGET_FACT[cell]])
        lines.append(f"### `{cell}` (targets: {', '.join(targets)})")
        lines.append("| fact | baseline mean | cell mean | toward band? | in-band base→cell |")
        lines.append("|---|---:|---:|:--:|:--:|")
        for fact in targets:
            b = _cell_mean(data, BASELINE, fact)
            c = _cell_mean(data, cell, fact)
            lo, hi = BANDS[fact]
            ctr = (lo + hi) / 2
            toward = "→" if abs(c - ctr) < abs(b - ctr) else "—"
            band_str = f"{'Y' if _in_band(fact, b) else 'N'}→{'Y' if _in_band(fact, c) else 'N'}"
            lines.append(f"| {fact} | {b:+.3f} | {c:+.3f} | {toward} | {band_str} |")
        # collateral: facts that left the band relative to baseline
        broken = []
        for fact in BANDS:
            b = _cell_mean(data, BASELINE, fact)
            c = _cell_mean(data, cell, fact)
            if not np.isnan(b) and not np.isnan(c) and _in_band(fact, b) and not _in_band(fact, c):
                broken.append(fact)
        lines.append(f"- collateral (in-band at baseline, out-of-band at cell): "
                     f"{', '.join(broken) if broken else 'none'}")
        lines.append("")
    return lines


def check_liveness() -> list[str]:
    lines = ["## (c) Surrogate gradient liveness vs training-rollout length n", ""]
    try:
        sys.path.insert(0, str(REPO))
        import torch
        from ecomd.training import fact_surrogates as fs
    except Exception as e:  # pragma: no cover
        return lines + [f"  [skip] could not import torch/fact_surrogates: {e}", ""]

    lines.append("| n | skew | agg | fano | dfa |")
    lines.append("|---:|:--:|:--:|:--:|:--:|")
    g = lambda x: "live" if x.grad_fn is not None else "**DEAD**"
    for n in (7, 24, 50, 200, 400):
        torch.manual_seed(0)
        r = (torch.randn(n, requires_grad=True) * 0.01)
        sk = fs.gain_loss_skew(r)
        ag = fs.agg_gaussianity(r, scale_large=50)
        fn = fs.soft_fano(r, quantile=0.99, n_windows=50)
        dh = fs.dfa_hurst_surrogate(r.abs(), min_scale=16, max_scale_frac=0.1)
        agg_note = g(ag) + ("(k1-only)" if n < 8 * 50 else "")
        lines.append(f"| {n} | {g(sk)} | {agg_note} | {g(fn)} | {g(dh)} |")
    lines += ["",
              "fano needs n≥50, dfa needs n≥~200, agg needs n≥400 for the correct "
              "(k1−kL) signal. Training rollout (chunk_steps=24, warmup=16) feeds "
              "only ~7 returns ⇒ 3/4 surrogates dead/degraded ⇒ exp-102 did NOT "
              "test the objective-coverage hypothesis (outcome B).", ""]
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("exp_dir", help="experiment dir, e.g. experiments/102_multifact_loss_n30")
    args = ap.parse_args()
    exp_dir = (REPO / args.exp_dir) if not Path(args.exp_dir).is_absolute() else Path(args.exp_dir)

    data = load_aggregated(exp_dir)
    out = [f"# Surrogate-coverage diagnostic — {exp_dir.name}", ""]
    out += check_bit_identity(data)
    out += check_attribution(data)
    out += check_liveness()
    print("\n".join(out))


if __name__ == "__main__":
    main()
