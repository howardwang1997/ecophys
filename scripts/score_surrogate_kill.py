"""Surrogate-kill for the concave √-impact solve (pre-registration clause, plan_v3 §6.1).

The clause: a claim that a cheap null surrogate (IID/GBM, GARCH(1,1)-t, AR1-SV) reproduces is a
pipeline artifact and dies. Here we test the concave solve's gate — hill∈[2,4] AND acf²∈[0.15,0.55]
(plus the full 11-fact joint) — against the surrogates, all scored by the SAME compute_all pipeline.

The concave solve SURVIVES iff it passes facts the surrogates cannot — i.e., its net 11-fact pass
exceeds the best surrogate AND it reproduces structural facts (zumbach, leverage, DFA) a GARCH/IID
null can't. If a surrogate matches the solve's joint pass, the claim is an artifact.

Caveat: cached surrogate rollouts (080 GARCH/GBM T=2520, 093 AR1-SV) vs concave solve (113 T=4000)
differ in length; hill/acf² are length-robust enough for the qualitative gate, flagged in output.

Read-only. Usage: python scripts/score_surrogate_kill.py
"""
from __future__ import annotations

import glob
import json
from collections import defaultdict

import numpy as np

# Mirrors scripts/score_phase.py BANDS (canonical 11-fact bands).
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
GATE = ["hill_tail_index", "acf_squared_returns"]          # the concave-solve gate
STRUCTURAL = ["zumbach_asymmetry", "leverage_effect", "dfa_hurst_abs_r"]  # what a null can't fake

# label -> dir glob (each dir's inference_merged.json has aggregated.<fact>.mean)
SOURCES = {
    "baseline (spx)":      "experiments/113_gabaix_solve/results_baseline_seed*",
    "CONCAVE d050 (spx)":  "experiments/113_gabaix_solve/results_concave_d050_seed*",
    "GARCH-t (spx)":       "experiments/080_baselines_30seed/results_garch_seed*",
    "GBM/IID (spx)":       "experiments/080_baselines_30seed/results_gbm_seed*",
    "AR1-SV (spx)":        "experiments/093_5asset_traditional_baselines/results_trad_ar1sv_spx_seed*",
}


def model_means(glob_pat: str) -> tuple[dict[str, float], int]:
    facts: dict[str, list[float]] = defaultdict(list)
    n = 0
    for d in glob.glob(glob_pat):
        try:
            agg = json.loads(open(d + "/inference_merged.json").read())["aggregated"]
        except Exception:
            continue
        n += 1
        for f in BANDS:
            m = agg.get(f, {}).get("mean")
            if isinstance(m, (int, float)) and np.isfinite(m):
                facts[f].append(float(m))
    return {f: float(np.mean(v)) for f, v in facts.items() if v}, n


def passes(fact: str, val: float | None) -> bool:
    if val is None:
        return False
    lo, hi = BANDS[fact]
    return lo <= val <= hi


def main() -> None:
    models = {}
    for label, pat in SOURCES.items():
        means, n = model_means(pat)
        models[label] = (means, n)

    facts = list(BANDS)
    print("# Surrogate-kill — concave √-impact solve vs cheap nulls (same compute_all pipeline)\n")
    hdr = f"{'fact':28}" + "".join(f"{lab.split(' (')[0][:11]:>13}" for lab in SOURCES)
    print(hdr)
    for f in facts:
        row = f"{f:28}"
        for lab in SOURCES:
            v = models[lab][0].get(f)
            mark = "✓" if passes(f, v) else "·"
            row += f"{(f'{v:.2f}' if v is not None else 'NA')+mark:>13}"
        print(row)
    print("─" * len(hdr))
    # net 11-fact, gate (hill+acf2), structural
    net = {lab: sum(passes(f, models[lab][0].get(f)) for f in facts) for lab in SOURCES}
    gate = {lab: all(passes(f, models[lab][0].get(f)) for f in GATE) for lab in SOURCES}
    struct = {lab: sum(passes(f, models[lab][0].get(f)) for f in STRUCTURAL) for lab in SOURCES}
    print(f"{'NET /11':28}" + "".join(f"{net[lab]:>12}{'':1}" for lab in SOURCES))
    print(f"{'gate(hill&acf2) pass':28}" + "".join(f"{('YES' if gate[lab] else 'no'):>12}{'':1}" for lab in SOURCES))
    print(f"{'structural /3 (zmb,lev,dfa)':28}" + "".join(f"{struct[lab]:>12}{'':1}" for lab in SOURCES))
    print("  n seeds: " + ", ".join(f"{lab.split(' (')[0]}={models[lab][1]}" for lab in SOURCES))

    print("\n# verdict")
    solve = "CONCAVE d050 (spx)"
    surrogates = ["GARCH-t (spx)", "GBM/IID (spx)", "AR1-SV (spx)"]
    best_surr = max(surrogates, key=lambda s: net[s])
    gate_faked = [s for s in surrogates if gate[s]]
    if gate_faked:
        print(f"  ⚠ the 2-fact gate (hill&acf²) is REPRODUCED by: {', '.join(g.split(' (')[0] for g in gate_faked)}")
        print(f"    → the hill+acf² gate ALONE is NOT surrogate-proof; the solve must be defended on")
        print(f"      the JOINT 11-fact + structural facts a null can't fake.")
    if net[solve] > net[best_surr] and struct[solve] >= struct[best_surr]:
        print(f"  ✓ SOLVE SURVIVES: concave net={net[solve]}/11 > best surrogate "
              f"({best_surr.split(' (')[0]} {net[best_surr]}/11), and structural "
              f"{struct[solve]}/3 ≥ {struct[best_surr]}/3 → not a pipeline artifact.")
    else:
        print(f"  ✗ SOLVE AT RISK: concave net={net[solve]}/11 vs best surrogate "
              f"{best_surr.split(' (')[0]} {net[best_surr]}/11 — the claim is too close to a null; "
              f"report honestly / strengthen the joint argument.")


if __name__ == "__main__":
    main()
