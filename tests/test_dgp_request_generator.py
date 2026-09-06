"""Tests for the E-2 M0/M1-lumpable DGP request generator.

CPU spot-checks only (PI rule 2026-09-06): every episode here is 3-6 rounds
and the whole file runs in seconds. No GPU, no training, no batch batteries.

Coverage map (spec: prereg v2 C2(a)/C4/D1_05; simulator contracts §2.4):
substream naming and spawn-equivalence; determinism / byte-identity; exact
request-level CRN across allocation kernels; M0/M1 policy-surface lumpability;
pop_2x / tick_2x axis knobs; hand-checked episode grammar; preflight
compatibility (run_preflight aliased onto this module); D2 synthetic-wrapper
conservation/replay; M0 == M1 stream identity (the R2-C anchor).
"""

from __future__ import annotations

import itertools
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
for _entry in (str(REPO_ROOT / "scripts"), str(REPO_ROOT)):
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

import lab_asset.dgp_request_generator as gen  # noqa: E402
from lab_asset.matching import EventType, ReferenceEngine  # noqa: E402
from lab_asset.replay import replay  # noqa: E402
from lab_asset.schema import AllocationRule  # noqa: E402

SMALL = dict(n_rounds=6)


def canonical_payload(stream: gen.EpisodeStream, *drop: str) -> dict[str, object]:
    payload = json.loads(gen.episode_canonical_json(stream))
    for key in drop:
        payload.pop(key)
    return payload


def run_engine(stream: gen.EpisodeStream, rule: AllocationRule, draw_seed: int) -> ReferenceEngine:
    engine = ReferenceEngine(gen.build_prestate(stream, rule, draw_seed))
    for request in gen.order_requests(stream):
        engine.submit(request)
    engine.finish()
    return engine


def tape_rejection_count(engine: ReferenceEngine) -> int:
    return sum(
        record.event_type is EventType.ORDER_REJECTED for record in engine.tape
    )


# ── 1. RNG tree: named substreams, spawn equivalence, disjointness ──────────


def test_named_substream_seed_matches_spawn_derivation() -> None:
    root = 11_007
    children = np.random.SeedSequence(entropy=root).spawn(len(gen.SUBSTREAM_NAMES))
    for index, name in enumerate(gen.SUBSTREAM_NAMES):
        expected = int(children[index].generate_state(1, dtype=np.uint32)[0])
        assert gen.named_substream_seed(root, name) == expected


def test_episode_seed_sequence_is_data_child() -> None:
    root = 11_013
    data_child = np.random.SeedSequence(entropy=root, spawn_key=(0,))
    episode_children = data_child.spawn(8)
    for episode in (0, 1, 7):
        mine = gen.episode_seed_sequence(root, episode).generate_state(4, dtype=np.uint32)
        expected = episode_children[episode].generate_state(4, dtype=np.uint32)
        assert list(mine) == list(expected)


def test_substream_seeds_are_disjoint_and_validated() -> None:
    seeds = [
        gen.named_substream_seed(root, name)
        for root in (11_000, 12_000, 31_000)
        for name in gen.SUBSTREAM_NAMES
    ]
    assert len(set(seeds)) == len(seeds)
    with pytest.raises(ValueError):
        gen.named_substream_seed(11_000, "kernel:1")
    with pytest.raises(ValueError):
        gen.named_substream_seed(-1, "data")
    with pytest.raises(ValueError):
        gen.episode_seed_sequence(11_000, -1)


# ── 2. Determinism and config surface ───────────────────────────────────────


def test_generate_episode_is_deterministic() -> None:
    cfg = gen.DGPConfig(**SMALL)
    first = gen.generate_episode(11_001, 0, cfg)
    second = gen.generate_episode(11_001, 0, cfg)
    assert gen.episode_canonical_json(first) == gen.episode_canonical_json(second)
    third = gen.generate_episode(11_001, 1, cfg)
    assert gen.episode_canonical_json(first) != gen.episode_canonical_json(third)


def test_config_mapping_round_trip_and_fingerprint() -> None:
    cfg = gen.DGPConfig(**SMALL)
    rebuilt = gen.config_from_mapping(gen.config_to_mapping(cfg))
    assert gen.config_fingerprint(rebuilt) == gen.config_fingerprint(cfg)
    altered = replace(cfg, resting_add_rate=cfg.resting_add_rate + 0.1)
    assert gen.config_fingerprint(altered) != gen.config_fingerprint(cfg)
    with pytest.raises(ValueError):
        gen.config_from_mapping({"not_a_knob": 1})
    with pytest.raises(ValueError):
        gen.config_from_mapping({"n_makers": 1})


def test_build_episode_mapping_entry_matches_generate_episode() -> None:
    mapping = gen.config_to_mapping(gen.DGPConfig(**SMALL))
    via_mapping = gen.build_episode(11_002, 0, mapping)
    direct = gen.generate_episode(11_002, 0, gen.DGPConfig(**SMALL))
    assert gen.episode_canonical_json(via_mapping) == gen.episode_canonical_json(direct)


# ── 3. Exact request-level CRN across allocation kernels ────────────────────


@pytest.mark.parametrize("family", ["lab_asset", "garch_student_t5"])
def test_stream_is_kernel_blind(family: str) -> None:
    cfg = gen.DGPConfig(**SMALL, dgp_family=gen.DgpFamily(family))
    fifo = gen.generate_episode(11_003, 0, cfg, shadow_rule=AllocationRule.FIFO)
    ru = gen.generate_episode(
        11_003, 0, cfg, shadow_rule=AllocationRule.RANDOM_UNIT_WITHIN_PRICE
    )
    left = canonical_payload(fifo, "config_fingerprint")
    right = canonical_payload(ru, "config_fingerprint")
    assert left == right


def test_zero_rejections_under_both_arms() -> None:
    stream = gen.generate_episode(11_004, 0, gen.DGPConfig(**SMALL))
    assert stream.walk_plans, "episode should contain at least one walk"
    for rule in (AllocationRule.FIFO, AllocationRule.RANDOM_UNIT_WITHIN_PRICE):
        engine = run_engine(stream, rule, gen.derive_seed(11_004, "draw", 1, 0))
        assert tape_rejection_count(engine) == 0


# ── 4. M0/M1 policy surface ─────────────────────────────────────────────────


def test_project_own_invariant_refuses_makers_and_reads_aggregates_only() -> None:
    stream = gen.generate_episode(11_005, 0, gen.DGPConfig(**SMALL))
    engine = run_engine(stream, AllocationRule.FIFO, 7)
    maker = next(actor for actor, role in stream.actor_roles.items() if role == "maker")
    aggressor = next(
        actor for actor, role in stream.actor_roles.items() if role == "aggressor"
    )
    with pytest.raises(ValueError):
        gen.project_own_invariant(engine, maker)
    own = gen.project_own_invariant(engine, aggressor)
    assert own.actor == aggressor
    assert own.cash <= stream.initial_cash[aggressor]
    assert own.inventory == (
        stream.initial_inventory[aggressor] + own.units_bought - own.units_sold
    )
    view = gen.project_anonymous(engine)
    for _price, units in view.bids + view.asks:
        assert units > 0
    assert view.best_bid is None or view.best_ask is None or view.best_bid < view.best_ask


def test_own_invariant_state_is_kernel_invariant_for_aggressors() -> None:
    stream = gen.generate_episode(11_005, 1, gen.DGPConfig(**SMALL))
    aggressor = stream.walk_plans[0].aggressor_actor
    states = []
    for rule in (AllocationRule.FIFO, AllocationRule.RANDOM_UNIT_WITHIN_PRICE):
        engine = run_engine(stream, rule, 11)
        states.append(gen.project_own_invariant(engine, aggressor))
    assert states[0] == states[1]


# ── 5. C4 axes: pop_2x ──────────────────────────────────────────────────────


def test_pop_2x_regenerates_population_with_conservation() -> None:
    base = gen.DGPConfig(**SMALL)
    doubled = gen.config_for_axis(base, "pop_2x")
    assert doubled.n_makers == 2 * base.n_makers
    assert doubled.n_aggressors == 2 * base.n_aggressors
    assert doubled.maker_unit_budget == 2 * base.maker_unit_budget
    assert doubled.aggressor_unit_budget == 2 * base.aggressor_unit_budget
    assert doubled.replenish_orders == 2 * base.replenish_orders
    stream = gen.generate_episode(11_006, 0, doubled)
    assert len(stream.actors) == doubled.n_makers + doubled.n_aggressors == 32
    for rule in (AllocationRule.FIFO, AllocationRule.RANDOM_UNIT_WITHIN_PRICE):
        engine = run_engine(stream, rule, 3)
        assert tape_rejection_count(engine) == 0
        assert sum(engine.cash.values()) == sum(stream.initial_cash.values())
        assert sum(engine.inventory.values()) == sum(stream.initial_inventory.values())


# ── 6. C4 axes: tick_2x ─────────────────────────────────────────────────────


def test_tick_2x_is_homogeneous_price_dilation() -> None:
    base = gen.DGPConfig(**SMALL)
    coarser = gen.config_for_axis(base, "tick_2x")
    assert coarser.tick_factor == 2
    assert coarser.price_bands == (2 * base.reference_price - 2 * base.price_half_band,
                                   2 * base.reference_price + 2 * base.price_half_band)
    stream = gen.generate_episode(11_007, 0, coarser)
    prices = [order.price for order in stream.initial_book]
    prices += [int(spec["price"]) for spec in stream.requests if spec["kind"] == "submit"]
    assert prices and all(price % 2 == 0 for price in prices)
    lo, hi = stream.price_bands
    assert all(lo <= price <= hi for price in prices)
    with pytest.raises(ValueError):
        gen.config_for_axis(base, "pop_4x")


# ── 7. Hand-checked episode grammar ─────────────────────────────────────────


def test_episode_grammar_holds() -> None:
    stream = gen.generate_episode(11_008, 0, gen.DGPConfig(n_rounds=5))
    submits = [spec for spec in stream.requests if spec["kind"] == "submit"]
    assert stream.requests[-1] == {"kind": "finish"}
    assert len(stream.round_has_walk) == stream.n_rounds == 5
    assert len(stream.walk_plans) == sum(stream.round_has_walk) >= 1

    ticks = [int(spec["match_ts"]) for spec in submits]
    assert all(later > earlier for earlier, later in itertools.pairwise(ticks))
    max_arrival = max(order.arrival_clock for order in stream.initial_book)
    assert min(ticks) > max_arrival

    round_ids = [int(spec["round_id"]) for spec in submits]
    assert round_ids == sorted(round_ids)
    assert all(0 <= rid < stream.n_rounds for rid in round_ids)

    for plan in stream.walk_plans:
        spec = stream.requests[plan.request_index]
        assert spec["kind"] == "submit"
        assert spec["actor"] == plan.aggressor_actor
        assert stream.actor_roles[plan.aggressor_actor] == "aggressor"
        assert spec["price"] == plan.target_price
        assert spec["quantity"] == plan.swept_units + plan.v_star
        r_star = plan.r_star
        assert r_star >= gen.DGPConfig().min_pool_units
        assert 1 <= plan.v_star <= r_star - 1
        assert int(spec["round_id"]) == plan.round_id
    assert stream.predicted_cleared_volume == sum(
        plan.swept_units + plan.v_star for plan in stream.walk_plans
    )


def test_initial_pools_straddle_latency_window() -> None:
    stream = gen.generate_episode(11_008, 1, gen.DGPConfig(**SMALL))
    window = stream.latency_window
    pools: dict[tuple[str, int], list[int]] = {}
    for order in stream.initial_book:
        pools.setdefault((order.side.value, order.price), []).append(order.arrival_clock)
    assert pools
    for clocks in pools.values():
        assert len(clocks) >= 2
        assert min(clocks) <= window < max(clocks)


# ── 8. Preflight compatibility (evaluation-surface duck typing) ─────────────


def test_run_preflight_invariants_hold_against_this_generator() -> None:
    kp_dir = REPO_ROOT / "experiments" / "reexploration" / "k_preflight_20260906"
    if str(kp_dir) not in sys.path:
        sys.path.insert(0, str(kp_dir))
    import run_preflight

    original = run_preflight.dgp_stream
    run_preflight.dgp_stream = gen
    try:
        stream = gen.generate_episode(11_009, 0, gen.DGPConfig(n_rounds=5))
        result = run_preflight.run_episode_evaluations(stream, 2)
    finally:
        run_preflight.dgp_stream = original
    invariants = result["invariants"]
    assert invariants == {
        "fifo_payload_projection_identity": True,
        "request_boundary_aggregate_hash_identity": True,
        "ru_accepted_stream_identity": True,
        "cleared_volume_matches_plan": True,
        "zero_rejections": True,
        "ru_null_stat_draw_variance_zero": True,
    }


# ── 9. D2 synthetic wrappers: conservation, replay, exclusion ───────────────


@pytest.mark.parametrize("family_name", gen.D2_RUN_VARIANTS)
def test_d2_wrapper_conserves_and_replays(family_name: str) -> None:
    family = gen.DgpFamily(family_name)
    cfg = gen.DGPConfig(**SMALL, dgp_family=family)
    stream = gen.generate_episode(11_010, 0, cfg)
    again = gen.generate_episode(11_010, 0, cfg)
    assert gen.episode_canonical_json(stream) == gen.episode_canonical_json(again)
    assert stream.dgp_family == family_name
    assert stream.walk_plans

    for rule in (AllocationRule.FIFO, AllocationRule.RANDOM_UNIT_WITHIN_PRICE):
        engine = run_engine(stream, rule, 5)
        assert tape_rejection_count(engine) == 0
        assert sum(engine.cash.values()) == sum(stream.initial_cash.values())
        assert sum(engine.inventory.values()) == sum(stream.initial_inventory.values())
        report = replay(gen.build_prestate(stream, rule, 5), engine.tape)
        assert report.ok, str(report)


def test_d2_series_drives_walk_side() -> None:
    root, index = 11_011, 0
    family = gen.DgpFamily.GARCH_STUDENT_T5
    cfg = gen.DGPConfig(**SMALL, dgp_family=family)
    stream = gen.generate_episode(root, index, cfg)
    children = gen.episode_seed_sequence(root, index).spawn(2)
    series_seed = int(children[1].generate_state(1, dtype=np.uint32)[0])
    returns, _volume = gen.d2_series(family, cfg.n_rounds, series_seed, cfg.series_burn_in)
    for plan in stream.walk_plans:
        side = stream.requests[plan.request_index]["side"]
        expected = "B" if float(returns[plan.round_id]) >= 0.0 else "S"
        assert side == expected


def test_negative_jump_iid_is_defined_but_excluded() -> None:
    assert "negative_jump_iid" in gen.D2_SERIES_REGISTRY
    assert "negative_jump_iid" in gen.D2_NAMED_NOT_RUN
    assert "negative_jump_iid" not in gen.D2_RUN_VARIANTS
    with pytest.raises(ValueError):
        gen.DgpFamily("negative_jump_iid")

    class _Named:
        value = "negative_jump_iid"

    with pytest.raises(ValueError):
        gen.d2_series(_Named(), 4, 0, 0)  # type: ignore[arg-type]


# ── 10. M0 == M1 stream identity (the R2-C lumpability anchor) ──────────────


@pytest.mark.parametrize("family_name", ["lab_asset", "multiscale_logvol"])
def test_m0_and_m1_emit_identical_streams(family_name: str) -> None:
    cfg = gen.DGPConfig(**SMALL, dgp_family=gen.DgpFamily(family_name))
    m1 = gen.generate_episode(11_012, 0, replace(cfg, feedback_class=gen.FeedbackClass.M1))
    m0 = gen.generate_episode(11_012, 0, replace(cfg, feedback_class=gen.FeedbackClass.M0))
    assert m1.feedback_class == "m1" and m0.feedback_class == "m0"
    left = canonical_payload(m1, "feedback_class", "config_fingerprint")
    right = canonical_payload(m0, "feedback_class", "config_fingerprint")
    assert left == right
