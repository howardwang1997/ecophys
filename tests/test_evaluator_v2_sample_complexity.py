from __future__ import annotations

from pathlib import Path

import numpy as np
import yaml

from ecomd.eval.stylized_facts import (
    acf_squared_returns,
    gain_loss_asymmetry,
    leverage_effect,
    volume_volatility_corr,
)
from ecomd.eval.synthetic_dgps import dgp_registry, simulate_dgp
from scripts.run_evaluator_v2_sample_complexity import (
    evaluate_protocol,
    suffix_admissible_minimum,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _registry() -> dict[str, dict[str, object]]:
    protocol = yaml.safe_load(
        (REPO_ROOT / "configs/evaluator_v2/sample_complexity_v1.yaml").read_text()
    )
    return dgp_registry(protocol["dgp"])


def test_every_frozen_dgp_is_finite_aligned_and_deterministic() -> None:
    registry = _registry()
    for name in registry:
        left = simulate_dgp(name, length=256, burn_in=200, seed=17, registry=registry)
        right = simulate_dgp(name, length=256, burn_in=200, seed=17, registry=registry)
        assert left.volume is not None
        assert left.returns.shape == (256,)
        assert left.volume.shape == (256,)
        assert np.all(np.isfinite(left.returns))
        assert np.all(np.isfinite(left.volume))
        np.testing.assert_array_equal(left.returns, right.returns)
        np.testing.assert_array_equal(left.volume, right.volume)


def test_signal_dgps_contain_their_declared_structures() -> None:
    registry = _registry()
    negative = simulate_dgp(
        "negative_jump_iid", length=20_000, burn_in=2_000, seed=31, registry=registry
    )
    assert gain_loss_asymmetry(negative.returns).estimate < -1.0

    garch = simulate_dgp(
        "garch_gaussian", length=10_000, burn_in=2_000, seed=41, registry=registry
    )
    iid = simulate_dgp(
        "student_t3_iid", length=10_000, burn_in=2_000, seed=41, registry=registry
    )
    assert acf_squared_returns(garch.returns).estimate > 0.03
    assert acf_squared_returns(garch.returns).estimate > acf_squared_returns(iid.returns).estimate

    asymmetric = simulate_dgp(
        "gjr_garch", length=10_000, burn_in=2_000, seed=43, registry=registry
    )
    symmetric_leverage = leverage_effect(garch.returns).estimate
    asymmetric_leverage = leverage_effect(asymmetric.returns).estimate
    assert asymmetric_leverage < -0.1
    assert asymmetric_leverage < symmetric_leverage

    coupled = simulate_dgp(
        "garch_volume_coupled", length=10_000, burn_in=2_000, seed=47, registry=registry
    )
    independent = simulate_dgp(
        "garch_volume_independent", length=10_000, burn_in=2_000, seed=47, registry=registry
    )
    assert coupled.volume is not None
    assert independent.volume is not None
    coupled_corr = volume_volatility_corr(coupled.returns, coupled.volume).estimate
    independent_corr = volume_volatility_corr(
        independent.returns, independent.volume
    ).estimate
    assert coupled_corr > 0.5
    assert abs(independent_corr) < 0.1


def test_suffix_minimum_rejects_an_earlier_isolated_pass() -> None:
    lengths = [120, 240, 500, 1000]
    assert suffix_admissible_minimum(
        lengths,
        {120: True, 240: False, 500: True, 1000: True},
    ) == 500
    assert suffix_admissible_minimum(
        lengths,
        {120: True, 240: True, 500: True, 1000: False},
    ) is None


def test_reduced_execution_smoke_covers_every_frozen_cell() -> None:
    protocol = yaml.safe_load(
        (REPO_ROOT / "configs/evaluator_v2/sample_complexity_v1.yaml").read_text()
    )
    protocol["monte_carlo"]["replications_per_length"] = 1
    protocol["monte_carlo"]["surrogate_replicates_per_path"] = 1
    protocol["monte_carlo"]["burn_in"] = 50
    result = evaluate_protocol(protocol)
    assert set(result["cells"]) == set(protocol["metric_tests"])
    assert all(
        set(metric_cells) == {"120", "180", "240", "500", "1000", "2000", "4000"}
        for metric_cells in result["cells"].values()
    )
    assert result["decisions"]["zumbach_asymmetry"]["metric_admissible"] is None
