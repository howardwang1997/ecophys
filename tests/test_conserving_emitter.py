"""Conserving-channel emitter tests (D0 build item E-4).

Core subject: the integer-exact volume/cash conservation identities of
``scripts/lab_asset/conserving_emitter.py`` across emitted clearing rounds,
byte-exact determinism, role attribution, execution-free-round handling, and
replay-guard tamper rejection. The clearing-round grid is E-1's corpus grammar
(engine-clock execution match ticks, ascending), verified row-for-row against
``ecomd.corpus.fexec_projector.project_fexec_corpus``.

Fixtures are consumed STRICTLY read-only:
- frozen A-2 exit bundle ``experiments/lab_asset_a2/a2_exit_20260905/``
  (manifest lineage fea8b136...9581c),
- lab-asset-v3.1 enrichment ``experiments/lab_asset_a2/enrichment_20260906/``
  (multi-order rationed levels; PI decision D1_03).

CPU smoke only: every re-execution is a <= 27-record fixture or a synthetic
4-actor session. No GPU, no training, no market data, no outcome access.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, replace
from pathlib import Path

import pytest
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from lab_asset.conserving_emitter import (  # noqa: E402
    CHANNEL_ORDER,
    ConservingChannelSeries,
    _execution_rounds,
    conservation_violations,
    emit_conserving_channels,
    emit_conserving_channels_json,
    regenerate_with_engine,
    settlement_violations,
)
from lab_asset.matching import ReferenceEngine  # noqa: E402
from lab_asset.replay import replay  # noqa: E402
from lab_asset.schema import (  # noqa: E402
    AllocationRule,
    EventType,
    InitialOrder,
    OrderRequest,
    SessionPrestate,
    Side,
    TapeRecord,
    ThreeClocks,
    prestate_from_json,
)

from ecomd.corpus.fexec_projector import project_fexec_corpus  # noqa: E402

FROZEN_DIR = REPO_ROOT / "experiments/lab_asset_a2/a2_exit_20260905"
ENRICHMENT_DIR = REPO_ROOT / "experiments/lab_asset_a2/enrichment_20260906"

ACTORS = ("alice", "bob", "carol", "dave")
ROLE_MAP = {
    "alice": "designated_maker",
    "bob": "designated_maker",
    "carol": "designated_maker",
    "dave": "trader",
}


# ─────────────────────────────────────────────────────────────────────────────
# Fixture loading (read-only)
# ─────────────────────────────────────────────────────────────────────────────


def load_tape(fixture_dir: Path) -> list[TapeRecord]:
    records: list[TapeRecord] = []
    for line in (fixture_dir / "tape.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        records.append(
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
    return records


def load_prestate(fixture_dir: Path) -> SessionPrestate:
    return prestate_from_json((fixture_dir / "prestate.json").read_text())


def tape_execution_totals(tape: list[TapeRecord]) -> tuple[int, int, int]:
    """Independent tape-side recomputation (volume, cash ticks, count)."""

    volume = 0
    cash = 0
    count = 0
    for record in tape:
        if record.event_type != EventType.EXECUTION:
            continue
        execution = record.payload["execution"]
        assert isinstance(execution, dict)
        quantity = execution["quantity"]
        price = execution["price"]
        assert isinstance(quantity, int) and isinstance(price, int)
        volume += quantity
        cash += price * quantity
        count += 1
    return volume, cash, count


def tape_match_ticks(tape: list[TapeRecord]) -> list[int]:
    """Independent tape-side round grid: distinct execution match ticks."""

    ticks: list[int] = []
    for record in tape:
        if record.event_type != EventType.EXECUTION:
            continue
        execution = record.payload["execution"]
        clocks = execution["clocks"]
        match_ts = (
            clocks["match_ts"] if isinstance(clocks, dict) else clocks.match_ts
        )
        assert isinstance(match_ts, int)
        if match_ts not in ticks:
            ticks.append(match_ts)
    return ticks


# ─────────────────────────────────────────────────────────────────────────────
# Synthetic session (both kernels)
# ─────────────────────────────────────────────────────────────────────────────


def synthetic_prestate(rule: AllocationRule, *, seed: int = 7) -> SessionPrestate:
    return SessionPrestate(
        session_id=f"e4-synth-{rule.value}",
        seed=seed,
        allocation_rule=rule,
        initial_cash={actor: 10_000 for actor in ACTORS},
        initial_inventory={actor: 100 for actor in ACTORS},
        price_bands=(90, 110),
        actors=ACTORS,
        actor_roles=dict(ROLE_MAP),
        initial_book=(
            InitialOrder("A1", "alice", Side.ASK, 100, 5),
            InitialOrder("A2", "bob", Side.ASK, 100, 3),
            InitialOrder("B1", "carol", Side.BID, 98, 3),
        ),
    )


def run_synthetic(prestate: SessionPrestate) -> list[TapeRecord]:
    engine = ReferenceEngine(prestate)
    engine.submit(
        OrderRequest(
            event_id=1,
            actor="dave",
            client_order_id="d1",
            side=Side.BID,
            price=100,
            quantity=6,
            clocks=ThreeClocks(1, 1, 1),
            round_id=1,
        )
    )
    engine.submit(
        OrderRequest(
            event_id=2,
            actor="dave",
            client_order_id="d2",
            side=Side.BID,
            price=90,
            quantity=1,
            clocks=ThreeClocks(2, 2, 2),
            round_id=2,
        )
    )
    engine.submit(
        OrderRequest(
            event_id=3,
            actor="dave",
            client_order_id="d3",
            side=Side.ASK,
            price=98,
            quantity=2,
            clocks=ThreeClocks(3, 3, 3),
            round_id=3,
        )
    )
    engine.finish()
    return engine.tape


@pytest.fixture(params=[AllocationRule.FIFO, AllocationRule.RANDOM_UNIT_WITHIN_PRICE])
def synthetic_series(request: pytest.FixtureRequest) -> ConservingChannelSeries:
    rule = request.param
    assert isinstance(rule, AllocationRule)
    prestate = synthetic_prestate(rule)
    return emit_conserving_channels(prestate, run_synthetic(prestate))


# ─────────────────────────────────────────────────────────────────────────────
# Conservation identities (the core tests)
# ─────────────────────────────────────────────────────────────────────────────


def test_synthetic_conservation_and_settlement_identities(
    synthetic_series: ConservingChannelSeries,
) -> None:
    assert conservation_violations(synthetic_series) == []
    prestate = synthetic_prestate(
        AllocationRule(synthetic_series.allocation_rule)
    )
    settlement = settlement_violations(
        prestate, run_synthetic(prestate), synthetic_series
    )
    assert settlement == []


def test_synthetic_channels_and_matrices(synthetic_series: ConservingChannelSeries) -> None:
    series = synthetic_series
    # Round 2 is execution-free (resting order only): NOT a round on the E-1
    # engine-clock grid; the grid is the distinct execution match ticks [1, 3].
    assert series.n_rounds == 2
    assert [round_.match_ts for round_ in series.rounds] == [1, 3]
    assert series.rounds[0].round_ids == (1,)
    assert series.rounds[1].round_ids == (3,)
    assert series.rounds[0].volume_units == 6
    assert series.rounds[0].cash_ticks == 600
    assert series.rounds[1].volume_units == 2
    assert series.rounds[1].cash_ticks == 196
    assert series.increment_matrix() == [[6, 600], [2, 196]]
    assert series.cumulative_matrix() == [[6, 600], [8, 796]]
    assert CHANNEL_ORDER == ("volume_units", "cash_ticks")
    assert series.to_payload()["channel_order"] == list(CHANNEL_ORDER)


def test_synthetic_side_and_role_attribution(synthetic_series: ConservingChannelSeries) -> None:
    series = synthetic_series
    first, last = series.rounds
    assert (first.buy_volume_units, first.buy_cash_ticks) == (6, 600)
    assert (first.sell_volume_units, first.sell_cash_ticks) == (0, 0)
    assert (last.buy_volume_units, last.buy_cash_ticks) == (0, 0)
    assert (last.sell_volume_units, last.sell_cash_ticks) == (2, 196)
    for round_ in (first, last):
        assert round_.aggressor_role_volume == {"trader": round_.volume_units}
        assert round_.aggressor_role_cash == {"trader": round_.cash_ticks}
        assert round_.maker_role_volume == {"designated_maker": round_.volume_units}
        assert round_.maker_role_cash == {"designated_maker": round_.cash_ticks}


def test_synthetic_fifo_actor_deltas_exact() -> None:
    prestate = synthetic_prestate(AllocationRule.FIFO)
    series = emit_conserving_channels(prestate, run_synthetic(prestate))
    first, last = series.rounds
    # FIFO round 1 (match tick 1): alice fills 5 @100, bob fills 1 @100; dave buys.
    assert first.actor_cash_delta == {"alice": 500, "bob": 100, "carol": 0, "dave": -600}
    assert first.actor_inventory_delta == {
        "alice": -5,
        "bob": -1,
        "carol": 0,
        "dave": 6,
    }
    assert first.actor_units_bought_delta == {
        "alice": 0,
        "bob": 0,
        "carol": 0,
        "dave": 6,
    }
    assert first.actor_units_sold_delta == {"alice": 5, "bob": 1, "carol": 0, "dave": 0}
    # Round 2 (match tick 3): dave aggressively sells 2 @98 into carol's
    # resting bid: carol is the buyer (pays 196, receives 2 units).
    assert last.actor_cash_delta == {"alice": 0, "bob": 0, "carol": -196, "dave": 196}
    assert last.actor_inventory_delta == {"alice": 0, "bob": 0, "carol": 2, "dave": -2}


def test_byte_exact_determinism() -> None:
    for rule in (AllocationRule.FIFO, AllocationRule.RANDOM_UNIT_WITHIN_PRICE):
        prestate = synthetic_prestate(rule)
        tape = run_synthetic(prestate)
        first = emit_conserving_channels_json(prestate, tape)
        second = emit_conserving_channels_json(prestate, reloaded(tape))
        assert first == second
        assert emit_conserving_channels(prestate, tape).to_json() == first


def plain_payload(record: TapeRecord) -> dict[str, object]:
    """Deep-converted payload (asdict semantics): nested dataclasses to dicts."""

    raw = asdict(record)["payload"]
    assert isinstance(raw, dict)
    return json.loads(json.dumps(raw, sort_keys=True))


def reloaded(tape: list[TapeRecord]) -> list[TapeRecord]:
    """Re-parse the tape through its canonical JSON round trip."""

    return [replace(record, payload=plain_payload(record)) for record in tape]


def test_tampered_tape_rejected() -> None:
    prestate = synthetic_prestate(AllocationRule.FIFO)
    tape = run_synthetic(prestate)
    exec_index = next(
        i for i, r in enumerate(tape) if r.event_type == EventType.EXECUTION
    )
    tampered = list(tape)
    payload = plain_payload(tape[exec_index])
    inner = payload["execution"]
    assert isinstance(inner, dict)
    inner["quantity"] += 1
    tampered[exec_index] = replace(tape[exec_index], payload=payload)
    with pytest.raises(ValueError, match="replay guard"):
        emit_conserving_channels(prestate, tampered)
    request_tampered = list(tape)
    request_payload = plain_payload(tape[1])
    assert isinstance(request_payload, dict)
    request_payload["quantity"] = 5
    request_tampered[1] = replace(tape[1], payload=request_payload)
    with pytest.raises(ValueError, match="replay guard"):
        emit_conserving_channels(prestate, request_tampered)


def test_execution_round_grouping() -> None:
    """The grid groups execution records by match_ts, ascending, one tick
    merging multiple executions; non-execution records never key rounds."""

    def execution(sequence: int, match_ts: int) -> TapeRecord:
        return TapeRecord(
            sequence=sequence,
            event_type=EventType.EXECUTION,
            payload={
                "execution": {
                    "quantity": 1,
                    "price": 100,
                    "round_id": 0,
                    "clocks": {"match_ts": match_ts},
                }
            },
        )

    def request(sequence: int) -> TapeRecord:
        return TapeRecord(
            sequence=sequence,
            event_type=EventType.ORDER_REQUEST,
            payload={"round_id": 5},
        )

    tape = [request(0), execution(1, 7), execution(2, 3), execution(3, 7), request(4)]
    assert _execution_rounds(tape) == {3: [2], 7: [1, 3]}
    assert _execution_rounds([request(0), request(1)]) == {}


def test_no_execution_session_emits_no_rounds() -> None:
    """Execution-free ticks are not rounds (E-1's grammar): a session whose
    requests never trade emits an empty series, not zero-valued rounds."""

    prestate = synthetic_prestate(AllocationRule.FIFO)
    engine = ReferenceEngine(prestate)
    engine.submit(
        OrderRequest(
            event_id=1,
            actor="dave",
            client_order_id="d1",
            side=Side.BID,
            price=95,
            quantity=2,
            clocks=ThreeClocks(1, 1, 1),
            round_id=1,
        )
    )
    engine.finish()
    series = emit_conserving_channels(prestate, engine.tape)
    assert series.rounds == ()
    assert series.increment_matrix() == []
    assert series.cumulative_matrix() == []
    assert conservation_violations(series) == []
    assert settlement_violations(prestate, engine.tape, series) == []
    assert series.to_json() == emit_conserving_channels_json(prestate, engine.tape)


def test_request_free_session_has_no_rounds() -> None:
    prestate = synthetic_prestate(AllocationRule.FIFO)
    engine = ReferenceEngine(prestate)
    engine.finish()
    series = emit_conserving_channels(prestate, engine.tape)
    assert series.rounds == ()
    assert series.increment_matrix() == []
    assert series.to_json() == emit_conserving_channels_json(prestate, engine.tape)
    assert conservation_violations(series) == []


def test_violation_detectors_fire_on_corrupted_series() -> None:
    prestate = synthetic_prestate(AllocationRule.FIFO)
    tape = run_synthetic(prestate)
    series = emit_conserving_channels(prestate, tape)
    corrupted = replace(
        series,
        rounds=(
            replace(series.rounds[0], cash_ticks=series.rounds[0].cash_ticks + 1),
            *series.rounds[1:],
        ),
    )
    assert conservation_violations(corrupted)
    assert settlement_violations(prestate, tape, corrupted)
    bad_actor = replace(
        series.rounds[0],
        actor_cash_delta={**series.rounds[0].actor_cash_delta, "alice": 501},
    )
    corrupted_actor = replace(
        series, rounds=(bad_actor, *series.rounds[1:])
    )
    assert settlement_violations(prestate, tape, corrupted_actor)


def test_regenerate_with_engine_exposes_state() -> None:
    prestate = synthetic_prestate(AllocationRule.FIFO)
    tape = run_synthetic(prestate)
    engine, regenerated = regenerate_with_engine(prestate, tape)
    assert regenerated == tape
    # cash/inventory live in engine state: total cash conserved, volume moved
    assert sum(engine.cash.values()) == sum(prestate.initial_cash.values())
    assert sum(engine.inventory.values()) == sum(prestate.initial_inventory.values())
    assert engine.units_bought["dave"] == 6
    assert engine.units_bought["carol"] == 2
    assert engine.units_sold["alice"] == 5
    assert engine.units_sold["dave"] == 2
    assert engine.cash["dave"] == 10_000 - 600 + 196
    assert engine.inventory["carol"] == 100 + 2


# ─────────────────────────────────────────────────────────────────────────────
# Cross-item agreement: E-1's frozen corpus grammar (round grid + channels)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("rule", [AllocationRule.FIFO, AllocationRule.RANDOM_UNIT_WITHIN_PRICE])
def test_projector_channel_agreement_synthetic(rule: AllocationRule) -> None:
    prestate = synthetic_prestate(rule)
    tape = run_synthetic(prestate)
    series = emit_conserving_channels(prestate, tape)
    corpus = project_fexec_corpus(prestate, tape, seed=0)
    assert series.increment_matrix() == corpus.channels_delta.tolist()
    assert series.cumulative_matrix() == corpus.channels_cumulative.tolist()
    assert [round_.match_ts for round_ in series.rounds] == list(corpus.match_ticks)
    assert [round_.round_ids for round_ in series.rounds] == [
        round_.round_ids for round_ in corpus.rounds
    ]


@pytest.mark.parametrize("name", ["fixture_fifo", "fixture_random_unit_within_price"])
def test_projector_channel_agreement_frozen(name: str) -> None:
    prestate = load_prestate(FROZEN_DIR / name)
    tape = load_tape(FROZEN_DIR / name)
    series = emit_conserving_channels(prestate, tape)
    corpus = project_fexec_corpus(prestate, tape, seed=0)
    assert series.increment_matrix() == corpus.channels_delta.tolist()
    assert series.cumulative_matrix() == corpus.channels_cumulative.tolist()
    assert [round_.match_ts for round_ in series.rounds] == list(corpus.match_ticks)
    # round_id is metadata only: uniformly 0 in the frozen bundle
    assert all(round_.round_ids == (0,) for round_ in series.rounds)
    assert torch.equal(
        torch.tensor(series.increment_matrix(), dtype=torch.int64),
        corpus.channels_delta,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Frozen A-2 exit bundle (read-only; manifest fea8b136...9581c)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("name", ["fixture_fifo", "fixture_random_unit_within_price"])
def test_frozen_bundle_conservation(name: str) -> None:
    prestate = load_prestate(FROZEN_DIR / name)
    tape = load_tape(FROZEN_DIR / name)
    assert replay(prestate, tape).ok
    series = emit_conserving_channels(prestate, tape)
    assert conservation_violations(series) == []
    assert settlement_violations(prestate, tape, series) == []
    volume, cash, count = tape_execution_totals(tape)
    assert series.cumulative_matrix()[-1] == [volume, cash]
    assert sum(r.n_executions for r in series.rounds) == count
    assert [round_.match_ts for round_ in series.rounds] == tape_match_ticks(tape)
    assert series.to_json() == emit_conserving_channels_json(prestate, tape)


@pytest.mark.parametrize("name", ["fixture_fifo", "fixture_random_unit_within_price"])
def test_frozen_bundle_engine_state_matches_series(name: str) -> None:
    prestate = load_prestate(FROZEN_DIR / name)
    tape = load_tape(FROZEN_DIR / name)
    series = emit_conserving_channels(prestate, tape)
    engine, _ = regenerate_with_engine(prestate, tape)
    initial_cash = {actor: prestate.initial_cash[actor] for actor in prestate.actors}
    expected_cash = {
        actor: initial_cash[actor]
        + sum(r.actor_cash_delta[actor] for r in series.rounds)
        for actor in prestate.actors
    }
    assert engine.cash == expected_cash
    assert sum(engine.units_bought.values()) == series.rounds[-1].cumulative_volume_units
    assert sum(engine.units_sold.values()) == series.rounds[-1].cumulative_volume_units


# ─────────────────────────────────────────────────────────────────────────────
# lab-asset-v3.1 enrichment (multi-order rationed fixtures; read-only)
# ─────────────────────────────────────────────────────────────────────────────


def enrichment_names() -> list[str]:
    manifest = json.loads((ENRICHMENT_DIR / "enrichment_manifest.json").read_text())
    fixtures = manifest["fixtures"]
    assert isinstance(fixtures, dict)
    return sorted(fixtures)


@pytest.mark.parametrize("name", enrichment_names())
def test_enrichment_bundle_conservation(name: str) -> None:
    prestate = load_prestate(ENRICHMENT_DIR / "fixtures" / name)
    tape = load_tape(ENRICHMENT_DIR / "fixtures" / name)
    assert replay(prestate, tape).ok
    series = emit_conserving_channels(prestate, tape)
    assert conservation_violations(series) == []
    assert settlement_violations(prestate, tape, series) == []
    volume, cash, count = tape_execution_totals(tape)
    assert series.cumulative_matrix()[-1] == [volume, cash]
    assert sum(r.n_executions for r in series.rounds) == count
    assert [round_.match_ts for round_ in series.rounds] == tape_match_ticks(tape)


def test_enrichment_arm_pairs_aggregate_channels_match() -> None:
    """C2(a) CRN premise through the conserving channels: identical request
    streams across arms give identical AGGREGATE conserving series (identity
    allocations differ; per-round totals must not)."""

    manifest = json.loads((ENRICHMENT_DIR / "enrichment_manifest.json").read_text())
    pairs = manifest["pairs"]
    assert isinstance(pairs, dict)
    assert len(pairs) >= 2
    for pair_key in sorted(pairs):
        members = pairs[pair_key]
        assert isinstance(members, list) and len(members) == 2
        fifo_name, ru_name = members
        series = []
        for member in (fifo_name, ru_name):
            prestate = load_prestate(ENRICHMENT_DIR / member)
            tape = load_tape(ENRICHMENT_DIR / member)
            emitted = emit_conserving_channels(prestate, tape)
            assert conservation_violations(emitted) == []
            series.append(emitted)
        fifo_series, ru_series = series
        assert fifo_series.increment_matrix() == ru_series.increment_matrix()
        assert fifo_series.cumulative_matrix() == ru_series.cumulative_matrix()
        assert (
            fifo_series.initial_total_cash == ru_series.initial_total_cash
        )
        assert (
            fifo_series.rounds[-1].post_total_cash
            == ru_series.rounds[-1].post_total_cash
        )
