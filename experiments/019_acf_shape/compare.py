"""ACF(r²) decay-shape comparison across architectures + real data.

Shows quantitatively what Paper A claims about "v0.x produces peak-decay,
v2.0 flat, v2.1 recovers shape." Aggregates per-lag ACF curves from the
already-trained-and-saved checkpoints under experiments/.

Output:
  results/acf_shape_data.json — per-architecture ACF curve mean ± std
  results/acf_shape_comparison.md — markdown table for Paper A

This is post-hoc analysis on existing eval JSONs (no retraining).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "results"


def acf_curve_from_realizations(realizations: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    """Pull per-lag ACF(r²) array from a stylized-facts realizations list.
    Returns (mean_curve, std_curve). Lag-0 is at index 0 (=1.0).
    """
    curves = []
    for r in realizations:
        # Different schema between experiments — handle both
        facts = r.get("facts") or r.get("results", {})
        diag = facts.get("acf_squared_returns", {}).get("diagnostic", {})
        if not diag:
            continue
        acf = diag.get("acf", [])
        if acf:
            curves.append(np.array(acf))
    if not curves:
        return np.array([]), np.array([])
    # Trim to common min length
    min_len = min(len(c) for c in curves)
    curves = np.stack([c[:min_len] for c in curves])
    return curves.mean(axis=0), curves.std(axis=0)


def load_arch(label: str, json_path: Path) -> dict:
    """Read a stylized-facts JSON and return per-lag ACF stats."""
    if not json_path.exists():
        return {"label": label, "missing": True, "path": str(json_path)}
    d = json.loads(json_path.read_text())
    realiz = d.get("realizations") or d
    if isinstance(realiz, dict):
        # Some files have aggregated only — try fallback
        realiz = [d]
    elif isinstance(realiz, list) and realiz and "results" not in realiz[0] and "facts" not in realiz[0]:
        # Top-level format with single result inside
        realiz = [{"facts": d.get("results", {})}]
    mean, std = acf_curve_from_realizations(realiz)
    return {
        "label": label,
        "path": str(json_path.relative_to(REPO)),
        "n_realizations": len(realiz),
        "acf_mean": mean.tolist() if mean.size else [],
        "acf_std": std.tolist() if std.size else [],
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    sources = [
        ("Real SPX daily", REPO / "experiments/000_reference_values/results/stylized_facts_spx_2015-2026_daily.json"),
        ("v0.6 trained (Mac)", REPO / "experiments/005_ecomd_v0p6/results/ecomd_v0p6_stylized_facts.json"),
        ("v0.8 trained (Mac)", REPO / "experiments/011_ecomd_v0p8/results/ecomd_v0p8_stylized_facts.json"),
        ("v0.7 trained (Mac, σ↓)", REPO / "experiments/010_ecomd_v0p7/results/ecomd_v0p7_stylized_facts.json"),
        ("v1 MACE H hybrid", REPO / "experiments/008_ecomd_v1_ablation/results/H_F4_hybrid_stylized_facts.json"),
        ("v1 MACE A_matched", REPO / "experiments/008_ecomd_v1_ablation/results/A_matched_stylized_facts.json"),
    ]

    results = []
    for label, path in sources:
        r = load_arch(label, path)
        if r.get("missing"):
            print(f"  [skip] {label}: file missing — {path}")
            continue
        if r.get("acf_mean"):
            mean = r["acf_mean"]
            print(f"{label:<35}  n={r['n_realizations']}  "
                  f"lag1={mean[1] if len(mean) > 1 else 'n/a':+.3f}  "
                  f"lag10={mean[10] if len(mean) > 10 else 'n/a':+.3f}  "
                  f"lag16={mean[16] if len(mean) > 16 else 'n/a':+.3f}")
        results.append(r)

    (OUT / "acf_shape_data.json").write_text(json.dumps(results, indent=2))

    # Markdown table
    lines = [
        "# ACF(r²) decay shape — architecture comparison",
        "",
        "Real SPX daily ACF(r²) shows peak-decay: ~0.45 at lag 1, decays to ~0.11 at lag 16.",
        "Architectures that produce vol clustering correctly should show similar peak-decay.",
        "Flat curves indicate 'constant variance regime' — Goodhart-failure mode (single",
        "summary number passes but actual physics is wrong).",
        "",
        "| architecture | lag 1 | lag 5 | lag 10 | lag 16 | shape |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        if not r.get("acf_mean"):
            continue
        mean = r["acf_mean"]

        def get(i):
            return f"{mean[i]:+.3f}" if len(mean) > i else "—"

        # Classify shape
        if len(mean) > 16:
            ratio = mean[1] / max(abs(mean[10]), 1e-3)
            shape_label = "**peak-decay**" if ratio > 1.5 else "flat"
        else:
            shape_label = "—"

        lines.append(
            f"| {r['label']} | {get(1)} | {get(5)} | {get(10)} | {get(16)} | {shape_label} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "- **peak-decay** (lag1/lag10 > 1.5): real vol clustering — variance shocks decay over time.",
        "- **flat** (curve ~ constant): constant-variance regime, NOT vol clustering.",
        "- v1 MACE H hybrid is the canonical Goodhart case: passes #6 mean test but flat shape.",
    ]
    (OUT / "acf_shape_comparison.md").write_text("\n".join(lines))
    print(f"\nwrote {OUT/'acf_shape_comparison.md'}")


if __name__ == "__main__":
    main()
