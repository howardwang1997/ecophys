"""CPU smoke gate for the L2 recurrent fact-surrogate (build items L2-1..L2-4).

Pipeline-validation only, per PI decision D1_13 (code-only pre-D0 build):
forward determinism, deterministic decode (contract C2(d)), checkpoint
round-trip, ONE synthetic-batch gradient step, and RNG-tree substream
namespacing. Everything runs on CPU, writes nothing outside ``tmp_path``, and
persists no checkpoint for reuse. No GPU, no market data, no engine fixtures —
the frozen A-2 bundle is not touched. Style follows
``tests/test_through_m_estimators.py``.
"""

from __future__ import annotations

import copy
import math
from pathlib import Path

import pytest
import torch
from torch import Tensor

from ecomd.mechanisms.through_m import Kernel, straight_through_through_m
from ecomd.models.fact_surrogate import (
    FEXEC_ROUND_FEATURES,
    FactSurrogateBatch,
    FactSurrogateConfig,
    RecurrentFactSurrogate,
    fexec_round_features,
    lattice_ste,
)
from ecomd.training import fact_surrogates as fs
from ecomd.training.losses import multi_fact_terms
from ecomd.training.train_fact_surrogate import (
    K_INFERENCE_DRAWS,
    SUBSTREAM_NAMES,
    Enforcement,
    EstimatorKind,
    FactSurrogateTrainConfig,
    build_mechanism,
    checkpoint_execution_metadata,
    config_payload,
    derive_substream_seeds,
    fact_targets_from_config,
    fact_weights_from_config,
    substream_generator,
    train_fact_surrogate,
)
from ecomd.training.train_fact_surrogate import (
    load_fact_surrogate_checkpoint as load_checkpoint,
)
from ecomd.training.train_fact_surrogate import (
    save_fact_surrogate_checkpoint as save_checkpoint,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SEED_ROOT = 12000  # B3/B4 namespace (PI decision D1_10) — representative root only


def _execution_payload(
    *,
    quantity: int,
    price: int,
    maker_remaining: int,
    side: str,
    pre_bid: int,
    pre_ask: int,
    post_bid: int,
    post_ask: int,
    draw: dict[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "execution": {
            "execution_id": "E00000001",
            "maker_order_id": "O00000001",
            "side_of_aggressor": side,
            "price": price,
            "quantity": quantity,
            "maker_remaining": maker_remaining,
        },
        "aggressor_role": "external",
        "maker_role": "maker",
        "pre_best_bid": pre_bid,
        "pre_best_ask": pre_ask,
        "post_best_bid": post_bid,
        "post_best_ask": post_ask,
    }
    if draw is not None:
        payload["allocation_draw"] = draw
    return payload


def _model(seed_root: int = SEED_ROOT) -> RecurrentFactSurrogate:
    generator = substream_generator(seed_root, "init")
    return RecurrentFactSurrogate(FactSurrogateConfig(), generator=generator)


def _synthetic_batch(
    batch_size: int = 2,
    n_rounds: int = 32,
    *,
    n_slots: int = 8,
    with_draws: bool = False,
    seed: int = 7,
) -> FactSurrogateBatch:
    """Synthetic micro-batch built THROUGH the real F_exec feature map.

    Rounds alternate aggressor sides and quote moves; ``with_draws`` marks the
    payloads with ``allocation_draw`` (the random-unit kernel-identity
    channel). Channels/slot prices are integers on the engine lattice so the
    through-M conservation test is integer-exact.
    """

    generator = torch.Generator()
    generator.manual_seed(seed)
    feature_rows: list[Tensor] = []
    channels_rows: list[Tensor] = []
    price_rows: list[Tensor] = []
    init_rows: list[Tensor] = []
    for episode in range(batch_size):
        volume = 100 * (episode + 1)
        cash = 10_000 * (episode + 1)
        init_rows.append(torch.tensor([float(volume), float(cash)]))
        features: list[Tensor] = []
        channels: list[Tensor] = []
        prices: list[Tensor] = []
        for step in range(n_rounds):
            side = "B" if step % 2 == 0 else "S"
            quantity = 1 + int(torch.randint(4, (1,), generator=generator).item())
            price = 100 if side == "B" else 101
            draw = (
                {
                    "price": price,
                    "eligible_units": 4,
                    "selected_unit": 1,
                    "maker_order_id": "O00000001",
                }
                if with_draws
                else None
            )
            payload = _execution_payload(
                quantity=quantity,
                price=price,
                maker_remaining=2,
                side=side,
                pre_bid=100,
                pre_ask=101,
                post_bid=100,
                post_ask=101,
                draw=draw,
            )
            features.append(fexec_round_features([payload]))
            volume += quantity
            cash += price * quantity
            channels.append(torch.tensor([float(volume), float(cash)]))
            prices.append(
                torch.tensor([float(price)] * n_slots)
            )
        feature_rows.append(torch.stack(features))
        channels_rows.append(torch.stack(channels))
        price_rows.append(torch.stack(prices))
    return FactSurrogateBatch(
        features=torch.stack(feature_rows),
        channels=torch.stack(channels_rows),
        slot_prices=torch.stack(price_rows),
        channels_init=torch.stack(init_rows),
    )


# ─────────────────────────────────────────────────────────────────────────────
# F_exec feature map (input grammar)
# ─────────────────────────────────────────────────────────────────────────────


def test_feature_map_hand_computed_values() -> None:
    payloads = [
        _execution_payload(
            quantity=3, price=101, maker_remaining=1, side="B",
            pre_bid=100, pre_ask=102, post_bid=100, post_ask=101,
        ),
        _execution_payload(
            quantity=1, price=102, maker_remaining=4, side="B",
            pre_bid=100, pre_ask=102, post_bid=101, post_ask=102,
            draw={"price": 102, "eligible_units": 5, "selected_unit": 2,
                  "maker_order_id": "O00000002"},
        ),
    ]
    features = fexec_round_features(payloads, dtype=torch.float64)
    assert features.shape == (len(FEXEC_ROUND_FEATURES),)
    expected = [
        1.0,                                        # has_execution
        math.log1p(2),                              # log_n_exec
        math.log1p(4),                              # log_volume
        1.0,                                        # aggressor_buy_share
        1.0 / 4.0,                                  # draw_volume_share (draw on 1 of 4 units)
        2.0,                                        # pre_spread (102-100, first record)
        1.0,                                        # post_spread (102-101, last record)
        -1.0,                                       # spread_change
        ((101.0 + 102.0) / 2.0) - 101.0,            # mid_move
        1.0,                                        # best_bid_move
        0.0,                                        # best_ask_move
        ((3 * 101 + 1 * 102) / 4.0 - 101.0) / 2.0,  # vwap_rel_spread
        math.log1p(5),                              # log_maker_residual
        0.0,                                        # quotes_missing
    ]
    torch.testing.assert_close(features, torch.tensor(expected, dtype=torch.float64))


def test_feature_map_empty_round_token_and_missing_quote_rule() -> None:
    empty = fexec_round_features([])
    assert empty.shape == (len(FEXEC_ROUND_FEATURES),)
    assert float(empty[0]) == 0.0
    assert bool(torch.equal(empty, torch.zeros_like(empty)))

    payloads = [
        _execution_payload(
            quantity=2, price=99, maker_remaining=0, side="S",
            pre_bid=100, pre_ask=None, post_bid=99, post_ask=99,
        )
    ]
    features = fexec_round_features(payloads, dtype=torch.float64)
    assert features[13] == 1.0            # quotes_missing
    assert features[5] == 0.0             # pre_spread falls back to 0
    assert features[6] == 0.0             # post_spread = 99-99
    assert features[8] == 99.0 - 100.0    # mid_move under fallback (pre_mid=100)
    assert features[10] == 0.0            # ask move 0 when a side is None


def test_feature_map_rejects_malformed_payloads() -> None:
    bad: dict[str, object] = {"execution": {"quantity": "x"}}
    with pytest.raises(ValueError, match="quantity"):
        fexec_round_features([bad])
    no_execution: dict[str, object] = {"pre_best_bid": 1}
    with pytest.raises(ValueError, match="execution"):
        fexec_round_features([no_execution])


# ─────────────────────────────────────────────────────────────────────────────
# Forward shapes + determinism (C2(d); gate G8/G9 semantics)
# ─────────────────────────────────────────────────────────────────────────────


def test_forward_shapes() -> None:
    model = _model()
    batch = _synthetic_batch()
    output = model(batch)
    b, t = batch.features.shape[0], batch.features.shape[1]
    assert output.returns.shape == (b, t)
    assert output.abs_channels.shape == (b, t, 2)
    assert output.inc_channels.shape == (b, t, 2)
    assert output.flow.shape == (b, t, model.cfg.n_slots)
    assert output.demand.shape == (b, t)
    assert output.hidden.shape == (b, model.cfg.d_hidden)
    assert output.mechanism_channels is None
    # integer lattice: flow/demand decodes are engine-lattice valued
    assert bool((output.flow == torch.round(output.flow)).all())
    assert bool((output.demand == torch.round(output.demand)).all())
    assert bool((output.demand >= 1.0).all())


def test_same_seed_twice_byte_identical_eval_output() -> None:
    batch = _synthetic_batch()
    first = _model(SEED_ROOT)(batch)
    second = _model(SEED_ROOT)(batch)
    for a, b in zip(
        (first.returns, first.abs_channels, first.inc_channels, first.flow,
         first.demand, first.hidden),
        (second.returns, second.abs_channels, second.inc_channels, second.flow,
         second.demand, second.hidden),
        strict=True,
    ):
        assert torch.equal(a, b)


def test_decode_determinism_double_execution_no_sampling_heads() -> None:
    model = _model()
    batch = _synthetic_batch()
    assert not any(
        isinstance(module, torch.nn.Dropout) for module in model.modules()
    )
    with torch.no_grad():
        first = model(batch)
        second = model(batch)
    assert torch.equal(first.returns, second.returns)
    assert torch.equal(first.abs_channels, second.abs_channels)
    assert torch.equal(first.inc_channels, second.inc_channels)
    assert torch.equal(first.flow, second.flow)
    assert torch.equal(first.demand, second.demand)


def test_construction_with_generator_leaves_global_rng_untouched() -> None:
    torch.manual_seed(123)
    before = torch.get_rng_state()
    _model(SEED_ROOT)
    _model(SEED_ROOT + 1)
    assert torch.equal(torch.get_rng_state(), before)


def test_lattice_ste_forward_exact_backward_identity() -> None:
    raw = torch.tensor([0.3, 1.7, 2.5], requires_grad=True)
    lattice = lattice_ste(raw)
    assert torch.equal(lattice.detach(), torch.tensor([0.0, 2.0, 2.0]))
    lattice.backward(torch.tensor([1.0, 2.0, 4.0]))
    assert raw.grad is not None
    assert torch.equal(raw.grad, torch.tensor([1.0, 2.0, 4.0]))


# ─────────────────────────────────────────────────────────────────────────────
# Through-M compatibility (estimator-menu interface; L2-2)
# ─────────────────────────────────────────────────────────────────────────────


def test_through_m_forward_conservation_and_gradient_flow() -> None:
    model = _model()
    batch = _synthetic_batch(n_rounds=8, with_draws=False)
    mechanism = build_mechanism(
        FactSurrogateTrainConfig(
            enforcement=Enforcement.THROUGH_M,
            estimator=EstimatorKind.STRAIGHT_THROUGH,
            kernel=Kernel.FIFO,
        ),
        train_kernel_generator=substream_generator(SEED_ROOT, "train_kernel"),
    )
    assert mechanism is not None
    output = model(batch, mechanism=mechanism)
    assert output.mechanism_channels is not None

    raw_output = model(batch)
    assert raw_output.mechanism_channels is None
    assert not torch.equal(
        output.mechanism_channels.detach(), raw_output.abs_channels.detach()
    )

    increments = output.mechanism_channels - batch.channels_init.unsqueeze(1)
    assert bool(
        torch.equal(increments[..., 0], torch.round(increments[..., 0]))
    ), "volume channel must stay integer-exact through M"
    assert bool(
        torch.equal(increments[..., 1], torch.round(increments[..., 1]))
    ), "cash channel must stay integer-exact through M (integer slot prices)"
    executed = increments[..., 0].detach()
    assert bool((executed >= 0).all())

    loss = ((output.mechanism_channels - batch.channels) ** 2).mean()
    loss.backward()
    flow_grads = model.flow_head.weight.grad
    assert flow_grads is not None and bool(torch.isfinite(flow_grads).all())
    assert float(flow_grads.abs().sum()) > 0.0, (
        "straight-through estimator must pass gradient to the flow head"
    )


def test_through_m_flow_feeds_the_frozen_estimator_contract() -> None:
    """The model's per-round flow row is a legal ``quantities`` argument."""
    model = _model()
    batch = _synthetic_batch(n_rounds=4)
    output = model(batch)
    quantities = output.flow[0, 0]
    allocation = straight_through_through_m(quantities, 3, Kernel.FIFO)
    assert allocation.shape == quantities.shape
    assert int(allocation.sum().detach()) <= int(quantities.sum().detach())


# ─────────────────────────────────────────────────────────────────────────────
# Seeding surface (L2-3; contract C1/C2)
# ─────────────────────────────────────────────────────────────────────────────


def test_substream_surface_names_and_count() -> None:
    assert K_INFERENCE_DRAWS == 16
    assert SUBSTREAM_NAMES[:4] == ("data", "init", "minibatch", "train_kernel")
    assert SUBSTREAM_NAMES[4] == "kernel:1"
    assert SUBSTREAM_NAMES[-1] == "kernel:16"
    assert len(SUBSTREAM_NAMES) == 20


def test_substream_namespacing_distinct_and_replayable() -> None:
    seeds = derive_substream_seeds(SEED_ROOT)
    assert len(set(seeds.values())) == len(SUBSTREAM_NAMES), "substreams must be distinct"
    assert seeds == derive_substream_seeds(SEED_ROOT), "same root replays identically"
    other = derive_substream_seeds(SEED_ROOT + 1)
    assert all(seeds[name] != other[name] for name in SUBSTREAM_NAMES)

    draws = {
        name: torch.rand(4, generator=substream_generator(SEED_ROOT, name)).tolist()
        for name in ("init", "minibatch", "train_kernel")
    }
    assert len({tuple(values) for values in draws.values()}) == 3
    replay = torch.rand(4, generator=substream_generator(SEED_ROOT, "init")).tolist()
    assert replay == draws["init"]

    with pytest.raises(ValueError, match="unknown substream"):
        substream_generator(SEED_ROOT, "not_a_substream")


# ─────────────────────────────────────────────────────────────────────────────
# Trainer smoke: ONE synthetic-batch gradient step (D1_13 scope)
# ─────────────────────────────────────────────────────────────────────────────


def _single_step_config(**kwargs: object) -> FactSurrogateTrainConfig:
    defaults: dict[str, object] = {"n_iters": 1, "lr": 1e-3}
    defaults.update(kwargs)
    return FactSurrogateTrainConfig(**defaults)  # type: ignore[arg-type]


def test_cpu_smoke_single_gradient_step_raw_arm() -> None:
    model = _model()
    batch = _synthetic_batch(n_rounds=64)
    before = copy.deepcopy(model.state_dict())
    history = train_fact_surrogate(
        model, batch, _single_step_config(), seed_root=SEED_ROOT
    )
    assert len(history) == 1
    record = history[0]
    assert math.isfinite(record["total"]) and record["total"] > 0.0
    assert math.isfinite(record["grad_norm"])
    for key in ("total", "channel_loss", "grad_norm", "coordinate", "enforcement"):
        assert key in record
    changed = [name for name, tensor in model.state_dict().items()
               if not torch.equal(tensor, before[name])]
    assert changed, "one optimizer step must move parameters"


def test_cpu_smoke_single_gradient_step_through_m_and_fact_terms() -> None:
    model = _model()
    batch = _synthetic_batch(n_rounds=64, with_draws=True)
    config = _single_step_config(
        enforcement=Enforcement.THROUGH_M,
        estimator=EstimatorKind.STRAIGHT_THROUGH,
        kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE,
        w_gain_loss=0.1,
        gain_loss_skew_target=-0.3,
        w_fano=0.1,
        fano_target=1.5,
    )
    history = train_fact_surrogate(model, batch, config, seed_root=SEED_ROOT)
    record = history[0]
    for key in ("gain_loss", "fano"):
        assert key in record and math.isfinite(record[key])
    assert math.isfinite(record["total"])


def test_fact_terms_match_direct_surrogate_composition() -> None:
    """The trainer's fact wiring is the existing library, not a fork: the
    penalty equals |surrogate(decoded series) - target| on a fixed series."""
    model = _model()
    batch = _synthetic_batch(n_rounds=64)
    output = model(batch)
    config = _single_step_config(w_gain_loss=0.25, gain_loss_skew_target=-0.2)
    terms = multi_fact_terms(
        output.returns[0],
        fact_targets_from_config(config),
        fact_weights_from_config(config),
    )
    direct = (fs.gain_loss_skew(output.returns[0]) + 0.2).abs()
    torch.testing.assert_close(terms["gain_loss"], direct)


def test_trainer_replay_determinism_same_seed_root() -> None:
    batch = _synthetic_batch(n_rounds=16)

    first_model = _model(SEED_ROOT + 5)
    train_fact_surrogate(
        first_model, batch, _single_step_config(n_iters=3), seed_root=SEED_ROOT + 5
    )
    second_model = _model(SEED_ROOT + 5)
    train_fact_surrogate(
        second_model, batch, _single_step_config(n_iters=3), seed_root=SEED_ROOT + 5
    )
    for name, tensor in first_model.state_dict().items():
        assert torch.equal(tensor, second_model.state_dict()[name]), name


def test_trainer_rejects_non_cpu_batch() -> None:
    model = _model()
    batch = _synthetic_batch()
    if not torch.backends.mps.is_available():
        return
    batch_mps = FactSurrogateBatch(
        features=batch.features.to("mps"),
        channels=batch.channels.to("mps"),
        slot_prices=batch.slot_prices.to("mps"),
    )
    with pytest.raises(ValueError, match="CPU-only"):
        train_fact_surrogate(
            model, batch_mps, _single_step_config(), seed_root=SEED_ROOT
        )


# ─────────────────────────────────────────────────────────────────────────────
# Checkpoint contract (L2-4; format v2, CPU-loadable, git/config binding)
# ─────────────────────────────────────────────────────────────────────────────


def test_checkpoint_round_trip_tmp_only(tmp_path: Path) -> None:
    model = _model()
    batch = _synthetic_batch()
    with torch.no_grad():
        reference = model(batch)

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    config = FactSurrogateTrainConfig()
    metadata = checkpoint_execution_metadata(REPO_ROOT, config)
    assert isinstance(metadata["git_sha"], str) and len(metadata["git_sha"]) == 40
    assert isinstance(metadata["config_sha256"], str) and len(metadata["config_sha256"]) == 64

    path = tmp_path / "l2_smoke.pt"
    save_checkpoint(
        path,
        model=model,
        optimizer=optimizer,
        iter_idx=0,
        config=config,
        hidden=reference.hidden,
        substream_generators={
            name: substream_generator(SEED_ROOT, name)
            for name in ("init", "minibatch", "train_kernel")
        },
        history=[],
        execution_metadata=metadata,
    )
    assert path.is_file() and not list(tmp_path.glob(".*tmp*"))

    loaded = load_checkpoint(path, model=_model(), optimizer=None)
    assert int(loaded["format_version"]) == 2
    assert int(loaded["world_size"]) == 1
    assert bool(loaded["state_complete"])
    assert loaded["execution_metadata"]["git_sha"] == metadata["git_sha"]
    assert loaded["sim_config"] == config_payload(config)
    runtime = loaded["rank_runtimes"][0]
    assert torch.equal(runtime["recurrent_hidden"], reference.hidden)
    assert set(runtime["substream_generator_states"]) == {
        "init", "minibatch", "train_kernel"
    }

    restored = _model()
    load_checkpoint(path, model=restored)
    with torch.no_grad():
        replay = restored(batch)
    assert torch.equal(replay.returns, reference.returns)
    assert torch.equal(replay.abs_channels, reference.abs_channels)
    assert torch.equal(replay.inc_channels, reference.inc_channels)
    assert torch.equal(replay.hidden, reference.hidden)


def test_checkpoint_loadable_with_map_location_cpu(tmp_path: Path) -> None:
    model = _model()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    config = FactSurrogateTrainConfig()
    path = tmp_path / "l2_map_location.pt"
    save_checkpoint(
        path,
        model=model,
        optimizer=optimizer,
        iter_idx=3,
        config=config,
        hidden=model.init_hidden(2),
        substream_generators={},
        history=[{"iter": 0}],
        execution_metadata=checkpoint_execution_metadata(REPO_ROOT, config),
    )
    raw = torch.load(path, map_location="cpu", weights_only=False)
    assert isinstance(raw, dict)
    assert int(raw["iter_idx"]) == 3
    assert isinstance(raw["sim_state_dict"], dict)


def test_checkpoint_rejects_wrong_format_version(tmp_path: Path) -> None:
    model = _model()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    config = FactSurrogateTrainConfig()
    path = tmp_path / "l2_bad_version.pt"
    save_checkpoint(
        path,
        model=model,
        optimizer=optimizer,
        iter_idx=0,
        config=config,
        hidden=model.init_hidden(1),
        substream_generators={},
        history=[],
        execution_metadata={},
    )
    payload = torch.load(path, map_location="cpu", weights_only=False)
    payload["format_version"] = 99
    torch.save(payload, path)
    with pytest.raises(ValueError, match="format_version"):
        load_checkpoint(path, model=_model())
