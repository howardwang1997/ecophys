"""Score exp 116 — criticality probe. hill(κ) per system size N; locate κ_c (hill crosses 2);
test whether the transition SHARPENS with N (finite-size scaling = true critical point vs crossover).

Result dirs: results_<ckpt>__N<N>_k<kk>/inference_merged.json
Usage: python scripts/score_criticality.py experiments/116_criticality
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


def main() -> None:
    root = Path(sys.argv[1])
    # (N, kappa) -> list of hill
    grid: dict[tuple[int, float], list[float]] = defaultdict(list)
    for rd in sorted(root.glob("results_*__N*_k*")):
        mj = rd / "inference_merged.json"
        if not mj.exists():
            continue
        m = re.search(r"__N(\d+)_k(\d+)$", rd.name)
        if not m:
            continue
        N = int(m.group(1))
        kdig = m.group(2)
        kap = float(kdig[0] + "." + kdig[1:]) if len(kdig) > 1 else float(kdig)
        d = json.loads(mj.read_text()).get("aggregated", {})
        v = d.get("hill_tail_index")
        h = (v or {}).get("mean") if isinstance(v, dict) else v
        if h is not None and np.isfinite(h):
            grid[(N, kap)].append(float(h))

    Ns = sorted({N for N, _ in grid})
    kaps = sorted({k for _, k in grid})
    print("# exp 116 criticality — hill(κ) per N. Transition = hill crossing 2 (α<2 = overshoot).\n")
    hdr = f"{'κ':>6}" + "".join(f"{'hill@N=' + str(N):>14}" for N in Ns)
    print(hdr)
    crossings = {}
    slopes = {}
    for N in Ns:
        hs = [(k, float(np.mean(grid[(N, k)]))) for k in kaps if (N, k) in grid]
        # κ_c where hill crosses 2 (linear interp between bracketing points)
        kc = None
        for (k0, h0), (k1, h1) in zip(hs, hs[1:]):
            if (h0 - 2) * (h1 - 2) <= 0 and h0 != h1:
                kc = k0 + (k1 - k0) * (h0 - 2) / (h0 - h1)
                break
        crossings[N] = kc
        # local slope at the crossing (sharpness)
        if kc is not None and len(hs) >= 2:
            xs = np.array([k for k, _ in hs]); ys = np.array([h for _, h in hs])
            j = int(np.argmin(np.abs(xs - kc)))
            lo, hi = max(0, j - 1), min(len(xs) - 1, j + 1)
            slopes[N] = (ys[hi] - ys[lo]) / (xs[hi] - xs[lo] + 1e-9)
    for k in kaps:
        row = f"{k:>6.1f}"
        for N in Ns:
            row += f"{np.mean(grid[(N, k)]):>14.3f}" if (N, k) in grid else f"{'—':>14}"
        print(row)

    print("\n# critical point read")
    for N in Ns:
        kc = crossings[N]; sl = slopes.get(N)
        print(f"  N={N:<6} κ_c(hill=2) = {kc if kc is None else round(kc,3)}   "
              f"|dhill/dκ| at κ_c = {abs(sl):.2f}" if sl is not None else
              f"  N={N:<6} κ_c(hill=2) = {kc}")
    if len(Ns) >= 2 and all(slopes.get(N) is not None for N in Ns):
        s_small, s_large = abs(slopes[Ns[0]]), abs(slopes[Ns[-1]])
        sharpening = s_large > 1.3 * s_small
        kc_conv = (crossings[Ns[0]] is not None and crossings[Ns[-1]] is not None
                   and abs(crossings[Ns[0]] - crossings[Ns[-1]]) < 0.15)
        print(f"\n  FSS: transition sharpness N={Ns[0]}→{Ns[-1]}: {s_small:.2f} → {s_large:.2f} "
              f"({'SHARPENS' if sharpening else 'flat'});  κ_c converges: {kc_conv}")
        if sharpening and kc_conv:
            print("  ⇒ signature of a TRUE non-equilibrium critical point (Paper B fork: GO).")
        else:
            print("  ⇒ smooth crossover, not a sharp critical point (Paper B fork: thermo stays; "
                  "Paper A depth still valid as 'aggregate-flow-driven crossover').")
    print("\n  NOTE: a clean κ_c + scaling collapse warrants a finer κ grid near κ_c + a 3rd N.")


if __name__ == "__main__":
    main()
