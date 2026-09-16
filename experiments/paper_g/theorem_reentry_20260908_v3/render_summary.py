"""Post-computation display of all frozen theorem-check cells."""

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main() -> None:
    root = Path(__file__).resolve().parent
    data = json.loads((root / "results/result.json").read_text())
    for key in ["m0_span_cells", "gate_cells"]:
        with (root / f"{key}.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(data[key][0]))
            writer.writeheader()
            writer.writerows(data[key])
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), constrained_layout=True)
    for q, color in [(2, "#31688e"), (8, "#d56c24")]:
        selected = [r for r in data["m0_span_cells"] if r["capacity"] == q]
        rates = sorted({r["rho"] for r in selected})
        maxima = [max(r["max_span"] for r in selected if r["rho"] == rho) for rho in rates]
        axes[0].plot(range(len(rates)), maxima, "o-", color=color, label=f"Q={q}, grid maximum")
        axes[0].axhline(2*(q+2), color=color, linestyle="--", label=f"Q={q}, proved bound")
        rows = sorted([r for r in data["gate_cells"] if r["capacity"] == q and r["horizon"] == 4096], key=lambda r: r["truncated_wait"])
        x = [r["truncated_wait"] for r in rows]
        axes[1].plot(x, [r["value_gap"] for r in rows], "o-", color=color, label=f"Q={q}, exact DP")
        axes[1].plot(x, [max(0, r["proved_gap_lower_bound"]) for r in rows], "--", color=color, label=f"Q={q}, lower bound")
    axes[0].set_xticks(range(4), ["0", "0.001", "0.1", "1"])
    axes[0].set_xlabel("Unit-depth replenishment probability")
    axes[0].set_ylabel("Maximum optimal-value span (ticks)")
    axes[0].set_title("M0: bounded initial resource advantage")
    axes[0].set_ylim(bottom=0)
    axes[1].set_xscale("log")
    axes[1].set_xlabel("Expected suspension within 4,096 rounds")
    axes[1].set_ylabel("Eligible minus suspended value (ticks)")
    axes[1].set_title("Persistent access: loss grows with waiting")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=.15)
        ax.legend(fontsize=7)
    fig.suptitle("Paper G — deterministic development checks; analytic bounds", fontsize=12)
    fig.savefig(root / "theorem_boundary.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
