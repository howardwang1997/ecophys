"""Run the frozen outcome-blind Liquity V2 agentic-priority-queue D0 audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from ecomd.data.aave_agent_guardrail import normalize_hex_data, normalize_topic
from ecomd.data.aave_qualification import canonical_sha256, normalize_address
from ecomd.data.liquity_agentic_queue import (
    decode_support_log,
    log_identity,
    summarize_agentic_queue_support,
)
from ecomd.data.sqd_portal import SqdPortalClient
from scripts.audit_aave_rate_response_d1b import (
    RpcError,
    _get_logs_with_split,
    _git,
    _keccak_topic,
    _RpcClient,
    _verify_repo,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVENT_NAMES = {
    "TroveOperation",
    "BatchedTroveUpdated",
    "BatchUpdated",
    "Redemption",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"YAML contract must be an object: {path}")
    return payload


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, UTC).isoformat()


def _source_file_audit(root: Path, expected: Mapping[str, Any]) -> dict[str, str]:
    observed: dict[str, str] = {}
    files = expected.get("files")
    if not isinstance(files, Mapping) or not files:
        raise RuntimeError("official source has no pinned file hashes")
    for relative, expected_hash in files.items():
        path = root / str(relative)
        if not path.is_file():
            raise RuntimeError(f"pinned source file is absent: {path}")
        digest = _sha256_file(path)
        if digest != str(expected_hash):
            raise RuntimeError(f"pinned source hash mismatch for {relative}: {digest} != {expected_hash}")
        observed[str(relative)] = digest
    return dict(sorted(observed.items()))


def _source_audit(
    config: Mapping[str, Any],
    *,
    bold_root: Path,
    arm_root: Path,
) -> dict[str, Any]:
    official = config["official_sources"]
    bold_expected = official["bold"]
    arm_expected = official["autonomous_rate_manager"]
    repositories = {
        "bold": _verify_repo(
            bold_root,
            str(bold_expected["expected_git_sha"]),
            label="Liquity bold",
        ),
        "autonomous_rate_manager": _verify_repo(
            arm_root,
            str(arm_expected["expected_git_sha"]),
            label="Liquity autonomous rate manager",
        ),
    }
    file_hashes = {
        "bold": _source_file_audit(bold_root, bold_expected),
        "autonomous_rate_manager": _source_file_audit(arm_root, arm_expected),
    }

    ethereum = config["ethereum"]
    address_payload = json.loads((bold_root / "contracts/addresses/1.json").read_text(encoding="utf-8"))
    if not isinstance(address_payload, Mapping):
        raise RuntimeError("official mainnet address manifest is malformed")
    raw_branches = address_payload.get("branches")
    if not isinstance(raw_branches, Sequence) or isinstance(raw_branches, (str, bytes)):
        raise RuntimeError("official mainnet address manifest has no branches")
    source_branches: dict[str, Mapping[str, Any]] = {}
    for raw_branch in raw_branches:
        if not isinstance(raw_branch, Mapping):
            raise RuntimeError("official address manifest contains a malformed branch")
        source_branches[str(raw_branch["collSymbol"])] = raw_branch
    configured_branches = ethereum["branches"]
    if set(source_branches) != set(configured_branches):
        raise RuntimeError("configured collateral branches differ from the official manifest")
    for branch, configured in configured_branches.items():
        source = source_branches[str(branch)]
        comparisons = {
            "borrower_operations": "borrowerOperations",
            "trove_manager": "troveManager",
            "sorted_troves": "sortedTroves",
        }
        for configured_key, source_key in comparisons.items():
            if normalize_address(str(configured[configured_key])) != normalize_address(
                str(source[source_key])
            ):
                raise RuntimeError(f"{branch} {configured_key} differs from official source")

    networks = json.loads((bold_root / "subgraph/networks.json").read_text(encoding="utf-8"))
    source_start = int(networks["mainnet"]["BoldToken"]["startBlock"])
    if source_start != int(ethereum["from_block"]):
        raise RuntimeError("frozen start block differs from the official subgraph start")

    interface = (bold_root / "contracts/src/Interfaces/ITroveEvents.sol").read_text(encoding="utf-8")
    abi_source = (bold_root / "frontend/app/src/abi/TroveManager.ts").read_text(encoding="utf-8")
    for event_name in REQUIRED_EVENT_NAMES:
        if f"event {event_name}(" not in interface:
            raise RuntimeError(f"{event_name} is absent from the pinned Solidity interface")
        if f'"name": "{event_name}"' not in abi_source:
            raise RuntimeError(f"{event_name} is absent from the pinned ABI")

    event_signatures = config["event_signatures"]
    if set(event_signatures) != REQUIRED_EVENT_NAMES:
        raise RuntimeError("frozen event signatures differ from the required D0 event set")
    for event_name, record in event_signatures.items():
        observed_topic = _keccak_topic(str(record["signature"]))
        if observed_topic != normalize_topic(str(record["topic0"])):
            raise RuntimeError(f"frozen topic mismatch for {event_name}")

    arm_readme = (arm_root / "README.md").read_text(encoding="utf-8")
    required_arm_fragments = {
        "Interest Rate (IR) Manager",
        "automated interest rate adjustments",
        "batch manager contracts",
    }
    missing_arm_fragments = sorted(
        fragment for fragment in required_arm_fragments if fragment not in arm_readme
    )
    if missing_arm_fragments:
        raise RuntimeError(f"pinned ARM description is missing: {missing_arm_fragments}")

    return {
        "repositories": repositories,
        "file_sha256": file_hashes,
        "branch_addresses_match_official_manifest": True,
        "subgraph_start_block_matches": True,
        "event_names_and_topics_match_pinned_source": True,
        "arm_mechanism_matches_pinned_source": True,
        "official_arm_address_binding": {
            "source_url": str(official["official_arm_directory"]["url"]),
            "retrieved_utc": str(official["official_arm_directory"]["retrieved_utc"]),
            "binding_is_documentary_not_cryptographic": True,
        },
    }


def _validate_freeze_contract(
    config: Mapping[str, Any],
    *,
    config_path: Path,
) -> dict[str, Any]:
    contract = config["contract"]
    version = int(contract["version"])
    if version == 1:
        if str(contract["status"]) != ("frozen_before_event_log_support_counts_or_any_queue_outcomes"):
            raise RuntimeError("D0 v1 lacks the required outcome-blind freeze status")
        return {"is_transport_amendment": False}
    if version == 5:
        if str(contract["status"]) != (
            "transport_only_finalized_portal_recovery_after_onfinality_overload_before_support_gate"
        ):
            raise RuntimeError("D0 v5 lacks the required finalized-Portal recovery status")
        amendment = config.get("amendment")
        if not isinstance(amendment, Mapping):
            raise RuntimeError("D0 v5 has no finalized-Portal transport record")
        expected_amendment_fields = {
            "parent_config_path",
            "parent_config_sha256",
            "scope",
            "no_scientific_field_changed",
            "support_gate_breakdown_computed_before_amendment",
            "numerical_protocol_outcome_decoded_before_amendment",
            "observations_before_amendment",
            "changed_fields",
            "official_portal_sources",
        }
        if set(amendment) != expected_amendment_fields:
            raise RuntimeError("D0 v5 amendment fields differ from the reviewed Portal schema")
        if (
            amendment.get("scope")
            != "replace_overloaded_public_json_rpc_replica_with_finalized_sqd_portal_identity_stream"
            or amendment.get("no_scientific_field_changed") is not True
            or amendment.get("support_gate_breakdown_computed_before_amendment") is not False
            or amendment.get("numerical_protocol_outcome_decoded_before_amendment") is not False
        ):
            raise RuntimeError("D0 v5 does not preserve outcome-blind scientific invariance")
        parent_relative = Path(str(amendment["parent_config_path"]))
        parent_path = (REPO_ROOT / parent_relative).resolve()
        if not parent_path.is_relative_to(REPO_ROOT) or not parent_path.is_file():
            raise RuntimeError("D0 v5 parent config is outside the repository or absent")
        parent_digest = _sha256_file(parent_path)
        if parent_digest != str(amendment["parent_config_sha256"]):
            raise RuntimeError("D0 v5 parent config digest mismatch")
        parent = _load_yaml(parent_path)
        parent_audit = _validate_freeze_contract(parent, config_path=parent_path)
        if (
            int(parent["contract"]["version"]) != 4
            or parent_audit.get("is_weight_aware_transport_recovery") is not True
        ):
            raise RuntimeError("D0 v5 parent is not the reviewed v4 recovery amendment")
        if set(config) != set(parent):
            raise RuntimeError("D0 v5 added an unreviewed top-level section")
        if set(contract) != set(parent["contract"]):
            raise RuntimeError("D0 v5 contract fields differ from its parent")
        for field in {"name", "purpose"}:
            if contract.get(field) != parent["contract"].get(field):
                raise RuntimeError(f"D0 v5 changed the contract {field}")
        invariant_sections = set(parent) - {"contract", "amendment", "transport"}
        for section in invariant_sections:
            if config.get(section) != parent.get(section):
                raise RuntimeError(f"D0 v5 changed frozen scientific section: {section}")

        transport = config["transport"]
        parent_transport = parent["transport"]
        portal_fields = {
            "replication_transport_kind",
            "replication_portal_dataset_url",
            "replication_portal_stream_endpoint",
            "replication_portal_expected_metadata",
            "replication_portal_timeout_seconds",
            "replication_portal_retry_attempts",
            "replication_portal_retry_backoff_seconds",
            "replication_legacy_rpc_fields_inactive",
        }
        if set(transport) != set(parent_transport) | portal_fields:
            raise RuntimeError("D0 v5 transport fields exceed the reviewed Portal scope")
        for field, value in parent_transport.items():
            if field != "replication_rpc" and transport.get(field) != value:
                raise RuntimeError(f"D0 v5 changed frozen parent transport field: {field}")
        inactive_fields = {
            "replication_addresses_together",
            "replication_minimum_request_interval_seconds",
            "replication_rate_limit_retries",
            "replication_split_on_exhausted_rate_limit",
            "replication_rate_limit_split_order",
            "replication_maximum_rate_limit_split_depth",
        }
        if (
            transport.get("replication_rpc") is not None
            or transport.get("replication_transport_kind") != "sqd_finalized_portal"
            or transport.get("replication_portal_dataset_url")
            != "https://portal.sqd.dev/datasets/ethereum-mainnet"
            or transport.get("replication_portal_stream_endpoint") != "finalized-stream"
            or transport.get("replication_portal_expected_metadata")
            != {"dataset": "ethereum-mainnet", "start_block": 0, "real_time": True}
            or float(transport.get("replication_portal_timeout_seconds", 0)) != 60.0
            or int(transport.get("replication_portal_retry_attempts", -1)) != 4
            or float(transport.get("replication_portal_retry_backoff_seconds", -1)) != 1.0
            or set(map(str, transport.get("replication_legacy_rpc_fields_inactive", []))) != inactive_fields
        ):
            raise RuntimeError("D0 v5 finalized-Portal settings are invalid")
        expected_changed_fields = {
            "contract.version",
            "contract.status",
            "contract.frozen_utc",
            "amendment",
            "transport.replication_rpc",
            *{f"transport.{field}" for field in portal_fields},
        }
        if set(map(str, amendment["changed_fields"])) != expected_changed_fields:
            raise RuntimeError("D0 v5 changed-fields declaration is incomplete")
        sources = amendment["official_portal_sources"]
        if (
            not isinstance(sources, Mapping)
            or sources.get("api_documentation_url")
            != "https://docs.sqd.ai/migrate-to-portal-with-real-time-data-on-evm/"
            or sources.get("portal_client_npm_package") != "@subsquid/portal-client"
            or str(sources.get("portal_client_npm_version")) != "0.4.0"
            or sources.get("portal_client_npm_shasum") != "410f563cb33776c480e36ff2146a238fe2d63663"
        ):
            raise RuntimeError("D0 v5 lacks the frozen official Portal protocol evidence")
        observations = amendment["observations_before_amendment"]
        if (
            not isinstance(observations, Mapping)
            or observations.get("support_gate_breakdown_computed") is not False
            or observations.get("numerical_protocol_outcome_decoded") is not False
        ):
            raise RuntimeError("D0 v5 pre-amendment observations violate the blind recovery scope")
        if config_path != config_path.resolve() or not config_path.is_relative_to(REPO_ROOT):
            raise RuntimeError("formal D0 config must resolve inside the repository")
        return {
            "is_transport_amendment": True,
            "is_resumable_transport_recovery": True,
            "is_finalized_portal_transport_recovery": True,
            "parent_config_path": str(parent_relative),
            "parent_config_sha256": parent_digest,
            "scientific_sections_equal_to_parent": True,
            "d0_support_breakdown_computed_before_amendment": False,
            "numerical_protocol_outcomes_decoded_before_amendment": False,
        }
    if version == 4:
        if str(contract["status"]) != (
            "transport_only_weight_aware_recovery_after_onfinality_429_before_support_gate"
        ):
            raise RuntimeError("D0 v4 lacks the required weight-aware recovery status")
        amendment = config.get("amendment")
        if not isinstance(amendment, Mapping):
            raise RuntimeError("D0 v4 has no weight-aware transport record")
        expected_amendment_fields = {
            "parent_config_path",
            "parent_config_sha256",
            "scope",
            "no_scientific_field_changed",
            "support_gate_breakdown_computed_before_amendment",
            "numerical_protocol_outcome_decoded_before_amendment",
            "observations_before_amendment",
            "changed_fields",
            "official_rate_limit_source",
        }
        if set(amendment) != expected_amendment_fields:
            raise RuntimeError("D0 v4 amendment fields differ from the reviewed recovery schema")
        if (
            amendment.get("scope")
            != "pace_replication_to_official_public_limit_and_split_overweight_log_responses"
            or amendment.get("no_scientific_field_changed") is not True
            or amendment.get("support_gate_breakdown_computed_before_amendment") is not False
            or amendment.get("numerical_protocol_outcome_decoded_before_amendment") is not False
        ):
            raise RuntimeError("D0 v4 does not preserve outcome-blind scientific invariance")
        parent_relative = Path(str(amendment["parent_config_path"]))
        parent_path = (REPO_ROOT / parent_relative).resolve()
        if not parent_path.is_relative_to(REPO_ROOT) or not parent_path.is_file():
            raise RuntimeError("D0 v4 parent config is outside the repository or absent")
        parent_digest = _sha256_file(parent_path)
        if parent_digest != str(amendment["parent_config_sha256"]):
            raise RuntimeError("D0 v4 parent config digest mismatch")
        parent = _load_yaml(parent_path)
        parent_audit = _validate_freeze_contract(parent, config_path=parent_path)
        if (
            int(parent["contract"]["version"]) != 3
            or parent_audit.get("is_resumable_transport_recovery") is not True
        ):
            raise RuntimeError("D0 v4 parent is not the reviewed v3 recovery amendment")
        if set(config) != set(parent):
            raise RuntimeError("D0 v4 added an unreviewed top-level section")
        if set(contract) != set(parent["contract"]):
            raise RuntimeError("D0 v4 contract fields differ from its parent")
        for field in {"name", "purpose"}:
            if contract.get(field) != parent["contract"].get(field):
                raise RuntimeError(f"D0 v4 changed the contract {field}")
        invariant_sections = set(parent) - {"contract", "amendment", "transport"}
        for section in invariant_sections:
            if config.get(section) != parent.get(section):
                raise RuntimeError(f"D0 v4 changed frozen scientific section: {section}")
        transport = config["transport"]
        parent_transport = parent["transport"]
        recovery_fields = {
            "replication_minimum_request_interval_seconds",
            "replication_rate_limit_retries",
            "replication_split_on_exhausted_rate_limit",
            "replication_rate_limit_split_order",
            "replication_maximum_rate_limit_split_depth",
        }
        if set(transport) != set(parent_transport) | recovery_fields:
            raise RuntimeError("D0 v4 transport fields exceed the reviewed recovery scope")
        for field, value in parent_transport.items():
            if transport.get(field) != value:
                raise RuntimeError(f"D0 v4 changed frozen parent transport field: {field}")
        if (
            float(transport["replication_minimum_request_interval_seconds"]) != 6.1
            or int(transport["replication_rate_limit_retries"]) != 2
            or transport["replication_split_on_exhausted_rate_limit"] is not True
            or list(transport["replication_rate_limit_split_order"]) != ["addresses", "block_range"]
            or int(transport["replication_maximum_rate_limit_split_depth"]) != 32
        ):
            raise RuntimeError("D0 v4 weight-aware recovery settings are invalid")
        expected_changed_fields = {
            "contract.version",
            "contract.status",
            "contract.frozen_utc",
            "amendment",
            "transport.replication_minimum_request_interval_seconds",
            "transport.replication_rate_limit_retries",
            "transport.replication_split_on_exhausted_rate_limit",
            "transport.replication_rate_limit_split_order",
            "transport.replication_maximum_rate_limit_split_depth",
        }
        if set(map(str, amendment["changed_fields"])) != expected_changed_fields:
            raise RuntimeError("D0 v4 changed-fields declaration is incomplete")
        source = amendment["official_rate_limit_source"]
        if (
            not isinstance(source, Mapping)
            or source.get("url") != "https://documentation.onfinality.io/support/public-rate-limits"
            or int(source.get("ethereum_response_units_per_minute", -1)) != 10
            or int(source.get("ethereum_burst_response_units", -1)) != 10
        ):
            raise RuntimeError("D0 v4 lacks the frozen official Ethereum public-limit evidence")
        observations = amendment["observations_before_amendment"]
        if (
            not isinstance(observations, Mapping)
            or observations.get("support_gate_breakdown_computed") is not False
            or observations.get("numerical_protocol_outcome_decoded") is not False
        ):
            raise RuntimeError("D0 v4 pre-amendment observations violate the blind recovery scope")
        if config_path != config_path.resolve() or not config_path.is_relative_to(REPO_ROOT):
            raise RuntimeError("formal D0 config must resolve inside the repository")
        return {
            "is_transport_amendment": True,
            "is_resumable_transport_recovery": True,
            "is_weight_aware_transport_recovery": True,
            "parent_config_path": str(parent_relative),
            "parent_config_sha256": parent_digest,
            "scientific_sections_equal_to_parent": True,
            "d0_support_breakdown_computed_before_amendment": False,
            "numerical_protocol_outcomes_decoded_before_amendment": False,
        }
    if version == 3:
        if str(contract["status"]) != (
            "transport_only_recovery_after_onfinality_rate_limit_before_support_gate"
        ):
            raise RuntimeError("D0 v3 lacks the required transport-recovery status")
        amendment = config.get("amendment")
        if not isinstance(amendment, Mapping):
            raise RuntimeError("D0 v3 has no transport-recovery record")
        expected_amendment_fields = {
            "parent_config_path",
            "parent_config_sha256",
            "scope",
            "no_scientific_field_changed",
            "support_gate_breakdown_computed_before_amendment",
            "numerical_protocol_outcome_decoded_before_amendment",
            "observations_before_amendment",
            "changed_fields",
        }
        if set(amendment) != expected_amendment_fields:
            raise RuntimeError("D0 v3 amendment fields differ from the reviewed recovery schema")
        if (
            amendment.get("scope")
            != "make_onfinality_replication_resumable_and_reduce_requests_without_changing_coverage"
            or amendment.get("no_scientific_field_changed") is not True
            or amendment.get("support_gate_breakdown_computed_before_amendment") is not False
            or amendment.get("numerical_protocol_outcome_decoded_before_amendment") is not False
        ):
            raise RuntimeError("D0 v3 does not preserve outcome-blind scientific invariance")
        parent_relative = Path(str(amendment["parent_config_path"]))
        parent_path = (REPO_ROOT / parent_relative).resolve()
        if not parent_path.is_relative_to(REPO_ROOT) or not parent_path.is_file():
            raise RuntimeError("D0 v3 parent config is outside the repository or absent")
        parent_digest = _sha256_file(parent_path)
        if parent_digest != str(amendment["parent_config_sha256"]):
            raise RuntimeError("D0 v3 parent config digest mismatch")
        parent = _load_yaml(parent_path)
        parent_audit = _validate_freeze_contract(parent, config_path=parent_path)
        if int(parent["contract"]["version"]) != 2 or parent_audit.get("is_transport_amendment") is not True:
            raise RuntimeError("D0 v3 parent is not the reviewed v2 transport amendment")
        if set(config) != set(parent):
            raise RuntimeError("D0 v3 added an unreviewed top-level section")
        if set(contract) != set(parent["contract"]):
            raise RuntimeError("D0 v3 contract fields differ from its parent")
        for field in {"name", "purpose"}:
            if contract.get(field) != parent["contract"].get(field):
                raise RuntimeError(f"D0 v3 changed the contract {field}")
        invariant_sections = set(parent) - {"contract", "amendment", "transport"}
        for section in invariant_sections:
            if config.get(section) != parent.get(section):
                raise RuntimeError(f"D0 v3 changed frozen scientific section: {section}")
        transport = config["transport"]
        parent_transport = parent["transport"]
        recovery_fields = {
            "replication_addresses_together",
            "replication_checkpoint_schema_version",
            "replication_checkpoint_every_chunks",
        }
        if set(transport) != set(parent_transport) | recovery_fields:
            raise RuntimeError("D0 v3 transport fields exceed the reviewed recovery scope")
        for field, value in parent_transport.items():
            if transport.get(field) != value:
                raise RuntimeError(f"D0 v3 changed frozen parent transport field: {field}")
        if (
            transport["replication_addresses_together"] is not True
            or int(transport["replication_checkpoint_schema_version"]) != 1
            or int(transport["replication_checkpoint_every_chunks"]) != 1
        ):
            raise RuntimeError("D0 v3 recovery transport settings are invalid")
        expected_changed_fields = {
            "contract.version",
            "contract.status",
            "contract.frozen_utc",
            "amendment",
            "transport.replication_addresses_together",
            "transport.replication_checkpoint_schema_version",
            "transport.replication_checkpoint_every_chunks",
        }
        if set(map(str, amendment["changed_fields"])) != expected_changed_fields:
            raise RuntimeError("D0 v3 changed-fields declaration is incomplete")
        observations = amendment["observations_before_amendment"]
        if (
            not isinstance(observations, Mapping)
            or observations.get("support_gate_breakdown_computed") is not False
            or observations.get("numerical_protocol_outcome_decoded") is not False
        ):
            raise RuntimeError("D0 v3 pre-amendment observations violate the blind recovery scope")
        if config_path != config_path.resolve() or not config_path.is_relative_to(REPO_ROOT):
            raise RuntimeError("formal D0 config must resolve inside the repository")
        return {
            "is_transport_amendment": True,
            "is_resumable_transport_recovery": True,
            "parent_config_path": str(parent_relative),
            "parent_config_sha256": parent_digest,
            "scientific_sections_equal_to_parent": True,
            "d0_support_breakdown_computed_before_amendment": False,
            "numerical_protocol_outcomes_decoded_before_amendment": False,
        }
    if version != 2 or str(contract["status"]) != (
        "transport_only_amendment_after_drpc_identity_omission_before_support_gate"
    ):
        raise RuntimeError("unsupported Liquity D0 contract version or status")

    amendment = config.get("amendment")
    if not isinstance(amendment, Mapping):
        raise RuntimeError("D0 v2 has no transport-amendment record")
    if (
        amendment.get("no_scientific_field_changed") is not True
        or amendment.get("support_gate_breakdown_computed_before_amendment") is not False
        or amendment.get("numerical_protocol_outcome_decoded_before_amendment") is not False
    ):
        raise RuntimeError("D0 v2 does not preserve outcome-blind scientific invariance")
    parent_relative = Path(str(amendment["parent_config_path"]))
    parent_path = (REPO_ROOT / parent_relative).resolve()
    if not parent_path.is_relative_to(REPO_ROOT) or not parent_path.is_file():
        raise RuntimeError("D0 v2 parent config is outside the repository or absent")
    parent_digest = _sha256_file(parent_path)
    if parent_digest != str(amendment["parent_config_sha256"]):
        raise RuntimeError("D0 v2 parent config digest mismatch")
    parent = _load_yaml(parent_path)
    if int(parent["contract"]["version"]) != 1 or str(parent["contract"]["status"]) != (
        "frozen_before_event_log_support_counts_or_any_queue_outcomes"
    ):
        raise RuntimeError("D0 v2 parent is not the original outcome-blind version")
    if str(contract["name"]) != str(parent["contract"]["name"]) or str(contract["purpose"]) != str(
        parent["contract"]["purpose"]
    ):
        raise RuntimeError("D0 v2 changed the contract name or scientific purpose")
    if set(config) != set(parent) | {"amendment"}:
        raise RuntimeError("D0 v2 added an unreviewed top-level section")

    invariant_sections = {
        "official_sources",
        "ethereum",
        "event_signatures",
        "operation_codes",
        "support_window",
        "pass_thresholds",
        "forbidden_before_d0_pass",
        "stop_rules",
        "resources",
    }
    for section in invariant_sections:
        if config.get(section) != parent.get(section):
            raise RuntimeError(f"D0 v2 changed frozen scientific section: {section}")
    invariant_transport_fields = {
        "formal_rpc",
        "rpc_is_replaceable_transport",
        "minimum_request_interval_seconds",
        "rate_limit_retries",
        "rate_limit_backoff_initial_seconds",
        "rate_limit_backoff_max_seconds",
        "maximum_get_logs_span",
        "full_log_identity_replication_required",
        "qualification_shards_frozen_without_event_counts",
        "minimum_nonempty_qualification_shards",
    }
    transport = config["transport"]
    parent_transport = parent["transport"]
    if set(transport) != set(parent_transport) | {
        "state_witness_rpc",
        "preformal_identity_diagnostics",
    }:
        raise RuntimeError("D0 v2 transport fields exceed the frozen amendment scope")
    for field in invariant_transport_fields:
        if transport.get(field) != parent_transport.get(field):
            raise RuntimeError(f"D0 v2 changed frozen transport protocol field: {field}")
    if str(transport["state_witness_rpc"]) != str(parent_transport["replication_rpc"]):
        raise RuntimeError("D0 v2 did not preserve dRPC as the state witness")
    if str(transport["replication_rpc"]) == str(parent_transport["replication_rpc"]):
        raise RuntimeError("D0 v2 did not replace the disqualified log replication RPC")
    if config_path != config_path.resolve() or not config_path.is_relative_to(REPO_ROOT):
        raise RuntimeError("formal D0 config must resolve inside the repository")
    return {
        "is_transport_amendment": True,
        "parent_config_path": str(parent_relative),
        "parent_config_sha256": parent_digest,
        "scientific_sections_equal_to_parent": True,
        "d0_support_breakdown_computed_before_amendment": False,
        "numerical_protocol_outcomes_decoded_before_amendment": False,
    }


def _rpc_client(
    url: str,
    transport: Mapping[str, Any],
    *,
    minimum_request_interval_seconds: float | None = None,
    rate_limit_retries: int | None = None,
) -> _RpcClient:
    return _RpcClient(
        url=url,
        timeout=60,
        transport_retries=3,
        minimum_request_interval_seconds=(
            float(transport["minimum_request_interval_seconds"])
            if minimum_request_interval_seconds is None
            else minimum_request_interval_seconds
        ),
        rate_limit_retries=(
            int(transport["rate_limit_retries"]) if rate_limit_retries is None else rate_limit_retries
        ),
        rate_limit_backoff_initial_seconds=float(transport["rate_limit_backoff_initial_seconds"]),
        rate_limit_backoff_max_seconds=float(transport["rate_limit_backoff_max_seconds"]),
    )


def _query_logs(
    client: _RpcClient,
    *,
    addresses: Sequence[str],
    topics: Sequence[str],
    from_block: int,
    to_block: int,
    maximum_span: int,
    label: str,
    addresses_together: bool = False,
) -> list[Mapping[str, Any]]:
    if maximum_span <= 0:
        raise ValueError("maximum log span must be positive")
    logs: list[Mapping[str, Any]] = []
    chunk_count = (to_block - from_block) // maximum_span + 1
    address_groups = [list(addresses)] if addresses_together else [[address] for address in addresses]
    for chunk_index, start in enumerate(range(from_block, to_block + 1, maximum_span), start=1):
        end = min(start + maximum_span - 1, to_block)
        for address_group in address_groups:
            logs.extend(
                _get_logs_with_split(
                    client,
                    addresses=address_group,
                    topics=topics,
                    start_block=start,
                    end_block_inclusive=end,
                    remaining_split_depth=24,
                    split_topics_first=True,
                )
            )
        if chunk_index == 1 or chunk_index % 25 == 0 or chunk_index == chunk_count:
            print(
                f"{label}: {chunk_index}/{chunk_count} chunks x {len(address_groups)} address filters, "
                f"{len(logs)} logs",
                flush=True,
            )
    return logs


def _checkpoint_event(event: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "block_number": int(event["block_number"]),
        "block_hash": normalize_topic(str(event["block_hash"])),
        "transaction_hash": normalize_topic(str(event["transaction_hash"])),
        "log_index": int(event["log_index"]),
        "contract_address": normalize_address(str(event["contract_address"])),
        "topic0": normalize_topic(str(event["topic0"])),
    }


def _get_replica_logs_with_rate_limit_split(
    client: _RpcClient,
    *,
    addresses: Sequence[str],
    topics: Sequence[str],
    start_block: int,
    end_block_inclusive: int,
    remaining_split_depth: int,
    split_counts: Counter[str],
) -> list[Mapping[str, Any]]:
    try:
        return _get_logs_with_split(
            client,
            addresses=addresses,
            topics=topics,
            start_block=start_block,
            end_block_inclusive=end_block_inclusive,
            remaining_split_depth=24,
            split_topics_first=True,
        )
    except RpcError as error:
        rate_limited = error.http_status == 429 or error.rpc_code == -32029
        if not rate_limited or remaining_split_depth <= 0:
            raise
        if len(addresses) > 1:
            split_counts["address"] += 1
            middle = len(addresses) // 2
            print(
                f"full.replica: rate-limit split {len(addresses)} addresses at "
                f"blocks {start_block}-{end_block_inclusive}",
                flush=True,
            )
            return _get_replica_logs_with_rate_limit_split(
                client,
                addresses=addresses[:middle],
                topics=topics,
                start_block=start_block,
                end_block_inclusive=end_block_inclusive,
                remaining_split_depth=remaining_split_depth - 1,
                split_counts=split_counts,
            ) + _get_replica_logs_with_rate_limit_split(
                client,
                addresses=addresses[middle:],
                topics=topics,
                start_block=start_block,
                end_block_inclusive=end_block_inclusive,
                remaining_split_depth=remaining_split_depth - 1,
                split_counts=split_counts,
            )
        if start_block < end_block_inclusive:
            split_counts["block_range"] += 1
            middle_block = (start_block + end_block_inclusive) // 2
            print(
                f"full.replica: rate-limit split blocks {start_block}-{end_block_inclusive} "
                f"at {middle_block}",
                flush=True,
            )
            return _get_replica_logs_with_rate_limit_split(
                client,
                addresses=addresses,
                topics=topics,
                start_block=start_block,
                end_block_inclusive=middle_block,
                remaining_split_depth=remaining_split_depth - 1,
                split_counts=split_counts,
            ) + _get_replica_logs_with_rate_limit_split(
                client,
                addresses=addresses,
                topics=topics,
                start_block=middle_block + 1,
                end_block_inclusive=end_block_inclusive,
                remaining_split_depth=remaining_split_depth - 1,
                split_counts=split_counts,
            )
        raise


def _write_replica_checkpoint(path: Path, payload: Mapping[str, Any]) -> str:
    body = dict(payload)
    body.pop("canonical_payload_sha256", None)
    digest = canonical_sha256(body)
    serialized = {**body, "canonical_payload_sha256": digest}
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(serialized, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return digest


def _validate_checkpoint_chunks(
    chunks: Any,
    *,
    from_block: int,
    to_block: int,
    maximum_span: int,
    addresses: Sequence[str],
    topics: Sequence[str],
) -> list[dict[str, Any]]:
    if not isinstance(chunks, list):
        raise RuntimeError("replica checkpoint chunks are not a list")
    allowed_addresses = {normalize_address(address) for address in addresses}
    allowed_topics = {normalize_topic(topic) for topic in topics}
    normalized_chunks: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int, str, str]] = set()
    expected_event_fields = {
        "block_number",
        "block_hash",
        "transaction_hash",
        "log_index",
        "contract_address",
        "topic0",
    }
    for expected_index, chunk in enumerate(chunks, start=1):
        if not isinstance(chunk, Mapping):
            raise RuntimeError("replica checkpoint chunk is not an object")
        expected_start = from_block + (expected_index - 1) * maximum_span
        expected_end = min(expected_start + maximum_span - 1, to_block)
        if set(chunk) != {
            "chunk_index",
            "from_block",
            "to_block",
            "event_count",
            "events",
            "canonical_log_identity_sha256",
        }:
            raise RuntimeError("replica checkpoint chunk fields differ from schema")
        if (
            int(chunk["chunk_index"]) != expected_index
            or int(chunk["from_block"]) != expected_start
            or int(chunk["to_block"]) != expected_end
        ):
            raise RuntimeError("replica checkpoint chunks are not a contiguous frozen prefix")
        events = chunk["events"]
        if not isinstance(events, list) or int(chunk["event_count"]) != len(events):
            raise RuntimeError("replica checkpoint event count is invalid")
        normalized_events: list[dict[str, Any]] = []
        for event in events:
            if not isinstance(event, Mapping) or set(event) != expected_event_fields:
                raise RuntimeError("replica checkpoint event fields differ from schema")
            normalized = _checkpoint_event(event)
            if normalized != dict(event):
                raise RuntimeError("replica checkpoint event is not canonically encoded")
            if not expected_start <= int(normalized["block_number"]) <= expected_end:
                raise RuntimeError("replica checkpoint event lies outside its chunk")
            if normalized["contract_address"] not in allowed_addresses:
                raise RuntimeError("replica checkpoint contains an unexpected address")
            if normalized["topic0"] not in allowed_topics:
                raise RuntimeError("replica checkpoint contains an unexpected topic")
            identity = log_identity(normalized)
            if identity in seen:
                raise RuntimeError("replica checkpoint contains duplicate log identities")
            seen.add(identity)
            normalized_events.append(normalized)
        normalized_events.sort(key=log_identity)
        digest = _identity_digest(normalized_events)
        if digest != str(chunk["canonical_log_identity_sha256"]):
            raise RuntimeError("replica checkpoint chunk identity digest mismatch")
        normalized_chunks.append(
            {
                "chunk_index": expected_index,
                "from_block": expected_start,
                "to_block": expected_end,
                "event_count": len(normalized_events),
                "events": normalized_events,
                "canonical_log_identity_sha256": digest,
            }
        )
    return normalized_chunks


def _load_replica_checkpoint(
    path: Path,
    *,
    expected_identity: Mapping[str, Any],
    from_block: int,
    to_block: int,
    maximum_span: int,
    addresses: Sequence[str],
    topics: Sequence[str],
) -> dict[str, Any]:
    if not path.exists():
        return {
            "schema_version": 1,
            "identity": dict(expected_identity),
            "completed_chunks": [],
            "contains_only_sanitized_log_identity_fields": True,
            "raw_rpc_responses_persisted": False,
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping) or set(payload) != {
        "schema_version",
        "identity",
        "completed_chunks",
        "contains_only_sanitized_log_identity_fields",
        "raw_rpc_responses_persisted",
        "canonical_payload_sha256",
    }:
        raise RuntimeError("replica checkpoint top-level schema is invalid")
    body = {key: value for key, value in payload.items() if key != "canonical_payload_sha256"}
    if canonical_sha256(body) != str(payload["canonical_payload_sha256"]):
        raise RuntimeError("replica checkpoint payload digest mismatch")
    if (
        int(payload["schema_version"]) != 1
        or payload["identity"] != dict(expected_identity)
        or payload["contains_only_sanitized_log_identity_fields"] is not True
        or payload["raw_rpc_responses_persisted"] is not False
    ):
        raise RuntimeError("replica checkpoint identity or blinding contract is invalid")
    chunks = _validate_checkpoint_chunks(
        payload["completed_chunks"],
        from_block=from_block,
        to_block=to_block,
        maximum_span=maximum_span,
        addresses=addresses,
        topics=topics,
    )
    return {**body, "completed_chunks": chunks}


def _query_replica_with_checkpoint(
    client: _RpcClient,
    *,
    checkpoint_path: Path,
    checkpoint_identity: Mapping[str, Any],
    addresses: Sequence[str],
    topics: Sequence[str],
    branches_by_trove_manager: Mapping[str, str],
    signatures_by_topic: Mapping[str, str],
    trove_operations_by_code: Mapping[int, str],
    batch_operations_by_code: Mapping[int, str],
    from_block: int,
    to_block: int,
    maximum_span: int,
    split_on_exhausted_rate_limit: bool,
    maximum_rate_limit_split_depth: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if checkpoint_path.is_relative_to(REPO_ROOT):
        raise RuntimeError("formal replica checkpoint must be outside the Git worktree")
    payload = _load_replica_checkpoint(
        checkpoint_path,
        expected_identity=checkpoint_identity,
        from_block=from_block,
        to_block=to_block,
        maximum_span=maximum_span,
        addresses=addresses,
        topics=topics,
    )
    chunks = list(payload["completed_chunks"])
    resumed_chunks = len(chunks)
    events = [dict(event) for chunk in chunks for event in chunk["events"]]
    seen = set(map(log_identity, events))
    split_counts: Counter[str] = Counter()
    chunk_count = (to_block - from_block) // maximum_span + 1
    if resumed_chunks:
        print(
            f"full.replica: resuming after {resumed_chunks}/{chunk_count} verified chunks, "
            f"{len(events)} logs",
            flush=True,
        )
    for chunk_index in range(resumed_chunks + 1, chunk_count + 1):
        start = from_block + (chunk_index - 1) * maximum_span
        end = min(start + maximum_span - 1, to_block)
        if split_on_exhausted_rate_limit:
            raw = _get_replica_logs_with_rate_limit_split(
                client,
                addresses=addresses,
                topics=topics,
                start_block=start,
                end_block_inclusive=end,
                remaining_split_depth=maximum_rate_limit_split_depth,
                split_counts=split_counts,
            )
        else:
            raw = _get_logs_with_split(
                client,
                addresses=addresses,
                topics=topics,
                start_block=start,
                end_block_inclusive=end,
                remaining_split_depth=24,
                split_topics_first=True,
            )
        decoded = _decode_logs(
            raw,
            branches_by_trove_manager=branches_by_trove_manager,
            signatures_by_topic=signatures_by_topic,
            trove_operations_by_code=trove_operations_by_code,
            batch_operations_by_code=batch_operations_by_code,
            from_block=start,
            to_block=end,
        )
        sanitized = sorted((_checkpoint_event(event) for event in decoded), key=log_identity)
        identities = set(map(log_identity, sanitized))
        if seen & identities:
            raise RuntimeError("replica checkpoint query produced duplicate cross-chunk identities")
        seen.update(identities)
        events.extend(sanitized)
        chunk = {
            "chunk_index": chunk_index,
            "from_block": start,
            "to_block": end,
            "event_count": len(sanitized),
            "events": sanitized,
            "canonical_log_identity_sha256": _identity_digest(sanitized),
        }
        chunks.append(chunk)
        payload = {**payload, "completed_chunks": chunks}
        checkpoint_digest = _write_replica_checkpoint(checkpoint_path, payload)
        if chunk_index == 1 or chunk_index % 25 == 0 or chunk_index == chunk_count:
            print(
                f"full.replica: {chunk_index}/{chunk_count} chunks x 1 address filter, "
                f"{len(events)} logs; checkpoint={checkpoint_digest[:12]}",
                flush=True,
            )
    final_digest = _write_replica_checkpoint(checkpoint_path, payload)
    return events, {
        "schema_version": 1,
        "resumed_chunks_at_start": resumed_chunks,
        "completed_chunks": len(chunks),
        "canonical_payload_sha256": final_digest,
        "contains_only_sanitized_log_identity_fields": True,
        "raw_rpc_responses_persisted": False,
        "path_outside_git_worktree": True,
        "reported_replica_request_stats_cover_current_attempt_only": True,
        "rate_limit_split_counts_current_attempt": dict(sorted(split_counts.items())),
    }


def _query_portal_with_checkpoint(
    client: SqdPortalClient,
    *,
    checkpoint_path: Path,
    checkpoint_identity: Mapping[str, Any],
    addresses: Sequence[str],
    topics: Sequence[str],
    from_block: int,
    to_block: int,
    maximum_span: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if checkpoint_path.is_relative_to(REPO_ROOT):
        raise RuntimeError("formal replica checkpoint must be outside the Git worktree")
    payload = _load_replica_checkpoint(
        checkpoint_path,
        expected_identity=checkpoint_identity,
        from_block=from_block,
        to_block=to_block,
        maximum_span=maximum_span,
        addresses=addresses,
        topics=topics,
    )
    chunks = list(payload["completed_chunks"])
    resumed_chunks = len(chunks)
    events = [dict(event) for chunk in chunks for event in chunk["events"]]
    seen = set(map(log_identity, events))
    chunk_count = (to_block - from_block) // maximum_span + 1
    portal_stats: Counter[str] = Counter()
    if resumed_chunks:
        print(
            f"full.replica: resuming after {resumed_chunks}/{chunk_count} verified chunks, "
            f"{len(events)} logs",
            flush=True,
        )
    for chunk_index in range(resumed_chunks + 1, chunk_count + 1):
        start = from_block + (chunk_index - 1) * maximum_span
        end = min(start + maximum_span - 1, to_block)
        queried, stats = client.finalized_log_identities(
            addresses=addresses,
            topics=topics,
            from_block=start,
            to_block=end,
        )
        portal_stats.update(stats)
        sanitized = sorted((_checkpoint_event(event) for event in queried), key=log_identity)
        identities = set(map(log_identity, sanitized))
        if seen & identities:
            raise RuntimeError("Portal checkpoint query produced duplicate cross-chunk identities")
        seen.update(identities)
        events.extend(sanitized)
        chunk = {
            "chunk_index": chunk_index,
            "from_block": start,
            "to_block": end,
            "event_count": len(sanitized),
            "events": sanitized,
            "canonical_log_identity_sha256": _identity_digest(sanitized),
        }
        chunks.append(chunk)
        payload = {**payload, "completed_chunks": chunks}
        checkpoint_digest = _write_replica_checkpoint(checkpoint_path, payload)
        if chunk_index == 1 or chunk_index % 25 == 0 or chunk_index == chunk_count:
            print(
                f"full.replica: {chunk_index}/{chunk_count} chunks via finalized Portal, "
                f"{len(events)} logs; checkpoint={checkpoint_digest[:12]}",
                flush=True,
            )
    final_digest = _write_replica_checkpoint(checkpoint_path, payload)
    return events, {
        "schema_version": 1,
        "resumed_chunks_at_start": resumed_chunks,
        "completed_chunks": len(chunks),
        "canonical_payload_sha256": final_digest,
        "contains_only_sanitized_log_identity_fields": True,
        "raw_portal_responses_persisted": False,
        "path_outside_git_worktree": True,
        "reported_portal_request_stats_cover_current_attempt_only": True,
        "portal_stats_current_attempt": dict(sorted(portal_stats.items())),
    }


def _decode_logs(
    logs: Sequence[Mapping[str, Any]],
    *,
    branches_by_trove_manager: Mapping[str, str],
    signatures_by_topic: Mapping[str, str],
    trove_operations_by_code: Mapping[int, str],
    batch_operations_by_code: Mapping[int, str],
    from_block: int,
    to_block: int,
) -> list[dict[str, Any]]:
    events = [
        decode_support_log(
            raw,
            branches_by_trove_manager=branches_by_trove_manager,
            signatures_by_topic=signatures_by_topic,
            trove_operations_by_code=trove_operations_by_code,
            batch_operations_by_code=batch_operations_by_code,
            from_block=from_block,
            to_block=to_block,
        )
        for raw in logs
    ]
    identities = [log_identity(event) for event in events]
    if len(set(identities)) != len(identities):
        raise RuntimeError("RPC returned duplicate canonical log identities")
    return events


def _identity_digest(events: Sequence[Mapping[str, Any]]) -> str:
    return canonical_sha256([list(identity) for identity in sorted(map(log_identity, events))])


def _assert_exact_replication(
    formal: Sequence[Mapping[str, Any]],
    replica: Sequence[Mapping[str, Any]],
    *,
    label: str,
) -> str:
    formal_identities = sorted(map(log_identity, formal))
    replica_identities = sorted(map(log_identity, replica))
    if formal_identities != replica_identities:
        formal_set = set(formal_identities)
        replica_set = set(replica_identities)
        raise RuntimeError(
            f"{label} log identity replication failed: "
            f"formal={len(formal_identities)}, replica={len(replica_identities)}, "
            f"formal_only={len(formal_set - replica_set)}, "
            f"replica_only={len(replica_set - formal_set)}"
        )
    return canonical_sha256([list(identity) for identity in formal_identities])


def _code_audit(
    formal: _RpcClient,
    replica: _RpcClient,
    *,
    addresses: Mapping[str, str],
    block_number: int,
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for label, address in sorted(addresses.items()):
        normalized_address = normalize_address(address)
        formal_code = normalize_hex_data(
            str(formal.call("eth_getCode", [normalized_address, hex(block_number)]))
        )
        replica_code = normalize_hex_data(
            str(replica.call("eth_getCode", [normalized_address, hex(block_number)]))
        )
        if formal_code == "0x" or replica_code == "0x":
            raise RuntimeError(f"{label} has no deployed bytecode at the frozen block")
        if formal_code != replica_code:
            raise RuntimeError(f"{label} bytecode differs across RPC transports")
        code_bytes = bytes.fromhex(formal_code[2:])
        results[label] = {
            "address": normalized_address,
            "byte_length": len(code_bytes),
            "sha256": hashlib.sha256(code_bytes).hexdigest(),
            "exact_across_rpcs": True,
        }
    return results


def _attach_relevant_timestamps(
    client: _RpcClient,
    events: Sequence[dict[str, Any]],
    *,
    official_arms_by_branch: Mapping[str, str],
) -> int:
    normalized_arms = {
        branch: normalize_address(address) for branch, address in official_arms_by_branch.items()
    }
    relevant = [
        event
        for event in events
        if event["event_name"] == "Redemption"
        or (
            event["event_name"] == "BatchUpdated"
            and int(event["operation"]) == 2
            and normalize_address(str(event["interest_batch_manager"]))
            == normalized_arms[str(event["branch"])]
        )
    ]
    events_by_block: dict[int, list[dict[str, Any]]] = {}
    for event in relevant:
        events_by_block.setdefault(int(event["block_number"]), []).append(event)
    blocks = sorted(events_by_block)
    for index, block_number in enumerate(blocks, start=1):
        header = client.block(block_number)
        for event in events_by_block[block_number]:
            if str(event["block_hash"]) != str(header["hash"]):
                raise RuntimeError("event block hash differs from canonical header")
            event["block_timestamp"] = int(header["timestamp"])
        if index == 1 or index % 100 == 0 or index == len(blocks):
            print(f"headers: {index}/{len(blocks)} relevant blocks", flush=True)
    return len(blocks)


def _request_stats(client: _RpcClient) -> dict[str, Any]:
    return {
        "rpc_request_counts": dict(sorted(client.method_counts.items())),
        "log_range_splits": client.log_range_splits,
        "log_topic_splits": client.log_topic_splits,
        "rate_limit_retry_count": client.rate_limit_retry_count,
        "rate_limit_wait_seconds": round(client.rate_limit_wait_seconds, 3),
        "server_error_retry_count": client.server_error_retry_count,
        "server_error_wait_seconds": round(client.server_error_wait_seconds, 3),
    }


def audit(
    config_path: Path,
    *,
    bold_root: Path,
    arm_root: Path,
    output_path: Path,
    replica_checkpoint_path: Path | None = None,
) -> dict[str, Any]:
    """Execute D0 without decoding queue position or numerical protocol outcomes."""
    if _git("status", "--porcelain"):
        raise RuntimeError("formal Liquity D0 requires a clean EcoPhys worktree")
    git_sha = _git("rev-parse", "HEAD")
    config_sha256 = _sha256_file(config_path)
    config = _load_yaml(config_path)
    amendment_audit = _validate_freeze_contract(config, config_path=config_path)
    source_audit = _source_audit(config, bold_root=bold_root, arm_root=arm_root)
    if _keccak_topic("Transfer(address,address,uint256)") != (
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    ):
        raise RuntimeError("local Keccak-256 failed the ERC-20 event vector")

    transport = config["transport"]
    formal = _rpc_client(str(transport["formal_rpc"]), transport)
    replication_kind = str(transport.get("replication_transport_kind", "json_rpc"))
    replica_rpc: _RpcClient | None = None
    portal: SqdPortalClient | None = None
    if replication_kind == "sqd_finalized_portal":
        portal = SqdPortalClient(
            str(transport["replication_portal_dataset_url"]),
            timeout_seconds=float(transport["replication_portal_timeout_seconds"]),
            retry_attempts=int(transport["replication_portal_retry_attempts"]),
            retry_backoff_seconds=float(transport["replication_portal_retry_backoff_seconds"]),
        )
    elif replication_kind == "json_rpc":
        replica_rpc = _rpc_client(
            str(transport["replication_rpc"]),
            transport,
            minimum_request_interval_seconds=float(
                transport.get(
                    "replication_minimum_request_interval_seconds",
                    transport["minimum_request_interval_seconds"],
                )
            ),
            rate_limit_retries=int(
                transport.get("replication_rate_limit_retries", transport["rate_limit_retries"])
            ),
        )
    else:
        raise RuntimeError(f"unsupported D0 replication transport: {replication_kind}")
    state_witness_url = str(transport.get("state_witness_rpc", transport["replication_rpc"]))
    state_witness = (
        replica_rpc
        if replica_rpc is not None and state_witness_url == str(transport["replication_rpc"])
        else _rpc_client(state_witness_url, transport)
    )
    chain_id = hex(int(config["ethereum"]["chain_id"]))
    rpc_clients = [formal, state_witness]
    if replica_rpc is not None:
        rpc_clients.append(replica_rpc)
    if any(client.call("eth_chainId", []) != chain_id for client in rpc_clients):
        raise RuntimeError("one or more D0 RPC transports are on the wrong chain")

    ethereum = config["ethereum"]
    from_block = int(ethereum["from_block"])
    to_block = int(ethereum["to_block"])
    formal_end = formal.block(to_block)
    state_witness_end = state_witness.block(to_block)
    expected_hash = normalize_topic(str(ethereum["to_block_hash"]))
    expected_timestamp = int(ethereum["to_block_timestamp"])
    portal_audit: dict[str, Any] | None = None
    if formal_end != state_witness_end:
        raise RuntimeError("frozen end-block headers differ across RPC state witnesses")
    if str(formal_end["hash"]) != expected_hash or int(formal_end["timestamp"]) != expected_timestamp:
        raise RuntimeError("frozen D0 end block differs from the preregistration")
    if portal is not None:
        metadata = portal.metadata()
        expected_metadata = dict(transport["replication_portal_expected_metadata"])
        observed_metadata = {key: metadata.get(key) for key in expected_metadata}
        if observed_metadata != expected_metadata:
            raise RuntimeError("SQD Portal metadata differs from the frozen dataset identity")
        finalized_head = portal.finalized_head()
        if int(finalized_head["number"]) < to_block:
            raise RuntimeError("SQD Portal finalized head does not cover the frozen D0 interval")
        portal_end = portal.finalized_block_header(to_block)
        if str(portal_end["hash"]) != expected_hash or int(portal_end["timestamp"]) != expected_timestamp:
            raise RuntimeError("SQD Portal frozen end block differs from the preregistration")
        portal_audit = {
            "metadata": observed_metadata,
            "finalized_head_at_start": finalized_head,
            "frozen_end_header": portal_end,
            "frozen_end_header_matches_rpc_witnesses": True,
        }
    elif replica_rpc is not None:
        replica_end = replica_rpc.block(to_block)
        if formal_end != replica_end:
            raise RuntimeError("frozen end-block headers differ across RPC transports")

    branch_records = ethereum["branches"]
    branches_by_trove_manager = {
        normalize_address(str(record["trove_manager"])): str(branch)
        for branch, record in branch_records.items()
    }
    official_arms = {
        str(branch): normalize_address(str(record["official_arm"]))
        for branch, record in branch_records.items()
    }
    deployment_addresses: dict[str, str] = {}
    for branch, record in branch_records.items():
        deployment_addresses[f"{branch}.trove_manager"] = str(record["trove_manager"])
        deployment_addresses[f"{branch}.borrower_operations"] = str(record["borrower_operations"])
    deployment_audit = _code_audit(
        formal,
        state_witness,
        addresses=deployment_addresses,
        block_number=to_block,
    )

    signatures_by_topic = {
        normalize_topic(str(record["topic0"])): str(event_name)
        for event_name, record in config["event_signatures"].items()
    }
    topics = sorted(signatures_by_topic)
    addresses = sorted(branches_by_trove_manager)
    trove_operations_by_code = {
        int(code): str(name) for name, code in config["operation_codes"]["trove"].items()
    }
    batch_operations_by_code = {
        int(code): str(name) for name, code in config["operation_codes"]["batch"].items()
    }
    maximum_span = int(transport["maximum_get_logs_span"])
    replica_addresses_together = bool(transport.get("replication_addresses_together", False))

    qualification: list[dict[str, Any]] = []
    nonempty_qualification_shards = 0
    for index, shard in enumerate(transport["qualification_shards_frozen_without_event_counts"]):
        shard_start = int(shard["from_block"])
        shard_end = int(shard["to_block"])
        formal_raw = _query_logs(
            formal,
            addresses=addresses,
            topics=topics,
            from_block=shard_start,
            to_block=shard_end,
            maximum_span=maximum_span,
            label=f"qualification[{index}].formal",
        )
        formal_events = _decode_logs(
            formal_raw,
            branches_by_trove_manager=branches_by_trove_manager,
            signatures_by_topic=signatures_by_topic,
            trove_operations_by_code=trove_operations_by_code,
            batch_operations_by_code=batch_operations_by_code,
            from_block=shard_start,
            to_block=shard_end,
        )
        replica_transport_stats: dict[str, Any] | None = None
        if portal is not None:
            replica_events, replica_transport_stats = portal.finalized_log_identities(
                addresses=addresses,
                topics=topics,
                from_block=shard_start,
                to_block=shard_end,
            )
            print(
                f"qualification[{index}].replica: "
                f"{replica_transport_stats['page_count']} Portal pages, "
                f"{len(replica_events)} logs",
                flush=True,
            )
        else:
            if replica_rpc is None:
                raise RuntimeError("JSON-RPC replication client is absent")
            replica_raw = _query_logs(
                replica_rpc,
                addresses=addresses,
                topics=topics,
                from_block=shard_start,
                to_block=shard_end,
                maximum_span=maximum_span,
                label=f"qualification[{index}].replica",
                addresses_together=replica_addresses_together,
            )
            replica_events = _decode_logs(
                replica_raw,
                branches_by_trove_manager=branches_by_trove_manager,
                signatures_by_topic=signatures_by_topic,
                trove_operations_by_code=trove_operations_by_code,
                batch_operations_by_code=batch_operations_by_code,
                from_block=shard_start,
                to_block=shard_end,
            )
        digest = _assert_exact_replication(
            formal_events, replica_events, label=f"qualification shard {index}"
        )
        nonempty_qualification_shards += bool(formal_events)
        qualification.append(
            {
                "from_block": shard_start,
                "to_block": shard_end,
                "event_count": len(formal_events),
                "canonical_log_identity_sha256": digest,
                "exact_identity_sets_equal": True,
                "replica_transport_stats": replica_transport_stats,
            }
        )
    if nonempty_qualification_shards < int(transport["minimum_nonempty_qualification_shards"]):
        raise RuntimeError("too few frozen qualification shards contained support events")

    formal_raw = _query_logs(
        formal,
        addresses=addresses,
        topics=topics,
        from_block=from_block,
        to_block=to_block,
        maximum_span=maximum_span,
        label="full.formal",
    )
    formal_events = _decode_logs(
        formal_raw,
        branches_by_trove_manager=branches_by_trove_manager,
        signatures_by_topic=signatures_by_topic,
        trove_operations_by_code=trove_operations_by_code,
        batch_operations_by_code=batch_operations_by_code,
        from_block=from_block,
        to_block=to_block,
    )
    checkpoint_audit: dict[str, Any] | None = None
    if int(config["contract"]["version"]) >= 3:
        if replica_checkpoint_path is None:
            raise RuntimeError("D0 v3+ requires an explicit external replica checkpoint path")
        if (
            int(transport["replication_checkpoint_schema_version"]) != 1
            or int(transport["replication_checkpoint_every_chunks"]) != 1
        ):
            raise RuntimeError("D0 v3+ checkpoint settings differ from the implemented protocol")
        checkpoint_identity: dict[str, Any] = {
            "config_path": str(config_path.relative_to(REPO_ROOT)),
            "config_sha256": config_sha256,
            "git_sha": git_sha,
            "from_block": from_block,
            "to_block": to_block,
            "maximum_get_logs_span": maximum_span,
            "addresses": addresses,
            "topics": topics,
        }
        if portal is not None:
            checkpoint_identity.update(
                {
                    "replication_transport_kind": replication_kind,
                    "replication_portal_dataset_url": str(transport["replication_portal_dataset_url"]),
                    "replication_portal_stream_endpoint": str(
                        transport["replication_portal_stream_endpoint"]
                    ),
                    "replication_portal_expected_metadata": dict(
                        transport["replication_portal_expected_metadata"]
                    ),
                    "replication_portal_timeout_seconds": float(
                        transport["replication_portal_timeout_seconds"]
                    ),
                    "replication_portal_retry_attempts": int(transport["replication_portal_retry_attempts"]),
                    "replication_portal_retry_backoff_seconds": float(
                        transport["replication_portal_retry_backoff_seconds"]
                    ),
                }
            )
            replica_events, checkpoint_audit = _query_portal_with_checkpoint(
                portal,
                checkpoint_path=replica_checkpoint_path,
                checkpoint_identity=checkpoint_identity,
                addresses=addresses,
                topics=topics,
                from_block=from_block,
                to_block=to_block,
                maximum_span=maximum_span,
            )
        else:
            if replica_rpc is None:
                raise RuntimeError("JSON-RPC replication client is absent")
            checkpoint_identity.update(
                {
                    "replication_rpc": str(transport["replication_rpc"]),
                    "addresses_together": replica_addresses_together,
                    "minimum_request_interval_seconds": float(
                        transport.get(
                            "replication_minimum_request_interval_seconds",
                            transport["minimum_request_interval_seconds"],
                        )
                    ),
                    "rate_limit_retries": int(
                        transport.get("replication_rate_limit_retries", transport["rate_limit_retries"])
                    ),
                    "split_on_exhausted_rate_limit": bool(
                        transport.get("replication_split_on_exhausted_rate_limit", False)
                    ),
                    "maximum_rate_limit_split_depth": int(
                        transport.get("replication_maximum_rate_limit_split_depth", 0)
                    ),
                }
            )
            replica_events, checkpoint_audit = _query_replica_with_checkpoint(
                replica_rpc,
                checkpoint_path=replica_checkpoint_path,
                checkpoint_identity=checkpoint_identity,
                addresses=addresses,
                topics=topics,
                branches_by_trove_manager=branches_by_trove_manager,
                signatures_by_topic=signatures_by_topic,
                trove_operations_by_code=trove_operations_by_code,
                batch_operations_by_code=batch_operations_by_code,
                from_block=from_block,
                to_block=to_block,
                maximum_span=maximum_span,
                split_on_exhausted_rate_limit=bool(
                    transport.get("replication_split_on_exhausted_rate_limit", False)
                ),
                maximum_rate_limit_split_depth=int(
                    transport.get("replication_maximum_rate_limit_split_depth", 0)
                ),
            )
    else:
        if replica_rpc is None:
            raise RuntimeError("JSON-RPC replication client is absent")
        replica_raw = _query_logs(
            replica_rpc,
            addresses=addresses,
            topics=topics,
            from_block=from_block,
            to_block=to_block,
            maximum_span=maximum_span,
            label="full.replica",
        )
        replica_events = _decode_logs(
            replica_raw,
            branches_by_trove_manager=branches_by_trove_manager,
            signatures_by_topic=signatures_by_topic,
            trove_operations_by_code=trove_operations_by_code,
            batch_operations_by_code=batch_operations_by_code,
            from_block=from_block,
            to_block=to_block,
        )
    identity_digest = _assert_exact_replication(formal_events, replica_events, label="full frozen interval")
    relevant_header_count = _attach_relevant_timestamps(
        formal, formal_events, official_arms_by_branch=official_arms
    )
    support = summarize_agentic_queue_support(
        formal_events,
        official_arms_by_branch=official_arms,
        thresholds=config["pass_thresholds"],
        redemption_proximity_seconds=int(config["support_window"]["redemption_proximity_seconds"]),
        raw_event_count=len(formal_raw),
    )
    decision = (
        "pass_to_separately_frozen_d1_queue_reconstruction"
        if support["passed"]
        else "stop_liquity_nmi_route_before_numerical_outcomes"
    )
    event_counts = Counter(str(event["event_name"]) for event in formal_events)
    branch_counts = Counter(str(event["branch"]) for event in formal_events)
    sanitized_events = sorted(
        formal_events,
        key=lambda event: (
            int(event["block_number"]),
            int(event["transaction_index"]),
            int(event["log_index"]),
        ),
    )
    if portal is not None:
        replica_request_stats: dict[str, Any] = {
            "transport_kind": replication_kind,
            "request_count": portal.request_count,
            "retry_count": portal.retry_count,
            "ndjson_bytes_received": portal.bytes_received,
            "portal_audit": portal_audit,
        }
    else:
        if replica_rpc is None:
            raise RuntimeError("JSON-RPC replication client is absent")
        replica_request_stats = _request_stats(replica_rpc)
    result: dict[str, Any] = {
        "schema_version": 1,
        "contract_name": str(config["contract"]["name"]),
        "contract_version": int(config["contract"]["version"]),
        "decision": decision,
        "amendment_audit": amendment_audit,
        "repository": {
            "git_sha": git_sha,
            "clean_worktree_at_start": True,
            "config_path": str(config_path.relative_to(REPO_ROOT)),
            "config_sha256": config_sha256,
        },
        "source_audit": source_audit,
        "ethereum": {
            "chain_id": int(ethereum["chain_id"]),
            "from_block": from_block,
            "to_block": to_block,
            "to_block_hash": expected_hash,
            "to_block_timestamp": expected_timestamp,
            "to_block_utc": _utc(expected_timestamp),
            "branches": {
                branch: {key: normalize_address(str(value)) for key, value in record.items()}
                for branch, record in sorted(branch_records.items())
            },
        },
        "deployment_audit": deployment_audit,
        "event_surface": {
            "event_count": len(formal_events),
            "event_counts": dict(sorted(event_counts.items())),
            "branch_counts": dict(sorted(branch_counts.items())),
            "canonical_log_identity_sha256": identity_digest,
            "sanitized_decoded_event_sha256": canonical_sha256(sanitized_events),
            "relevant_event_block_header_count": relevant_header_count,
            "raw_rpc_responses_persisted": False,
            "numerical_protocol_outcomes_decoded_or_persisted": False,
        },
        "support_gate": support,
        "transport": {
            "formal_rpc": str(transport["formal_rpc"]),
            "replication_transport_kind": replication_kind,
            "replication_rpc": transport["replication_rpc"],
            "replication_portal_dataset_url": transport.get("replication_portal_dataset_url"),
            "state_witness_rpc": state_witness_url,
            "qualification_shards": qualification,
            "nonempty_qualification_shards": nonempty_qualification_shards,
            "full_log_identity_sets_equal": True,
            "formal": _request_stats(formal),
            "replica": replica_request_stats,
            "state_witness": _request_stats(state_witness),
            "replica_checkpoint": checkpoint_audit,
        },
        "blinding": {
            "only_event_type_operation_identity_and_canonical_time_decoded": True,
            "rates_debt_collateral_redemption_values_prices_and_queue_rank_decoded": False,
            "adjustment_direction_or_size_decoded": False,
            "market_prices_or_liquidation_outcomes_queried": False,
            "causal_or_predictive_effects_computed": False,
            "raw_rpc_responses_retained": False,
        },
        "compute": {
            "cpu_only": True,
            "gpu_used": False,
            "paid_data_used": False,
            "ecomd_used": False,
        },
    }
    result["canonical_payload_sha256"] = canonical_sha256(result)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(output_path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--bold-root", type=Path, required=True)
    parser.add_argument("--arm-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replica-checkpoint", type=Path)
    args = parser.parse_args()
    result = audit(
        args.config.resolve(),
        bold_root=args.bold_root.resolve(),
        arm_root=args.arm_root.resolve(),
        output_path=args.output.resolve(),
        replica_checkpoint_path=(
            args.replica_checkpoint.resolve() if args.replica_checkpoint is not None else None
        ),
    )
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "metrics": result["support_gate"]["metrics"],
                "manifest": str(args.output.resolve()),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
