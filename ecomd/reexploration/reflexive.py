"""Reflexive deployment cell (pre-freeze build item 10; exploratory-only).

Implements the frozen reflexive cell vocabulary: "simulator vs a simple
adapting execution policy (sim-in-loop)" measuring the execution-cost /
welfare gap vs DGP, descriptive only [pins: prereg v2 sections 4.6-4.7;
ops plan Part B section 1 (10 seeds, cells {R00, R11}, D1, both lineages);
contract v1 Part 4 / C12 five firewalls; calendar proposal item 10].

Firewall conformance built into the code (C12, verbatim intents):

1. Namespace separation — every emitted record carries
   ``exploratory=true, reflexive=true`` and a ``RFX-`` run-id prefix; the
   writer refuses any output directory whose path does not contain
   "reflexive" (fail-closed; confirmatory globs cannot pick these up by
   accident of a typo'd path either).
2. Temporal separation — a real (non-smoke) session REFUSES to start
   unless handed an unlock file carrying the four published block-analyzer
   analysis-JSON sha256 hashes (analyzer contract Part 3.1; the C12 unlock
   event). The pre-D0 build smoke bypasses the gate only in ``smoke=True``
   mode, which additionally refuses any trained checkpoint reference: a
   smoke session is engineering-only and can never masquerade as the
   scheduled cell. A non-smoke through-M sim arm must also select the
   ENGINE_BRIDGE mechanism backend (production arms never run MIRROR).
3. Statistical separation — outputs are descriptive summaries only; the
   mandatory label string is stamped on every record and every summary;
   ``summarize`` emits no confidence intervals, tests, or classifications.
4. No gate inputs — nothing here is importable by the confirmatory
   analyzers by construction (separate module, separate namespace fields);
   a reflexive crash is reported inside the record, never raised outward
   into campaign gates.
5. No retro-hypotheses — records carry the label verbatim; any hypothesis
   suggested by these outputs belongs to future work by the frozen clause.

Deployment semantics (implementation choice under the frozen wording,
recorded here and in the session log): both arms clear through the exact
lab-asset-v3 ReferenceEngine (allocation FIFO — contract C4 training
kernel; both reflexive cells' inference kernels resolve to FIFO on the id
axis) with seed-paired background streams. The deployed simulator enters
the POLICY's information loop through one scalar channel: the estimated
per-round conserving-channel VOLUME increment the policy sizes its child
orders against (EWMA) — realized engine volume in the DGP arm, decoded by
the deployed simulator in the SIM arm — so the measured gap isolates the
execution cost of acting on simulator feedback. Settlement is always true
engine settlement, keeping the two arms' welfare comparable. Inference
decoding follows the campaign grammar exactly: R00 reads the raw
coordinate head (ABS minus observed pre-round state, or INC); R11 routes
the integer-lattice flow/demand decode through the through-M mechanism
built by ``build_inference_mechanism`` at inference draw 1 of the seed's
own ``kernel:1`` substream (contract C2(b) draw order 1..16). L1 decodes
contemporaneously from (features_t, x_t); L2 decodes from the pre-round
hidden state before consuming features_t (the architecture's own timing).
Neither feed leaks within-round information into the policy's decision.

The policy itself is deterministic (no RNG anywhere in it): participation-
targeted liquidation; urgency is the behind-schedule ratio
u = (remaining/Q) * (T / rounds_left) (u = 1 on schedule, > 1 behind), and
crossing the threshold escalates to marketable limit orders; a passive
fill streak past the escalation bound escalates too. Warmup rounds run
the background flow only and DO feed the feedback providers (the deployed
simulator sees the pre-trade book as context; the policy's volume EWMA
warms on realized pre-trade rounds) without counting fill streaks.

Background-stream seeds use the E-2 ``derive_seed`` sha256 idiom under a
reserved "reflexive" part label and are asserted disjoint from the 20
training substreams of the same root (campaign G2 posture: disjoint by
overwhelming probability, asserted anyway).

Cell vocabulary mapping (ops plan section 0; the campaign's authoritative
8-cell grid is (arm_id, inference_enforcement)): R00 -> (absolute_raw,
raw); R11 -> (increment_raw, through_m). Records carry the explicit pair,
so the executed configuration is unambiguous even where the R/A letter
notation is read differently. ``validate_cell_vocabulary`` cross-checks
the mapping and the seed subsets against ``campaign`` at test time.

No GPU, no training, no market data, no confirmatory access is authorized
by this module. Execution of the scheduled cell itself additionally
requires the D0 freeze and the four-hash unlock (firewall 2).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REFLEXIVE_LABEL: str = "exploratory, excluded from confirmatory inference"
RUN_ID_PREFIX: str = "RFX-"
SESSION_SCHEMA: str = "ecomd-reflexive-session-v1"
SUMMARY_SCHEMA: str = "ecomd-reflexive-summary-v1"
POLICY_ACTOR: str = "px"
BG_ACTORS: tuple[str, ...] = ("b1", "b2", "b3", "b4", "b5")
N_BG_ACTORS: int = len(BG_ACTORS)
PRICE_BANDS: tuple[int, int] = (90, 110)
UNLOCK_HASH_LINES: int = 4  # four block analyzers (analyzer contract Part 3.1)
INFERENCE_DRAW_INDEX: int = 1  # contract C2(b) draw order 1..16; draw 1 deploys

# Annex B(d) / campaign.py reflexive_subset: first 10 of each training
# namespace. Cross-checked against ecomd.reexploration.campaign in
# validate_cell_vocabulary (tests pin it); kept literal here so importing
# this module never pulls torch.
REFLEXIVE_SEEDS: dict[str, tuple[int, ...]] = {
    "l1": tuple(range(11000, 11010)),
    "l2": tuple(range(12000, 12010)),
}
SEED_NAMESPACES: dict[str, str] = {"l1": "l1_training", "l2": "l2_training"}

DESCRIPTIVE_METRICS: tuple[str, ...] = (
    "implementation_shortfall_ticks",
    "unfilled_marked_shortfall_ticks",
    "avg_fill_price",
    "cash_received",
    "filled_units",
    "unfilled_units",
    "passive_fill_units",
    "aggressive_fill_units",
    "rounds_to_complete",
)


@dataclass(frozen=True)
class CellSpec:
    """One reflexive cell: R-label -> explicit campaign vocabulary pair."""

    r_label: str
    arm_id: str
    inference_enforcement: str
    coordinate: str


CELLS: dict[str, CellSpec] = {
    "R00": CellSpec("R00", "absolute_raw", "raw", "absolute"),
    "R11": CellSpec("R11", "increment_raw", "through_m", "increment"),
}


def validate_cell_vocabulary() -> None:
    """Fail loudly if CELLS drifts from the campaign's frozen grid."""

    from ecomd.reexploration.campaign import (
        ARMS_BY_ID,
        INFERENCE_ENFORCEMENTS,
        L1_TRAINING,
        L2_TRAINING,
    )

    for cell in CELLS.values():
        arm = ARMS_BY_ID.get(cell.arm_id)
        if arm is None:
            raise ValueError(f"cell {cell.r_label}: unknown arm {cell.arm_id}")
        if arm.coordinate != cell.coordinate:
            raise ValueError(
                f"cell {cell.r_label}: coordinate {cell.coordinate} != arm's "
                f"{arm.coordinate}"
            )
        if arm.enforcement != "raw":
            raise ValueError(
                f"cell {cell.r_label}: arm {cell.arm_id} is not a raw-train arm"
            )
        if cell.inference_enforcement not in INFERENCE_ENFORCEMENTS:
            raise ValueError(
                f"cell {cell.r_label}: inference {cell.inference_enforcement} "
                "outside the frozen enforcement pair"
            )
    if REFLEXIVE_SEEDS["l1"] != L1_TRAINING.reflexive_subset:
        raise ValueError("l1 reflexive subset drifted from Annex B(d)")
    if REFLEXIVE_SEEDS["l2"] != L2_TRAINING.reflexive_subset:
        raise ValueError("l2 reflexive subset drifted from Annex B(d)")


# ─────────────────────────────────────────────────────────────────────────────
# Seed derivation (E-2 derive_seed idiom, reserved "reflexive" part label)
# ─────────────────────────────────────────────────────────────────────────────


def reflexive_seed(seed_root: int, part: str) -> int:
    """int(sha256('|'.join(parts))[:8], 16) — E-2 derive_seed, byte-compatible.

    Parts: (seed_root, "reflexive", part). Disjoint from the 20 named
    training substreams with overwhelming probability; asserted by
    assert_seed_disjointness, never assumed.
    """

    payload = "|".join((str(seed_root), "reflexive", part))
    return int(hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8], 16)


def assert_seed_disjointness(seed_root: int) -> None:
    """The reflexive stream integers must miss every training substream."""

    from ecomd.training.train_fact_surrogate import derive_substream_seeds

    training = set(derive_substream_seeds(seed_root).values())
    for part in ("background",):
        value = reflexive_seed(seed_root, part)
        if value in training:
            raise RuntimeError(
                f"reflexive stream {part}={value} collides with a training "
                f"substream of root {seed_root}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# The simple adapting execution policy (deterministic; no RNG)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PolicyConfig:
    """Frozen policy + session parameters (defaults sized for the N<=500 smoke)."""

    q_total: int = 100
    n_rounds: int = 200
    warmup_rounds: int = 25
    # Background-flow calibration targets the F_exec corpus DGP scale
    # (dgp_request_generator defaults: ~10+ executed units per round, order
    # quantities 2-5) so the deployed simulators — trained on that corpus —
    # and the realized DGP volume live on one scale. The F_exec feature map
    # is tick-relative/log-scale and the volume decode reads channel 0 only,
    # so the (90, 110) band placement (robot_pilot's) versus the corpus's
    # (920, 1080) shifts nothing; the cash channel is never read.
    bg_events_per_round: int = 28
    bg_quantity_max: int = 5  # per-order quantity ~ U{1..5} (corpus: 2-5)
    participation: float = 0.10
    chunk_max: int = 16
    urgency_cross: float = 1.25  # behind-schedule ratio (u = 1 on schedule)
    streak_escalate: int = 3
    ewma_alpha: float = 0.25

    def __post_init__(self) -> None:
        if self.q_total < 1 or self.n_rounds < 1:
            raise ValueError("q_total and n_rounds must be >= 1")
        if not 0.0 < self.participation <= 1.0:
            raise ValueError("participation must be in (0, 1]")
        if self.chunk_max < 1 or self.streak_escalate < 1:
            raise ValueError("chunk_max and streak_escalate must be >= 1")
        if not 0.0 < self.ewma_alpha <= 1.0:
            raise ValueError("ewma_alpha must be in (0, 1]")
        if self.urgency_cross <= 1.0:
            raise ValueError("urgency_cross must exceed 1 (behind-schedule)")
        if self.bg_events_per_round < 1:
            raise ValueError("bg_events_per_round must be >= 1")
        if self.bg_quantity_max < 1:
            raise ValueError("bg_quantity_max must be >= 1")


@dataclass(frozen=True)
class Observation:
    """Everything the policy may condition on (pre-round, arm-blind)."""

    round_index: int
    rounds_left: int
    remaining: int
    ewma_volume: float
    streak: int
    best_bid: int | None
    best_ask: int | None
    working_price: int | None
    working_qty: int | None


@dataclass(frozen=True)
class PolicyAction:
    kind: str  # "place" | "reprice" | "cancel" | "idle"
    price: int = 0
    quantity: int = 0


@dataclass
class _PolicyState:
    remaining: int
    ewma_volume: float = 0.0
    streak: int = 0
    filled_units: int = 0


class AdaptiveExecutionPolicy:
    """Participation-targeted liquidation with deadline/shortfall escalation.

    Deterministic pure function of the observation stream: chunk size
    ``clamp(round(participation * ewma_volume), 1, min(chunk_max, q))``;
    escalation to marketable-at-the-bid once the behind-schedule ratio
    u = (remaining/Q) * (T / rounds_left) crosses ``urgency_cross`` (1 on
    schedule, > 1 behind) or the passive fill streak exceeds the bound;
    passive otherwise (join the ask, improve one tick when the spread
    admits it). A working order whose target price is unchanged is HELD:
    replacing at the same price only forfeits FIFO queue priority (the
    floor-pinned smoke showed an every-round reprice starve the policy of
    fills behind an ever-growing background queue). The volume EWMA is the
    feedback channel: DGP arm feeds it realized increments, SIM arm feeds
    it model-decoded increments.
    """

    def __init__(self, config: PolicyConfig) -> None:
        self.cfg = config
        self.state = _PolicyState(remaining=config.q_total)

    def urgency(self, obs: Observation) -> float:
        if obs.rounds_left <= 0:
            return float("inf")
        share_left = obs.remaining / self.cfg.q_total
        time_pressure = self.cfg.n_rounds / obs.rounds_left
        return share_left * time_pressure

    def decide(self, obs: Observation) -> PolicyAction:
        if obs.remaining <= 0:
            return PolicyAction("cancel" if obs.working_qty else "idle")
        chunk = max(
            1,
            min(
                self.cfg.chunk_max,
                obs.remaining,
                round(self.cfg.participation * obs.ewma_volume),
            ),
        )
        escalate = (
            self.urgency(obs) >= self.cfg.urgency_cross
            or obs.streak >= self.cfg.streak_escalate
        )
        bid, ask = obs.best_bid, obs.best_ask
        if escalate and bid is not None:
            price = bid  # marketable sell
        elif ask is not None:
            spread = (ask - bid) if bid is not None else 2
            price = ask - 1 if spread >= 2 else ask
        elif bid is not None:
            price = bid + 1
        else:
            price = (PRICE_BANDS[0] + PRICE_BANDS[1]) // 2
        price = max(PRICE_BANDS[0], min(PRICE_BANDS[1], price))
        if obs.working_qty:
            if price == obs.working_price:
                return PolicyAction("idle", price, chunk)  # hold queue priority
            return PolicyAction("reprice", price, chunk)
        return PolicyAction("place", price, chunk)

    def update(
        self, feedback_volume: float, filled: int, *, count_streak: bool = True
    ) -> None:
        """Consume the round's feedback increment and own fills.

        ``count_streak=False`` is the warmup mode: the EWMA warms on
        pre-trade realized volume without accruing an unfilled streak.
        """

        alpha = self.cfg.ewma_alpha
        self.state.ewma_volume = (
            (1.0 - alpha) * self.state.ewma_volume + alpha * float(feedback_volume)
        )
        if filled > 0:
            self.state.streak = 0
            self.state.filled_units += filled
            self.state.remaining = max(0, self.state.remaining - filled)
        elif count_streak:
            self.state.streak += 1


# ─────────────────────────────────────────────────────────────────────────────
# Feedback providers (the sim-in-loop channel: one scalar, volume increment)
# ─────────────────────────────────────────────────────────────────────────────


class DgpFeedback:
    """Realized conserving-channel volume increment of the last round."""

    needs_features: bool = False

    def __init__(self) -> None:
        self._latest: int = 0

    def consume_round(
        self, features: Any, x_pre: tuple[int, int], volume_increment: int
    ) -> None:
        self._latest = volume_increment

    def latest(self) -> int:
        return self._latest


class StubFeedback:
    """Deterministic distortion for tests/smoke (volume estimate multiplier)."""

    needs_features: bool = False

    def __init__(self, base: DgpFeedback, volume_multiplier: float) -> None:
        self._base = base
        self._mult = volume_multiplier

    def consume_round(
        self, features: Any, x_pre: tuple[int, int], volume_increment: int
    ) -> None:
        self._base.consume_round(features, x_pre, volume_increment)

    def latest(self) -> int:
        return max(0, round(self._base.latest() * self._mult))


def _build_mechanism(seed_root: int, train_config: Any) -> Any:
    """Through-M inference mechanism at the seed's own draw-1 substream."""

    from ecomd.training.train_fact_surrogate import build_inference_mechanism

    return build_inference_mechanism(
        train_config, seed_root=seed_root, draw_index=INFERENCE_DRAW_INDEX
    )


def build_model_feedback(
    model: Any,
    *,
    coordinate: str,
    inference_enforcement: str,
    seed_root: int,
    train_config: Any | None = None,
) -> _ModelFeedback:
    """Wrap a trained (or throwaway) L1/L2 model as the feedback provider.

    ``train_config`` defaults to the smoke default (MIRROR backend); the
    scheduled op session must pass the checkpoint's config with the
    ENGINE_BRIDGE backend selected (guarded in run_reflexive_session).
    """

    if train_config is None:
        from ecomd.training.train_fact_surrogate import FactSurrogateTrainConfig

        train_config = FactSurrogateTrainConfig()
    mechanism = (
        _build_mechanism(seed_root, train_config)
        if inference_enforcement == "through_m"
        else None
    )
    return _ModelFeedback(model, coordinate, inference_enforcement, mechanism)


class _ModelFeedback:
    needs_features: bool = True

    def __init__(
        self,
        model: Any,
        coordinate: str,
        inference_enforcement: str,
        mechanism: Any,
    ) -> None:
        if coordinate not in ("absolute", "increment"):
            raise ValueError(f"unknown coordinate {coordinate!r}")
        if inference_enforcement not in ("raw", "through_m"):
            raise ValueError(f"unknown enforcement {inference_enforcement!r}")
        if inference_enforcement == "through_m" and mechanism is None:
            raise ValueError("through_m feedback requires a mechanism")
        model.eval()
        self._model = model
        self._coordinate = coordinate
        self._enforcement = inference_enforcement
        self._mechanism = mechanism
        self._is_l2 = model.__class__.__name__ == "RecurrentFactSurrogate"
        self._h: Any = None
        self._latest: int = 0

    def _mechanism_volume(self, flow_1d: Any, demand_scalar: Any) -> int:
        allocation = self._mechanism(flow_1d, int(demand_scalar.detach().item()))
        return max(0, round(float(allocation.sum().detach().item())))

    def consume_round(
        self, features: Any, x_pre: tuple[int, int], volume_increment: int
    ) -> None:
        import torch

        with torch.no_grad():
            estimate = self._decode(features, x_pre, torch)
        self._latest = max(0, round(float(estimate)))

    def _decode(self, features: Any, x_pre: tuple[int, int], torch: Any) -> Any:
        model = self._model
        if self._is_l2:
            if self._h is None:
                self._h = model.init_hidden(1)
            # Pre-round decode for THIS round from h (features < t), then
            # the hidden state consumes features_t (the L2 grammar).
            if self._enforcement == "through_m":
                from ecomd.models.fact_surrogate import lattice_ste

                flow = lattice_ste(torch.nn.functional.softplus(model.flow_head(self._h)))
                demand = torch.clamp(
                    lattice_ste(
                        torch.nn.functional.softplus(model.demand_head(self._h).squeeze(-1))
                    ),
                    min=1.0,
                )
                self._h = model.cell(features.view(1, -1), self._h)
                return self._mechanism_volume(flow[0], demand[0])
            head = model.inc_head(self._h) if self._coordinate == "increment" else (
                model.abs_head(self._h) - torch.tensor([[x_pre[0], x_pre[1]]])
            )
            self._h = model.cell(features.view(1, -1), self._h)
            return head[0, 0]
        from ecomd.models.fact_surrogate import FactSurrogateBatch

        # channels is shape-validated but unread at T=1 (pre_round_base is
        # channels_init for a single-round batch); x_pre fills it.
        batch = FactSurrogateBatch(
            features=features.view(1, 1, -1),
            channels=torch.tensor([[[x_pre[0], x_pre[1]]]], dtype=torch.float32),
            slot_prices=torch.zeros(1, 1, model.cfg.n_slots),
            channels_init=torch.tensor([[x_pre[0], x_pre[1]]], dtype=torch.float32),
        )
        if self._enforcement == "through_m":
            out = model(batch)
            return self._mechanism_volume(out.flow[0, 0], out.demand[0, 0])
        out = model(batch)
        if self._coordinate == "increment":
            return out.inc_channels[0, 0, 0]
        return out.abs_channels[0, 0, 0] - float(x_pre[0])

    def latest(self) -> int:
        return self._latest


# ─────────────────────────────────────────────────────────────────────────────
# Session runner
# ─────────────────────────────────────────────────────────────────────────────


def _import_lab_asset(module_name: str) -> Any:
    """Lazy access to scripts/lab_asset (campaign._e2_module precedent)."""

    repo_root = Path(__file__).resolve().parents[2]
    scripts_dir = str(repo_root / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import importlib

    return importlib.import_module(module_name)


def _best(book: dict[int, Any], is_bid: bool) -> int | None:
    return (max(book) if is_bid else min(book)) if book else None


def _mid(bid: int | None, ask: int | None) -> float:
    if bid is None and ask is None:
        return float((PRICE_BANDS[0] + PRICE_BANDS[1]) / 2)
    if bid is None:
        assert ask is not None
        return float(ask)
    if ask is None:
        return float(bid)
    return (bid + ask) / 2.0


@dataclass
class _OwnFills:
    units: int = 0
    cash: int = 0
    passive_units: int = 0
    aggressive_units: int = 0
    weighted_price_sum: float = 0.0
    rounds: list[int] = field(default_factory=list)
    pairs: list[tuple[int, int]] = field(default_factory=list)

    def add(self, price: int, quantity: int, passive: bool, round_index: int) -> None:
        self.units += quantity
        self.cash += price * quantity
        if passive:
            self.passive_units += quantity
        else:
            self.aggressive_units += quantity
        self.weighted_price_sum += price * quantity
        self.rounds.append(round_index)
        self.pairs.append((price, quantity))


def _background_event(
    engine: Any, rng: random.Random, t: int, event_id: int, quantity_max: int
) -> None:
    """One zero-intelligence background event (robot_pilot rate structure).

    Quantities are drawn ~ U{1..quantity_max} (multi-unit, matching the F_exec
    corpus DGP's 2-5 range) so realized per-round volume sits on the corpus
    scale the deployed simulators were trained on. Background actors manage
    only their OWN resting orders (cancel/replace candidates are filtered to
    BG_ACTORS); the policy's orders are never touched by background flow.
    """

    schema = _import_lab_asset("lab_asset.schema")

    def quantity() -> int:
        return 1 + rng.randrange(quantity_max)

    bb = _best(engine.bids, True)
    ba = _best(engine.asks, False)
    spread = max((ba - bb) if (bb is not None and ba is not None) else 2, 1)
    resting_count = sum(
        len(orders)
        for book in (engine.bids, engine.asks)
        for orders in book.values()
        if orders
    )
    arrival_rate = 1.0 * (1.0 + spread)
    market_rate = 0.6
    replace_rate = 0.15 * resting_count
    cancel_rate = 0.05 * resting_count
    total = arrival_rate + market_rate + replace_rate + cancel_rate
    u = rng.random() * total
    clocks = schema.ThreeClocks(t, t, t)
    if u < arrival_rate:
        is_bid = rng.random() < 0.5
        r = rng.random()
        if is_bid:
            # Empty-side anchoring uses the opposite best (2 ticks inside),
            # never a fixed level: a fixed anchor above a floor-pinned ask
            # makes every incoming bid cross and the book collapse one-sided.
            base = bb if bb is not None else ((ba - 2) if ba is not None else 99)
            price = base + 1 if r < 0.30 else (base if r < 0.80 else base - 1)
        else:
            base = ba if ba is not None else ((bb + 2) if bb is not None else 101)
            price = base - 1 if r < 0.30 else (base if r < 0.80 else base + 1)
        engine.submit(
            schema.OrderRequest(
                event_id=event_id,
                actor=BG_ACTORS[rng.randrange(N_BG_ACTORS)],
                client_order_id=f"BG{event_id:09d}",
                side=schema.Side.BID if is_bid else schema.Side.ASK,
                price=max(PRICE_BANDS[0], min(PRICE_BANDS[1], price)),
                quantity=quantity(),
                clocks=clocks,
                round_id=t,
            )
        )
    elif u < arrival_rate + market_rate:
        is_buy = rng.random() < 0.5
        if is_buy and ba is not None:
            engine.submit(
                schema.OrderRequest(
                    event_id=event_id,
                    actor=BG_ACTORS[rng.randrange(N_BG_ACTORS)],
                    client_order_id=f"BG{event_id:09d}",
                    side=schema.Side.BID,
                    price=ba + 2,
                    quantity=quantity(),
                    clocks=clocks,
                    round_id=t,
                )
            )
        elif not is_buy and bb is not None:
            engine.submit(
                schema.OrderRequest(
                    event_id=event_id,
                    actor=BG_ACTORS[rng.randrange(N_BG_ACTORS)],
                    client_order_id=f"BG{event_id:09d}",
                    side=schema.Side.ASK,
                    price=bb - 2,
                    quantity=quantity(),
                    clocks=clocks,
                    round_id=t,
                )
            )
    else:
        resting: list[tuple[int, str, int, int, str]] = [
            (price, oid, actor, qty, side_value)
            for side_value, book in (("B", engine.bids), ("S", engine.asks))
            for price, orders in book.items()
            for oid, actor, qty in orders
            if actor in BG_ACTORS
        ]
        if not resting:
            return
        _price, oid, owner, _qty, side_value = resting[rng.randrange(len(resting))]
        if u < arrival_rate + market_rate + replace_rate:
            engine.replace(
                schema.ReplaceRequest(
                    event_id=event_id,
                    actor=owner,
                    replaces_order_id=oid,
                    client_order_id=f"BR{event_id:09d}",
                    side=schema.Side.BID if side_value == "B" else schema.Side.ASK,
                    price=max(
                        PRICE_BANDS[0],
                        min(
                            PRICE_BANDS[1],
                            _price + (1 if rng.random() < 0.5 else -1),
                        ),
                    ),
                    quantity=quantity(),
                    clocks=clocks,
                    round_id=t,
                )
            )
        else:
            engine.cancel(
                schema.CancelRequest(
                    event_id=event_id,
                    actor=owner,
                    order_id=oid,
                    clocks=clocks,
                    round_id=t,
                )
            )


def _check_unlock(unlock_file: Path) -> None:
    """Firewall 2: the four published analyzer hashes must be presented."""

    hashes = [line.strip() for line in unlock_file.read_text().splitlines() if line.strip()]
    if len(hashes) < UNLOCK_HASH_LINES or any(
        len(h) != 64 or any(c not in "0123456789abcdef" for c in h) for h in hashes
    ):
        raise SystemExit(
            f"unlock file {unlock_file} must carry {UNLOCK_HASH_LINES} sha256 "
            "hex lines (the published block-analyzer analysis-JSON hashes; "
            "C12 temporal firewall)"
        )


def _check_out_dir(out_dir: Path, smoke: bool) -> None:
    parts = {p.lower() for p in out_dir.parts}
    if "reflexive" not in parts:
        raise SystemExit(
            f"reflexive firewall 1: output path {out_dir} lacks a 'reflexive' "
            "path component (records must live in the reflexive namespace)"
        )
    if smoke and "smoke" not in parts:
        raise SystemExit(
            f"smoke sessions must write under a 'smoke' path component: {out_dir}"
        )


def _check_record(record: Mapping[str, Any]) -> None:
    if record.get("exploratory") is not True or record.get("reflexive") is not True:
        raise SystemExit("record missing namespace fields (firewall 1)")
    if record.get("label") != REFLEXIVE_LABEL:
        raise SystemExit("record missing the mandatory label (firewall 3)")


def validate_namespace(records: Sequence[Mapping[str, Any]]) -> None:
    """Firewall conformance check over emitted records (fail loudly)."""

    for record in records:
        if not str(record.get("run_id", "")).startswith(RUN_ID_PREFIX):
            raise SystemExit(f"run_id missing the {RUN_ID_PREFIX} prefix")
        _check_record(record)


def run_reflexive_session(
    *,
    seed: int,
    lineage: str,
    cell_id: str,
    arm: str,
    feedback: Any = None,
    checkpoint_ref: str | None = None,
    config: PolicyConfig | None = None,
    out_dir: Path | None = None,
    smoke: bool = False,
    unlock_file: Path | None = None,
    train_config: Any | None = None,
) -> dict[str, Any]:
    """One (lineage, cell, arm, seed) reflexive session.

    ``feedback``: DgpFeedback for arm="dgp"; a build_model_feedback provider
    for arm="sim". ``smoke`` bypasses the unlock gate but refuses trained
    checkpoints and requires a smoke output path.
    """

    cfg = config or PolicyConfig()
    cell = CELLS.get(cell_id)
    if cell is None:
        raise SystemExit(f"unknown cell {cell_id!r}; expected one of {sorted(CELLS)}")
    if lineage not in REFLEXIVE_SEEDS:
        raise SystemExit(f"unknown lineage {lineage!r}")
    if seed not in REFLEXIVE_SEEDS[lineage]:
        raise SystemExit(
            f"seed {seed} outside the Annex B(d) reflexive subset for {lineage}"
        )
    if arm not in ("dgp", "sim"):
        raise SystemExit(f"unknown arm {arm!r}")
    if arm == "sim" and feedback is None:
        raise SystemExit("arm='sim' requires a feedback provider")
    if arm == "dgp" and feedback is None:
        feedback = DgpFeedback()
    if not smoke:
        if unlock_file is None:
            raise SystemExit(
                "non-smoke reflexive execution requires unlock_file carrying "
                "the four published analyzer hashes (C12 temporal firewall)"
            )
        _check_unlock(Path(unlock_file))
        if arm == "sim" and cell.inference_enforcement == "through_m":
            backend_name = getattr(
                getattr(train_config, "mechanism_backend", None), "name", "ABSENT"
            )
            if backend_name != "ENGINE_BRIDGE":
                raise SystemExit(
                    "non-smoke through-M sim arm requires the ENGINE_BRIDGE "
                    f"mechanism backend (got {backend_name}); production arms "
                    "never run MIRROR"
                )
    elif checkpoint_ref is not None:
        raise SystemExit(
            "smoke sessions cannot reference trained checkpoints "
            "(engineering-only; the scheduled cell needs the unlock gate)"
        )
    assert_seed_disjointness(seed)
    if out_dir is not None:
        out_dir = Path(out_dir)
        _check_out_dir(out_dir, smoke)

    matching = _import_lab_asset("lab_asset.matching")
    schema = _import_lab_asset("lab_asset.schema")
    replay = _import_lab_asset("lab_asset.replay").replay
    run_id = f"{RUN_ID_PREFIX}{lineage}-{cell.r_label}-{arm}-{seed}" + (
        "-SMOKE" if smoke else ""
    )
    bg_rng = random.Random(reflexive_seed(seed, "background"))
    actors = (*BG_ACTORS, POLICY_ACTOR)
    prestate = schema.SessionPrestate(
        session_id=run_id,
        seed=seed,
        allocation_rule=schema.AllocationRule.FIFO,
        initial_cash={a: 10_000_000 for a in actors},
        initial_inventory={a: 100_000 for a in actors},
        price_bands=PRICE_BANDS,
        actors=actors,
    )
    engine = matching.ReferenceEngine(prestate)
    event_id = 0

    def next_event_id() -> int:
        nonlocal event_id
        event_id += 1
        return event_id

    policy = AdaptiveExecutionPolicy(cfg)
    fills = _OwnFills()
    working: dict[str, Any] | None = None  # {"order_id", "price", "qty"}
    last_px_price = 0
    channel_state = [0, 0]  # true (volume_cum, cash_cum) from session start
    tape_mark = 0  # tape records already consumed by the round-close scan

    fexec: Any = None
    if getattr(feedback, "needs_features", False):
        from ecomd.models.fact_surrogate import fexec_round_features

        fexec = fexec_round_features

    def close_round(t: int, *, count_streak: bool = True) -> None:
        """Scan the round's new tape records: project F_exec payloads,
        channel increments, own fills; feed the feedback provider; update
        the policy. Every record past tape_mark belongs to round t by
        construction (only this round's actions were emitted since)."""

        nonlocal working, tape_mark
        payloads: list[dict[str, object]] = []
        volume_inc = 0
        cash_inc = 0
        own_filled = 0
        for record in engine.tape[tape_mark:]:
            if record.event_type == schema.EventType.EXECUTION:
                payload = record.payload
                execution = payload["execution"]
                quantity = execution["quantity"]
                price = execution["price"]
                volume_inc += quantity
                cash_inc += price * quantity
                payloads.append(payload)
                own_side = execution["aggressor_actor"] == POLICY_ACTOR or (
                    execution["maker_actor"] == POLICY_ACTOR
                )
                if own_side:
                    passive = execution["maker_actor"] == POLICY_ACTOR
                    fills.add(price, quantity, passive=passive, round_index=t)
                    own_filled += quantity
                    if passive and working is not None and execution.get(
                        "maker_order_id"
                    ) == working["order_id"]:
                        working["qty"] = max(0, working["qty"] - quantity)
                        if working["qty"] == 0:
                            working = None
            elif record.event_type == schema.EventType.ORDER_ACCEPTED:
                payload = record.payload
                if str(payload.get("client_order_id", "")).startswith("PX"):
                    working = {
                        "order_id": payload["order_id"],
                        "price": last_px_price,
                        "qty": payload.get("resting_quantity", 0),
                    }
        tape_mark = len(engine.tape)
        features = fexec(payloads) if fexec is not None else None
        x_pre = (channel_state[0], channel_state[1])
        channel_state[0] += volume_inc
        channel_state[1] += cash_inc
        feedback.consume_round(features, x_pre, volume_inc)
        policy.update(feedback.latest(), own_filled, count_streak=count_streak)

    # Warmup: background flow only; providers and the volume EWMA consume
    # the pre-trade rounds (deployed context), streaks do not accrue.
    for t in range(cfg.warmup_rounds):
        for _ in range(cfg.bg_events_per_round):
            _background_event(
                engine, bg_rng, t, next_event_id(), cfg.bg_quantity_max
            )
        close_round(t, count_streak=False)

    arrival_mid = _mid(_best(engine.bids, True), _best(engine.asks, False))

    total_rounds = cfg.warmup_rounds + cfg.n_rounds
    for t in range(cfg.warmup_rounds, total_rounds):
        obs = Observation(
            round_index=t - cfg.warmup_rounds,
            rounds_left=total_rounds - t,
            remaining=policy.state.remaining,
            ewma_volume=policy.state.ewma_volume,
            streak=policy.state.streak,
            best_bid=_best(engine.bids, True),
            best_ask=_best(engine.asks, False),
            working_price=working["price"] if working else None,
            working_qty=working["qty"] if working else None,
        )
        action = policy.decide(obs)
        clocks = schema.ThreeClocks(t, t, t)
        if action.kind == "place":
            eid = next_event_id()
            last_px_price = action.price
            working = None
            engine.submit(
                schema.OrderRequest(
                    event_id=eid,
                    actor=POLICY_ACTOR,
                    client_order_id=f"PX{eid:09d}",
                    side=schema.Side.ASK,
                    price=action.price,
                    quantity=action.quantity,
                    clocks=clocks,
                    round_id=t,
                )
            )
        elif action.kind == "reprice" and working is not None:
            old_id = working["order_id"]
            eid = next_event_id()
            last_px_price = action.price
            engine.replace(
                schema.ReplaceRequest(
                    event_id=eid,
                    actor=POLICY_ACTOR,
                    replaces_order_id=old_id,
                    client_order_id=f"PX{eid:09d}",
                    side=schema.Side.ASK,
                    price=action.price,
                    quantity=action.quantity,
                    clocks=clocks,
                    round_id=t,
                )
            )
            # Adopt the replacement's new order id / resting quantity.
            for tape_entry in reversed(engine.tape):
                if (
                    tape_entry.event_type == schema.EventType.ORDER_REPLACED
                    and tape_entry.payload.get("replaces_order_id") == old_id
                ):
                    payload = tape_entry.payload
                    working = {
                        "order_id": payload["order_id"],
                        "price": action.price,
                        "qty": payload.get("resting_quantity", 0),
                    }
                    if working["qty"] == 0:
                        working = None
                    break
        elif action.kind == "cancel" and working is not None:
            engine.cancel(
                schema.CancelRequest(
                    event_id=next_event_id(),
                    actor=POLICY_ACTOR,
                    order_id=working["order_id"],
                    clocks=clocks,
                    round_id=t,
                )
            )
            working = None
        for _ in range(cfg.bg_events_per_round):
            _background_event(
                engine, bg_rng, t, next_event_id(), cfg.bg_quantity_max
            )
        close_round(t)
        if policy.state.remaining == 0 and working is None:
            break

    engine.finish()
    report = replay(prestate, engine.tape)
    tape_digest = hashlib.sha256(
        b"".join(
            schema.record_to_json(record).encode("utf-8") for record in engine.tape
        )
    ).hexdigest()
    terminal_mid = _mid(_best(engine.bids, True), _best(engine.asks, False))
    shortfall = sum(
        (arrival_mid - price) * quantity for price, quantity in fills.pairs
    )
    unfilled = cfg.q_total - fills.units
    unfilled_marked = (arrival_mid - terminal_mid) * unfilled
    rounds_to_complete = (
        max(fills.rounds) - cfg.warmup_rounds + 1 if fills.rounds else cfg.n_rounds
    )
    record: dict[str, Any] = {
        "schema": SESSION_SCHEMA,
        "run_id": run_id,
        "exploratory": True,
        "reflexive": True,
        "smoke": bool(smoke),
        "label": REFLEXIVE_LABEL,
        "lineage": lineage,
        "cell": {
            "r_label": cell.r_label,
            "arm_id": cell.arm_id,
            "inference_enforcement": cell.inference_enforcement,
            "coordinate": cell.coordinate,
        },
        "seed": seed,
        "seed_namespace": SEED_NAMESPACES[lineage],
        "arm": arm,
        "checkpoint_ref": checkpoint_ref,
        "feedback": {
            "channel": "volume_increment",
            "inference_draw_index": (
                INFERENCE_DRAW_INDEX if cell.inference_enforcement == "through_m" else None
            ),
            "mechanism_backend": (
                str(getattr(train_config, "mechanism_backend", None))
                if arm == "sim" and cell.inference_enforcement == "through_m"
                else None
            ),
        },
        "policy": {
            "q_total": cfg.q_total,
            "n_rounds": cfg.n_rounds,
            "warmup_rounds": cfg.warmup_rounds,
            "bg_events_per_round": cfg.bg_events_per_round,
            "bg_quantity_max": cfg.bg_quantity_max,
            "participation": cfg.participation,
            "chunk_max": cfg.chunk_max,
            "urgency_cross": cfg.urgency_cross,
            "streak_escalate": cfg.streak_escalate,
            "ewma_alpha": cfg.ewma_alpha,
        },
        "engine": {
            "allocation_rule": "fifo",
            "price_bands": list(PRICE_BANDS),
            "n_bg_actors": N_BG_ACTORS,
            "background_seed": reflexive_seed(seed, "background"),
        },
        "metrics": {
            "implementation_shortfall_ticks": shortfall,
            "unfilled_marked_shortfall_ticks": unfilled_marked,
            "avg_fill_price": (
                fills.weighted_price_sum / fills.units if fills.units else None
            ),
            "cash_received": fills.cash,
            "filled_units": fills.units,
            "unfilled_units": unfilled,
            "passive_fill_units": fills.passive_units,
            "aggressive_fill_units": fills.aggressive_units,
            "rounds_to_complete": rounds_to_complete,
            "arrival_mid": arrival_mid,
            "terminal_mid": terminal_mid,
        },
        "replay_ok": bool(report.ok),
        "tape_length": len(engine.tape),
        "tape_sha256": tape_digest,
    }
    _check_record(record)
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{run_id}.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n"
        )
    return record


# ─────────────────────────────────────────────────────────────────────────────
# Descriptive summary (firewall 3: no inference, mandatory label)
# ─────────────────────────────────────────────────────────────────────────────


def summarize(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Per (lineage, cell): paired per-seed sim-minus-dgp gaps + descriptive
    mean/min/max. No intervals, no tests, no classifications (firewall 3)."""

    validate_namespace(records)
    by_key: dict[tuple[str, str], dict[int, dict[str, Any]]] = {}
    for record in records:
        if record.get("smoke"):
            continue
        key = (record["lineage"], record["cell"]["r_label"])
        by_key.setdefault(key, {}).setdefault(record["seed"], {})[record["arm"]] = record
    groups: dict[str, Any] = {}
    for (lineage, r_label), per_seed in sorted(by_key.items()):
        gaps: dict[str, list[float]] = {m: [] for m in DESCRIPTIVE_METRICS}
        complete = 0
        for _seed, arms in sorted(per_seed.items()):
            if "dgp" not in arms or "sim" not in arms:
                continue
            complete += 1
            for metric in DESCRIPTIVE_METRICS:
                dgp_value = arms["dgp"]["metrics"][metric]
                sim_value = arms["sim"]["metrics"][metric]
                if dgp_value is None or sim_value is None:
                    continue
                gaps[metric].append(float(sim_value) - float(dgp_value))
        groups[f"{lineage}|{r_label}"] = {
            "paired_seeds": complete,
            "gap_sim_minus_dgp": {
                metric: {
                    "mean": (sum(v) / len(v)) if v else None,
                    "min": min(v) if v else None,
                    "max": max(v) if v else None,
                }
                for metric, v in gaps.items()
            },
        }
    return {
        "schema": SUMMARY_SCHEMA,
        "exploratory": True,
        "reflexive": True,
        "label": REFLEXIVE_LABEL,
        "note": (
            "descriptive only — TRADES 2025 / DEX closed-loop 2026 paired-seed "
            "descriptive discipline; excluded from confirmatory inference"
        ),
        "groups": groups,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lineage", required=True, choices=sorted(REFLEXIVE_SEEDS))
    ap.add_argument("--cell", required=True, choices=sorted(CELLS))
    ap.add_argument("--arm", required=True, choices=["dgp", "sim"])
    ap.add_argument("--seeds", required=True, help="comma-separated seed integers")
    ap.add_argument("--rounds", type=int, default=PolicyConfig.n_rounds)
    ap.add_argument("--q-total", type=int, default=PolicyConfig.q_total)
    ap.add_argument("--warmup", type=int, default=PolicyConfig.warmup_rounds)
    ap.add_argument(
        "--bg-events", type=int, default=PolicyConfig.bg_events_per_round
    )
    ap.add_argument(
        "--bg-qty-max", type=int, default=PolicyConfig.bg_quantity_max
    )
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--unlock-file", type=Path, default=None)
    ap.add_argument(
        "--untrained-model",
        choices=["l1", "l2"],
        default=None,
        help="smoke-only: run the sim arm against an untrained throwaway model",
    )
    args = ap.parse_args(argv)

    if args.arm == "sim" and not args.smoke and args.untrained_model:
        raise SystemExit(
            "--untrained-model is smoke-only (load a checkpoint at the op session)"
        )

    seeds = [int(s) for s in args.seeds.split(",")]
    config = PolicyConfig(
        q_total=args.q_total,
        n_rounds=args.rounds,
        warmup_rounds=args.warmup,
        bg_events_per_round=args.bg_events,
        bg_quantity_max=args.bg_qty_max,
    )
    records: list[dict[str, Any]] = []
    for seed in seeds:
        feedback: Any = None
        cell = CELLS[args.cell]
        if args.arm == "sim":
            if args.untrained_model is None:
                raise SystemExit(
                    "sim arm needs --untrained-model (smoke) or a checkpoint "
                    "loader at the scheduled op session"
                )
            if args.untrained_model == "l1":
                from ecomd.models.l1_coordinate_heads import L1CoordinateHeads

                model: Any = L1CoordinateHeads()  # throwaway init (smoke only)
            else:
                from ecomd.models.fact_surrogate import RecurrentFactSurrogate

                model = RecurrentFactSurrogate()  # throwaway init (smoke only)
            feedback = build_model_feedback(
                model,
                coordinate=cell.coordinate,
                inference_enforcement=cell.inference_enforcement,
                seed_root=seed,
            )
        records.append(
            run_reflexive_session(
                seed=seed,
                lineage=args.lineage,
                cell_id=args.cell,
                arm=args.arm,
                feedback=feedback,
                config=config,
                out_dir=args.out_dir,
                smoke=args.smoke,
                unlock_file=args.unlock_file,
            )
        )
    if args.smoke:
        for record in records:
            metrics = record["metrics"]
            print(
                f"{record['run_id']}: filled={metrics['filled_units']} "
                f"unfilled={metrics['unfilled_units']} "
                f"passive={metrics['passive_fill_units']} "
                f"aggressive={metrics['aggressive_fill_units']} "
                f"replay_ok={record['replay_ok']}"
            )
    summary = summarize(records)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
