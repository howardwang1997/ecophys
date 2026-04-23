"""Fit GARCH(1,1) to each real dataset, generate synthetic returns, and
compare stylized facts against (a) the real data, (b) the Lux-Marchesi
1999 baseline from experiment 001.

Outputs:
  results/garch_fit_params.json          — fitted (ω, α, β, ν) per dataset
  results/garch_stylized_facts.json      — stylized facts on simulated returns
  results/three_way_comparison.md        — side-by-side comparison table
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ecomd.baselines.garch import GARCH11
from ecomd.eval.stylized_facts import compute_all, log_returns_from_prices

log = logging.getLogger("garch_baseline")

REPO = Path(__file__).resolve().parents[2]
RAW_DIR = REPO / "data" / "raw"
REF_RESULTS = REPO / "experiments" / "000_reference_values" / "results"
LM_RESULTS = REPO / "experiments" / "001_lux_marchesi_baseline" / "results"
OUT = Path(__file__).parent / "results"


DATASETS = [
    ("spx",     "2015-2026_daily", "yfinance",  "^GSPC"),
    ("spy",     "2015-2026_daily", "yfinance",  "SPY"),
    ("btcusdt", "2024Q1_1m",       "binance",   "BTCUSDT"),
    ("ethusdt", "2024Q1_1m",       "binance",   "ETHUSDT"),
]


# ─── Data loading ──────────────────────────────────────────────────────


def _read_yfinance(symbol: str) -> pd.DataFrame:
    root = RAW_DIR / "yfinance" / "interval=1d" / f"symbol={symbol}"
    frames = [pd.read_parquet(p) for p in sorted(root.glob("year=*.parquet"))]
    return pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)


def _read_binance(symbol: str) -> pd.DataFrame:
    root = RAW_DIR / "binance" / "market=spot" / "interval=1m" / f"symbol={symbol}"
    frames = [pd.read_parquet(p) for p in sorted(root.rglob("month=*.parquet"))]
    return pd.concat(frames, ignore_index=True).sort_values("open_time").reset_index(drop=True)


def _returns_for(dataset: str, source: str, symbol: str) -> np.ndarray:
    if source == "yfinance":
        df = _read_yfinance(symbol)
        col = "adjusted_close" if "adjusted_close" in df.columns else "close"
        return log_returns_from_prices(df[col].astype(float).to_numpy())
    elif source == "binance":
        df = _read_binance(symbol)
        return log_returns_from_prices(df["close"].astype(float).to_numpy())
    raise AssertionError(source)


# ─── Fit + simulate ────────────────────────────────────────────────────


def _fit_and_simulate(name: str, real_returns: np.ndarray,
                      n_realizations: int, n_steps: int,
                      dist: str = "t") -> dict[str, Any]:
    log.info("fitting GARCH(1,1)-%s on %s (n=%d)", dist, name, real_returns.size)
    fitted = GARCH11.fit(real_returns, dist=dist)
    log.info("  fitted: %s", fitted)

    # Run realisations
    realisations = []
    for seed in range(n_realizations):
        r = fitted.simulate(n_steps=n_steps, seed=seed)
        facts = compute_all(r, volume=None)
        realisations.append({
            "seed": seed,
            "results": {k: asdict(v) for k, v in facts.items()},
            "summary": {
                "std": float(r.std()),
                "min": float(r.min()),
                "max": float(r.max()),
            },
        })
    agg = _aggregate(realisations)
    return {
        "dataset": name,
        "fit_params": {
            "omega": fitted.params.omega,
            "alpha": fitted.params.alpha,
            "beta": fitted.params.beta,
            "nu": fitted.params.nu,
            "mean": fitted.params.mean,
            "scale": fitted.params.scale,
            "alpha_plus_beta": fitted.params.alpha + fitted.params.beta,
        },
        "realisations": realisations,
        "aggregated": agg,
    }


def _aggregate(runs: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    metric_names = set()
    for run in runs:
        metric_names.update(run["results"].keys())
    out: dict[str, dict[str, float]] = {}
    for m in sorted(metric_names):
        vals = [run["results"][m]["estimate"] for run in runs if m in run["results"]]
        vals = [v for v in vals if isinstance(v, (int, float)) and np.isfinite(v)]
        if vals:
            out[m] = {"mean": float(np.mean(vals)), "std": float(np.std(vals)), "n": len(vals)}
    return out


# ─── Reference loading ─────────────────────────────────────────────────


def _load_real_reference(dataset: str, period: str) -> dict[str, float]:
    path = REF_RESULTS / f"stylized_facts_{dataset}_{period}.json"
    if not path.is_file():
        return {}
    with path.open() as f:
        payload = json.load(f)
    return {name: res["estimate"] for name, res in payload["results"].items()}


def _load_lm_aggregate() -> dict[str, dict[str, float]]:
    path = LM_RESULTS / "lux_marchesi_stylized_facts.json"
    if not path.is_file():
        return {}
    with path.open() as f:
        runs = json.load(f)
    # Extract aggregated mean/std per metric
    metric_names: set[str] = set()
    for r in runs:
        metric_names.update(r["results"].keys())
    out: dict[str, dict[str, float]] = {}
    for m in metric_names:
        vals = []
        for r in runs:
            if m in r["results"]:
                e = r["results"][m].get("estimate")
                if isinstance(e, (int, float)) and np.isfinite(e):
                    vals.append(e)
        if vals:
            out[m] = {"mean": float(np.mean(vals)), "std": float(np.std(vals))}
    return out


# ─── Main ──────────────────────────────────────────────────────────────


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    OUT.mkdir(parents=True, exist_ok=True)

    n_realizations = 10
    n_steps = 20_000

    fits: list[dict[str, Any]] = []
    for name, period, source, symbol in DATASETS:
        real_r = _returns_for(name, source, symbol)
        fit = _fit_and_simulate(name, real_r, n_realizations=n_realizations, n_steps=n_steps, dist="t")
        fits.append({**fit, "period": period})

    # Dump raw
    (OUT / "garch_stylized_facts.json").write_text(json.dumps(fits, indent=2))
    # Compact fit params
    (OUT / "garch_fit_params.json").write_text(json.dumps(
        [{"dataset": f["dataset"], "period": f["period"], **f["fit_params"]} for f in fits], indent=2
    ))

    # ── Build 3-way comparison table ──
    lm_agg = _load_lm_aggregate()
    rows = [
        ("#1 ACF(r)",            "autocorr_returns",          "<0.05"),
        ("#2 α Hill",            "hill_tail_index",           "[3, 5]"),
        ("#3 skew",              "gain_loss_asymmetry",       "<0 daily equity"),
        ("#4 Δκ agg",            "aggregational_gaussianity", ">0"),
        ("#5 Fano",              "intermittency_fano",        ">1"),
        ("#6 ⟨ACF(r²)⟩",        "acf_squared_returns",       ">0.05"),
        ("#7 κ GARCH-std",       "conditional_kurtosis",      ">0, <uncond"),
        ("#8 H DFA|r|",          "dfa_hurst_abs_r",           "[0.55, 0.80]"),
        ("#9 ΣLev",              "leverage_effect",           "<0 daily"),
        ("#10 corr(V,|r|)",      "volume_volatility_corr",    "[0.2, 0.6]"),
        ("#11 Zumbach D",        "zumbach_asymmetry",         ">0 indices"),
    ]

    lines: list[str] = []
    lines.append("# Three-way comparison: Real data / Lux-Marchesi 1999 / GARCH(1,1)-t")
    lines.append("")
    lines.append(f"GARCH: fitted per-dataset, {n_realizations} × {n_steps} step synthetic realizations, t-innovations.")
    lines.append("Lux-Marchesi: single parameter set (paper defaults), 10 × 20k realisations (from experiment 001).")
    lines.append("")
    lines.append("## Fitted GARCH(1,1)-t parameters")
    lines.append("")
    lines.append("| dataset | ω | α | β | α+β | ν |")
    lines.append("|---|---|---|---|---|---|")
    for f in fits:
        fp = f["fit_params"]
        nu_str = f"{fp['nu']:.2f}" if fp["nu"] is not None else "—"
        lines.append(f"| {f['dataset']} | {fp['omega']:.2e} | {fp['alpha']:.3f} | {fp['beta']:.3f} | {fp['alpha_plus_beta']:.3f} | {nu_str} |")
    lines.append("")
    lines.append("")

    # For each dataset, produce a table comparing real vs GARCH
    for f in fits:
        name = f["dataset"]
        period = f["period"]
        real = _load_real_reference(name, period)
        agg_garch = f["aggregated"]
        lines.append(f"## {name} ({period})")
        lines.append("")
        lines.append("| metric | expected | real | GARCH(1,1)-t | LM99 (asset-agnostic) |")
        lines.append("|---|---|---|---|---|")
        for label, key, expected in rows:
            real_v = real.get(key)
            g = agg_garch.get(key)
            lm = lm_agg.get(key)
            real_s = f"{real_v:+.3f}" if isinstance(real_v, (int, float)) and np.isfinite(real_v) else "—"
            g_s = f"{g['mean']:+.3f} ± {g['std']:.3f}" if g else "—"
            lm_s = f"{lm['mean']:+.3f} ± {lm['std']:.3f}" if lm else "—"
            lines.append(f"| {label} | {expected} | {real_s} | {g_s} | {lm_s} |")
        lines.append("")

    # Overall scoreboard: how many facts does each model reproduce for each dataset?
    lines.append("## Scoreboard — how many facts each simulator matches (loose tolerance)")
    lines.append("")
    lines.append("Counts metrics where the simulator's mean lands within broad expected range.")
    lines.append("Note: LM99 has no per-asset fit — it's an asset-agnostic model run with paper defaults.")
    lines.append("")
    lines.append("| metric check | GARCH scores (per dataset) | LM99 score (once) |")
    lines.append("|---|---|---|")

    def _score(m: float | None, key: str) -> bool:
        if m is None or not np.isfinite(m):
            return False
        if key == "autocorr_returns":
            return m < 0.08
        elif key == "hill_tail_index":
            return 2.0 <= m <= 6.0
        elif key == "gain_loss_asymmetry":
            return m < -0.05
        elif key == "aggregational_gaussianity":
            return m > 0
        elif key == "intermittency_fano":
            return m > 1.0
        elif key == "acf_squared_returns":
            return m > 0.05
        elif key == "conditional_kurtosis":
            return abs(m) < 3.0
        elif key == "dfa_hurst_abs_r":
            return 0.50 <= m <= 0.85
        elif key == "leverage_effect":
            return m < -0.05
        elif key == "volume_volatility_corr":
            return m > 0.1
        elif key == "zumbach_asymmetry":
            return m > 0.01
        return False

    for label, key, expected in rows:
        gs_per = []
        for f in fits:
            g = f["aggregated"].get(key)
            gs_per.append("✓" if g and _score(g["mean"], key) else "✗")
        lm_v = lm_agg.get(key)
        lm_score = "✓" if lm_v and _score(lm_v["mean"], key) else "✗"
        lines.append(f"| {label} | {' '.join(gs_per)} ({'/'.join(d[0] for d in DATASETS)}) | {lm_score} |")

    lines.append("")
    lines.append("### Total matches")
    lines.append("")
    totals = {
        d[0]: sum(1 for _, key, _ in rows if _score((f["aggregated"].get(key) or {}).get("mean"), key))
        for d, f in zip(DATASETS, fits, strict=True)
    }
    totals_sum = {d[0]: f"{totals[d[0]]}/11" for d in DATASETS}
    lm_total = sum(1 for _, key, _ in rows if _score((lm_agg.get(key) or {}).get("mean"), key))
    lines.append("")
    lines.append("| model | spx | spy | btc | eth | LM99 |")
    lines.append("|---|---|---|---|---|---|")
    lines.append(f"| GARCH(1,1)-t fitted | {totals_sum['spx']} | {totals_sum['spy']} | {totals_sum['btcusdt']} | {totals_sum['ethusdt']} | — |")
    lines.append(f"| LM99 asset-agnostic | — | — | — | — | {lm_total}/11 |")

    (OUT / "three_way_comparison.md").write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\n→ wrote {OUT / 'three_way_comparison.md'}")
    print(f"→ wrote {OUT / 'garch_fit_params.json'}")
    print(f"→ wrote {OUT / 'garch_stylized_facts.json'}")


if __name__ == "__main__":
    main()
