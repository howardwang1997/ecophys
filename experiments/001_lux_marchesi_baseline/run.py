"""Compare Lux-Marchesi 1999 ABM output to real market stylized facts.

Methodology:
  - Run multiple independent realizations of Lux-Marchesi 1999 (different seeds)
  - Compute all 11 stylized facts on each realization
  - Aggregate mean ± std across realizations
  - Compare side-by-side with SPX / SPY / BTC / ETH reference values
    (loaded from experiments/000_reference_values/results/).

Output:
  - results/lux_marchesi_stylized_facts.json : per-realization metrics
  - results/comparison_table.md : scan-friendly side-by-side comparison
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from ecomd.baselines.lux_marchesi import LuxMarchesi1999, LuxMarchesiParams
from ecomd.eval.stylized_facts import compute_all

log = logging.getLogger("lux_marchesi_baseline")

REPO = Path(__file__).resolve().parents[2]
REF_RESULTS = REPO / "experiments" / "000_reference_values" / "results"
OUT = Path(__file__).parent / "results"


# ─── Simulation ───────────────────────────────────────────────────────────


def _run_realization(seed: int, n_steps: int, dt: float) -> dict[str, Any]:
    sim = LuxMarchesi1999(LuxMarchesiParams())
    traj = sim.run(n_steps=n_steps, dt=dt, seed=seed)
    r = traj.log_returns
    # Use chartist trading activity as a rough "volume" proxy: abs(n_cp - n_cn)
    # at each step. Length will be n_steps; align by dropping the first one.
    imbalance = np.abs(traj.n_optimist - traj.n_pessimist).astype(float)[1:]
    facts = compute_all(r, volume=imbalance)
    return {
        "seed": seed,
        "n_steps": n_steps,
        "dt": dt,
        "results": {k: asdict(v) for k, v in facts.items()},
        "summary": {
            "mean_n_f": float(traj.n_fundamentalist.mean()),
            "mean_n_cp": float(traj.n_optimist.mean()),
            "mean_n_cn": float(traj.n_pessimist.mean()),
            "std_log_return": float(r.std()),
            "min_log_return": float(r.min()),
            "max_log_return": float(r.max()),
        },
    }


def _aggregate(runs: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    metric_names = set()
    for run in runs:
        metric_names.update(run["results"].keys())
    agg: dict[str, dict[str, float]] = {}
    for m in sorted(metric_names):
        vals = [run["results"][m]["estimate"] for run in runs if m in run["results"]]
        vals = [v for v in vals if isinstance(v, (int, float)) and np.isfinite(v)]
        if not vals:
            continue
        agg[m] = {
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals)),
            "min": float(np.min(vals)),
            "max": float(np.max(vals)),
            "n_runs": len(vals),
        }
    return agg


# ─── Reference loading ────────────────────────────────────────────────────


REFERENCE_DATASETS = ["spx", "spy", "btcusdt", "ethusdt"]
REFERENCE_PERIODS = {
    "spx": "2015-2026_daily",
    "spy": "2015-2026_daily",
    "btcusdt": "2024Q1_1m",
    "ethusdt": "2024Q1_1m",
}


def _load_reference(dataset: str) -> dict[str, float]:
    period = REFERENCE_PERIODS[dataset]
    path = REF_RESULTS / f"stylized_facts_{dataset}_{period}.json"
    if not path.is_file():
        log.warning("missing reference: %s", path)
        return {}
    with path.open() as f:
        payload = json.load(f)
    return {name: res["estimate"] for name, res in payload["results"].items()}


# ─── Main ─────────────────────────────────────────────────────────────────


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    OUT.mkdir(parents=True, exist_ok=True)

    n_realizations = 10
    n_steps = 20_000       # 200 units of model time at dt=0.01 → solid stylized-facts stats
    dt = 0.01

    log.info("running %d Lux-Marchesi realizations, %d steps each (dt=%.3f)", n_realizations, n_steps, dt)
    runs = [_run_realization(seed=s, n_steps=n_steps, dt=dt) for s in range(n_realizations)]

    # dump raw
    (OUT / "lux_marchesi_stylized_facts.json").write_text(json.dumps(runs, indent=2))
    agg = _aggregate(runs)

    # Load real-market references
    refs = {d: _load_reference(d) for d in REFERENCE_DATASETS}

    # Build comparison table
    metric_rows = [
        ("#1 ACF(r)",            "autocorr_returns",           "<0.05",          "low"),
        ("#2 α (Hill)",          "hill_tail_index",            "[3, 5]",         "in range"),
        ("#3 skew",              "gain_loss_asymmetry",        "<0 (daily equity)", "sign"),
        ("#4 Δκ agg",            "aggregational_gaussianity",  ">0",             "positive"),
        ("#5 Fano",              "intermittency_fano",         ">1",             "> 1"),
        ("#6 ⟨ACF(r²)⟩",        "acf_squared_returns",        ">0.05",          "above 0.05"),
        ("#7 κ GARCH-std",       "conditional_kurtosis",       ">0, < unconditional", "positive"),
        ("#8 H DFA|r|",          "dfa_hurst_abs_r",            "[0.55, 0.80]",   "in range (stationary)"),
        ("#9 ΣLev",              "leverage_effect",            "<0 (daily)",     "negative"),
        ("#10 corr(V,|r|)",      "volume_volatility_corr",     "[0.2, 0.6]",     "positive"),
        ("#11 Zumbach D",        "zumbach_asymmetry",          ">0 (indices)",   "positive"),
    ]

    lines: list[str] = []
    lines.append("# Lux-Marchesi 1999 baseline vs real-market reference values")
    lines.append("")
    lines.append(f"{n_realizations} realizations × {n_steps} steps at dt={dt}. "
                 "Lux-Marchesi entries show mean ± std across realizations.")
    lines.append("")
    header = "| metric | Cont 2001 expected | Lux-Marchesi 1999 | SPX daily | SPY daily | BTC 1m | ETH 1m |"
    lines.append(header)
    lines.append("|" + "|".join(["---"] * 7) + "|")
    for label, key, expected, _ in metric_rows:
        lm = agg.get(key)
        lm_str = f"{lm['mean']:+.3f} ± {lm['std']:.3f}" if lm else "—"
        row = [label, expected, lm_str]
        for dset in REFERENCE_DATASETS:
            v = refs[dset].get(key)
            row.append(f"{v:+.3f}" if isinstance(v, (int, float)) and np.isfinite(v) else "—")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append("")
    lines.append("## Did Lux-Marchesi reproduce the target stylized fact?")
    lines.append("")
    lines.append("| metric | target property | LM outcome | OK? |")
    lines.append("|---|---|---|---|")
    for label, key, expected, _desc in metric_rows:
        lm = agg.get(key)
        if not lm:
            lines.append(f"| {label} | {expected} | missing | — |")
            continue
        m = lm["mean"]
        verdict = "—"
        if key == "autocorr_returns":
            verdict = "✓" if m < 0.05 else "✗"
        elif key == "hill_tail_index":
            verdict = "✓" if 2.5 <= m <= 6.0 else "✗"
        elif key == "gain_loss_asymmetry":
            verdict = "✓" if m < 0 else "≈0"
        elif key == "aggregational_gaussianity":
            verdict = "✓" if m > 0 else "✗"
        elif key == "intermittency_fano":
            verdict = "✓" if m > 1.0 else "✗"
        elif key == "acf_squared_returns":
            verdict = "✓" if m > 0.05 else "✗"
        elif key == "conditional_kurtosis":
            verdict = "✓" if m > 0 else "✗"
        elif key == "dfa_hurst_abs_r":
            verdict = "✓" if 0.50 <= m <= 0.85 else "✗"
        elif key == "leverage_effect":
            verdict = "✓" if m < 0 else "≈0"
        elif key == "volume_volatility_corr":
            verdict = "✓" if m > 0.05 else "✗"
        elif key == "zumbach_asymmetry":
            verdict = "✓" if m > 0.01 else "≈0"
        lines.append(f"| {label} | {expected} | {m:+.3f} | {verdict} |")
    lines.append("")

    (OUT / "comparison_table.md").write_text("\n".join(lines))
    print("\n".join(lines))
    print()
    print(f"→ wrote {OUT / 'lux_marchesi_stylized_facts.json'}")
    print(f"→ wrote {OUT / 'comparison_table.md'}")


if __name__ == "__main__":
    main()
