#!/usr/bin/env python3
"""exp 125/126 — G-A rigor CIs + the coherent-vs-incoherent contrast table.

Reads the per-arm windowed_hill_report.json (steady/post-shock alpha_ED) and the per-seed
inference_rank_*.json facts (hill_tail_index, acf_squared_returns). Emits, per asset:
  - control / kick6 / temp* / liq* steady alpha_ED with a normal-approx 95% CI (mean +/- 1.96 std/sqrt n),
  - post-shock min alpha_ED and the dip vs control,
  - the coherent (state_kick) vs incoherent (temperature / heavy-noise) contrast on (tail, clustering):
    coherent driving should raise BOTH tail-heaviness and ACF2(r^2); incoherent should raise neither.

Usage:  python scripts/aggregate_atlas_cis.py --exp DIR [DIR2 ...]
Writes: <first exp dir>/aggregate_atlas_cis.json
"""
import argparse, glob, json, os, math
from collections import defaultdict

ASSETS = ("spx", "ndx", "btcusdt", "gold", "eurusd")


def _arm(path):  # .../results_<arm>/windowed_hill_report.json  OR .../results_<arm>/<tag>/inference_rank_*.json
    parts = path.split(os.sep)
    for p in parts:
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


def split_asset(arm):
    for a in ASSETS:
        if arm.startswith(a + "_"):
            return a, arm[len(a) + 1:]
    return None, arm


def steady_postmin(w):
    if not w:
        return None
    centers = [int(c) for c in w["centers"]]
    aED = w["alpha_ED_mean"]
    aSD = w.get("alpha_ED_std", [0] * len(aED))
    shock = int(w.get("shock_step", 3000))
    n = int(w.get("n_rollouts", 0)) or 1
    steady = [(m, s) for c, m, s in zip(centers, aED, aSD) if c >= 500 and c < shock]
    if not steady:
        steady = [(m, s) for c, m, s in zip(centers, aED, aSD) if c >= 500]
    post = [(c, m) for c, m in zip(centers, aED) if shock <= c < shock + 1500]
    mean = sum(m for m, _ in steady) / len(steady)
    sd = sum(s for _, s in steady) / len(steady)
    ci = 1.96 * sd / math.sqrt(n)
    pm = min(post, key=lambda x: x[1]) if post else (None, None)
    return {"steady_alphaED": round(mean, 4), "ci95": round(ci, 4), "n": n,
            "postmin_alphaED": round(pm[1], 4) if pm[1] is not None else None,
            "postmin_center": pm[0]}


def fmean(xs):
    return sum(xs) / len(xs) if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", nargs="+", required=True)
    args = ap.parse_args()
    WIN = read_windowed(args.exp)
    FACTS = read_facts(args.exp)

    rigor = defaultdict(dict)
    for arm, w in WIN.items():
        a, suf = split_asset(arm)
        if a is None:
            continue
        sp = steady_postmin(w)
        if sp:
            rigor[a][suf] = sp
    # dip vs control
    for a, arms in rigor.items():
        c = arms.get("control", {}).get("steady_alphaED")
        for suf, rec in arms.items():
            pre = rec.get("steady_alphaED")
            pm = rec.get("postmin_alphaED")
            rec["dip_pre_minus_postmin"] = round(pre - pm, 4) if (pre is not None and pm is not None) else None

    # coherent vs incoherent contrast (tail = hill_tail_index fact; clustering = acf_squared_returns)
    def cell(arm):
        h = FACTS.get(arm, {}).get("hill_tail_index")
        c = FACTS.get(arm, {}).get("acf_squared_returns")
        return {"hill_tail": round(fmean(h), 4) if h else None,
                "acf2_r2": round(fmean(c), 4) if c else None,
                "n": len(h) if h else 0}
    contrast = {}
    for a in ASSETS:
        row = {k: cell(f"{a}_{k}") for k in ("control", "kick6", "temp5", "liq5", "levy15")}
        contrast[a] = row

    out = {"rigor_steady_postshock": rigor, "coherent_vs_incoherent": contrast,
           "note": ("CI = normal-approx 95% (mean +-1.96 std/sqrt n) from windowed mean/std; "
                    "coherent kick6 should raise BOTH |tail| (hill DOWN) and clustering (acf2 UP), "
                    "incoherent temp5/levy15 neither.")}
    outp = os.path.join(args.exp[0], "aggregate_atlas_cis.json")
    json.dump(out, open(outp, "w"), indent=1)
    print("wrote", outp)
    for a in ASSETS:
        if a in rigor:
            c = rigor[a].get("control", {})
            k = rigor[a].get("kick6", {})
            print(f"  {a:<8} control steady={c.get('steady_alphaED')}±{c.get('ci95')} (n={c.get('n')})  "
                  f"kick6 postmin={k.get('postmin_alphaED')} dip={k.get('dip_pre_minus_postmin')}")


if __name__ == "__main__":
    main()
