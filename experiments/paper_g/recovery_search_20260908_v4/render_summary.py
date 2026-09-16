"""Render frozen deterministic outputs; no new scientific computation."""

from pathlib import Path
import csv
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
result = json.loads((root/"results/result.json").read_text())
rows = result["scaling_cells"]
with (root/"scaling_cells.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.8), sharey=True)
colors = ["#1f6e9c", "#c56321", "#38835a"]
for ax, regime, parameters, name, title in zip(
    axes, ["fixed_lambda", "lambda_c_over_T"], [[.1, .01, .001], [.25, 1., 4.]],
    ["lambda", "c"], ["One fixed environment per curve", r"Different environments: $\lambda=c/T$"]
):
    for color, parameter in zip(colors, parameters):
        selected = [r for r in rows if r["regime"] == regime and r["alpha"] == .5 and r[name] == parameter]
        symbol = r"\lambda" if name == "lambda" else "c"
        ax.plot([r["horizon"] for r in selected], [r["regret_per_round"] for r in selected],
                marker="o", markersize=4, color=color, linewidth=1.8, label=rf"${symbol}={parameter:g}$")
        if regime == "lambda_c_over_T":
            ax.axhline(selected[0]["normalized_limit"], color=color, linestyle=":", linewidth=1.1)
    ax.set_xscale("log", base=2)
    ax.set_xticks([16, 64, 256, 1024, 4096, 16384], ["16", "64", "256", "1024", "4096", "16384"])
    ax.tick_params(axis="x", labelsize=9)
    ax.set_xlabel("Horizon T (rounds)")
    ax.set_title(title, fontsize=12)
    ax.grid(alpha=.18)
    ax.legend(frameon=False, fontsize=10)
axes[0].set_ylabel(r"Exact minimax regret per round $R_T^*/T$")
axes[0].set_ylim(0, .14)
fig.suptitle(r"Unknown recovery channels: exact learning cost ($\alpha=0.5$, $\Delta=1$)", fontsize=14, y=.98)
fig.text(.5, .025, "Synthetic first-success search; deterministic development values. Dotted lines: analytic limits.\nNo coupled-inventory or field-market claim; all 72 frozen cells are retained in CSV.", ha="center", fontsize=9, color="#454545")
fig.tight_layout(rect=(0, .12, 1, .94))
fig.savefig(root/"recovery_search_boundary.png", dpi=180)
plt.close(fig)
