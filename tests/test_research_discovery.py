from __future__ import annotations

import hashlib
import io
import json
import shutil
import subprocess
import tarfile
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest
import yaml

from scripts.quarantine_research_discovery_sandbox import (
    execute_quarantine,
    load_quarantine_plan,
)
from scripts.validate_research_discovery import (
    DiscoveryValidationError,
    validate_discovery,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CARD_ID = "transportable_interventional_market_law_discovery"
SANDBOX_ID = "disposable_market_probe"
FIXED_AS_OF = datetime(2026, 8, 25, 12, 0, tzinfo=UTC)


def load_mapping(path: Path) -> dict[str, object]:
    loaded = cast(object, yaml.safe_load(path.read_text(encoding="utf-8")))
    assert isinstance(loaded, dict)
    assert all(isinstance(key, str) for key in loaded)
    return cast(dict[str, object], loaded)


def child_mapping(parent: dict[str, object], key: str) -> dict[str, object]:
    child = parent[key]
    assert isinstance(child, dict)
    assert all(isinstance(item, str) for item in child)
    return cast(dict[str, object], child)


def child_mappings(parent: dict[str, object], key: str) -> list[dict[str, object]]:
    children = parent[key]
    assert isinstance(children, list)
    assert all(isinstance(child, dict) for child in children)
    return [cast(dict[str, object], child) for child in children]


def write_mapping(path: Path, value: dict[str, object]) -> None:
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def copy_fixture(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    discovery = repo / "research" / "discovery"
    graph_dir = repo / ".claude" / "memory"
    shutil.copytree(REPO_ROOT / "research" / "discovery", discovery)
    graph_dir.mkdir(parents=True)
    shutil.copy2(
        REPO_ROOT / ".claude" / "memory" / "research_route_knowledge_graph.yaml",
        graph_dir / "research_route_knowledge_graph.yaml",
    )
    result_dir = repo / "papers" / "proposal"
    result_dir.mkdir(parents=True)
    shutil.copy2(
        REPO_ROOT / "papers" / "proposal" / "ecomd_discovery_loop_reselection_result_2026-08-25.md",
        result_dir / "ecomd_discovery_loop_reselection_result_2026-08-25.md",
    )
    shutil.copy2(
        REPO_ROOT
        / "papers"
        / "proposal"
        / "ecomd_discovery_loop_topic_cycle_10_model_discrimination_funnel_result_2026-08-26.md",
        result_dir
        / "ecomd_discovery_loop_topic_cycle_10_model_discrimination_funnel_result_2026-08-26.md",
    )
    shutil.copy2(
        REPO_ROOT
        / "papers"
        / "proposal"
        / "ecomd_discovery_loop_topic_cycle_11_market_physical_relaxation_result_2026-08-26.md",
        result_dir
        / "ecomd_discovery_loop_topic_cycle_11_market_physical_relaxation_result_2026-08-26.md",
    )
    shutil.copy2(
        REPO_ROOT
        / "papers"
        / "proposal"
        / "ecomd_discovery_loop_topic_cycle_12_price_time_commitment_result_2026-08-26.md",
        result_dir
        / "ecomd_discovery_loop_topic_cycle_12_price_time_commitment_result_2026-08-26.md",
    )
    shutil.copy2(
        REPO_ROOT
        / "papers"
        / "proposal"
        / "ecomd_discovery_loop_topic_cycle_13_bilateral_credit_liquidity_result_2026-08-26.md",
        result_dir
        / "ecomd_discovery_loop_topic_cycle_13_bilateral_credit_liquidity_result_2026-08-26.md",
    )
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    shutil.copy2(
        REPO_ROOT / "scripts" / "quarantine_research_discovery_sandbox.py",
        scripts_dir / "quarantine_research_discovery_sandbox.py",
    )
    return repo


def card_path(repo: Path) -> Path:
    return repo / "research" / "discovery" / "cards" / f"{CARD_ID}.yaml"


def decision_path(repo: Path) -> Path:
    return repo / "research" / "discovery" / "decisions" / f"{CARD_ID}.yaml"


def novelty_path(repo: Path) -> Path:
    return repo / "research" / "discovery" / "novelty" / f"{CARD_ID}.yaml"


def history_path(repo: Path) -> Path:
    return repo / "research" / "discovery" / "decision_history.yaml"


def forecast_path(repo: Path) -> Path:
    return repo / "research" / "discovery" / "forecast_ledger.yaml"


def search_cycle_path(repo: Path) -> Path:
    return repo / "research" / "discovery" / "search_cycle_ledger.yaml"


def update_decision_hash(repo: Path) -> None:
    decision = load_mapping(decision_path(repo))
    decision["card_sha256"] = hashlib.sha256(card_path(repo).read_bytes()).hexdigest()
    write_mapping(decision_path(repo), decision)


def canonical_json(value: dict[str, object]) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def write_json(path: Path, value: dict[str, object]) -> None:
    path.write_bytes(canonical_json(value))


def sandbox_path(repo: Path, sandbox_id: str = SANDBOX_ID) -> Path:
    return repo / "research" / "discovery" / "sandboxes" / f"{sandbox_id}.yaml"


def sandbox_decision_path(repo: Path, sandbox_id: str = SANDBOX_ID) -> Path:
    return repo / "research" / "discovery" / "sandbox_decisions" / f"{sandbox_id}.yaml"


def write_event_log(path: Path, entries: list[dict[str, object]]) -> list[dict[str, object]]:
    previous: str | None = None
    encoded: list[bytes] = []
    for sequence, original in enumerate(entries):
        entry = dict(original)
        entry["schema_version"] = 1
        entry["seq"] = sequence
        entry["previous_entry_sha256"] = previous
        entry.pop("entry_sha256", None)
        digest = hashlib.sha256(canonical_json(entry)).hexdigest()
        entry["entry_sha256"] = digest
        previous = digest
        entries[sequence] = entry
        encoded.append(canonical_json(entry))
    path.write_bytes(b"\n".join(encoded) + b"\n")
    return entries


def load_event_log(path: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for raw_line in path.read_bytes().splitlines():
        loaded = json.loads(raw_line.decode("utf-8"))
        assert isinstance(loaded, dict)
        entries.append(cast(dict[str, object], loaded))
    return entries


def rehash_sandbox_authorization(repo: Path, sandbox_id: str = SANDBOX_ID) -> None:
    manifest_hash = hashlib.sha256(sandbox_path(repo, sandbox_id).read_bytes()).hexdigest()
    ledger_path = (
        repo
        / "research"
        / "discovery"
        / "sandbox_artifacts"
        / sandbox_id
        / "events.jsonl"
    )
    entries = load_event_log(ledger_path)
    assert len(entries) == 1
    entries[0]["manifest_sha256"] = manifest_hash
    write_event_log(ledger_path, entries)
    decision = load_mapping(sandbox_decision_path(repo, sandbox_id))
    decision["manifest_sha256"] = manifest_hash
    decision["genesis_entry_sha256"] = entries[0]["entry_sha256"]
    write_mapping(sandbox_decision_path(repo, sandbox_id), decision)


def add_authorized_sandbox(
    repo: Path,
    *,
    sandbox_id: str = SANDBOX_ID,
    campaign_id: str = "fixture_campaign",
    exploration_units: tuple[str, ...] = ("unit_a",),
    confirmation_units: tuple[str, ...] = ("unit_b",),
    snapshot_label: str = "fixture_asset",
    cpu_seconds: int = 3600,
    expires_at: str = "2026-08-26T01:00:00Z",
) -> None:
    discovery = repo / "research" / "discovery"
    inputs = discovery / "sandbox_inputs" / sandbox_id
    members = inputs / "members"
    artifacts = discovery / "sandbox_artifacts" / sandbox_id
    members.mkdir(parents=True)
    artifacts.mkdir(parents=True)
    provenance = inputs / "provenance.yaml"
    snapshot = inputs / "snapshot_manifest.json"
    partition = inputs / "partition.yaml"
    launcher = inputs / "sandbox_launcher.sh"
    incident_handler = repo / "scripts" / "quarantine_research_discovery_sandbox.py"
    write_mapping(
        provenance,
        {"source": "https://example.org/disposable-market-asset", "license": "CC-BY-4.0"},
    )
    write_json(snapshot, {"asset": snapshot_label, "version": "fixture_v2"})
    launcher.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    exploration_path = members / "exploration.txt"
    confirmation_path = members / "confirmation.txt"
    exploration_path.write_text("".join(f"{unit}\n" for unit in sorted(exploration_units)))
    confirmation_path.write_text("".join(f"{unit}\n" for unit in sorted(confirmation_units)))
    snapshot_sha = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    fingerprint_payload: dict[str, object] = {
        "asset_key": snapshot_label,
        "kind": "public_dataset",
        "snapshot_sha256": snapshot_sha,
        "source": "https://example.org/disposable-market-asset",
        "version": "fixture_v2",
    }
    asset_fingerprint = hashlib.sha256(canonical_json(fingerprint_payload)).hexdigest()
    write_mapping(
        partition,
        {
            "schema_version": 1,
            "sandbox_id": sandbox_id,
            "asset_fingerprint_sha256": asset_fingerprint,
            "unit_namespace": "fixture_market_sessions",
            "splits": [
                {
                    "id": "exploration",
                    "role": "exploration",
                    "members_ref": (
                        f"research/discovery/sandbox_inputs/{sandbox_id}/members/exploration.txt"
                    ),
                    "members_sha256": hashlib.sha256(exploration_path.read_bytes()).hexdigest(),
                    "member_count": len(exploration_units),
                },
                {
                    "id": "confirmation",
                    "role": "confirmation",
                    "members_ref": (
                        f"research/discovery/sandbox_inputs/{sandbox_id}/members/confirmation.txt"
                    ),
                    "members_sha256": hashlib.sha256(confirmation_path.read_bytes()).hexdigest(),
                    "member_count": len(confirmation_units),
                },
            ],
        },
    )

    sandbox = {
        "schema_version": 2,
        "id": sandbox_id,
        "campaign_id": campaign_id,
        "created_at": "2026-08-25T01:00:00Z",
        "expires_at": expires_at,
        "purpose": "Use a disposable split to test whether an asset can generate a child topic.",
        "parent_route_ids": [CARD_ID],
        "asset": {
            "key": snapshot_label,
            "kind": "public_dataset",
            "source": "https://example.org/disposable-market-asset",
            "version": "fixture_v2",
            "license": "CC-BY-4.0",
            "fingerprint_sha256": asset_fingerprint,
            "provenance": {
                "ref": f"research/discovery/sandbox_inputs/{sandbox_id}/provenance.yaml",
                "sha256": hashlib.sha256(provenance.read_bytes()).hexdigest(),
            },
            "snapshot_manifest": {
                "ref": (
                    f"research/discovery/sandbox_inputs/{sandbox_id}/snapshot_manifest.json"
                ),
                "sha256": snapshot_sha,
            },
            "state_or_observation_coverage": "Complete fixture state for the disposable split.",
            "intervention_or_search_space": "A frozen finite intervention grid.",
            "evidence_refs": ["autodiscovery"],
        },
        "partition": {
            "ref": f"research/discovery/sandbox_inputs/{sandbox_id}/partition.yaml",
            "sha256": hashlib.sha256(partition.read_bytes()).hexdigest(),
        },
        "reservation": {
            "cpu_seconds": cpu_seconds,
            "storage_bytes": 10_000_000,
            "monetary_cost_usd_micros": 0,
            "gpu_seconds": 0,
            "branches": 4,
        },
        "authorization": {
            "allowed_actions": ["disposable_outcome_inspection", "cpu_simulator_probe"],
            "forbidden_actions": [
                "confirmation_holdout_access",
                "dataset_purchase",
                "gpu_use",
                "production_model_implementation",
                "ecomd_integration",
                "external_outreach",
                "paper_claim_support",
                "topic_status_promotion",
            ],
        },
        "confirmation_contract": {
            "mode": "preexisting_unmounted",
            "derivation": None,
            "outcomes_materialized": False,
            "release_condition": "after_sandbox_terminal_and_d0_freeze",
            "controller": "fixture_holdout_keeper",
        },
        "execution_contract": {
            "executor": "oci_container",
            "launcher": {
                "ref": (
                    f"research/discovery/sandbox_inputs/{sandbox_id}/sandbox_launcher.sh"
                ),
                "sha256": hashlib.sha256(launcher.read_bytes()).hexdigest(),
            },
            "incident_handler": {
                "ref": "scripts/quarantine_research_discovery_sandbox.py",
                "sha256": hashlib.sha256(incident_handler.read_bytes()).hexdigest(),
            },
            "image_digest": f"sha256:{'1' * 64}",
            "network": "none",
            "root_filesystem": "read_only",
            "repository_tree_mount": "none",
            "input_channel": "read_only_config_with_enumerated_units_only",
            "confirmation_materialization": "not_generated_not_staged_not_mounted",
            "output_channel": "bounded_stdout_tar",
            "secrets": "none",
            "device_access": "cpu_only",
        },
        "integrity": {
            "ledger_ref": f"research/discovery/sandbox_artifacts/{sandbox_id}/events.jsonl",
            "stop_rule": "first_of_budget_expiry_forbidden_access_or_manual_close",
            "result_disposition": "child_card_d_minus_3_only",
        },
        "decision_ref": f"research/discovery/sandbox_decisions/{sandbox_id}.yaml",
    }
    sandbox_path(repo, sandbox_id).parent.mkdir(parents=True, exist_ok=True)
    write_mapping(sandbox_path(repo, sandbox_id), sandbox)
    manifest_sha = hashlib.sha256(sandbox_path(repo, sandbox_id).read_bytes()).hexdigest()
    ledger_path = artifacts / "events.jsonl"
    entries = write_event_log(
        ledger_path,
        [
            {
                "schema_version": 1,
                "seq": 0,
                "event_type": "authorized",
                "occurred_at": "2026-08-25T02:00:00Z",
                "manifest_sha256": manifest_sha,
                "previous_entry_sha256": None,
            }
        ],
    )
    decision = {
        "schema_version": 2,
        "sandbox_id": sandbox_id,
        "decision": "authorized",
        "decided_at": "2026-08-25T02:00:00Z",
        "authorized_by": "fixture_user",
        "manifest_sha256": manifest_sha,
        "genesis_entry_sha256": entries[0]["entry_sha256"],
        "rationale": "Fixture authorization for a disposable, non-confirmatory probe.",
    }
    sandbox_decision_path(repo, sandbox_id).parent.mkdir(parents=True, exist_ok=True)
    write_mapping(sandbox_decision_path(repo, sandbox_id), decision)


def close_sandbox(repo: Path, sandbox_id: str = SANDBOX_ID) -> str:
    discovery = repo / "research" / "discovery"
    manifest = load_mapping(sandbox_path(repo, sandbox_id))
    manifest_sha = hashlib.sha256(sandbox_path(repo, sandbox_id).read_bytes()).hexdigest()
    partition = child_mapping(manifest, "partition")
    artifact_root = discovery / "sandbox_artifacts" / sandbox_id
    ledger_path = artifact_root / "events.jsonl"
    entries = load_event_log(ledger_path)
    finished_entries = [entry for entry in entries if entry.get("event_type") == "branch_finished"]
    branch_ids = [cast(str, entry["branch_id"]) for entry in finished_entries]
    usage = {
        "cpu_seconds": 0,
        "storage_bytes": 0,
        "monetary_cost_usd_micros": 0,
        "gpu_seconds": 0,
        "branches": len(branch_ids),
    }
    for entry in finished_entries:
        receipt = cast(dict[str, object], entry["receipt"])
        receipt_path = repo / cast(str, receipt["ref"])
        receipt_data = cast(dict[str, object], json.loads(receipt_path.read_text(encoding="utf-8")))
        for field in ("cpu_seconds", "storage_bytes", "monetary_cost_usd_micros", "gpu_seconds"):
            usage[field] += cast(int, receipt_data[field])
    result = {
        "schema_version": 1,
        "sandbox_id": sandbox_id,
        "campaign_id": manifest["campaign_id"],
        "created_at": "2026-08-25T03:00:00Z",
        "manifest_sha256": manifest_sha,
        "partition_sha256": partition["sha256"],
        "ledger_head_before_terminal_sha256": entries[-1]["entry_sha256"],
        "outcome_status": "stopped",
        "taint": "sandbox_exploratory_tainted",
        "confirmation_accessed": False,
        "scientific_claim_support_allowed": False,
        "route_activation_allowed": False,
        "admissible_use": "screening_question_motivation_only",
        "branch_ids": branch_ids,
        "usage": usage,
        "artifacts": [],
        "summary": "Fixture sandbox closed without opening a branch.",
    }
    result_path = artifact_root / "result.yaml"
    write_mapping(result_path, result)
    result_sha = hashlib.sha256(result_path.read_bytes()).hexdigest()
    entries.append(
        {
            "schema_version": 1,
            "seq": len(entries),
            "event_type": "state_transition",
            "occurred_at": "2026-08-25T03:00:00Z",
            "from_state": "authorized",
            "to_state": "closed",
            "reason": "fixture manual close",
            "result": {
                "ref": f"research/discovery/sandbox_artifacts/{sandbox_id}/result.yaml",
                "sha256": result_sha,
            },
            "previous_entry_sha256": entries[-1]["entry_sha256"],
        }
    )
    write_event_log(ledger_path, entries)
    registry_path = discovery / "sandbox_taint_registry.yaml"
    registry = load_mapping(registry_path)
    results = registry["sandbox_results"]
    assert isinstance(results, list)
    results.append(
        {
            "id": f"{sandbox_id}_result",
            "kind": "sandbox_result",
            "sandbox_id": sandbox_id,
            "artifact_ref": f"research/discovery/sandbox_artifacts/{sandbox_id}/result.yaml",
            "artifact_sha256": result_sha,
            "derived_from": [],
            "epistemic_class": "sandbox_exploratory_tainted",
            "admissible_use": "screening_question_motivation_only",
        }
    )
    write_mapping(registry_path, registry)
    return f"{sandbox_id}_result"


def add_finished_branch(repo: Path, sandbox_id: str = SANDBOX_ID) -> None:
    artifact_root = repo / "research" / "discovery" / "sandbox_artifacts" / sandbox_id
    branch_root = artifact_root / "branches" / "branch_one"
    branch_root.mkdir(parents=True)
    code_manifest = branch_root / "code_manifest.json"
    config = branch_root / "config.yaml"
    request = branch_root / "request.yaml"
    receipt = branch_root / "receipt.json"
    output = branch_root / "bundle.tar"
    write_json(code_manifest, {"git_sha": "0" * 40, "files": []})
    write_mapping(config, {"unit_ids": ["unit_a"], "tests": ["signal_exists"]})
    payload = b"exploratory only\n"
    with tarfile.open(output, mode="w") as archive:
        member = tarfile.TarInfo("screening_summary.txt")
        member.size = len(payload)
        archive.addfile(member, io.BytesIO(payload))
    write_json(
        receipt,
        {
            "schema_version": 1,
            "sandbox_id": sandbox_id,
            "branch_id": "branch_one",
            "started_at": "2026-08-25T02:11:00Z",
            "finished_at": "2026-08-25T02:13:00Z",
            "cpu_seconds": 120,
            "storage_bytes": output.stat().st_size,
            "monetary_cost_usd_micros": 0,
            "gpu_seconds": 0,
            "run_status": "completed",
            "container_exit_code": 0,
            "wall_seconds": 120,
            "executor": "oci_container",
            "launcher_sha256": hashlib.sha256(
                (
                    repo
                    / "research"
                    / "discovery"
                    / "sandbox_inputs"
                    / sandbox_id
                    / "sandbox_launcher.sh"
                ).read_bytes()
            ).hexdigest(),
            "incident_handler_sha256": hashlib.sha256(
                (
                    repo
                    / "scripts"
                    / "quarantine_research_discovery_sandbox.py"
                ).read_bytes()
            ).hexdigest(),
            "image_digest": f"sha256:{'1' * 64}",
            "network": "none",
            "root_filesystem": "read_only",
            "repository_tree_mount": "none",
            "input_channel": "read_only_config_with_enumerated_units_only",
            "confirmation_materialization": "not_generated_not_staged_not_mounted",
            "output_channel": "bounded_stdout_tar",
            "secrets": "none",
            "device_access": "cpu_only",
        },
    )
    request_value: dict[str, object] = {
        "schema_version": 1,
        "sandbox_id": sandbox_id,
        "branch_id": "branch_one",
        "hypothesis_id": "hypothesis_one",
        "hypothesis": "A measurable signal exists on the disposable split.",
        "falsifier": "The frozen effect estimate is inside the null margin.",
        "multiplicity_family_id": "fixture_family",
        "test_ids": ["signal_exists"],
        "unit_ids": ["unit_a"],
        "cpu_seconds": 120,
        "output_bytes": 20_000,
        "code_manifest": {
            "ref": (
                f"research/discovery/sandbox_artifacts/{sandbox_id}/branches/"
                "branch_one/code_manifest.json"
            ),
            "sha256": hashlib.sha256(code_manifest.read_bytes()).hexdigest(),
        },
        "config": {
            "ref": (
                f"research/discovery/sandbox_artifacts/{sandbox_id}/branches/"
                "branch_one/config.yaml"
            ),
            "sha256": hashlib.sha256(config.read_bytes()).hexdigest(),
        },
    }
    write_mapping(request, request_value)
    ledger_path = artifact_root / "events.jsonl"
    entries = load_event_log(ledger_path)
    entries.extend(
        [
            {
                "schema_version": 1,
                "seq": len(entries),
                "event_type": "branch_opened",
                "occurred_at": "2026-08-25T02:10:00Z",
                "branch_id": "branch_one",
                "hypothesis_id": "hypothesis_one",
                "hypothesis": "A measurable signal exists on the disposable split.",
                "falsifier": "The frozen effect estimate is inside the null margin.",
                "multiplicity_family_id": "fixture_family",
                "test_ids": ["signal_exists"],
                "unit_ids": ["unit_a"],
                "cpu_seconds": 120,
                "output_bytes": 20_000,
                "code_manifest": request_value["code_manifest"],
                "config": request_value["config"],
                "request": {
                    "ref": (
                        f"research/discovery/sandbox_artifacts/{sandbox_id}/branches/"
                        "branch_one/request.yaml"
                    ),
                    "sha256": hashlib.sha256(request.read_bytes()).hexdigest(),
                },
            },
            {
                "schema_version": 1,
                "seq": len(entries) + 1,
                "event_type": "branch_finished",
                "occurred_at": "2026-08-25T02:20:00Z",
                "branch_id": "branch_one",
                "receipt": {
                    "ref": (
                        f"research/discovery/sandbox_artifacts/{sandbox_id}/branches/"
                        "branch_one/receipt.json"
                    ),
                    "sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
                },
                "artifacts": [
                    {
                        "ref": (
                            f"research/discovery/sandbox_artifacts/{sandbox_id}/branches/"
                            "branch_one/bundle.tar"
                        ),
                        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                        "bytes": output.stat().st_size,
                    }
                ],
            },
        ]
    )
    write_event_log(ledger_path, entries)


def add_open_branch(repo: Path, sandbox_id: str = SANDBOX_ID) -> None:
    add_finished_branch(repo, sandbox_id)
    artifact_root = repo / "research" / "discovery" / "sandbox_artifacts" / sandbox_id
    ledger_path = artifact_root / "events.jsonl"
    entries = load_event_log(ledger_path)
    write_event_log(ledger_path, entries[:2])
    branch_root = artifact_root / "branches" / "branch_one"
    (branch_root / "receipt.json").unlink()
    (branch_root / "bundle.tar").unlink()


def set_graph_status(repo: Path, status: str) -> None:
    path = repo / ".claude" / "memory" / "research_route_knowledge_graph.yaml"
    graph = load_mapping(path)
    nodes = child_mappings(graph, "nodes")
    node = next(candidate for candidate in nodes if candidate["id"] == CARD_ID)
    node["status"] = status
    write_mapping(path, graph)


def make_active(repo: Path) -> None:
    card = load_mapping(card_path(repo))
    card["status"] = "active"
    card["stage"] = "D0"
    card["closed_at"] = None
    hostile = child_mapping(child_mapping(card, "probabilities"), "hostile_t0")
    hostile.update({"lower": 0.20, "upper": 0.30, "point": 0.25})
    for killer in child_mappings(card, "killer_tests"):
        killer["status"] = "survived"
    contracts = child_mapping(card, "contracts")
    for simulator in child_mappings(contracts, "simulators"):
        simulator["status"] = "qualified"
    child_mapping(contracts, "real_data_bridge")["status"] = "qualified"
    for reuse in child_mappings(card, "failure_reuse"):
        reuse["disposition"] = "distinguished"
    child_mapping(card, "contamination_control")["status"] = "frozen"
    authorization = child_mapping(card, "authorization")
    authorization["authorized_actions"] = ["simulator_execution"]
    write_mapping(card_path(repo), card)

    novelty = load_mapping(novelty_path(repo))
    novelty["unresolved_direct_collisions"] = []
    write_mapping(novelty_path(repo), novelty)

    decision = load_mapping(decision_path(repo))
    decision["status"] = "active"
    decision["stage"] = "D0"
    decision["authorized_actions"] = ["simulator_execution"]
    write_mapping(decision_path(repo), decision)
    set_graph_status(repo, "active")
    history = load_mapping(history_path(repo))
    history["transitions"] = []
    write_mapping(history_path(repo), history)
    update_decision_hash(repo)


def initialize_git_base(repo: Path) -> None:
    commands = [
        ["git", "init", "-q"],
        ["git", "add", "."],
        [
            "git",
            "-c",
            "user.name=Discovery Contract Test",
            "-c",
            "user.email=discovery-contract@example.invalid",
            "commit",
            "-q",
            "-m",
            "protected base",
        ],
    ]
    for command in commands:
        subprocess.run(command, cwd=repo, check=True, capture_output=True)


def test_canonical_discovery_contract_validates() -> None:
    result = validate_discovery(REPO_ROOT)

    assert "1 cards (failed_closed=1)" in result
    assert "145 evidence records" in result
    assert "25 primary-work assignments" in result
    assert "1 status transitions" in result
    assert "0 exploration sandboxes (none)" in result
    assert "2 prospective forecasts (1 resolved; 1 T0-floor resolutions)" in result
    assert "4 prospective search cycles (48 raw questions; 0 cards)" in result


def test_authorized_disposable_exploration_sandbox_validates(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)

    result = validate_discovery(repo, as_of=FIXED_AS_OF)

    assert "1 exploration sandboxes (authorized=1)" in result


def test_protected_history_allows_append_after_separate_authorization(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    initialize_git_base(repo)
    add_finished_branch(repo)

    result = validate_discovery(repo, as_of=FIXED_AS_OF, base_ref="HEAD")

    assert "Protected sandbox history OK against HEAD: 1 inherited" in result


def test_protected_history_rejects_rewritten_forecast(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    initialize_git_base(repo)
    ledger = load_mapping(forecast_path(repo))
    child_mappings(ledger, "forecasts")[0]["point"] = 0.13
    write_mapping(forecast_path(repo), ledger)

    assert "Discovery governance OK" in validate_discovery(repo, as_of=FIXED_AS_OF)
    with pytest.raises(DiscoveryValidationError, match=r"forecast ledger.*prefix"):
        validate_discovery(repo, as_of=FIXED_AS_OF, base_ref="HEAD")


def test_protected_history_allows_appended_forecast_resolution(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    initialize_git_base(repo)
    ledger = load_mapping(forecast_path(repo))
    resolutions = ledger["resolutions"]
    assert isinstance(resolutions, list)
    resolutions.append(
        {
            "forecast_id": "cycle9_rule605_same_estimand_bridge_gate",
            "resolved_at": "2027-01-15T00:00:00Z",
            "outcome": False,
            "evidence_refs": ["cycle9_rule605_faq"],
            "rationale": "The frozen bridge rule did not pass.",
        }
    )
    write_mapping(forecast_path(repo), ledger)

    result = validate_discovery(repo, as_of=FIXED_AS_OF, base_ref="HEAD")

    assert "2 prospective forecasts (2 resolved; 1 T0-floor resolutions)" in result


def test_protected_history_rejects_rewritten_authorization(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    initialize_git_base(repo)
    sandbox = load_mapping(sandbox_path(repo))
    sandbox["purpose"] = "A rewritten purpose that remains internally hash-consistent."
    write_mapping(sandbox_path(repo), sandbox)
    rehash_sandbox_authorization(repo)

    assert "Discovery governance OK" in validate_discovery(repo, as_of=FIXED_AS_OF)
    with pytest.raises(DiscoveryValidationError, match="protected sandbox file was rewritten"):
        validate_discovery(repo, as_of=FIXED_AS_OF, base_ref="HEAD")


def test_new_sandbox_cannot_execute_in_authorization_change(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    initialize_git_base(repo)
    add_authorized_sandbox(repo)
    add_finished_branch(repo)

    assert "Discovery governance OK" in validate_discovery(repo, as_of=FIXED_AS_OF)
    with pytest.raises(DiscoveryValidationError, match="authorization-only before execution"):
        validate_discovery(repo, as_of=FIXED_AS_OF, base_ref="HEAD")


def test_runtime_contract_must_pin_an_oci_image_digest(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    sandbox = load_mapping(sandbox_path(repo))
    child_mapping(sandbox, "execution_contract")["image_digest"] = "bourse:latest"
    write_mapping(sandbox_path(repo), sandbox)
    rehash_sandbox_authorization(repo)

    with pytest.raises(DiscoveryValidationError, match="JSON schema"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_synthetic_confirmation_requires_future_public_randomness(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    sandbox = load_mapping(sandbox_path(repo))
    asset = child_mapping(sandbox, "asset")
    asset["kind"] = "synthetic_simulator"
    snapshot = child_mapping(asset, "snapshot_manifest")
    fingerprint_payload: dict[str, object] = {
        "asset_key": asset["key"],
        "kind": "synthetic_simulator",
        "snapshot_sha256": snapshot["sha256"],
        "source": asset["source"],
        "version": asset["version"],
    }
    asset["fingerprint_sha256"] = hashlib.sha256(canonical_json(fingerprint_payload)).hexdigest()
    partition_ref = child_mapping(sandbox, "partition")
    partition_path = repo / cast(str, partition_ref["ref"])
    partition = load_mapping(partition_path)
    partition["asset_fingerprint_sha256"] = asset["fingerprint_sha256"]
    write_mapping(partition_path, partition)
    partition_ref["sha256"] = hashlib.sha256(partition_path.read_bytes()).hexdigest()
    write_mapping(sandbox_path(repo), sandbox)
    rehash_sandbox_authorization(repo)

    with pytest.raises(DiscoveryValidationError, match="future public randomness"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_sandbox_exploration_and_confirmation_overlap_is_rejected(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    sandbox = load_mapping(sandbox_path(repo))
    partition_ref = child_mapping(sandbox, "partition")
    partition_path = repo / cast(str, partition_ref["ref"])
    partition = load_mapping(partition_path)
    splits = child_mappings(partition, "splits")
    confirmation_ref = cast(str, splits[1]["members_ref"])
    confirmation_path = repo / confirmation_ref
    confirmation_path.write_text("unit_a\n", encoding="utf-8")
    splits[1]["members_sha256"] = hashlib.sha256(confirmation_path.read_bytes()).hexdigest()
    write_mapping(partition_path, partition)
    partition_ref["sha256"] = hashlib.sha256(partition_path.read_bytes()).hexdigest()
    write_mapping(sandbox_path(repo), sandbox)
    rehash_sandbox_authorization(repo)

    with pytest.raises(DiscoveryValidationError, match="units in more than one split"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_sandbox_gpu_budget_is_rejected(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    sandbox = load_mapping(sandbox_path(repo))
    child_mapping(sandbox, "reservation")["gpu_seconds"] = 1
    write_mapping(sandbox_path(repo), sandbox)
    rehash_sandbox_authorization(repo)

    with pytest.raises(DiscoveryValidationError, match="JSON schema"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_expired_sandbox_without_terminal_taint_is_rejected(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo, expires_at="2026-08-25T04:00:00Z")

    with pytest.raises(DiscoveryValidationError, match="lacks a terminal result"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_sandbox_manifest_tampering_is_rejected(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    sandbox = load_mapping(sandbox_path(repo))
    sandbox["purpose"] = "Tampered after authorization."
    write_mapping(sandbox_path(repo), sandbox)

    with pytest.raises(DiscoveryValidationError, match="manifest hash mismatch"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_sandbox_provenance_hash_tampering_is_rejected(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    provenance = (
        repo
        / "research"
        / "discovery"
        / "sandbox_inputs"
        / SANDBOX_ID
        / "provenance.yaml"
    )
    write_mapping(provenance, {"source": "tampered", "license": "unknown"})

    with pytest.raises(DiscoveryValidationError, match="sha256 mismatch"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_same_asset_cannot_reset_budget_with_new_campaign(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo, sandbox_id="probe_one", campaign_id="campaign_one")
    close_sandbox(repo, "probe_one")
    add_authorized_sandbox(repo, sandbox_id="probe_two", campaign_id="campaign_two")

    with pytest.raises(DiscoveryValidationError, match="more than one sandbox campaign"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_campaign_reservations_are_cumulative(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(
        repo,
        sandbox_id="probe_one",
        cpu_seconds=20_000,
        exploration_units=("unit_a",),
        confirmation_units=("unit_b",),
    )
    close_sandbox(repo, "probe_one")
    add_authorized_sandbox(
        repo,
        sandbox_id="probe_two",
        cpu_seconds=20_000,
        exploration_units=("unit_a",),
        confirmation_units=("unit_b",),
    )

    with pytest.raises(DiscoveryValidationError, match="cumulative cpu_seconds"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_cross_sandbox_holdout_role_swap_is_rejected(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(
        repo,
        sandbox_id="probe_one",
        exploration_units=("unit_a",),
        confirmation_units=("unit_b",),
    )
    close_sandbox(repo, "probe_one")
    add_authorized_sandbox(
        repo,
        sandbox_id="probe_two",
        exploration_units=("unit_b",),
        confirmation_units=("unit_a",),
    )

    with pytest.raises(DiscoveryValidationError, match="changes exploration/confirmation role"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_closed_sandbox_result_is_registered_as_tainted_motivation(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    tainted_ref = close_sandbox(repo)
    card = load_mapping(card_path(repo))
    evidence_uses = child_mapping(card, "evidence_uses")
    evidence_uses["sandbox_motivation_refs"] = [tainted_ref]
    write_mapping(card_path(repo), card)
    update_decision_hash(repo)

    result = validate_discovery(repo, as_of=FIXED_AS_OF)

    assert "1 sandbox-tainted results" in result
    assert "1 exploration sandboxes (closed=1)" in result


def test_hash_chained_branch_receipt_and_terminal_result_validate(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    add_finished_branch(repo)
    close_sandbox(repo)

    result = validate_discovery(repo, as_of=FIXED_AS_OF)

    assert "1 sandbox-tainted results" in result


def test_interrupted_branch_is_irreversibly_quarantined(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    initialize_git_base(repo)
    add_open_branch(repo)

    def validate_at_fixture_time(
        repo_root: Path,
        *,
        base_ref: str | None = None,
    ) -> str:
        return validate_discovery(repo_root, as_of=FIXED_AS_OF, base_ref=base_ref)

    monkeypatch.setattr(
        "scripts.quarantine_research_discovery_sandbox.validate_discovery",
        validate_at_fixture_time,
    )
    monkeypatch.setattr(
        "scripts.quarantine_research_discovery_sandbox.cleanup_container",
        lambda _name: "absent",
    )
    monkeypatch.setattr(
        "scripts.quarantine_research_discovery_sandbox.utc_now",
        lambda: datetime(2026, 8, 25, 4, 0, tzinfo=UTC),
    )
    plan = load_quarantine_plan(repo, SANDBOX_ID, "branch_one", "HEAD")

    result = execute_quarantine(
        plan,
        "host_interruption",
        "Fixture host interruption after branch_opened.",
        "fixture_operator",
    )

    assert result["outcome_status"] == "quarantined"
    usage = child_mapping(result, "usage")
    assert usage["cpu_seconds"] == 120
    assert usage["storage_bytes"] == 1_020_000
    validation = validate_discovery(repo, as_of=FIXED_AS_OF, base_ref="HEAD")
    assert "1 exploration sandboxes (quarantined=1)" in validation


def test_branch_request_cannot_select_confirmation_unit(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    add_finished_branch(repo)
    branch_root = (
        repo
        / "research"
        / "discovery"
        / "sandbox_artifacts"
        / SANDBOX_ID
        / "branches"
        / "branch_one"
    )
    config_path = branch_root / "config.yaml"
    request_path = branch_root / "request.yaml"
    write_mapping(config_path, {"unit_ids": ["unit_b"], "tests": ["signal_exists"]})
    request = load_mapping(request_path)
    request["unit_ids"] = ["unit_b"]
    child_mapping(request, "config")["sha256"] = hashlib.sha256(
        config_path.read_bytes()
    ).hexdigest()
    write_mapping(request_path, request)
    ledger_path = branch_root.parents[1] / "events.jsonl"
    entries = load_event_log(ledger_path)
    entries[1]["unit_ids"] = ["unit_b"]
    entries[1]["config"] = request["config"]
    child_mapping(entries[1], "request")["sha256"] = hashlib.sha256(
        request_path.read_bytes()
    ).hexdigest()
    write_event_log(ledger_path, entries)

    with pytest.raises(DiscoveryValidationError, match="uses non-exploration units"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_branch_event_must_repeat_frozen_request(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    add_finished_branch(repo)
    ledger_path = (
        repo
        / "research"
        / "discovery"
        / "sandbox_artifacts"
        / SANDBOX_ID
        / "events.jsonl"
    )
    entries = load_event_log(ledger_path)
    entries[1]["hypothesis"] = "A post-request replacement hypothesis."
    write_event_log(ledger_path, entries)

    with pytest.raises(DiscoveryValidationError, match="differs from the frozen branch request"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_receipt_storage_must_equal_declared_artifacts(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    add_finished_branch(repo)
    branch_root = (
        repo
        / "research"
        / "discovery"
        / "sandbox_artifacts"
        / SANDBOX_ID
        / "branches"
        / "branch_one"
    )
    receipt_path = branch_root / "receipt.json"
    receipt_obj = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert isinstance(receipt_obj, dict)
    receipt = cast(dict[str, object], receipt_obj)
    receipt["storage_bytes"] = 0
    write_json(receipt_path, receipt)
    ledger_path = branch_root.parents[1] / "events.jsonl"
    entries = load_event_log(ledger_path)
    child_mapping(entries[2], "receipt")["sha256"] = hashlib.sha256(
        receipt_path.read_bytes()
    ).hexdigest()
    write_event_log(ledger_path, entries)

    with pytest.raises(DiscoveryValidationError, match="storage_bytes differs from artifacts"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_branch_ledger_hash_tampering_is_rejected(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    add_finished_branch(repo)
    ledger = (
        repo
        / "research"
        / "discovery"
        / "sandbox_artifacts"
        / SANDBOX_ID
        / "events.jsonl"
    )
    entries = load_event_log(ledger)
    entries[1]["hypothesis"] = "Post-authorization tampering."
    ledger.write_bytes(b"\n".join(canonical_json(entry) for entry in entries) + b"\n")

    with pytest.raises(DiscoveryValidationError, match="entry_sha256 mismatch"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


@pytest.mark.parametrize("field", ["d2_confirmation_refs", "paper_claim_refs"])
def test_sandbox_result_cannot_support_confirmation_or_paper_claim(
    tmp_path: Path,
    field: str,
) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    tainted_ref = close_sandbox(repo)
    card = load_mapping(card_path(repo))
    child_mapping(card, "evidence_uses")[field] = [tainted_ref]
    write_mapping(card_path(repo), card)
    update_decision_hash(repo)

    with pytest.raises(DiscoveryValidationError, match="sandbox-tainted evidence"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_sandbox_result_cannot_support_a_killer_or_decision(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    tainted_ref = close_sandbox(repo)
    card = load_mapping(card_path(repo))
    child_mappings(card, "killer_tests")[0]["evidence_refs"] = [tainted_ref]
    write_mapping(card_path(repo), card)
    update_decision_hash(repo)

    with pytest.raises(DiscoveryValidationError, match="sandbox-tainted evidence"):
        validate_discovery(repo, as_of=FIXED_AS_OF)

    card = load_mapping(card_path(repo))
    child_mappings(card, "killer_tests")[0]["evidence_refs"] = ["causal_consistency"]
    write_mapping(card_path(repo), card)
    update_decision_hash(repo)
    decision = load_mapping(decision_path(repo))
    decision["evidence_refs"] = [tainted_ref]
    write_mapping(decision_path(repo), decision)

    with pytest.raises(DiscoveryValidationError, match="sandbox-tainted evidence"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_terminal_sandbox_requires_taint_registry_entry(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    add_authorized_sandbox(repo)
    close_sandbox(repo)
    write_mapping(
        repo / "research" / "discovery" / "sandbox_taint_registry.yaml",
        {"schema_version": 1, "sandbox_results": []},
    )

    with pytest.raises(DiscoveryValidationError, match="lack taint-registry results"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_protocol_sandbox_hard_cap_cannot_be_weakened(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    path = repo / "research" / "discovery" / "protocol.yaml"
    protocol = load_mapping(path)
    child_mapping(protocol, "disposable_exploration_sandbox")["maximum_cpu_seconds"] = 28_801
    write_mapping(path, protocol)

    with pytest.raises(DiscoveryValidationError, match="must equal hard limit"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_probability_alone_cannot_terminalize_a_route(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    path = repo / "research" / "discovery" / "protocol.yaml"
    protocol = load_mapping(path)
    child_mapping(protocol, "decision_policy")["probability_alone_can_terminalize"] = True
    write_mapping(path, protocol)

    with pytest.raises(DiscoveryValidationError, match="probability alone cannot terminalize"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_probability_floor_scope_must_be_active_only(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    path = repo / "research" / "discovery" / "protocol.yaml"
    protocol = load_mapping(path)
    policy = child_mapping(protocol, "decision_policy")
    child_mapping(policy, "floor_scope")["statuses"] = ["candidate", "active"]
    write_mapping(path, protocol)

    with pytest.raises(DiscoveryValidationError, match="apply only to active status"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_forecast_interval_must_contain_point(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    ledger = load_mapping(forecast_path(repo))
    forecast = child_mappings(ledger, "forecasts")[0]
    forecast.update({"lower": 0.20, "point": 0.12, "upper": 0.25})
    write_mapping(forecast_path(repo), ledger)

    with pytest.raises(DiscoveryValidationError, match="lower <= point <= upper"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_forecast_subject_must_be_registered_route(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    ledger = load_mapping(forecast_path(repo))
    child_mappings(ledger, "forecasts")[0]["subject_route_id"] = "unknown_route"
    write_mapping(forecast_path(repo), ledger)

    with pytest.raises(DiscoveryValidationError, match="subject_route_id is unknown"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_forecast_can_resolve_only_once(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    ledger = load_mapping(forecast_path(repo))
    resolution = {
        "forecast_id": "cycle9_rule605_same_estimand_bridge_gate",
        "resolved_at": "2027-01-15T00:00:00Z",
        "outcome": False,
        "evidence_refs": ["cycle9_rule605_faq"],
        "rationale": "The frozen bridge rule did not pass.",
    }
    ledger["resolutions"] = [resolution, dict(resolution)]
    write_mapping(forecast_path(repo), ledger)

    with pytest.raises(DiscoveryValidationError, match="duplicate resolution"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_declared_json_schema_is_actually_applied(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    path = repo / "research" / "discovery" / "topic_card.schema.json"
    schema = cast(dict[str, object], json.loads(path.read_text(encoding="utf-8")))
    schema["not"] = {}
    write_json(path, schema)

    with pytest.raises(DiscoveryValidationError, match="violates JSON schema"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_boolean_schema_version_is_rejected(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    card = load_mapping(card_path(repo))
    card["schema_version"] = True
    write_mapping(card_path(repo), card)

    with pytest.raises(DiscoveryValidationError, match=r"schema_version|JSON schema"):
        validate_discovery(repo, as_of=FIXED_AS_OF)


def test_nature_scale_evidence_contract_is_required(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    path = repo / "research" / "discovery" / "protocol.yaml"
    protocol = load_mapping(path)
    del protocol["nature_scale_evidence"]
    write_mapping(path, protocol)

    with pytest.raises(DiscoveryValidationError, match="nature_scale_evidence"):
        validate_discovery(repo)


def test_topic_search_funnel_contract_is_required(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    path = repo / "research" / "discovery" / "protocol.yaml"
    protocol = load_mapping(path)
    del protocol["topic_search_funnel"]
    write_mapping(path, protocol)

    with pytest.raises(DiscoveryValidationError, match="topic_search_funnel"):
        validate_discovery(repo)


def test_cross_domain_invariance_quick_screen_is_required(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    path = repo / "research" / "discovery" / "protocol.yaml"
    protocol = load_mapping(path)
    funnel = child_mapping(protocol, "topic_search_funnel")
    requirements = funnel["quick_screen_required"]
    assert isinstance(requirements, list)
    requirements.remove("cross_domain_native_parameter_and_representation_invariance")
    write_mapping(path, protocol)

    with pytest.raises(DiscoveryValidationError, match="quick-screen requirements"):
        validate_discovery(repo)


@pytest.mark.parametrize(
    "requirement",
    [
        "same_estimand_for_claimed_model_disagreement",
        "dimensionless_parameter_completion_twin_when_claimed",
        "capacity_state_and_allocation_policy_completion_when_claimed",
    ],
)
def test_cycle12_and_cycle13_quick_screen_gates_are_required(
    tmp_path: Path,
    requirement: str,
) -> None:
    repo = copy_fixture(tmp_path)
    path = repo / "research" / "discovery" / "protocol.yaml"
    protocol = load_mapping(path)
    funnel = child_mapping(protocol, "topic_search_funnel")
    requirements = funnel["quick_screen_required"]
    assert isinstance(requirements, list)
    requirements.remove(requirement)
    write_mapping(path, protocol)

    with pytest.raises(DiscoveryValidationError, match="quick-screen requirements"):
        validate_discovery(repo)


def test_search_cycle_funnel_limit_is_enforced(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    ledger = load_mapping(search_cycle_path(repo))
    cycle = child_mappings(ledger, "cycles")[0]
    counts = child_mapping(cycle, "counts")
    counts["raw_question_programs"] = 13
    source_counts = child_mapping(cycle, "source_lane_counts")
    source_counts["unresolved_model_disagreement"] = cast(
        int,
        source_counts["unresolved_model_disagreement"],
    ) + 1
    archetype_counts = child_mapping(cycle, "archetype_counts")
    archetype_counts["theory_mechanism"] = cast(
        int,
        archetype_counts["theory_mechanism"],
    ) + 1
    dispositions = child_mapping(cycle, "final_dispositions")
    dispositions["portfolio_pruned"] = cast(int, dispositions["portfolio_pruned"]) + 1
    write_mapping(search_cycle_path(repo), ledger)

    with pytest.raises(DiscoveryValidationError, match="exceeds funnel limit"):
        validate_discovery(repo)


def test_search_cycle_probability_cannot_terminalize(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    ledger = load_mapping(search_cycle_path(repo))
    cycle = child_mappings(ledger, "cycles")[0]
    quality = child_mapping(cycle, "record_quality")
    quality["probability_only_terminalizations"] = 1
    write_mapping(search_cycle_path(repo), ledger)

    with pytest.raises(DiscoveryValidationError, match="probability alone"):
        validate_discovery(repo)


def test_fully_qualified_active_fixture_validates(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    make_active(repo)

    result = validate_discovery(repo)

    assert "1 cards (active=1)" in result


def test_card_hash_tampering_is_rejected(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    card = load_mapping(card_path(repo))
    card["title"] = "Tampered title"
    write_mapping(card_path(repo), card)

    with pytest.raises(DiscoveryValidationError, match="card_sha256 mismatch"):
        validate_discovery(repo)


def test_card_and_knowledge_graph_status_must_match(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    set_graph_status(repo, "candidate")

    with pytest.raises(DiscoveryValidationError, match="card/KG status mismatch"):
        validate_discovery(repo)


def test_decision_history_must_match_current_card_status(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    history = load_mapping(history_path(repo))
    transition = child_mappings(history, "transitions")[0]
    transition["to_status"] = "candidate"
    write_mapping(history_path(repo), history)

    with pytest.raises(DiscoveryValidationError, match="decision history/card status mismatch"):
        validate_discovery(repo)


def test_active_card_below_hostile_t0_floor_is_rejected(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    make_active(repo)
    card = load_mapping(card_path(repo))
    hostile = child_mapping(child_mapping(card, "probabilities"), "hostile_t0")
    hostile.update({"lower": 0.10, "upper": 0.30, "point": 0.20})
    write_mapping(card_path(repo), card)
    update_decision_hash(repo)

    with pytest.raises(DiscoveryValidationError, match="hostile T0 lower bound"):
        validate_discovery(repo)


def test_active_card_with_pending_killer_is_rejected(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    make_active(repo)
    card = load_mapping(card_path(repo))
    child_mappings(card, "killer_tests")[0]["status"] = "pending"
    write_mapping(card_path(repo), card)
    update_decision_hash(repo)

    with pytest.raises(DiscoveryValidationError, match="killer test not survived"):
        validate_discovery(repo)


def test_active_card_with_unresolved_direct_collision_is_rejected(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    make_active(repo)
    novelty = load_mapping(novelty_path(repo))
    novelty["unresolved_direct_collisions"] = ["causalds"]
    write_mapping(novelty_path(repo), novelty)

    with pytest.raises(DiscoveryValidationError, match="unresolved direct collisions"):
        validate_discovery(repo)


def test_active_card_without_two_qualified_lineages_is_rejected(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    make_active(repo)
    card = load_mapping(card_path(repo))
    contracts = child_mapping(card, "contracts")
    child_mappings(contracts, "simulators")[1]["status"] = "unverified"
    write_mapping(card_path(repo), card)
    update_decision_hash(repo)

    with pytest.raises(DiscoveryValidationError, match="fewer than two qualified lineages"):
        validate_discovery(repo)


def test_active_card_without_real_bridge_is_rejected(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    make_active(repo)
    card = load_mapping(card_path(repo))
    contracts = child_mapping(card, "contracts")
    child_mapping(contracts, "real_data_bridge")["status"] = "unqualified"
    write_mapping(card_path(repo), card)
    update_decision_hash(repo)

    with pytest.raises(DiscoveryValidationError, match="qualified real-data bridge"):
        validate_discovery(repo)


def test_active_card_with_blocked_failure_family_is_rejected(tmp_path: Path) -> None:
    repo = copy_fixture(tmp_path)
    make_active(repo)
    card = load_mapping(card_path(repo))
    child_mappings(card, "failure_reuse")[0]["disposition"] = "blocked"
    write_mapping(card_path(repo), card)
    update_decision_hash(repo)

    with pytest.raises(DiscoveryValidationError, match="blocked failure families"):
        validate_discovery(repo)
