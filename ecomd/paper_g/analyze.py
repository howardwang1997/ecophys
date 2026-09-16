"""Development summaries; no confirmatory inference or asymptotic-rate claims."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t as student_t


def mean_interval(values: list[float]) -> dict[str, float | int]:
    x = np.asarray(values, dtype=float)
    mean = float(x.mean())
    half = float(student_t.ppf(0.975, len(x)-1)*x.std(ddof=1)/np.sqrt(len(x)))
    return {"n": len(x), "mean": mean, "ci_low": mean-half, "ci_high": mean+half}


def analyze(directory: Path) -> None:
    data = json.loads((directory / "results.json").read_text())
    rows = data["runs"]
    methods = sorted({r["method"] for r in rows})
    groups = [(rho, feed) for rho in (0.1, 1.0) for feed in ("actual", "reveal")]
    seeds = sorted({r["seed"] for r in rows})
    if len(rows) != len(methods)*len(groups)*len(seeds) or any(r["violations"] for r in rows):
        raise ValueError("incomplete or invalid pilot")
    cells: list[dict[str, Any]] = []
    contrasts: list[dict[str, Any]] = []
    for method in methods:
        by_key = {(r["seed"], r["rho"], r["feedback"]): r for r in rows if r["method"] == method}
        for rho, feed in groups:
            selected = [by_key[(seed, rho, feed)] for seed in seeds]
            cells.append({"method": method, "rho": rho, "feedback": feed,
                          **mean_interval([r["regret_per_round"] for r in selected]),
                          "wealth_mean": float(np.mean([r["wealth"] for r in selected])),
                          "oracle_value": selected[0]["oracle_value"],
                          "informative_buy_mean": float(np.mean([r["informative_buy_observations"] for r in selected])),
                          "informative_sell_mean": float(np.mean([r["informative_sell_observations"] for r in selected]))})
        paired = []
        for seed in seeds:
            def r(rho: float, f: str) -> float:
                return float(by_key[(seed, rho, f)]["regret_per_round"])
            paired.append(r(0.1, "actual")-r(0.1, "reveal")-r(1.0, "actual")+r(1.0, "reveal"))
        contrasts.append({"method": method, **mean_interval(paired), "paired_values": paired})
    output = {
        "evidence_label": "development_not_confirmation", "horizon": rows[0]["horizon"],
        "cells": cells, "feedback_by_recovery_contrasts": contrasts,
        "wall_seconds": data["wall_seconds"], "job_cpu_seconds": data["job_cpu_seconds"],
        "planning_seconds_summed": sum(r["planning_seconds"] for r in rows),
        "max_worker_peak_rss_mib": max(r["max_rss_kib"] for r in rows)/1024,
        "run_count": len(rows), "dealer_rounds": sum(r["horizon"] for r in rows),
        "violations": sum(r["violations"] for r in rows),
        "interpretation": "Eight development seeds, one capacity/regime, one short horizon. Intervals are descriptive Monte Carlo uncertainty, not confirmation or a learning-rate theorem.",
    }
    (directory / "summary.json").write_text(json.dumps(output, indent=2)+"\n")
    with (directory / "cell_summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(cells[0]))
        writer.writeheader()
        writer.writerows(cells)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    colors = ["#276FBF", "#CF5C36"]
    labels = ["Scarce\nactual", "Scarce\nreveal", "Abundant\nactual", "Abundant\nreveal"]
    for j, method in enumerate(methods):
        selected = [c for c in cells if c["method"] == method]
        x = np.arange(4)+(j-0.5)*0.32
        y = np.array([c["mean"] for c in selected])
        err = np.array([c["ci_high"]-c["mean"] for c in selected])
        axes[0].bar(x, y, width=0.3, color=colors[j], label=method.replace("_", " "), alpha=0.85)
        axes[0].errorbar(x, y, yerr=err, fmt="none", ecolor="#333333", capsize=3)
        contrast = contrasts[j]
        axes[1].errorbar(contrast["mean"], j, xerr=contrast["ci_high"]-contrast["mean"],
                         fmt="o", color=colors[j], capsize=5, markersize=7)
    axes[0].set_xticks(np.arange(4), labels)
    axes[0].set_ylabel("Oracle gap (ticks / opportunity)")
    axes[0].set_title("Learning gap within each market")
    axes[0].legend(fontsize=8)
    axes[1].axvline(0, color="#777777", linestyle="--", linewidth=1)
    axes[1].set_yticks(range(len(methods)), [m.replace("_", "\n") for m in methods])
    axes[1].set_xlabel("Feedback x recovery contrast (ticks / opportunity)")
    axes[1].set_title("Paired interaction: mean and 95% t interval")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.15)
    fig.suptitle("Paper G development pilot | Q=2 | balanced flow | T=1024 | 8 seeds", fontsize=12)
    fig.savefig(directory / "development_summary.png", dpi=180)
    plt.close(fig)
    print(json.dumps(output, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    analyze(parser.parse_args().directory)


if __name__ == "__main__":
    main()
