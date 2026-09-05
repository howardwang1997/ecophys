"""A-2 exit exporter: versioned schema artifact and conformance fixture bundle.

Emits the frozen tape-grammar specification and golden fixtures (prestate + full
tape + replay verdict per scenario, both allocation arms) with a SHA-256
manifest, and self-checks that every payload key observed in fixtures is
declared in the specification. Any hardened platform fork must reproduce these
fixtures bit-for-bit to qualify as the same estimand package.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lab_asset import schema as schema_module
from lab_asset.matching import ReferenceEngine
from lab_asset.replay import replay
from lab_asset.schema import (
    AllocationRule,
    CancelRequest,
    EventType,
    LatencyChoice,
    OrderRequest,
    ReplaceRequest,
    SessionPrestate,
    Side,
    ThreeClocks,
    prestate_to_json,
    record_to_json,
)

SCHEMA_VERSION = "lab-asset-v3"

PAYLOAD_FIELDS: dict[str, list[str]] = {
    EventType.SESSION_START.value: [
        "session_id",
        "schema_version",
        "allocation_rule",
        "prestate_hash",
    ],
    EventType.LATENCY_CHOICE.value: [
        "event_id",
        "actor",
        "round_id",
        "investment",
        "resulting_delay_ticks",
        "clocks",
    ],
    EventType.LATENCY_CHOICE_REJECTED.value: [
        "rejection_id",
        "event_id",
        "actor",
        "round_id",
        "investment",
        "reason",
        "clocks",
    ],
    EventType.ORDER_REQUEST.value: [
        "event_id",
        "actor",
        "role",
        "client_order_id",
        "round_id",
        "side",
        "price",
        "quantity",
        "clocks",
    ],
    EventType.ORDER_ACCEPTED.value: [
        "client_order_id",
        "order_id",
        "resting_quantity",
        "clocks",
        "pre_best_bid",
        "pre_best_ask",
        "post_best_bid",
        "post_best_ask",
    ],
    EventType.ORDER_REJECTED.value: [
        "rejection_id",
        "client_order_id",
        "reason",
        "clocks",
        "pre_best_bid",
        "pre_best_ask",
        "post_best_bid",
        "post_best_ask",
    ],
    EventType.CANCEL_REQUEST.value: [
        "event_id",
        "actor",
        "role",
        "order_id",
        "round_id",
        "clocks",
    ],
    EventType.ORDER_CANCELLED.value: [
        "order_id",
        "actor",
        "cancelled_quantity",
        "clocks",
        "pre_best_bid",
        "pre_best_ask",
        "post_best_bid",
        "post_best_ask",
    ],
    EventType.CANCEL_REJECTED.value: [
        "rejection_id",
        "order_id",
        "reason",
        "clocks",
        "pre_best_bid",
        "pre_best_ask",
        "post_best_bid",
        "post_best_ask",
    ],
    EventType.REPLACE_REQUEST.value: [
        "event_id",
        "actor",
        "role",
        "replaces_order_id",
        "client_order_id",
        "round_id",
        "side",
        "price",
        "quantity",
        "clocks",
    ],
    EventType.ORDER_REPLACED.value: [
        "replaces_order_id",
        "replaced_quantity",
        "order_id",
        "parent_order_id",
        "lineage_root",
        "resting_quantity",
        "clocks",
        "pre_best_bid",
        "pre_best_ask",
        "post_best_bid",
        "post_best_ask",
    ],
    EventType.REPLACE_REJECTED.value: [
        "rejection_id",
        "replaces_order_id",
        "reason",
        "clocks",
        "pre_best_bid",
        "pre_best_ask",
        "post_best_bid",
        "post_best_ask",
    ],
    EventType.EXECUTION.value: [
        "execution",
        "aggressor_role",
        "maker_role",
        "allocation_draw?",
        "pre_best_bid",
        "pre_best_ask",
        "post_best_bid",
        "post_best_ask",
    ],
    EventType.SESSION_END.value: [],
}

SPEC_NOTES = {
    "identifiers": (
        "order O%08d, execution E%08d, rejection R%08d; client_order_id and "
        "event_id are client-supplied; order_parent carries replacement lineage"
    ),
    "hashes": (
        "stable_hash = sha256 of canonical JSON (sort_keys, separators (',',':')); "
        "state_hash binds prestate hash, full book with FIFO order, cash, "
        "inventory, induced counters, order metadata/status/parent, used client "
        "ids, latency choices, counters, last match tick and engine RNG state; "
        "aggregate_state_hash binds anonymous level quantities and totals only"
    ),
    "replay": (
        "re-execute the request events (order/cancel/replace/latency/session "
        "end) from the prestate; the regenerated tape must equal the recorded "
        "tape record-by-record including every state hash"
    ),
    "roles": "role resolves from the prestate actor_roles map and is never client-supplied",
    "session_id": "tape-level attribute carried by SESSION_START and the prestate hash",
}


def build_spec() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "sides": [side.value for side in Side],
        "allocation_rules": [rule.value for rule in AllocationRule],
        "event_types": [event.value for event in EventType],
        "order_rejection_reasons": [
            reason.value for reason in schema_module.RejectionReason
        ],
        "cancel_rejection_reasons": [
            reason.value for reason in schema_module.CancelRejectionReason
        ],
        "latency_rejection_reasons": [
            reason.value for reason in schema_module.LatencyChoiceRejectionReason
        ],
        "replace_rejection_reasons": [
            reason.value for reason in schema_module.ReplaceRejectionReason
        ],
        "payload_fields": {key: value for key, value in PAYLOAD_FIELDS.items()},
        "notes": SPEC_NOTES,
    }


def clocks(t: int) -> ThreeClocks:
    return ThreeClocks(client_ts=t, receipt_ts=t, match_ts=t)


def make_fixture_prestate(rule: AllocationRule, seed: int) -> SessionPrestate:
    actors = ("a", "b", "c", "d")
    return SessionPrestate(
        session_id=f"A2FIX-{rule.value}-{seed}",
        seed=seed,
        allocation_rule=rule,
        initial_cash={"a": 100_000, "b": 100_000, "c": 100_000, "d": 100_000},
        initial_inventory={"a": 100, "b": 100, "c": 100, "d": 100},
        price_bands=(90, 110),
        actors=actors,
        induced_buy_values={"a": tuple(110 for _ in range(50))},
        induced_sell_costs={"b": tuple(90 for _ in range(50))},
        information_schedule=(schema_module.InformationRelease(0, "fundamental", 100),),
        initial_book=(
            schema_module.InitialOrder("IB1", "d", Side.ASK, 103, 4),
        ),
        actor_roles={"a": "designated_maker"},
        scheduler_seed=17,
        scheduler_tick=0,
        scheduler_state="round-0-ready",
        assignment_key_commitment="a2-fixture-commitment",
        latency_endowment=2,
        latency_delay_by_investment=(5, 3, 1),
    )


def run_fixture_scenario(
    rule: AllocationRule, seed: int
) -> tuple[ReferenceEngine, bool]:
    engine = ReferenceEngine(make_fixture_prestate(rule, seed))
    t = 1
    engine.submit(OrderRequest(t, "a", "a1", Side.BID, 99, 5, clocks(t)))
    t += 1
    engine.submit(OrderRequest(t, "b", "b1", Side.ASK, 101, 4, clocks(t)))
    t += 1
    engine.submit(OrderRequest(t, "c", "c1", Side.BID, 101, 2, clocks(t)))
    t += 1
    engine.cancel(CancelRequest(t, "b", "O00000001", clocks(t)))
    t += 1
    engine.replace(
        ReplaceRequest(t, "a", "O00000001", "a2", Side.BID, 100, 3, clocks(t))
    )
    t += 1
    engine.replace(
        ReplaceRequest(t, "a", "O00000001", "a3", Side.BID, 99, 999, clocks(t))
    )
    t += 1
    engine.choose_latency(LatencyChoice(t, "b", 1, 1, clocks(t)))
    t += 1
    engine.submit(OrderRequest(t, "c", "c2", Side.BID, 90, 0, clocks(t)))
    t += 1
    engine.replace(
        ReplaceRequest(t, "b", "O00000002", "b2", Side.ASK, 102, 3, clocks(t))
    )
    t += 1
    engine.choose_latency(LatencyChoice(t, "b", 1, 0, clocks(t)))
    t += 1
    engine.finish()
    report = replay(engine.prestate, engine.tape)
    return engine, report.ok


NESTED_FIELDS: dict[str, list[str]] = {
    "clocks": ["client_ts", "receipt_ts", "match_ts"],
    "execution": [
        "event_id",
        "execution_id",
        "aggressor_order_id",
        "maker_order_id",
        "maker_actor",
        "aggressor_actor",
        "side_of_aggressor",
        "price",
        "quantity",
        "maker_remaining",
        "clocks",
        "round_id",
    ],
    "allocation_draw": ["price", "eligible_units", "selected_unit", "maker_order_id"],
}


def observed_payload_keys(engine: ReferenceEngine) -> set[tuple[str, str]]:
    from dataclasses import asdict, is_dataclass

    observed: set[tuple[str, str]] = set()

    def walk(event: str, prefix: str, value: object) -> None:
        if is_dataclass(value) and not isinstance(value, type):
            value = asdict(value)
        if isinstance(value, dict):
            for nested, item in value.items():
                walk(event, f"{prefix}.{nested}" if prefix else nested, item)
        else:
            observed.add((event, prefix))

    for record in engine.tape:
        for key, value in record.payload.items():
            walk(record.event_type.value, key, value)
    return observed


def declared_payload_keys(spec: dict[str, object]) -> set[tuple[str, str]]:
    payload_fields = spec["payload_fields"]
    assert isinstance(payload_fields, dict)
    declared: set[tuple[str, str]] = set()
    for event, fields in payload_fields.items():
        for field in fields:
            name = field.removesuffix("?")
            if name in NESTED_FIELDS:
                for nested in NESTED_FIELDS[name]:
                    if nested == "clocks":
                        for clock_key in NESTED_FIELDS["clocks"]:
                            declared.add((event, f"{name}.clocks.{clock_key}"))
                    else:
                        declared.add((event, f"{name}.{nested}"))
            else:
                declared.add((event, name))
    return declared


def check_spec_covers_fixtures(
    spec: dict[str, object], engines: list[ReferenceEngine]
) -> None:
    declared = declared_payload_keys(spec)
    for engine in engines:
        observed = observed_payload_keys(engine)
        missing = observed - declared
        if missing:
            raise SystemExit(
                f"spec missing payload fields for {engine.prestate.session_id}: "
                f"{sorted(missing)}"
            )


def write_bundle(out_dir: Path) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    spec = build_spec()
    engines: list[ReferenceEngine] = []
    fixtures: dict[str, object] = {}
    for rule in (AllocationRule.FIFO, AllocationRule.RANDOM_UNIT_WITHIN_PRICE):
        engine, ok = run_fixture_scenario(rule, seed=20260905)
        assert ok, f"fixture replay failed for {rule.value}"
        engines.append(engine)
        name = f"fixture_{rule.value}"
        fixture_dir = out_dir / name
        fixture_dir.mkdir()
        (fixture_dir / "prestate.json").write_text(prestate_to_json(engine.prestate))
        (fixture_dir / "tape.jsonl").write_text(
            "".join(record_to_json(record) + "\n" for record in engine.tape)
        )
        (fixture_dir / "replay_report.json").write_text(
            json.dumps({"ok": True, "records": len(engine.tape)}, sort_keys=True)
            + "\n"
        )
        fixtures[name] = {
            "allocation_rule": rule.value,
            "records": len(engine.tape),
        }
    check_spec_covers_fixtures(spec, engines)
    (out_dir / "schema_spec.json").write_text(
        json.dumps(spec, indent=2, sort_keys=True) + "\n"
    )
    manifest: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "label": "lab_asset_a2_exit_bundle",
        "engineering_only": True,
        "not_route_evidence": True,
        "fixtures": fixtures,
        "files": {},
    }
    for path in sorted(out_dir.rglob("*")):
        if path.is_file() and path.name != "bundle_manifest.json":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            manifest["files"][str(path.relative_to(out_dir))] = digest  # type: ignore[index]
    (out_dir / "bundle_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    return manifest


def main() -> None:
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/lab_asset_a2_exit")
    manifest = write_bundle(out_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
