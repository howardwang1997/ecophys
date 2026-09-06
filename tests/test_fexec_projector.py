"""E-1 F_exec corpus projector: CPU spot checks (build item E-1, D-1 stage).

Second-scale, CPU-only, single-file scope (PI no-heavy-compute rule): hand
tapes, tiny engine sessions, and READ-ONLY use of the frozen A-2 bundle
(``experiments/lab_asset_a2/a2_exit_20260905/`` — bytes are read, never
written; per-file sha256s re-verified against the bundle manifest before any
projection). No GPU, no market data, no training.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import sys
from dataclasses import replace as dc_replace
from pathlib import Path
from typing import Any

import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

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

from ecomd.corpus.fexec_projector import (
    DEFAULT_N_SLOTS,
    FEXEC_REQUIRED_FIELDS,
    project_fexec_corpus,
)
from ecomd.models.fact_surrogate import FEXEC_ROUND_FEATURES, fexec_round_features

REPO_ROOT = Path(__file__).resolve().parents[1]
FROZEN_DIR = REPO_ROOT / "experiments/lab_asset_a2/a2_exit_20260905"
SEED = 11000  # B1/B2 training namespace root (PI decision D1_10)


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
    maker_order_id: str = "O00000001",
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "execution": {
            "event_id": event_id,
            "execution_id": execution_id,
            "aggressor_order_id": "O00000002",
            "maker_order_id": maker_order_id,
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


def _engine_tape(
    rule: AllocationRule, *, seed: int = 7, same_tick: bool = False
) -> tuple[SessionPrestate, list[TapeRecord]]:
    prestate = make_prestate(
        rule,
        seed=seed,
        initial_book=(InitialOrder("A1", "b", Side.ASK, 101, 5),),
    )
    engine = ReferenceEngine(prestate)
    engine.submit(
        OrderRequest(
            event_id=1,
            actor="c",
            client_order_id="c1",
            side=Side.BID,
            price=101,
            quantity=2,
            clocks=ThreeClocks(1, 1, 1),
        )
    )
    engine.submit(
        OrderRequest(
            event_id=2,
            actor="d",
            client_order_id="d1",
            side=Side.BID,
            price=101,
            quantity=1,
            clocks=ThreeClocks(1 if same_tick else 2, 1 if same_tick else 2, 1 if same_tick else 2),
        )
    )
    engine.submit(
        OrderRequest(
            event_id=3,
            actor="a",
            client_order_id="a1",
            side=Side.BID,
            price=99,
            quantity=1,
            clocks=ThreeClocks(3, 3, 3),
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


# --------------------------------------------------------------------------- tests


def test_hand_computed_small_tape_projection() -> None:
    prestate = make_prestate(AllocationRule.FIFO)
    corpus = project_fexec_corpus(prestate, _hand_tape(prestate), SEED)

    assert corpus.match_ticks == (5, 7)
    assert corpus.n_executions == 3
    assert [round_.first_sequence for round_ in corpus.rounds] == [3, 6]
    assert [round_.last_sequence for round_ in corpus.rounds] == [4, 6]
    assert all(round_.round_ids == (0,) for round_ in corpus.rounds)

    # round 0: volume 3 at price 100; round 1: volume 4 at price 102
    assert corpus.channels_delta.tolist() == [[3, 300], [4, 408]]
    assert corpus.channels_cumulative.tolist() == [[3, 300], [7, 708]]
    assert corpus.slot_prices.tolist() == [[100] + [0] * 7, [102] + [0] * 7]
    assert corpus.slot_quantities.tolist() == [[3] + [0] * 7, [4] + [0] * 7]

    row0 = corpus.features[0].tolist()
    assert row0[FEXEC_ROUND_FEATURES.index("has_execution")] == 1.0
    assert row0[FEXEC_ROUND_FEATURES.index("log_n_exec")] == pytest.approx(math.log1p(2))
    assert row0[FEXEC_ROUND_FEATURES.index("log_volume")] == pytest.approx(math.log1p(3))
    assert row0[FEXEC_ROUND_FEATURES.index("aggressor_buy_share")] == 1.0
    assert row0[FEXEC_ROUND_FEATURES.index("draw_volume_share")] == 0.0
    assert row0[FEXEC_ROUND_FEATURES.index("pre_spread_ticks")] == 2.0
    assert row0[FEXEC_ROUND_FEATURES.index("post_spread_ticks")] == 2.0
    assert row0[FEXEC_ROUND_FEATURES.index("spread_change")] == 0.0
    assert row0[FEXEC_ROUND_FEATURES.index("mid_move_ticks")] == 0.0
    assert row0[FEXEC_ROUND_FEATURES.index("vwap_rel_spread")] == 0.0
    assert row0[FEXEC_ROUND_FEATURES.index("log_maker_residual")] == pytest.approx(
        math.log1p(2)
    )
    assert row0[FEXEC_ROUND_FEATURES.index("quotes_missing")] == 0.0

    row1 = corpus.features[1].tolist()
    assert row1[FEXEC_ROUND_FEATURES.index("aggressor_buy_share")] == 0.0
    assert row1[FEXEC_ROUND_FEATURES.index("draw_volume_share")] == 1.0
    assert row1[FEXEC_ROUND_FEATURES.index("spread_change")] == 2.0
    assert row1[FEXEC_ROUND_FEATURES.index("mid_move_ticks")] == 2.0
    assert row1[FEXEC_ROUND_FEATURES.index("best_bid_move")] == 1.0
    assert row1[FEXEC_ROUND_FEATURES.index("best_ask_move")] == 3.0
    assert row1[FEXEC_ROUND_FEATURES.index("vwap_rel_spread")] == pytest.approx(1.0)


def test_engine_tape_round_grouping_by_match_ts() -> None:
    prestate, tape = _engine_tape(AllocationRule.FIFO)
    corpus = project_fexec_corpus(prestate, tape, SEED)

    # requests at ticks 1 and 2 execute; the tick-3 resting order does not
    assert corpus.match_ticks == (1, 2)
    assert corpus.n_executions == 2
    assert corpus.channels_delta.tolist() == [[2, 202], [1, 101]]
    assert corpus.slot_prices.tolist() == [[101] + [0] * 7] * 2
    assert corpus.slot_quantities.tolist() == [[2] + [0] * 7, [1] + [0] * 7]

    # one-sided initial book: engine-real None best_bid exercises the fallback
    assert corpus.features[0][FEXEC_ROUND_FEATURES.index("quotes_missing")].item() == 1.0

    merged_prestate, merged_tape = _engine_tape(AllocationRule.FIFO, same_tick=True)
    merged = project_fexec_corpus(merged_prestate, merged_tape, SEED)
    assert merged.match_ticks == (1,)
    assert merged.n_executions == 2
    assert merged.channels_delta.tolist() == [[3, 303]]


def test_padding_contract_and_overflow() -> None:
    prestate = make_prestate(AllocationRule.FIFO)

    def multi_level_tape() -> list[TapeRecord]:
        records = [_hand_tape(prestate)[0]]
        for index, price in enumerate((100, 101, 102)):
            records.append(
                _record(
                    index + 2,
                    EventType.EXECUTION,
                    _execution_payload(
                        quantity=1,
                        price=price,
                        maker_remaining=1,
                        side="B",
                        match_ts=5,
                        round_id=0,
                        pre_bid=99,
                        pre_ask=103,
                        post_bid=99,
                        post_ask=103,
                        event_id=index + 2,
                    ),
                )
            )
        return records

    corpus = project_fexec_corpus(prestate, multi_level_tape(), SEED, n_slots=3)
    assert corpus.n_slots == 3
    assert corpus.slot_prices.tolist() == [[100, 101, 102]]
    assert corpus.slot_quantities.tolist() == [[1, 1, 1]]

    narrow = project_fexec_corpus(prestate, multi_level_tape(), SEED, n_slots=5)
    assert narrow.slot_prices.tolist() == [[100, 101, 102, 0, 0]]
    assert narrow.slot_quantities.tolist() == [[1, 1, 1, 0, 0]]

    with pytest.raises(ValueError, match="n_slots"):
        project_fexec_corpus(prestate, multi_level_tape(), SEED, n_slots=2)
    with pytest.raises(ValueError, match="n_slots"):
        project_fexec_corpus(prestate, multi_level_tape(), SEED, n_slots=0)


def test_byte_identity_and_regeneration_safety() -> None:
    prestate, tape = _engine_tape(AllocationRule.RANDOM_UNIT_WITHIN_PRICE, seed=11)
    first = project_fexec_corpus(prestate, tape, SEED)
    second = project_fexec_corpus(prestate, tape, SEED)
    assert first.corpus_hash == second.corpus_hash
    for name in ("features", "channels_delta", "channels_cumulative",
                 "slot_prices", "slot_quantities"):
        assert torch.equal(getattr(first, name), getattr(second, name))

    def serialized(corpus: Any) -> bytes:
        buffer = io.BytesIO()
        torch.save(
            {name: getattr(corpus, name) for name in
             ("features", "channels_delta", "channels_cumulative",
              "slot_prices", "slot_quantities")},
            buffer,
        )
        return buffer.getvalue()

    assert serialized(first) == serialized(second)

    from_regenerated = project_fexec_corpus(
        prestate, regenerate(prestate, tape), SEED
    )
    assert from_regenerated.corpus_hash == first.corpus_hash
    assert serialized(from_regenerated) == serialized(first)

    other_seed = project_fexec_corpus(prestate, tape, SEED + 1)
    assert other_seed.corpus_hash != first.corpus_hash
    assert torch.equal(other_seed.features, first.features)


def test_exclusion_of_request_side_events() -> None:
    prestate, tape = _engine_tape(AllocationRule.FIFO)
    baseline = project_fexec_corpus(prestate, tape, SEED)

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
    moved = project_fexec_corpus(prestate, perturbed, SEED)

    assert moved.content_hash == baseline.content_hash
    assert torch.equal(moved.features, baseline.features)
    assert torch.equal(moved.channels_delta, baseline.channels_delta)
    assert torch.equal(moved.slot_prices, baseline.slot_prices)
    assert moved.tape_hash != baseline.tape_hash
    assert moved.corpus_hash != baseline.corpus_hash

    # the selection itself never carries request-side payload fields
    for round_ in moved.rounds:
        for payload in round_.payloads:
            assert set(payload) <= set(FEXEC_REQUIRED_FIELDS) | {"allocation_draw"}
            assert "resting_quantity" not in payload


def test_none_quote_fallback() -> None:
    prestate = make_prestate(AllocationRule.FIFO)
    tape = [
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
        _record(
            2,
            EventType.EXECUTION,
            _execution_payload(
                quantity=2,
                price=100,
                maker_remaining=1,
                side="B",
                match_ts=4,
                round_id=0,
                pre_bid=99,
                pre_ask=101,
                post_bid=None,
                post_ask=101,
            ),
        ),
    ]
    corpus = project_fexec_corpus(prestate, tape, SEED)
    row = corpus.features[0].tolist()
    assert row[FEXEC_ROUND_FEATURES.index("quotes_missing")] == 1.0
    assert row[FEXEC_ROUND_FEATURES.index("pre_spread_ticks")] == 2.0
    assert row[FEXEC_ROUND_FEATURES.index("post_spread_ticks")] == 0.0
    assert row[FEXEC_ROUND_FEATURES.index("spread_change")] == -2.0
    assert row[FEXEC_ROUND_FEATURES.index("mid_move_ticks")] == 1.0
    assert row[FEXEC_ROUND_FEATURES.index("best_bid_move")] == 0.0
    assert row[FEXEC_ROUND_FEATURES.index("best_ask_move")] == 0.0
    assert row == fexec_round_features(list(corpus.rounds[0].payloads)).tolist()


def test_malformed_tape_rejection() -> None:
    prestate = make_prestate(AllocationRule.FIFO)
    valid = _hand_tape(prestate)

    def with_execution_payload(mutate: Any) -> list[TapeRecord]:
        records = list(valid)
        broken = dict(records[2].payload)
        mutate(broken)
        records[2] = dc_replace(records[2], payload=broken)
        return records

    def drop(key: str) -> Any:
        def apply(payload: dict[str, Any]) -> None:
            del payload[key]

        return apply

    wrong_version = [
        dc_replace(
            valid[0],
            payload={**valid[0].payload, "schema_version": "lab-asset-v2"},
        ),
        *valid[1:],
    ]
    other_prestate = make_prestate(AllocationRule.FIFO, session_id="S0002")
    cases: dict[str, Any] = {
        "missing_fexec_field": with_execution_payload(drop("maker_role")),
        "extra_request_side_field": with_execution_payload(
            lambda p: p.update({"resting_quantity": 3})
        ),
        "broken_allocation_draw": with_execution_payload(
            lambda p: p.update(
                {"allocation_draw": {"price": 100, "eligible_units": 4}}
            )
        ),
        "non_int_match_ts": with_execution_payload(
            lambda p: p["execution"]["clocks"].update({"match_ts": "5"})
        ),
        "negative_match_ts": with_execution_payload(
            lambda p: p["execution"]["clocks"].update({"match_ts": -1})
        ),
        "float_quantity": with_execution_payload(
            lambda p: p["execution"].update({"quantity": 2.5})
        ),
        "bad_side": with_execution_payload(
            lambda p: p["execution"].update({"side_of_aggressor": "X"})
        ),
        "no_session_start": list(valid[1:]),
        "duplicate_session_start": [valid[1], valid[0], *valid[2:]],
        "wrong_schema_version": wrong_version,
    }
    for tape_arg in cases.values():
        with pytest.raises(ValueError):
            project_fexec_corpus(prestate, tape_arg, SEED)
    with pytest.raises(ValueError):
        project_fexec_corpus(other_prestate, list(valid), SEED)
    with pytest.raises(ValueError):
        project_fexec_corpus(prestate, list(valid), -1)


def test_tensor_shapes_and_dtypes() -> None:
    prestate, tape = _engine_tape(AllocationRule.FIFO)
    corpus = project_fexec_corpus(prestate, tape, SEED)
    assert corpus.features.shape == (2, len(FEXEC_ROUND_FEATURES))
    assert corpus.features.dtype == torch.float32
    assert corpus.channels_delta.dtype == torch.int64
    assert corpus.channels_delta.shape == (2, 2)
    assert corpus.slot_prices.shape == (2, DEFAULT_N_SLOTS)
    assert corpus.slot_quantities.dtype == torch.int64
    assert torch.equal(
        corpus.channels_cumulative, torch.cumsum(corpus.channels_delta, dim=0)
    )

    empty = project_fexec_corpus(
        prestate, [tape[0], tape[-1]], SEED  # session_start + session_end only
    )
    assert empty.features.shape == (0, len(FEXEC_ROUND_FEATURES))
    assert empty.channels_delta.shape == (0, 2)
    assert empty.slot_prices.shape == (0, DEFAULT_N_SLOTS)
    assert empty.n_executions == 0


def test_frozen_bundle_fifo_projection() -> None:
    prestate, tape = _load_frozen_fixture("fixture_fifo")
    corpus = project_fexec_corpus(prestate, tape, SEED)

    assert corpus.allocation_rule == "fifo"
    assert len(corpus.rounds) == len(corpus.match_ticks) >= 1
    assert corpus.features.shape[1] == len(FEXEC_ROUND_FEATURES)
    draw_share = FEXEC_ROUND_FEATURES.index("draw_volume_share")
    assert corpus.n_executions == sum(
        1 for record in tape if record.event_type == EventType.EXECUTION
    )
    assert all(
        row[draw_share] == 0.0 for row in corpus.features.tolist()
    ), "fifo executions must carry no allocation_draw"

    for index, round_ in enumerate(corpus.rounds):
        assert torch.equal(
            corpus.features[index], fexec_round_features(list(round_.payloads))
        )
        assert round_.round_index == index
    assert list(corpus.match_ticks) == sorted(corpus.match_ticks)


def test_frozen_bundle_random_unit_and_regeneration() -> None:
    prestate, tape = _load_frozen_fixture("fixture_random_unit_within_price")
    corpus = project_fexec_corpus(prestate, tape, SEED)

    assert corpus.allocation_rule == "random_unit_within_price"
    draw_share = FEXEC_ROUND_FEATURES.index("draw_volume_share")
    assert all(row[draw_share] == 1.0 for row in corpus.features.tolist()), (
        "every random-unit execution record carries allocation_draw"
    )

    regenerated = project_fexec_corpus(prestate, regenerate(prestate, tape), SEED)
    assert regenerated.corpus_hash == corpus.corpus_hash
    assert regenerated.content_hash == corpus.content_hash
    assert torch.equal(regenerated.features, corpus.features)
    assert torch.equal(regenerated.channels_delta, corpus.channels_delta)
    assert torch.equal(regenerated.slot_quantities, corpus.slot_quantities)

    # channels/slots re-derived by hand from the execution payloads
    volume = 0
    cash = 0
    levels: dict[int, int] = {}
    for record in tape:
        if record.event_type != EventType.EXECUTION:
            continue
        execution = record.payload["execution"]
        assert isinstance(execution, dict)
        quantity = execution["quantity"]
        price = execution["price"]
        volume += quantity
        cash += price * quantity
        levels[price] = levels.get(price, 0) + quantity
    assert corpus.channels_delta.sum(dim=0).tolist() == [volume, cash]
    assert corpus.slot_prices[0, : len(levels)].tolist() == sorted(levels)
    assert corpus.slot_quantities[0, : len(levels)].tolist() == [
        levels[price] for price in sorted(levels)
    ]
