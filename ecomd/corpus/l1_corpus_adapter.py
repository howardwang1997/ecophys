"""L1 corpus adapter: F_exec corpus -> EcoMD v2 input surface (build item L1-1).

Spec (simulator contracts section 2.1, item L1-1): a projector mapping the
F_exec projection of a lab-asset-v3 tape to lineage L1's input surface
(``EcoMDSimulator`` / ``EcoMDv2Potential``). Per clearing round ``t`` the
adapter emits exactly the spec'd surfaces:

1. INPUT — anonymous book-state summary + conserving channels, shaped as the
   agent-state tensor ``s ∈ R^{N x d_state}`` plus the market-context vector of
   the ``EcoMDSimulator.step`` pattern (ecomd.py:1110-1116:
   ``[log_price, volatility, last_log_return]``). ``N = n_slots``: the
   anonymous book is the touched-price-level ladder of the frozen corpus
   grammar (build item E-1), so each anonymous "agent" is one queue slot and
   padding slots are the documented never-clearable level-agents. ``d_state``
   is FIXED at ``L1_D_STATE`` = 6:

   ============  ========================================================
   channel       definition (input for round t; τ = t-1, all pre-round)
   ============  ========================================================
   0 log1p_qty   ``log1p(slot_quantities[τ, j])`` — last completed round's
                 executed volume at slot j.
   1 price_dev   ``(slot_prices[τ, j] - post_mid_τ) / max(post_spread_τ, 1)``
                 for non-padding slots (price > 0); 0.0 for padding slots.
   2 log_cum_vol ``log1p(cumulative volume units through round τ)`` [shared].
   3 log_cum_cash ``log1p(cumulative cash ticks through round τ)``   [shared].
   4 post_spread ``post_spread_τ`` in ticks                          [shared].
   5 mid_move    ``post_mid_τ - pre_mid_τ`` under the frozen grammar's
                 quote-fallback rule (surviving side; both None -> 0)
                                                                 [shared].
   ============  ========================================================

   Context (same fallback rule for the mids): ``log_price_t =
   log(max(post_mid_τ, 1))`` (0.0 at ``t = 0``); ``last_log_return_t =
   log(max(post_mid_τ, 1)) - log(max(post_mid_{τ-1}, 1))`` (0.0 for
   ``t <= 1``); ``volatility_t`` = EWMA of |return| over completed rounds in
   the repo convention ``v_k = (1-alpha)*v_{k-1} + alpha*|r_k|`` with
   ``alpha = VOLATILITY_EWMA_ALPHA`` (0.05, the price_formation default), seeded
   at 0.0 — the pre-session no-information token (the tape carries no
   ``sigma_price`` prior).

   PRE-ROUND-STATE-ONLY RULE (load-bearing): the input at round ``t`` is a
   function of rounds ``< t`` ONLY — round ``t``'s F_exec records never leak
   into round ``t``'s input. ``t = 0`` carries the all-zero no-event token;
   the session-initial resting book is engine state outside the F_exec
   selection and is deliberately not projected (E-1's pure-selection scope).

2. FLOW SLOT — ``flow_slot`` (R, N): the exposed ``z_t`` slot that L1's new
   head (build item L1-2) writes its per-round resting-quantity prediction
   into. The adapter EXPOSES the slot (zero-filled, deterministic); it never
   predicts. ``slot_prices`` rides on the supervision side for the through-M
   cash arithmetic (allocation x price).

3. SUPERVISION / TARGET CONTEXT — the F_exec event records of round ``t``:
   E-1's frozen 14-feature row, the per-round payload tuples (1:1 via
   ``schema_spec.json`` payload fields), and the slot tensors.

4. CONSERVING CHANNELS — E-4's increment/cumulative matrices passed through
   integer-exactly (``channels_inc`` / ``channels_abs``, int64; contract C5's
   two aggregate channels in ``CHANNEL_ORDER``). When ``series=`` is not
   supplied the adapter derives them itself via the E-4 emitter
   (``lab_asset.conserving_emitter``, imported lazily so ``ecomd`` stays
   importable without ``scripts/`` on the path; import direction adapter ->
   engine modules only — ``ecomd/models/`` never imports ``lab_asset``).

Lineage invariance: the adapter does NOT re-project the tape. Every feature,
payload and slot value is E-1's ``FexecCorpus`` verbatim; every channel value
is E-4's series verbatim (grid and content agreement are enforced at build
time, not assumed — two independently produced artifacts are cross-checked).
The adapter's own contribution is only the documented lag/mapping above.

Determinism: a pure function of ``(prestate, tape, seed)`` (``seed`` binds
identity only — no stochastic consumer anywhere in this path; the contracts
section 2.4 global-RNG lesson applied day one). Same inputs -> byte-identical
outputs. ``adapter_hash`` binds the adapter id/version, the fixed channel
names, E-1's ``corpus_hash`` (provenance: full tape incl. request-side
records), the E-4 series hash, seed, ``n_slots``, dtype and the tensor-only
``content_hash`` — request-side perturbations change provenance, never
content.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final, Protocol, TypeGuard, cast

import torch
from torch import Tensor

from .fexec_projector import (
    DEFAULT_N_SLOTS,
    FexecPrestate,
    FexecRound,
    FexecTapeRecord,
    project_fexec_corpus,
)

__all__ = [
    "ADAPTER_ID",
    "ADAPTER_VERSION",
    "L1_AGENT_STATE_CHANNELS",
    "L1_CONTEXT_CHANNELS",
    "L1_CONTEXT_SIZE",
    "L1_D_STATE",
    "VOLATILITY_EWMA_ALPHA",
    "ConservingSeriesView",
    "L1Corpus",
    "build_l1_corpus",
]

ADAPTER_ID: Final[str] = "ecomd.corpus.l1_corpus_adapter"
ADAPTER_VERSION: Final[int] = 1
L1_D_STATE: Final[int] = 6
L1_CONTEXT_SIZE: Final[int] = 3
L1_AGENT_STATE_CHANNELS: Final[tuple[str, ...]] = (
    "log1p_prev_slot_quantity",
    "prev_slot_price_rel_spread",
    "log1p_cum_volume",
    "log1p_cum_cash",
    "prev_post_spread",
    "prev_mid_move",
)
L1_CONTEXT_CHANNELS: Final[tuple[str, ...]] = (
    "log_price",
    "volatility",
    "last_log_return",
)
VOLATILITY_EWMA_ALPHA: Final[float] = 0.05


class _ConservingRoundView(Protocol):
    """One E-4 round as seen here: only the grid key is consumed."""

    @property
    def match_ts(self) -> int: ...


class ConservingSeriesView(Protocol):
    """Structural view of E-4's ``ConservingChannelSeries`` consumed here.

    Engine modules are referenced, not imported (the E-1 idiom), so the
    adapter stays importable without ``scripts/`` on the path while still
    accepting the real E-4 object (or a hand-built equivalent).
    """

    @property
    def session_id(self) -> str: ...

    @property
    def allocation_rule(self) -> str: ...

    @property
    def rounds(self) -> Sequence[_ConservingRoundView]: ...

    @property
    def n_rounds(self) -> int: ...

    def increment_matrix(self) -> list[list[int]]: ...

    def cumulative_matrix(self) -> list[list[int]]: ...

    def to_json(self) -> str: ...


@dataclass(frozen=True)
class L1Corpus:
    """The L1 input surface of one lab-asset-v3 session.

    INPUT surface (strictly pre-round): ``agent_states`` (R, N, d_state) and
    ``context`` (R, 3, the ecomd.py:1110-1116 triple order). EXPOSED SLOT:
    ``flow_slot`` (R, N), zero-filled — L1-2 writes ``z_t`` here.
    SUPERVISION surface: ``features`` (R, 14, frozen grammar), ``rounds``
    (1:1 payload tuples), ``slot_prices`` / ``slot_quantities`` (R, N) int64.
    CONSERVING CHANNELS: ``channels_inc`` / ``channels_abs`` (R, 2) int64 —
    E-4 pass-through, integer-exact.
    """

    session_id: str
    schema_version: str
    allocation_rule: str
    seed: int
    n_slots: int
    d_state: int
    match_ticks: tuple[int, ...]
    n_rounds: int
    n_executions: int
    agent_states: Tensor
    context: Tensor
    flow_slot: Tensor
    features: Tensor
    channels_inc: Tensor
    channels_abs: Tensor
    slot_prices: Tensor
    slot_quantities: Tensor
    rounds: tuple[FexecRound, ...]
    corpus_hash: str
    series_hash: str
    content_hash: str
    adapter_hash: str

    @property
    def n_agents(self) -> int:
        """L1 agent count: one anonymous level-agent per queue slot."""
        return self.n_slots


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _stable_hash(payload: object) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _is_int(value: object) -> TypeGuard[int]:
    return isinstance(value, int) and not isinstance(value, bool)


def _derive_series(
    prestate: FexecPrestate, tape: Sequence[FexecTapeRecord]
) -> ConservingSeriesView:
    """E-4 conserving channels via the emitter, imported lazily.

    ``scripts/lab_asset`` is not an installed package; keeping the import
    inside this function means ``import ecomd`` never requires it. The import
    direction is adapter -> engine modules only.
    """

    try:
        from lab_asset.conserving_emitter import emit_conserving_channels
    except ImportError as error:
        raise ValueError(
            "deriving the conserving channels requires the E-4 emitter "
            "(scripts/lab_asset on sys.path); pass series= explicitly when "
            "it is unavailable"
        ) from error
    return cast(ConservingSeriesView, emit_conserving_channels(prestate, tape))


def _int_matrix(matrix: object, name: str, n_rounds: int) -> list[list[int]]:
    if not isinstance(matrix, list) or len(matrix) != n_rounds:
        raise ValueError(
            f"E-4 series {name} must be a list of {n_rounds} rows, got {matrix!r}"
        )
    rows: list[list[int]] = []
    for row in matrix:
        if not isinstance(row, list) or len(row) != 2:
            raise ValueError(f"E-4 series {name} rows must have 2 channels, got {row!r}")
        for value in row:
            if not _is_int(value):
                raise ValueError(f"E-4 series {name} values must be ints, got {row!r}")
        rows.append([int(value) for value in row])
    return rows


def _quote_mid_spread(bid: int | None, ask: int | None) -> tuple[float, float]:
    """(mid, spread) under the frozen grammar's quote-fallback rule.

    Mirrors ``ecomd.models.fact_surrogate._quote_mid_spread`` (the documented
    rule E-1's features already use): both sides None -> (0, 0); one side
    None -> mid falls back to the surviving side, spread 0.
    """

    if bid is None and ask is None:
        return 0.0, 0.0
    if bid is None or ask is None:
        survivor = cast(int, ask if bid is None else bid)
        return float(survivor), 0.0
    return (bid + ask) / 2.0, float(ask - bid)


def _payload_quote(payload: Mapping[str, object], key: str) -> int | None:
    value = payload[key]
    if value is None or _is_int(value):
        return value
    raise ValueError(f"execution payload {key} must be an int or None, got {value!r}")


def _round_quotes(
    rounds: Sequence[FexecRound],
) -> list[tuple[float, float, float]]:
    """(pre_mid, post_mid, post_spread) per round from the E-1 selections.

    Pre-quotes come from the round's first record, post-quotes from its last
    (the frozen grammar's convention). Values are float64 Python arithmetic —
    independent of the emitted tensor dtype.
    """

    quotes: list[tuple[float, float, float]] = []
    for round_ in rounds:
        if not round_.payloads:
            # E-1 emits no execution-free rounds, but keep the token exact.
            quotes.append((0.0, 0.0, 0.0))
            continue
        first = round_.payloads[0]
        last = round_.payloads[-1]
        pre_mid, _ = _quote_mid_spread(
            _payload_quote(first, "pre_best_bid"),
            _payload_quote(first, "pre_best_ask"),
        )
        post_mid, post_spread = _quote_mid_spread(
            _payload_quote(last, "post_best_bid"),
            _payload_quote(last, "post_best_ask"),
        )
        quotes.append((pre_mid, post_mid, post_spread))
    return quotes


def _log_price(mid: float) -> float:
    # tick prices are positive in any real session; floor at 1 so the
    # no-information token (mid 0) stays finite
    return math.log(max(mid, 1.0))


def build_l1_corpus(
    prestate: FexecPrestate,
    tape: Sequence[FexecTapeRecord],
    seed: int,
    *,
    series: ConservingSeriesView | None = None,
    n_slots: int = DEFAULT_N_SLOTS,
    dtype: torch.dtype = torch.float32,
) -> L1Corpus:
    """Adapt a lab-asset-v3 tape to L1's input surface.

    Pure function of ``(prestate, tape, seed)``: E-1's projector and E-4's
    emitter are themselves pure functions of (prestate, tape), composed here
    with the documented pre-round lag/mapping. ``series=`` lets the caller
    inject a precomputed E-4 series (identical semantics; useful when
    ``scripts/`` is not importable or the series is cached); the adapter
    still enforces grid and content agreement against E-1's projection.
    """

    if seed < 0:
        raise ValueError(f"seed must be nonnegative, got {seed}")
    if n_slots < 1:
        raise ValueError(f"n_slots must be >= 1, got {n_slots}")
    if len(L1_AGENT_STATE_CHANNELS) != L1_D_STATE:
        raise ValueError("L1_AGENT_STATE_CHANNELS must enumerate d_state channels")

    corpus = project_fexec_corpus(prestate, tape, seed, n_slots=n_slots, dtype=dtype)
    active = series if series is not None else _derive_series(prestate, tape)

    n_rounds = len(corpus.rounds)
    grid = [round_.match_ts for round_ in active.rounds]
    if grid != list(corpus.match_ticks):
        raise ValueError(
            "E-4 series round grid does not match the E-1 corpus match ticks: "
            f"{grid} vs {list(corpus.match_ticks)}"
        )
    if active.session_id != corpus.session_id:
        raise ValueError(
            f"E-4 series session {active.session_id!r} does not match the "
            f"corpus session {corpus.session_id!r}"
        )
    if active.allocation_rule != corpus.allocation_rule:
        raise ValueError(
            f"E-4 series allocation rule {active.allocation_rule!r} does not "
            f"match the corpus rule {corpus.allocation_rule!r}"
        )

    inc_rows = _int_matrix(active.increment_matrix(), "increment_matrix()", n_rounds)
    abs_rows = _int_matrix(active.cumulative_matrix(), "cumulative_matrix()", n_rounds)
    if inc_rows != corpus.channels_delta.tolist():
        raise ValueError(
            "E-4 increment matrix disagrees with E-1 channels_delta: "
            f"{inc_rows} vs {corpus.channels_delta.tolist()}"
        )
    if abs_rows != corpus.channels_cumulative.tolist():
        raise ValueError(
            "E-4 cumulative matrix disagrees with E-1 channels_cumulative: "
            f"{abs_rows} vs {corpus.channels_cumulative.tolist()}"
        )

    if n_rounds:
        channels_inc = torch.tensor(inc_rows, dtype=torch.int64)
        channels_abs = torch.tensor(abs_rows, dtype=torch.int64)
    else:
        channels_inc = torch.zeros((0, 2), dtype=torch.int64)
        channels_abs = torch.zeros((0, 2), dtype=torch.int64)

    quotes = _round_quotes(corpus.rounds)
    log_prices = [_log_price(post_mid) for _, post_mid, _ in quotes]
    returns = [0.0] * n_rounds
    for k in range(1, n_rounds):
        returns[k] = log_prices[k] - log_prices[k - 1]
    volatilities = [0.0] * n_rounds
    for k in range(1, n_rounds):
        volatilities[k] = (
            1.0 - VOLATILITY_EWMA_ALPHA
        ) * volatilities[k - 1] + VOLATILITY_EWMA_ALPHA * abs(returns[k])

    slot_prices = corpus.slot_prices.tolist()
    slot_quantities = corpus.slot_quantities.tolist()

    state_rows: list[list[list[float]]] = []
    context_rows: list[list[float]] = []
    for t in range(n_rounds):
        if t == 0:
            state_rows.append([[0.0] * L1_D_STATE for _ in range(n_slots)])
            context_rows.append([0.0, 0.0, 0.0])
            continue
        tau = t - 1
        pre_mid, post_mid, post_spread = quotes[tau]
        cum_volume = int(channels_abs[tau, 0])
        cum_cash = int(channels_abs[tau, 1])
        denom = max(post_spread, 1.0)
        row: list[list[float]] = []
        for j in range(n_slots):
            price = slot_prices[tau][j]
            quantity = slot_quantities[tau][j]
            price_dev = (price - post_mid) / denom if price > 0 else 0.0
            row.append(
                [
                    math.log1p(quantity),
                    price_dev,
                    math.log1p(cum_volume),
                    math.log1p(cum_cash),
                    post_spread,
                    post_mid - pre_mid,
                ]
            )
        state_rows.append(row)
        context_rows.append([log_prices[tau], volatilities[tau], returns[tau]])

    if n_rounds:
        agent_states = torch.tensor(state_rows, dtype=dtype)
        context = torch.tensor(context_rows, dtype=dtype)
    else:
        agent_states = torch.zeros((0, n_slots, L1_D_STATE), dtype=dtype)
        context = torch.zeros((0, L1_CONTEXT_SIZE), dtype=dtype)
    flow_slot = torch.zeros((n_rounds, n_slots), dtype=dtype)

    series_hash = _stable_hash({"series_json": active.to_json()})
    content_hash = _stable_hash(
        {
            "match_ticks": list(corpus.match_ticks),
            "n_slots": n_slots,
            "d_state": L1_D_STATE,
            "agent_states": agent_states.tolist(),
            "context": context.tolist(),
            "flow_slot": flow_slot.tolist(),
            "features": corpus.features.tolist(),
            "channels_inc": channels_inc.tolist(),
            "channels_abs": channels_abs.tolist(),
            "slot_prices": corpus.slot_prices.tolist(),
            "slot_quantities": corpus.slot_quantities.tolist(),
        }
    )
    adapter_hash = _stable_hash(
        {
            "adapter": ADAPTER_ID,
            "adapter_version": ADAPTER_VERSION,
            "agent_state_channels": list(L1_AGENT_STATE_CHANNELS),
            "context_channels": list(L1_CONTEXT_CHANNELS),
            "volatility_ewma_alpha": VOLATILITY_EWMA_ALPHA,
            "seed": seed,
            "n_slots": n_slots,
            "dtype": str(dtype),
            "corpus_hash": corpus.corpus_hash,
            "series_hash": series_hash,
            "content_hash": content_hash,
        }
    )

    return L1Corpus(
        session_id=corpus.session_id,
        schema_version=corpus.schema_version,
        allocation_rule=corpus.allocation_rule,
        seed=seed,
        n_slots=n_slots,
        d_state=L1_D_STATE,
        match_ticks=corpus.match_ticks,
        n_rounds=n_rounds,
        n_executions=corpus.n_executions,
        agent_states=agent_states,
        context=context,
        flow_slot=flow_slot,
        features=corpus.features,
        channels_inc=channels_inc,
        channels_abs=channels_abs,
        slot_prices=corpus.slot_prices,
        slot_quantities=corpus.slot_quantities,
        rounds=corpus.rounds,
        corpus_hash=corpus.corpus_hash,
        series_hash=series_hash,
        content_hash=content_hash,
        adapter_hash=adapter_hash,
    )
