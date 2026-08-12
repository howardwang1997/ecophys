from __future__ import annotations

import importlib.util
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from typing import cast

import numpy as np
import pytest
import yaml

from ecomd.research.market_rule_feedback_preflight import (
    GeneratedPanel,
    bias_bound_oracle,
    canonical_stream_label,
    differential_attrition_detected,
    distinct_mass_points_by_side,
    fit_rdrobust,
    generate_panel,
    rng_for_stream,
    shared_rule_reason,
    sorting_detected,
    statutory_tick,
    tick_first_stage,
    wilson_interval,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "experiments/147_generated_market_rule_feedback_rd/config.yaml"
RUNNER_PATH = ROOT / "experiments/147_generated_market_rule_feedback_rd/run_preflight.py"


def _config() -> dict[str, object]:
    raw: object = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    return cast(dict[str, object], raw)


def _scenario(config: Mapping[str, object], section: str, name: str) -> Mapping[str, object]:
    entries = config[section]
    assert isinstance(entries, list)
    matches = [entry for entry in entries if isinstance(entry, dict) and entry.get("name") == name]
    assert len(matches) == 1
    return matches[0]


def _load_runner() -> object:
    spec = importlib.util.spec_from_file_location("exp147_run_preflight", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_frozen_stream_is_order_independent_and_canonical() -> None:
    label = canonical_stream_label(
        seed=14720260813,
        scenario="smooth_null",
        cutoff=10.0,
        sigma=0.1,
        replicate=7,
        float_format=".12g",
    )
    first = rng_for_stream(
        seed=14720260813,
        scenario="smooth_null",
        cutoff=10.0,
        sigma=0.1,
        replicate=7,
        float_format=".12g",
    ).normal(size=4)
    second = rng_for_stream(
        seed=14720260813,
        scenario="smooth_null",
        cutoff=10.0,
        sigma=0.1,
        replicate=7,
        float_format=".12g",
    ).normal(size=4)

    assert label == "14720260813|smooth_null|10|0.1|7"
    np.testing.assert_array_equal(first, second)
    np.testing.assert_allclose(
        first,
        np.asarray([0.9143921391187628, -0.26316332922535773, 0.33319780960406437, 0.3829324431158713]),
        rtol=0.0,
        atol=1.0e-15,
    )


def test_standard_and_clustered_panels_obey_frozen_shape_and_effect() -> None:
    config = _config()
    standard = generate_panel(
        config,
        _scenario(config, "effect_scenarios", "reinforcing"),
        cutoff=10.0,
        sigma=0.1,
        replicate=0,
    )
    clustered = generate_panel(
        config,
        _scenario(config, "effect_scenarios", "clustered_reinforcing"),
        cutoff=10.0,
        sigma=0.1,
        replicate=0,
    )

    assert standard.x.shape == (1440,)
    assert standard.cluster is None
    assert standard.true_tau == 0.05
    assert clustered.cluster is not None
    assert np.unique(clustered.cluster).size == 240
    assert all(np.count_nonzero(clustered.cluster == identifier) == 6 for identifier in range(240))


def test_regression_to_mean_is_a_zero_assignment_effect_case() -> None:
    config = _config()
    panel = generate_panel(
        config,
        _scenario(config, "null_scenarios", "regression_to_mean_null"),
        cutoff=600.0,
        sigma=0.1,
        replicate=2,
    )

    assert panel.true_tau == 0.0
    assert panel.x.min() >= np.log(0.8) - 1.0e-12
    assert panel.x.max() <= np.log(1.2) + 1.0e-12
    assert np.unique(panel.x).size > 100


def test_rdrobust_wrapper_extracts_bias_corrected_robust_row() -> None:
    config = _config()
    estimator = config["estimator"]
    assert isinstance(estimator, dict)
    x = np.concatenate([np.linspace(-0.2, -0.001, 120), np.linspace(0.0, 0.2, 120)])
    year = np.tile(np.arange(2018, 2024), 40).astype(np.int64)
    year_effect = 0.01 * (year - 2020.5)
    y = 0.5 * x + 0.4 * x**2 + year_effect + 0.05 * (x >= 0.0) + 0.005 * np.sin(np.arange(x.size))
    panel = GeneratedPanel(
        x=x,
        y=y,
        year=year,
        cluster=None,
        true_tau=0.05,
        known_year_effect=year_effect,
    )

    result = fit_rdrobust(panel, estimator, minimum_mass_points=10)

    assert result.vce == "HC3"
    assert result.ci_low < 0.05 < result.ci_high
    assert abs(result.estimate - 0.05) < 0.01
    assert result.n_left == result.n_right == 120


def test_rdrobust_wrapper_preserves_frozen_cr3_path() -> None:
    config = deepcopy(_config())
    config["n_candidates_per_year"] = 40
    config["cluster_count"] = 40
    estimator = config["estimator"]
    assert isinstance(estimator, dict)
    panel = generate_panel(
        config,
        _scenario(config, "effect_scenarios", "clustered_reinforcing"),
        cutoff=10.0,
        sigma=0.1,
        replicate=5,
    )

    result = fit_rdrobust(panel, estimator, minimum_mass_points=10)

    assert result.vce == "CR3"
    assert result.n_left + result.n_right == 240
    assert np.isfinite(result.estimate)


def test_rdrobust_wrapper_refuses_coarse_support_before_fit() -> None:
    config = _config()
    estimator = config["estimator"]
    assert isinstance(estimator, dict)
    x = np.log(np.round(10.0 * np.linspace(0.8, 1.2, 240)) / 10.0)
    year = np.tile(np.arange(2018, 2024), 40).astype(np.int64)
    panel = GeneratedPanel(
        x=x,
        y=np.zeros(x.size),
        year=year,
        cluster=None,
        true_tau=0.0,
        known_year_effect=np.zeros(x.size),
    )

    with pytest.raises(ValueError, match="mass points"):
        fit_rdrobust(panel, estimator, minimum_mass_points=10)


def test_bias_bound_oracle_covers_deterministic_quadratic_fixture() -> None:
    x = np.concatenate([np.linspace(-0.18, -0.002, 100), np.linspace(0.0, 0.18, 100)])
    year = np.tile(np.arange(2018, 2024), 34)[: x.size].astype(np.int64)
    year_effect = 0.01 * (year - 2020.5)
    y = 0.5 * x + 0.4 * x**2 + year_effect
    panel = GeneratedPanel(
        x=x,
        y=y,
        year=year,
        cluster=None,
        true_tau=0.0,
        known_year_effect=year_effect,
    )

    result = bias_bound_oracle(
        panel,
        bandwidth=0.18,
        curvature_bound=0.8,
        sigma=0.1,
        confidence_level=0.95,
        minimum_mass_points=10,
    )

    assert result.ci_low <= 0.0 <= result.ci_high
    assert result.bias_bound > 0.0
    assert result.mass_points_left == result.mass_points_right == 100


def test_diagnostics_detect_strong_microfixtures_and_mass_point_failure() -> None:
    sorting, sorting_p, x = sorting_detected(
        np.random.default_rng(12),
        sample_size=400,
        bandwidth=0.18,
        right_probability=0.75,
        alpha=0.01,
    )
    attrition, attrition_p = differential_attrition_detected(
        np.random.default_rng(13),
        sample_size=1000,
        base_probability=0.05,
        right_side_increment=0.30,
        positive_shock_increment=0.15,
        alpha=0.01,
    )
    coarse = np.log(np.round(10.0 * np.linspace(0.8, 1.2, 400)) / 10.0)

    assert sorting and sorting_p < 0.01
    assert attrition and attrition_p < 0.01
    assert distinct_mass_points_by_side(x, bandwidth=0.18)[0] > 10
    assert min(distinct_mass_points_by_side(coarse, bandwidth=0.18)) < 10


def test_rule_guards_use_registry_and_full_statutory_table() -> None:
    assert shared_rule_reason(80.0, [80.0, 2000.0]) == "COINCIDENT_RTS28_REPORTING_BOUNDARY"
    assert shared_rule_reason(600.0, [80.0, 2000.0]) is None
    assert statutory_tick(0.05, 1) == 0.0005
    assert statutory_tick(50000.0, 6) == 10.0
    assert tick_first_stage(10.0, 0.05) == (True, 0.0005, 0.0002)
    assert tick_first_stage(600.0, 0.05) == (False, 0.0001, 0.0001)
    assert tick_first_stage(600.0, 1.0) == (True, 0.002, 0.001)
    assert tick_first_stage(9000.0, 0.2) == (False, 0.0001, 0.0001)
    assert tick_first_stage(9000.0, 1.0) == (True, 0.0005, 0.0002)


def test_wilson_interval_and_invalid_inputs() -> None:
    low, high = wilson_interval(15, 300, 0.95)

    assert low < 0.05 < high
    with pytest.raises(ValueError, match="Wilson"):
        wilson_interval(1, 0, 0.95)
    with pytest.raises(ValueError, match="statutory"):
        tick_first_stage(123.0, 1.0)


def test_runner_cell_summary_applies_every_null_gate() -> None:
    runner = _load_runner()
    config = _config()
    replicate_results: list[dict[str, object]] = []
    for replicate in range(300):
        significant = replicate < 15
        replicate_results.append(
            {
                "replicate": replicate,
                "fit_failure": False,
                "oracle_failure": False,
                "estimate": {
                    "estimate": 0.0,
                    "p_value": 0.01 if significant else 0.5,
                    "ci_low": -0.1,
                    "ci_high": 0.1,
                },
            }
        )

    summary = runner._cell_summary(
        scenario_name="constructed_null",
        cutoff=10.0,
        sigma=0.1,
        true_tau=0.0,
        replicate_results=replicate_results,
        config=config,
        is_null=True,
        is_descriptive=False,
        oracle_required=False,
    )

    assert summary["significant_rate"] == 0.05
    assert summary["gate_pass"] is True
    assert all(summary["gate_checks"].values())


def test_runner_network_audit_hook_and_zero_success_summary_fail_closed() -> None:
    runner = _load_runner()
    config = _config()
    with pytest.raises(PermissionError, match="network disabled"):
        runner._network_audit_hook("socket.connect", ())

    replicate_results = [
        {
            "replicate": replicate,
            "fit_failure": True,
            "fit_error_type": "LinAlgError",
            "fit_error": "fixture",
            "oracle_failure": False,
        }
        for replicate in range(12)
    ]
    summary = runner._cell_summary(
        scenario_name="constructed_failure",
        cutoff=10.0,
        sigma=0.1,
        true_tau=0.0,
        replicate_results=replicate_results,
        config=config,
        is_null=True,
        is_descriptive=False,
        oracle_required=False,
    )

    assert summary["successful_fits"] == 0
    assert summary["gate_pass"] is False
    assert summary["gate_checks"]["successful_fits"] is False
