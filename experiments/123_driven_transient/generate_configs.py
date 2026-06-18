"""Generate exp 123 driven-transient sim configs.

Each config = the asset's trained concave_d050 simulator config (the checkpoint we drive)
+ `log_raw_excess_demand: true` so the logged excess_demand is the raw pre-impact ζ_ED tail.
Doses / arms / control / shock-step are NOT separate configs — they are `run_large --shock-*`
CLI variations on the SAME config (see scripts/gpu_exp123_stage1.sh).

  conda run -n ecophys python experiments/123_driven_transient/generate_configs.py
"""
from __future__ import annotations
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/123_driven_transient"

# asset → source concave_d050 config (spx from exp 113; the rest from exp 114)
SRC = {
    "spx":     "experiments/113_gabaix_solve/config_concave_d050_seed0.yaml",
    "ndx":     "experiments/114_concave_confirm/config_ndx_concave_d050_seed0.yaml",
    "gold":    "experiments/114_concave_confirm/config_gold_concave_d050_seed0.yaml",
    "eurusd":  "experiments/114_concave_confirm/config_eurusd_concave_d050_seed0.yaml",
    "btcusdt": "experiments/114_concave_confirm/config_btcusdt_concave_d050_seed0.yaml",
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for asset, src in SRC.items():
        p = ROOT / src
        if not p.exists():
            print(f"  [skip] {asset}: source missing ({src})")
            continue
        cfg = yaml.safe_load(p.read_text())
        kw = cfg["simulator"].setdefault("price_formation_kwargs", {})
        kw["log_raw_excess_demand"] = True          # P1: log the raw pre-impact ζ_ED tail
        cfg["simulator"]["price_formation_kwargs"] = kw
        out = OUT / f"config_{asset}.yaml"
        out.write_text(yaml.safe_dump(cfg, sort_keys=True))
        print(f"  wrote {out.relative_to(ROOT)}  (from {Path(src).name})")


if __name__ == "__main__":
    main()
