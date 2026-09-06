"""Conserving-channel emitter (D0 build item E-4).

Extracts the C5 conserving-channel series from regenerated engine state: per
clearing round, the two AGGREGATE engine-level channels {total executed volume
units, total executed cash ticks} (prereg v2 clause C5, panel R2-6).  Cash and
inventory are engine STATE, not tape payload fields (simulator contracts
section 1, "Conservation and settlement"): they enter tapes only through the
state hashes.  The emitter therefore re-executes the recorded request stream
exactly as ``lab_asset.replay.regenerate`` does -- reusing its record->request
coercion helpers and enforcing ``replay``'s record-by-record comparison -- while
keeping the engine handle so ledger snapshots (cash, inventory, units_bought,
units_sold) can be read at round boundaries.

Round grid: the corpus clearing-round grammar owned by the F_exec projector
(build item E-1, ``ecomd/corpus/fexec_projector.py``) -- a clearing round is the
set of execution records sharing one ``execution.clocks.match_ts`` (the engine's
``last_match_ts``), indexed by the distinct execution match ticks in ascending
order; requests landing on one tick merge into one round.  Execution-free ticks
are not rounds (they carry no F_exec information; E-1's documented decision),
so sessions without executions emit an empty series.  The client-supplied
``round_id`` is carried per round as metadata only (it is client-controlled and
uniformly 0 in the frozen fixtures).  Sharing E-1's grid is what keeps the
corpus contract lineage-invariant: the per-round channel matrices below align
row-for-row with the projector's ``channels_delta``/``channels_cumulative``
(order pinned by ``CHANNEL_ORDER``), which is verified by a cross-item test.

Ledger windows are exact because ``ReferenceEngine._settle`` is the ONLY
mutator of the four per-actor ledgers outside construction (cash, inventory,
units_bought, units_sold; matching.py ``__init__`` + ``_settle``), and
``_settle`` runs once per execution: the per-round ledger delta is the ledger
state after the round's last execution minus the state after the previous
round's last execution (the construction baseline before the first round).

Role attribution: C5 pins the PRIMARY endpoint to the two aggregate channels
("no per-actor or per-side series in the primary endpoint").  The emitter
additionally emits clearly auxiliary attribution series -- aggressor-side
(buy/sell) and payload-role (``aggressor_role``/``maker_role``) partitions of
the same conserving totals, plus per-actor net ledger deltas -- for audit and
diagnostics.  Every attribution is a partition identity checked by
:func:`conservation_violations`.

Integer exactness: every emitted quantity is an ``int`` and every conservation
identity is integer arithmetic; no floats anywhere in this module.  The
DGP-native channel scaling ``s_ch`` of C5 is NOT computed here (it is pinned to
the hash-sealed DGP-only sample branch, outside E-4's scope).

Determinism: a pure function of (prestate, tape).  The only randomness is the
engine's own prestate-seeded RNG, replayed identically; JSON emission is
canonical (sorted keys, compact separators) and byte-stable.  The corpus
consumer surface (:meth:`ConservingChannelSeries.increment_matrix` /
:meth:`ConservingChannelSeries.cumulative_matrix`) pins the channel order to
``CHANNEL_ORDER`` so the lineage corpus tensors (``FactSurrogateBatch.channels``,
build items E-1/L1-1/L2-1) are lineage-invariant.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from lab_asset.matching import ReferenceEngine
from lab_asset.replay import _as_int, _as_str, _clocks, _subdict
from lab_asset.schema import (
    CancelRequest,
    EventType,
    LatencyChoice,
    OrderRequest,
    ReplaceRequest,
    SessionPrestate,
    Side,
    TapeRecord,
    ThreeClocks,
    record_to_json,
)

__all__ = [
    "CHANNEL_ORDER",
    "CONSERVING_SCHEMA_VERSION",
    "ConservingChannelSeries",
    "RoundChannels",
    "conservation_violations",
    "emit_conserving_channels",
    "emit_conserving_channels_json",
    "regenerate_with_engine",
    "settlement_violations",
]

CONSERVING_SCHEMA_VERSION = "lab-asset-v3-conserving-v1"
CHANNEL_ORDER: tuple[str, ...] = ("volume_units", "cash_ticks")

_Ledger = dict[str, dict[str, int]]
# (engine tape length after a request event, ledger state at that boundary)
_Boundary = tuple[int, _Ledger]


# ─────────────────────────────────────────────────────────────────────────────
# Re-execution (the regenerate path, with the engine handle exposed)
# ─────────────────────────────────────────────────────────────────────────────


def _ledger(engine: ReferenceEngine) -> _Ledger:
    return {
        "cash": dict(engine.cash),
        "inventory": dict(engine.inventory),
        "units_bought": dict(engine.units_bought),
        "units_sold": dict(engine.units_sold),
    }


def _assert_replay(engine: ReferenceEngine, tape: list[TapeRecord]) -> None:
    """replay()'s exact comparison semantics (replay.py:157-169), enforced."""

    if len(engine.tape) != len(tape):
        raise ValueError(
            f"conserving emitter replay guard: tape length {len(tape)} != "
            f"regenerated {len(engine.tape)}"
        )
    for regenerated, recorded in zip(engine.tape, tape, strict=True):
        if (
            regenerated.sequence != recorded.sequence
            or regenerated.event_type != recorded.event_type
            or regenerated.pre_state_hash != recorded.pre_state_hash
            or regenerated.post_state_hash != recorded.post_state_hash
            or regenerated.pre_aggregate_state_hash
            != recorded.pre_aggregate_state_hash
            or regenerated.post_aggregate_state_hash
            != recorded.post_aggregate_state_hash
            or record_to_json(regenerated) != record_to_json(recorded)
        ):
            raise ValueError(
                f"conserving emitter replay guard failed at sequence {recorded.sequence}"
            )


def _reexecute(
    prestate: SessionPrestate, tape: list[TapeRecord]
) -> tuple[ReferenceEngine, list[_Boundary]]:
    """Replay the request stream, snapshotting the ledgers at request boundaries.

    Returns the live engine and ``boundaries``: pairs of (engine tape length,
    ledger state) recorded after construction and after each re-executed
    request event.  Because request events are the only engine calls and
    executions only happen inside them, the ledger state "after tape index i"
    is the first boundary whose tape length exceeds i.
    """

    engine = ReferenceEngine(prestate)
    boundaries: list[_Boundary] = [(len(engine.tape), _ledger(engine))]
    for record in tape:
        if record.event_type == EventType.ORDER_REQUEST:
            payload = record.payload
            engine.submit(
                OrderRequest(
                    event_id=_as_int(payload["event_id"]),
                    actor=_as_str(payload["actor"]),
                    client_order_id=_as_str(payload["client_order_id"]),
                    side=Side(_as_str(payload["side"])),
                    price=_as_int(payload["price"]),
                    quantity=_as_int(payload["quantity"]),
                    clocks=_clocks(payload),
                    round_id=_as_int(payload["round_id"]),
                )
            )
        elif record.event_type == EventType.CANCEL_REQUEST:
            payload = record.payload
            engine.cancel(
                CancelRequest(
                    event_id=_as_int(payload["event_id"]),
                    actor=_as_str(payload["actor"]),
                    order_id=_as_str(payload["order_id"]),
                    clocks=_clocks(payload),
                    round_id=_as_int(payload["round_id"]),
                )
            )
        elif record.event_type == EventType.REPLACE_REQUEST:
            payload = record.payload
            engine.replace(
                ReplaceRequest(
                    event_id=_as_int(payload["event_id"]),
                    actor=_as_str(payload["actor"]),
                    replaces_order_id=_as_str(payload["replaces_order_id"]),
                    client_order_id=_as_str(payload["client_order_id"]),
                    side=Side(_as_str(payload["side"])),
                    price=_as_int(payload["price"]),
                    quantity=_as_int(payload["quantity"]),
                    clocks=_clocks(payload),
                    round_id=_as_int(payload["round_id"]),
                )
            )
        elif record.event_type in (
            EventType.LATENCY_CHOICE,
            EventType.LATENCY_CHOICE_REJECTED,
        ):
            payload = record.payload
            engine.choose_latency(
                LatencyChoice(
                    event_id=_as_int(payload["event_id"]),
                    actor=_as_str(payload["actor"]),
                    round_id=_as_int(payload["round_id"]),
                    investment=_as_int(payload["investment"]),
                    clocks=_clocks(payload),
                )
            )
        elif record.event_type == EventType.SESSION_END:
            engine.finish()
        else:
            continue
        boundaries.append((len(engine.tape), _ledger(engine)))
    _assert_replay(engine, tape)
    return engine, boundaries


def _ledger_after(boundaries: list[_Boundary], position: int) -> _Ledger:
    """Ledger state after tape index ``position`` (0-based; -1 = baseline)."""

    for length, ledger in boundaries:
        if length > position:
            return ledger
    return boundaries[-1][1]


def regenerate_with_engine(
    prestate: SessionPrestate, tape: list[TapeRecord]
) -> tuple[ReferenceEngine, list[TapeRecord]]:
    """Regenerate a tape exactly as ``lab_asset.replay.regenerate`` would, but
    return the live engine (whose ``.cash``/``.inventory`` hold the regenerated
    engine state) alongside the regenerated tape.  Byte-exact agreement with the
    recorded tape is enforced (``replay`` comparison semantics)."""

    engine, _ = _reexecute(prestate, tape)
    return engine, engine.tape


# ─────────────────────────────────────────────────────────────────────────────
# Round grid (E-1's corpus grammar: execution match ticks, ascending)
# ─────────────────────────────────────────────────────────────────────────────


def _execution_match_ts(record: TapeRecord) -> int:
    execution = _subdict(record.payload, "execution")
    clocks: dict[str, object] | ThreeClocks = execution["clocks"]  # type: ignore[assignment]
    # engine-live tapes nest the ThreeClocks dataclass; fixture tapes loaded
    # from disk carry the same data as a plain dict
    match_ts = clocks["match_ts"] if isinstance(clocks, dict) else clocks.match_ts
    return _as_int(match_ts)


def _execution_rounds(tape: list[TapeRecord]) -> dict[int, list[int]]:
    """match_ts -> tape indices of that round's execution records, ascending.

    The engine validates ``match_ts >= last_match_ts`` and advances
    ``last_match_ts`` per request, so execution ticks are nondecreasing in tape
    order and first appearance equals ascending tick order; keys are sorted
    anyway so the grid is deterministic even for hand-built inputs.
    """

    grouped: dict[int, list[int]] = {}
    for index, record in enumerate(tape):
        if record.event_type != EventType.EXECUTION:
            continue
        grouped.setdefault(_execution_match_ts(record), []).append(index)
    return {tick: indices for tick in sorted(grouped) for indices in [grouped[tick]]}


def _delta(after: dict[str, int], before: dict[str, int]) -> dict[str, int]:
    return {actor: after[actor] - before[actor] for actor in after}


# ─────────────────────────────────────────────────────────────────────────────
# Emitted series
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RoundChannels:
    """One clearing round of conserving-channel data (all values integer).

    ``volume_units``/``cash_ticks`` are the two C5 primary channels (aggregate
    executed totals).  ``buy_*``/``sell_*`` and the role/partition dicts are
    auxiliary attributions of the same totals; ``actor_*_delta`` are the
    engine-state net ledger deltas over the round (auxiliary, not endpoint
    series).  ``cumulative_*`` are the ABS-state channels after the round; the
    per-round values are the INC-coordinate increments.  ``match_ts`` is the
    round grid key (E-1's corpus grammar); ``round_ids`` is client metadata.
    """

    match_ts: int
    round_ids: tuple[int, ...]
    first_sequence: int
    last_sequence: int
    n_executions: int
    volume_units: int
    cash_ticks: int
    cumulative_volume_units: int
    cumulative_cash_ticks: int
    buy_volume_units: int
    buy_cash_ticks: int
    sell_volume_units: int
    sell_cash_ticks: int
    aggressor_role_volume: dict[str, int]
    aggressor_role_cash: dict[str, int]
    maker_role_volume: dict[str, int]
    maker_role_cash: dict[str, int]
    actor_cash_delta: dict[str, int]
    actor_inventory_delta: dict[str, int]
    actor_units_bought_delta: dict[str, int]
    actor_units_sold_delta: dict[str, int]
    post_total_cash: int
    post_total_inventory: int

    def to_payload(self) -> dict[str, object]:
        return {
            "match_ts": self.match_ts,
            "round_ids": list(self.round_ids),
            "first_sequence": self.first_sequence,
            "last_sequence": self.last_sequence,
            "n_executions": self.n_executions,
            "volume_units": self.volume_units,
            "cash_ticks": self.cash_ticks,
            "cumulative_volume_units": self.cumulative_volume_units,
            "cumulative_cash_ticks": self.cumulative_cash_ticks,
            "buy_volume_units": self.buy_volume_units,
            "buy_cash_ticks": self.buy_cash_ticks,
            "sell_volume_units": self.sell_volume_units,
            "sell_cash_ticks": self.sell_cash_ticks,
            "aggressor_role_volume": self.aggressor_role_volume,
            "aggressor_role_cash": self.aggressor_role_cash,
            "maker_role_volume": self.maker_role_volume,
            "maker_role_cash": self.maker_role_cash,
            "actor_cash_delta": self.actor_cash_delta,
            "actor_inventory_delta": self.actor_inventory_delta,
            "actor_units_bought_delta": self.actor_units_bought_delta,
            "actor_units_sold_delta": self.actor_units_sold_delta,
            "post_total_cash": self.post_total_cash,
            "post_total_inventory": self.post_total_inventory,
        }


@dataclass(frozen=True)
class ConservingChannelSeries:
    """The full per-round conserving-channel series of one session."""

    session_id: str
    allocation_rule: str
    rounds: tuple[RoundChannels, ...]
    initial_total_cash: int
    initial_total_inventory: int

    @property
    def n_rounds(self) -> int:
        return len(self.rounds)

    def increment_matrix(self) -> list[list[int]]:
        """Per-round increments in pinned channel order ``CHANNEL_ORDER``.

        The INC-coordinate target and the C5 error channels; row-aligned with
        the F_exec projector's ``channels_delta`` (build item E-1) and
        consumable directly by the lineage corpus adapters (L1-1/L2-1)."""

        return [[round_.volume_units, round_.cash_ticks] for round_ in self.rounds]

    def cumulative_matrix(self) -> list[list[int]]:
        """Post-round ABS-state channels in pinned channel order."""

        return [
            [round_.cumulative_volume_units, round_.cumulative_cash_ticks]
            for round_ in self.rounds
        ]

    def to_payload(self) -> dict[str, object]:
        return {
            "schema_version": CONSERVING_SCHEMA_VERSION,
            "session_id": self.session_id,
            "allocation_rule": self.allocation_rule,
            "channel_order": list(CHANNEL_ORDER),
            "n_rounds": self.n_rounds,
            "initial_total_cash": self.initial_total_cash,
            "initial_total_inventory": self.initial_total_inventory,
            "rounds": [round_.to_payload() for round_ in self.rounds],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_payload(), sort_keys=True, separators=(",", ":"))


def emit_conserving_channels(
    prestate: SessionPrestate, tape: list[TapeRecord]
) -> ConservingChannelSeries:
    """Emit the conserving-channel series of a recorded session.

    Pure function of (prestate, tape): re-executes the request stream (replay
    guard enforced byte-exactly), snapshots the engine ledgers at request
    boundaries and aggregates the conserving channels per clearing round on the
    E-1 corpus round grid (distinct execution match ticks, ascending).  No
    engine or replay-code modification; no RNG beyond the prestate-seeded
    engine's own, replayed identically.
    """

    _, boundaries = _reexecute(prestate, tape)
    rounds: list[RoundChannels] = []
    cumulative_volume = 0
    cumulative_cash = 0
    previous_last_index = -1
    for match_ts, indices in _execution_rounds(tape).items():
        volume = 0
        cash = 0
        buy_volume = 0
        buy_cash = 0
        sell_volume = 0
        sell_cash = 0
        round_ids: set[int] = set()
        aggressor_role_volume: dict[str, int] = {}
        aggressor_role_cash: dict[str, int] = {}
        maker_role_volume: dict[str, int] = {}
        maker_role_cash: dict[str, int] = {}
        for index in indices:
            payload = tape[index].payload
            execution = _subdict(payload, "execution")
            quantity = _as_int(execution["quantity"])
            price = _as_int(execution["price"])
            notional = price * quantity
            side = _as_str(execution["side_of_aggressor"])
            aggressor_role = _as_str(payload["aggressor_role"])
            maker_role = _as_str(payload["maker_role"])
            volume += quantity
            cash += notional
            round_ids.add(_as_int(execution["round_id"]))
            if side == "B":
                buy_volume += quantity
                buy_cash += notional
            elif side == "S":
                sell_volume += quantity
                sell_cash += notional
            else:
                raise ValueError(
                    f"side_of_aggressor must be 'B' or 'S', got {side!r}"
                )
            aggressor_role_volume[aggressor_role] = (
                aggressor_role_volume.get(aggressor_role, 0) + quantity
            )
            aggressor_role_cash[aggressor_role] = (
                aggressor_role_cash.get(aggressor_role, 0) + notional
            )
            maker_role_volume[maker_role] = (
                maker_role_volume.get(maker_role, 0) + quantity
            )
            maker_role_cash[maker_role] = (
                maker_role_cash.get(maker_role, 0) + notional
            )
        # _settle is the only ledger mutator, so the round's ledger delta is
        # exactly the state after its last execution minus the previous round's
        # (or the construction baseline before the first round).
        before = _ledger_after(boundaries, previous_last_index)
        after = _ledger_after(boundaries, indices[-1])
        previous_last_index = indices[-1]
        cumulative_volume += volume
        cumulative_cash += cash
        rounds.append(
            RoundChannels(
                match_ts=match_ts,
                round_ids=tuple(sorted(round_ids)),
                first_sequence=tape[indices[0]].sequence,
                last_sequence=tape[indices[-1]].sequence,
                n_executions=len(indices),
                volume_units=volume,
                cash_ticks=cash,
                cumulative_volume_units=cumulative_volume,
                cumulative_cash_ticks=cumulative_cash,
                buy_volume_units=buy_volume,
                buy_cash_ticks=buy_cash,
                sell_volume_units=sell_volume,
                sell_cash_ticks=sell_cash,
                aggressor_role_volume=aggressor_role_volume,
                aggressor_role_cash=aggressor_role_cash,
                maker_role_volume=maker_role_volume,
                maker_role_cash=maker_role_cash,
                actor_cash_delta=_delta(after["cash"], before["cash"]),
                actor_inventory_delta=_delta(after["inventory"], before["inventory"]),
                actor_units_bought_delta=_delta(
                    after["units_bought"], before["units_bought"]
                ),
                actor_units_sold_delta=_delta(
                    after["units_sold"], before["units_sold"]
                ),
                post_total_cash=sum(after["cash"].values()),
                post_total_inventory=sum(after["inventory"].values()),
            )
        )
    return ConservingChannelSeries(
        session_id=prestate.session_id,
        allocation_rule=prestate.allocation_rule.value,
        rounds=tuple(rounds),
        initial_total_cash=sum(prestate.initial_cash.values()),
        initial_total_inventory=sum(prestate.initial_inventory.values()),
    )


def emit_conserving_channels_json(
    prestate: SessionPrestate, tape: list[TapeRecord]
) -> str:
    """Canonical byte-stable JSON of :func:`emit_conserving_channels`."""

    return emit_conserving_channels(prestate, tape).to_json()


# ─────────────────────────────────────────────────────────────────────────────
# Conservation identities (integer-exact)
# ─────────────────────────────────────────────────────────────────────────────


def conservation_violations(series: ConservingChannelSeries) -> list[str]:
    """Engine-state-internal conservation identities; empty list = all hold.

    Checked per round, integers only: (i) actor cash deltas sum to zero;
    (ii) actor inventory deltas sum to zero; (iii) gross units_bought and
    units_sold deltas each equal the executed volume; (iv) buy/sell and role
    attributions partition the aggregate channels; (v) cumulative channels are
    running sums; (vi) total cash and total inventory are unchanged from the
    prestate at every round boundary.
    """

    violations: list[str] = []
    running_volume = 0
    running_cash = 0
    for round_ in series.rounds:
        rid = round_.match_ts
        if sum(round_.actor_cash_delta.values()) != 0:
            violations.append(f"round {rid}: actor cash deltas do not sum to zero")
        if sum(round_.actor_inventory_delta.values()) != 0:
            violations.append(
                f"round {rid}: actor inventory deltas do not sum to zero"
            )
        if sum(round_.actor_units_bought_delta.values()) != round_.volume_units:
            violations.append(
                f"round {rid}: units_bought delta != executed volume units"
            )
        if sum(round_.actor_units_sold_delta.values()) != round_.volume_units:
            violations.append(
                f"round {rid}: units_sold delta != executed volume units"
            )
        if round_.buy_volume_units + round_.sell_volume_units != round_.volume_units:
            violations.append(
                f"round {rid}: buy+sell volume != aggregate volume units"
            )
        if round_.buy_cash_ticks + round_.sell_cash_ticks != round_.cash_ticks:
            violations.append(f"round {rid}: buy+sell cash != aggregate cash ticks")
        partitions = (
            ("aggressor_role_volume", round_.aggressor_role_volume, round_.volume_units),
            ("aggressor_role_cash", round_.aggressor_role_cash, round_.cash_ticks),
            ("maker_role_volume", round_.maker_role_volume, round_.volume_units),
            ("maker_role_cash", round_.maker_role_cash, round_.cash_ticks),
        )
        for label, mapping, total in partitions:
            if sum(mapping.values()) != total:
                violations.append(f"round {rid}: {label} does not partition the total")
        running_volume += round_.volume_units
        running_cash += round_.cash_ticks
        if (
            round_.cumulative_volume_units != running_volume
            or round_.cumulative_cash_ticks != running_cash
        ):
            violations.append(f"round {rid}: cumulative channels != running sums")
        if round_.post_total_cash != series.initial_total_cash:
            violations.append(
                f"round {rid}: total cash {round_.post_total_cash} != initial "
                f"{series.initial_total_cash}"
            )
        if round_.post_total_inventory != series.initial_total_inventory:
            violations.append(
                f"round {rid}: total inventory {round_.post_total_inventory} != "
                f"initial {series.initial_total_inventory}"
            )
    return violations


def settlement_violations(
    prestate: SessionPrestate, tape: list[TapeRecord], series: ConservingChannelSeries
) -> list[str]:
    """Cross-check the emitted engine-state series against the tape payloads.

    Recomputes, per round and per actor, the net cash/inventory deltas implied
    by the execution payloads (buyer/seller resolved exactly as the engine's
    ``_settle`` does, from ``side_of_aggressor``) and compares them with the
    emitted engine-state deltas; also compares the aggregate channels and
    execution counts.  Empty list = tape and regenerated engine state agree
    exactly (integer arithmetic).
    """

    by_round = {round_.match_ts: round_ for round_ in series.rounds}
    violations: list[str] = []
    for match_ts, indices in _execution_rounds(tape).items():
        round_ = by_round.get(match_ts)
        if round_ is None:
            violations.append(f"round {match_ts}: in tape but missing from series")
            continue
        expected_cash = {actor: 0 for actor in prestate.actors}
        expected_inventory = {actor: 0 for actor in prestate.actors}
        volume = 0
        cash_ticks = 0
        for index in indices:
            execution = _subdict(tape[index].payload, "execution")
            quantity = _as_int(execution["quantity"])
            price = _as_int(execution["price"])
            side = _as_str(execution["side_of_aggressor"])
            aggressor = _as_str(execution["aggressor_actor"])
            maker = _as_str(execution["maker_actor"])
            buyer, seller = (aggressor, maker) if side == "B" else (maker, aggressor)
            notional = price * quantity
            expected_cash[buyer] -= notional
            expected_cash[seller] += notional
            expected_inventory[buyer] += quantity
            expected_inventory[seller] -= quantity
            volume += quantity
            cash_ticks += notional
        if expected_cash != round_.actor_cash_delta:
            violations.append(
                f"round {match_ts}: payload-settlement cash deltas != engine-state deltas"
            )
        if expected_inventory != round_.actor_inventory_delta:
            violations.append(
                f"round {match_ts}: payload-settlement inventory deltas != "
                "engine-state deltas"
            )
        if volume != round_.volume_units or cash_ticks != round_.cash_ticks:
            violations.append(
                f"round {match_ts}: payload aggregates != emitted channels"
            )
        if len(indices) != round_.n_executions:
            violations.append(
                f"round {match_ts}: payload execution count != emitted count"
            )
    return violations
