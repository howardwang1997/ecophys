"""Conformance tests for the dual-hash-validated fiber resampler (PI decision D1_02).

Inventory (honest by construction):
  - every enriched random_unit fixture: dual-hash acceptance, aggregate-tape
    byte-invariance, >= 2 distinct accepted chains where combinatorics allow;
  - acceptance semantics under native RNG-state preservation: an attempt is
    accepted iff its ALLOCATION TRAJECTORY differs from the original, so the
    acceptance rate equals 1 - P_engine(original realized trajectory) — checked
    against that exact law-level prediction on every fixture;
  - injection-point ground truth: pinning the recorded selected_unit values
    reproduces each episode byte-exactly (hashes included);
  - the exhaustion stratum: count law is a point mass yet interleaving still
    yields distinct accepted chains;
  - fifo fixtures: the draw fiber is a point — the resampler correctly REFUSES
    (aggregate identical, state chain identical -> not accepted);
  - the frozen a2_exit_20260905 random_unit fixture: its only rationed level is
    a SINGLE-ORDER pool, so distinct resamples are impossible — asserted
    directly (all attempts rejected; only the exchangeable selected_unit
    annotation may differ), plus a strict xfail marker so the inventory
    expectation stays explicit;
  - exact-law conformance: sequential engine law == MVHG closed form (exact
    enumeration), engine-driven pinned enumeration on the small V* rungs, and
    seeded Monte-Carlo chi-square on the larger ones (tallied over ALL attempts
    — each an iid engine-law realization);
  - determinism (same base seed -> identical resample stream), read-only guard
    on the frozen bundle, and frozen prereg statement hash.

The frozen bundle experiments/lab_asset_a2/a2_exit_20260905/ is never written;
neither is the enrichment bundle.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lab_asset.fiber_resampler import (
    FIBER_RESAMPLER_SEED_NAMESPACE,
    PREREG_STATEMENT,
    NativeStatePreservingDrawSource,
    PinnedDrawSource,
    aggregate_projection,
    aggregate_tape_lines,
    allocation_counts,
    chi_square_gof,
    draw_seed_stream,
    dual_hash_report,
    enumerate_engine_count_law,
    first_execution_identity_divergence,
    load_episode,
    mvhg_pmf,
    order_sequence_probability,
    pool_orders_at_price,
    replay_loop_matches_validator,
    resample,
    resample_many,
    resample_pinned,
    sequential_draw_law,
    state_chain_digest,
    summarize,
)
from lab_asset.replay import regenerate
from lab_asset.schema import EventType, record_to_json, stable_hash

FROZEN_DIR = REPO_ROOT / "experiments/lab_asset_a2/a2_exit_20260905"
ENRICHMENT_DIR = REPO_ROOT / "experiments/lab_asset_a2/enrichment_20260906"
FROZEN_BUNDLE_SHA256 = (
    "fea8a136b0c3e19a00bddcb131a1540ca40fda6c1576dbc949001dbf76a9581c"
)

POOL_PRICE = 100
RU_INTERIOR = ["random_unit_vstar1", "random_unit_vstar2", "random_unit_vstar4", "random_unit_vstar6"]
RU_ALL = RU_INTERIOR + ["random_unit_exhaustion"]
POOL_ORDERS = ["P1", "P2", "P3", "P4"]
POOL_QUANTITIES = [5, 4, 3, 2]
VSTAR = {
    "random_unit_vstar1": 1,
    "random_unit_vstar2": 2,
    "random_unit_vstar4": 4,
    "random_unit_vstar6": 6,
    "random_unit_exhaustion": 14,
}
STREAM_COUNT = 64
MC_COUNT = 5000
PREREG_STATEMENT_SHA256 = (
    "703ca36ecdf261dc9879f58bb7a253af8ee4e01d1168bf3ae804398d326a2c4b"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def episode(name: str):
    return load_episode(ENRICHMENT_DIR / "fixtures" / name)


def frozen_hashes() -> dict[str, str]:
    manifest = json.loads((FROZEN_DIR / "bundle_manifest.json").read_text())
    return {
        relative: sha256_file(FROZEN_DIR / relative)
        for relative in manifest["files"]
    }


def base_seed_for(name: str) -> int:
    return FIBER_RESAMPLER_SEED_NAMESPACE + RU_ALL.index(name)


def first_pool_sequence(tape) -> int:
    for record in tape:
        if record.event_type != EventType.EXECUTION:
            continue
        execution = record.payload["execution"]
        if execution["price"] == POOL_PRICE:
            return record.sequence
    raise AssertionError("no pool-price execution")


def pool_of(ep):
    """(pool order ids, pool quantities) at POOL_PRICE, derived from the prestate."""

    ids = pool_orders_at_price(ep.prestate, POOL_PRICE)
    quantities = {o.order_id: o.quantity for o in ep.prestate.initial_book}
    assert ids == POOL_ORDERS, ids
    return ids, [quantities[order_id] for order_id in ids]


def original_maker_sequence(ep):
    """Pool-order indices drawn at POOL_PRICE, in execution order (the trajectory)."""

    ids, _ = pool_of(ep)
    index = {order_id: i for i, order_id in enumerate(ids)}
    sequence = []
    for record in ep.tape:
        if record.event_type != EventType.EXECUTION:
            continue
        execution = record.payload["execution"]
        if execution["price"] == POOL_PRICE:
            sequence.append(index[execution["maker_order_id"]])
    return tuple(sequence)


def expected_acceptance(ep) -> float:
    """1 - P_engine(original realized allocation trajectory)."""

    _, quantities = pool_of(ep)
    return 1.0 - order_sequence_probability(quantities, original_maker_sequence(ep))


def binomial_band(rate: float, attempts: int, sigma: float = 5.0) -> float:
    return sigma * math.sqrt(rate * (1.0 - rate) / attempts)


def recorded_units(tape) -> list[int]:
    return [
        record.payload["allocation_draw"]["selected_unit"]
        for record in tape
        if record.event_type == EventType.EXECUTION
    ]


def strip_selected_unit(tape) -> list[str]:
    """Canonical record bytes with only allocation_draw.selected_unit removed."""

    lines = []
    for record in tape:
        data = json.loads(record_to_json(record))
        draw = data["payload"].get("allocation_draw")
        if isinstance(draw, dict):
            draw.pop("selected_unit", None)
        lines.append(json.dumps(data, sort_keys=True))
    return lines


@pytest.fixture(scope="module")
def original_episodes():
    return {name: episode(name) for name in RU_ALL}


@pytest.fixture(scope="module")
def resample_streams(original_episodes):
    return {
        name: resample_many(
            original_episodes[name].prestate,
            original_episodes[name].tape,
            base_seed_for(name),
            STREAM_COUNT,
        )
        for name in RU_ALL
    }


# ------------------------------------------------------------- replay parity
def test_resampler_replay_loop_matches_frozen_validator(original_episodes) -> None:
    frozen_ru = load_episode(FROZEN_DIR / "fixture_random_unit_within_price")
    frozen_fifo = load_episode(FROZEN_DIR / "fixture_fifo")
    for ep in (*original_episodes.values(), frozen_ru, frozen_fifo):
        assert replay_loop_matches_validator(ep.prestate, ep.tape), ep.name


def test_uninjected_replay_regenerates_fixture_bytes(original_episodes) -> None:
    for name in RU_ALL:
        ep = original_episodes[name]
        disk = (ENRICHMENT_DIR / "fixtures" / name / "tape.jsonl").read_text()
        assert "".join(
            record_to_json(r) + "\n" for r in regenerate(ep.prestate, list(ep.tape))
        ) == disk


# ---------------------------------------------- injection-point ground truth
@pytest.mark.parametrize(
    "name", ["random_unit_vstar2", "random_unit_vstar6", "random_unit_exhaustion"]
)
def test_pinned_original_draws_reproduce_episode_byte_exactly(original_episodes, name) -> None:
    ep = original_episodes[name]
    outcome = resample_pinned(ep.prestate, ep.tape, recorded_units(ep.tape), label="original")
    assert [record_to_json(r) for r in outcome.tape] == [
        record_to_json(r) for r in ep.tape
    ]
    assert outcome.report.aggregate_identical
    assert not outcome.report.state_chain_differs
    assert not outcome.report.accepted
    assert outcome.chain_digest == state_chain_digest(ep.tape)


# ------------------------------------------------ dual-hash acceptance (core)
def test_dual_hash_acceptance_on_every_enriched_ru_fixture(
    original_episodes, resample_streams
) -> None:
    for name in RU_ALL:
        expected_rate = expected_acceptance(original_episodes[name])
        outcomes = resample_streams[name]
        summary = summarize(outcomes)
        assert summary.attempts == STREAM_COUNT
        for outcome in outcomes:
            assert outcome.report.aggregate_identical, (name, outcome.report)
            assert outcome.report.first_aggregate_mismatch is None
            assert outcome.report.accepted == outcome.report.state_chain_differs, (
                name,
                outcome.report,
            )
        assert summary.accepted == sum(
            1 for o in outcomes if o.report.state_chain_differs
        ), name
        band = binomial_band(expected_rate, STREAM_COUNT)
        assert abs(summary.acceptance_rate - expected_rate) <= band, (
            name,
            summary,
            expected_rate,
        )
        assert summary.accepted >= 2, (name, summary)


def test_at_least_two_distinct_accepted_chains_where_combinatorics_allow(
    resample_streams,
) -> None:
    for name in RU_ALL:
        summary = summarize(resample_streams[name])
        assert summary.distinct_accepted_chains >= 2, (name, summary)


def test_identity_divergence_confined_to_pool_draws(
    original_episodes, resample_streams
) -> None:
    for name in RU_ALL:
        original = original_episodes[name].tape
        first_pool = first_pool_sequence(original)
        for outcome in resample_streams[name]:
            if not outcome.report.accepted:
                continue
            # accepted => the allocation trajectory differs => maker identity
            # must diverge somewhere, and only at the multi-order pool level
            divergence = first_execution_identity_divergence(original, outcome.tape)
            assert divergence is not None, (name, outcome.origin)
            assert divergence >= first_pool, (name, divergence, first_pool)
            record = outcome.tape[divergence - 1]
            execution = record.payload["execution"]
            assert execution["price"] == POOL_PRICE, (name, divergence)


def test_state_chain_of_original_is_not_among_resamples(original_episodes, resample_streams) -> None:
    for name in RU_ALL:
        original_digest = state_chain_digest(original_episodes[name].tape)
        assert all(
            outcome.chain_digest != original_digest
            for outcome in resample_streams[name]
            if outcome.report.accepted
        ), name
        # an attempt reproducing the original trajectory is rejected outright
        clones = [
            outcome
            for outcome in resample_streams[name]
            if outcome.chain_digest == original_digest
        ]
        assert all(not outcome.report.accepted for outcome in clones), name


# ------------------------------------------------- aggregate-tape invariance
def test_aggregate_tape_byte_invariance(original_episodes, resample_streams) -> None:
    for name in RU_ALL:
        original_lines = aggregate_tape_lines(original_episodes[name].tape)
        for outcome in resample_streams[name]:
            if not outcome.report.accepted:
                continue
            assert aggregate_tape_lines(outcome.tape) == original_lines, (
                name,
                outcome.origin,
            )


def test_aggregate_projection_strips_identity_fields_only(original_episodes) -> None:
    for name in RU_ALL:
        for record in original_episodes[name].tape:
            projection = aggregate_projection(record)
            blob = json.dumps(projection)
            if record.event_type == EventType.EXECUTION:
                assert "maker_order_id" not in blob
                assert "maker_actor" not in blob
                assert "maker_remaining" not in blob
                assert "selected_unit" not in blob
                assert "eligible_units" in blob  # aggregate-visible
                assert "execution_id" in blob
            assert "pre_state_hash" not in blob
            assert "post_aggregate_state_hash" in blob


# ----------------------------------------------------------- exhaustion stratum
def test_exhaustion_count_law_is_point_mass_yet_chains_vary(
    original_episodes, resample_streams
) -> None:
    outcomes = resample_streams["random_unit_exhaustion"]
    law = mvhg_pmf(POOL_QUANTITIES, 14)
    assert law == {(5, 4, 3, 2): 1.0}
    for outcome in outcomes:
        assert outcome.report.aggregate_identical, outcome.report
        realized = allocation_counts(outcome.tape, POOL_PRICE)[POOL_PRICE]
        counts = tuple(realized.get(oid, 0) for oid in POOL_ORDERS)
        assert counts == (5, 4, 3, 2), outcome.origin
    summary = summarize(outcomes)
    expected_rate = expected_acceptance(original_episodes["random_unit_exhaustion"])
    assert abs(summary.acceptance_rate - expected_rate) <= binomial_band(
        expected_rate, STREAM_COUNT
    ), (summary, expected_rate)
    assert summary.distinct_accepted_chains >= 2, summary


# --------------------------------------------------------- deterministic kernels
def test_fifo_draw_fiber_is_a_point_and_resampler_refuses() -> None:
    ep = load_episode(ENRICHMENT_DIR / "fixtures" / "fifo_vstar2")
    outcome = resample(ep.prestate, ep.tape, draw_seed=987654321)
    # the fifo kernel consumes no RNG draws: native-state preservation makes the
    # injected replay byte-identical to the fixture, so nothing varies at all
    assert [record_to_json(r) for r in outcome.tape] == [
        record_to_json(r) for r in ep.tape
    ]
    assert outcome.report.same_length
    assert outcome.report.aggregate_identical
    assert not outcome.report.state_chain_differs
    assert not outcome.report.accepted


# --------------------------------------------- frozen bundle: single-order pool
def test_frozen_ru_single_order_pool_yields_no_accepted_resamples() -> None:
    ep = load_episode(FROZEN_DIR / "fixture_random_unit_within_price")
    streams = resample_many(ep.prestate, ep.tape, base_seed=424242, count=16)
    assert streams  # the engine did run
    for outcome in streams:
        assert outcome.report.aggregate_identical, outcome.report
        assert not outcome.report.state_chain_differs
        assert not outcome.report.accepted
        # maker allocation is invariant; only the exchangeable selected_unit
        # annotation (a within-order unit label) may differ
        assert strip_selected_unit(outcome.tape) == strip_selected_unit(ep.tape)
        assert first_execution_identity_divergence(ep.tape, outcome.tape) is None
        assert allocation_counts(outcome.tape) == allocation_counts(ep.tape)
    assert summarize(streams).distinct_accepted_chains == 0
    # the rationed level is a single maker of quantity 4, executed twice
    pool_counts = allocation_counts(ep.tape)
    single_order_levels = {
        price: counts for price, counts in pool_counts.items() if len(counts) == 1
    }
    assert single_order_levels and all(
        len(counts) == 1 for counts in pool_counts.values()
    ), pool_counts


@pytest.mark.xfail(
    reason="frozen a2_exit random_unit fixture has single-order rationed pools "
    "(price 101, one maker of quantity 4): draw regeneration is maker-invariant, "
    "so no distinct accepted chains exist; enriched multi-order pools provide them",
    strict=True,
)
def test_frozen_ru_distinct_chains_xfail_single_order_pool() -> None:
    ep = load_episode(FROZEN_DIR / "fixture_random_unit_within_price")
    summary = summarize(resample_many(ep.prestate, ep.tape, base_seed=424243, count=16))
    assert summary.distinct_accepted_chains >= 2


# ------------------------------------------------------------- exact MVHG laws
@pytest.mark.parametrize(
    "pool,draws",
    [
        ((5, 4, 3, 2), 1),
        ((5, 4, 3, 2), 2),
        ((5, 4, 3, 2), 4),
        ((5, 4, 3, 2), 6),
        ((5, 4, 3, 2), 14),
        ((2, 1), 2),
        ((1, 1, 1), 2),
        ((3, 1), 3),
        ((2, 2), 4),
        ((4,), 3),
    ],
)
def test_sequential_engine_law_equals_mvhg_closed_form(pool, draws) -> None:
    sequential = sequential_draw_law(pool, draws)
    closed = mvhg_pmf(pool, draws)
    assert set(sequential) == set(closed)
    for key in closed:
        assert abs(sequential[key] - closed[key]) < 1e-12, key
    assert abs(sum(closed.values()) - 1.0) < 1e-12


def test_mvhg_support_sums_and_matches_manual_small_cases() -> None:
    assert mvhg_pmf((2, 1), 2) == pytest.approx({(2, 0): 1 / 3, (1, 1): 2 / 3})
    assert mvhg_pmf((1, 1, 1), 2) == pytest.approx(
        {(1, 1, 0): 1 / 3, (1, 0, 1): 1 / 3, (0, 1, 1): 1 / 3}
    )
    law = mvhg_pmf((5, 4, 3, 2), 2)
    assert law[(2, 0, 0, 0)] == pytest.approx(10 / 91)
    assert law[(0, 0, 0, 2)] == pytest.approx(1 / 91)


@pytest.mark.parametrize("name", ["random_unit_vstar1", "random_unit_vstar2"])
def test_engine_pinned_enumeration_matches_mvhg(original_episodes, name) -> None:
    ep = original_episodes[name]
    law, reports = enumerate_engine_count_law(
        ep.prestate, ep.tape, POOL_PRICE, VSTAR[name]
    )
    assert reports and all(report.aggregate_identical for report in reports)
    # under native-state preservation exactly one enumerated sequence — the
    # original realized trajectory — reproduces the original chain and is
    # rejected; every other trajectory is an accepted within-fiber resample
    non_accepted = [report for report in reports if not report.accepted]
    assert len(non_accepted) == 1, (name, len(non_accepted))
    assert not non_accepted[0].state_chain_differs
    assert sum(1 for report in reports if report.accepted) == len(reports) - 1
    closed = mvhg_pmf(POOL_QUANTITIES, VSTAR[name])
    assert set(law) == set(closed)
    for key in closed:
        assert abs(law[key] - closed[key]) < 1e-12, (name, key)


# -------------------------------------------------------- Monte-Carlo chi-square
@pytest.mark.parametrize("name", RU_INTERIOR)
def test_monte_carlo_chisq_against_mvhg(original_episodes, name) -> None:
    ep = original_episodes[name]
    outcomes = resample_many(ep.prestate, ep.tape, base_seed_for(name) + 500, MC_COUNT)
    summary = summarize(outcomes)
    expected_rate = expected_acceptance(ep)
    band = binomial_band(expected_rate, MC_COUNT)
    assert abs(summary.acceptance_rate - expected_rate) <= band, (
        name,
        summary,
        expected_rate,
    )
    # count-law conformance over ALL attempts (unconditioned engine law)
    observed: dict[tuple[int, ...], int] = {}
    for outcome in outcomes:
        realized = allocation_counts(outcome.tape, POOL_PRICE)[POOL_PRICE]
        counts = tuple(realized.get(oid, 0) for oid in POOL_ORDERS)
        observed[counts] = observed.get(counts, 0) + 1
    assert sum(observed.values()) == MC_COUNT
    result = chi_square_gof(observed, mvhg_pmf(POOL_QUANTITIES, VSTAR[name]))
    assert result.pvalue > 0.001, (name, result)


# ----------------------------------------------------------- determinism of API
def test_same_base_seed_reproduces_identical_resample_stream(original_episodes) -> None:
    ep = original_episodes["random_unit_vstar6"]
    first = resample_many(ep.prestate, ep.tape, base_seed=777, count=16)
    second = resample_many(ep.prestate, ep.tape, base_seed=777, count=16)
    assert [o.origin for o in first] == [o.origin for o in second]
    for left, right in zip(first, second):
        assert [record_to_json(r) for r in left.tape] == [
            record_to_json(r) for r in right.tape
        ]
    other = resample_many(ep.prestate, ep.tape, base_seed=778, count=16)
    assert [o.chain_digest for o in first] != [o.chain_digest for o in other]


def test_draw_seed_stream_deterministic() -> None:
    assert draw_seed_stream(123, 8) == draw_seed_stream(123, 8)
    assert len(set(draw_seed_stream(123, 64))) == 64


# --------------------------------------------------- dual-hash checker itself
def test_dual_hash_refuses_identical_and_tampered_tapes(original_episodes) -> None:
    ep = original_episodes["random_unit_vstar2"]
    # original vs itself: aggregate identical but state chain identical -> refuse
    report = dual_hash_report(ep.tape, list(ep.tape))
    assert report.aggregate_identical and not report.state_chain_differs
    assert not report.accepted
    # tampered aggregate hash -> aggregate sequence not identical
    tampered = list(ep.tape)
    payload = dict(tampered[2].payload)
    tampered[2] = type(tampered[2])(
        sequence=tampered[2].sequence,
        event_type=tampered[2].event_type,
        payload=payload,
        pre_state_hash=tampered[2].pre_state_hash,
        post_state_hash=tampered[2].post_state_hash,
        pre_aggregate_state_hash="0" * 64,
        post_aggregate_state_hash=tampered[2].post_aggregate_state_hash,
    )
    report = dual_hash_report(ep.tape, tampered)
    assert not report.aggregate_identical
    assert not report.accepted
    assert report.first_aggregate_mismatch == 3
    # length mismatch -> refuse
    report = dual_hash_report(ep.tape, list(ep.tape)[:-1])
    assert not report.same_length and not report.accepted


def test_pinned_draw_source_guards() -> None:
    source = PinnedDrawSource([0, 1], label="unit-test")
    assert source.randrange(4) == 0
    assert source.randrange(4) == 1
    with pytest.raises(ValueError):
        source.randrange(4)  # exhausted
    bad = PinnedDrawSource([9], label="unit-test")
    with pytest.raises(ValueError):
        bad.randrange(4)  # out of eligible range


def test_native_state_preserving_source_tracks_engine_rng() -> None:
    native = NativeStatePreservingDrawSource(PinnedDrawSource([0], "native-test"), 42)
    fresh = random.Random(42)
    state0 = native.getstate()
    assert state0 == fresh.getstate()
    assert stable_hash(state0)  # json-serializable through the frozen hasher
    value = native.randrange(7)
    fresh.randrange(7)  # the identical native call is consumed and discarded
    assert value == 0
    assert native.getstate() == fresh.getstate()
    # pinned exhaustion propagates through the wrapper
    with pytest.raises(ValueError):
        native.randrange(7)


# ------------------------------------------------------- frozen prereg pinning
def test_prereg_statement_is_frozen_verbatim() -> None:
    assert hashlib.sha256(PREREG_STATEMENT.encode("utf-8")).hexdigest() == (
        PREREG_STATEMENT_SHA256
    )
    assert PREREG_STATEMENT.startswith("The fiber resampler certifies aggregate-law")


# ------------------------------------------------------------ read-only guards
def test_frozen_bundle_read_only_before_and_after_resampling() -> None:
    before = frozen_hashes()
    manifest = json.loads((FROZEN_DIR / "bundle_manifest.json").read_text())
    assert set(before) == set(manifest["files"]) and len(before) == 7
    for relative, expected in sorted(manifest["files"].items()):
        assert before[relative] == expected, relative
    assert sha256_file(FROZEN_DIR / "bundle_manifest.json") == FROZEN_BUNDLE_SHA256

    ep = load_episode(FROZEN_DIR / "fixture_random_unit_within_price")
    resample_many(ep.prestate, ep.tape, base_seed=999, count=8)

    after = frozen_hashes()
    assert after == before
    assert sha256_file(FROZEN_DIR / "bundle_manifest.json") == FROZEN_BUNDLE_SHA256


def test_enrichment_bundle_untouched_by_resampling() -> None:
    manifest = json.loads((ENRICHMENT_DIR / "enrichment_manifest.json").read_text())
    for relative, expected in sorted(manifest["files"].items()):
        assert sha256_file(ENRICHMENT_DIR / relative) == expected, relative


def test_frozen_ru_fixture_replays_under_frozen_validator() -> None:
    # Cross-check that the frozen fixture loads with the frozen parser and that
    # the resampler's un-injected loop reproduces it (ground for the xfail above).
    raw = json.loads((FROZEN_DIR / "fixture_random_unit_within_price/prestate.json").read_text())
    assert raw["schema_version"] == "lab-asset-v3"
    ep = load_episode(FROZEN_DIR / "fixture_random_unit_within_price")
    assert replay_loop_matches_validator(ep.prestate, ep.tape)
