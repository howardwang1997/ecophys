"""Score exp 113 — Gabaix mechanism solve. Per cell: mean hill / acf2 (the gate)
AND the LEARNED mechanism parameters ζ (mass exponent) and δ (impact concavity)
extracted from each checkpoint — the scientifically decisive readout: did the
soft_hill loss calibrate (ζ,δ) toward the GGPS inverse-cubic prediction (ζ≈1, δ≈0.5)?

Gate: a cell is a SOLVE iff hill ∈ [2,4] AND acf2 ∈ [0.15,0.55] vs baseline.

Usage: python scripts/score_gabaix.py experiments/113_gabaix_solve
"""

from __future__ import annotations

import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch

HILL_BAND = (2.0, 4.0)
ACF2_BAND = (0.15, 0.55)


def _cell(name: str) -> str:
    return re.sub(r"_seed\d+$", "", name[len("results_"):])


def _facts(p: Path) -> dict:
    d = json.loads(p.read_text()).get("aggregated", {})
    out = {}
    for k in ("hill_tail_index", "acf_squared_returns", "aggregational_gaussianity"):
        v = d.get(k)
        m = (v or {}).get("mean") if isinstance(v, dict) else v
        if m is not None and np.isfinite(m):
            out[k] = float(m)
    return out


def _learned_zd(ckpt: Path) -> tuple[float | None, float | None]:
    try:
        sd = torch.load(ckpt, map_location="cpu")["sim_state_dict"]
    except Exception:
        return None, None
    z = d = None
    for k, v in sd.items():
        if k.endswith("mass_log_zeta"):
            z = float(torch.exp(v.detach()))
        if k.endswith("impact_logit_delta"):
            d = float(torch.sigmoid(v.detach()))
    return z, d


def main() -> None:
    root = Path(sys.argv[1])
    cells: dict[str, dict[str, list]] = defaultdict(
        lambda: {"hill": [], "acf2": [], "agg": [], "zeta": [], "delta": []})
    for rd in sorted(root.glob("results_*")):
        mj = rd / "inference_merged.json"
        if not mj.exists():
            continue
        c = _cell(rd.name)
        fa = _facts(mj)
        if "hill_tail_index" not in fa:
            continue
        cells[c]["hill"].append(fa["hill_tail_index"])
        cells[c]["acf2"].append(fa.get("acf_squared_returns", np.nan))
        cells[c]["agg"].append(fa.get("aggregational_gaussianity", np.nan))
        z, d = _learned_zd(rd / "checkpoint.pt")
        if z is not None:
            cells[c]["zeta"].append(z)
        if d is not None:
            cells[c]["delta"].append(d)

    def m(xs):
        xs = [x for x in xs if x is not None and np.isfinite(x)]
        return (float(np.mean(xs)), float(np.std(xs) / max(1, len(xs) ** 0.5))) if xs else (float("nan"), float("nan"))

    base_hill = m(cells.get("baseline", {}).get("hill", []))[0] if "baseline" in cells else float("nan")
    print(f"# exp 113 concave-impact solve — baseline hill={base_hill:.3f} (overshoot)  "
          f"(target: thin to hill≈3; δ control, sqrt-law δ=0.5)\n")
    hdr = f"{'cell':24}{'n':>4}{'hill[2,4]':>11}{'acf2[.15,.55]':>14}{'ζ_learned':>11}{'δ_learned':>11}{'SOLVE':>7}"
    print(hdr)
    for c in sorted(cells, key=lambda c: -m(cells[c]["hill"])[0] if cells[c]["hill"] else 0):
        s = cells[c]
        hi, _ = m(s["hill"]); ac, _ = m(s["acf2"])
        z, _ = m(s["zeta"]); d, _ = m(s["delta"])
        hb = HILL_BAND[0] <= hi <= HILL_BAND[1]
        ab = ACF2_BAND[0] <= ac <= ACF2_BAND[1]
        solve = "✓" if (hb and ab) else ("hill" if not hb else "acf2")
        zs = f"{z:.3f}" if not math.isnan(z) else "  —"
        ds = f"{d:.3f}" if not math.isnan(d) else "  —"
        print(f"{c:24}{len(s['hill']):>4}{hi:>11.3f}{ac:>14.3f}{zs:>11}{ds:>11}{solve:>7}")
    print("\n  SOLVE = hill∈[2,4] AND acf2∈[.15,.55]. Confirm winner at 5-asset n=30 "
          "(Welch+Bonferroni vs baseline, NOT best-of-N).")
    print("  Decisive: (a) the hill(δ) sweep — which fixed δ lands α in [2,4] with acf2 kept; "
          "(b) does concave_learn's δ self-calibrate there? (ζ column blank — masses dropped.)")


if __name__ == "__main__":
    main()
