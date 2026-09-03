from __future__ import annotations

import sys
from pathlib import Path

import pytest

FIGURES = Path(__file__).resolve().parents[1] / "papers/paper_d_constraints/figures"
if str(FIGURES) not in sys.path:
    sys.path.insert(0, str(FIGURES))

from make_pdebench_unet_macros import make_macros  # noqa: E402


def _analysis(primary_class: str, material_cells: int) -> dict[str, object]:
    classes = [primary_class] + [
        "material_nonadditivity" if index < material_cells - 1 else "practical_additivity"
        for index in range(11)
    ]
    effects = {
        key: {"mean": 1.0, "ci": [0.5, 1.5]}
        for key in ("I_bundle", "T0", "T1", "E0", "E1", "phi_train", "phi_infer")
    }
    cells = {
        key: 1.0
        for key in ("A00", "R00", "A01", "R01", "A10", "R10", "A11", "R11")
    }
    all_cases = [
        {"three_way_interaction": {"classification": classification}}
        for classification in classes
    ]
    return {
        "schema_version": "constraint-iclr-pdebench-enforcement-cube-analysis-v1",
        "benchmark_id": "pdebench_advection_beta0.4_unet_factorial_v1",
        "integrity_gates_passed": True,
        "core_record_count": 150,
        "derived_record_count": 90,
        "checkpoint_count": 120,
        "core_input_sha256": "a" * 64,
        "core_analysis_sha256": "b" * 64,
        "checkpoint_lock_sha256": "c" * 64,
        "derived_input_sha256": "d" * 64,
        "primary": {
            "case": "ood_r512",
            "horizon": 16,
            "three_way_interaction": {
                "mean": 2.0,
                "ci95": [1.5, 2.5],
                "sesoi": 0.5,
                "classification": primary_class,
                "sign_flip_p_holm": 0.01,
            },
            "effects": effects,
            "cell_mean_conserving_rmse": cells,
        },
        "all_cases": all_cases,
    }


def test_unet_macro_admission_requires_primary_and_six_cells() -> None:
    macros = make_macros(_analysis("material_nonadditivity", 6))
    assert r"\newcommand{\UNetAdmission}{passed}" in macros
    assert r"\newcommand{\UNetMaterialCells}{6}" in macros
    macros = make_macros(_analysis("material_nonadditivity", 5))
    assert r"\newcommand{\UNetAdmission}{did not pass}" in macros


def test_unet_macro_generator_rejects_wrong_benchmark() -> None:
    analysis = _analysis("material_nonadditivity", 6)
    analysis["benchmark_id"] = "wrong"
    with pytest.raises(ValueError, match="benchmark"):
        make_macros(analysis)
