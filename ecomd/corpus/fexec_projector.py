"""F_exec corpus projector: lab-asset-v3 tape -> per-clearing-round tensors.

Build item E-1 of the D0 build register (simulator contracts section 4; spec
section 1, PI decision D1_01): the through-M training corpus is ``F_exec`` =
execution payloads + ``allocation_draw`` + pre/post BBO prices — a PURE
SELECTION among recorded schema payload fields of ``execution``-type records
(frozen ``schema_spec.json`` field list ``[execution, aggressor_role,
maker_role, allocation_draw?, pre_best_bid, pre_best_ask, post_best_bid,
post_best_ask]``). ``order_accepted.resting_quantity`` and every request-side
event are excluded by construction: nothing outside ``execution`` records
projects into corpus content.

The output grammar is lineage-invariant by construction: the per-round feature
matrix is emitted by the frozen 14-feature map
``ecomd.models.fact_surrogate.FEXEC_ROUND_FEATURES`` itself (the L2 input
grammar), so both lineages consume identical features. The additional batch
slots the L1 side needs come from the same frozen selection:

- Rounds are grouped by the ENGINE CLOCK: a clearing round is the set of
  execution records sharing one ``execution.clocks.match_ts`` (the engine's
  ``last_match_ts``); round index ``t`` maps to the ``t``-th distinct execution
  match tick in ascending order, and requests at one tick merge into one
  round. The client-supplied ``round_id`` is carried as metadata only (it is
  client-controlled and uniformly 0 in the frozen fixtures, so it cannot define
  the round grid). Rounds without executions are not part of the corpus — they
  carry no F_exec information; the documented no-event token remains reachable
  by calling ``fexec_round_features`` on an empty payload sequence directly.
- ``channels_delta[t] = (total executed volume units, total executed cash
  ticks)`` of round ``t`` — contract C5's two aggregate conserving channels,
  derivable from execution payloads alone; ``channels_cumulative`` is the
  zero-base cumsum (the ABS-head target base). Cumulative engine STATE
  (cash/inventory levels) is not tape-derivable and stays with build item E-4
  (``lab_asset.replay.regenerate``).
- Ragged-round padding contract (owned by this module per the L2 build
  caveat): each round's touched price levels — the distinct execution prices
  of the round, ascending — occupy slots ``0..k-1``; slots are right-padded
  to fixed ``n_slots`` (default 8, matching
  ``ecomd.models.fact_surrogate.FactSurrogateConfig.n_slots``) with quantity-0
  slots at price 0, which the through-M estimators treat as never-clearable
  (the padding price is inert for the cash channel because allocation x price
  = 0). A round touching more than ``n_slots`` levels raises ``ValueError`` —
  never silent truncation.

Determinism and identity: the projector has no stochastic consumer (the
simulator-contracts section 2.4 global-RNG lesson, applied day one), so the
``seed`` argument is identity binding only. Same ``(prestate, tape, seed,
n_slots, dtype)`` -> byte-identical outputs. ``corpus_hash`` is sha256 over
canonical JSON binding the projector version, the frozen grammar, the
session/prestate commitment, the seed, ``n_slots``, dtype, the full-tape
``tape_hash`` (provenance) and the selection-only ``content_hash`` (corpus
content): request-side perturbations change provenance but never content.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Final, Protocol, TypeGuard, cast

import torch
from torch import Tensor

from ..models.fact_surrogate import FEXEC_ROUND_FEATURES, fexec_round_features

__all__ = [
    "DEFAULT_N_SLOTS",
    "FEXEC_OPTIONAL_FIELDS",
    "FEXEC_REQUIRED_FIELDS",
    "FexecCorpus",
    "FexecRound",
    "project_fexec_corpus",
]

FEXEC_REQUIRED_FIELDS: Final[tuple[str, ...]] = (
    "execution",
    "aggressor_role",
    "maker_role",
    "pre_best_bid",
    "pre_best_ask",
    "post_best_bid",
    "post_best_ask",
)
FEXEC_OPTIONAL_FIELDS: Final[tuple[str, ...]] = ("allocation_draw",)
DEFAULT_N_SLOTS: Final[int] = 8
PROJECTOR_VERSION: Final[int] = 1
PROJECTOR_ID: Final[str] = "ecomd.corpus.fexec_projector"
REQUIRED_SCHEMA_VERSION: Final[str] = "lab-asset-v3"
ENGINE_KERNELS: Final[frozenset[str]] = frozenset(
    {"fifo", "random_unit_within_price"}
)
_ALLOCATION_DRAW_FIELDS: Final[frozenset[str]] = frozenset(
    {"price", "eligible_units", "selected_unit", "maker_order_id"}
)
_SESSION_START_FIELDS: Final[frozenset[str]] = frozenset(
    {"session_id", "schema_version", "allocation_rule", "prestate_hash"}
)


class FexecPrestate(Protocol):
    """Structural view of ``lab_asset.schema.SessionPrestate`` used here.

    Engine modules are referenced, not imported (the ``ecomd.mechanisms.through_m``
    idiom), so the projector stays importable without the ``scripts`` path.
    """

    @property
    def session_id(self) -> str: ...

    @property
    def schema_version(self) -> str: ...

    @property
    def allocation_rule(self) -> str: ...

    @property
    def seed(self) -> int: ...


class FexecTapeRecord(Protocol):
    """Structural view of ``lab_asset.schema.TapeRecord`` used here."""

    @property
    def sequence(self) -> int: ...

    @property
    def event_type(self) -> str: ...

    @property
    def payload(self) -> Mapping[str, object]: ...


@dataclass(frozen=True)
class FexecRound:
    """One clearing round's F_exec selection (supervision context).

    ``payloads`` are freshly built selection dicts (exactly the frozen schema
    field list, ``allocation_draw`` only when the engine recorded one) in tape
    order; ``round_ids`` is the sorted set of client-supplied ``round_id``
    values observed in the round, metadata only.
    """

    round_index: int
    match_ts: int
    first_sequence: int
    last_sequence: int
    round_ids: tuple[int, ...]
    payloads: tuple[Mapping[str, object], ...]


@dataclass(frozen=True)
class FexecCorpus:
    """Per-round F_exec tensors plus identity hashes.

    ``features`` is ``(R, len(FEXEC_ROUND_FEATURES))`` in the frozen grammar's
    ``dtype``; ``channels_delta`` / ``channels_cumulative`` are ``(R, 2)``
    int64 (volume units, cash ticks); ``slot_prices`` / ``slot_quantities``
    are ``(R, n_slots)`` int64 under the padding contract above.
    """

    session_id: str
    schema_version: str
    allocation_rule: str
    seed: int
    n_slots: int
    match_ticks: tuple[int, ...]
    rounds: tuple[FexecRound, ...]
    n_executions: int
    features: Tensor
    channels_delta: Tensor
    channels_cumulative: Tensor
    slot_prices: Tensor
    slot_quantities: Tensor
    tape_hash: str
    content_hash: str
    corpus_hash: str


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _stable_hash(payload: object) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _is_int(value: object) -> TypeGuard[int]:
    return isinstance(value, int) and not isinstance(value, bool)


def _canonicalize(value: object) -> object:
    """Normalize engine-live objects to their JSON round-trip form.

    Engine-live payloads nest dataclasses (``ThreeClocks``) and ``StrEnum``
    values; fixture tapes loaded from disk carry the same data as plain
    dicts/strings. Canonicalization makes the two byte-identical under the
    canonical JSON hashing below, which is what lets a regenerated tape
    reproduce a recorded tape's hashes exactly.
    """

    if is_dataclass(value) and not isinstance(value, type):
        return asdict(cast(Any, value))
    if isinstance(value, Mapping):
        return {key: _canonicalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    return value


def _clock_match_ts(execution: Mapping[str, object]) -> int:
    clocks = execution.get("clocks")
    match_ts = (
        clocks.get("match_ts") if isinstance(clocks, Mapping)
        else getattr(clocks, "match_ts", None)
    )
    if not _is_int(match_ts):
        raise ValueError("execution.clocks.match_ts must be an int")
    return match_ts


def _execution_mapping(payload: Mapping[str, object]) -> Mapping[str, object]:
    raw = payload.get("execution")
    if not isinstance(raw, Mapping):
        raise ValueError("execution payload must carry an 'execution' mapping")
    return raw


def _select_execution_payload(
    payload: Mapping[str, object],
) -> dict[str, object]:
    """Pure F_exec selection of one ``execution`` record payload.

    Enforces the frozen field list exactly: every required field present, no
    key outside the frozen selection (``resting_quantity`` and any
    request-side field are rejected here, not merely dropped), and the nested
    fields this projector consumes are type-checked.
    """

    keys = set(payload)
    missing = [field for field in FEXEC_REQUIRED_FIELDS if field not in keys]
    if missing:
        raise ValueError(f"execution payload missing F_exec fields: {missing}")
    extra = keys - set(FEXEC_REQUIRED_FIELDS) - set(FEXEC_OPTIONAL_FIELDS)
    if extra:
        raise ValueError(f"execution payload carries non-F_exec fields: {sorted(extra)}")

    execution = _execution_mapping(payload)
    for field in ("quantity", "price", "round_id"):
        if not _is_int(execution.get(field)):
            raise ValueError(f"execution.{field} must be an int, got {execution.get(field)!r}")
    if _clock_match_ts(execution) < 0:
        raise ValueError("execution.clocks.match_ts must be nonnegative")

    draw = payload.get("allocation_draw")
    if draw is not None:
        if not isinstance(draw, Mapping) or set(draw) != _ALLOCATION_DRAW_FIELDS:
            raise ValueError(
                "allocation_draw must carry exactly "
                f"{sorted(_ALLOCATION_DRAW_FIELDS)}, got {draw!r}"
            )
        for field in ("price", "eligible_units", "selected_unit"):
            if not _is_int(draw.get(field)):
                raise ValueError(f"allocation_draw.{field} must be an int")
        if not isinstance(draw.get("maker_order_id"), str):
            raise ValueError("allocation_draw.maker_order_id must be a str")

    selected: dict[str, object] = {field: payload[field] for field in FEXEC_REQUIRED_FIELDS}
    if draw is not None:
        selected["allocation_draw"] = draw
    return {key: _canonicalize(value) for key, value in selected.items()}


def _session_binding(
    prestate: FexecPrestate, tape: Sequence[FexecTapeRecord]
) -> dict[str, str]:
    """Validate the tape's session_start commitment against the prestate."""

    if not tape:
        raise ValueError("tape must contain at least the session_start record")
    if tape[0].event_type != "session_start":
        raise ValueError("tape must begin with the session_start record")
    extra_starts = sum(
        1 for record in tape[1:] if record.event_type == "session_start"
    )
    if extra_starts:
        raise ValueError("tape must contain exactly one session_start record")

    payload = tape[0].payload
    if set(payload) != _SESSION_START_FIELDS:
        raise ValueError(
            "session_start payload must carry exactly "
            f"{sorted(_SESSION_START_FIELDS)}, got {sorted(payload)}"
        )
    binding: dict[str, str] = {}
    for field in ("session_id", "schema_version", "allocation_rule", "prestate_hash"):
        value = payload[field]
        if not isinstance(value, str):
            raise ValueError(f"session_start.{field} must be a str, got {value!r}")
        binding[field] = value

    if binding["schema_version"] != REQUIRED_SCHEMA_VERSION:
        raise ValueError(
            f"schema_version must be {REQUIRED_SCHEMA_VERSION!r}, got {binding['schema_version']!r}"
        )
    if binding["allocation_rule"] not in ENGINE_KERNELS:
        raise ValueError(
            f"allocation_rule must be one of {sorted(ENGINE_KERNELS)}, "
            f"got {binding['allocation_rule']!r}"
        )
    if prestate.session_id != binding["session_id"]:
        raise ValueError(
            f"prestate session_id {prestate.session_id!r} does not match the "
            f"tape commitment {binding['session_id']!r}"
        )
    if prestate.schema_version != REQUIRED_SCHEMA_VERSION:
        raise ValueError(
            f"prestate schema_version must be {REQUIRED_SCHEMA_VERSION!r}, "
            f"got {prestate.schema_version!r}"
        )
    if str(prestate.allocation_rule) != binding["allocation_rule"]:
        raise ValueError(
            f"prestate allocation_rule {prestate.allocation_rule!r} does not match "
            f"the tape commitment {binding['allocation_rule']!r}"
        )
    if is_dataclass(prestate) and not isinstance(prestate, type):
        try:
            recomputed = _stable_hash(asdict(cast(Any, prestate)))
        except (TypeError, ValueError) as error:
            raise ValueError("prestate is not canonically serializable") from error
        if recomputed != binding["prestate_hash"]:
            raise ValueError(
                "recomputed prestate hash does not match the session_start commitment"
            )
    return binding


def project_fexec_corpus(
    prestate: FexecPrestate,
    tape: Sequence[FexecTapeRecord],
    seed: int,
    *,
    n_slots: int = DEFAULT_N_SLOTS,
    dtype: torch.dtype = torch.float32,
) -> FexecCorpus:
    """Project a lab-asset-v3 tape to the per-clearing-round F_exec corpus.

    Pure function of ``(prestate, tape, seed)`` (plus ``n_slots``/``dtype``):
    deterministic, replay-safe (a regenerated tape projects to a byte-identical
    corpus), and self-certifying (the session_start prestate commitment is
    re-verified against the passed prestate). ``seed`` binds identity only —
    the projector draws nothing.
    """

    if seed < 0:
        raise ValueError(f"seed must be nonnegative, got {seed}")
    if n_slots < 1:
        raise ValueError(f"n_slots must be >= 1, got {n_slots}")
    binding = _session_binding(prestate, tape)

    grouped: dict[int, list[tuple[int, dict[str, object]]]] = {}
    for record in tape:
        if record.event_type != "execution":
            continue
        selected = _select_execution_payload(record.payload)
        match_ts = _clock_match_ts(_execution_mapping(selected))
        grouped.setdefault(match_ts, []).append((record.sequence, selected))

    rounds: list[FexecRound] = []
    feature_rows: list[Tensor] = []
    delta_rows: list[list[int]] = []
    price_rows: list[list[int]] = []
    quantity_rows: list[list[int]] = []
    n_executions = 0
    for index, match_ts in enumerate(sorted(grouped)):
        entries = grouped[match_ts]
        volume = 0
        cash = 0
        level_quantity: dict[int, int] = {}
        round_ids: set[int] = set()
        for _, selected in entries:
            execution = cast(Mapping[str, object], selected["execution"])
            quantity = cast(int, execution["quantity"])
            price = cast(int, execution["price"])
            volume += quantity
            cash += price * quantity
            level_quantity[price] = level_quantity.get(price, 0) + quantity
            round_ids.add(cast(int, execution["round_id"]))
        if len(level_quantity) > n_slots:
            raise ValueError(
                f"round at match_ts={match_ts} touches {len(level_quantity)} price "
                f"levels, exceeding n_slots={n_slots}; raise n_slots (no truncation)"
            )
        prices = sorted(level_quantity)
        pad = [0] * (n_slots - len(prices))
        price_rows.append(prices + pad)
        quantity_rows.append([level_quantity[price] for price in prices] + pad)
        delta_rows.append([volume, cash])
        payloads = tuple(selected for _, selected in entries)
        feature_rows.append(fexec_round_features(payloads, dtype=dtype))
        rounds.append(
            FexecRound(
                round_index=index,
                match_ts=match_ts,
                first_sequence=entries[0][0],
                last_sequence=entries[-1][0],
                round_ids=tuple(sorted(round_ids)),
                payloads=payloads,
            )
        )
        n_executions += len(entries)

    n_rounds = len(rounds)
    if feature_rows:
        features = torch.stack(feature_rows)
    else:
        features = torch.zeros((n_rounds, len(FEXEC_ROUND_FEATURES)), dtype=dtype)
    if delta_rows:
        channels_delta = torch.tensor(delta_rows, dtype=torch.int64)
    else:
        channels_delta = torch.zeros((n_rounds, 2), dtype=torch.int64)
    channels_cumulative = torch.cumsum(channels_delta, dim=0)
    if price_rows:
        slot_prices = torch.tensor(price_rows, dtype=torch.int64)
        slot_quantities = torch.tensor(quantity_rows, dtype=torch.int64)
    else:
        slot_prices = torch.zeros((n_rounds, n_slots), dtype=torch.int64)
        slot_quantities = torch.zeros((n_rounds, n_slots), dtype=torch.int64)

    tape_hash = _stable_hash(
        [
            {
                "sequence": record.sequence,
                "event_type": record.event_type,
                "payload": _canonicalize(record.payload),
            }
            for record in tape
        ]
    )
    content_hash = _stable_hash(
        [
            {
                "match_ts": round_.match_ts,
                "first_sequence": round_.first_sequence,
                "last_sequence": round_.last_sequence,
                "round_ids": list(round_.round_ids),
                "payloads": [dict(payload) for payload in round_.payloads],
            }
            for round_ in rounds
        ]
    )
    corpus_hash = _stable_hash(
        {
            "projector": PROJECTOR_ID,
            "projector_version": PROJECTOR_VERSION,
            "grammar": list(FEXEC_ROUND_FEATURES),
            "schema_version": binding["schema_version"],
            "session_id": binding["session_id"],
            "allocation_rule": binding["allocation_rule"],
            "prestate_hash": binding["prestate_hash"],
            "seed": seed,
            "n_slots": n_slots,
            "dtype": str(dtype),
            "tape_hash": tape_hash,
            "content_hash": content_hash,
        }
    )

    return FexecCorpus(
        session_id=binding["session_id"],
        schema_version=binding["schema_version"],
        allocation_rule=binding["allocation_rule"],
        seed=seed,
        n_slots=n_slots,
        match_ticks=tuple(round_.match_ts for round_ in rounds),
        rounds=tuple(rounds),
        n_executions=n_executions,
        features=features,
        channels_delta=channels_delta,
        channels_cumulative=channels_cumulative,
        slot_prices=slot_prices,
        slot_quantities=slot_quantities,
        tape_hash=tape_hash,
        content_hash=content_hash,
        corpus_hash=corpus_hash,
    )
