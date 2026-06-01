"""Score exp 112 Part B — the α scaling-curve diagnose.

Reads scaling/results_<seed>_<tag>/inference_merged.json (run_large output), groups by
scan family, averages across the anchor checkpoints, and applies the pre-registered
analysis:

  B1  hill(N) at ed_normalize=False — fit hill ≈ α_inf + c/N (linear in 1/N); report
      the thermodynamic-limit intercept α_inf (+CI) and the N where hill crosses 2.
  B1n hill(N) at ed_normalize=True  — CONTROL; should be ~flat (slope≈0) if the
      unnormalized aggregate-flow SNR is the tail mechanism.
  B2  hill(κ) AND acf2(κ) vs hawkes self-excitation — locate κ* where hill enters
      [2,4] and the κ-window where acf2 stays in band. Disjoint ⇒ Pareto coupling
      confirmed against the control parameter; overlap ⇒ a coupling-tuned solve.

Usage: python scripts/score_scaling.py experiments/112_tail_clamp/scaling
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HILL_BAND = (2.0, 4.0)
ACF2_BAND = (0.15, 0.55)


def _facts(p: Path) -> dict[str, float]:
    d = json.loads(p.read_text()).get("aggregated", {})
    out = {}
    for k in ("hill_tail_index", "acf_squared_returns", "aggregational_gaussianity"):
        v = d.get(k)
        m = (v or {}).get("mean") if isinstance(v, dict) else v
        if m is not None and np.isfinite(m):
            out[k] = float(m)
    return out


def _parse(tagdir: str):
    # results_seed0_B1_N_n250  /  results_seed2_B1n_Nnorm_n5000  /  results_seed1_B2_hk0.3
    name = tagdir[len("results_"):]
    m = re.match(r"(seed\d+)_(.+)", name)
    if not m:
        return None
    _, tag = m.groups()
    if tag.startswith("B1_N_n"):
        return ("B1", float(tag[len("B1_N_n"):]))
    if tag.startswith("B1n_Nnorm_n"):
        return ("B1n", float(tag[len("B1n_Nnorm_n"):]))
    if tag.startswith("B2_hk"):
        return ("B2", float(tag[len("B2_hk"):]))
    return None


def _agg(points: dict[float, list[float]]):
    xs = sorted(points)
    mean = np.array([np.mean(points[x]) for x in xs])
    sem = np.array([np.std(points[x]) / max(1, len(points[x]) ** 0.5) for x in xs])
    return np.array(xs, float), mean, sem


def main() -> None:
    root = Path(sys.argv[1])
    fam: dict[str, dict[str, defaultdict]] = {
        f: {"hill": defaultdict(list), "acf2": defaultdict(list), "agg": defaultdict(list)}
        for f in ("B1", "B1n", "B2")
    }
    n = 0
    for d in sorted(root.glob("results_*")):
        mj = d / "inference_merged.json"
        if not mj.exists():
            continue
        parsed = _parse(d.name)
        if not parsed:
            continue
        f, x = parsed
        fa = _facts(mj)
        if "hill_tail_index" in fa:
            fam[f]["hill"][x].append(fa["hill_tail_index"])
            fam[f]["acf2"][x].append(fa.get("acf_squared_returns", np.nan))
            fam[f]["agg"][x].append(fa.get("aggregational_gaussianity", np.nan))
            n += 1
    print(f"# exp 112 scaling — {n} inference runs under {root}\n")

    # ── B1 / B1n: hill(N) ─────────────────────────────────────────────
    for f, label in [("B1", "B1  hill(N) ed_norm=FALSE (baseline)"),
                     ("B1n", "B1n hill(N) ed_norm=TRUE  (control)")]:
        if not fam[f]["hill"]:
            continue
        N, hill, sem = _agg(fam[f]["hill"])
        print(f"## {label}")
        print(f"{'N':>8}{'hill':>9}{'±sem':>8}")
        for x, h, s in zip(N, hill, sem):
            print(f"{int(x):>8}{h:>9.3f}{s:>8.3f}")
        # linear fit hill = α_inf + c/N  (thermodynamic limit = intercept at 1/N→0)
        inv = 1.0 / N
        A = np.vstack([inv, np.ones_like(inv)]).T
        (c, a_inf), res, *_ = np.linalg.lstsq(A, hill, rcond=None)
        # crude CI on intercept via residual std
        dof = max(1, len(N) - 2)
        rstd = float(np.sqrt((res[0] / dof))) if len(res) else float("nan")
        cross = None
        for i in range(len(N) - 1):
            if (hill[i] - 2.0) * (hill[i + 1] - 2.0) < 0:  # straddles 2
                t = (2.0 - hill[i]) / (hill[i + 1] - hill[i])
                cross = N[i] * (N[i + 1] / N[i]) ** t
        print(f"  → fit hill ≈ {a_inf:.3f} + {c:.1f}/N   (α_inf intercept ≈ {a_inf:.3f}, "
              f"resid σ≈{rstd:.3f}, slope c={c:.1f})")
        if f == "B1":
            verdict = ("α_inf<2 ⇒ INTRINSICALLY infinite-variance in thermodynamic limit"
                       if a_inf < 2 else "α_inf≥2 ⇒ finite-variance limit (overshoot is finite-N)")
            print(f"  → {verdict}")
            print(f"  → hill crosses 2 near N≈{int(cross) if cross else 'n/a (no straddle in range)'}")
        else:
            print(f"  → control slope c={c:.1f} (≈0 ⇒ √N-normalization flattens the tail "
                  f"⇒ aggregate-flow SNR confirmed as the mechanism)")
        print()

    # ── B2: hill(κ) and acf2(κ) ───────────────────────────────────────
    if fam["B2"]["hill"]:
        K, hill, hsem = _agg(fam["B2"]["hill"])
        _, acf2, asem = _agg(fam["B2"]["acf2"])
        print("## B2  hill(κ_hawkes) and acf2(κ) — the Pareto coupling vs feedback strength")
        print(f"{'κ_hawkes':>9}{'hill':>9}{'in[2,4]':>9}{'acf2':>9}{'in-band':>9}")
        hill_ok, acf2_ok = [], []
        for x, h, a in zip(K, hill, acf2):
            hb = HILL_BAND[0] <= h <= HILL_BAND[1]
            ab = ACF2_BAND[0] <= a <= ACF2_BAND[1]
            hill_ok.append(hb); acf2_ok.append(ab)
            print(f"{x:>9.2f}{h:>9.3f}{('Y' if hb else '·'):>9}{a:>9.3f}{('Y' if ab else '·'):>9}")
        both = [round(float(k), 3) for k, hb, ab in zip(K, hill_ok, acf2_ok) if hb and ab]
        hk = [round(float(k), 3) for k, hb in zip(K, hill_ok) if hb]
        ak = [round(float(k), 3) for k, ab in zip(K, acf2_ok) if ab]
        print(f"  → hill∈[2,4] at κ ∈ {hk}")
        print(f"  → acf2 in-band at κ ∈ {ak}")
        if both:
            print(f"  → OVERLAP at κ ∈ {both}: a coupling-tuned operating point exists "
                  f"(knob-solve) → promote to 5-asset n=30")
        else:
            print("  → DISJOINT: no κ satisfies both ⇒ Pareto coupling CONFIRMED against the "
                  "control parameter (strongest diagnose form)")


if __name__ == "__main__":
    main()
