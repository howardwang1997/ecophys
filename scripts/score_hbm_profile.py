#!/usr/bin/env python3
"""Aggregate Phase 6 HBM profile results.

Reads experiments/028_hbm_profile/results_*/training_log.json and
writes a markdown table comparing predicted vs measured peak HBM.

Run on Mac or H20 after h20_hbm_profile.sh completes.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROFILE_DIR = REPO / "experiments/028_hbm_profile"


def main() -> None:
    rows = []
    for d in sorted(PROFILE_DIR.glob("results_*")):
        log_path = d / "training_log.json"
        label = d.name.replace("results_", "")
        if not log_path.exists():
            rows.append({"label": label, "status": "OOM/missing"})
            continue
        try:
            data = json.loads(log_path.read_text())
        except Exception as e:
            rows.append({"label": label, "status": f"parse error: {e}"})
            continue

        sim_cfg = data["config"]["simulator"]
        train_cfg = data["config"]["training"]
        peak = data.get("peak_hbm", {})

        # Predicted: per_step ≈ 3.5 GB at N=10K stochastic_mlp, scales linearly with N.
        # peak ≈ K × per_step + ~3 GB fixed (recorder + allocator).
        per_step = 3.5 * (sim_cfg["n_agents"] / 10_000)
        K_eff = sim_cfg.get("bptt_checkpoint_every", 0)
        if K_eff <= 0:
            K_eff = train_cfg["chunk_steps"]  # full chunk in graph
        predicted_gb = K_eff * per_step + 3.0

        rows.append({
            "label": label,
            "status": "OK",
            "N": sim_cfg["n_agents"],
            "chunk": train_cfg["chunk_steps"],
            "K": sim_cfg.get("bptt_checkpoint_every", 0),
            "predicted_gb": predicted_gb,
            "measured_alloc_gb": peak.get("alloc_gb"),
            "measured_reserved_gb": peak.get("reserved_gb"),
            "train_time_s": data.get("train_time_seconds"),
        })

    # Write report
    lines = [
        "# Phase 6 — HBM Profile Results",
        "",
        "Each config trained 3 iters; peak HBM captured via "
        "`torch.cuda.max_memory_*`. Predicted column uses calibration "
        "of 3.5 GB/step at N=10K stochastic_mlp + create_graph=True + "
        "linear scaling in N + ~3 GB fixed overhead.",
        "",
        "| config | N | chunk | K | predicted GB | **measured alloc GB** | reserved GB | train time |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        if r.get("status") != "OK":
            lines.append(f"| `{r['label']}` | — | — | — | — | **{r.get('status', '?')}** | — | — |")
        else:
            alloc = r["measured_alloc_gb"]
            reserved = r["measured_reserved_gb"]
            lines.append(
                f"| `{r['label']}` | {r['N']:,} | {r['chunk']} | {r['K']} | "
                f"{r['predicted_gb']:.1f} | "
                f"**{'—' if alloc is None else f'{alloc:.2f}'}** | "
                f"{'—' if reserved is None else f'{reserved:.2f}'} | "
                f"{'—' if r['train_time_s'] is None else f'{r['train_time_s']:.0f}s'} |"
            )
    lines.append("")
    lines.append("## Calibration check")
    lines.append("")
    # Find baseline
    baseline = next((r for r in rows if r.get("label", "").startswith("p6_baseline")
                     and r.get("status") == "OK" and r.get("measured_alloc_gb")), None)
    if baseline:
        ratio = baseline["measured_alloc_gb"] / baseline["predicted_gb"]
        lines.append(f"Baseline (chunk=24 N=10K K=0): predicted={baseline['predicted_gb']:.1f} GB, "
                     f"measured={baseline['measured_alloc_gb']:.2f} GB, ratio = {ratio:.2f}×")
        if 0.85 < ratio < 1.15:
            lines.append("→ **Calibration accurate** (within ±15%)")
        else:
            lines.append(f"→ **Calibration off by {ratio:.2f}×** — refit per-step constant accordingly")
    lines.append("")
    lines.append("## Implications")
    lines.append("")
    lines.append("- If measured ≪ predicted: we have headroom for larger N or longer chunk")
    lines.append("- If a config OOM'd: that's the empirical ceiling for current arch")
    lines.append("- Spatial-sharded pairwise (next sprint, `feature/spatial-checkpoint`) "
                 "expected to break peak ∝ N → peak ∝ B (spatial batch size)")

    out = PROFILE_DIR / "report.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out}")
    for r in rows:
        if r.get("status") == "OK":
            print(f"  {r['label']:<32} predicted={r['predicted_gb']:5.1f}GB  "
                  f"measured={r['measured_alloc_gb'] or 0:5.2f}GB")
        else:
            print(f"  {r['label']:<32} {r['status']}")


if __name__ == "__main__":
    main()
