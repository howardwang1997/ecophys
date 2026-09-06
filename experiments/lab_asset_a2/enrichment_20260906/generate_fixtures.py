"""Deterministic builder for the lab-asset-v3.1 enrichment fixture bundle (PI decision D1_03).

Reads enrichment_config.json, runs the REAL scripts/lab_asset engine (CPU-only,
deterministic), validates every tape through the frozen replay contract, derives
per-episode fiber metadata (never-executed / never-drawn sets, latency window W
under the documented straddle rule), and emits fixtures/ + schema_extension.json
+ enrichment_manifest.json.

The frozen parent bundle experiments/lab_asset_a2/a2_exit_20260905/ is strictly
read-only: the generator verifies its file hashes against its own manifest and
refuses to run on any mismatch. Nothing under the parent path is ever written.

Byte-exact regeneration: the bundle is a pure function of (config, engine code,
frozen parent bundle); no timestamps or absolute paths are emitted. Re-running
this script reproduces every file sha256-identically.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lab_asset.matching import ReferenceEngine
from lab_asset.replay import ReplayReport, regenerate, replay
from lab_asset.schema import (  # noqa: E402
    AllocationRule,
    CancelRequest,
    EventType,
    InitialOrder,
    OrderRequest,
    ReplaceRequest,
    SessionPrestate,
    Side,
    ThreeClocks,
    prestate_to_json,
    record_to_json,
)

ENRICHMENT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = ENRICHMENT_DIR / "enrichment_config.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen_parent(relpath: str) -> dict[str, object]:
    """Read-only guard: verify the frozen bundle against its own manifest."""

    parent_dir = REPO_ROOT / relpath
    manifest = json.loads((parent_dir / "bundle_manifest.json").read_text())
    files = manifest["files"]
    assert isinstance(files, dict)
    assert len(files) == 7, f"expected the 7 frozen files, found {len(files)}"
    for relative, expected in sorted(files.items()):
        digest = sha256_file(parent_dir / relative)
        if digest != expected:
            raise SystemExit(f"frozen bundle tampered: {relative} {digest} != {expected}")
    return manifest


def build_prestate(cfg: dict[str, object], rule: AllocationRule, episode: dict[str, object]) -> SessionPrestate:
    cfg_book = cfg["initial_book"]
    assert isinstance(cfg_book, list)
    initial_book = tuple(
        InitialOrder(
            order_id=row["order_id"],
            actor=row["actor"],
            side=Side(row["side"]),
            price=row["price"],
            quantity=row["quantity"],
        )
        for row in cfg_book
    )
    actors = tuple(cfg["actors"])
    assert isinstance(actors, tuple)
    scheduler = cfg["scheduler"]
    assert isinstance(scheduler, dict)
    return SessionPrestate(
        session_id=str(episode["session_id"]),
        seed=int(cfg["master_seed"]),
        allocation_rule=rule,
        initial_cash={actor: int(cfg["initial_cash_per_actor"]) for actor in actors},
        initial_inventory={actor: int(cfg["initial_inventory_per_actor"]) for actor in actors},
        price_bands=(int(cfg["price_bands"][0]), int(cfg["price_bands"][1])),
        actors=actors,
        actor_roles=dict(cfg["actor_roles"]),
        scheduler_seed=int(scheduler["seed"]),
        scheduler_tick=int(scheduler["tick"]),
        scheduler_state=str(scheduler["state"]),
        assignment_key_commitment=str(cfg["assignment_key_commitment"]),
        latency_endowment=int(cfg["latency_endowment"]),
        latency_delay_by_investment=tuple(int(x) for x in cfg["latency_delay_by_investment"]),
        initial_book=initial_book,
        schema_version=str(cfg["schema_extension_label"]),
    )


def run_request_stream(cfg: dict[str, object], episode: dict[str, object], engine: ReferenceEngine) -> None:
    stream = cfg["request_stream"]
    assert isinstance(stream, list)
    for item in stream:
        assert isinstance(item, dict)
        tick = int(item["tick"])
        clocks = ThreeClocks(tick, tick, tick)
        kind = item["kind"]
        if kind == "submit":
            quantity = item["quantity"]
            if quantity == "EPISODE_QTY":
                quantity = int(episode["aggressor_quantity"])
            engine.submit(
                OrderRequest(
                    event_id=int(item["event_id"]),
                    actor=str(item["actor"]),
                    client_order_id=str(item["client_order_id"]),
                    side=Side(str(item["side"])),
                    price=int(item["price"]),
                    quantity=int(quantity),
                    clocks=clocks,
                )
            )
        elif kind == "cancel":
            engine.cancel(
                CancelRequest(
                    event_id=int(item["event_id"]),
                    actor=str(item["actor"]),
                    order_id=str(item["order_id"]),
                    clocks=clocks,
                )
            )
        elif kind == "replace":
            engine.replace(
                ReplaceRequest(
                    event_id=int(item["event_id"]),
                    actor=str(item["actor"]),
                    replaces_order_id=str(item["replaces_order_id"]),
                    client_order_id=str(item["client_order_id"]),
                    side=Side(str(item["side"])),
                    price=int(item["price"]),
                    quantity=int(item["quantity"]),
                    clocks=clocks,
                )
            )
        elif kind == "finish":
            engine.finish()
        else:
            raise ValueError(f"unknown request kind: {kind}")


def clocks_map(cfg: dict[str, object]) -> dict[str, int]:
    return {
        str(row["order_id"]): int(row["arrival_clock"])
        for row in cfg["initial_book"]
    }


def pool_orders(cfg: dict[str, object]) -> list[tuple[str, int, int]]:
    by_id = {str(row["order_id"]): row for row in cfg["initial_book"]}
    pool = cfg["pool"]
    assert isinstance(pool, dict)
    return [
        (oid, int(by_id[oid]["quantity"]), int(by_id[oid]["arrival_clock"]))
        for oid in pool["order_ids"]
    ]


def untouched_orders(cfg: dict[str, object]) -> list[tuple[str, int, int]]:
    by_id = {str(row["order_id"]): row for row in cfg["initial_book"]}
    untouched = cfg["untouched_levels"]
    assert isinstance(untouched, dict)
    return [
        (oid, int(by_id[oid]["quantity"]), int(by_id[oid]["arrival_clock"]))
        for oid in untouched["order_ids"]
    ]


def executions(engine: ReferenceEngine) -> list[dict[str, object]]:
    return [
        dict(record.payload["execution"])
        for record in engine.tape
        if record.event_type == EventType.EXECUTION
    ]


def episode_metadata(
    cfg: dict[str, object],
    episode: dict[str, object],
    engine: ReferenceEngine,
    arm_name: str,
) -> dict[str, object]:
    pool = pool_orders(cfg)
    pool_price = int(cfg["pool"]["price"])
    pool_ids = {oid for oid, _, _ in pool}
    pool_exec: dict[str, dict[str, int]] = {}
    for execution in executions(engine):
        if int(execution["price"]) == pool_price and str(execution["maker_order_id"]) in pool_ids:
            entry = pool_exec.setdefault(
                str(execution["maker_order_id"]), {"filled": 0, "remaining": None}
            )
            entry["filled"] += int(execution["quantity"])
            entry["remaining"] = int(execution["maker_remaining"])

    ambiguous_key = "never_executed_touched" if arm_name == "fifo" else "never_drawn_touched"
    ambiguous = [
        [oid, qty, clock] for oid, qty, clock in pool if oid not in pool_exec
    ]
    untouched = [[oid, qty, clock] for oid, qty, clock in untouched_orders(cfg)]

    clocks_by_id = clocks_map(cfg)
    if ambiguous:
        sorted_clocks = sorted(clock for _, _, clock in ambiguous)
        m = len(sorted_clocks)
        window = sorted_clocks[(m + 1) // 2 - 1]
        m_in = sum(1 for _, _, clock in ambiguous if clock <= window)
        m_out = m - m_in
        straddle = m_in >= 1 and m_out >= 1
    else:
        window = None
        m_in = 0
        m_out = 0
        straddle = False

    accepted = [
        record.payload
        for record in engine.tape
        if record.event_type == EventType.ORDER_ACCEPTED
    ]
    post_best_ask = accepted[-1]["post_best_ask"] if accepted else None

    supports = {
        "fifo_orthant": arm_name == "fifo" and len(ambiguous) >= 2,
        "ru_split": arm_name == "random_unit" and len(ambiguous) >= 2,
        "v_ladder": bool(episode["v_ladder"]),
        "exhaustion": bool(episode["exhaustion"]),
        "clock_straddle": straddle,
    }
    return {
        "allocation_rule": engine.prestate.allocation_rule.value,
        "session_id": engine.prestate.session_id,
        "pair_key": str(episode["pair_key"]),
        "arm": arm_name,
        "seed": int(cfg["master_seed"]),
        "records": len(engine.tape),
        "episode": {
            "aggressor_quantity": int(episode["aggressor_quantity"]),
            "aggressor_price": 100,
            "s_better": int(cfg["better_levels"]["s_better"]),
            "v_star": int(episode["v_star"]),
            "r_star": int(cfg["pool"]["r_star"]),
            "pool_price": pool_price,
            "pool_orders": [[oid, qty, clock] for oid, qty, clock in pool],
            "executed_pool_orders": {
                oid: pool_exec[oid] for oid in sorted(pool_exec)
            },
            "ambiguous_kind": "never_executed" if arm_name == "fifo" else "never_drawn",
            "post_best_ask_after_episode": post_best_ask,
        },
        "ambiguous_set": {
            "touched_level_price": pool_price,
            ambiguous_key: ambiguous,
            "never_executed_untouched": untouched,
        },
        "latency_window": {
            "rule": "touched_level_median_straddle",
            "W": window,
            "m_in": m_in,
            "m_out": m_out,
            "clock_straddle": straddle,
            "arrival_clocks": clocks_by_id,
        },
        "supports": supports,
    }


def write_fixture(
    fixture_dir: Path,
    cfg: dict[str, object],
    engine: ReferenceEngine,
) -> None:
    prestate = engine.prestate
    report: ReplayReport = replay(prestate, engine.tape)
    if not report.ok:
        raise SystemExit(f"replay failed for {prestate.session_id}: {report}")
    payload = json.loads(prestate_to_json(prestate))
    payload["arrival_clocks"] = clocks_map(cfg)
    fixture_dir.mkdir(parents=True, exist_ok=True)
    (fixture_dir / "prestate.json").write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"))
    )
    (fixture_dir / "tape.jsonl").write_text(
        "".join(record_to_json(record) + "\n" for record in engine.tape)
    )
    (fixture_dir / "replay_report.json").write_text(
        json.dumps({"ok": True, "records": len(engine.tape)}, sort_keys=True) + "\n"
    )
    regenerated = "".join(
        record_to_json(record) + "\n"
        for record in regenerate(prestate, engine.tape)
    )
    if regenerated != (fixture_dir / "tape.jsonl").read_text():
        raise SystemExit(f"byte-exact regeneration failed for {prestate.session_id}")


def build_schema_extension(cfg: dict[str, object], parent_manifest: dict[str, object]) -> dict[str, object]:
    parent_files = parent_manifest["files"]
    assert isinstance(parent_files, dict)
    return {
        "extension_label": str(cfg["schema_extension_label"]),
        "parent_schema_label": str(cfg["parent_schema_label"]),
        "parent_schema_spec_sha256": parent_files["schema_spec.json"],
        "parent_bundle_manifest_sha256": sha256_file(
            REPO_ROOT / str(cfg["parent_bundle_relpath"]) / "bundle_manifest.json"
        ),
        "kind": "backward_compatible_additive_extension",
        "fields": [
            {
                "name": "arrival_clocks",
                "location": "prestate.json top level (sibling of the lab-asset-v3 keys)",
                "type": "object mapping order_id -> integer arrival tick",
                "constraint": "keys must be exactly the initial_book order_ids of the same prestate; values are integers",
                "semantics": (
                    "tick at which the resting order was submitted to the venue "
                    "(pre-session for initial_book orders); raw-flow metadata consumed by "
                    "latency-window consumers C_lat^W and by the S1a / O-C / O-D fiber "
                    "constructions; NOT read by the v3 engine, which loads initial orders "
                    "at session start regardless of their arrival clock"
                ),
                "hash_treatment": (
                    "excluded from prestate_hash by design (the v3 state_hash binds "
                    "asdict(SessionPrestate), which does not include extension keys); file "
                    "integrity is covered by the enrichment_manifest.json sha256 entries"
                ),
                "v3_compatibility": (
                    "lab-asset-v3 prestate_from_json reads only v3 keys and ignores unknown "
                    "top-level keys, so v3 parsers and the frozen replay validator consume "
                    "v3.1 prestates unchanged; proven by re-parsing every enriched prestate "
                    "with the frozen parser and byte-exactly regenerating its tape"
                ),
            }
        ],
        "schema_version_label_policy": (
            "enriched prestates set schema_version to 'lab-asset-v3.1'; v3 consumers that do "
            "not gate on exact label equality are unaffected; consumers gating on equality "
            "must treat lab-asset-v3.1 as lab-asset-v3 plus this extension"
        ),
        "latency_window_rule": cfg["latency_window_rule"],
        "invariants": [
            "tape grammar unchanged: every enriched tape payload key is declared in the frozen schema_spec.json payload_fields",
            "deterministic replay: re-executing the recorded request events from the prestate reproduces the tape byte-for-byte",
            "arm-consistent pairs: each episode exists under both kernels with the prestate identical except allocation_rule and an identical request stream",
            "the frozen a2_exit_20260905 bundle is never mutated",
        ],
    }


def write_manifest(
    cfg: dict[str, object],
    parent_manifest: dict[str, object],
    fixture_meta: dict[str, object],
    out_dir: Path,
) -> dict[str, object]:
    parent_files = dict(parent_manifest["files"])
    files: dict[str, str] = {}
    for path in sorted(out_dir.rglob("*")):
        if (
            path.is_file()
            and path.name != "enrichment_manifest.json"
            and "__pycache__" not in path.parts
        ):
            files[str(path.relative_to(out_dir))] = sha256_file(path)
    pairs: dict[str, list[str]] = {}
    for name in sorted(fixture_meta):
        pair_key = str(fixture_meta[name]["pair_key"])
        pairs.setdefault(pair_key, []).append(f"fixtures/{name}")
    manifest: dict[str, object] = {
        "label": "lab_asset_enrichment_bundle",
        "schema_label": str(cfg["schema_extension_label"]),
        "parent_schema_label": str(cfg["parent_schema_label"]),
        "authorization": str(cfg["authorization"]),
        "engineering_only": True,
        "not_route_evidence": True,
        "read_only_parent": True,
        "master_seed": int(cfg["master_seed"]),
        "seed_derivation": str(cfg["seed_derivation_note"]),
        "pair_design": (
            "each episode exists under both allocation kernels with identical prestate "
            "except allocation_rule (identical session_id, seed, book, arrival clocks, "
            "actors) and an identical request stream"
        ),
        "parent_bundle": {
            "relpath": str(cfg["parent_bundle_relpath"]),
            "bundle_manifest_sha256": sha256_file(
                REPO_ROOT / str(cfg["parent_bundle_relpath"]) / "bundle_manifest.json"
            ),
            "schema_version": parent_manifest["schema_version"],
            "label": parent_manifest["label"],
            "files": parent_files,
            "read_only": True,
        },
        "pairs": {key: sorted(value) for key, value in sorted(pairs.items())},
        "fixtures": {name: fixture_meta[name] for name in sorted(fixture_meta)},
        "files": files,
        "tooling": {
            "generate_fixtures_sha256": sha256_file(Path(__file__).resolve()),
            "engine": "scripts/lab_asset (ReferenceEngine + replay validator), CPU-only",
        },
    }
    (out_dir / "enrichment_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    return manifest


def build_bundle(out_dir: Path) -> dict[str, object]:
    cfg = json.loads(CONFIG_PATH.read_text())
    parent_manifest = verify_frozen_parent(str(cfg["parent_bundle_relpath"]))

    out_dir.mkdir(parents=True, exist_ok=True)
    for tooling_name in ("enrichment_config.json", "generate_fixtures.py"):
        source = ENRICHMENT_DIR / tooling_name
        target = out_dir / tooling_name
        if source.resolve() != target.resolve():
            target.write_bytes(source.read_bytes())

    fixture_meta: dict[str, object] = {}
    for arm in cfg["arms"]:
        assert isinstance(arm, dict)
        rule = AllocationRule(str(arm["allocation_rule"]))
        for episode in cfg["episodes"]:
            assert isinstance(episode, dict)
            engine = ReferenceEngine(build_prestate(cfg, rule, episode))
            run_request_stream(cfg, episode, engine)
            name = f"{arm['fixture_prefix']}_{episode['name']}"
            write_fixture(out_dir / "fixtures" / str(name), cfg, engine)
            fixture_meta[str(name)] = episode_metadata(cfg, episode, engine, str(arm["name"]))

    extension = build_schema_extension(cfg, parent_manifest)
    (out_dir / "schema_extension.json").write_text(
        json.dumps(extension, indent=2, sort_keys=True) + "\n"
    )
    return write_manifest(cfg, parent_manifest, fixture_meta, out_dir)


def main() -> None:
    out_dir = ENRICHMENT_DIR
    if len(sys.argv) > 1:
        out_dir = Path(sys.argv[1]).resolve()
    manifest = build_bundle(out_dir)
    fixtures = manifest["fixtures"]
    assert isinstance(fixtures, dict)
    print(
        f"enrichment bundle written: {len(fixtures)} fixtures, "
        f"{len(manifest['files'])} hashed files -> {out_dir}"
    )


if __name__ == "__main__":
    main()
