"""L1-1 corpus adapter: CPU spot checks (build item L1-1, D-1 stage).

Second-scale, CPU-only, single-file scope (PI no-heavy-compute rule): hand
tapes with hand series, tiny engine sessions, and READ-ONLY use of the frozen
A-2 bundle (``experiments/lab_asset_a2/a2_exit_20260905/`` — bytes are read,
never written; per-file sha256s re-verified against the bundle manifest
before any build). No GPU, no training, no market data, no outcome access.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import sys
from dataclasses import dataclass
from dataclasses import replace as dc_replace
from pathlib import Path
from typing import Any

import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lab_asset.conserving_emitter import (
    conservation_violations,
    emit_conserving_channels,
    settlement_violations,
)
from lab_asset.matching import ReferenceEngine
from lab_asset.replay import regenerate
from lab_asset.schema import (
    AllocationRule,
    EventType,
    InitialOrder,
    OrderRequest,
    SessionPrestate,
    Side,
    TapeRecord,
    ThreeClocks,
    prestate_from_json,
    prestate_hash,
)

from ecomd.corpus.fexec_projector import project_fexec_corpus
from ecomd.corpus.l1_corpus_adapter import (
    ADAPTER_ID,
    L1_AGENT_STATE_CHANNELS,
    L1_CONTEXT_CHANNELS,
    L1_CONTEXT_SIZE,
    L1_D_STATE,
    ConservingSeriesView,
    build_l1_corpus,
)
from ecomd.models.fact_surrogate import (
    FEXEC_ROUND_FEATURES,
    FactSurrogateConfig,
    fexec_round_features,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FROZEN_DIR = REPO_ROOT / "experiments/lab_asset_a2/a2_exit_20260905"
SEED = 11000  # B1/B2 training namespace root (PI decision D1_10)
TENSOR_FIELDS = (
    "agent_states",
    "context",
    "flow_slot",
    "features",
    "channels_inc",
    "channels_abs",
    "slot_prices",
    "slot_quantities",
)


# --------------------------------------------------------------------------- helpers


def make_prestate(
    rule: AllocationRule,
    *,
    seed: int = 7,
    session_id: str = "S0001",
    initial_book: tuple[InitialOrder, ...] = (),
) -> SessionPrestate:
    actors = ("a", "b", "c", "d")
    return SessionPrestate(
        session_id=session_id,
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


def _execution_payload(
    *,
    quantity: int,
    price: int,
    maker_remaining: int,
    side: str,
    match_ts: int,
    round_id: int,
    pre_bid: int | None,
    pre_ask: int | None,
    post_bid: int | None,
    post_ask: int | None,
    draw: dict[str, Any] | None = None,
    event_id: int = 1,
    execution_id: str = "E00000001",
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "execution": {
            "event_id": event_id,
            "execution_id": execution_id,
            "aggressor_order_id": "O00000002",
            "maker_order_id": "O00000001",
            "maker_actor": "b",
            "aggressor_actor": "c",
            "side_of_aggressor": side,
            "price": price,
            "quantity": quantity,
            "maker_remaining": maker_remaining,
            "clocks": {"client_ts": match_ts, "receipt_ts": match_ts, "match_ts": match_ts},
            "round_id": round_id,
        },
        "aggressor_role": "trader",
        "maker_role": "designated_maker",
        "pre_best_bid": pre_bid,
        "pre_best_ask": pre_ask,
        "post_best_bid": post_bid,
        "post_best_ask": post_ask,
    }
    if draw is not None:
        payload["allocation_draw"] = draw
    return payload


def _record(sequence: int, event_type: EventType, payload: dict[str, Any]) -> TapeRecord:
    return TapeRecord(sequence=sequence, event_type=event_type, payload=payload)


def _hand_tape(prestate: SessionPrestate) -> list[TapeRecord]:
    """Two clearing rounds: tick 5 (two fills at 100), tick 7 (one fill at 102)."""

    return [
        _record(
            1,
            EventType.SESSION_START,
            {
                "session_id": prestate.session_id,
                "schema_version": prestate.schema_version,
                "allocation_rule": prestate.allocation_rule.value,
                "prestate_hash": prestate_hash(prestate),
            },
        ),
        _record(2, EventType.ORDER_REQUEST, {"event_id": 1, "actor": "c"}),
        _record(
            3,
            EventType.EXECUTION,
            _execution_payload(
                quantity=2,
                price=100,
                maker_remaining=0,
                side="B",
                match_ts=5,
                round_id=0,
                pre_bid=99,
                pre_ask=101,
                post_bid=99,
                post_ask=101,
                event_id=3,
                execution_id="E00000001",
            ),
        ),
        _record(
            4,
            EventType.EXECUTION,
            _execution_payload(
                quantity=1,
                price=100,
                maker_remaining=2,
                side="B",
                match_ts=5,
                round_id=0,
                pre_bid=99,
                pre_ask=101,
                post_bid=99,
                post_ask=101,
                event_id=4,
                execution_id="E00000002",
            ),
        ),
        _record(5, EventType.ORDER_ACCEPTED, {"resting_quantity": 0}),
        _record(
            6,
            EventType.EXECUTION,
            _execution_payload(
                quantity=4,
                price=102,
                maker_remaining=1,
                side="S",
                match_ts=7,
                round_id=0,
                pre_bid=99,
                pre_ask=101,
                post_bid=100,
                post_ask=104,
                draw={
                    "price": 102,
                    "eligible_units": 5,
                    "selected_unit": 3,
                    "maker_order_id": "O00000009",
                },
                event_id=6,
                execution_id="E00000003",
            ),
        ),
    ]


@dataclass(frozen=True)
class _HandRound:
    match_ts: int


@dataclass(frozen=True)
class _HandSeries:
    """Structural stand-in for E-4's ConservingChannelSeries (Protocol)."""

    session_id: str
    allocation_rule: str
    ticks: tuple[int, ...]
    increments: tuple[tuple[int, int], ...]
    cumulatives: tuple[tuple[int, int], ...]

    @property
    def rounds(self) -> tuple[_HandRound, ...]:
        return tuple(_HandRound(tick) for tick in self.ticks)

    @property
    def n_rounds(self) -> int:
        return len(self.ticks)

    def increment_matrix(self) -> list[list[int]]:
        return [list(row) for row in self.increments]

    def cumulative_matrix(self) -> list[list[int]]:
        return [list(row) for row in self.cumulatives]

    def to_json(self) -> str:
        return json.dumps(
            {
                "session_id": self.session_id,
                "allocation_rule": self.allocation_rule,
                "ticks": list(self.ticks),
                "increments": [list(row) for row in self.increments],
                "cumulatives": [list(row) for row in self.cumulatives],
            },
            sort_keys=True,
            separators=(",", ":"),
        )


def _hand_series(prestate: SessionPrestate) -> _HandSeries:
    return _HandSeries(
        session_id=prestate.session_id,
        allocation_rule=prestate.allocation_rule.value,
        ticks=(5, 7),
        increments=((3, 300), (4, 408)),
        cumulatives=((3, 300), (7, 708)),
    )


def _engine_tape(
    rule: AllocationRule,
    *,
    seed: int = 7,
    first_quantity: int = 2,
) -> tuple[SessionPrestate, list[TapeRecord]]:
    """Three marketable bids at three distinct ticks -> three clearing rounds."""

    prestate = make_prestate(
        rule,
        seed=seed,
        initial_book=(InitialOrder("A1", "b", Side.ASK, 101, 5),),
    )
    engine = ReferenceEngine(prestate)
    for event_id, (actor, tick, quantity) in enumerate(
        (("c", 1, first_quantity), ("d", 2, 1), ("a", 3, 1)), start=1
    ):
        engine.submit(
            OrderRequest(
                event_id=event_id,
                actor=actor,
                client_order_id=f"{actor}{event_id}",
                side=Side.BID,
                price=101,
                quantity=quantity,
                clocks=ThreeClocks(tick, tick, tick),
            )
        )
    engine.finish()
    return prestate, engine.tape


def _load_frozen_fixture(name: str) -> tuple[SessionPrestate, list[TapeRecord]]:
    manifest = json.loads((FROZEN_DIR / "bundle_manifest.json").read_text())
    files: dict[str, str] = manifest["files"]
    for relative, expected in sorted(files.items()):
        if relative.startswith(f"{name}/"):
            digest = hashlib.sha256((FROZEN_DIR / relative).read_bytes()).hexdigest()
            assert digest == expected, f"frozen bundle file mutated: {relative}"
    fixture_dir = FROZEN_DIR / name
    prestate = prestate_from_json((fixture_dir / "prestate.json").read_text())
    tape: list[TapeRecord] = []
    for line in (fixture_dir / "tape.jsonl").read_text().splitlines():
        if line.strip():
            raw = json.loads(line)
            tape.append(
                TapeRecord(
                    sequence=raw["sequence"],
                    event_type=EventType(raw["event_type"]),
                    payload=raw["payload"],
                    pre_state_hash=raw["pre_state_hash"],
                    post_state_hash=raw["post_state_hash"],
                    pre_aggregate_state_hash=raw["pre_aggregate_state_hash"],
                    post_aggregate_state_hash=raw["post_aggregate_state_hash"],
                )
            )
    return prestate, tape


def _serialized(corpus: Any) -> bytes:
    buffer = io.BytesIO()
    torch.save({name: getattr(corpus, name) for name in TENSOR_FIELDS}, buffer)
    return buffer.getvalue()


def _assert_tensor_identity(left: Any, right: Any) -> None:
    for name in TENSOR_FIELDS:
        assert torch.equal(getattr(left, name), getattr(right, name)), name


# --------------------------------------------------------------------------- tests


def test_hand_checked_small_tape() -> None:
    prestate = make_prestate(AllocationRule.FIFO)
    l1 = build_l1_corpus(prestate, _hand_tape(prestate), SEED, series=_hand_series(prestate))
    projector = project_fexec_corpus(prestate, _hand_tape(prestate), SEED)

    assert l1.match_ticks == (5, 7)
    assert (l1.n_rounds, l1.n_executions, l1.n_agents, l1.d_state) == (2, 3, 8, 6)

    # t = 0: the all-zero session-initial no-event token
    assert torch.equal(l1.agent_states[0], torch.zeros(8, L1_D_STATE))
    assert torch.equal(l1.context[0], torch.zeros(L1_CONTEXT_SIZE))

    # t = 1 (tau = 0): round 0 posted (99,101) quotes, 3 units at price 100,
    # cumulative channels (3, 300)
    row0 = l1.agent_states[1, 0].tolist()
    assert row0 == pytest.approx(
        [
            math.log1p(3),            # log1p_prev_slot_quantity
            (100 - 100.0) / 2.0,      # prev_slot_price_rel_spread
            math.log1p(3),            # log1p_cum_volume
            math.log1p(300),          # log1p_cum_cash
            2.0,                      # prev_post_spread
            0.0,                      # prev_mid_move
        ]
    )
    pad_row = l1.agent_states[1, 1].tolist()
    assert pad_row == pytest.approx(
        [0.0, 0.0, math.log1p(3), math.log1p(300), 2.0, 0.0]
    )
    assert l1.context[1].tolist() == pytest.approx([math.log(100.0), 0.0, 0.0])

    # supervision is E-1 verbatim; channels are the hand series verbatim
    assert torch.equal(l1.features, projector.features)
    assert l1.channels_inc.tolist() == [[3, 300], [4, 408]]
    assert l1.channels_abs.tolist() == [[3, 300], [7, 708]]
    assert torch.equal(l1.slot_prices, projector.slot_prices)
    assert torch.equal(l1.slot_quantities, projector.slot_quantities)
    assert torch.equal(l1.flow_slot, torch.zeros(2, 8))
    assert [r.first_sequence for r in l1.rounds] == [3, 6]


def test_shapes_dtypes_and_constants() -> None:
    assert len(L1_AGENT_STATE_CHANNELS) == L1_D_STATE == 6
    assert list(L1_CONTEXT_CHANNELS) == ["log_price", "volatility", "last_log_return"]
    assert ADAPTER_ID == "ecomd.corpus.l1_corpus_adapter"

    prestate, tape = _engine_tape(AllocationRule.FIFO)
    l1 = build_l1_corpus(prestate, tape, SEED)
    assert l1.agent_states.shape == (3, 8, L1_D_STATE)
    assert l1.agent_states.dtype == torch.float32
    assert l1.context.shape == (3, L1_CONTEXT_SIZE)
    assert l1.flow_slot.shape == (3, 8)
    assert l1.features.shape == (3, len(FEXEC_ROUND_FEATURES))
    for name in ("channels_inc", "channels_abs", "slot_prices", "slot_quantities"):
        assert getattr(l1, name).dtype == torch.int64
    assert l1.channels_inc.shape == (3, 2)

    # a genuine no-execution session (non-marketable bid, empty initial book):
    # zero rounds, zero-shaped tensors, replay-safe
    empty_prestate = make_prestate(AllocationRule.FIFO, initial_book=())
    empty_engine = ReferenceEngine(empty_prestate)
    empty_engine.submit(
        OrderRequest(
            event_id=1,
            actor="c",
            client_order_id="c1",
            side=Side.BID,
            price=99,
            quantity=1,
            clocks=ThreeClocks(1, 1, 1),
        )
    )
    empty_engine.finish()
    empty = build_l1_corpus(empty_prestate, empty_engine.tape, SEED)
    assert empty.n_rounds == 0
    assert empty.agent_states.shape == (0, 8, L1_D_STATE)
    assert empty.context.shape == (0, L1_CONTEXT_SIZE)
    assert empty.flow_slot.shape == (0, 8)
    assert empty.channels_inc.shape == (0, 2)


@pytest.mark.parametrize("rule", [AllocationRule.FIFO, AllocationRule.RANDOM_UNIT_WITHIN_PRICE])
def test_e4_pass_through_exactness(rule: AllocationRule) -> None:
    prestate, tape = _engine_tape(rule)
    l1 = build_l1_corpus(prestate, tape, SEED)
    series = emit_conserving_channels(prestate, tape)

    assert l1.channels_inc.tolist() == series.increment_matrix()
    assert l1.channels_abs.tolist() == series.cumulative_matrix()
    assert l1.channels_inc.tolist() == [[2, 202], [1, 101], [1, 101]]
    assert l1.channels_abs.tolist() == [[2, 202], [3, 303], [4, 404]]
    assert conservation_violations(series) == []
    assert settlement_violations(prestate, tape, series) == []


@pytest.mark.parametrize("rule", [AllocationRule.FIFO, AllocationRule.RANDOM_UNIT_WITHIN_PRICE])
def test_determinism_byte_identity_and_regeneration(rule: AllocationRule) -> None:
    prestate, tape = _engine_tape(rule, seed=11)
    first = build_l1_corpus(prestate, tape, SEED)
    second = build_l1_corpus(prestate, tape, SEED)

    assert first.adapter_hash == second.adapter_hash
    assert first.content_hash == second.content_hash
    assert first.series_hash == second.series_hash
    _assert_tensor_identity(first, second)
    assert _serialized(first) == _serialized(second)

    from_regenerated = build_l1_corpus(prestate, regenerate(prestate, tape), SEED)
    assert from_regenerated.adapter_hash == first.adapter_hash
    assert _serialized(from_regenerated) == _serialized(first)

    other_seed = build_l1_corpus(prestate, tape, SEED + 1)
    assert other_seed.adapter_hash != first.adapter_hash
    _assert_tensor_identity(other_seed, first)  # seed binds identity only

    # explicit series injection is indistinguishable from internal derivation
    injected = build_l1_corpus(
        prestate, tape, SEED, series=emit_conserving_channels(prestate, tape)
    )
    assert injected.adapter_hash == first.adapter_hash


def test_request_side_exclusion() -> None:
    prestate, tape = _engine_tape(AllocationRule.FIFO)
    clean_series = emit_conserving_channels(prestate, tape)
    baseline = build_l1_corpus(prestate, tape, SEED)

    perturbed: list[TapeRecord] = []
    for record in tape:
        if record.event_type == EventType.ORDER_REQUEST:
            perturbed.append(
                dc_replace(record, payload={**record.payload, "actor": "zzz"})
            )
        elif record.event_type == EventType.ORDER_ACCEPTED:
            perturbed.append(
                dc_replace(record, payload={**record.payload, "resting_quantity": 99})
            )
        else:
            perturbed.append(record)

    moved = build_l1_corpus(prestate, perturbed, SEED, series=clean_series)
    _assert_tensor_identity(moved, baseline)
    assert moved.content_hash == baseline.content_hash
    assert moved.corpus_hash != baseline.corpus_hash  # provenance sees the tape
    assert moved.adapter_hash != baseline.adapter_hash

    # internal derivation on a request-side-perturbed tape is rejected by the
    # E-4 replay guard (a stricter guarantee than exclusion)
    with pytest.raises(ValueError, match="replay guard"):
        build_l1_corpus(prestate, perturbed, SEED)


@pytest.mark.parametrize("rule", [AllocationRule.FIFO, AllocationRule.RANDOM_UNIT_WITHIN_PRICE])
def test_pre_round_state_only_rule(rule: AllocationRule) -> None:
    prestate, tape = _engine_tape(rule)
    full = build_l1_corpus(prestate, tape, SEED)

    cut = next(
        record.sequence
        for record in tape
        if record.event_type == EventType.ORDER_REQUEST and record.payload["event_id"] == 3
    )
    prefix = [record for record in tape if record.sequence < cut]
    short = build_l1_corpus(prestate, prefix, SEED)

    # round 2's existence cannot reach into inputs of rounds 0..1
    assert short.agent_states.shape == (2, 8, L1_D_STATE)
    assert torch.equal(short.agent_states, full.agent_states[:2])
    assert torch.equal(short.context, full.context[:2])
    assert torch.equal(short.features, full.features[:2])
    assert torch.equal(short.channels_inc, full.channels_inc[:2])

    # and a different round-0 realization changes inputs only from round 1 on
    other_prestate, other_tape = _engine_tape(rule, first_quantity=1)
    moved = build_l1_corpus(other_prestate, other_tape, SEED)
    assert torch.equal(moved.agent_states[0], full.agent_states[0])  # t=0 token
    assert not torch.equal(moved.agent_states[1], full.agent_states[1])
    assert moved.agent_states[1, 0, 0].item() == pytest.approx(math.log1p(1))
    assert full.agent_states[1, 0, 0].item() == pytest.approx(math.log1p(2))


def test_supervision_alignment() -> None:
    prestate, tape = _engine_tape(AllocationRule.FIFO)
    l1 = build_l1_corpus(prestate, tape, SEED)

    for index, round_ in enumerate(l1.rounds):
        assert torch.equal(
            l1.features[index], fexec_round_features(list(round_.payloads))
        )
        volume = 0
        cash = 0
        for payload in round_.payloads:
            execution = payload["execution"]
            assert isinstance(execution, dict)
            volume += execution["quantity"]
            cash += execution["price"] * execution["quantity"]
        assert l1.channels_inc[index].tolist() == [volume, cash]
        assert l1.channels_abs[index].tolist() == l1.channels_inc[: index + 1].sum(0).tolist()

    assert l1.n_agents == FactSurrogateConfig().n_slots
    assert torch.equal(l1.flow_slot, torch.zeros_like(l1.flow_slot))
    assert l1.match_ticks == (1, 2, 3)


def test_consumable_by_l1_surfaces() -> None:
    from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
    from ecomd.models.price_formation import PriceState

    prestate, tape = _engine_tape(AllocationRule.FIFO)
    l1 = build_l1_corpus(prestate, tape, SEED)

    # agent-state tensor is EcoMDSimulator's s surface: (n_agents, d_state)
    assert l1.agent_states[1].shape == (l1.n_agents, L1_D_STATE)
    assert l1.agent_states[1].dtype == torch.float32

    # context rows follow the ecomd.py:1110-1116 stack pattern exactly
    log_price, volatility, last_log_return = (
        l1.context[1, 0],
        l1.context[1, 1],
        l1.context[1, 2],
    )
    triple = torch.stack([log_price, volatility, last_log_return])
    assert triple.shape == (3,)
    assert torch.equal(triple, l1.context[1])

    config = EcoMDConfig(
        n_agents=l1.n_agents,
        d_state=L1_D_STATE,
        hidden=16,
        dt=0.01,
        pairwise_kind="ecomd_v2",
        v2_k_random=4,
        learn_gamma=False,
        learn_temperature=False,
    )
    simulator = EcoMDSimulator(config)
    price_state = PriceState(
        log_price=l1.context[1, 0].clone(),
        last_log_return=l1.context[1, 2].clone(),
        volatility=l1.context[1, 1].clone(),
        step=1,
    )
    s = l1.agent_states[1]
    generator = torch.Generator().manual_seed(0)
    s_next, price_next, _, _, _, _ = simulator.step(
        s, s, price_state, generator=generator
    )
    assert s_next.shape == s.shape
    assert torch.isfinite(s_next).all()
    assert torch.isfinite(price_next.log_price).all()


def test_frozen_bundle_end_to_end() -> None:
    prestate, tape = _load_frozen_fixture("fixture_fifo")
    first = build_l1_corpus(prestate, tape, SEED)
    second = build_l1_corpus(prestate, tape, SEED)

    assert first.allocation_rule == "fifo"
    assert first.n_rounds == len(first.match_ticks) >= 1
    assert first.n_executions == sum(
        1 for record in tape if record.event_type == EventType.EXECUTION
    )
    draw_share = FEXEC_ROUND_FEATURES.index("draw_volume_share")
    assert all(row[draw_share] == 0.0 for row in first.features.tolist())

    assert first.adapter_hash == second.adapter_hash
    _assert_tensor_identity(first, second)
    assert _serialized(first) == _serialized(second)

    series = emit_conserving_channels(prestate, tape)
    assert first.channels_inc.tolist() == series.increment_matrix()
    assert first.channels_abs.tolist() == series.cumulative_matrix()
    assert conservation_violations(series) == []


def test_malformed_and_mismatch_rejection() -> None:
    prestate = make_prestate(AllocationRule.FIFO)
    tape = _hand_tape(prestate)

    with pytest.raises(ValueError, match="seed"):
        build_l1_corpus(prestate, tape, -1)
    with pytest.raises(ValueError, match="n_slots"):
        build_l1_corpus(prestate, tape, SEED, n_slots=0)

    wrong_grid = dc_replace(_hand_series(prestate), ticks=(5, 8))
    with pytest.raises(ValueError, match="round grid"):
        build_l1_corpus(prestate, tape, SEED, series=wrong_grid)

    wrong_increments = dc_replace(
        _hand_series(prestate), increments=((3, 300), (4, 409))
    )
    with pytest.raises(ValueError, match="increment matrix disagrees"):
        build_l1_corpus(prestate, tape, SEED, series=wrong_increments)

    wrong_cumulatives = dc_replace(
        _hand_series(prestate), cumulatives=((3, 300), (7, 709))
    )
    with pytest.raises(ValueError, match="cumulative matrix disagrees"):
        build_l1_corpus(prestate, tape, SEED, series=wrong_cumulatives)

    wrong_session = dc_replace(_hand_series(prestate), session_id="S9999")
    with pytest.raises(ValueError, match="session"):
        build_l1_corpus(prestate, tape, SEED, series=wrong_session)

    wrong_rule = dc_replace(_hand_series(prestate), allocation_rule="pro_rata")
    with pytest.raises(ValueError, match="allocation rule"):
        build_l1_corpus(prestate, tape, SEED, series=wrong_rule)

    truncated = dc_replace(_hand_series(prestate), increments=((3, 300),))
    with pytest.raises(ValueError, match="increment_matrix"):
        build_l1_corpus(prestate, tape, SEED, series=truncated)

    bad_increments: Any = ((3, 300), (4, 408.5))
    non_int = _HandSeries(
        session_id=prestate.session_id,
        allocation_rule=prestate.allocation_rule.value,
        ticks=(5, 7),
        increments=bad_increments,
        cumulatives=((3, 300), (7, 708)),
    )
    with pytest.raises(ValueError, match="must be ints"):
        build_l1_corpus(prestate, tape, SEED, series=non_int)


def test_missing_emitter_path_raises_with_instructive_error() -> None:
    prestate = make_prestate(AllocationRule.FIFO)
    tape = _hand_tape(prestate)

    scripts_path = str(REPO_ROOT / "scripts")
    saved_path = list(sys.path)
    saved_modules = {
        name: module
        for name, module in sys.modules.items()
        if name == "lab_asset" or name.startswith("lab_asset.")
    }
    for name in saved_modules:
        del sys.modules[name]
    sys.path = [entry for entry in sys.path if entry != scripts_path]
    try:
        with pytest.raises(ValueError, match="series="):
            build_l1_corpus(prestate, tape, SEED)
    finally:
        sys.path = saved_path
        sys.modules.update(saved_modules)


def test_series_view_protocol_is_structural() -> None:
    # the E-4 concrete object satisfies the Protocol without inheritance
    prestate, tape = _engine_tape(AllocationRule.FIFO)
    series: ConservingSeriesView = emit_conserving_channels(prestate, tape)
    l1 = build_l1_corpus(prestate, tape, SEED, series=series)
    assert l1.n_rounds == 3
