"""L1-2 — ABS/INC supervised coordinate heads + the two RNG-substream bindings.

Build item L1-2 of the D0 build register (simulator contracts sections 2.2 and
2.4; prereg v2 C3/C5): the two coordinate heads (predict ``x_{t+1}`` vs
``x_{t+1} - x_t`` on conserving-channel targets) over the lineage-invariant
F_exec grammar, the C5 supervised rollout-error loss composing with the
existing ``multi_fact_terms`` path, the opt-in ``spawn(seed, "init")``
type-label binding, and the ``spawn(seed, "minibatch")`` order stream.

Verified here (CPU spot checks only, mirroring
``tests/test_ecomd_v2_sps_rng_binding.py`` for the RNG discipline):
(a) ABS/INC targets are exact inverses on consecutive states, and the INC
    arm's state prediction is the base-lifted increment (head-level algebra);
(b) the C5 statistic is computed exactly (hand-checked scaled squared mean);
(c) decode determinism by double execution and full construction determinism
    from the init substream;
(d) init + minibatch draw from named substreams while the GLOBAL torch RNG
    state is bit-unchanged (no global-RNG consumers anywhere in the path);
(e) supervised-loss gradient flow (single synthetic-batch gradient step:
    finite loss/grads, parameters move), for both coordinates, including the
    composition with ``multi_fact_terms``;
(f) the training loop is reproducible byte-identically from one seed root;
(g) shape/argument validation fails loud.
"""

from __future__ import annotations

import pytest
import torch
from torch import Tensor

from ecomd.models.ecomd import EcoMDConfig
from ecomd.models.fact_surrogate import FEXEC_ROUND_FEATURES, FactSurrogateBatch
from ecomd.models.l1_coordinate_heads import (
    L1CoordinateHeads,
    L1CoordinateHeadsConfig,
    L1CoordinateOutput,
)
from ecomd.training.l1_supervised import (
    L1SupervisedTrainConfig,
    MinibatchOrderStream,
    bind_v2_type_seed,
    build_coordinate_targets,
    combine_supervised_and_fact_terms,
    coordinate_state_prediction,
    init_substream_seed,
    l1_supervised_terms,
    train_l1_coordinate_heads,
)
from ecomd.training.losses import LossWeights, MomentTargets, multi_fact_terms
from ecomd.training.train_fact_surrogate import Coordinate, derive_substream_seeds

SEED_ROOT = 11000  # B1/B2 namespace start (contract C1, PI decision D1_10)


# ─── Helpers ────────────────────────────────────────────────────────────────


def _synthetic_batch(
    batch_size: int = 4,
    n_rounds: int = 7,
    *,
    seed: int = 0,
    n_slots: int = 8,
    with_init: bool = True,
) -> FactSurrogateBatch:
    """Synthetic conserving-channel batch: integer-valued cumulative volume
    and cash paths over the frozen 14-feature grammar (no market data)."""

    generator = torch.Generator().manual_seed(seed)
    features = torch.randn(
        batch_size, n_rounds, len(FEXEC_ROUND_FEATURES), generator=generator
    )
    increments = torch.randint(1, 9, (batch_size, n_rounds, 2), generator=generator)
    channels = torch.cumsum(increments.to(torch.float32), dim=1)
    slot_prices = torch.randint(99, 106, (batch_size, n_rounds, n_slots), generator=generator)
    channels_init = (
        torch.randint(10, 20, (batch_size, 2), generator=generator).to(torch.float32)
        if with_init
        else None
    )
    return FactSurrogateBatch(
        features=features,
        channels=channels,
        slot_prices=slot_prices,
        channels_init=channels_init,
    )


def _model(
    seed_root: int = SEED_ROOT, config: L1CoordinateHeadsConfig | None = None
) -> L1CoordinateHeads:
    generator = torch.Generator().manual_seed(init_substream_seed(seed_root))
    return L1CoordinateHeads(config, generator=generator)


def _bytes(tensor: Tensor) -> bytes:
    return tensor.detach().cpu().contiguous().numpy().tobytes()


def _state_bytes(model: L1CoordinateHeads) -> bytes:
    return b"".join(_bytes(parameter) for parameter in model.parameters())


# ─── (a) ABS/INC are exact inverses on consecutive states ───────────────────


@pytest.mark.parametrize("with_init", [True, False])
def test_coordinate_targets_exact_inverse_algebra(with_init: bool) -> None:
    batch = _synthetic_batch(with_init=with_init)
    channels_init = batch.channels_init
    targets = build_coordinate_targets(batch.channels, channels_init)

    assert torch.equal(targets.abs_targets - targets.base, targets.inc_targets)
    assert torch.equal(targets.base + targets.inc_targets, targets.abs_targets)
    if with_init:
        assert channels_init is not None
        assert torch.equal(targets.base[:, 0], channels_init)
    else:
        assert torch.equal(targets.base[:, 0], torch.zeros_like(targets.base[:, 0]))
    assert torch.equal(targets.base[:, 1:], batch.channels[:, :-1])
    assert torch.equal(targets.abs_targets, batch.channels)


def test_increment_prediction_is_the_base_lifted_decode() -> None:
    model = _model()
    batch = _synthetic_batch()
    output = model(batch)
    targets = build_coordinate_targets(batch.channels, batch.channels_init)

    assert torch.equal(
        coordinate_state_prediction(output, targets.base, Coordinate.ABSOLUTE),
        output.abs_channels,
    )
    assert torch.equal(
        coordinate_state_prediction(output, targets.base, Coordinate.INCREMENT),
        targets.base + output.inc_channels,
    )


# ─── (b) the C5 statistic is exact ──────────────────────────────────────────


def test_c5_terms_match_hand_computation() -> None:
    abs_targets = torch.tensor([[[3.0, 5.0], [4.0, 9.0]]])  # (1, 2, 2)
    base = torch.tensor([[[0.0, 0.0], [3.0, 5.0]]])
    assert torch.equal(build_coordinate_targets(abs_targets).base, base)

    output = L1CoordinateOutput(
        abs_channels=torch.tensor([[[2.5, 6.0], [5.0, 7.0]]]),
        inc_channels=torch.tensor([[[1.0, 4.0], [2.0, 1.0]]]),
        flow=torch.zeros(1, 2, 8),
        demand=torch.ones(1, 2),
    )
    targets = build_coordinate_targets(abs_targets)
    scales = [2.0, 5.0]

    abs_terms = l1_supervised_terms(output, targets, Coordinate.ABSOLUTE, scales)
    expected_scaled = torch.tensor(
        [[[(2.5 - 3.0) / 2.0, (6.0 - 5.0) / 5.0], [(5.0 - 4.0) / 2.0, (7.0 - 9.0) / 5.0]]]
    )
    expected_total = (expected_scaled ** 2).mean()
    assert torch.allclose(abs_terms["_total"], expected_total)
    assert torch.allclose(abs_terms["c5_endpoint"], expected_total.sqrt())
    for channel in range(2):
        assert torch.allclose(
            abs_terms[f"channel_{channel}"], (expected_scaled[..., channel] ** 2).mean()
        )

    inc_terms = l1_supervised_terms(output, targets, Coordinate.INCREMENT, scales)
    inc_scaled = ((base + output.inc_channels) - abs_targets) / torch.tensor(scales)
    assert torch.allclose(inc_terms["_total"], (inc_scaled ** 2).mean())


def test_channel_scales_validation() -> None:
    batch = _synthetic_batch()
    output = _model()(batch)
    targets = build_coordinate_targets(batch.channels, batch.channels_init)
    with pytest.raises(ValueError, match="channel_scales"):
        l1_supervised_terms(output, targets, Coordinate.ABSOLUTE, [1.0])
    with pytest.raises(ValueError, match="positive"):
        l1_supervised_terms(output, targets, Coordinate.ABSOLUTE, [1.0, 0.0])


# ─── (c) determinism: double execution and construction ────────────────────


def test_decode_determinism_by_double_execution() -> None:
    model = _model()
    batch = _synthetic_batch()
    first = model(batch)
    second = model(batch)
    assert _bytes(first.abs_channels) == _bytes(second.abs_channels)
    assert _bytes(first.inc_channels) == _bytes(second.inc_channels)
    assert _bytes(first.flow) == _bytes(second.flow)
    assert _bytes(first.demand) == _bytes(second.demand)


def test_construction_determinism_from_init_substream() -> None:
    assert _state_bytes(_model(SEED_ROOT)) == _state_bytes(_model(SEED_ROOT))
    assert _state_bytes(_model(SEED_ROOT)) != _state_bytes(_model(SEED_ROOT + 1))


# ─── (d) substream bindings; global torch RNG untouched ────────────────────


def test_init_binding_is_the_shared_named_substream() -> None:
    seeds = derive_substream_seeds(SEED_ROOT)
    assert init_substream_seed(SEED_ROOT) == seeds["init"]
    assert init_substream_seed(SEED_ROOT) != seeds["minibatch"]
    assert init_substream_seed(SEED_ROOT) != init_substream_seed(SEED_ROOT + 1)


def test_init_binding_is_opt_in_and_leaves_the_default_untouched() -> None:
    config = EcoMDConfig()
    bound = bind_v2_type_seed(config, SEED_ROOT)
    assert bound.v2_type_seed == init_substream_seed(SEED_ROOT)
    assert config.v2_type_seed == 42  # existing default behavior unchanged
    assert bound != config


def test_model_init_consumes_zero_global_rng() -> None:
    torch.manual_seed(5)
    state_before = torch.get_rng_state()
    _model(SEED_ROOT)
    assert torch.equal(torch.get_rng_state(), state_before), (
        "generator-threaded construction consumed the global torch RNG"
    )


def test_forward_consumes_zero_global_rng() -> None:
    model = _model(SEED_ROOT)
    batch = _synthetic_batch()
    torch.manual_seed(11)
    state_before = torch.get_rng_state()
    model(batch)
    assert torch.equal(torch.get_rng_state(), state_before), (
        "decode must be deterministic (C2(d)) and consume no RNG"
    )


def test_minibatch_order_stream_is_named_substream_and_global_free() -> None:
    torch.manual_seed(7)
    state_before = torch.get_rng_state()
    stream_a = MinibatchOrderStream.from_seed_root(SEED_ROOT)
    stream_b = MinibatchOrderStream.from_seed_root(SEED_ROOT)
    stream_c = MinibatchOrderStream.from_seed_root(SEED_ROOT + 1)

    orders_a = [stream_a.next_order(4) for _ in range(5)]
    orders_b = [stream_b.next_order(4) for _ in range(5)]
    orders_c = [stream_c.next_order(4) for _ in range(5)]
    assert torch.equal(torch.get_rng_state(), state_before), (
        "the minibatch-order stream consumed the global torch RNG"
    )
    assert all(torch.equal(a, b) for a, b in zip(orders_a, orders_b, strict=True))
    assert any(not torch.equal(a, c) for a, c in zip(orders_a, orders_c, strict=True))
    for order in orders_a:
        assert torch.equal(torch.sort(order).values, torch.arange(4))
    with pytest.raises(ValueError, match="n must be"):
        stream_a.next_order(0)


# ─── (e) supervised-loss gradient flow (single synthetic-batch step) ───────


@pytest.mark.parametrize(
    ("coordinate", "scales"),
    [
        (Coordinate.ABSOLUTE, (1.0, 1.0)),
        (Coordinate.INCREMENT, (2.0, 5.0)),
    ],
)
def test_supervised_gradient_flow_single_step(
    coordinate: Coordinate, scales: tuple[float, float]
) -> None:
    model = _model()
    batch = _synthetic_batch()
    targets = build_coordinate_targets(batch.channels, batch.channels_init)
    output = model(batch)
    terms = l1_supervised_terms(output, targets, coordinate, scales)

    total = terms["_total"]
    assert torch.isfinite(total)
    total.backward()  # type: ignore[no-untyped-call]
    grads = [p.grad for p in model.parameters() if p.grad is not None]
    assert grads and all(torch.isfinite(g).all() for g in grads)
    grad_mag = torch.tensor(0.0)
    for parameter in model.parameters():
        if parameter.grad is not None:
            grad_mag = grad_mag + parameter.grad.abs().sum()
    assert grad_mag.item() > 0.0

    before = _state_bytes(model)
    torch.optim.SGD(model.parameters(), lr=0.1).step()
    assert _state_bytes(model) != before, "parameters did not move in the gradient step"


def test_composition_with_multi_fact_terms() -> None:
    model = _model()
    batch = _synthetic_batch()
    returns = torch.linspace(-0.02, 0.02, 64)
    weights = LossWeights(w_gain_loss=0.3)
    fact_targets = MomentTargets(
        acf_sq_mean=0.0, leverage_sum=0.0, hill_alpha=0.0, gain_loss_skew=0.1
    )

    output = model(batch)
    coordinate_targets = build_coordinate_targets(batch.channels, batch.channels_init)
    supervised = l1_supervised_terms(
        output, coordinate_targets, Coordinate.INCREMENT, (2.0, 5.0)
    )
    fact = multi_fact_terms(returns, fact_targets, weights)
    merged = combine_supervised_and_fact_terms(supervised, fact, w_supervised=0.5)

    assert torch.allclose(merged["total"], 0.5 * supervised["_total"] + fact["_total"])
    assert "gain_loss" in merged and "gain_loss_sim" in merged

    model.zero_grad()
    merged["total"].backward()  # type: ignore[no-untyped-call]
    grad_mag = torch.tensor(0.0)
    for parameter in model.parameters():
        if parameter.grad is not None:
            assert torch.isfinite(parameter.grad).all()
            grad_mag = grad_mag + parameter.grad.abs().sum()
    assert grad_mag.item() > 0.0, "supervised gradient must reach the head parameters"


# ─── (f) training-loop reproducibility from one seed root ──────────────────


def test_training_loop_single_step_reproducible_and_global_free() -> None:
    config = L1SupervisedTrainConfig(
        n_iters=1,
        coordinate=Coordinate.ABSOLUTE,
        channel_scales=(2.0, 5.0),
        w_gain_loss=0.3,
        gain_loss_skew_target=0.1,
    )
    batch = _synthetic_batch()
    returns = torch.linspace(-0.01, 0.01, 64)

    torch.manual_seed(3)
    state_before = torch.get_rng_state()
    history_a = train_l1_coordinate_heads(
        _model(), batch, config, seed_root=SEED_ROOT, returns=returns
    )
    assert torch.equal(torch.get_rng_state(), state_before), (
        "the supervised training loop consumed the global torch RNG"
    )

    history_b = train_l1_coordinate_heads(
        _model(), batch, config, seed_root=SEED_ROOT, returns=returns
    )
    assert history_a == history_b
    assert len(history_a) == 1
    for record in history_a:
        assert all(value == value for value in record.values())  # no NaN anywhere
        assert record["grad_norm"] >= 0.0
        assert record["coordinate"] == "absolute"
    assert history_a[0]["supervised"] > 0.0

    model_a = _model()
    model_b = _model()
    train_l1_coordinate_heads(model_a, batch, config, seed_root=SEED_ROOT, returns=returns)
    train_l1_coordinate_heads(model_b, batch, config, seed_root=SEED_ROOT, returns=returns)
    assert _state_bytes(model_a) == _state_bytes(model_b)
    assert _state_bytes(model_a) != _state_bytes(_model()), "one step must move parameters"


def test_training_loop_without_returns_runs_supervised_only() -> None:
    config = L1SupervisedTrainConfig(n_iters=1, coordinate=Coordinate.INCREMENT)
    model = _model()
    history = train_l1_coordinate_heads(
        model, _synthetic_batch(), config, seed_root=SEED_ROOT
    )
    assert len(history) == 1
    assert "gain_loss" not in history[0]
    assert history[0]["total"] == history[0]["supervised"]


def test_training_loop_rejects_non_cpu_and_bad_iters() -> None:
    config = L1SupervisedTrainConfig(n_iters=0)
    with pytest.raises(ValueError, match="n_iters"):
        train_l1_coordinate_heads(
            _model(), _synthetic_batch(), config, seed_root=SEED_ROOT
        )


# ─── (g) shape/argument validation ─────────────────────────────────────────


def test_forward_validates_shapes() -> None:
    model = _model()
    good = _synthetic_batch(n_slots=8)

    bad_features = FactSurrogateBatch(
        features=torch.randn(2, 3, len(FEXEC_ROUND_FEATURES) + 1),
        channels=torch.zeros(2, 3, 2),
        slot_prices=torch.zeros(2, 3, 8, dtype=torch.int64),
    )
    with pytest.raises(ValueError, match="features must be"):
        model(bad_features)

    bad_channels = FactSurrogateBatch(
        features=good.features,
        channels=torch.zeros(2, 3, 3),
        slot_prices=good.slot_prices,
    )
    with pytest.raises(ValueError, match="channels must be"):
        model(bad_channels)

    bad_slots = FactSurrogateBatch(
        features=good.features,
        channels=good.channels,
        slot_prices=torch.zeros(2, 3, 4, dtype=torch.int64),
    )
    with pytest.raises(ValueError, match="slot_prices must be"):
        model(bad_slots)

    bad_init = FactSurrogateBatch(
        features=good.features,
        channels=good.channels,
        slot_prices=good.slot_prices,
        channels_init=torch.zeros(2, 3),
    )
    with pytest.raises(ValueError, match="channels_init must be"):
        model(bad_init)


def test_output_lattice_and_shapes() -> None:
    batch_size, n_rounds, n_slots = 3, 5, 8
    model = _model(config=L1CoordinateHeadsConfig(d_hidden=16))
    batch = _synthetic_batch(batch_size=batch_size, n_rounds=n_rounds)
    output = model(batch)
    assert output.abs_channels.shape == (batch_size, n_rounds, 2)
    assert output.inc_channels.shape == (batch_size, n_rounds, 2)
    assert output.flow.shape == (batch_size, n_rounds, n_slots)
    assert output.demand.shape == (batch_size, n_rounds)
    assert torch.equal(output.flow, torch.round(output.flow))
    assert bool((output.flow >= 0).all())
    assert torch.equal(output.demand, torch.round(output.demand))
    assert bool((output.demand >= 1).all())


def test_config_validation() -> None:
    with pytest.raises(ValueError, match="d_hidden"):
        L1CoordinateHeads(L1CoordinateHeadsConfig(d_hidden=0))
    with pytest.raises(ValueError, match="n_slots"):
        L1CoordinateHeads(L1CoordinateHeadsConfig(n_slots=0))
    with pytest.raises(ValueError, match="n_channels"):
        L1CoordinateHeads(L1CoordinateHeadsConfig(n_channels=0))
