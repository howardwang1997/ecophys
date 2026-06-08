"""Score exp 120 — train-at-N control vs exp-116 inference-swept hill(N).

The criticality claim (116) is that the tail index hill drops toward/through α=2 as the number of
interacting agents N grows. 116 measures this by sweeping N at INFERENCE on a model trained at
N=10000. This script overlays the train-at-N control (120: a baseline trained AND evaluated at each
N) on the inference-swept curve. Agreement ⇒ the N-scaling is a property of the learned dynamics,
not a train/test extrapolation artifact (the key reviewer defense).

Per asset:
  - 120 train-at-N:    hill(N) mean ± 95% CI (bootstrap over seeds), each model at its own N
  - 116 inference:     hill(N) mean ± 95% CI at κ=0 (the relevant anchor), one model swept
  - per-N agreement:   |Δhill| and whether the CIs overlap
Verdict: curves agree (artifact-free) iff CIs overlap at every shared N (or |Δ| small throughout).

Usage: python scripts/score_fss_train.py [--train experiments/120_fss_train]
                                          [--infer experiments/116_criticality]
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

RNG = np.random.default_rng(0)
TRAIN_RE = re.compile(r"results_N(?P<N>\d+)_seed\d+$")
INFER_RE = re.compile(r"results_(?P<anchor>.+?)__N(?P<N>\d+)_k(?P<k>\d+)$")


def _hill_vals(merged: Path) -> list[float]:
    d = json.loads(merged.read_text())
    out = [float(r["facts"]["hill_tail_index"]["estimate"])
           for r in d.get("realizations", [])
           if isinstance(r.get("facts", {}).get("hill_tail_index", {}).get("estimate"), (int, float))
           and np.isfinite(r["facts"]["hill_tail_index"]["estimate"])]
    if not out:
        m = d.get("aggregated", {}).get("hill_tail_index", {}).get("mean")
        if isinstance(m, (int, float)) and np.isfinite(m):
            out = [float(m)]
    return out


def _ci(v: np.ndarray) -> tuple[float, float]:
    if len(v) < 3:
        return (float("nan"), float("nan"))
    bs = [np.mean(RNG.choice(v, len(v), replace=True)) for _ in range(2000)]
    return tuple(np.percentile(bs, [2.5, 97.5]))


def collect_train(root: Path) -> dict[str, dict[int, list[float]]]:
    out: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for d in sorted(root.glob("*/results_N*_seed*")):
        m = TRAIN_RE.match(d.name)
        mj = d / "inference_merged.json"
        if m and mj.exists():
            out[d.parent.name][int(m["N"])].extend(_hill_vals(mj))
    return out


def collect_infer(root: Path) -> dict[int, list[float]]:
    """Inference-swept hill(N) at κ=0, pooled over anchors+seeds."""
    out: dict[int, list[float]] = defaultdict(list)
    for d in sorted(root.glob("results_*__N*_k00")):
        m = INFER_RE.match(d.name)
        mj = d / "inference_merged.json"
        if m and mj.exists():
            out[int(m["N"])].extend(_hill_vals(mj))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--train", default="experiments/120_fss_train")
    ap.add_argument("--infer", default="experiments/116_criticality")
    args = ap.parse_args()

    train = collect_train(Path(args.train))
    infer = collect_infer(Path(args.infer))

    if not train:
        print("no exp-120 train-at-N results yet"); return

    infer_means = {n: float(np.mean(v)) for n, v in infer.items() if v}
    infer_ci = {n: _ci(np.array(v)) for n, v in infer.items() if v}

    for asset in sorted(train):
        print(f"\n# asset={asset} — train-at-N (120) vs inference-swept (116, κ=0)")
        print(f"  {'N':>7}{'train hill':>12}{'train CI':>16}{'infer hill':>12}{'infer CI':>16}{'agree':>7}")
        Ns = sorted(train[asset])
        all_agree = True
        any_overlap_checked = False
        for N in Ns:
            tv = np.array(train[asset][N])
            tlo, thi = _ci(tv)
            tm = float(np.mean(tv))
            tci = f"[{tlo:.2f},{thi:.2f}]" if tlo == tlo else "(n<3)"
            if N in infer_means:
                im = infer_means[N]; ilo, ihi = infer_ci[N]
                ici = f"[{ilo:.2f},{ihi:.2f}]" if ilo == ilo else "(n<3)"
                overlap = not (thi < ilo or ihi < tlo) if (tlo == tlo and ilo == ilo) else None
                if overlap is not None:
                    any_overlap_checked = True
                    all_agree = all_agree and overlap
                ag = "✓" if overlap else ("✗" if overlap is False else "—")
                print(f"  {N:>7}{tm:>12.2f}{tci:>16}{im:>12.2f}{ici:>16}{ag:>7}")
            else:
                print(f"  {N:>7}{tm:>12.2f}{tci:>16}{'—':>12}{'(no 116 N)':>16}{'—':>7}")
        # train-at-N monotonic drop?
        tmeans = [float(np.mean(train[asset][N])) for N in Ns]
        drop = tmeans[0] - tmeans[-1]
        crosses2 = any(m < 2.0 for m in tmeans) and any(m >= 2.0 for m in tmeans)
        print(f"  train-at-N: hill {tmeans[0]:.2f}(N={Ns[0]}) → {tmeans[-1]:.2f}(N={Ns[-1]}), "
              f"Δ={drop:+.2f}; crosses α=2: {crosses2}")
        if any_overlap_checked:
            print(f"  → ARTIFACT CONTROL: train vs inference curves "
                  f"{'AGREE (criticality is a learned-dynamics property, not extrapolation)' if all_agree else 'DISAGREE — N-scaling is partly train/test mismatch; report honestly'}")
        else:
            print("  → no shared N with 116 yet (run both, then re-score)")


if __name__ == "__main__":
    main()
