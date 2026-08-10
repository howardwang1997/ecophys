from __future__ import annotations

import numpy as np

from ecomd.eval.evaluator_v2 import (
    SeriesBlock,
    assess_relation,
    build_nonoverlapping_blocks,
    deterministic_seed,
    finite_sample_order_index,
    make_surrogate,
    safe_estimate,
    split_conformal_interval,
)


def test_nonoverlapping_blocks_drop_remainder_and_preserve_alignment() -> None:
    returns = np.arange(10, dtype=np.float64)
    volume = np.arange(100, 110, dtype=np.float64)
    blocks = build_nonoverlapping_blocks(returns, volume, 4)
    assert len(blocks) == 2
    np.testing.assert_array_equal(blocks[0].returns, [0.0, 1.0, 2.0, 3.0])
    np.testing.assert_array_equal(blocks[1].returns, [4.0, 5.0, 6.0, 7.0])
    assert blocks[1].volume is not None
    np.testing.assert_array_equal(blocks[1].volume, [104.0, 105.0, 106.0, 107.0])


def test_finite_sample_split_conformal_and_insufficient_case() -> None:
    assert finite_sample_order_index(4, 0.2) == 4
    result = split_conformal_interval(
        reference=[0.0, 2.0],
        calibration=[0.5, 1.0, 1.5, 2.0],
        confirmation=[0.0, 2.0, 3.0, 1.0],
        temporal=[0.0, 2.0, 0.0, 2.0],
        report_only=[4.0],
        alpha=0.2,
        minimum_confirmation_coverage=0.75,
        minimum_temporal_coverage=0.75,
    )
    assert result.status == "ok"
    assert result.center == 1.0
    assert result.radius == 1.0
    assert result.confirmation_coverage == 0.75
    assert result.temporal_coverage == 1.0
    assert result.report_only_coverage == 0.0
    assert result.pass_both

    insufficient = split_conformal_interval(
        reference=[0.0, 1.0],
        calibration=[0.0, 1.0],
        confirmation=[0.0],
        temporal=[0.0],
        report_only=[],
        alpha=0.2,
        minimum_confirmation_coverage=0.75,
        minimum_temporal_coverage=0.75,
    )
    assert insufficient.calibration_order_index == 3
    assert insufficient.status == "finite_sample_order_exceeds_calibration_blocks"
    assert not insufficient.pass_both


def test_surrogates_are_deterministic_and_preserve_declared_invariants() -> None:
    returns = np.asarray([-3.0, -1.0, 0.5, 2.0, 4.0, 7.0], dtype=np.float64)
    volume = np.asarray([10.0, 20.0, 30.0, 40.0, 50.0, 60.0], dtype=np.float64)
    block = SeriesBlock(returns=returns, volume=volume)
    seed = deterministic_seed(811920, "SPX", "reference", 120, 0, "kind", 0)
    assert seed == deterministic_seed(811920, "SPX", "reference", 120, 0, "kind", 0)

    joint = make_surrogate(block, "temporal_joint_permutation", seed=seed)
    assert joint.volume is not None
    assert sorted(zip(joint.returns, joint.volume, strict=True)) == sorted(
        zip(returns, volume, strict=True)
    )
    repeated = make_surrogate(block, "temporal_joint_permutation", seed=seed)
    np.testing.assert_array_equal(joint.returns, repeated.returns)
    np.testing.assert_array_equal(joint.volume, repeated.volume)

    signed = make_surrogate(block, "sign_randomization", seed=seed)
    np.testing.assert_array_equal(np.abs(signed.returns), np.abs(returns))
    np.testing.assert_array_equal(signed.volume, volume)

    shifted = make_surrogate(block, "volume_alignment_break", seed=seed)
    np.testing.assert_array_equal(shifted.returns, returns)
    assert shifted.volume is not None
    assert not np.array_equal(shifted.volume, volume)
    np.testing.assert_array_equal(np.sort(shifted.volume), np.sort(volume))

    gaussian = make_surrogate(block, "gaussian_iid", seed=seed)
    np.testing.assert_allclose(
        np.mean(gaussian.returns), np.mean(returns), rtol=0.0, atol=1e-14
    )
    np.testing.assert_allclose(
        np.std(gaussian.returns, ddof=0),
        np.std(returns, ddof=0),
        rtol=0.0,
        atol=1e-14,
    )
    assert gaussian.volume is not None
    np.testing.assert_array_equal(np.sort(gaussian.volume), np.sort(volume))


def test_relation_assessment_uses_paired_medians_and_pooled_iqr() -> None:
    higher = assess_relation(
        real=[3.0, 4.0, 5.0, 6.0],
        controls=[[0.0, 1.0], [1.0, 2.0], [2.0, 3.0], [3.0, 4.0]],
        relation="real_higher",
        minimum_direction_fraction=0.75,
        minimum_abs_effect_iqr=0.5,
        maximum_abs_equivalence_effect_iqr=0.5,
    )
    assert higher.direction_fraction == 1.0
    assert higher.passed

    equivalent = assess_relation(
        real=[0.0, 1.0, 2.0, 3.0],
        controls=[[-1.0, 1.0], [0.0, 2.0], [1.0, 3.0], [2.0, 4.0]],
        relation="equivalent",
        minimum_direction_fraction=0.75,
        minimum_abs_effect_iqr=0.5,
        maximum_abs_equivalence_effect_iqr=0.5,
    )
    assert equivalent.median_effect_pooled_iqr_units == 0.0
    assert equivalent.passed


def test_frozen_short_block_estimators_fail_closed_instead_of_adapting() -> None:
    rng = np.random.default_rng(17)
    block = SeriesBlock(returns=rng.normal(size=120), volume=None)
    aggregation, aggregation_error = safe_estimate("aggregational_gaussianity", block)
    dfa, dfa_error = safe_estimate("dfa_hurst_abs_r", block)
    assert aggregation is None
    assert aggregation_error == (
        "ValueError: aggregational_gaussianity produced a non-finite estimate"
    )
    assert dfa is None
    assert dfa_error is not None and "max_scale=12 <= min_scale=16" in dfa_error
