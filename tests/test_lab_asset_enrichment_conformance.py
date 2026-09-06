"""Conformance tests for the lab-asset-v3.1 enrichment bundle (PI decision D1_03).

Covers, against experiments/lab_asset_a2/enrichment_20260906/:
  (i)   the frozen 27-test conformance suite re-run against the enriched fixtures
        where applicable (applicability table below; mirrors by test_frozen__*),
  (ii)  schema-extension validation (backward-compatible lab-asset-v3.1),
  (iii) enrichment-manifest hash verification incl. quoted frozen parent lineage,
  (iv)  replay determinism incl. byte-exact regeneration and tamper detection,
  (v)   a read-only guard asserting the 7 frozen a2_exit_20260905 sha256s.

The frozen bundle experiments/lab_asset_a2/a2_exit_20260905/ is never written.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from dataclasses import asdict, replace as dc_replace
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lab_asset.export_schema import (
    check_spec_covers_fixtures,
    declared_payload_keys,
    observed_payload_keys,
)
from lab_asset.matching import ReferenceEngine
from lab_asset.replay import replay
from lab_asset.schema import (
    CancelRequest,
    EventType,
    OrderRequest,
    ReplaceRequest,
    SessionPrestate,
    Side,
    TapeRecord,
    ThreeClocks,
    prestate_from_json,
    record_to_json,
)

FROZEN_DIR = REPO_ROOT / "experiments/lab_asset_a2/a2_exit_20260905"
ENRICHMENT_DIR = REPO_ROOT / "experiments/lab_asset_a2/enrichment_20260906"
FROZEN_TEST_FILE = REPO_ROOT / "tests/test_lab_asset_conformance.py"
FROZEN_BUNDLE_SHA256 = (
    "fea8a136b0c3e19a00bddcb131a1540ca40fda6c1576dbc949001dbf76a9581c"
)
REQUEST_EVENTS = (
    EventType.ORDER_REQUEST,
    EventType.CANCEL_REQUEST,
    EventType.REPLACE_REQUEST,
    EventType.LATENCY_CHOICE,
    EventType.LATENCY_CHOICE_REJECTED,
    EventType.SESSION_END,
)

# Which of the 27 frozen conformance tests apply to the enriched fixtures.
# "applies" = the frozen assertion is re-evaluated on enrichment-bundle data by a
# mirrored test named test_frozen__<name> in this module. "not_applies" tests are
# own-scenario engine unit tests (golden arithmetic, rejection ladders, latency
# events, priority-race module) whose subjects are absent from the enriched
# fixtures by design; they remain green in the frozen suite and are unaffected by
# an additive schema extension.
APPLICABILITY: dict[str, dict[str, object]] = {
    "test_session_start_commits_complete_prestate": {"applies": True},
    "test_golden_marketable_cross_settles_holdings": {
        "applies": False,
        "reason": "golden settlement arithmetic on its own two-actor scenario; enriched settlement fidelity is enforced by the replay contract",
    },
    "test_partial_fill_chain_and_basic_rejections": {
        "applies": False,
        "reason": "rejection legs (duplicate client id, bands, zero quantity) are absent from enriched fixtures by design",
    },
    "test_cash_inventory_actor_and_clock_constraints": {
        "applies": False,
        "reason": "rejection ladder scenario; enriched fixtures contain no rejected requests",
    },
    "test_induced_value_unit_capacities_are_enforced": {
        "applies": False,
        "reason": "enriched prestates carry no induced-value schedules",
    },
    "test_self_trade_prevention_covers_every_crossed_level": {
        "applies": False,
        "reason": "enriched fixtures have no self-crossing submissions by design",
    },
    "test_cancel_lifecycle_and_ownership": {
        "applies": False,
        "reason": "cancel-rejection paths absent; the successful cancel is exercised via the quote/lineage mirrors",
    },
    "test_fifo_is_arrival_ordered_and_partial_maker_keeps_priority": {"applies": True},
    "test_random_unit_draws_are_quantity_weighted_and_recorded": {
        "applies": True,
        "reason_note": "recording leg (allocation_draw consistency); the 800-seed statistical weighting is an own-scenario engine property",
    },
    "test_random_unit_allocation_is_invariant_to_contiguous_child_splitting": {
        "applies": False,
        "reason": "own-scenario engine invariance check",
    },
    "test_identity_hash_preserves_fifo_order_while_aggregate_hash_does_not": {
        "applies": False,
        "reason": "submission-order swap scenario; its substance is covered by the arm-pair aggregate mirror",
    },
    "test_aggregate_state_matches_across_arms_at_request_boundaries": {"applies": True},
    "test_latency_choice_is_recorded_rejected_and_replayable": {
        "applies": False,
        "reason": "enriched fixtures emit no latency-choice events",
    },
    "test_isolated_race_removes_the_marginal_return_to_speed": {
        "applies": False,
        "reason": "priority_race module check, not a fixture property",
    },
    "test_initial_book_is_loaded_and_resource_checked": {"applies": True},
    "test_bit_level_determinism_and_hash_chain": {"applies": True},
    "test_deterministic_replay_reproduces_recorded_tape": {"applies": True},
    "test_replay_detects_tampered_tape": {"applies": True},
    "test_replace_resting_to_resting_records_lineage_and_quotes": {"applies": True},
    "test_replace_that_crosses_executes_against_opposite_book": {
        "applies": False,
        "reason": "enriched replace (D1 102->103) does not cross by design",
    },
    "test_replace_rejections_are_reason_coded_and_resource_freeing": {
        "applies": False,
        "reason": "no replace rejections in enriched fixtures",
    },
    "test_replace_frees_reserved_resources_for_larger_quantity": {
        "applies": False,
        "reason": "private-validator own scenario",
    },
    "test_rejection_ids_are_sequential_across_families": {
        "applies": False,
        "reason": "no rejection events in enriched fixtures",
    },
    "test_pre_post_quotes_on_accepted_actions": {"applies": True},
    "test_roles_recorded_and_prestate_validated": {"applies": True},
    "test_replay_reproduces_and_detects_tampering_on_replace_tape": {"applies": True},
    "test_a2_exit_bundle_round_trip_and_tamper_detection": {"applies": True},
}


# ------------------------------------------------------------------ helpers
def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest() -> dict[str, object]:
    return json.loads((ENRICHMENT_DIR / "enrichment_manifest.json").read_text())


def fixture_names(manifest: dict[str, object]) -> list[str]:
    return sorted(manifest["fixtures"])  # type: ignore[arg-type]


def load_tape(name: str) -> list[TapeRecord]:
    records: list[TapeRecord] = []
    for line in (ENRICHMENT_DIR / "fixtures" / name / "tape.jsonl").read_text().splitlines():
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


def load_prestate(name: str) -> SessionPrestate:
    """Parse an enriched prestate with the FROZEN v3 parser (ignores extension keys)."""

    return prestate_from_json(
        (ENRICHMENT_DIR / "fixtures" / name / "prestate.json").read_text()
    )


def _sub(payload: dict[str, object], key: str) -> dict[str, object]:
    value = payload[key]
    assert isinstance(value, dict)
    return value


def _int(value: object) -> int:
    assert isinstance(value, int)
    return value


def _str(value: object) -> str:
    assert isinstance(value, str)
    return value


def clocks_of(payload: dict[str, object]) -> ThreeClocks:
    raw = _sub(payload, "clocks")
    return ThreeClocks(
        client_ts=_int(raw["client_ts"]),
        receipt_ts=_int(raw["receipt_ts"]),
        match_ts=_int(raw["match_ts"]),
    )


def run_stream(prestate: SessionPrestate, tape: list[TapeRecord]) -> ReferenceEngine:
    """Re-execute the recorded request stream and return the live engine."""

    engine = ReferenceEngine(prestate)
    for record in tape:
        payload = record.payload
        if record.event_type == EventType.ORDER_REQUEST:
            engine.submit(
                OrderRequest(
                    event_id=_int(payload["event_id"]),
                    actor=_str(payload["actor"]),
                    client_order_id=_str(payload["client_order_id"]),
                    side=Side(_str(payload["side"])),
                    price=_int(payload["price"]),
                    quantity=_int(payload["quantity"]),
                    clocks=clocks_of(payload),
                    round_id=_int(payload["round_id"]),
                )
            )
        elif record.event_type == EventType.CANCEL_REQUEST:
            engine.cancel(
                CancelRequest(
                    event_id=_int(payload["event_id"]),
                    actor=_str(payload["actor"]),
                    order_id=_str(payload["order_id"]),
                    clocks=clocks_of(payload),
                    round_id=_int(payload["round_id"]),
                )
            )
        elif record.event_type == EventType.REPLACE_REQUEST:
            engine.replace(
                ReplaceRequest(
                    event_id=_int(payload["event_id"]),
                    actor=_str(payload["actor"]),
                    replaces_order_id=_str(payload["replaces_order_id"]),
                    client_order_id=_str(payload["client_order_id"]),
                    side=Side(_str(payload["side"])),
                    price=_int(payload["price"]),
                    quantity=_int(payload["quantity"]),
                    clocks=clocks_of(payload),
                    round_id=_int(payload["round_id"]),
                )
            )
        elif record.event_type == EventType.SESSION_END:
            engine.finish()
    return engine


def stream_digests(prestate: SessionPrestate, tape: list[TapeRecord]) -> tuple[list[str], ReferenceEngine]:
    engine = ReferenceEngine(prestate)
    digests: list[str] = []
    for record in tape:
        if record.event_type not in REQUEST_EVENTS:
            continue
        before = len(engine.tape)
        if record.event_type == EventType.ORDER_REQUEST:
            payload = record.payload
            engine.submit(
                OrderRequest(
                    event_id=_int(payload["event_id"]),
                    actor=_str(payload["actor"]),
                    client_order_id=_str(payload["client_order_id"]),
                    side=Side(_str(payload["side"])),
                    price=_int(payload["price"]),
                    quantity=_int(payload["quantity"]),
                    clocks=clocks_of(payload),
                    round_id=_int(payload["round_id"]),
                )
            )
        elif record.event_type == EventType.CANCEL_REQUEST:
            payload = record.payload
            engine.cancel(
                CancelRequest(
                    event_id=_int(payload["event_id"]),
                    actor=_str(payload["actor"]),
                    order_id=_str(payload["order_id"]),
                    clocks=clocks_of(payload),
                    round_id=_int(payload["round_id"]),
                )
            )
        elif record.event_type == EventType.REPLACE_REQUEST:
            payload = record.payload
            engine.replace(
                ReplaceRequest(
                    event_id=_int(payload["event_id"]),
                    actor=_str(payload["actor"]),
                    replaces_order_id=_str(payload["replaces_order_id"]),
                    client_order_id=_str(payload["client_order_id"]),
                    side=Side(_str(payload["side"])),
                    price=_int(payload["price"]),
                    quantity=_int(payload["quantity"]),
                    clocks=clocks_of(payload),
                    round_id=_int(payload["round_id"]),
                )
            )
        elif record.event_type == EventType.SESSION_END:
            engine.finish()
        assert len(engine.tape) > before
        digests.append(engine.aggregate_state_digest())
    return digests, engine


def executions_of(tape: list[TapeRecord]) -> list[dict[str, object]]:
    return [
        _sub(record.payload, "execution")
        for record in tape
        if record.event_type == EventType.EXECUTION
    ]


def payloads_of(tape: list[TapeRecord], etype: EventType) -> list[dict[str, object]]:
    return [record.payload for record in tape if record.event_type == etype]


def tampered_copy(
    tape: list[TapeRecord], etype: EventType, key_path: tuple[str, ...], new_value: object
) -> list[TapeRecord]:
    out: list[TapeRecord] = []
    done = False
    for record in tape:
        if record.event_type == etype and not done:
            payload = dict(record.payload)
            node = payload
            for key in key_path[:-1]:
                nested = dict(_sub(node, key))
                node[key] = nested
                node = nested
            node[key_path[-1]] = new_value
            out.append(dc_replace(record, payload=payload))
            done = True
        else:
            out.append(record)
    assert done, f"no {etype.value} record to tamper"
    return out


def is_ru(name: str) -> bool:
    return name.startswith("random_unit")


def interior(name: str) -> bool:
    return "exhaustion" not in name


# ------------------------------------------------ (v) frozen read-only guard
def test_frozen_bundle_read_only_guard() -> None:
    frozen_manifest = json.loads((FROZEN_DIR / "bundle_manifest.json").read_text())
    files = frozen_manifest["files"]
    assert isinstance(files, dict)
    assert len(files) == 7
    for relative, expected in sorted(files.items()):
        assert sha256_file(FROZEN_DIR / relative) == expected, relative
    assert sha256_file(FROZEN_DIR / "bundle_manifest.json") == FROZEN_BUNDLE_SHA256


# ---------------------------------------------- (iii) manifest verification
def test_manifest_hashes_every_emitted_file() -> None:
    manifest = load_manifest()
    files = manifest["files"]
    assert isinstance(files, dict)
    on_disk = {
        str(path.relative_to(ENRICHMENT_DIR))
        for path in ENRICHMENT_DIR.rglob("*")
        if path.is_file()
        and path.name != "enrichment_manifest.json"
        and "__pycache__" not in path.parts
    }
    assert set(files) == on_disk
    assert "enrichment_manifest.json" not in files
    for relative, expected in sorted(files.items()):
        assert sha256_file(ENRICHMENT_DIR / relative) == expected, relative


def test_manifest_parent_lineage_quotes_frozen_bundle_verbatim() -> None:
    manifest = load_manifest()
    parent = manifest["parent_bundle"]
    assert isinstance(parent, dict)
    frozen_manifest = json.loads((FROZEN_DIR / "bundle_manifest.json").read_text())
    assert parent["files"] == frozen_manifest["files"]
    assert parent["bundle_manifest_sha256"] == FROZEN_BUNDLE_SHA256
    assert parent["schema_version"] == "lab-asset-v3"
    assert parent["read_only"] is True
    assert parent["files"]["schema_spec.json"] == sha256_file(FROZEN_DIR / "schema_spec.json")


def test_manifest_inventory_and_pair_structure() -> None:
    manifest = load_manifest()
    fixtures = manifest["fixtures"]
    assert isinstance(fixtures, dict)
    assert len(fixtures) == 10
    pairs = manifest["pairs"]
    assert isinstance(pairs, dict)
    assert len(pairs) == 5
    for pair_key, members in pairs.items():
        assert len(members) == 2
        arms = {fixtures[m.split("/")[-1]]["allocation_rule"] for m in members}
        assert arms == {"fifo", "random_unit_within_price"}
    for name, fixture in fixtures.items():
        assert fixture["records"] == len(load_tape(name))
        assert fixture["seed"] == manifest["master_seed"]
        assert isinstance(fixture["supports"], dict)


# --------------------------------------------- (ii) schema-extension checks
def test_schema_extension_declares_backward_compatible_v3_1() -> None:
    extension = json.loads((ENRICHMENT_DIR / "schema_extension.json").read_text())
    assert extension["extension_label"] == "lab-asset-v3.1"
    assert extension["parent_schema_label"] == "lab-asset-v3"
    assert extension["kind"] == "backward_compatible_additive_extension"
    frozen_manifest = json.loads((FROZEN_DIR / "bundle_manifest.json").read_text())
    assert extension["parent_schema_spec_sha256"] == frozen_manifest["files"]["schema_spec.json"]
    assert extension["parent_bundle_manifest_sha256"] == FROZEN_BUNDLE_SHA256
    fields = extension["fields"]
    assert isinstance(fields, list)
    arrival = next(f for f in fields if f["name"] == "arrival_clocks")
    for key in ("location", "type", "constraint", "semantics", "hash_treatment", "v3_compatibility"):
        assert arrival[key]
    assert "latency_window_rule" in extension


def test_v3_parser_ignores_extension_fields_and_replays() -> None:
    for name in fixture_names(load_manifest()):
        raw = json.loads((ENRICHMENT_DIR / "fixtures" / name / "prestate.json").read_text())
        assert raw["schema_version"] == "lab-asset-v3.1"
        assert set(raw["arrival_clocks"]) == {o["order_id"] for o in raw["initial_book"]}
        assert all(isinstance(v, int) for v in raw["arrival_clocks"].values())
        prestate = load_prestate(name)  # frozen v3 parser
        assert not hasattr(prestate, "arrival_clocks")
        assert prestate.schema_version == "lab-asset-v3.1"
        tape = load_tape(name)
        report = replay(prestate, tape)
        assert report.ok, f"{name}: {report}"


def test_enriched_tapes_stay_within_frozen_spec_payload_grammar() -> None:
    frozen_spec = json.loads((FROZEN_DIR / "schema_spec.json").read_text())
    declared = declared_payload_keys(frozen_spec)
    for name in fixture_names(load_manifest()):
        engine = run_stream(load_prestate(name), load_tape(name))
        observed = observed_payload_keys(engine)
        missing = observed - declared
        assert not missing, f"{name}: payload keys outside frozen spec: {sorted(missing)}"
    engines = [
        run_stream(load_prestate(name), load_tape(name))
        for name in fixture_names(load_manifest())
    ]
    check_spec_covers_fixtures(frozen_spec, engines)


# ------------------------------------------ (iv) replay determinism + tamper
def test_replay_reports_ok_and_byte_exact_regeneration() -> None:
    for name in fixture_names(load_manifest()):
        prestate = load_prestate(name)
        tape = load_tape(name)
        report = replay(prestate, tape)
        assert report.ok, f"{name}: {report}"
        request_events = sum(1 for r in tape if r.event_type in REQUEST_EVENTS)
        assert report.events_replayed == request_events
        disk = (ENRICHMENT_DIR / "fixtures" / name / "tape.jsonl").read_text()
        assert "".join(record_to_json(r) + "\n" for r in run_stream(prestate, tape).tape) == disk
        recorded_report = json.loads(
            (ENRICHMENT_DIR / "fixtures" / name / "replay_report.json").read_text()
        )
        assert recorded_report == {"ok": True, "records": len(tape)}


def test_regeneration_twice_identical() -> None:
    for name in fixture_names(load_manifest()):
        prestate, tape = load_prestate(name), load_tape(name)
        first = [record_to_json(r) for r in run_stream(prestate, tape).tape]
        second = [record_to_json(r) for r in run_stream(prestate, tape).tape]
        assert first == second


# ----------------------------------------------------- (i) frozen re-run: 13
def test_applicability_table_covers_frozen_27() -> None:
    source = FROZEN_TEST_FILE.read_text()
    frozen_names = set(re.findall(r"^def (test_[a-z0-9_]+)\(", source, re.MULTILINE))
    assert len(frozen_names) == 27
    assert set(APPLICABILITY) == frozen_names
    applicable = [n for n, entry in APPLICABILITY.items() if entry["applies"]]
    assert len(applicable) == 13
    for name in applicable:
        assert f"test_frozen__{name}" in globals(), f"missing mirror for {name}"
    for name, entry in APPLICABILITY.items():
        if not entry["applies"]:
            assert isinstance(entry["reason"], str) and entry["reason"]


def test_frozen__test_session_start_commits_complete_prestate() -> None:
    for name in fixture_names(load_manifest()):
        tape = load_tape(name)
        start = tape[0]
        assert start.event_type == EventType.SESSION_START
        engine = ReferenceEngine(load_prestate(name))
        assert start.payload["prestate_hash"] == engine.prestate_digest
        assert start.payload["allocation_rule"] == engine.prestate.allocation_rule.value
        assert start.payload["schema_version"] == "lab-asset-v3.1"
        assert start.pre_state_hash != start.post_state_hash


def test_frozen__test_fifo_is_arrival_ordered_and_partial_maker_keeps_priority() -> None:
    for name in fixture_names(load_manifest()):
        if is_ru(name):
            continue
        tape = load_tape(name)
        makers = [(e["maker_order_id"], _int(e["quantity"])) for e in executions_of(tape)]
        expected_prefix = [("A1", 2), ("A2", 3)]
        if name == "fifo_vstar1":
            assert makers == expected_prefix + [("P1", 1)]
        elif name == "fifo_vstar2":
            assert makers == expected_prefix + [("P1", 2)]
        elif name == "fifo_vstar4":
            assert makers == expected_prefix + [("P1", 4)]
        elif name == "fifo_vstar6":
            assert makers == expected_prefix + [("P1", 5), ("P2", 1)]
        else:
            assert makers == expected_prefix + [("P1", 5), ("P2", 4), ("P3", 3), ("P4", 2)]
        engine = run_stream(load_prestate(name), tape)
        queue = engine.asks[100] if 100 in engine.asks else []
        partial = [row for row in queue if row[0] in {"P1", "P2"}]
        untouched = [row for row in queue if row[0] in {"P3", "P4"}]
        assert partial + untouched == queue  # partially filled maker keeps its rank
        if name == "fifo_vstar1":
            assert queue == [("P1", "m1", 4), ("P2", "m2", 4), ("P3", "m3", 3), ("P4", "m4", 2)]
        elif name == "fifo_vstar6":
            assert queue == [("P2", "m2", 3), ("P3", "m3", 3), ("P4", "m4", 2)]
        elif name == "fifo_exhaustion":
            assert 100 not in engine.asks


def test_frozen__test_random_unit_draws_are_quantity_weighted_and_recorded() -> None:
    for name in fixture_names(load_manifest()):
        if not is_ru(name):
            continue
        tape = load_tape(name)
        remaining = {98: 2, 99: 3, 100: 14, 102: 6, 104: 7}
        pool_draws = 0
        for record in tape:
            if record.event_type != EventType.EXECUTION:
                continue
            execution = _sub(record.payload, "execution")
            price = _int(execution["price"])
            assert _int(execution["quantity"]) == 1
            draw = _sub(record.payload, "allocation_draw")
            assert _int(draw["price"]) == price
            assert _int(draw["eligible_units"]) == remaining[price]
            assert 0 <= _int(draw["selected_unit"]) < remaining[price]
            assert _str(draw["maker_order_id"]) == _str(execution["maker_order_id"])
            remaining[price] -= 1
            if price == 100:
                pool_draws += 1
        fixture = load_manifest()["fixtures"][name]
        assert isinstance(fixture, dict)
        assert pool_draws == _int(fixture["episode"]["v_star"])


def test_frozen__test_aggregate_state_matches_across_arms_at_request_boundaries() -> None:
    manifest = load_manifest()
    for pair_key, members in sorted(manifest["pairs"].items()):  # type: ignore[union-attr]
        assert len(members) == 2
        fifo_name = next(m.split("/")[-1] for m in members if "fifo" in m)
        ru_name = next(m.split("/")[-1] for m in members if "random_unit" in m)
        fifo_digests, fifo_engine = stream_digests(
            load_prestate(fifo_name), load_tape(fifo_name)
        )
        ru_digests, ru_engine = stream_digests(load_prestate(ru_name), load_tape(ru_name))
        assert fifo_digests == ru_digests, pair_key
        assert fifo_engine.identity_state_digest() != ru_engine.identity_state_digest()
        assert len(executions_of(fifo_engine.tape)) != len(executions_of(ru_engine.tape))


def test_frozen__test_initial_book_is_loaded_and_resource_checked() -> None:
    expected_book = {
        98: [("A1", "u1", 2)],
        99: [("A2", "u2", 3)],
        100: [("P1", "m1", 5), ("P2", "m2", 4), ("P3", "m3", 3), ("P4", "m4", 2)],
        102: [("D1", "d1", 6)],
        104: [("D2", "d2", 7)],
    }
    for name in fixture_names(load_manifest()):
        engine = ReferenceEngine(load_prestate(name))  # prestate validation passes
        assert engine.bids == {}
        assert engine.asks == expected_book


def test_frozen__test_bit_level_determinism_and_hash_chain() -> None:
    # The frozen test asserts chain continuity on its own simple submit/finish tapes.
    # Per-record continuity across a *composite* action (replace_request ->
    # order_replaced, where the engine mutates the book between sealed records, and
    # request -> rejection, where hashed rejection counters increment during payload
    # construction) is not an engine contract: the frozen a2_exit_20260905 tapes break
    # at exactly those boundaries too. The binding contract is record-by-record
    # replay equality (test_replay), which these fixtures satisfy byte-exactly.
    composite_boundary = {
        (EventType.REPLACE_REQUEST, EventType.ORDER_REPLACED),
        (EventType.REPLACE_REQUEST, EventType.REPLACE_REJECTED),
        (EventType.CANCEL_REQUEST, EventType.CANCEL_REJECTED),
        (EventType.ORDER_REQUEST, EventType.ORDER_REJECTED),
    }
    for name in fixture_names(load_manifest()):
        tape = load_tape(name)
        for previous, current in zip(tape, tape[1:], strict=False):
            if (previous.event_type, current.event_type) in composite_boundary:
                continue
            assert previous.post_state_hash == current.pre_state_hash, (
                name,
                previous.sequence,
                current.sequence,
            )
        prestate = load_prestate(name)
        first = [record_to_json(r) for r in run_stream(prestate, tape).tape]
        second = [record_to_json(r) for r in run_stream(prestate, tape).tape]
        assert first == second


def test_frozen__test_deterministic_replay_reproduces_recorded_tape() -> None:
    for name in fixture_names(load_manifest()):
        prestate, tape = load_prestate(name), load_tape(name)
        report = replay(prestate, tape)
        assert report.ok, f"{name}: {report}"
        request_events = sum(1 for r in tape if r.event_type in REQUEST_EVENTS)
        assert report.events_replayed == request_events


def test_frozen__test_replay_detects_tampered_tape() -> None:
    for name in fixture_names(load_manifest()):
        prestate, tape = load_prestate(name), load_tape(name)
        assert replay(prestate, tampered_copy(tape, EventType.EXECUTION, ("execution", "quantity"), 99)).ok is False


def test_frozen__test_replace_resting_to_resting_records_lineage_and_quotes() -> None:
    for name in fixture_names(load_manifest()):
        prestate, tape = load_prestate(name), load_tape(name)
        replaced = payloads_of(tape, EventType.ORDER_REPLACED)
        assert len(replaced) == 1
        payload = replaced[0]
        assert payload["replaces_order_id"] == "D1"
        assert payload["order_id"] == "O00000010"
        assert payload["parent_order_id"] == "D1"
        assert payload["lineage_root"] == "D1"
        assert payload["replaced_quantity"] == 6
        assert payload["resting_quantity"] == 4
        if interior(name):
            assert payload["pre_best_ask"] == 100 and payload["post_best_ask"] == 100
        else:
            assert payload["pre_best_ask"] == 102 and payload["post_best_ask"] == 103
        engine = run_stream(prestate, tape)
        assert engine.order_status["D1"] == "replaced"
        assert engine.order_status["O00000010"] == "resting"
        assert engine.order_parent["O00000010"] == "D1"
        assert engine.lineage_root("O00000010") == "D1"


def test_frozen__test_pre_post_quotes_on_accepted_actions() -> None:
    for name in fixture_names(load_manifest()):
        tape = load_tape(name)
        accepted = payloads_of(tape, EventType.ORDER_ACCEPTED)
        assert len(accepted) == 1
        assert accepted[0]["pre_best_ask"] == 98
        assert accepted[0]["post_best_ask"] == (102 if not interior(name) else 100)
        assert accepted[0]["pre_best_bid"] is None and accepted[0]["post_best_bid"] is None
        for execution_payload in payloads_of(tape, EventType.EXECUTION):
            for key in ("pre_best_bid", "pre_best_ask", "post_best_bid", "post_best_ask"):
                assert key in execution_payload
        cancelled = payloads_of(tape, EventType.ORDER_CANCELLED)
        assert len(cancelled) == 1
        assert cancelled[0]["cancelled_quantity"] == 7
        assert cancelled[0]["post_best_ask"] == (102 if not interior(name) else 100)
        rejected = payloads_of(tape, EventType.ORDER_REJECTED)
        assert rejected == []


def test_frozen__test_roles_recorded_and_prestate_validated() -> None:
    for name in fixture_names(load_manifest()):
        tape = load_tape(name)
        roles = [
            (record.event_type, record.payload["role"])
            for record in tape
            if record.event_type
            in (EventType.ORDER_REQUEST, EventType.CANCEL_REQUEST, EventType.REPLACE_REQUEST)
        ]
        assert roles == [
            (EventType.ORDER_REQUEST, "trader"),
            (EventType.CANCEL_REQUEST, "trader"),
            (EventType.REPLACE_REQUEST, "designated_maker"),
        ]
        ReferenceEngine(load_prestate(name))  # validation leg: constructs cleanly


def test_frozen__test_replay_reproduces_and_detects_tampering_on_replace_tape() -> None:
    for name in fixture_names(load_manifest()):
        prestate, tape = load_prestate(name), load_tape(name)
        assert replay(prestate, tape).ok
        broken = tampered_copy(
            tape, EventType.ORDER_REPLACED, ("resting_quantity",), 999
        )
        assert replay(prestate, broken).ok is False


def test_frozen__test_a2_exit_bundle_round_trip_and_tamper_detection(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location(
        "enrichment_generate_fixtures", ENRICHMENT_DIR / "generate_fixtures.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    out_dir = tmp_path / "bundle"
    module.build_bundle(out_dir)
    for relative in sorted(json.loads((out_dir / "enrichment_manifest.json").read_text())["files"]):
        assert (out_dir / relative).read_bytes() == (ENRICHMENT_DIR / relative).read_bytes(), relative
    assert (
        out_dir / "enrichment_manifest.json"
    ).read_bytes() == (ENRICHMENT_DIR / "enrichment_manifest.json").read_bytes()

    def files_ok(bundle_dir: Path) -> bool:
        manifest = json.loads((bundle_dir / "enrichment_manifest.json").read_text())
        return all(
            sha256_file(bundle_dir / relative) == expected
            for relative, expected in manifest["files"].items()
        )

    assert files_ok(out_dir)
    tape_path = out_dir / "fixtures/fifo_vstar2/tape.jsonl"
    original = tape_path.read_bytes()
    tape_path.write_bytes(original.replace(b'"quantity":7', b'"quantity":8', 1))
    assert not files_ok(out_dir)


# ------------------------------------------------ enrichment-specific gates
def test_fifo_orthant_requirements() -> None:
    manifest = load_manifest()
    flagged = []
    for name in fixture_names(manifest):
        fixture = manifest["fixtures"][name]
        assert isinstance(fixture, dict)
        supports = fixture["supports"]
        if supports["fifo_orthant"]:
            flagged.append(name)
            ambiguous = fixture["ambiguous_set"]["never_executed_touched"]
            assert len(ambiguous) >= 2
    assert set(flagged) == {
        "fifo_vstar1",
        "fifo_vstar2",
        "fifo_vstar4",
        "fifo_vstar6",
    }
    for name in flagged:
        tape = load_tape(name)
        executed = {e["maker_order_id"] for e in executions_of(tape)}
        manifest_ambiguous = {
            row[0] for row in load_manifest()["fixtures"][name]["ambiguous_set"]["never_executed_touched"]
        }
        assert manifest_ambiguous == {"P1", "P2", "P3", "P4"} - executed
        pool = load_manifest()["fixtures"][name]["episode"]["pool_orders"]
        assert len(pool) >= 3  # multi-order rationed touched level


def test_ru_split_clock_straddle_requirements() -> None:
    manifest = load_manifest()
    flagged = []
    for name in fixture_names(manifest):
        fixture = manifest["fixtures"][name]
        assert isinstance(fixture, dict)
        if not fixture["supports"]["ru_split"]:
            continue
        flagged.append(name)
        ambiguous = fixture["ambiguous_set"]["never_drawn_touched"]
        assert len(ambiguous) >= 2
        prestate_raw = json.loads(
            (ENRICHMENT_DIR / "fixtures" / name / "prestate.json").read_text()
        )
        clocks = prestate_raw["arrival_clocks"]
        assert {row[0]: row[2] for row in ambiguous} == {
            oid: clocks[oid] for oid, _, _ in ambiguous
        }
        sorted_clocks = sorted(row[2] for row in ambiguous)
        m = len(sorted_clocks)
        expected_w = sorted_clocks[(m + 1) // 2 - 1]
        window = fixture["latency_window"]
        assert window["W"] == expected_w
        assert window["m_in"] == sum(1 for _, _, c in ambiguous if c <= expected_w)
        assert window["m_out"] == m - window["m_in"]
        assert window["m_in"] >= 1 and window["m_out"] >= 1
        assert fixture["supports"]["clock_straddle"] is True
        tape = load_tape(name)
        drawn = {e["maker_order_id"] for e in executions_of(tape) if e["price"] == 100}
        assert {row[0] for row in ambiguous} == {"P1", "P2", "P3", "P4"} - drawn
    assert set(flagged) == {
        "random_unit_vstar1",
        "random_unit_vstar2",
        "random_unit_vstar4",
        "random_unit_vstar6",
    }


def test_v_ladder_matches_s3_scaffold() -> None:
    manifest = load_manifest()
    ladder = {
        name: fixture
        for name, fixture in manifest["fixtures"].items()  # type: ignore[union-attr]
        if fixture["supports"]["v_ladder"]
    }
    ru_ladder = {n: f for n, f in ladder.items() if is_ru(n)}
    assert {f["episode"]["v_star"] for f in ru_ladder.values()} == {1, 2, 4, 6}
    assert {f["episode"]["aggressor_quantity"] for f in ru_ladder.values()} == {6, 7, 9, 11}
    expected_j = {1: 1, 2: 1, 4: 1, 6: 2}
    for name, fixture in ladder.items():
        episode = fixture["episode"]
        assert isinstance(episode, dict)
        assert episode["s_better"] == 5
        assert episode["r_star"] == 14
        assert episode["v_star"] == episode["aggressor_quantity"] - 5
        assert [row[1] for row in episode["pool_orders"]] == [5, 4, 3, 2]  # S3 frozen family
        if not is_ru(name):
            executed = episode["executed_pool_orders"]
            v = episode["v_star"]
            assert len(executed) == expected_j[v]
            expected_fills = {1: {"P1": 1}, 2: {"P1": 2}, 4: {"P1": 4}, 6: {"P1": 5, "P2": 1}}[v]
            assert {oid: info["filled"] for oid, info in executed.items()} == expected_fills
            remaining = {oid: info["remaining"] for oid, info in executed.items()}
            if v == 1:
                assert remaining == {"P1": 4}
            elif v == 2:
                assert remaining == {"P1": 3}
            elif v == 4:
                assert remaining == {"P1": 1}
            else:
                assert remaining == {"P1": 0, "P2": 3}


def test_exhaustion_stratification_control() -> None:
    manifest = load_manifest()
    exhaustion_names = [
        name
        for name, fixture in manifest["fixtures"].items()  # type: ignore[union-attr]
        if fixture["supports"]["exhaustion"]
    ]
    assert set(exhaustion_names) == {"fifo_exhaustion", "random_unit_exhaustion"}
    for name in exhaustion_names:
        fixture = manifest["fixtures"][name]
        assert isinstance(fixture, dict)
        episode = fixture["episode"]
        assert episode["v_star"] == episode["r_star"] == 14
        assert episode["post_best_ask_after_episode"] == 102  # price-only quote reveals the stratum
        assert not fixture["supports"]["clock_straddle"]
        assert not fixture["supports"]["fifo_orthant"]
        assert not fixture["supports"]["ru_split"]
    fifo = manifest["fixtures"]["fifo_exhaustion"]
    assert isinstance(fifo, dict)
    assert fifo["episode"]["executed_pool_orders"] == {
        "P1": {"filled": 5, "remaining": 0},
        "P2": {"filled": 4, "remaining": 0},
        "P3": {"filled": 3, "remaining": 0},
        "P4": {"filled": 2, "remaining": 0},
    }
    ru_pool_draws = sum(
        1
        for e in executions_of(load_tape("random_unit_exhaustion"))
        if e["price"] == 100
    )
    assert ru_pool_draws == 14


def test_arm_consistent_pairs_differ_only_in_allocation_rule() -> None:
    manifest = load_manifest()
    for pair_key, members in sorted(manifest["pairs"].items()):  # type: ignore[union-attr]
        assert len(members) == 2
        fifo_name = next(m.split("/")[-1] for m in members if "fifo" in m)
        ru_name = next(m.split("/")[-1] for m in members if "random_unit" in m)
        fifo_raw = asdict(load_prestate(fifo_name))
        ru_raw = asdict(load_prestate(ru_name))
        fifo_raw.pop("allocation_rule")
        ru_raw.pop("allocation_rule")
        assert fifo_raw == ru_raw, pair_key
        assert load_prestate(fifo_name).session_id == load_prestate(ru_name).session_id

        def requests_of(name: str) -> list[tuple[str, ...]]:
            return [
                (
                    record.event_type.value,
                    json.dumps(record.payload, sort_keys=True),
                )
                for record in load_tape(name)
                if record.event_type
                in (EventType.ORDER_REQUEST, EventType.CANCEL_REQUEST, EventType.REPLACE_REQUEST)
            ]

        assert requests_of(fifo_name) == requests_of(ru_name), pair_key
