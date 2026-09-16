"""Descriptive summaries of the fixed second development campaign."""

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

from .analyze import mean_interval


def analyze(root: Path) -> None:
    audit = json.loads((root / "audit" / "audit.json").read_text())
    probe = json.loads((root / "probe" / "probe.json").read_text())
    learning = json.loads((root / "learning" / "learning.json").read_text())
    data = learning["rows"]
    capacities = sorted({r["capacity"] for r in data})
    horizons = sorted({r["horizon"] for r in data})
    methods = sorted({r["method"] for r in data})
    seeds = sorted({r["seed"] for r in data})
    cells: list[dict[str, Any]] = []
    contrasts: list[dict[str, Any]] = []
    for q in capacities:
        for horizon in horizons:
            for method in methods:
                rows = {(r["seed"], r["rho"], r["feedback"]): r for r in data if r["capacity"] == q and r["horizon"] == horizon and r["method"] == method}
                if len(rows) != 4*len(seeds):
                    raise ValueError("incomplete learning cell")
                for rho in (0.1, 1.0):
                    for feed in ("actual", "reveal"):
                        selected = [rows[(s, rho, feed)] for s in seeds]
                        cells.append({"capacity": q, "horizon": horizon, "method": method, "rho": rho, "feedback": feed,
                                      **mean_interval([r["regret_per_round"] for r in selected]),
                                      "hedge_fraction_mean": float(np.mean([r["hedges"]/horizon for r in selected]))})
                differences = [rows[(s, .1, "actual")]["regret_per_round"]-rows[(s, .1, "reveal")]["regret_per_round"]
                               -rows[(s, 1., "actual")]["regret_per_round"]+rows[(s, 1., "reveal")]["regret_per_round"] for s in seeds]
                contrasts.append({"capacity": q, "horizon": horizon, "method": method, **mean_interval(differences), "paired_values": differences})
    probes = []
    for name in sorted({r["law"] for r in probe["rows"]}):
        for rho in (0.0, 0.1, 1.0):
            selected = [r for r in probe["rows"] if r["law"] == name and r["rho"] == rho]
            probes.append({"law": name, "rho": rho, **mean_interval([r["probe_rate"] for r in selected]),
                           "predicted_rate": selected[0]["predicted_probe_rate"],
                           "predicted_cycle_length": selected[0]["predicted_cycle_length"],
                           "completed_cycle_mean": sum(r["cycle_sum"] for r in selected)/sum(r["completed_cycles"] for r in selected),
                           "right_censored_cycles": sum(r["censored_cycle_elapsed"] > 0 for r in selected)})
    signatures_equal = all(len({r["inventory_signature"] for r in probe["rows"] if r["seed"] == s and r["law"] == name}) == 1
                           for name in {r["law"] for r in probe["rows"]} for s in {r["seed"] for r in probe["rows"]})
    if not signatures_equal or any(r["violations"] for r in data+probe["rows"]):
        raise ValueError("invalid mechanism check")
    summary = {"evidence_label": "development_not_confirmation", "audit_binding": audit["binding"],
               "learning_cells": cells, "interactions": contrasts, "probe_summaries": probes,
               "probe_inventory_histories_identical_across_rho": signatures_equal,
               "learning_run_count": len(data), "learning_rounds": sum(r["horizon"] for r in data),
               "learning_wall_seconds": learning["wall_seconds"], "learning_job_cpu_seconds": learning["job_cpu_seconds"],
               "max_worker_peak_rss_mib": max(r["max_rss_kib"] for r in data)/1024,
               "probe_run_count": len(probe["rows"]), "probe_rounds": sum(r["horizon"] for r in probe["rows"]),
               "probe_wall_seconds": probe["wall_seconds"], "audit_wall_seconds": audit["wall_seconds"],
               "violations": 0,
               "inference_scope": "Descriptive t intervals across development roots. Multiple configurations, no confirmatory significance or minimax claims."}
    (root / "summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    for filename, records in (("learning_cells.csv", cells), ("probe_summary.csv", probes)):
        with (root / filename).open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), constrained_layout=True)
    labels = [f"Q={q}, T={h}" for q in capacities for h in horizons]
    for j, method in enumerate(methods):
        selected = [r for r in contrasts if r["method"] == method]
        means = [r["mean"] for r in selected]
        axes[0].errorbar(means, np.arange(len(selected))+(j-.5)*.16,
                         xerr=[r["ci_high"]-r["mean"] for r in selected], fmt="o", capsize=3,
                         label=method.replace("_", " "))
    axes[0].axvline(0, color="gray", linestyle="--", linewidth=1)
    axes[0].set_yticks(range(len(labels)), labels)
    axes[0].set_xlabel("Feedback x recovery contrast\n(ticks / opportunity)")
    axes[0].set_title("Directional-flow learning: 16 seeds")
    axes[0].legend(fontsize=7, loc="best")
    for name in ("balanced", "directional"):
        selected = [r for r in probes if r["law"] == name]
        axes[1].errorbar(range(3), [r["mean"] for r in selected],
                         yerr=[r["ci_high"]-r["mean"] for r in selected], fmt="o-", capsize=3, label=name)
        axes[1].axhline(selected[0]["predicted_rate"], color="gray", linestyle=":", linewidth=1)
    axes[1].set_xticks(range(3), ["0", "0.1", "1"])
    axes[1].set_xlabel("Hedge replenishment probability")
    axes[1].set_ylabel("Full-type probes / opportunity")
    axes[1].set_title("Feasible probe: 32 seeds\nDotted lines = theory")
    axes[1].legend(fontsize=8)
    axes[2].bar([f"Q={r['capacity']}" for r in audit["binding"]], [r["availability_value_per_round"] for r in audit["binding"]], color="#497A84")
    axes[2].set_ylabel("Abundant minus scarce oracle value\n(ticks / opportunity)")
    axes[2].set_title("Execution changes attainable value")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=.15)
    fig.suptitle("Paper G M0 — fixed development resolution experiments", fontsize=13)
    fig.savefig(root / "resolution_summary.png", dpi=180)
    plt.close(fig)
    print(json.dumps({k: v for k, v in summary.items() if k != "learning_cells"}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    analyze(parser.parse_args().root)


if __name__ == "__main__":
    main()
