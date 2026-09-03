from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "papers/paper_d_constraints/figures"
sys.path.insert(0, str(FIGURES))

from make_pdebench_gauge_feedback_macros import (  # noqa: E402
    make_macros as make_gauge_macros,
)
from make_pdebench_swe_macros import make_macros as make_swe_macros  # noqa: E402
from make_synthetic_amended_table import make_macros as make_synthetic_macros  # noqa: E402


def _summary(mean: float = 0.1) -> dict[str, object]:
    return {"mean": mean, "ci": [mean - 0.01, mean + 0.01]}


def _analyses() -> tuple[dict[str, object], dict[str, object]]:
    interaction = {
        "mean": 0.1,
        "ci95": [0.08, 0.12],
        "sesoi": 0.01,
        "classification": "material_nonadditivity",
        "sign_flip_p_holm": 0.001,
    }
    core = {
        "schema_version": "constraint-iclr-pdebench-swe-factorial-analysis-v1",
        "benchmark_id": "swe-test",
        "record_count": 150,
        "integrity_gates_passed": True,
        "primary": {
            "case": "ood_r128",
            "horizon": 16,
            "interaction": {
                "mean": 0.01,
                "ci95": [0.001, 0.02],
                "classification": "statistical_nonadditivity_below_or_crossing_sesoi",
            },
        },
    }
    effects = {name: _summary() for name in ("I_bundle", "T0", "T1", "E0", "E1", "phi_train", "phi_infer")}
    tradeoff_metrics = {
        name: {"infer_free_train": _summary()}
        for name in ("conservation", "positivity", "positivity_secondary", "dynamics")
    }
    primary = {
        "case": "ood_r128",
        "horizon": 16,
        "three_way_interaction": interaction,
        "cell_mean_primary_metric": {
            name: 0.1 for name in ("A00", "R00", "A01", "R01", "A10", "R10", "A11", "R11")
        },
        "effects": effects,
    }
    cube = {
        "schema_version": "constraint-iclr-pdebench-swe-enforcement-cube-analysis-v1",
        "benchmark_id": "swe-test",
        "core_record_count": 150,
        "derived_record_count": 90,
        "checkpoint_count": 120,
        "core_analysis_sha256": "a" * 64,
        "integrity_gates_passed": True,
        "primary": primary,
        "all_cases": [{"three_way_interaction": interaction} for _ in range(8)],
        "conservation_positivity_tradeoff": {
            "case": "ood_r128",
            "horizon": 31,
            "classification": "resolved_conservation_positivity_tradeoff",
            "metrics": tradeoff_metrics,
        },
    }
    return core, cube


def test_swe_macros_require_complete_bound_analyses_and_valid_tex_names() -> None:
    core, cube = _analyses()
    content = make_swe_macros(core, cube, core_analysis_sha256="a" * 64)
    commands = re.findall(r"\\newcommand\{\\([^}]+)\}", content)
    assert commands
    assert all(re.fullmatch(r"[A-Za-z]+", command) for command in commands)
    assert r"\newcommand{\SWEJ}{0.10000}" in content
    assert r"\newcommand{\SWEJOverSesoi}{10.0}" in content
    assert r"\newcommand{\SWETradeoffClassification}" in content

    cube["core_analysis_sha256"] = "b" * 64
    with pytest.raises(ValueError, match="not bound"):
        make_swe_macros(core, cube, core_analysis_sha256="a" * 64)


def test_gauge_feedback_macros_require_exact_complete_analysis() -> None:
    analysis = {
        "schema_version": "constraint-iclr-pdebench-gauge-feedback-analysis-v1",
        "integrity_gates_passed": True,
        "record_count": 60,
        "checkpoint_count": 120,
        "practical_ratio_threshold": 0.10,
        "primary": {
            "case": "ood_r512",
            "classification": "material_gauge_feedback",
            "coordinate_average_feedback_ratio": {
                "mean": 0.25,
                "ci95": [0.20, 0.30],
            },
            "coordinate_average_feedback_rmse": {
                "mean": 0.02,
                "ci95": [0.01, 0.03],
            },
            "by_coordinate_feedback_ratio": {
                "hard_abs": {"mean": 0.30, "ci95": [0.25, 0.35]},
                "hard": {"mean": 0.20, "ci95": [0.15, 0.25]},
            },
        },
        "secondary_final_harm_association": {
            "classification": "not_supported",
            "rho": 0.1,
            "ci95": [-0.2, 0.4],
        },
    }
    content = make_gauge_macros(analysis)
    commands = re.findall(r"\\newcommand\{\\([^}]+)\}", content)
    assert commands
    assert all(re.fullmatch(r"[A-Za-z]+", command) for command in commands)
    assert r"\newcommand{\GaugeRatio}{0.25000}" in content
    assert r"\newcommand{\GaugeRatioOverThreshold}{2.5}" in content
    assert r"\newcommand{\GaugeClassification}{material gauge feedback}" in content

    analysis["record_count"] = 59
    with pytest.raises(ValueError, match="exact frozen coverage"):
        make_gauge_macros(analysis)


def test_gauge_feedback_v2_macros_require_contamination_gate() -> None:
    analysis = {
        "schema_version": "constraint-iclr-pdebench-gauge-feedback-analysis-v2",
        "integrity_gates_passed": True,
        "record_count": 60,
        "checkpoint_count": 120,
        "practical_ratio_threshold": 0.10,
        "identity_integrity": {
            "max_contamination_fraction": 0.0001,
            "relative_to_projected_baseline_max": 0.001,
        },
        "primary": {
            "case": "ood_r512",
            "classification": "material_gauge_feedback",
            "coordinate_average_feedback_ratio": {
                "mean": 0.25,
                "ci95": [0.20, 0.30],
            },
            "coordinate_average_feedback_rmse": {
                "mean": 0.02,
                "ci95": [0.01, 0.03],
            },
            "by_coordinate_feedback_ratio": {
                "hard_abs": {"mean": 0.30, "ci95": [0.25, 0.35]},
                "hard": {"mean": 0.20, "ci95": [0.15, 0.25]},
            },
        },
        "all_cases": [{"classification": "material_gauge_feedback"} for _ in range(3)],
        "secondary_final_harm_association": {
            "classification": "not_supported",
            "rho": 0.1,
            "ci95": [-0.2, 0.4],
        },
    }
    content = make_gauge_macros(analysis)
    assert r"\newcommand{\GaugeMaxContamination}{0.00010}" in content
    assert r"\newcommand{\GaugeMaterialCases}{3}" in content
    analysis["identity_integrity"]["max_contamination_fraction"] = 0.01
    with pytest.raises(ValueError, match="contamination gate failed"):
        make_gauge_macros(analysis)


def test_generated_advection_cube_macros_have_valid_tex_names() -> None:
    content = (FIGURES / "pdebench_cube_macros.tex").read_text(encoding="utf-8")
    commands = re.findall(r"\\newcommand\{\\([^}]+)\}", content)
    assert commands
    assert all(re.fullmatch(r"[A-Za-z]+", command) for command in commands)
    assert "-0.0" not in (FIGURES / "pdebench_cube_rows.tex").read_text(encoding="utf-8")


def test_synthetic_macros_report_integrity_gated_counts() -> None:
    analysis_path = (
        ROOT
        / "experiments/constraint_attribution_iclr/confirmation/formal_amended_20260901/"
        "analysis_amended_20260901.json"
    )
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    content = make_synthetic_macros(analysis)
    assert r"\newcommand{\SyntheticSystems}{8}" in content
    assert r"\newcommand{\SyntheticParameterizationHolm}{8}" in content
    assert r"\newcommand{\SyntheticResidualFavored}{6}" in content
    assert r"\newcommand{\SyntheticEquivalent}{6}" in content
    assert r"\newcommand{\SyntheticFullPass}{1}" in content
