from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from ecomd.observation.l2_emission import (
    AggregateL2EmissionConfig,
    SyntheticL2Stream,
    bernoulli_log_likelihood,
    emit_aggregate_l2,
    fit_flow_slope,
    fit_level_decay,
    fit_size_model,
    reconstruct_aggregate_book,
    simulate_latent_ar1,
)


def test_emitted_messages_reconstruct_every_queue_exactly() -> None:
    generator = np.random.default_rng(134)
    config = AggregateL2EmissionConfig()
    latent = simulate_latent_ar1(2_000, 0.8, generator)
    stream = emit_aggregate_l2(latent, 0.7, config, generator)
    reconstructed = reconstruct_aggregate_book(stream)
    np.testing.assert_array_equal(reconstructed, stream.snapshots)

    previous = np.empty_like(stream.snapshots)
    previous[0] = stream.initial_book
    previous[1:] = stream.snapshots[:-1]
    hidden = stream.event_type == 5
    np.testing.assert_array_equal(stream.snapshots[hidden], previous[hidden])
    assert np.all(stream.snapshots[:, 1::4] > 0)
    assert np.all(stream.snapshots[:, 3::4] > 0)


def test_parameter_fits_recover_large_synthetic_sample() -> None:
    generator = np.random.default_rng(1_340)
    config = AggregateL2EmissionConfig()
    latent = generator.standard_normal(80_000)
    stream = emit_aggregate_l2(latent, 0.8, config, generator)
    visible = stream.event_type != 5
    action = np.where(stream.event_type == 1, 1, -1)
    signed_flow = stream.direction * action
    level = np.where(
        stream.direction == 1,
        config.best_bid - stream.price,
        stream.price - config.best_ask,
    )

    beta = fit_flow_slope(latent[visible], signed_flow[visible])
    eta = fit_level_decay(level[visible], config.n_levels)
    size = fit_size_model(latent, stream.size)
    assert beta.converged and eta.converged and size.converged
    assert float(beta.values[0]) == pytest.approx(0.8, rel=0.04)
    assert float(eta.values[0]) == pytest.approx(config.eta, rel=0.04)
    assert float(size.values[0]) == pytest.approx(config.log_mu, rel=0.02)
    assert float(size.values[1]) == pytest.approx(config.gamma, rel=0.08)


def test_latent_sign_flip_is_an_exact_parameter_gauge() -> None:
    generator = np.random.default_rng(13_400)
    latent = generator.standard_normal(20_000)
    probability = 1.0 / (1.0 + np.exp(-1.2 * latent))
    signed_flow = np.where(generator.random(latent.size) < probability, 1, -1)
    direct = fit_flow_slope(latent, signed_flow)
    flipped = fit_flow_slope(-latent, signed_flow)
    assert direct.converged and flipped.converged
    assert float(direct.values[0] + flipped.values[0]) == pytest.approx(0.0, abs=1e-12)
    assert bernoulli_log_likelihood(
        float(direct.values[0]), latent, signed_flow
    ) == pytest.approx(
        bernoulli_log_likelihood(
            float(flipped.values[0]), -latent, signed_flow
        ),
        abs=1e-10,
    )


def test_nonpositive_queue_and_unknown_event_type_hard_fail() -> None:
    generator = np.random.default_rng(42)
    config = AggregateL2EmissionConfig(initial_queue=1, p_add=0.01, log_mu=4.0)
    latent = np.zeros(200, dtype=np.float64)
    with pytest.raises(RuntimeError, match="non-positive queue"):
        emit_aggregate_l2(latent, 0.0, config, generator)

    valid_config = AggregateL2EmissionConfig()
    valid = emit_aggregate_l2(
        np.zeros(10, dtype=np.float64),
        0.0,
        valid_config,
        np.random.default_rng(43),
    )
    invalid = replace(valid, event_type=np.full(valid.n_events, 6, dtype=np.int64))
    assert isinstance(invalid, SyntheticL2Stream)
    with pytest.raises(ValueError, match="unknown event type"):
        reconstruct_aggregate_book(invalid)

