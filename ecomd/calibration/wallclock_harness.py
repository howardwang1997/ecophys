"""ECoMD calibration wall-clock harness — M1.6 component.

Post-processing step for batch 091. Each ECoMD calibration run in 091 is
a standard `train_distributed.py` execution with a specific `n_iters`
budget. After the batch lands, this module reads each run's
`training_log.json` (wall-clock per iter) and `inference_merged.json`
(final fact-pass count) to build a (n_iters, wall, coverage) tradeoff
curve.

For Paper A's headline claim (~100× faster than ABIDES+SBI), we report:
  - mean wall-clock to reach ≥7/11 facts in band (paper-quality coverage)
  - mean n_iters to reach the same
  - per-asset Pareto frontier (n_iters × coverage)

The ABIDES+SBI leg is run as a separate harness once ABIDES is installed
on H20 (blocked, see state doc §3.5). When that lands, append its
(wall, coverage) data points to the same plot.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

# Cont 2001 band membership thresholds — see ecomd/eval/stylized_facts.py
# scoring conventions. We import the canonical scorer to stay consistent.

_PASS_BANDS = {
    "autocorr_returns":          (-0.10,  0.20),
    "hill_tail_index":           ( 2.00,  4.00),
    "gain_loss_asymmetry":       ( 0.10,  1.50),
    "aggregational_gaussianity": ( 10.0,  200.0),
    "intermittency_fano":        ( 1.10,  5.00),
    "acf_squared_returns":       ( 0.05,  0.50),
    "conditional_kurtosis":      ( 3.50,  20.00),
    "dfa_hurst_abs_r":           ( 0.60,  0.90),
    "leverage_effect":           (-0.50, -0.02),
    "volume_volatility_corr":    ( 0.10,  0.80),
    "zumbach_asymmetry":         ( 0.001, 0.50),
}


@dataclass
class CalibrationRun:
    """A single ECoMD calibration run = one (asset, cell, n_iters_budget, seed)."""

    config_path: Path
    asset: str
    n_iters_budget: int
    seed: int
    wall_seconds: float = field(default=float("nan"))
    n_iters_actual: int = 0
    facts_pass: int = 0
    facts_total: int = 11
    fact_values: dict = field(default_factory=dict)
    out_dir: Path | None = None

    @property
    def coverage(self) -> float:
        return self.facts_pass / max(self.facts_total, 1)


def _count_facts_pass(aggregated: dict) -> int:
    n = 0
    for fact, band in _PASS_BANDS.items():
        rec = aggregated.get(fact)
        if rec is None:
            continue
        val = rec.get("mean") if isinstance(rec, dict) else None
        if val is None or not np.isfinite(val):
            continue
        if band[0] <= val <= band[1]:
            n += 1
    return n


def extract_run_metadata(config_path: Path) -> CalibrationRun:
    """Parse one results dir for the (wall, n_iters, coverage) triple."""
    import yaml
    cfg = yaml.safe_load(config_path.read_text())
    train_cfg = cfg.get("training", {})
    asset = train_cfg.get("target_dataset", "spx")
    seed = int(train_cfg.get("seed", 0))
    n_iters_budget = int(train_cfg.get("n_iters", 0))

    out_dir = config_path.parent / f"results_{config_path.stem.replace('config_', '')}"
    run = CalibrationRun(
        config_path=config_path,
        asset=asset,
        seed=seed,
        n_iters_budget=n_iters_budget,
        out_dir=out_dir if out_dir.exists() else None,
    )
    if not out_dir.exists():
        return run

    train_log = out_dir / "training_log.json"
    if train_log.exists():
        try:
            tl = json.loads(train_log.read_text())
            if isinstance(tl, list) and tl:
                last = tl[-1]
                run.wall_seconds = float(last.get("elapsed_seconds", float("nan")))
                run.n_iters_actual = int(last.get("iter", 0))
            elif isinstance(tl, dict):
                run.wall_seconds = float(tl.get("total_seconds", float("nan")))
                run.n_iters_actual = int(tl.get("final_iter", 0))
        except (json.JSONDecodeError, ValueError, KeyError):
            pass

    inf = out_dir / "inference_merged.json"
    if inf.exists():
        try:
            inf_data = json.loads(inf.read_text())
            agg = inf_data.get("aggregated", {})
            run.facts_pass = _count_facts_pass(agg)
            run.fact_values = {
                k: (v.get("mean") if isinstance(v, dict) else None)
                for k, v in agg.items()
            }
        except (json.JSONDecodeError, ValueError):
            pass
    return run


def analyze_calibration_dir(batch_dir: Path) -> list[CalibrationRun]:
    """Read every config_*.yaml in a batch dir and parse its run metadata."""
    runs: list[CalibrationRun] = []
    for cfg_path in sorted(batch_dir.glob("config_*.yaml")):
        runs.append(extract_run_metadata(cfg_path))
    return runs


def print_pareto_report(runs: list[CalibrationRun], coverage_target: int = 7) -> str:
    """Per-asset Pareto frontier + wall-clock to reach `coverage_target` facts."""
    by_asset: dict[str, list[CalibrationRun]] = {}
    for r in runs:
        by_asset.setdefault(r.asset, []).append(r)

    lines = ["# Calibration speed harness — ECoMD leg\n"]
    lines.append(f"Coverage target: {coverage_target}/11 facts in band\n")
    for asset, asset_runs in sorted(by_asset.items()):
        lines.append(f"## Asset: {asset}")
        valid = [r for r in asset_runs if np.isfinite(r.wall_seconds) and r.facts_pass > 0]
        if not valid:
            lines.append("  no completed runs\n")
            continue
        # Group by n_iters_budget, mean across seeds
        budgets: dict[int, list[CalibrationRun]] = {}
        for r in valid:
            budgets.setdefault(r.n_iters_budget, []).append(r)
        lines.append("| n_iters | mean wall (s) | mean coverage | n_seeds |")
        lines.append("|---:|---:|---:|---:|")
        for b in sorted(budgets):
            grp = budgets[b]
            mw = float(np.mean([r.wall_seconds for r in grp]))
            mc = float(np.mean([r.facts_pass for r in grp]))
            lines.append(f"| {b} | {mw:.1f} | {mc:.2f}/11 | {len(grp)} |")
        # Reach-target metric
        ge_target = [r for r in valid if r.facts_pass >= coverage_target]
        if ge_target:
            fastest = min(ge_target, key=lambda r: r.wall_seconds)
            lines.append(f"\nFirst to reach ≥{coverage_target}/11: "
                          f"n_iters={fastest.n_iters_budget}, "
                          f"wall={fastest.wall_seconds:.1f}s, "
                          f"seed={fastest.seed}")
        else:
            lines.append(f"\nNo run reached ≥{coverage_target}/11 in this budget grid.")
        lines.append("")
    return "\n".join(lines)


def _smoke() -> None:
    """Smoke: synthesize fake run data and verify the parser."""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        td_p = Path(td)
        # Fake config
        cfg = {
            "training": {"target_dataset": "spx", "seed": 0, "n_iters": 100},
            "simulator": {},
        }
        import yaml
        cfg_path = td_p / "config_test_seed0.yaml"
        cfg_path.write_text(yaml.safe_dump(cfg))
        # Fake results dir
        rd = td_p / "results_test_seed0"
        rd.mkdir()
        (rd / "training_log.json").write_text(json.dumps([
            {"iter": 50, "elapsed_seconds": 120.0},
            {"iter": 100, "elapsed_seconds": 240.0},
        ]))
        (rd / "inference_merged.json").write_text(json.dumps({
            "aggregated": {
                "autocorr_returns":          {"mean": 0.05},  # in band
                "hill_tail_index":           {"mean": 3.0},   # in band
                "gain_loss_asymmetry":       {"mean": 0.5},   # in band
                "aggregational_gaussianity": {"mean": 150.0}, # in band
                "intermittency_fano":        {"mean": 2.0},   # in band
                "acf_squared_returns":       {"mean": 0.3},   # in band
                "conditional_kurtosis":      {"mean": 10.0},  # in band
                "dfa_hurst_abs_r":           {"mean": 0.75},  # in band
                "leverage_effect":           {"mean": 0.05},  # OUT (band -0.5..-0.02)
                "volume_volatility_corr":    {"mean": 0.4},   # in band
                "zumbach_asymmetry":         {"mean": -0.01}, # OUT
            },
        }))
        runs = analyze_calibration_dir(td_p)
        assert len(runs) == 1
        r = runs[0]
        assert r.asset == "spx", f"expected spx, got {r.asset}"
        assert r.facts_pass == 9, f"expected 9 pass, got {r.facts_pass}"
        assert r.n_iters_actual == 100, f"got {r.n_iters_actual}"
        assert r.wall_seconds == 240.0, f"got {r.wall_seconds}"
        print(print_pareto_report(runs, coverage_target=7))
        print("[smoke] OK")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--report", type=Path, default=None,
                        help="Build Pareto report for a 091 batch dir")
    parser.add_argument("--coverage-target", type=int, default=7)
    args = parser.parse_args()
    if args.smoke:
        _smoke()
    elif args.report:
        runs = analyze_calibration_dir(args.report)
        print(print_pareto_report(runs, coverage_target=args.coverage_target))
    else:
        print("Usage: python -m ecomd.calibration.wallclock_harness --smoke | --report <dir>")
