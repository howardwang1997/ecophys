"""Dual-hash-validated fiber resampler (PI decision D1_02; KT-A3/KT-M1 instrument).

Given a ``random_unit_within_price`` episode (prestate + tape) whose rationed
touched level holds a multi-order pool, regenerate alternative without-replacement
unit-to-order draw assignments holding the AGGREGATE tape fixed (same executed
prices/volumes per level, same aggregate statistics).

Acceptance — the dual-hash contract, reusing the frozen hash semantics of
``lab_asset.schema`` verbatim: a resample is accepted iff

  (i)  the ``aggregate_state_hash`` sequence over the episode is IDENTICAL to the
       original (positional equality of event types and pre/post aggregate
       hashes), and
  (ii) the ``state_hash`` chain DIFFERS (at least one positional difference in
       pre/post full-state hashes).

Route taken (and why). The engine has no pinned-draw replay hook: searched
``replay.py``/``matching.py`` — ``replay.regenerate`` constructs
``ReferenceEngine(prestate)`` whose ``rng = random.Random(prestate.seed)``, and
that rng is consumed only by random-unit ``_select_maker`` (three touch sites:
seed, ``getstate`` inside ``state_hash``, ``randrange`` at the draw). Rather than
re-implementing the engine's identity-state bookkeeping at the tape level (which
would duplicate queue/settlement/status semantics and risk diverging from the
frozen hash contract), the resampler replays the recorded request stream through
the UNMODIFIED ``ReferenceEngine`` with only the draw source swapped after
construction. Every state transition, settlement, record and both hash chains
are therefore computed by the engine itself (engine-native hashes); the original
prestate and request stream are held byte-fixed and the draw realization is the
only input that varies. ``replay_loop_matches_validator`` re-establishes that
this module's replay loop is byte-equivalent to ``lab_asset.replay.regenerate``
on every episode it is applied to, and ``resample_pinned`` with the recorded
draw values reproduces an episode byte-exactly (the injection-point ground
truth).

One semantic refinement is load-bearing. ``state_hash`` embeds
``rng.getstate()``, so naively swapping the draw source flips that component
even when no allocation differs: a fifo episode consumes no draws at all and a
single-order pool maps every unit draw to the same maker, yet both would show
"differing state_hash chains" — rng-state-only pairs that would masquerade as
within-fiber pairs and trivialize the KT-A3 control. The resampler therefore
injects draws through ``NativeStatePreservingDrawSource``: each regenerated
``randrange(eligible)`` also consumes and discards the identical call on a fresh
``random.Random(prestate.seed)``, so the hashed RNG trajectory is exactly the
engine-native one (the eligible-unit sequence is aggregate-invariant across
resamples). Under this contract state-chain equality coincides with
allocation-trajectory equality: fifo and single-order pools admit NO accepted
resample (their draw fiber is a point, as the theory requires), and on
multi-order pools an attempt is accepted unless it reproduces the original
realized allocation trajectory — the acceptance rate is therefore
``1 - P_engine(original realized allocation trajectory)``, an interpretable,
law-level quantity reported per fixture.

The count law of resampled allocations is the engine's own draw law: each draw
is uniform over the remaining units of the touched level, so per-order
allocation counts are multivariate hypergeometric MVHG(q_P, V*) — verified
exactly (``sequential_draw_law`` state DP == ``mvhg_pmf`` closed form), through
the engine (``enumerate_engine_count_law`` pinned-draw enumeration on the small
V* rungs), and by seeded Monte-Carlo chi-square on the larger pools. Count-law
conformance is evaluated over ALL attempts (each an iid engine-law realization);
dual-hash acceptance is a separate, reported verdict.

What the instrument certifies (preregistration statement, frozen text):

  ``PREREG_STATEMENT`` — the fiber resampler certifies aggregate-law invariance
  plus state-law variation: every accepted resample holds the aggregate tape
  (aggregate_state_hash sequence and aggregate statistics) byte-fixed while the
  identity-layer allocation state varies over the engine's without-replacement
  draw fiber, with native RNG-state accounting making state-chain equality
  coincide with allocation-trajectory equality, so deterministic kernels and
  single-order pools admit no accepted resample; this is the machine-checkable
  within-fiber (gauge-twin) relation of KT-A3/KT-M1, and no accepted resample
  exists outside it.
"""

from __future__ import annotations

import json
import math
import random
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from scipy.stats import chi2 as _scipy_chi2

from lab_asset.matching import ReferenceEngine
from lab_asset.replay import regenerate
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
    prestate_from_json,
    record_to_json,
    stable_hash,
)

__all__ = [
    "PREREG_STATEMENT",
    "ChiSquareResult",
    "DualHashReport",
    "Episode",
    "NativeStatePreservingDrawSource",
    "PinnedDrawSource",
    "ResampledEpisode",
    "ResampleSummary",
    "aggregate_projection",
    "aggregate_tape_lines",
    "allocation_counts",
    "bounded_compositions",
    "chi_square_gof",
    "draw_seed_stream",
    "dual_hash_report",
    "enumerate_engine_count_law",
    "feasible_order_sequences",
    "first_execution_identity_divergence",
    "load_episode",
    "mvhg_pmf",
    "order_sequence_probability",
    "pinned_units_for_order_sequence",
    "pool_orders_at_price",
    "replay_loop_matches_validator",
    "resample",
    "resample_many",
    "resample_pinned",
    "sequential_draw_law",
    "state_chain_digest",
    "summarize",
]

# First integer after the enrichment master seed 20260972; disjoint from the
# frozen training seed namespaces 11000-11029 / 12000-12029 (PI decision D1_10)
# and from the enrichment seed search space.
FIBER_RESAMPLER_SEED_NAMESPACE: int = 20260973

PREREG_STATEMENT: str = (
    "The fiber resampler certifies aggregate-law invariance plus state-law "
    "variation: every accepted resample holds the aggregate tape "
    "(aggregate_state_hash sequence and aggregate statistics) byte-fixed while "
    "the identity-layer allocation state varies over the engine's "
    "without-replacement draw fiber, with native RNG-state accounting making "
    "state-chain equality coincide with allocation-trajectory equality, so "
    "deterministic kernels and single-order pools admit no accepted resample; "
    "this is the machine-checkable within-fiber (gauge-twin) relation of "
    "KT-A3/KT-M1, and no accepted resample exists outside it."
)


# --------------------------------------------------------------------- episodes
@dataclass(frozen=True)
class Episode:
    """A fixture episode: frozen prestate plus its recorded tape."""

    name: str
    prestate: SessionPrestate
    tape: tuple[TapeRecord, ...]


def _parse_tape_record(raw: str) -> TapeRecord:
    data = json.loads(raw)
    return TapeRecord(
        sequence=data["sequence"],
        event_type=EventType(data["event_type"]),
        payload=data["payload"],
        pre_state_hash=data["pre_state_hash"],
        post_state_hash=data["post_state_hash"],
        pre_aggregate_state_hash=data["pre_aggregate_state_hash"],
        post_aggregate_state_hash=data["post_aggregate_state_hash"],
    )


def load_episode(fixture_dir: Path, name: str = "") -> Episode:
    """Load a prestate/tape pair from a fixture directory (read-only)."""

    fixture_dir = Path(fixture_dir)
    prestate = prestate_from_json((fixture_dir / "prestate.json").read_text())
    tape = tuple(
        _parse_tape_record(line)
        for line in (fixture_dir / "tape.jsonl").read_text().splitlines()
        if line.strip()
    )
    return Episode(name=name or fixture_dir.name, prestate=prestate, tape=tape)


# ------------------------------------------------------------------ draw source
class PinnedDrawSource:
    """Deterministic draw source replaying a pinned sequence of unit draws.

    Mirrors the rng operation the engine performs for a draw (``randrange``).
    """

    def __init__(self, selected_units: Sequence[int], label: str) -> None:
        self._values = list(selected_units)
        self._label = label
        self._position = 0

    def randrange(self, upper: int) -> int:
        if self._position >= len(self._values):
            raise ValueError(
                f"pinned draw source '{self._label}' exhausted at draw "
                f"{self._position}; {len(self._values)} values were pinned"
            )
        value = self._values[self._position]
        if not 0 <= value < upper:
            raise ValueError(
                f"pinned draw {self._position} (= {value}) outside the engine's "
                f"eligible range [0, {upper})"
            )
        self._position += 1
        return value


class NativeStatePreservingDrawSource:
    """Regenerated draws with engine-native RNG-state accounting.

    The engine hashes ``rng.getstate()`` into every ``state_hash``. Swapping the
    draw source naively would flip that component even when no allocation
    differs (fifo consumes no draws; a single-order pool maps every unit draw to
    the same maker), admitting trivial rng-state-only pairs as "within-fiber".
    This wrapper instead answers each ``randrange(eligible)`` from the
    alternative source while consuming and discarding the identical call on a
    fresh ``random.Random(prestate.seed)``: the eligible-unit sequence is
    aggregate-invariant across resamples, so the hashed RNG trajectory is
    exactly the engine-native one, and state-chain equality coincides with
    allocation-trajectory equality.
    """

    def __init__(self, draws: object, native_seed: int) -> None:
        self._draws = draws
        self._native = random.Random(native_seed)

    def randrange(self, upper: int) -> int:
        self._native.randrange(upper)  # keep the engine-native hashed trajectory
        result = self._draws.randrange(upper)  # type: ignore[attr-defined]
        assert isinstance(result, int)
        return result

    def getstate(self) -> object:
        return self._native.getstate()


# ------------------------------------------------------- request-stream replay
def _payload(record: TapeRecord) -> dict[str, object]:
    payload = record.payload
    assert isinstance(payload, dict)
    return payload


def _sub(payload: dict[str, object], key: str) -> dict[str, object]:
    value = payload[key]
    assert isinstance(value, dict)
    return value


def _as_int(value: object) -> int:
    assert isinstance(value, int)
    return value


def _as_str(value: object) -> str:
    assert isinstance(value, str)
    return value


def _clocks(payload: dict[str, object]) -> ThreeClocks:
    raw = _sub(payload, "clocks")
    return ThreeClocks(
        client_ts=_as_int(raw["client_ts"]),
        receipt_ts=_as_int(raw["receipt_ts"]),
        match_ts=_as_int(raw["match_ts"]),
    )


def _replay_with_draw_source(
    prestate: SessionPrestate,
    tape: Sequence[TapeRecord],
    draw_source: object | None,
) -> list[TapeRecord]:
    """Re-execute the recorded request stream; optionally swap the draw source.

    Mirrors ``lab_asset.replay.regenerate`` dispatch exactly (established by
    ``replay_loop_matches_validator``); the only difference is that after
    construction, and before any request is processed, the engine's draw source
    (``engine.rng``) is replaced. All state transitions, settlements, records
    and hashes remain engine code paths.
    """

    engine = ReferenceEngine(prestate)
    if draw_source is not None:
        engine.rng = draw_source
    for record in tape:
        payload = _payload(record)
        if record.event_type == EventType.ORDER_REQUEST:
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
    return engine.tape


def replay_loop_matches_validator(
    prestate: SessionPrestate, tape: Sequence[TapeRecord]
) -> bool:
    """This module's un-injected replay loop is byte-equivalent to regenerate()."""

    own = [record_to_json(r) for r in _replay_with_draw_source(prestate, tape, None)]
    canonical = [record_to_json(r) for r in regenerate(prestate, list(tape))]
    return own == canonical


# ---------------------------------------------------------- dual-hash acceptance
@dataclass(frozen=True)
class DualHashReport:
    """Outcome of the dual-hash acceptance contract on one candidate resample."""

    same_length: bool
    aggregate_identical: bool
    state_chain_differs: bool
    accepted: bool
    first_aggregate_mismatch: int | None
    first_state_divergence: int | None

    def __str__(self) -> str:
        return (
            f"accepted={self.accepted} "
            f"(aggregate_identical={self.aggregate_identical}, "
            f"state_chain_differs={self.state_chain_differs}, "
            f"first_aggregate_mismatch={self.first_aggregate_mismatch}, "
            f"first_state_divergence={self.first_state_divergence})"
        )


def dual_hash_report(
    original: Sequence[TapeRecord], resampled: Sequence[TapeRecord]
) -> DualHashReport:
    """Criterion (i) identical aggregate_state_hash sequence, (ii) differing state_hash chain.

    Comparison is positional record-by-record (the binding engine contract is
    replay equality at matching sequences; per-record hash-chain continuity
    breaks at composite request->outcome boundaries in every engine tape).
    Event types are included in criterion (i) so that a resample whose request
    tape diverges (e.g. a draw-mediated rejection) can never count as
    aggregate-fixed even where hash values coincide.
    """

    same_length = len(original) == len(resampled)
    first_aggregate_mismatch: int | None = None
    first_state_divergence: int | None = None
    for source, candidate in zip(original, resampled, strict=False):
        if first_aggregate_mismatch is None and (
            source.event_type != candidate.event_type
            or source.pre_aggregate_state_hash != candidate.pre_aggregate_state_hash
            or source.post_aggregate_state_hash != candidate.post_aggregate_state_hash
        ):
            first_aggregate_mismatch = source.sequence
        if first_state_divergence is None and (
            source.pre_state_hash != candidate.pre_state_hash
            or source.post_state_hash != candidate.post_state_hash
        ):
            first_state_divergence = source.sequence
        if first_aggregate_mismatch is not None and first_state_divergence is not None:
            break
    if not same_length and first_aggregate_mismatch is None:
        first_aggregate_mismatch = original[-1].sequence + 1 if original else 0
    aggregate_identical = same_length and first_aggregate_mismatch is None
    state_chain_differs = first_state_divergence is not None or not same_length
    return DualHashReport(
        same_length=same_length,
        aggregate_identical=aggregate_identical,
        state_chain_differs=state_chain_differs,
        accepted=aggregate_identical and state_chain_differs,
        first_aggregate_mismatch=first_aggregate_mismatch,
        first_state_divergence=first_state_divergence,
    )


# --------------------------------------------------------- aggregate projection
_EXECUTION_IDENTITY_KEYS = frozenset(
    {"maker_order_id", "maker_actor", "maker_remaining"}
)
_DRAW_IDENTITY_KEYS = frozenset({"maker_order_id", "selected_unit"})


def aggregate_projection(record: TapeRecord) -> dict[str, object]:
    """Identity-stripped record: the aggregate-tape view of one event.

    Removes per-record state hashes and every draw-/maker-identity payload field
    (maker order id, maker actor, maker remaining, maker role, the drawn
    selected_unit and drawn maker id), keeping everything the aggregate tape
    commits to: sequence, event type, aggregate hashes, execution
    price/quantity/aggressor fields, execution ids, quote fields, clocks, and
    the aggregate-visible ``allocation_draw`` fields (price, eligible_units).
    """

    # Canonicalize through the frozen serializer: engine-generated payloads hold
    # dataclass objects (e.g. ThreeClocks) that only asdict/record_to_json render.
    canonical = json.loads(record_to_json(record))
    payload: dict[str, object] = canonical["payload"]
    if record.event_type == EventType.EXECUTION:
        execution = {
            key: value
            for key, value in _sub(payload, "execution").items()
            if key not in _EXECUTION_IDENTITY_KEYS
        }
        payload["execution"] = execution
        payload.pop("maker_role", None)
        draw = payload.get("allocation_draw")
        if isinstance(draw, dict):
            payload["allocation_draw"] = {
                key: value
                for key, value in draw.items()
                if key not in _DRAW_IDENTITY_KEYS
            }
    return {
        "sequence": record.sequence,
        "event_type": record.event_type.value,
        "payload": payload,
        "pre_aggregate_state_hash": record.pre_aggregate_state_hash,
        "post_aggregate_state_hash": record.post_aggregate_state_hash,
    }


def aggregate_tape_lines(tape: Sequence[TapeRecord]) -> list[str]:
    """Canonical byte view of the aggregate tape (aggregate-projection lines)."""

    return [
        json.dumps(aggregate_projection(r), sort_keys=True, separators=(",", ":"))
        for r in tape
    ]


def first_execution_identity_divergence(
    original: Sequence[TapeRecord], resampled: Sequence[TapeRecord]
) -> int | None:
    """First sequence whose execution MAKER identity differs.

    Maker identity keys only (drawn maker order id, maker actor, maker
    remaining, and the draw annotation's maker id). ``selected_unit`` is an
    exchangeable within-order unit label (P5a), not order identity, so
    divergence there does not count here.
    """

    maker_keys = sorted(_EXECUTION_IDENTITY_KEYS | {"allocation_draw.maker_order_id"})
    for source, candidate in zip(original, resampled, strict=False):
        if source.event_type != EventType.EXECUTION:
            continue
        source_payload, candidate_payload = _payload(source), _payload(candidate)
        source_exec = _sub(source_payload, "execution")
        candidate_exec = _sub(candidate_payload, "execution")
        source_draw = source_payload.get("allocation_draw")
        candidate_draw = candidate_payload.get("allocation_draw")
        for key in maker_keys:
            if key.startswith("allocation_draw."):
                inner = key.split(".", 1)[1]
                left = source_draw.get(inner) if isinstance(source_draw, dict) else None
                right = (
                    candidate_draw.get(inner)
                    if isinstance(candidate_draw, dict)
                    else None
                )
            else:
                left, right = source_exec.get(key), candidate_exec.get(key)
            if left != right:
                return source.sequence
    return None


# ------------------------------------------------------------------- resampling
def draw_seed_stream(base_seed: int, count: int) -> list[int]:
    """Deterministic stream of independent draw seeds from one base seed."""

    parent = random.Random(base_seed)
    return [parent.randrange(2**63) for _ in range(count)]


def state_chain_digest(tape: Sequence[TapeRecord]) -> str:
    """Stable digest of the full state-hash chain (chain identity key)."""

    return stable_hash(
        [[r.sequence, r.pre_state_hash, r.post_state_hash] for r in tape]
    )


@dataclass(frozen=True)
class ResampledEpisode:
    """One candidate resample with its dual-hash verdict."""

    origin: str
    tape: tuple[TapeRecord, ...]
    report: DualHashReport
    chain_digest: str


def resample(
    prestate: SessionPrestate, tape: Sequence[TapeRecord], draw_seed: int
) -> ResampledEpisode:
    """Regenerate the episode under one fresh draw seed (engine-driven)."""

    source = NativeStatePreservingDrawSource(random.Random(draw_seed), prestate.seed)
    resampled = _replay_with_draw_source(prestate, tape, source)
    return ResampledEpisode(
        origin=f"seed:{draw_seed}",
        tape=tuple(resampled),
        report=dual_hash_report(tape, resampled),
        chain_digest=state_chain_digest(resampled),
    )


def resample_pinned(
    prestate: SessionPrestate,
    tape: Sequence[TapeRecord],
    selected_units: Sequence[int],
    label: str,
) -> ResampledEpisode:
    """Regenerate the episode under one pinned sequence of unit draws.

    Pinning the recorded draw values of an episode must reproduce its tape
    byte-exactly (native-state preservation makes the hashes agree too) — the
    ground-truth check that the injection point is exactly the draw source.
    """

    source = NativeStatePreservingDrawSource(
        PinnedDrawSource(selected_units, label), prestate.seed
    )
    resampled = _replay_with_draw_source(prestate, tape, source)
    return ResampledEpisode(
        origin=f"pinned:{label}",
        tape=tuple(resampled),
        report=dual_hash_report(tape, resampled),
        chain_digest=state_chain_digest(resampled),
    )


def resample_many(
    prestate: SessionPrestate,
    tape: Sequence[TapeRecord],
    base_seed: int,
    count: int,
) -> list[ResampledEpisode]:
    """Seeded stream of ``count`` candidate resamples (pure, deterministic)."""

    return [
        resample(prestate, tape, seed)
        for seed in draw_seed_stream(base_seed, count)
    ]


@dataclass(frozen=True)
class ResampleSummary:
    """Acceptance bookkeeping for one resample stream."""

    attempts: int
    accepted: int
    acceptance_rate: float
    distinct_accepted_chains: int

    def __str__(self) -> str:
        return (
            f"{self.accepted}/{self.attempts} accepted "
            f"(rate {self.acceptance_rate:.4f}), "
            f"{self.distinct_accepted_chains} distinct accepted chains"
        )


def summarize(outcomes: Sequence[ResampledEpisode]) -> ResampleSummary:
    accepted = [outcome for outcome in outcomes if outcome.report.accepted]
    return ResampleSummary(
        attempts=len(outcomes),
        accepted=len(accepted),
        acceptance_rate=(len(accepted) / len(outcomes)) if outcomes else 0.0,
        distinct_accepted_chains=len({o.chain_digest for o in accepted}),
    )


def allocation_counts(
    tape: Sequence[TapeRecord], price: int | None = None
) -> dict[int, dict[str, int]]:
    """Per-price maker draw counts (units allocated per maker order id)."""

    counts: dict[int, dict[str, int]] = {}
    for record in tape:
        if record.event_type != EventType.EXECUTION:
            continue
        execution = _sub(_payload(record), "execution")
        level = _as_int(execution["price"])
        if price is not None and level != price:
            continue
        maker = _as_str(execution["maker_order_id"])
        counts.setdefault(level, {})
        counts[level][maker] = counts[level].get(maker, 0) + _as_int(
            execution["quantity"]
        )
    return counts


def pool_orders_at_price(prestate: SessionPrestate, price: int) -> list[str]:
    """Maker order ids resting at ``price`` in the prestate, arrival order."""

    return [
        order.order_id
        for order in prestate.initial_book
        if order.price == price and order.side == Side.ASK
    ]


# ------------------------------------------------------------ exact draw laws
def bounded_compositions(total: int, caps: Sequence[int]) -> Iterator[tuple[int, ...]]:
    """All integer vectors c with sum(c) == total and 0 <= c_i <= caps_i."""

    def walk(index: int, remaining: int, prefix: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
        if index == len(caps) - 1:
            if 0 <= remaining <= caps[index]:
                yield prefix + (remaining,)
            return
        for take in range(min(remaining, caps[index]) + 1):
            yield from walk(index + 1, remaining - take, prefix + (take,))

    yield from walk(0, total, ())


def mvhg_pmf(pool: Sequence[int], draws: int) -> dict[tuple[int, ...], float]:
    """Closed-form multivariate hypergeometric pmf over allocation count vectors."""

    denominator = math.comb(sum(pool), draws)
    if denominator == 0:
        raise ValueError("empty support: draws exceed the pool")
    law: dict[tuple[int, ...], float] = {}
    for counts in bounded_compositions(draws, pool):
        numerator = 1.0
        for quantity, filled in zip(pool, counts):
            numerator *= math.comb(quantity, filled)
        law[counts] = numerator / denominator
    return law


def sequential_draw_law(
    pool: Sequence[int], draws: int
) -> dict[tuple[int, ...], float]:
    """Exact law of allocation counts under the engine's sequential draw rule.

    Dynamic program over remaining-quantity states of the engine law (each draw
    picks order i with probability remaining_i / total_remaining; uniform over
    remaining units aggregated by order). The remaining vector pins the count
    vector, so state identity is count identity.
    """

    remaining_by_state: dict[tuple[int, ...], float] = {tuple(pool): 1.0}
    for _ in range(draws):
        advanced: dict[tuple[int, ...], float] = {}
        for state, mass in remaining_by_state.items():
            total = sum(state)
            for index, quantity in enumerate(state):
                if quantity <= 0:
                    continue
                child = state[:index] + (quantity - 1,) + state[index + 1 :]
                advanced[child] = advanced.get(child, 0.0) + mass * quantity / total
        remaining_by_state = advanced
    return {
        tuple(q - r for q, r in zip(pool, state)): mass
        for state, mass in remaining_by_state.items()
    }


# ------------------------------------------------------- pinned engine driving
def pinned_units_for_order_sequence(
    pool: Sequence[int], order_sequence: Sequence[int]
) -> list[int]:
    """Selected-unit values realizing an order-choice sequence at one pool level.

    The engine maps ``selected_unit`` onto the cumulative ranges of remaining
    quantities in live queue order; the first unit of the target order's range
    deterministically selects it.
    """

    remaining = list(pool)
    pinned: list[int] = []
    for target in order_sequence:
        cumulative = sum(remaining[:target])
        if remaining[target] <= 0:
            raise ValueError(f"order {target} has no remaining unit to draw")
        pinned.append(cumulative)
        remaining[target] -= 1
    return pinned


def feasible_order_sequences(
    pool: Sequence[int], draws: int
) -> Iterator[tuple[int, ...]]:
    """Every order-choice sequence with positive probability under the draw law."""

    def walk(remaining: list[int], prefix: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
        if len(prefix) == draws:
            yield prefix
            return
        for index in range(len(pool)):
            if remaining[index] > 0:
                remaining[index] -= 1
                yield from walk(remaining, prefix + (index,))
                remaining[index] += 1

    yield from walk(list(pool), ())


def order_sequence_probability(
    pool: Sequence[int], order_sequence: Sequence[int]
) -> float:
    """Path probability of one order-choice sequence under the engine draw law."""

    remaining = list(pool)
    probability = 1.0
    for target in order_sequence:
        probability *= remaining[target] / sum(remaining)
        remaining[target] -= 1
    return probability


def enumerate_engine_count_law(
    prestate: SessionPrestate,
    tape: Sequence[TapeRecord],
    pool_price: int,
    draws: int,
) -> tuple[dict[tuple[int, ...], float], list[DualHashReport]]:
    """Engine-driven exact enumeration of the count law at one touched level.

    Realizes every feasible order-choice sequence at ``pool_price`` through the
    engine via ``PinnedDrawSource`` (single-order levels before the pool are
    pinned to unit 0 — any in-range value selects their unique maker), weights
    each realized count vector by its exact path probability, and returns the
    induced law together with every replay's dual-hash report. The engine's own
    selected_unit -> maker mapping is thereby tied to the sequential law.
    """

    order_ids = pool_orders_at_price(prestate, pool_price)
    pool = [
        order.quantity
        for order in prestate.initial_book
        if order.price == pool_price and order.side == Side.ASK
    ]
    law: dict[tuple[int, ...], float] = {}
    reports: list[DualHashReport] = []
    for sequence in feasible_order_sequences(pool, draws):
        pool_pins = pinned_units_for_order_sequence(pool, sequence)
        pinned: list[int] = []
        cursor = 0
        for record in tape:
            if record.event_type != EventType.EXECUTION:
                continue
            execution = _sub(_payload(record), "execution")
            if _as_int(execution["price"]) == pool_price:
                pinned.append(pool_pins[cursor])
                cursor += 1
            else:
                pinned.append(0)
        assert cursor == draws
        label = f"enum-{'-'.join(map(str, sequence))}"
        source = NativeStatePreservingDrawSource(
            PinnedDrawSource(pinned, label), prestate.seed
        )
        resampled = _replay_with_draw_source(prestate, tape, source)
        reports.append(dual_hash_report(tape, resampled))
        realized = allocation_counts(resampled, pool_price)[pool_price]
        counts = tuple(realized.get(order_id, 0) for order_id in order_ids)
        law[counts] = law.get(counts, 0.0) + order_sequence_probability(pool, sequence)
    return law, reports


# ------------------------------------------------------------ chi-square GOF
@dataclass(frozen=True)
class ChiSquareResult:
    """Pearson chi-square goodness-of-fit against an exact pmf."""

    statistic: float
    dof: int
    pvalue: float
    cells: int
    tail_pooled: bool

    def __str__(self) -> str:
        return (
            f"chi2={self.statistic:.3f} dof={self.dof} "
            f"p={self.pvalue:.5f} cells={self.cells} tail_pooled={self.tail_pooled}"
        )


def chi_square_gof(
    observed: Mapping[tuple[int, ...], int],
    pmf: Mapping[tuple[int, ...], float],
    min_expected: float = 5.0,
) -> ChiSquareResult:
    """Chi-square GOF of observed counts against an exact pmf.

    Cells with expected count below ``min_expected`` are pooled into a single
    tail cell (both expected and observed); the tail is dropped when it carries
    no expected and no observed mass.
    """

    n = sum(observed.values())
    if n == 0:
        raise ValueError("no observations")
    kept = {
        key: n * probability
        for key, probability in pmf.items()
        if n * probability >= min_expected
    }
    tail_expected = n * sum(
        probability for key, probability in pmf.items() if key not in kept
    )
    tail_observed = sum(
        count for key, count in observed.items() if key not in kept
    )
    statistic = sum(
        (observed.get(key, 0) - expected) ** 2 / expected
        for key, expected in kept.items()
    )
    cells = len(kept)
    tail_pooled = tail_expected > 0 or tail_observed > 0
    if tail_pooled:
        if tail_expected <= 0:
            raise ValueError("observed mass on zero-probability cells")
        statistic += (tail_observed - tail_expected) ** 2 / tail_expected
        cells += 1
    dof = cells - 1
    return ChiSquareResult(
        statistic=statistic,
        dof=dof,
        pvalue=float(_scipy_chi2.sf(statistic, dof)),
        cells=cells,
        tail_pooled=tail_pooled,
    )
