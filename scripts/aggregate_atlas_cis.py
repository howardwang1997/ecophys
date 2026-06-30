#!/usr/bin/env python3
"""exp 125/126 — G-A rigor CIs + the full controllability-atlas surface + coherent-vs-incoherent contrast.

Reads per-arm windowed_hill_report.json (steady/post-shock alpha_ED) and per-seed inference_rank_*.json
facts (hill_tail_index, acf_squared_returns). Emits, per asset:
  - rigor: control / kick6 steady alpha_ED with normal-approx 95% CI, post-shock min, dip vs control;
  - atlas control surface: every (driver in {temp,liq}, magnitude, duration) -> pre / postmin / dip
    (arm dirs are named results_<asset>_<temp|liq><mag>_d<DUR>);
  - the coherent (state_kick) vs incoherent (temperature / heavy-noise) contrast on (tail, clustering).

Usage:  python scripts/aggregate_atlas_cis.py --exp DIR [DIR2 ...]
Writes: <first exp dir>/aggregate_atlas_cis.json
"""
import argparse, glob, json, os, math, re
from collections import defaultdict

ASSETS = ("spx", "ndx", "btcusdt", "gold", "eurusd")
ATLAS_RE = re.compile(r"^(temp|liq)([\d.]+)_d(\d+)$")
KICK_RE = re.compile(r"^kick([\d.]+)$")


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
            for entry in (d if isinstance(d, list) else [d]):
                for fn, v in entry.get("facts", {}).items():
                    if isinstance(v, dict) and v.get("estimate") is not None:
                        out[arm][fn].append(v["estimate"])
    return out


def split_asset(arm):
    for a in ASSETS:
        if arm and arm.startswith(a + "_"):
            return a, arm[len(a) + 1:]
    return None, arm


def steady_postmin(w):
    centers = [int(c) for c in w["centers"]]
    aED = w["alpha_ED_mean"]; aSD = w.get("alpha_ED_std", [0] * len(aED))
    shock = int(w.get("shock_step", 3000)); n = int(w.get("n_rollouts", 0)) or 1
    steady = [(m, s) for c, m, s in zip(centers, aED, aSD) if 500 <= c < shock] or \
             [(m, s) for c, m, s in zip(centers, aED, aSD) if c >= 500]
    post = [(c, m) for c, m in zip(centers, aED) if shock <= c < shock + 1500]
    mean = sum(m for m, _ in steady) / len(steady)
    sd = sum(s for _, s in steady) / len(steady)
    pm = min(post, key=lambda x: x[1]) if post else (None, None)
    return {"steady_alphaED": round(mean, 4), "ci95": round(1.96 * sd / math.sqrt(n), 4), "n": n,
            "pre_alphaED": round(mean, 4),
            "postmin_alphaED": round(pm[1], 4) if pm[1] is not None else None,
            "dip": round(mean - pm[1], 4) if pm[1] is not None else None}


def fmean(xs):
    return round(sum(xs) / len(xs), 4) if xs else None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--exp", nargs="+", required=True)
    args = ap.parse_args()
    WIN = read_windowed(args.exp); FACTS = read_facts(args.exp)

    rigor = defaultdict(dict)
    atlas = defaultdict(lambda: defaultdict(dict))   # asset -> driver -> "mag{m}_dur{d}" -> rec
    for arm, w in WIN.items():
        a, suf = split_asset(arm)
        if a is None:
            continue
        m = ATLAS_RE.match(suf)
        if m:
            atlas[a][m.group(1)][f"mag{m.group(2)}_dur{m.group(3)}"] = steady_postmin(w)
        elif suf == "control" or KICK_RE.match(suf):
            rigor[a][suf] = steady_postmin(w)

    def cell(arm):
        h = FACTS.get(arm, {}).get("hill_tail_index"); c = FACTS.get(arm, {}).get("acf_squared_returns")
        return {"hill_tail": fmean(h), "acf2_r2": fmean(c), "n": len(h) if h else 0}
    contrast = {a: {k: cell(f"{a}_{k}") for k in
                    ("control", "kick6", "temp5_d20", "liq5_d20", "levy15")} for a in ASSETS}

    out = {"rigor": rigor, "atlas_control_surface": atlas, "coherent_vs_incoherent": contrast,
           "note": ("CI = normal-approx 95% from windowed mean/std. atlas keyed by driver/mag/dur. "
                    "coherent kick6 should raise BOTH |tail| (hill DOWN) and clustering (acf2 UP); "
                    "incoherent temp/levy neither. dip = pre-shock steady minus post-shock min alpha_ED.")}
    outp = os.path.join(args.exp[0], "aggregate_atlas_cis.json")
    json.dump(out, open(outp, "w"), indent=1); print("wrote", outp)
    for a in ASSETS:
        if a in rigor:
            c = rigor[a].get("control", {}); k = rigor[a].get("kick6", {})
            nliq = sum(len(v) for v in [atlas[a].get("liq", {})]) if a in atlas else 0
            ntemp = len(atlas[a].get("temp", {})) if a in atlas else 0
            print(f"  {a:<8} ctrl={c.get('steady_alphaED')}±{c.get('ci95')}  kick6 dip={k.get('dip')}  "
                  f"atlas cells: temp={ntemp} liq={nliq}")


if __name__ == "__main__":
    main()
