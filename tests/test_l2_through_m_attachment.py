"""L2-2: through-M attachment of the L2 recurrent fact-surrogate (via E-3).

CPU spot checks, second-scale (PI no-heavy-compute rule). ``build_mechanism``
with ``mechanism_backend=ENGINE_BRIDGE`` constructs the SHARED E-3 wrapper —
the real ``ReferenceEngine``-backed mechanism — and these tests pin: engine
replay equivalence on a small tape (exact integer match, both kernels), the
RNG-tree substream discipline of contract C1/C2 (``train_kernel`` feeds PAM
noise; ``kernel:1..16`` feed the K = 16 inference draws in order; global RNG
untouched), estimator/kernel selectability with the frozen backward
contracts, and byte-identity of two identically-seeded builds. The frozen A-2
bundle is not touched. No GPU, no training run, no market data.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from dataclasses import replace as dc_replace
from pathlib import Path

import numpy as np
import pytest
import torch
from torch import Tensor

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lab_asset.matching import ReferenceEngine
from lab_asset.replay import replay
from lab_asset.schema import (
    AllocationRule,
    EventType,
    InitialOrder,
    OrderRequest,
    SessionPrestate,
    Side,
    TapeRecord,
    ThreeClocks,
)

from ecomd.mechanisms.through_m import Kernel
from ecomd.models.fact_surrogate import (
    FactSurrogateBatch,
    FactSurrogateConfig,
    MechanismEstimator,
    RecurrentFactSurrogate,
    fexec_round_features,
)
from ecomd.training import train_fact_surrogate as tfs
from ecomd.training.train_fact_surrogate import (
    K_INFERENCE_DRAWS,
    Enforcement,
    EstimatorKind,
    MechanismBackend,
    build_inference_mechanism,
    build_mechanism,
    inference_kernel_draw_mechanisms,
    substream_generator,
    train_fact_surrogate,
)

SEED_ROOT = 12000  # B3/B4 namespace (PI decision D1_10) — representative root only

INITIAL_ASKS: tuple[InitialOrder, ...] = (
    InitialOrder("A1", "b", Side.ASK, 101, 2),
    InitialOrder("A2", "a", Side.ASK, 101, 3),
    InitialOrder("A3", "d", Side.ASK, 101, 4),
)
RESTING_QUANTITIES: tuple[int, ...] = (2, 3, 4)  # queue order at the touched price
DEMAND = 5  # aggressor quantity: partial clearing, one untouched maker under FIFO


# --------------------------------------------------------------------------- helpers


def make_prestate(
    rule: AllocationRule,
    *,
    seed: int = 7,
    initial_book: tuple[InitialOrder, ...] = INITIAL_ASKS,
) -> SessionPrestate:
    actors = ("a", "b", "c", "d")
    return SessionPrestate(
        session_id="S0001",
        seed=seed,
        allocation_rule=rule,
        initial_cash={actor: 100_000 for actor in actors},
        initial_inventory={actor: 100 for actor in actors},
        price_bands=(90, 110),
        actors=actors,
        initial_book=initial_book,
        scheduler_seed=17,
        scheduler_tick=0,
        scheduler_state="round-0-ready",
        assignment_key_commitment="test-commitment",
        latency_endowment=2,
        latency_delay_by_investment=(5, 3, 1),
    )


def _session(
    rule: AllocationRule, *, seed: int = 7
) -> tuple[SessionPrestate, list[TapeRecord]]:
    """One crossing session: three resting asks at 101, aggressor buys 5."""
    prestate = make_prestate(rule, seed=seed)
    engine = ReferenceEngine(prestate)
    engine.submit(
        OrderRequest(
            event_id=1,
            actor="c",
            client_order_id="c1",
            side=Side.BID,
            price=101,
            quantity=DEMAND,
            clocks=ThreeClocks(1, 1, 1),
        )
    )
    engine.finish()
    return prestate, engine.tape


def _recorded_maker_allocations(tape: Sequence[TapeRecord]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for record in tape:
        if record.event_type is not EventType.EXECUTION:
            continue
        execution = record.payload["execution"]
        assert isinstance(execution, dict)
        maker = execution["maker_order_id"]
        assert isinstance(maker, str) and isinstance(execution["quantity"], int)
        totals[maker] = totals.get(maker, 0) + int(execution["quantity"])
    return totals


def _recorded_draws(tape: Sequence[TapeRecord]) -> list[int]:
    draws: list[int] = []
    for record in tape:
        if record.event_type is not EventType.EXECUTION:
            continue
        draw = record.payload.get("allocation_draw")
        if draw is not None:
            assert isinstance(draw, dict)
            selected = draw["selected_unit"]
            assert isinstance(selected, int)
            draws.append(selected)
    return draws


def _quantities_tensor() -> Tensor:
    return torch.tensor(RESTING_QUANTITIES, dtype=torch.float32)


def _config(**kwargs: object) -> tfs.FactSurrogateTrainConfig:
    defaults: dict[str, object] = {
        "enforcement": Enforcement.THROUGH_M,
        "estimator": EstimatorKind.STRAIGHT_THROUGH,
        "kernel": Kernel.FIFO,
        "mechanism_backend": MechanismBackend.ENGINE_BRIDGE,
    }
    defaults.update(kwargs)
    return tfs.FactSurrogateTrainConfig(**defaults)  # type: ignore[arg-type]


def _synthetic_batch(
    batch_size: int = 2, n_rounds: int = 8, *, n_slots: int = 8
) -> FactSurrogateBatch:
    generator = torch.Generator()
    generator.manual_seed(11)
    feature_rows: list[Tensor] = []
    channel_rows: list[Tensor] = []
    price_rows: list[Tensor] = []
    for episode in range(batch_size):
        volume = 100 * (episode + 1)
        cash = 10_000 * (episode + 1)
        features: list[Tensor] = []
        channels: list[Tensor] = []
        prices: list[Tensor] = []
        for step in range(n_rounds):
            side = "B" if step % 2 == 0 else "S"
            quantity = 1 + int(torch.randint(4, (1,), generator=generator).item())
            price = 100 if side == "B" else 101
            payload: dict[str, object] = {
                "execution": {
                    "execution_id": "E00000001",
                    "maker_order_id": "O00000001",
                    "side_of_aggressor": side,
                    "price": price,
                    "quantity": quantity,
                    "maker_remaining": 2,
                },
                "aggressor_role": "external",
                "maker_role": "maker",
                "pre_best_bid": 100,
                "pre_best_ask": 101,
                "post_best_bid": 100,
                "post_best_ask": 101,
            }
            features.append(fexec_round_features([payload]))
            volume += quantity
            cash += price * quantity
            channels.append(torch.tensor([float(volume), float(cash)]))
            prices.append(torch.tensor([float(price)] * n_slots))
        feature_rows.append(torch.stack(features))
        channel_rows.append(torch.stack(channels))
        price_rows.append(torch.stack(prices))
    return FactSurrogateBatch(
        features=torch.stack(feature_rows),
        channels=torch.stack(channel_rows),
        slot_prices=torch.stack(price_rows),
    )


def _model(seed_root: int = SEED_ROOT) -> RecurrentFactSurrogate:
    return RecurrentFactSurrogate(
        FactSurrogateConfig(),
        generator=substream_generator(seed_root, "init"),
    )


def _engine_bridge_mechanism(config: tfs.FactSurrogateTrainConfig) -> MechanismEstimator:
    mechanism = build_mechanism(config, seed_root=SEED_ROOT)
    assert mechanism is not None
    return mechanism


# --------------------------------------------------------------------------- engine replay equivalence


def test_engine_bridge_fifo_matches_engine_replay_exactly() -> None:
    prestate, tape = _session(AllocationRule.FIFO)
    assert replay(prestate, tape).ok, "tape must be certified engine truth first"

    mechanism = _engine_bridge_mechanism(_config(kernel=Kernel.FIFO))
    allocation = mechanism(_quantities_tensor(), DEMAND).detach().to(torch.int64)

    expected_by_maker = _recorded_maker_allocations(tape)
    expected = torch.tensor(
        [expected_by_maker.get(order.order_id, 0) for order in INITIAL_ASKS],
        dtype=torch.int64,
    )
    assert torch.equal(allocation, expected)
    assert torch.equal(expected, torch.tensor([2, 3, 0])), "FIFO partial-clear hand check"


def test_engine_bridge_random_unit_law_matches_engine_replay() -> None:
    """The bridge's random-unit law is the engine's, unit by unit.

    The engine's own draws are recorded in the tape (``allocation_draw.
    selected_unit``, one per unit execution, depleting eligible counts). The
    frozen exact clearing of ``ecomd.mechanisms.through_m`` driven by those
    recorded draws must reproduce the tape's per-maker allocations. The
    bridge, whose first-call engine seed is the ``train_kernel``-node child
    the E-3 ``TrainKernelStream`` derives from the seed root, must equal the
    engine's own execution at that same seed — and that execution's recorded
    draws must reproduce its allocation through the frozen exact clearing.
    """
    from ecomd.mechanisms.through_m import exact_clearing
    from ecomd.mechanisms.through_m_wrapper import (
        NOMINAL_LEVEL_PRICE,
        TrainKernelStream,
        engine_execute_level,
    )

    prestate, tape = _session(AllocationRule.RANDOM_UNIT_WITHIN_PRICE)
    assert replay(prestate, tape).ok

    draws = _recorded_draws(tape)
    assert len(draws) == DEMAND, "random unit executes one record per unit"
    outcome = exact_clearing(
        _quantities_tensor(), DEMAND, Kernel.RANDOM_UNIT_WITHIN_PRICE, draws
    )
    expected_by_maker = _recorded_maker_allocations(tape)
    expected = torch.tensor(
        [expected_by_maker.get(order.order_id, 0) for order in INITIAL_ASKS],
        dtype=torch.int64,
    )
    assert torch.equal(outcome.allocation, expected)

    # the stream's first-call engine seed, derived from the seed root exactly
    # as the hook derives it internally
    stream = TrainKernelStream(SEED_ROOT)
    engine_seed, _pam_seed = stream.next_call_seeds()
    engine_outcome = engine_execute_level(
        _quantities_tensor(),
        DEMAND,
        level_price=NOMINAL_LEVEL_PRICE,
        kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE,
        engine_seed=engine_seed,
    )
    engine_draws = [
        fill.selected_unit
        for fill in engine_outcome.fills
        if fill.selected_unit is not None
    ]
    assert len(engine_draws) == DEMAND
    replayed = exact_clearing(
        _quantities_tensor(), DEMAND, Kernel.RANDOM_UNIT_WITHIN_PRICE, engine_draws
    )
    assert torch.equal(replayed.allocation, engine_outcome.allocation_exact), (
        "the E-3 engine execution satisfies its own recorded draw law"
    )

    mechanism = _engine_bridge_mechanism(
        _config(kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE)
    )
    bridge_allocation = mechanism(_quantities_tensor(), DEMAND)
    assert bridge_allocation.shape == _quantities_tensor().shape
    rounded = bridge_allocation.detach().to(torch.int64)
    assert int(rounded.sum()) == DEMAND, "bridge clears exactly the demanded units"
    assert bool((rounded >= 0).all()) and bool(
        (rounded <= torch.tensor(RESTING_QUANTITIES)).all()
    )
    assert torch.equal(rounded, engine_outcome.allocation_exact), (
        "the hook's forward is the engine execution at the stream's first "
        "train_kernel-child seed"
    )


def test_mirror_backend_matches_engine_and_bridge_on_fifo() -> None:
    """FIFO is deterministic: mirror, bridge and engine replay must agree."""
    _, tape = _session(AllocationRule.FIFO)
    expected_by_maker = _recorded_maker_allocations(tape)

    mirror = build_mechanism(
        _config(kernel=Kernel.FIFO, mechanism_backend=MechanismBackend.MIRROR),
        train_kernel_generator=substream_generator(SEED_ROOT, "train_kernel"),
    )
    assert mirror is not None
    mirror_allocation = mirror(_quantities_tensor(), DEMAND).detach().to(torch.int64)
    expected = torch.tensor(
        [expected_by_maker.get(order.order_id, 0) for order in INITIAL_ASKS],
        dtype=torch.int64,
    )
    assert torch.equal(mirror_allocation, expected)

    bridge = _engine_bridge_mechanism(_config(kernel=Kernel.FIFO))
    assert torch.equal(
        bridge(_quantities_tensor(), DEMAND).detach().to(torch.int64), expected
    )


def test_engine_bridge_missing_module_is_a_hard_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tfs, "ENGINE_BRIDGE_MODULE", "ecomd.mechanisms.no_such_bridge")
    with pytest.raises(RuntimeError, match="E-3 wrapper"):
        build_mechanism(_config(), seed_root=SEED_ROOT)
    with pytest.raises(RuntimeError, match="E-3 wrapper"):
        build_mechanism(
            _config(),
            train_kernel_generator=substream_generator(SEED_ROOT, "train_kernel"),
            seed_root=SEED_ROOT,
        )


def test_engine_bridge_requires_a_seed_root() -> None:
    with pytest.raises(ValueError, match="seed_root"):
        build_mechanism(_config(), train_kernel_generator=torch.Generator())


def test_mirror_backend_requires_a_generator() -> None:
    with pytest.raises(ValueError, match="train_kernel_generator"):
        build_mechanism(
            _config(mechanism_backend=MechanismBackend.MIRROR), seed_root=SEED_ROOT
        )


# --------------------------------------------------------------------------- substream discipline


def test_train_kernel_substream_feeds_pam_noise_and_global_rng_untouched() -> None:
    torch.manual_seed(123)
    torch_global_before = torch.get_rng_state()
    python_before = _python_rng_state()
    numpy_before = repr(np.random.get_state())

    quantities = torch.tensor([3.0, 3.0])
    sensitive_demand = 2  # equal resting scores: the pinned noise picks the maker

    first = build_mechanism(
        _config(
            estimator=EstimatorKind.PERTURB_AND_MAP,
            mechanism_backend=MechanismBackend.MIRROR,
        ),
        train_kernel_generator=substream_generator(SEED_ROOT, "train_kernel"),
    )
    assert first is not None
    second = build_mechanism(
        _config(
            estimator=EstimatorKind.PERTURB_AND_MAP,
            mechanism_backend=MechanismBackend.MIRROR,
        ),
        train_kernel_generator=substream_generator(SEED_ROOT, "train_kernel"),
    )
    assert second is not None

    first_allocation = first(quantities, sensitive_demand).detach()
    assert torch.equal(
        first_allocation, second(quantities, sensitive_demand).detach()
    ), "same train_kernel substream must give byte-identical PAM noise"

    # noise liveness across a seed-root family: the PAM noise must track the
    # train_kernel substream (deterministic given the pinned roots, but not a
    # fixed module-default stream)
    def root_allocation(
        root: int, probe_quantities: Tensor, probe_demand: int
    ) -> list[float]:
        mechanism = build_mechanism(
            _config(
                estimator=EstimatorKind.PERTURB_AND_MAP,
                mechanism_backend=MechanismBackend.MIRROR,
            ),
            train_kernel_generator=substream_generator(root, "train_kernel"),
        )
        assert mechanism is not None
        return mechanism(probe_quantities, probe_demand).detach().tolist()

    ru_probe = (torch.tensor([3.0, 3.0]), 1)  # equal scores: noise decides
    fifo_probe = (torch.tensor([3.0, 3.0, 3.0]), 1)
    roots = list(range(SEED_ROOT, SEED_ROOT + 8))
    ru_values = {tuple(root_allocation(r, *ru_probe)) for r in roots}
    fifo_values = {tuple(root_allocation(r, *fifo_probe)) for r in roots}
    assert len(ru_values) > 1, "random-unit PAM noise must vary across seed roots"
    assert len(fifo_values) > 1, "FIFO PAM noise must vary across seed roots"

    # the production path: the E-3 bridge hooks derive BOTH the engine draw
    # seed and the PAM noise seed from the train_kernel node of the seed root
    def bridge_probe(
        root: int, kernel: Kernel, probe_quantities: Tensor, probe_demand: int
    ) -> tuple[tuple[float, ...], tuple[float, ...]]:
        mechanism = build_mechanism(
            _config(estimator=EstimatorKind.PERTURB_AND_MAP, kernel=kernel),
            seed_root=root,
        )
        assert mechanism is not None
        tracked = probe_quantities.clone().requires_grad_(True)
        allocation = mechanism(tracked, probe_demand)
        torch.autograd.backward(allocation, torch.ones_like(allocation))
        assert tracked.grad is not None
        return (
            tuple(allocation.detach().tolist()),
            tuple(tracked.grad.tolist()),
        )

    bridge_first = bridge_probe(SEED_ROOT, Kernel.RANDOM_UNIT_WITHIN_PRICE, quantities, sensitive_demand)
    bridge_second = bridge_probe(SEED_ROOT, Kernel.RANDOM_UNIT_WITHIN_PRICE, quantities, sensitive_demand)
    assert bridge_first == bridge_second, (
        "same seed root must give byte-identical E-3 stream children"
    )

    bridge_ru = {
        bridge_probe(r, Kernel.RANDOM_UNIT_WITHIN_PRICE, *ru_probe)[0] for r in roots
    }
    assert len(bridge_ru) > 1, (
        "the engine draw seed must track the seed root's train_kernel node"
    )
    bridge_fifo_forward = {
        bridge_probe(r, Kernel.FIFO, *fifo_probe)[0] for r in roots
    }
    bridge_fifo_grads = {
        bridge_probe(r, Kernel.FIFO, *fifo_probe)[1] for r in roots
    }
    assert len(bridge_fifo_forward) == 1, "FIFO engine forward is seed-invariant"
    assert len(bridge_fifo_grads) > 1, (
        "the PAM noise seed must track the seed root's train_kernel node "
        "(FIFO backward mask observes the noise)"
    )

    assert torch.equal(torch.get_rng_state(), torch_global_before)
    assert _python_rng_state() == python_before
    assert repr(np.random.get_state()) == numpy_before


def _python_rng_state() -> object:
    import random as _random

    return _random.getstate()


# --------------------------------------------------------------------------- estimator selectability


@pytest.mark.parametrize(
    "estimator", [EstimatorKind.STRAIGHT_THROUGH, EstimatorKind.PERTURB_AND_MAP]
)
@pytest.mark.parametrize("kernel", [Kernel.FIFO, Kernel.RANDOM_UNIT_WITHIN_PRICE])
def test_both_estimators_selectable_under_both_kernels(
    estimator: EstimatorKind, kernel: Kernel
) -> None:
    assert (
        build_mechanism(
            _config(enforcement=Enforcement.RAW),
            train_kernel_generator=substream_generator(SEED_ROOT, "train_kernel"),
        )
        is None
    ), "the raw arm carries no mechanism"

    mechanism = _engine_bridge_mechanism(_config(estimator=estimator, kernel=kernel))
    quantities = _quantities_tensor().requires_grad_(True)
    allocation = mechanism(quantities, DEMAND)

    rounded = allocation.detach().to(torch.int64)
    assert torch.equal(allocation.detach(), rounded.to(allocation.dtype))
    assert int(rounded.sum()) == DEMAND
    assert bool((rounded >= 0).all()) and bool(
        (rounded <= torch.tensor(RESTING_QUANTITIES)).all()
    )

    torch.autograd.backward(allocation, torch.ones_like(allocation))
    assert quantities.grad is not None
    assert bool(torch.isfinite(quantities.grad).all())
    cleared = rounded > 0
    assert bool((quantities.grad[cleared] != 0).all()) or not bool(cleared.any())
    assert bool((quantities.grad[~cleared] == 0).all()), (
        "never-cleared coordinates are fiber directions: zero gradient (pinned)"
    )


def test_straight_through_backward_is_pinned_scale_masked_identity() -> None:
    mechanism = _engine_bridge_mechanism(_config())
    quantities = torch.tensor([2.0, 3.0, 4.0], requires_grad=True)
    allocation = mechanism(quantities, DEMAND)
    torch.autograd.backward(allocation, torch.tensor([10.0, 20.0, 40.0]))
    assert quantities.grad is not None
    # scale 1.0 pinned: identity on cleared coordinates [2, 3], zero on [0]
    assert torch.equal(quantities.grad, torch.tensor([10.0, 20.0, 0.0]))


# --------------------------------------------------------------------------- K = 16 inference draw loop


def test_inference_draw_loop_consumes_kernel_substreams_in_order() -> None:
    config = _config(
        kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE,
        mechanism_backend=MechanismBackend.MIRROR,
    )
    mechanisms = inference_kernel_draw_mechanisms(config, seed_root=SEED_ROOT)
    assert len(mechanisms) == K_INFERENCE_DRAWS == 16

    quantities = torch.tensor([3.0, 3.0])
    sensitive_demand = 2
    outputs = [
        mechanism(quantities, sensitive_demand).detach().tolist()
        for mechanism in mechanisms
    ]

    # draw k is seeded from kernel:k — byte-equal to the hand-built construction
    for draw_index in (1, 8, 16):
        hand_built = build_mechanism(
            dc_replace(config, enforcement=Enforcement.THROUGH_M),
            train_kernel_generator=substream_generator(
                SEED_ROOT, f"kernel:{draw_index}"
            ),
        )
        assert hand_built is not None
        again = build_inference_mechanism(
            config, seed_root=SEED_ROOT, draw_index=draw_index
        )
        assert torch.equal(
            again(quantities, sensitive_demand).detach(),
            hand_built(quantities, sensitive_demand).detach(),
        )

    # distinct substreams: at least two of the 16 draws differ on the sensitive input
    assert len({tuple(values) for values in outputs}) > 1

    # determinism of the whole loop across two identically-seeded builds
    replay_outputs = [
        mechanism(quantities, sensitive_demand).detach().tolist()
        for mechanism in inference_kernel_draw_mechanisms(
            _config(
                kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE,
                mechanism_backend=MechanismBackend.MIRROR,
            ),
            seed_root=SEED_ROOT,
        )
    ]
    assert outputs == replay_outputs

    with pytest.raises(ValueError, match="draw_index"):
        build_inference_mechanism(config, seed_root=SEED_ROOT, draw_index=0)
    with pytest.raises(ValueError, match="draw_index"):
        build_inference_mechanism(config, seed_root=SEED_ROOT, draw_index=17)


def test_deterministic_kernel_sixteen_identical_evaluations() -> None:
    """Gate G8 semantics: FIFO cells execute K identical, byte-identical draws."""
    config = _config(kernel=Kernel.FIFO)
    mechanisms = inference_kernel_draw_mechanisms(config, seed_root=SEED_ROOT)
    quantities = _quantities_tensor()
    outputs = [mechanism(quantities, DEMAND).detach() for mechanism in mechanisms]
    for output in outputs[1:]:
        assert torch.equal(output, outputs[0])


def test_inference_mechanisms_are_engine_bridged_and_generator_pure() -> None:
    """The inference loop constructs the REAL bridge, deterministically per k."""
    from ecomd.mechanisms.through_m_wrapper import perturb_and_map_hook

    config = _config(
        estimator=EstimatorKind.PERTURB_AND_MAP,
        kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE,
    )
    quantities = torch.tensor([3.0, 3.0])
    first = build_inference_mechanism(config, seed_root=SEED_ROOT, draw_index=5)
    second = build_inference_mechanism(config, seed_root=SEED_ROOT, draw_index=5)
    assert torch.equal(
        first(quantities, 2).detach(), second(quantities, 2).detach()
    )

    # draw k is rooted at substream kernel:k — byte-equal to a hand-built E-3
    # hook seeded with that node's derived integer (fresh mechanisms: the E-3
    # stream advances one child per call)
    draw_seed = tfs.derive_substream_seeds(SEED_ROOT)["kernel:5"]
    hand_built = perturb_and_map_hook(
        kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE, seed_root=draw_seed
    )
    fresh = build_inference_mechanism(config, seed_root=SEED_ROOT, draw_index=5)
    assert torch.equal(
        fresh(quantities, 2).detach(),
        hand_built(quantities, 2).detach(),
    )
    assert draw_seed != tfs.derive_substream_seeds(SEED_ROOT)["kernel:6"]


# --------------------------------------------------------------------------- byte identity


@pytest.mark.parametrize(
    "backend", [MechanismBackend.MIRROR, MechanismBackend.ENGINE_BRIDGE]
)
def test_two_identically_seeded_builds_are_byte_identical(backend: MechanismBackend) -> None:
    batch = _synthetic_batch()
    config = tfs.FactSurrogateTrainConfig(
        n_iters=1,
        lr=1e-3,
        enforcement=Enforcement.THROUGH_M,
        estimator=EstimatorKind.STRAIGHT_THROUGH,
        kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE,
        mechanism_backend=backend,
    )

    def build_and_run() -> tuple[dict[str, Tensor], list[dict[str, object]]]:
        model = _model(SEED_ROOT + 3)
        mechanism = build_mechanism(
            config,
            train_kernel_generator=substream_generator(SEED_ROOT + 3, "train_kernel"),
            seed_root=SEED_ROOT + 3,
        )
        assert mechanism is not None
        output = model(batch, mechanism=mechanism)
        tensors = {
            "mechanism_channels": output.mechanism_channels,
            "flow": output.flow,
            "returns": output.returns,
        }
        history = train_fact_surrogate(model, batch, config, seed_root=SEED_ROOT + 3)
        return tensors, history

    first_tensors, first_history = build_and_run()
    second_tensors, second_history = build_and_run()
    for key, first in first_tensors.items():
        assert first is not None and second_tensors[key] is not None
        assert torch.equal(first, second_tensors[key]), key
    assert first_history == second_history


def test_model_hook_attachment_through_real_bridge() -> None:
    """The L2-2 attachment itself: the recurrent head's per-step flow output
    executes through the E-3 bridge and returns integer-exact channels."""
    model = _model()
    batch = _synthetic_batch()
    mechanism = _engine_bridge_mechanism(
        _config(kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE)
    )
    output = model(batch, mechanism=mechanism)
    assert output.mechanism_channels is not None
    channels = output.mechanism_channels
    assert torch.equal(channels[..., 0], torch.round(channels[..., 0]))
    assert torch.equal(channels[..., 1], torch.round(channels[..., 1]))
    assert bool((channels[..., 0] >= 0).all()), "cleared volume is nonnegative"
    assert bool(
        (channels[:, 1:, 0] >= channels[:, :-1, 0]).all()
    ), "volume channel cumulates nonnegative per-round cleared units"

    loss = channels.sum()
    loss.backward()
    flow_grads = model.flow_head.weight.grad
    assert flow_grads is not None and bool(torch.isfinite(flow_grads).all())
