"""Test the tail-transfer prediction alpha = zeta/delta  (=> Hill ∝ 1/δ, and Hill·δ ≈ const = ζ_ED)
against the existing δ-grid Hill means. Compares to the current linear fit."""
import json, re
from collections import defaultdict
from pathlib import Path
import numpy as np

ASSETS = ["spx", "ndx", "gold", "eurusd", "btcusdt"]
exp = Path("experiments")

def hill(d):
    a = json.loads((d/"inference_merged.json").read_text()).get("aggregated",{})
    v = a.get("hill_tail_index"); m = v.get("mean") if isinstance(v,dict) else v
    return float(m) if m is not None and np.isfinite(m) else np.nan

pts = defaultdict(lambda: defaultdict(list))
def add(asset, delta, d):
    if (d/"inference_merged.json").exists():
        h = hill(d)
        if not np.isnan(h): pts[asset][delta].append(h)

for d in (exp/"113_gabaix_solve").glob("results_concave_d*_seed*"):
    m=re.match(r"results_concave_d(\d{3})_seed\d+$",d.name)
    if m: add("spx", int(m.group(1))/100, d)
for d in (exp/"114_concave_confirm").glob("results_*_concave_d*_seed*"):
    m=re.match(r"results_(\w+?)_concave_d(\d{3})_seed\d+$",d.name)
    if m: add(m.group(1), int(m.group(2))/100, d)
for d in (exp/"118_delta_grid").glob("*/results_s*_concave_d*"):
    m=re.match(r"results_s\d+_(\w+?)_concave_d(\d{3})$",d.name)
    if m: add(m.group(1), int(m.group(2))/100, d)

print(f"{'asset':8}{'δ: meanHill (Hill·δ)':52}{'lin r²':>8}{'inv r²':>8}{'ζ=Hill·δ':>11}{'CV%':>7}{'δ*=ζ/3':>9}")
for a in ASSETS:
    cells = pts.get(a,{})
    if len(cells)<3: 
        print(f"{a:8}(<3 δ)"); continue
    ds = np.array(sorted(cells))
    hm = np.array([np.mean(cells[d]) for d in ds])
    # linear fit Hill = p0 + p1 δ
    p = np.polyfit(ds, hm, 1); pred=np.polyval(p,ds)
    r2_lin = 1 - np.sum((hm-pred)**2)/np.sum((hm-hm.mean())**2)
    # inverse fit Hill = c/δ  (1-param, least squares on c): c = sum(hm/δ * 1)/sum(1/δ²)... do proper OLS through basis 1/δ
    x = 1/ds
    c = np.sum(x*hm)/np.sum(x*x)             # OLS Hill = c·(1/δ)
    predi = c*x
    r2_inv = 1 - np.sum((hm-predi)**2)/np.sum((hm-hm.mean())**2)
    prod = hm*ds                              # should be ≈ const = ζ if transfer law holds
    zeta = prod.mean(); cv = 100*prod.std()/prod.mean()
    desc = " ".join(f"{d:.2f}:{h:.2f}({h*d:.2f})" for d,h in zip(ds,hm))
    print(f"{a:8}{desc:52}{r2_lin:>8.2f}{r2_inv:>8.2f}{zeta:>11.3f}{cv:>7.1f}{zeta/3:>9.3f}")
print("\n transfer law predicts: Hill·δ ≈ const (=ζ_ED) across the grid, inv r² ≥ lin r², δ*≈0.5 ⟺ ζ_ED≈1.5")
