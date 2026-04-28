#!/usr/bin/env python3
"""Aggregate per-config 11-fact scores and 5-seed bootstrap CI for any
experiments/<dir>/results_<label>/inference_merged.json files.

Particularly designed for Phase C and Phase H (PLAN_2026-04-28 v2):
- Phase C (031_chunk_effect): groups by chunk; reports mean/CI per chunk
- Phase H (032_arch_regime_sweep): groups by axis (lr/iters/init/n_seeds);
  reports mean/CI per variant + 10-seed distribution histogram

Usage:
    conda run -n ecophys python scripts/score_phase.py experiments/031_chunk_effect
    conda run -n ecophys python scripts/score_phase.py experiments/032_arch_regime_sweep
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent

# Canonical 11-fact bands (must match score_paper_a_solidify.py /
# score_loss_ablation.py)
BANDS = {
    "autocorr_returns":           (-0.1, 0.20),
    "hill_tail_index":            (2.0, 4.0),
    "gain_loss_asymmetry":        (-30.0, -3.0),
    "aggregational_gaussianity":  (10, 200),
    "intermittency_fano":         (5, 100),
    "acf_squared_returns":        (0.15, 0.55),
    "conditional_kurtosis":       (-1.0, 3.0),
    "dfa_hurst_abs_r":            (0.6, 0.9),
    "leverage_effect":            (-6.0, -0.5),
    "volume_volatility_corr":     (0.3, 0.8),
    "zumbach_asymmetry":          (0.001, 0.5),
}


def score_one(p: Path) -> int | None:
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text())
    except Exception:
        return None
    agg = d.get("aggregated", {})
    n_pass = 0
    for k, (lo, hi) in BANDS.items():
        if k not in agg:
            continue
        v = agg[k]["mean"]
        if lo <= v <= hi:
            n_pass += 1
    return n_pass


def bootstrap_ci(values: list[int], n_boot: int = 10_000) -> tuple[float, float, float]:
    if not values:
        return float("nan"), float("nan"), float("nan")
    arr = np.array(values, dtype=float)
    rng = np.random.default_rng(seed=0)
    boots = rng.choice(arr, size=(n_boot, len(arr)), replace=True).mean(axis=1)
    return float(arr.mean()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def parse_label(label: str) -> dict:
    """Extract structure from label like:
      pc_chunk128_seed3      → {phase: pc, chunk: 128, seed: 3}
      pcfix_chunk128_seed3   → {phase: pcfix, chunk: 128, seed: 3}
      ct_default_seed3       → {phase: ct, variant: default, seed: 3}
      ct_sprint2_seed3       → {phase: ct, variant: sprint2, seed: 3}
      ph_lr_1e-3_seed1       → {phase: ph, group: lr, lr: 1e-3, seed: 1}
      ph_iters_400_seed0     → {phase: ph, group: iters, n_iters: 400, seed: 0}
      ph_init_s01_h48_seed1  → {phase: ph, group: init, init_scale: 01, hidden: 48, seed: 1}
      ph_n_seeds_default_seed3 → {phase: ph, group: n_seeds, seed: 3}
    """
    parts = label.split("_")
    out: dict = {"phase": parts[0], "raw": label}
    if parts[0] in ("pc", "pcfix"):
        for tok in parts[1:]:
            if tok.startswith("chunk"):
                out["chunk"] = int(tok.removeprefix("chunk"))
            elif tok.startswith("seed"):
                out["seed"] = int(tok.removeprefix("seed"))
        return out
    if parts[0] == "ct":
        out["variant"] = parts[1]
        for tok in parts[2:]:
            if tok.startswith("seed"):
                out["seed"] = int(tok.removeprefix("seed"))
        return out
    if parts[0] == "sw":
        # sw_stacked_seed3 → {phase: sw, variant: stacked, seed: 3}
        out["variant"] = parts[1] if len(parts) > 1 else "default"
        for tok in parts[1:]:
            if tok.startswith("seed"):
                out["seed"] = int(tok.removeprefix("seed"))
        return out
    if parts[0] == "abl":
        # abl_no_sprint2_seed3 → {phase: abl, cell: "no_sprint2", seed: 3}
        # Last token is "seedN", everything between "abl" and "seed" is cell
        seed_idx = next((i for i, t in enumerate(parts) if t.startswith("seed")), None)
        if seed_idx is not None:
            out["cell"] = "_".join(parts[1:seed_idx])
            out["seed"] = int(parts[seed_idx].removeprefix("seed"))
        return out
    if parts[0] == "ph":
        out["group"] = parts[1]
        for tok in parts[2:]:
            if tok.startswith("seed") and tok != "seeds" and len(tok) > 4 and tok[4:].isdigit():
                out["seed"] = int(tok[4:])
            elif tok.startswith("h") and len(tok) > 1 and tok[1:].isdigit():
                out["hidden"] = int(tok[1:])
            elif tok.startswith("s") and tok not in ("seeds", "seed") and len(tok) > 1:
                out["init_scale_tag"] = tok[1:]
        if out.get("group") == "lr":
            out["variant"] = parts[2]
        elif out.get("group") == "iters":
            out["variant"] = parts[2]
        elif out.get("group") == "init":
            out["variant"] = "_".join(parts[2:-1])
        elif out.get("group") == "n_seeds":
            out["variant"] = "default"
    return out


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: score_phase.py <config_dir>", file=sys.stderr)
        sys.exit(1)
    cfg_dir = Path(sys.argv[1])
    if not cfg_dir.exists():
        print(f"no such dir: {cfg_dir}", file=sys.stderr)
        sys.exit(1)

    rows = []
    for d in sorted(cfg_dir.glob("results_*")):
        if not d.is_dir():
            continue
        label = d.name.replace("results_", "")
        score = score_one(d / "inference_merged.json")
        rows.append({"label": label, "score": score, **parse_label(label)})

    lines: list[str] = [f"# Score — {cfg_dir.name}", ""]
    n_total = len(rows)
    n_done = sum(1 for r in rows if r["score"] is not None)
    lines.append(f"Discovered {n_total} runs, {n_done} with eval.")
    lines.append("")

    # Contamination paired (ct): group by variant (default vs sprint2)
    if any(r.get("phase") == "ct" for r in rows):
        ct_groups: dict[str, list[int]] = defaultdict(list)
        for r in rows:
            if r.get("phase") == "ct" and r.get("score") is not None:
                ct_groups[r["variant"]].append(r["score"])

        lines.append("## Contamination paired — default vs sprint2 (custom autograd)")
        lines.append("| variant | n_seeds | mean n/11 | 95% CI | std |")
        lines.append("|---|---:|---:|---|---:|")
        for variant in sorted(ct_groups):
            scores = ct_groups[variant]
            m, lo, hi = bootstrap_ci(scores)
            std = float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0
            lines.append(f"| `{variant}` | {len(scores)} | **{m:.2f}** | "
                         f"[{lo:.2f}, {hi:.2f}] | {std:.2f} |")
        lines.append("")

        # Per-seed paired comparison
        if "default" in ct_groups and "sprint2" in ct_groups:
            lines.append("### Per-seed paired comparison")
            lines.append("| seed | default | sprint2 | delta |")
            lines.append("|---:|---:|---:|---:|")
            ct_lookup: dict[tuple[str, int], int] = {}
            for r in rows:
                if r.get("phase") == "ct" and r.get("score") is not None:
                    ct_lookup[(r["variant"], r["seed"])] = r["score"]
            seeds = sorted({r["seed"] for r in rows if r.get("phase") == "ct" and r.get("seed") is not None})
            for seed in seeds:
                d_val = ct_lookup.get(("default", seed))
                s_val = ct_lookup.get(("sprint2", seed))
                delta = (s_val - d_val) if (d_val is not None and s_val is not None) else None
                d_str = f"{d_val}/11" if d_val is not None else "—"
                s_str = f"{s_val}/11" if s_val is not None else "—"
                delta_str = f"+{delta}" if (delta is not None and delta > 0) else (str(delta) if delta is not None else "—")
                lines.append(f"| {seed} | {d_str} | {s_str} | {delta_str} |")
            lines.append("")

    # Stacked-winner ablation (abl): group by cell, 10 seeds each
    if any(r.get("phase") == "abl" for r in rows):
        abl_groups: dict[str, list[int]] = defaultdict(list)
        for r in rows:
            if r.get("phase") == "abl" and r.get("score") is not None:
                abl_groups[r.get("cell", "?")].append(r["score"])

        lines.append("## Stacked-winner ablation — which knob breaks the stack?")
        lines.append("Reference: stacked-full (035) mean 2.40/11. Look for cells")
        lines.append("where mean RECOVERS to ≥ 4-5/11 — that knob is the saboteur.")
        lines.append("")
        lines.append("| cell | n_seeds | mean n/11 | 95% CI | std |")
        lines.append("|---|---:|---:|---|---:|")
        for cell in sorted(abl_groups):
            scores = abl_groups[cell]
            m, lo, hi = bootstrap_ci(scores)
            std = float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0
            lines.append(f"| `{cell}` | {len(scores)} | **{m:.2f}** | "
                         f"[{lo:.2f}, {hi:.2f}] | {std:.2f} |")
        lines.append("")

    # Stacked winner (sw): single config × multiple seeds
    if any(r.get("phase") == "sw" for r in rows):
        sw_scores = [r["score"] for r in rows
                     if r.get("phase") == "sw" and r.get("score") is not None]
        if sw_scores:
            m, lo, hi = bootstrap_ci(sw_scores)
            std = float(np.std(sw_scores, ddof=1)) if len(sw_scores) > 1 else 0.0
            lines.append("## Stacked winner — Sprint 2 + chunk=128 + hidden=96 + init=0.1")
            lines.append(f"| n_seeds | mean n/11 | 95% CI | std |")
            lines.append("|---:|---:|---|---:|")
            lines.append(f"| {len(sw_scores)} | **{m:.2f}** | "
                         f"[{lo:.2f}, {hi:.2f}] | {std:.2f} |")
            lines.append("")

            # Histogram
            from collections import Counter
            counter = Counter(sw_scores)
            lines.append("### Distribution")
            for s in range(0, 12):
                n = counter.get(s, 0)
                bar = "█" * n
                lines.append(f"  {s}/11: {bar} ({n})")
            lines.append("")

    # Loss noise fix (pcfix): group by chunk
    if any(r.get("phase") == "pcfix" for r in rows):
        pcfix_groups: dict[int, list[int]] = defaultdict(list)
        for r in rows:
            if r.get("phase") == "pcfix" and r.get("score") is not None:
                pcfix_groups[r["chunk"]].append(r["score"])

        lines.append("## Loss noise fix — by chunk")
        lines.append("| chunk | n_seeds | mean n/11 | 95% CI | std |")
        lines.append("|---:|---:|---:|---|---:|")
        for chunk in sorted(pcfix_groups):
            scores = pcfix_groups[chunk]
            m, lo, hi = bootstrap_ci(scores)
            std = float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0
            lines.append(f"| {chunk} | {len(scores)} | **{m:.2f}** | "
                         f"[{lo:.2f}, {hi:.2f}] | {std:.2f} |")
        lines.append("")

    # Phase C-style: group by chunk
    if any(r.get("phase") == "pc" for r in rows):
        lines.append("## Group by chunk")
        lines.append("| chunk | n_seeds | mean n/11 | 95% CI | std |")
        lines.append("|---:|---:|---:|---|---:|")
        groups: dict[int, list[int]] = defaultdict(list)
        for r in rows:
            if r.get("phase") == "pc" and r.get("score") is not None:
                groups[r["chunk"]].append(r["score"])
        for chunk in sorted(groups):
            scores = groups[chunk]
            m, lo, hi = bootstrap_ci(scores)
            std = float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0
            lines.append(f"| {chunk} | {len(scores)} | **{m:.2f}** | "
                         f"[{lo:.2f}, {hi:.2f}] | {std:.2f} |")
        lines.append("")

        # Per-seed across chunks
        lines.append("## Per-seed across chunks (looking for seed dominance)")
        lines.append("| seed | chunk=24 | chunk=64 | chunk=128 |")
        lines.append("|---:|---:|---:|---:|")
        seed_lookup: dict[tuple[int, int], int] = {}
        for r in rows:
            if r.get("phase") == "pc" and r.get("score") is not None:
                seed_lookup[(r["seed"], r["chunk"])] = r["score"]
        for seed in sorted({r.get("seed") for r in rows if r.get("seed") is not None}):
            line = f"| {seed} |"
            for c in (24, 64, 128):
                v = seed_lookup.get((seed, c))
                line += f" {v}/11 |" if v is not None else " — |"
            lines.append(line)
        lines.append("")

    # Phase H-style: group by (group, variant)
    if any(r.get("phase") == "ph" for r in rows):
        ph_groups: dict[tuple[str, str], list[int]] = defaultdict(list)
        for r in rows:
            if r.get("phase") == "ph" and r.get("score") is not None:
                key = (r.get("group", "?"), r.get("variant", "?"))
                ph_groups[key].append(r["score"])

        # Group by axis
        lines.append("## Phase H — by axis × variant")
        for axis in ("lr", "iters", "init", "n_seeds"):
            entries = [(v, scores) for (g, v), scores in ph_groups.items() if g == axis]
            if not entries:
                continue
            lines.append(f"### Axis `{axis}`")
            lines.append("| variant | n_seeds | mean n/11 | 95% CI | std |")
            lines.append("|---|---:|---:|---|---:|")
            for variant, scores in sorted(entries):
                m, lo, hi = bootstrap_ci(scores)
                std = float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0
                lines.append(f"| `{variant}` | {len(scores)} | **{m:.2f}** | "
                             f"[{lo:.2f}, {hi:.2f}] | {std:.2f} |")
            lines.append("")

        # 10-seed distribution histogram for n_seeds group
        n_seeds_group = ph_groups.get(("n_seeds", "default"), [])
        if n_seeds_group:
            lines.append("### 10-seed distribution at default config")
            from collections import Counter
            counter = Counter(n_seeds_group)
            for s in range(0, 12):
                n = counter.get(s, 0)
                bar = "█" * n
                lines.append(f"  {s}/11: {bar} ({n})")
            lines.append("")

    # Top 10 individual scores
    ranked = sorted([r for r in rows if r["score"] is not None],
                    key=lambda x: -x["score"])[:10]
    lines.append("## Top 10 individual runs")
    lines.append("| run | n/11 |")
    lines.append("|---|---:|")
    for r in ranked:
        lines.append(f"| `{r['label']}` | **{r['score']}/11** |")
    lines.append("")

    out = cfg_dir / "scoreboard.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
