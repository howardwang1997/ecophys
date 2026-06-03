"""Score exp 115 — mechanism composition (concave √-impact + SV/leverage).

Gate G1: concave_sv_both (a) net > 5.96 (prior SOTA) — Welch+Bonferroni vs baseline; (b) lifts ≥1
of {leverage, zumbach, dfa} vs baseline; (c) KEEPS the tail (hill∈[2,4], acf2∈[.15,.55]).
Attribution: concave_sv_both − concave = the SV/dynamics leg; concave_sv_both − concave_sv_nolev =
the leverage channel; concave_sv_both − sv_both = the tail leg.

Usage: python scripts/score_composition.py experiments/115_composition
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

SOTA = 5.96
BANDS = {
    "hill_tail_index": (2, 4), "acf_squared_returns": (0.15, 0.55),
    "aggregational_gaussianity": (10, 200), "dfa_hurst_abs_r": (0.4, 0.8),
    "autocorr_returns": (-0.1, 0.1), "intermittency_fano": (1, 1e9),
    "leverage_effect": (-1, 0), "gain_loss_asymmetry": (0, 1e9),
    "volume_volatility_corr": (0.1, 1), "zumbach_asymmetry": (0, 1e9),
    "conditional_kurtosis": (0, 100),
}
DYN_FACTS = ["leverage_effect", "zumbach_asymmetry", "dfa_hurst_abs_r"]


def _vals(mj: Path) -> dict:
    agg = json.loads(mj.read_text()).get("aggregated", {})
    out = {}
    for k in BANDS:
        v = agg.get(k)
        m = (v or {}).get("mean") if isinstance(v, dict) else v
        out[k] = float(m) if (m is not None and np.isfinite(m)) else np.nan
    return out


def _load(root: Path, cell: str) -> list[dict]:
    return [_vals(d / "inference_merged.json") for d in sorted(root.glob(f"results_{cell}_seed*"))
            if (d / "inference_merged.json").exists()]


def _net(rows): return np.array([sum(1 for k, (lo, hi) in BANDS.items()
                                     if not np.isnan(r[k]) and lo <= r[k] <= hi) for r in rows])
def _rate(rows, k):
    lo, hi = BANDS[k]; xs = [r[k] for r in rows if not np.isnan(r[k])]
    return 100 * np.mean([lo <= x <= hi for x in xs]) if xs else float("nan")


def main() -> None:
    root = Path(sys.argv[1])
    cells = ["baseline", "concave", "sv_both", "concave_sv_both", "concave_sv_nolev"]
    data = {c: _load(root, c) for c in cells}
    bnet = _net(data["baseline"]) if data["baseline"] else np.array([])

    print(f"# exp 115 composition — beat-SOTA gate (prior SOTA={SOTA}).  Bonferroni m=4.\n")
    print(f"{'cell':20}{'n':>4}{'net':>7}{'95%CI':>14}{'p_vs_base':>11}{'>SOTA':>7}")
    for c in cells:
        if not data[c]:
            print(f"{c:20}{'(missing)':>11}"); continue
        net = _net(data[c]); mu = net.mean(); sem = net.std() / max(1, len(net) ** 0.5)
        p = stats.ttest_ind(net, bnet, equal_var=False)[1] if len(bnet) and c != "baseline" else float("nan")
        ps = f"{p:.4f}{'*' if (p < 0.0125) else ''}" if not np.isnan(p) else "  —"
        sota = "✓" if mu > SOTA else ""
        print(f"{c:20}{len(net):>4}{mu:>7.2f}{f'[{mu-1.96*sem:.2f},{mu+1.96*sem:.2f}]':>14}{ps:>11}{sota:>7}")

    print("\n# per-fact in-band % — does composition lift the DISJOINT dynamics floors w/o losing tails?")
    show = ["hill_tail_index", "acf_squared_returns", "aggregational_gaussianity"] + DYN_FACTS
    print(f"{'fact':26}" + "".join(f"{c.replace('concave','cv').replace('_sv','+sv'):>12}" for c in cells))
    for k in show:
        line = f"{k:26}"
        for c in cells:
            line += f"{_rate(data[c], k):>12.0f}" if data[c] else f"{'—':>12}"
        print(line)

    hero = data.get("concave_sv_both")
    if hero:
        hmu = _net(hero).mean(); htail = _rate(hero, "hill_tail_index"); hacf = _rate(hero, "acf_squared_returns")
        lifted = [k for k in DYN_FACTS if _rate(hero, k) - _rate(data["baseline"], k) >= 10]
        tail_kept = htail >= 50 and hacf >= 50
        print(f"\n  HERO concave_sv_both: net={hmu:.2f}  tail-kept={tail_kept} "
              f"(hill {htail:.0f}%, acf2 {hacf:.0f}%)  dynamics-lifted={lifted or 'none'}")
        g1 = hmu > SOTA and tail_kept and bool(lifted)
        print(f"  GATE G1 (net>{SOTA} AND tail kept AND ≥1 dynamics floor lifted): "
              f"{'✓ PASS → 5-asset n=30 confirm (no best-of-N)' if g1 else '✗ — claim stays method+universality, NOT +SOTA'}")


if __name__ == "__main__":
    main()
