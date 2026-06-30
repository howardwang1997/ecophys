#!/usr/bin/env python3
"""exp 125/126 — G-D1: tail vs volatility-clustering across the noise ablations + the trained-Levy point.

Two tables:
 (1) INFERENCE noise override (G-D1a, fixed trained dynamics): normal -> t -> levy arms, per asset:
     steady alpha_ED (windowed), hill_tail_index (fact), ACF2(r^2), conditional_kurtosis. Tests whether
     heavier *inference* bath noise installs a heavier stationary tail (it did NOT in exp 125) and at
     what clustering cost.
 (2) TRAINED heavy noise (G-D1b): baseline_tdf5 vs levy17/levy15 trained checkpoints (score arms) — the
     real Route-A Pareto point: does end-to-end heavy-noise *training* reach a heavy stationary tail, and
     does ACF2(r^2) / leverage degrade as it does?

Usage:  python scripts/score_noise_ablation.py --exp DIR [DIR2 ...]
Writes: <first exp dir>/noise_ablation_cost.json
"""
import argparse, glob, json, os
from collections import defaultdict

ASSETS = ("spx", "ndx", "btcusdt", "gold", "eurusd")
NOISE_ORDER = ("normal", "t5", "t3", "levy19", "levy17", "levy15")
TRAINED = ("baseline_tdf5", "levy17_spx_seed0", "levy17_spx_seed1", "levy15_spx_seed0")
FACTS_OF_INTEREST = ("hill_tail_index", "acf_squared_returns", "conditional_kurtosis",
                     "leverage_effect", "zumbach_asymmetry")


def _arm(path):
    for p in path.split(os.sep):
        if p.startswith("results_"):
            return p[len("results_"):]
    return None


def read_windowed(exp_dirs):
    out = {}
    for e in exp_dirs:
        for p in glob.glob(os.path.join(e, "results_*", "windowed_hill_report.json")):
            try:
                out[_arm(p)] = json.load(open(p))
            except Exception:
                pass
    return out


def read_facts(exp_dirs):
    out = defaultdict(lambda: defaultdict(list))
    for e in exp_dirs:
        for p in glob.glob(os.path.join(e, "results_*", "*", "inference_rank_*.json")):
            arm = _arm(p)
            try:
                d = json.load(open(p))
            except Exception:
                continue
            if isinstance(d, dict):
                d = [d]
            for entry in d:
                for fn, v in entry.get("facts", {}).items():
                    if isinstance(v, dict) and v.get("estimate") is not None:
                        out[arm][fn].append(v["estimate"])
    return out


def fmean(xs):
    return round(sum(xs) / len(xs), 4) if xs else None


def steady(w):
    if not w:
        return None
    centers = [int(c) for c in w["centers"]]
    aED = w["alpha_ED_mean"]
    shock = int(w.get("shock_step", 3000))
    s = [m for c, m in zip(centers, aED) if c >= 500 and c < shock] or \
        [m for c, m in zip(centers, aED) if c >= 500]
    return round(sum(s) / len(s), 4) if s else None


def row(arm, WIN, FACTS):
    r = {"steady_alphaED": steady(WIN.get(arm)),
         "n_seeds": len(FACTS.get(arm, {}).get("hill_tail_index", []))}
    for fn in FACTS_OF_INTEREST:
        r[fn] = fmean(FACTS.get(arm, {}).get(fn, []))
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", nargs="+", required=True)
    args = ap.parse_args()
    WIN = read_windowed(args.exp)
    FACTS = read_facts(args.exp)

    infer = {}
    for a in ASSETS:
        rows = {arm: row(f"{a}_{arm}", WIN, FACTS) for arm in NOISE_ORDER}
        if any(rows[arm]["steady_alphaED"] is not None or rows[arm]["hill_tail_index"] is not None
               for arm in rows):
            infer[a] = rows

    trained = {name: row(name, WIN, FACTS) for name in TRAINED}
    trained = {k: v for k, v in trained.items()
               if v["steady_alphaED"] is not None or v["hill_tail_index"] is not None}

    out = {"G-D1a_inference_noise": infer, "G-D1b_trained_noise": trained,
           "note": ("hill_tail_index is the full-rollout fact (lower=heavier). G-D1a: heavier inference "
                    "noise did NOT heavy the tail in exp125 (hill rose) and ACF2 fell (no Pareto trade). "
                    "G-D1b is the decisive end-to-end test: a heavy stationary tail (hill DOWN, ~3) with "
                    "ACF2/leverage degrading = the tails-XOR-dynamics Pareto point.")}
    outp = os.path.join(args.exp[0], "noise_ablation_cost.json")
    json.dump(out, open(outp, "w"), indent=1)
    print("wrote", outp)
    for a, rows in infer.items():
        print(f"  [G-D1a] {a}: " + "  ".join(
            f"{k}(aED={rows[k]['steady_alphaED']},hill={rows[k]['hill_tail_index']},acf2={rows[k]['acf_squared_returns']})"
            for k in ("normal", "levy15") if rows.get(k)))
    for name, r in trained.items():
        print(f"  [G-D1b] {name}: steady_aED={r['steady_alphaED']} hill={r['hill_tail_index']} "
              f"acf2={r['acf_squared_returns']} lev={r['leverage_effect']} (n={r['n_seeds']})")


if __name__ == "__main__":
    main()
