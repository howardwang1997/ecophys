"""Score exp 116 v2 — finite-size scaling of the tail index hill(N).

Question: as the number of interacting agents N grows (at fixed learned dynamics), does the tail
index cross α=2 (hill=2, the infinite-variance boundary) at a critical N_c, and is the crossover
a finite-size-rounded step (→ emergent transition in N→∞) or a smooth crossover (no critical point)?

For each κ (pooling anchors + seeds):
  - hill(N) mean ± 95% CI (bootstrap over the per-realization hill values)
  - N_c = N where the fitted hill(logN) curve crosses 2 (log-linear interpolation between the
    bracketing N points)
  - crossover steepness = |d hill / d logN| (a sharper step is the finite-size signature; a single
    anchor-set can't prove the N→∞ limit, so this is reported, not over-claimed)

Honest verdict: report whether hill crosses 2 within the N ladder, N_c, and whether N_c is
κ-independent. A clean κ-independent, steep, well-localized N_c is *consistent with* an emergent
α<2 transition; a shallow, wide crossover is the "aggregate-flow crossover" reading. A true
scaling-collapse claim needs ≥4 system reaches and is flagged if the ladder is too sparse.

Usage: python scripts/score_criticality.py experiments/116_criticality
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

RNG = np.random.default_rng(0)
ALPHA2 = 2.0  # hill=2 ⇔ tail exponent α=2, the infinite-variance boundary
DIR_RE = re.compile(r"results_(?P<anchor>.+?)__N(?P<N>\d+)_k(?P<k>\d+)$")


def _hill_values(merged: Path) -> list[float]:
    """Per-realization hill estimates (falls back to aggregated mean for v1 single-real dirs)."""
    d = json.loads(merged.read_text())
    out = []
    for r in d.get("realizations", []):
        e = r.get("facts", {}).get("hill_tail_index", {}).get("estimate")
        if isinstance(e, (int, float)) and np.isfinite(e):
            out.append(float(e))
    if not out:
        m = d.get("aggregated", {}).get("hill_tail_index", {}).get("mean")
        if isinstance(m, (int, float)) and np.isfinite(m):
            out = [float(m)]
    return out


def _ktag_to_kappa(k: str) -> float:
    # "00"→0.0, "04"→0.4, "12"→1.2  (generator: f"{kap:.1f}".replace(".",""))
    return int(k) / 10.0


def _crossing(ns: np.ndarray, hills: np.ndarray) -> float | None:
    """N where hill(logN) crosses 2 (log-linear interp on the first bracketing pair)."""
    order = np.argsort(ns)
    ns, hills = ns[order], hills[order]
    for i in range(len(ns) - 1):
        h0, h1 = hills[i], hills[i + 1]
        if (h0 - ALPHA2) * (h1 - ALPHA2) <= 0 and h0 != h1:
            x0, x1 = np.log(ns[i]), np.log(ns[i + 1])
            frac = (h0 - ALPHA2) / (h0 - h1)
            return float(np.exp(x0 + frac * (x1 - x0)))
    return None


def main() -> None:
    root = Path(sys.argv[1])
    cell: dict[tuple[float, int], list[float]] = defaultdict(list)
    anchors: set[str] = set()
    for d in sorted(root.glob("results_*__N*_k*")):
        m = DIR_RE.match(d.name)
        mj = d / "inference_merged.json"
        if not (m and mj.exists()):
            continue
        vals = _hill_values(mj)
        if vals:
            cell[(_ktag_to_kappa(m["k"]), int(m["N"]))].extend(vals)
            anchors.add(m["anchor"])

    if not cell:
        print("no results found — run scripts/h20_116_criticality.sh first"); return

    kappas = sorted({k for k, _ in cell})
    Ns = sorted({n for _, n in cell})
    print(f"# exp 116 FSS — tail index hill(N). anchors={len(anchors)}  N∈{Ns}  κ∈{kappas}")
    print(f"# crossing hill=2 ⇔ tail exponent α=2 (infinite-variance boundary)\n")

    Ncs: dict[float, float] = {}
    for kap in kappas:
        present = [(n, cell[(kap, n)]) for n in Ns if cell.get((kap, n))]
        if len(present) < 2:
            print(f"κ={kap:.1f}: <2 N points — skip\n"); continue
        ns = np.array([n for n, _ in present], float)
        means = np.array([np.mean(v) for _, v in present])
        print(f"κ={kap:.1f}")
        print(f"  {'N':>7}{'hill':>8}{'95% CI':>18}{'n':>5}")
        for (n, v) in present:
            v = np.array(v)
            if len(v) >= 3:
                bs = [np.mean(RNG.choice(v, len(v), replace=True)) for _ in range(2000)]
                lo, hi = np.percentile(bs, [2.5, 97.5])
                ci = f"[{lo:.2f},{hi:.2f}]"
            else:
                ci = "(n<3)"
            flag = " <α=2" if v.mean() < ALPHA2 else ""
            print(f"  {n:>7}{v.mean():>8.2f}{ci:>18}{len(v):>5}{flag}")
        nc = _crossing(ns, means)
        Ncs[kap] = nc if nc is not None else float("nan")
        if nc is not None:
            order = np.argsort(ns)
            slope = np.polyfit(np.log(ns[order]), means[order], 1)[0]
            print(f"  → N_c(hill=2) ≈ {nc:,.0f}   (d hill/d logN ≈ {slope:.2f})")
        else:
            lohi = f"hill∈[{means.min():.2f},{means.max():.2f}]"
            side = "never reaches α=2 (no overshoot in ladder)" if means.min() > ALPHA2 \
                else "already <α=2 at smallest N (extend ladder DOWN)"
            print(f"  → no hill=2 crossing in N ladder: {lohi} — {side}")
        print()

    finite_ncs = {k: v for k, v in Ncs.items() if v == v}
    print("# verdict")
    if not finite_ncs:
        print("  hill does not cross 2 across the N ladder at any κ → extend the ladder; "
              "no critical N_c located yet.")
    else:
        vals = np.array(list(finite_ncs.values()))
        spread = (vals.max() - vals.min()) / vals.mean() if len(vals) > 1 else 0.0
        kdep = "κ-INDEPENDENT" if spread < 0.15 else f"κ-DEPENDENT (spread {spread:.0%})"
        print("  N_c crosses α=2 at: " + ", ".join(f"κ={k:.1f}:{v:,.0f}" for k, v in finite_ncs.items()))
        print(f"  → N_c is {kdep}.")
        if len(Ns) >= 4:
            print("  ladder has ≥4 N — fit hill=f((N−N_c)/N_c) collapse offline for the FSS figure;")
            print("  steep + κ-independent + localized N_c ⇒ CONSISTENT WITH emergent α<2 transition;")
            print("  shallow/wide ⇒ honest 'aggregate-flow crossover'.")
        else:
            print("  ladder <4 N — too sparse for a scaling-collapse claim (report crossover only).")


if __name__ == "__main__":
    main()
