from __future__ import annotations

from pathlib import Path

import yaml

from ecomd.eval.evaluator_v2 import METRIC_NAMES

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_sample_complexity_contract_is_complete_and_result_bound() -> None:
    protocol = yaml.safe_load(
        (REPO_ROOT / "configs/evaluator_v2/sample_complexity_v1.yaml").read_text()
    )
    assert protocol["contract"]["status"] == (
        "frozen_after_feasibility_v1_before_any_synthetic_metric_outputs"
    )
    assert protocol["contract"]["source_feasibility_result_canonical_sha256"] == (
        "057946d365686cc4e63c13e8db3d547e83601560d701e3ac52e39f572438d25f"
    )
    assert protocol["monte_carlo"] == {
        "lengths": [120, 180, 240, 500, 1000, 2000, 4000],
        "replications_per_length": 64,
        "surrogate_replicates_per_path": 8,
        "root_seed": 812100,
        "burn_in": 2000,
        "sequential_cpu_execution": True,
    }
    assert tuple(protocol["metric_tests"]) == METRIC_NAMES
    assert protocol["metric_tests"]["hill_tail_index"]["analytic_min_length"] == 500
    assert protocol["metric_tests"]["intermittency_fano"]["analytic_min_length"] == 2000
    assert protocol["metric_tests"]["zumbach_asymmetry"]["diagnostic_only"] is True
    assert protocol["gates"]["complete_real_and_all_surrogate_fraction"] == 1.0
    assert protocol["decision"]["no_post_result_dgp_parameter_threshold_or_grid_changes"] is True
    assert protocol["compute"] == {
        "cpu_only": True,
        "gpu_forbidden": True,
        "paid_data_forbidden": True,
        "h20_forbidden": True,
    }
