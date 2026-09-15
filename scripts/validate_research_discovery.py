#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import cast

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
OCI_IMAGE_DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
CARD_STATUSES = {"screening", "candidate", "parked", "active", "failed_closed"}
DECIDED_STATUSES = CARD_STATUSES - {"screening"}
STAGES = {"D_minus_3", "D_minus_2", "D_minus_1", "D0", "D1", "D2"}
SANDBOX_EFFECTIVE_STATES = {"authorized", "expired", "exhausted", "closed", "quarantined"}
SANDBOX_ACTIONS = {
    "free_dataset_acquisition",
    "disposable_outcome_inspection",
    "cpu_simulator_probe",
    "sandbox_analysis_implementation",
}
SANDBOX_HARD_MAX_CPU_SECONDS = 28_800
SANDBOX_HARD_MAX_STORAGE_BYTES = 5_000_000_000
SANDBOX_HARD_MAX_MONETARY_COST_USD_MICROS = 0
SANDBOX_HARD_MAX_GPU_SECONDS = 0
SANDBOX_HARD_MAX_BRANCHES = 16
SANDBOX_HARD_MAX_TTL_SECONDS = 604_800
SANDBOX_STDERR_LIMIT_BYTES = 1_000_000
SANDBOX_AMBIGUOUS_INTERRUPTION_POLICY = (
    "Remove and prove absence of the named container, assume outcome exposure, charge the "
    "full branch CPU and output reservation, and terminalize the sandbox as quarantined; "
    "retry is forbidden."
)
SANDBOX_REQUIRED_FORBIDDEN_ACTIONS = {
    "confirmation_holdout_access",
    "dataset_purchase",
    "gpu_use",
    "production_model_implementation",
    "ecomd_integration",
    "external_outreach",
    "paper_claim_support",
    "topic_status_promotion",
}
SEARCH_CYCLE_LIMITS = {
    "raw_question_programs": 12,
    "quick_screens": 6,
    "collision_screens": 3,
    "full_hostile_audits": 2,
    "machine_cards": 1,
}
SEARCH_SCREEN_REQUIREMENTS = {
    "quick_anchor_primary_works_maximum": 3,
    "quick_killer_toys_minimum": 1,
    "collision_primary_works_minimum": 6,
    "full_primary_works_minimum": 15,
    "full_killer_toys_minimum": 2,
}
SEARCH_SOURCE_LANES = {
    "unresolved_model_disagreement",
    "new_truth_or_control_capability",
    "market_native_action_or_constraint",
    "cross_domain_theorem_with_market_specific_obstruction",
}
SEARCH_QUICK_REQUIREMENTS = {
    "market_native_object",
    "at_least_two_rival_explanations",
    "same_estimand_for_claimed_model_disagreement",
    "one_discriminating_result",
    "scientific_value_for_positive_and_null_answers",
    "cross_domain_native_parameter_and_representation_invariance",
    "dimensionless_parameter_completion_twin_when_claimed",
    "capacity_state_and_allocation_policy_completion_when_claimed",
    "paired_pulse_second_order_kernel_and_native_phase_test_when_claimed",
}
SEARCH_TOPIC_ARCHETYPES = {
    "theory_mechanism",
    "measurement_method",
    "empirical_intervention",
    "simulator_method",
}
SEARCH_PORTFOLIO_BALANCE_TARGETS = {
    "measurement_method_minimum": 2,
    "empirical_intervention_minimum": 2,
    "theory_mechanism_maximum": 6,
}
CAPABILITY_BUILD_REQUIRED_CONTRACT_PARTS = {
    "named_blocker",
    "supported_estimand_family",
    "assignment_and_interference",
    "event_lifecycle_and_replay_prestate",
    "rights_ethics_and_release",
    "untouched_confirmation_partition",
    "independent_replication",
    "cost_and_stop_rules",
}
SEARCH_FINAL_DISPOSITIONS = {
    "portfolio_pruned",
    "quick_closed",
    "collision_closed",
    "full_closed",
    "deduplicated",
    "advanced",
    "deferred",
}
REENTRY_TRIGGER_SOURCE_KINDS = {
    "primary_model_disagreement",
    "truth_or_control_asset",
    "theorem_or_counterexample",
}
REENTRY_TRIGGER_DECISIONS = {
    "qualified_trigger",
    "partial_capability",
    "not_trigger",
}
REENTRY_TRIGGER_CLAIM_VERDICTS = {"satisfied", "partial", "failed"}
KG_STATUS_MAP = {
    "candidate": "candidate",
    "parked": "parked",
    "active": "active",
    "failed_closed": "failed_closed",
}
KILLER_STATUSES = {"pending", "survived", "killed"}
KILLER_TYPES = {
    "necessity",
    "sufficiency",
    "identifiability",
    "invariance",
    "negative_control",
}
FAILURE_DISPOSITIONS = {"blocked", "distinguished"}
SIMULATOR_STATUSES = {"unverified", "qualified", "rejected"}
REAL_BRIDGE_STATUSES = {"unqualified", "qualified", "rejected"}
NOVELTY_CLASSIFICATIONS = {"direct", "adjacent", "background"}
OUTCOME_BLIND_ACTIONS = {
    "literature_search",
    "source_code_audit",
    "schema_audit",
    "metadata_audit",
    "theorem_work",
    "simulator_contract_audit",
    "real_data_contract_audit",
}
CARD_FIELDS = {
    "schema_version",
    "id",
    "title",
    "created_at",
    "closed_at",
    "status",
    "stage",
    "parent_route_ids",
    "scope",
    "object",
    "claim",
    "contracts",
    "novelty_manifest",
    "killer_tests",
    "failure_reuse",
    "probabilities",
    "contamination_control",
    "evidence_uses",
    "authorization",
    "decision_ref",
}
DECISION_FIELDS = {
    "schema_version",
    "card_id",
    "decided_at",
    "status",
    "stage",
    "outcome_accessed",
    "card_sha256",
    "kg_node_id",
    "rationale",
    "authorized_actions",
    "forbidden_actions",
    "evidence_refs",
    "reopen_conditions",
}
SANDBOX_FIELDS = {
    "schema_version",
    "id",
    "campaign_id",
    "created_at",
    "expires_at",
    "purpose",
    "parent_route_ids",
    "asset",
    "partition",
    "reservation",
    "authorization",
    "confirmation_contract",
    "execution_contract",
    "integrity",
    "decision_ref",
}
SANDBOX_EXECUTION_FIELDS = {
    "executor",
    "launcher",
    "incident_handler",
    "image_digest",
    "network",
    "root_filesystem",
    "repository_tree_mount",
    "input_channel",
    "confirmation_materialization",
    "output_channel",
    "secrets",
    "device_access",
}
SANDBOX_BRANCH_REQUEST_FIELDS = {
    "schema_version",
    "sandbox_id",
    "branch_id",
    "hypothesis_id",
    "hypothesis",
    "falsifier",
    "multiplicity_family_id",
    "test_ids",
    "unit_ids",
    "cpu_seconds",
    "output_bytes",
    "code_manifest",
    "config",
}
SANDBOX_CONFIRMATION_FIELDS = {
    "mode",
    "derivation",
    "outcomes_materialized",
    "release_condition",
    "controller",
}
SANDBOX_DECISION_FIELDS = {
    "schema_version",
    "sandbox_id",
    "decision",
    "decided_at",
    "authorized_by",
    "manifest_sha256",
    "genesis_entry_sha256",
    "rationale",
}


class DiscoveryValidationError(ValueError):
    """Raised when the forward research-discovery contract is inconsistent."""


@dataclass(frozen=True)
class EvidenceMeta:
    epistemic_class: str
    sandbox_id: str | None = None
    artifact_ref: str | None = None
    artifact_sha256: str | None = None

    @property
    def tainted(self) -> bool:
        return self.epistemic_class == "sandbox_exploratory_tainted"


@dataclass(frozen=True)
class SandboxRecord:
    sandbox_id: str
    campaign_id: str
    parent_route_ids: frozenset[str]
    asset_fingerprint: str
    unit_namespace: str
    exploration_units: frozenset[str]
    confirmation_units: frozenset[str]
    reservation: Mapping[str, int]
    effective_state: str
    manifest_sha256: str
    partition_sha256: str
    artifact_root: Path
    result_ref: str | None
    result_sha256: str | None


@dataclass(frozen=True)
class SandboxExecutionContract:
    executor: str
    launcher_sha256: str
    incident_handler_sha256: str
    image_digest: str
    network: str
    root_filesystem: str
    repository_tree_mount: str
    input_channel: str
    confirmation_materialization: str
    output_channel: str
    secrets: str
    device_access: str


def require_mapping(value: object, context: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
        raise DiscoveryValidationError(f"{context} must be a string-keyed mapping")
    return cast(Mapping[str, object], value)


def require_list(value: object, context: str) -> list[object]:
    if not isinstance(value, list):
        raise DiscoveryValidationError(f"{context} must be a list")
    return cast(list[object], value)


def require_string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DiscoveryValidationError(f"{context} must be a non-empty string")
    return value


def require_id(value: object, context: str) -> str:
    identifier = require_string(value, context)
    if ID_PATTERN.fullmatch(identifier) is None:
        raise DiscoveryValidationError(f"{context} is not a valid identifier: {identifier!r}")
    return identifier


def require_date(value: object, context: str) -> date:
    raw = require_string(value, context)
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise DiscoveryValidationError(f"{context} is not an ISO date: {raw!r}") from exc


def require_utc_timestamp(value: object, context: str) -> datetime:
    raw = require_string(value, context)
    if not raw.endswith("Z"):
        raise DiscoveryValidationError(f"{context} must be an RFC3339 UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(raw[:-1] + "+00:00")
    except ValueError as exc:
        raise DiscoveryValidationError(f"{context} is not an RFC3339 timestamp: {raw!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise DiscoveryValidationError(f"{context} must use UTC")
    return parsed


def require_bool(value: object, context: str) -> bool:
    if type(value) is not bool:
        raise DiscoveryValidationError(f"{context} must be boolean")
    return value


def require_probability(value: object, context: str) -> float:
    if type(value) not in {int, float}:
        raise DiscoveryValidationError(f"{context} must be numeric")
    result = float(cast(int | float, value))
    if not 0.0 <= result <= 1.0:
        raise DiscoveryValidationError(f"{context} must lie in [0, 1]")
    return result


def require_nonnegative_integer(value: object, context: str) -> int:
    if type(value) is not int or value < 0:
        raise DiscoveryValidationError(f"{context} must be a nonnegative integer")
    return value


def require_positive_integer(value: object, context: str) -> int:
    result = require_nonnegative_integer(value, context)
    if result == 0:
        raise DiscoveryValidationError(f"{context} must be positive")
    return result


def require_schema_version_one(value: object, context: str) -> None:
    if type(value) is not int or value != 1:
        raise DiscoveryValidationError(f"{context} must be integer 1")


def require_string_list(
    value: object,
    context: str,
    *,
    allow_empty: bool = True,
) -> list[str]:
    raw = require_list(value, context)
    if not allow_empty and not raw:
        raise DiscoveryValidationError(f"{context} must not be empty")
    result = [require_string(item, f"{context}[{index}]") for index, item in enumerate(raw)]
    if len(result) != len(set(result)):
        raise DiscoveryValidationError(f"{context} contains duplicates")
    return result


def require_exact_fields(
    value: Mapping[str, object],
    expected: set[str],
    context: str,
) -> None:
    missing = expected - set(value)
    extra = set(value) - expected
    if missing or extra:
        raise DiscoveryValidationError(
            f"{context} fields differ: missing={sorted(missing)}, extra={sorted(extra)}"
        )


def load_yaml(path: Path, context: str) -> Mapping[str, object]:
    try:
        loaded = cast(object, yaml.safe_load(path.read_text(encoding="utf-8")))
    except (OSError, yaml.YAMLError) as exc:
        raise DiscoveryValidationError(f"cannot load {context} at {path}: {exc}") from exc
    return require_mapping(loaded, context)


def load_canonical_json_mapping(path: Path, context: str) -> Mapping[str, object]:
    try:
        raw = path.read_bytes()
        loaded = cast(object, json.loads(raw.decode("utf-8")))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise DiscoveryValidationError(f"cannot load {context} at {path}: {exc}") from exc
    mapping = require_mapping(loaded, context)
    if canonical_json_bytes(mapping) != raw:
        raise DiscoveryValidationError(f"{context} must be canonical compact JSON")
    return mapping


def load_json_schema(path: Path, context: str) -> Mapping[str, object]:
    try:
        loaded = cast(object, json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        raise DiscoveryValidationError(f"cannot load {context}: {exc}") from exc
    schema = require_mapping(loaded, context)
    try:
        Draft202012Validator.check_schema(dict(schema))
    except SchemaError as exc:
        raise DiscoveryValidationError(f"invalid {context}: {exc.message}") from exc
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise DiscoveryValidationError(f"{context} must declare JSON Schema 2020-12")
    return schema


def validate_json_instance(
    schema: Mapping[str, object],
    instance: Mapping[str, object],
    context: str,
) -> None:
    validator = Draft202012Validator(dict(schema), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(dict(instance)), key=lambda error: list(error.path))
    if not errors:
        return
    first = errors[0]
    location = ".".join(str(part) for part in first.path)
    suffix = f" at {location}" if location else ""
    raise DiscoveryValidationError(f"{context} violates JSON schema{suffix}: {first.message}")


def safe_repo_path(repo_root: Path, raw_path: str, context: str) -> Path:
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise DiscoveryValidationError(f"{context} must be a safe repository-relative path")
    resolved_root = repo_root.resolve()
    resolved = (resolved_root / relative).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise DiscoveryValidationError(f"{context} resolves outside the repository") from exc
    if not resolved.is_file():
        raise DiscoveryValidationError(f"{context} is not a file: {raw_path}")
    return resolved


def safe_repo_relative_path(repo_root: Path, raw_path: str, context: str) -> Path:
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise DiscoveryValidationError(f"{context} must be a safe repository-relative path")
    resolved_root = repo_root.resolve()
    resolved = (resolved_root / relative).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise DiscoveryValidationError(f"{context} resolves outside the repository") from exc
    return resolved


def require_sha256(value: object, context: str) -> str:
    digest = require_string(value, context)
    if SHA256_PATTERN.fullmatch(digest) is None:
        raise DiscoveryValidationError(f"{context} is not a SHA-256 digest")
    return digest


def require_oci_image_digest(value: object, context: str) -> str:
    digest = require_string(value, context)
    if OCI_IMAGE_DIGEST_PATTERN.fullmatch(digest) is None:
        raise DiscoveryValidationError(f"{context} is not a pinned OCI SHA-256 digest")
    return digest


TERMINAL_PIN_HISTORY_LIMIT = 64


def require_digest_ref(
    repo_root: Path,
    value: object,
    context: str,
    *,
    allow_committed_match: bool = False,
) -> tuple[str, Path, str]:
    mapping = require_mapping(value, context)
    require_exact_fields(mapping, {"ref", "sha256"}, context)
    raw_ref = require_string(mapping.get("ref"), f"{context}.ref")
    path = safe_repo_path(repo_root, raw_ref, f"{context}.ref")
    digest = require_sha256(mapping.get("sha256"), f"{context}.sha256")
    working_tree_matches = hashlib.sha256(path.read_bytes()).hexdigest() == digest
    if not working_tree_matches and not (
        allow_committed_match and committed_version_matches(repo_root, raw_ref, digest)
    ):
        detail = (
            " matches neither the working tree nor a committed version"
            if allow_committed_match
            else " mismatch"
        )
        raise DiscoveryValidationError(f"{context}.sha256{detail}")
    return raw_ref, path, digest


def committed_version_matches(repo_root: Path, ref: str, digest: str) -> bool:
    try:
        listing = run_git_bytes(
            repo_root,
            ["log", "--format=%H", "--", ref],
            f"committed versions of {ref}",
        )
    except DiscoveryValidationError:
        return False
    for raw_commit in listing.split()[:TERMINAL_PIN_HISTORY_LIMIT]:
        commit = raw_commit.decode("utf-8", errors="replace")
        try:
            blob = run_git_bytes(
                repo_root,
                ["show", f"{commit}:{ref}"],
                f"committed blob {commit}:{ref}",
            )
        except DiscoveryValidationError:
            continue
        if hashlib.sha256(blob).hexdigest() == digest:
            return True
    return False


def sandbox_ledger_is_terminal(artifact_root: Path) -> bool:
    try:
        raw = (artifact_root / "events.jsonl").read_bytes()
    except OSError:
        return False
    for line in raw.splitlines():
        try:
            entry = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return False
        if isinstance(entry, dict) and entry.get("event_type") == "state_transition":
            return True
    return False


def canonical_json_bytes(value: Mapping[str, object]) -> bytes:
    try:
        encoded = json.dumps(
            dict(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise DiscoveryValidationError(f"value is not canonical JSON: {exc}") from exc
    return encoded.encode("utf-8")


def sha256_mapping_without(value: Mapping[str, object], omitted: str) -> str:
    payload = {key: item for key, item in value.items() if key != omitted}
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def load_route_registry(
    repo_root: Path,
) -> tuple[dict[str, str], set[str], dict[str, set[str]]]:
    path = repo_root / ".claude" / "memory" / "research_route_knowledge_graph.yaml"
    root = load_yaml(path, "route graph")
    statuses: dict[str, str] = {}
    locator_ids: set[str] = set()
    failure_codes: dict[str, set[str]] = {}
    for index, raw_node in enumerate(require_list(root.get("nodes"), "route graph.nodes")):
        node = require_mapping(raw_node, f"route graph.nodes[{index}]")
        node_id = require_id(node.get("id"), f"route graph.nodes[{index}].id")
        status = require_string(node.get("status"), f"route graph.nodes[{index}].status")
        statuses[node_id] = status
        failure_codes[node_id] = set(
            require_string_list(
                node.get("failure_codes"),
                f"route graph.nodes[{index}].failure_codes",
            )
        )
        for field in ("evidence", "artifacts"):
            for locator_index, raw_locator in enumerate(
                require_list(node.get(field), f"route graph.nodes[{index}].{field}")
            ):
                locator = require_mapping(
                    raw_locator,
                    f"route graph.nodes[{index}].{field}[{locator_index}]",
                )
                if locator.get("availability") == "present":
                    locator_path = locator.get("path")
                    if isinstance(locator_path, str) and locator_path.startswith(
                        "research/discovery/sandbox_artifacts/"
                    ):
                        raise DiscoveryValidationError(
                            "route graph cannot register a sandbox artifact as clean evidence"
                        )
                locator_ids.add(
                    require_id(
                        locator.get("id"),
                        f"route graph.nodes[{index}].{field}[{locator_index}].id",
                    )
                )
    return statuses, locator_ids, failure_codes


def validate_topic_search_policy(
    repo_root: Path,
    protocol: Mapping[str, object],
) -> tuple[Mapping[str, object], str, str]:
    policy = require_mapping(
        protocol.get("topic_search_funnel"),
        "protocol.topic_search_funnel",
    )
    fields = {
        "policy_id",
        "purpose",
        "cycle_limits",
        "screen_requirements",
        "source_lanes",
        "quick_screen_required",
        "topic_archetypes",
        "portfolio_balance_targets",
        "capability_build_policy",
        "escalation_rule",
        "ranking_rule",
        "full_audit_forecast_rule",
        "scientific_value_rule",
        "nature_activation_contract",
        "search_cycle_ledger",
        "reentry_trigger_ledger",
    }
    require_exact_fields(policy, fields, "protocol.topic_search_funnel")
    if require_id(policy.get("policy_id"), "protocol.topic_search_funnel.policy_id") != (
        "ecomd_topic_search_funnel_v1"
    ):
        raise DiscoveryValidationError("protocol topic-search policy id differs from validator")
    for field in ("purpose", "scientific_value_rule", "nature_activation_contract"):
        require_string(policy.get(field), f"protocol.topic_search_funnel.{field}")

    limits = require_mapping(
        policy.get("cycle_limits"),
        "protocol.topic_search_funnel.cycle_limits",
    )
    require_exact_fields(limits, set(SEARCH_CYCLE_LIMITS), "protocol.topic_search_funnel.cycle_limits")
    for field, expected in SEARCH_CYCLE_LIMITS.items():
        actual = require_positive_integer(
            limits.get(field),
            f"protocol.topic_search_funnel.cycle_limits.{field}",
        )
        if actual != expected:
            raise DiscoveryValidationError(
                f"protocol topic-search {field} must equal {expected}"
            )

    requirements = require_mapping(
        policy.get("screen_requirements"),
        "protocol.topic_search_funnel.screen_requirements",
    )
    require_exact_fields(
        requirements,
        set(SEARCH_SCREEN_REQUIREMENTS),
        "protocol.topic_search_funnel.screen_requirements",
    )
    for field, expected in SEARCH_SCREEN_REQUIREMENTS.items():
        actual = require_positive_integer(
            requirements.get(field),
            f"protocol.topic_search_funnel.screen_requirements.{field}",
        )
        if actual != expected:
            raise DiscoveryValidationError(
                f"protocol topic-search requirement {field} must equal {expected}"
            )

    source_lanes = set(
        require_string_list(
            policy.get("source_lanes"),
            "protocol.topic_search_funnel.source_lanes",
            allow_empty=False,
        )
    )
    if source_lanes != SEARCH_SOURCE_LANES:
        raise DiscoveryValidationError("protocol topic-search source lanes differ from validator")
    quick_required = set(
        require_string_list(
            policy.get("quick_screen_required"),
            "protocol.topic_search_funnel.quick_screen_required",
            allow_empty=False,
        )
    )
    if quick_required != SEARCH_QUICK_REQUIREMENTS:
        raise DiscoveryValidationError("protocol quick-screen requirements differ from validator")

    archetypes = require_mapping(
        policy.get("topic_archetypes"),
        "protocol.topic_search_funnel.topic_archetypes",
    )
    if set(archetypes) != SEARCH_TOPIC_ARCHETYPES:
        raise DiscoveryValidationError("protocol topic archetypes differ from validator")
    for archetype, raw_contract in archetypes.items():
        contract = require_mapping(
            raw_contract,
            f"protocol.topic_search_funnel.topic_archetypes.{archetype}",
        )
        require_exact_fields(
            contract,
            {"early_truth_contract", "escalation_evidence"},
            f"protocol.topic_search_funnel.topic_archetypes.{archetype}",
        )
        for field in ("early_truth_contract", "escalation_evidence"):
            require_string(
                contract.get(field),
                f"protocol.topic_search_funnel.topic_archetypes.{archetype}.{field}",
            )

    balance = require_mapping(
        policy.get("portfolio_balance_targets"),
        "protocol.topic_search_funnel.portfolio_balance_targets",
    )
    balance_fields = set(SEARCH_PORTFOLIO_BALANCE_TARGETS) | {
        "applies_only_to_future_unsaturated_cycles",
        "advancement_quota",
    }
    require_exact_fields(
        balance,
        balance_fields,
        "protocol.topic_search_funnel.portfolio_balance_targets",
    )
    for field, expected in SEARCH_PORTFOLIO_BALANCE_TARGETS.items():
        actual = require_positive_integer(
            balance.get(field),
            f"protocol.topic_search_funnel.portfolio_balance_targets.{field}",
        )
        if actual != expected:
            raise DiscoveryValidationError(
                f"protocol topic-search portfolio target {field} must equal {expected}"
            )
    if (
        require_bool(
            balance.get("applies_only_to_future_unsaturated_cycles"),
            "protocol.topic_search_funnel.portfolio_balance_targets."
            "applies_only_to_future_unsaturated_cycles",
        )
        is not True
    ):
        raise DiscoveryValidationError(
            "protocol portfolio-balance targets must apply only to future unsaturated cycles"
        )
    if (
        require_bool(
            balance.get("advancement_quota"),
            "protocol.topic_search_funnel.portfolio_balance_targets.advancement_quota",
        )
        is not False
    ):
        raise DiscoveryValidationError(
            "protocol portfolio-balance sampling targets cannot become advancement quotas"
        )

    capability = require_mapping(
        policy.get("capability_build_policy"),
        "protocol.topic_search_funnel.capability_build_policy",
    )
    capability_fields = {
        "pivot_rule",
        "status_semantics",
        "plan_can_authorize_candidate_harvest",
        "execution_requires_separate_authorization",
        "reentry_requires_qualified_trigger",
        "required_contract_parts",
    }
    require_exact_fields(
        capability,
        capability_fields,
        "protocol.topic_search_funnel.capability_build_policy",
    )
    if capability.get("pivot_rule") != "saturated_family_without_qualified_trigger":
        raise DiscoveryValidationError("protocol capability-build pivot rule differs from validator")
    if capability.get("status_semantics") != "infrastructure_preflight_not_topic_status":
        raise DiscoveryValidationError(
            "protocol capability-build status semantics differ from validator"
        )
    capability_flags = {
        "plan_can_authorize_candidate_harvest": False,
        "execution_requires_separate_authorization": True,
        "reentry_requires_qualified_trigger": True,
    }
    for field, expected in capability_flags.items():
        actual = require_bool(
            capability.get(field),
            f"protocol.topic_search_funnel.capability_build_policy.{field}",
        )
        if actual is not expected:
            raise DiscoveryValidationError(
                f"protocol capability-build flag {field} must be {expected}"
            )
    contract_parts = set(
        require_string_list(
            capability.get("required_contract_parts"),
            "protocol.topic_search_funnel.capability_build_policy.required_contract_parts",
            allow_empty=False,
        )
    )
    if contract_parts != CAPABILITY_BUILD_REQUIRED_CONTRACT_PARTS:
        raise DiscoveryValidationError(
            "protocol capability-build contract parts differ from validator"
        )
    if policy.get("escalation_rule") != "cheapest_discriminating_evidence_first":
        raise DiscoveryValidationError("protocol topic-search escalation rule differs from validator")
    if policy.get("ranking_rule") != "pareto_then_weakest_link_no_compensatory_average":
        raise DiscoveryValidationError("protocol topic-search ranking rule differs from validator")
    if (
        policy.get("full_audit_forecast_rule")
        != "freeze_subject_and_full_t0_forecast_before_opening_full_manifest"
    ):
        raise DiscoveryValidationError("protocol full-audit forecast rule differs from validator")
    ledger_ref = require_string(
        policy.get("search_cycle_ledger"),
        "protocol.topic_search_funnel.search_cycle_ledger",
    )
    if ledger_ref != "research/discovery/search_cycle_ledger.yaml":
        raise DiscoveryValidationError("protocol search-cycle ledger path differs from validator")
    safe_repo_path(repo_root, ledger_ref, "protocol.topic_search_funnel.search_cycle_ledger")
    trigger_ledger_ref = require_string(
        policy.get("reentry_trigger_ledger"),
        "protocol.topic_search_funnel.reentry_trigger_ledger",
    )
    if trigger_ledger_ref != "research/discovery/reentry_trigger_ledger.yaml":
        raise DiscoveryValidationError("protocol re-entry trigger ledger path differs from validator")
    safe_repo_path(
        repo_root,
        trigger_ledger_ref,
        "protocol.topic_search_funnel.reentry_trigger_ledger",
    )
    return policy, ledger_ref, trigger_ledger_ref


def load_protocol(
    repo_root: Path,
) -> tuple[
    Mapping[str, object],
    float,
    int,
    set[str],
    Mapping[str, object],
    str,
    Mapping[str, object],
    str,
    str,
]:
    path = repo_root / "research" / "discovery" / "protocol.yaml"
    protocol = load_yaml(path, "protocol")
    require_schema_version_one(protocol.get("schema_version"), "protocol.schema_version")
    require_date(protocol.get("effective_at"), "protocol.effective_at")
    gate = require_mapping(protocol.get("activation_gate"), "protocol.activation_gate")
    floor = require_probability(
        gate.get("hostile_t0_lower_bound_minimum"),
        "protocol.activation_gate.hostile_t0_lower_bound_minimum",
    )
    minimum_primary = gate.get("minimum_primary_works")
    if type(minimum_primary) is not int or minimum_primary < 1:
        raise DiscoveryValidationError("protocol minimum_primary_works must be positive integer")
    decision_policy = require_mapping(
        protocol.get("decision_policy"),
        "protocol.decision_policy",
    )
    decision_policy_fields = {
        "hostile_t0_target",
        "floor_scope",
        "epistemic_status",
        "probability_alone_can_terminalize",
        "terminalization_requires_independent_hard_gate",
        "bounded_information_action_rule",
        "robust_net_value_expression",
        "minimum_resolved_forecasts_before_floor_review",
        "forecast_ledger",
        "historical_post_audit_probabilities_scored",
    }
    require_exact_fields(
        decision_policy,
        decision_policy_fields,
        "protocol.decision_policy",
    )
    require_string(
        decision_policy.get("hostile_t0_target"),
        "protocol.decision_policy.hostile_t0_target",
    )
    floor_scope = require_mapping(
        decision_policy.get("floor_scope"),
        "protocol.decision_policy.floor_scope",
    )
    require_exact_fields(
        floor_scope,
        {
            "statuses",
            "preactive_stages_with_no_floor",
            "bounded_information_stages",
        },
        "protocol.decision_policy.floor_scope",
    )
    if require_string_list(
        floor_scope.get("statuses"),
        "protocol.decision_policy.floor_scope.statuses",
        allow_empty=False,
    ) != ["active"]:
        raise DiscoveryValidationError("protocol probability floor must apply only to active status")
    if set(
        require_string_list(
            floor_scope.get("preactive_stages_with_no_floor"),
            "protocol.decision_policy.floor_scope.preactive_stages_with_no_floor",
            allow_empty=False,
        )
    ) != {"D_minus_3", "D_minus_2"}:
        raise DiscoveryValidationError("protocol preactive no-floor stages must be D_minus_3 and D_minus_2")
    if set(
        require_string_list(
            floor_scope.get("bounded_information_stages"),
            "protocol.decision_policy.floor_scope.bounded_information_stages",
            allow_empty=False,
        )
    ) != {"D_minus_1", "DX"}:
        raise DiscoveryValidationError("protocol bounded-information stages must be D_minus_1 and DX")
    if decision_policy.get("epistemic_status") != "provisional_uncalibrated_forecast_heuristic":
        raise DiscoveryValidationError("protocol hostile T0 floor must remain explicitly uncalibrated")
    if require_bool(
        decision_policy.get("probability_alone_can_terminalize"),
        "protocol.decision_policy.probability_alone_can_terminalize",
    ) is not False:
        raise DiscoveryValidationError("protocol probability alone cannot terminalize a route")
    if require_bool(
        decision_policy.get("terminalization_requires_independent_hard_gate"),
        "protocol.decision_policy.terminalization_requires_independent_hard_gate",
    ) is not True:
        raise DiscoveryValidationError("protocol terminalization must require an independent hard gate")
    if (
        decision_policy.get("bounded_information_action_rule")
        != "positive_robust_value_of_information_and_no_failed_hard_gate"
    ):
        raise DiscoveryValidationError("protocol bounded information work must use robust value of information")
    if (
        decision_policy.get("robust_net_value_expression")
        != "salvage_value + p_lower * (success_value - salvage_value) - action_cost > 0"
    ):
        raise DiscoveryValidationError("protocol robust net-value expression differs from validator")
    minimum_resolved = require_positive_integer(
        decision_policy.get("minimum_resolved_forecasts_before_floor_review"),
        "protocol.decision_policy.minimum_resolved_forecasts_before_floor_review",
    )
    if minimum_resolved != 20:
        raise DiscoveryValidationError("protocol probability-floor review requires exactly 20 forecasts")
    if require_bool(
        decision_policy.get("historical_post_audit_probabilities_scored"),
        "protocol.decision_policy.historical_post_audit_probabilities_scored",
    ) is not False:
        raise DiscoveryValidationError("historical post-audit probabilities cannot be scored as forecasts")
    forecast_ledger = require_string(
        decision_policy.get("forecast_ledger"),
        "protocol.decision_policy.forecast_ledger",
    )
    if forecast_ledger != "research/discovery/forecast_ledger.yaml":
        raise DiscoveryValidationError("protocol forecast ledger path differs from validator")
    safe_repo_path(repo_root, forecast_ledger, "protocol.decision_policy.forecast_ledger")
    search_policy, search_ledger, trigger_ledger = validate_topic_search_policy(
        repo_root,
        protocol,
    )
    nature = require_mapping(
        protocol.get("nature_scale_evidence"),
        "protocol.nature_scale_evidence",
    )
    nature_fields = {
        "irreducible_core_required",
        "same_estimand_truth_required",
        "breadth_required",
        "error_control_required",
        "sim_to_real_same_loop_required_when_claimed",
        "strong_baseline_and_cost_pareto_required_for_method_claim",
        "honest_limitations_and_open_artifacts_required",
    }
    require_exact_fields(nature, nature_fields, "protocol.nature_scale_evidence")
    require_string(
        nature.get("irreducible_core_required"),
        "protocol.nature_scale_evidence.irreducible_core_required",
    )
    require_string(
        nature.get("same_estimand_truth_required"),
        "protocol.nature_scale_evidence.same_estimand_truth_required",
    )
    require_string_list(
        nature.get("breadth_required"),
        "protocol.nature_scale_evidence.breadth_required",
        allow_empty=False,
    )
    for field in nature_fields - {
        "irreducible_core_required",
        "same_estimand_truth_required",
        "breadth_required",
    }:
        require_bool(
            nature.get(field),
            f"protocol.nature_scale_evidence.{field}",
        )
    forbidden = set(
        require_string_list(
            protocol.get("forbidden_before_active"),
            "protocol.forbidden_before_active",
            allow_empty=False,
        )
    )
    sandbox = require_mapping(
        protocol.get("disposable_exploration_sandbox"),
        "protocol.disposable_exploration_sandbox",
    )
    sandbox_fields = {
        "purpose",
        "status_effect",
        "maximum_cpu_seconds",
        "maximum_storage_bytes",
        "maximum_monetary_cost_usd_micros",
        "maximum_gpu_seconds",
        "maximum_branches",
        "maximum_ttl_seconds",
        "allowed_actions",
        "required_forbidden_actions",
        "require_separate_authorization",
        "require_asset_provenance",
        "require_immutable_partition",
        "require_append_only_hypothesis_ledger",
        "require_multiplicity_ledger",
        "require_nonoverlapping_confirmation_holdout",
        "require_protected_base_prefix_ci",
        "require_oci_runtime_isolation",
        "require_source_bound_oci_conformance_report",
        "ambiguous_runtime_interruption",
        "require_confirmation_unmaterialized",
        "scientific_claims_allowed",
        "route_activation_allowed",
    }
    require_exact_fields(
        sandbox,
        sandbox_fields,
        "protocol.disposable_exploration_sandbox",
    )
    require_string(sandbox.get("purpose"), "protocol.sandbox.purpose")
    if require_string(sandbox.get("status_effect"), "protocol.sandbox.status_effect") != "none":
        raise DiscoveryValidationError("protocol sandbox status_effect must be none")
    hard_limits = {
        "maximum_cpu_seconds": SANDBOX_HARD_MAX_CPU_SECONDS,
        "maximum_storage_bytes": SANDBOX_HARD_MAX_STORAGE_BYTES,
        "maximum_monetary_cost_usd_micros": SANDBOX_HARD_MAX_MONETARY_COST_USD_MICROS,
        "maximum_gpu_seconds": SANDBOX_HARD_MAX_GPU_SECONDS,
        "maximum_branches": SANDBOX_HARD_MAX_BRANCHES,
        "maximum_ttl_seconds": SANDBOX_HARD_MAX_TTL_SECONDS,
    }
    for field, expected in hard_limits.items():
        actual = require_nonnegative_integer(sandbox.get(field), f"protocol.sandbox.{field}")
        if actual != expected:
            raise DiscoveryValidationError(
                f"protocol sandbox {field} must equal hard limit {expected}"
            )
    allowed_actions = set(
        require_string_list(
            sandbox.get("allowed_actions"),
            "protocol.sandbox.allowed_actions",
            allow_empty=False,
        )
    )
    if allowed_actions != SANDBOX_ACTIONS:
        raise DiscoveryValidationError("protocol sandbox allowed_actions differ from validator")
    required_forbidden = set(
        require_string_list(
            sandbox.get("required_forbidden_actions"),
            "protocol.sandbox.required_forbidden_actions",
            allow_empty=False,
        )
    )
    if required_forbidden != SANDBOX_REQUIRED_FORBIDDEN_ACTIONS:
        raise DiscoveryValidationError(
            "protocol sandbox required_forbidden_actions differ from validator"
        )
    for field in (
        "require_separate_authorization",
        "require_asset_provenance",
        "require_immutable_partition",
        "require_append_only_hypothesis_ledger",
        "require_multiplicity_ledger",
        "require_nonoverlapping_confirmation_holdout",
        "require_protected_base_prefix_ci",
        "require_oci_runtime_isolation",
        "require_source_bound_oci_conformance_report",
        "require_confirmation_unmaterialized",
    ):
        if require_bool(sandbox.get(field), f"protocol.sandbox.{field}") is not True:
            raise DiscoveryValidationError(f"protocol sandbox {field} must be true")
    interruption_policy = require_string(
        sandbox.get("ambiguous_runtime_interruption"),
        "protocol.sandbox.ambiguous_runtime_interruption",
    )
    if interruption_policy != SANDBOX_AMBIGUOUS_INTERRUPTION_POLICY:
        raise DiscoveryValidationError(
            "protocol sandbox ambiguous interruption policy differs from validator"
        )
    for field in ("scientific_claims_allowed", "route_activation_allowed"):
        if require_bool(sandbox.get(field), f"protocol.sandbox.{field}") is not False:
            raise DiscoveryValidationError(f"protocol sandbox {field} must be false")
    return (
        protocol,
        floor,
        minimum_primary,
        forbidden,
        sandbox,
        forecast_ledger,
        search_policy,
        search_ledger,
        trigger_ledger,
    )


def load_evidence_registry(repo_root: Path) -> dict[str, EvidenceMeta]:
    path = repo_root / "research" / "discovery" / "evidence_registry.yaml"
    root = load_yaml(path, "evidence registry")
    require_schema_version_one(root.get("schema_version"), "evidence registry.schema_version")
    require_date(root.get("retrieved_at"), "evidence registry.retrieved_at")
    evidence: dict[str, EvidenceMeta] = {}
    expected = {"id", "kind", "title", "uri", "version", "license", "role", "limitation"}
    for index, raw_source in enumerate(require_list(root.get("sources"), "evidence registry.sources")):
        context = f"evidence registry.sources[{index}]"
        source = require_mapping(raw_source, context)
        require_exact_fields(source, expected, context)
        source_id = require_id(source.get("id"), f"{context}.id")
        if source_id in evidence:
            raise DiscoveryValidationError(f"duplicate evidence id: {source_id}")
        evidence[source_id] = EvidenceMeta(epistemic_class="clean_external")
        for field in expected - {"id"}:
            require_string(source.get(field), f"{context}.{field}")
        uri = require_string(source.get("uri"), f"{context}.uri")
        if not uri.startswith(("https://", "http://")):
            raise DiscoveryValidationError(f"{context}.uri must be HTTP(S)")
    return evidence


def load_sandbox_taint_registry(repo_root: Path) -> list[Mapping[str, object]]:
    path = repo_root / "research" / "discovery" / "sandbox_taint_registry.yaml"
    root = load_yaml(path, "sandbox taint registry")
    require_schema_version_one(root.get("schema_version"), "sandbox taint registry.schema_version")
    require_exact_fields(root, {"schema_version", "sandbox_results"}, "sandbox taint registry")
    entries: list[Mapping[str, object]] = []
    expected = {
        "id",
        "kind",
        "sandbox_id",
        "artifact_ref",
        "artifact_sha256",
        "derived_from",
        "epistemic_class",
        "admissible_use",
    }
    seen: set[str] = set()
    for index, raw_entry in enumerate(
        require_list(root.get("sandbox_results"), "sandbox taint registry.sandbox_results")
    ):
        context = f"sandbox taint registry.sandbox_results[{index}]"
        entry = require_mapping(raw_entry, context)
        require_exact_fields(entry, expected, context)
        evidence_id = require_id(entry.get("id"), f"{context}.id")
        if evidence_id in seen:
            raise DiscoveryValidationError(f"duplicate sandbox taint evidence id: {evidence_id}")
        seen.add(evidence_id)
        if require_string(entry.get("kind"), f"{context}.kind") != "sandbox_result":
            raise DiscoveryValidationError(f"{context}.kind must be sandbox_result")
        require_id(entry.get("sandbox_id"), f"{context}.sandbox_id")
        require_string(entry.get("artifact_ref"), f"{context}.artifact_ref")
        require_sha256(entry.get("artifact_sha256"), f"{context}.artifact_sha256")
        if require_string_list(entry.get("derived_from"), f"{context}.derived_from"):
            raise DiscoveryValidationError(f"{context}.derived_from must be empty in schema v1")
        if entry.get("epistemic_class") != "sandbox_exploratory_tainted":
            raise DiscoveryValidationError(f"{context}.epistemic_class is invalid")
        if entry.get("admissible_use") != "screening_question_motivation_only":
            raise DiscoveryValidationError(f"{context}.admissible_use is invalid")
        entries.append(entry)
    return entries


def validate_evidence_refs(
    value: object,
    context: str,
    evidence: Mapping[str, EvidenceMeta],
    *,
    allow_empty: bool = True,
    allow_tainted: bool = False,
    require_tainted: bool = False,
) -> list[str]:
    refs = require_string_list(value, context, allow_empty=allow_empty)
    unknown = set(refs) - set(evidence)
    if unknown:
        raise DiscoveryValidationError(f"{context} has unknown evidence refs: {sorted(unknown)}")
    tainted = {ref for ref in refs if evidence[ref].tainted}
    if tainted and not allow_tainted:
        raise DiscoveryValidationError(
            f"{context} uses sandbox-tainted evidence outside motivation: {sorted(tainted)}"
        )
    if require_tainted:
        clean = set(refs) - tainted
        if clean:
            raise DiscoveryValidationError(
                f"{context} accepts only sandbox-tainted motivation refs: {sorted(clean)}"
            )
    return refs


def validate_forecast_ledger(
    repo_root: Path,
    ledger_ref: str,
    route_statuses: Mapping[str, str],
    known_evidence: Mapping[str, EvidenceMeta],
    activation_floor: float,
) -> tuple[int, int, int]:
    path = safe_repo_path(repo_root, ledger_ref, "forecast ledger")
    root = load_yaml(path, "forecast ledger")
    require_exact_fields(
        root,
        {
            "schema_version",
            "floor_review_target_id",
            "target_definitions",
            "forecasts",
            "resolutions",
        },
        "forecast ledger",
    )
    require_schema_version_one(root.get("schema_version"), "forecast ledger.schema_version")
    floor_target_id = require_id(
        root.get("floor_review_target_id"),
        "forecast ledger.floor_review_target_id",
    )

    target_fields = {
        "id",
        "statement",
        "point_scoring_rule",
        "interval_use",
        "counts_toward_activation_floor_review",
        "activation_floor",
    }
    target_ids: set[str] = set()
    floor_targets: set[str] = set()
    for index, raw_target in enumerate(
        require_list(root.get("target_definitions"), "forecast ledger.target_definitions")
    ):
        context = f"forecast ledger.target_definitions[{index}]"
        target = require_mapping(raw_target, context)
        require_exact_fields(target, target_fields, context)
        target_id = require_id(target.get("id"), f"{context}.id")
        if target_id in target_ids:
            raise DiscoveryValidationError(f"duplicate forecast target id: {target_id}")
        target_ids.add(target_id)
        require_string(target.get("statement"), f"{context}.statement")
        if target.get("point_scoring_rule") != "brier":
            raise DiscoveryValidationError(f"{context}.point_scoring_rule must be brier")
        if target.get("interval_use") != "calibration_diagnostic_only":
            raise DiscoveryValidationError(
                f"{context}.interval_use must be calibration_diagnostic_only"
            )
        counts_for_floor = require_bool(
            target.get("counts_toward_activation_floor_review"),
            f"{context}.counts_toward_activation_floor_review",
        )
        target_floor = require_probability(
            target.get("activation_floor"),
            f"{context}.activation_floor",
        )
        if not math.isclose(target_floor, activation_floor, rel_tol=0.0, abs_tol=1e-12):
            raise DiscoveryValidationError(f"{context}.activation_floor differs from protocol")
        if counts_for_floor:
            floor_targets.add(target_id)
    if floor_target_id not in target_ids:
        raise DiscoveryValidationError("forecast floor-review target is not defined")
    if floor_targets != {floor_target_id}:
        raise DiscoveryValidationError(
            "exactly the declared T0 target must count toward activation-floor review"
        )

    forecast_fields = {
        "id",
        "recorded_at",
        "subject_route_id",
        "target_id",
        "resolve_by",
        "lower",
        "point",
        "upper",
        "resolution_rule",
        "basis_evidence_refs",
    }
    forecast_ids: set[str] = set()
    forecast_times: dict[str, datetime] = {}
    forecast_targets: dict[str, str] = {}
    for index, raw_forecast in enumerate(
        require_list(root.get("forecasts"), "forecast ledger.forecasts")
    ):
        context = f"forecast ledger.forecasts[{index}]"
        forecast = require_mapping(raw_forecast, context)
        require_exact_fields(forecast, forecast_fields, context)
        forecast_id = require_id(forecast.get("id"), f"{context}.id")
        if forecast_id in forecast_ids:
            raise DiscoveryValidationError(f"duplicate forecast id: {forecast_id}")
        forecast_ids.add(forecast_id)
        recorded_at = require_utc_timestamp(forecast.get("recorded_at"), f"{context}.recorded_at")
        resolve_by = require_utc_timestamp(forecast.get("resolve_by"), f"{context}.resolve_by")
        if resolve_by <= recorded_at:
            raise DiscoveryValidationError(f"{context}.resolve_by must follow recorded_at")
        forecast_times[forecast_id] = recorded_at
        subject_route_id = require_id(
            forecast.get("subject_route_id"),
            f"{context}.subject_route_id",
        )
        if subject_route_id not in route_statuses:
            raise DiscoveryValidationError(
                f"{context}.subject_route_id is unknown: {subject_route_id}"
            )
        target_id = require_id(forecast.get("target_id"), f"{context}.target_id")
        if target_id not in target_ids:
            raise DiscoveryValidationError(f"{context}.target_id is unknown: {target_id}")
        forecast_targets[forecast_id] = target_id
        lower = require_probability(forecast.get("lower"), f"{context}.lower")
        point = require_probability(forecast.get("point"), f"{context}.point")
        upper = require_probability(forecast.get("upper"), f"{context}.upper")
        if not lower <= point <= upper:
            raise DiscoveryValidationError(f"{context} forecast interval must satisfy lower <= point <= upper")
        require_string(forecast.get("resolution_rule"), f"{context}.resolution_rule")
        validate_evidence_refs(
            forecast.get("basis_evidence_refs"),
            f"{context}.basis_evidence_refs",
            known_evidence,
            allow_empty=False,
        )

    resolution_fields = {
        "forecast_id",
        "resolved_at",
        "outcome",
        "evidence_refs",
        "rationale",
    }
    resolved_ids: set[str] = set()
    floor_resolved = 0
    for index, raw_resolution in enumerate(
        require_list(root.get("resolutions"), "forecast ledger.resolutions")
    ):
        context = f"forecast ledger.resolutions[{index}]"
        resolution = require_mapping(raw_resolution, context)
        require_exact_fields(resolution, resolution_fields, context)
        forecast_id = require_id(resolution.get("forecast_id"), f"{context}.forecast_id")
        if forecast_id not in forecast_ids:
            raise DiscoveryValidationError(f"{context} references unknown forecast {forecast_id}")
        if forecast_id in resolved_ids:
            raise DiscoveryValidationError(f"duplicate resolution for forecast {forecast_id}")
        resolved_ids.add(forecast_id)
        resolved_at = require_utc_timestamp(
            resolution.get("resolved_at"),
            f"{context}.resolved_at",
        )
        if resolved_at < forecast_times[forecast_id]:
            raise DiscoveryValidationError(f"{context}.resolved_at precedes forecast")
        require_bool(resolution.get("outcome"), f"{context}.outcome")
        validate_evidence_refs(
            resolution.get("evidence_refs"),
            f"{context}.evidence_refs",
            known_evidence,
            allow_empty=False,
        )
        require_string(resolution.get("rationale"), f"{context}.rationale")
        if forecast_targets[forecast_id] == floor_target_id:
            floor_resolved += 1
    return len(forecast_ids), len(resolved_ids), floor_resolved


def validate_search_cycle_ledger(
    repo_root: Path,
    ledger_ref: str,
) -> tuple[int, int, int]:
    path = safe_repo_path(repo_root, ledger_ref, "search-cycle ledger")
    root = load_yaml(path, "search-cycle ledger")
    require_exact_fields(
        root,
        {
            "schema_version",
            "policy_id",
            "scope_start_cycle",
            "historical_baseline",
            "cycles",
        },
        "search-cycle ledger",
    )
    require_schema_version_one(root.get("schema_version"), "search-cycle ledger.schema_version")
    if root.get("policy_id") != "ecomd_topic_search_funnel_v1":
        raise DiscoveryValidationError("search-cycle ledger policy id differs from protocol")
    if require_positive_integer(
        root.get("scope_start_cycle"),
        "search-cycle ledger.scope_start_cycle",
    ) != 10:
        raise DiscoveryValidationError("search-cycle ledger must begin prospectively at cycle 10")

    baseline = require_mapping(
        root.get("historical_baseline"),
        "search-cycle ledger.historical_baseline",
    )
    require_exact_fields(
        baseline,
        {
            "cycles_completed",
            "formulations_screened",
            "machine_cards_created",
            "prospective_full_t0_forecasts",
            "status",
            "note",
        },
        "search-cycle ledger.historical_baseline",
    )
    fixed_baseline = {
        "cycles_completed": 9,
        "formulations_screened": 56,
        "machine_cards_created": 0,
        "prospective_full_t0_forecasts": 0,
    }
    for field, expected in fixed_baseline.items():
        actual = require_nonnegative_integer(
            baseline.get(field),
            f"search-cycle ledger.historical_baseline.{field}",
        )
        if actual != expected:
            raise DiscoveryValidationError(
                f"search-cycle historical baseline {field} must equal {expected}"
            )
    if baseline.get("status") != "retrospective_unscored":
        raise DiscoveryValidationError("search-cycle historical baseline must remain unscored")
    require_string(baseline.get("note"), "search-cycle ledger.historical_baseline.note")

    cycle_fields = {
        "id",
        "started_at",
        "completed_at",
        "result_ref",
        "literature_cutoff",
        "outcome_accessed",
        "counts",
        "final_dispositions",
        "source_lane_counts",
        "archetype_counts",
        "efficiency",
        "surviving_program_ids",
        "record_quality",
        "notes",
    }
    efficiency_fields = {
        "primary_sources_opened",
        "killer_toys_constructed",
        "simulator_runs",
        "outcome_assets_accessed",
        "reusable_assets_recorded",
    }
    record_quality_fields = {
        "all_raw_questions_recorded",
        "stage_decisions_recorded",
        "probability_only_terminalizations",
    }
    cycle_ids: set[str] = set()
    prior_cycle_number = 9
    raw_total = 0
    card_total = 0
    for index, raw_cycle in enumerate(
        require_list(root.get("cycles"), "search-cycle ledger.cycles")
    ):
        context = f"search-cycle ledger.cycles[{index}]"
        cycle = require_mapping(raw_cycle, context)
        optional_cycle_fields = {"deferred_at_f1"} & set(cycle)
        require_exact_fields(cycle, cycle_fields | optional_cycle_fields, context)
        cycle_id = require_id(cycle.get("id"), f"{context}.id")
        if cycle_id in cycle_ids:
            raise DiscoveryValidationError(f"duplicate search-cycle id: {cycle_id}")
        cycle_ids.add(cycle_id)
        match = re.fullmatch(r"discovery_cycle_(\d+)_\d{8}", cycle_id)
        if match is None:
            raise DiscoveryValidationError(f"{context}.id must encode cycle number and date")
        cycle_number = int(match.group(1))
        if cycle_number != prior_cycle_number + 1:
            raise DiscoveryValidationError("search-cycle numbers must be consecutive from cycle 10")
        prior_cycle_number = cycle_number
        started = require_utc_timestamp(cycle.get("started_at"), f"{context}.started_at")
        completed = require_utc_timestamp(cycle.get("completed_at"), f"{context}.completed_at")
        if completed < started:
            raise DiscoveryValidationError(f"{context}.completed_at precedes started_at")
        result_ref = require_string(cycle.get("result_ref"), f"{context}.result_ref")
        safe_repo_path(repo_root, result_ref, f"{context}.result_ref")
        require_date(cycle.get("literature_cutoff"), f"{context}.literature_cutoff")
        if require_bool(cycle.get("outcome_accessed"), f"{context}.outcome_accessed"):
            raise DiscoveryValidationError(f"{context} cannot access outcomes during topic search")

        counts = require_mapping(cycle.get("counts"), f"{context}.counts")
        require_exact_fields(counts, set(SEARCH_CYCLE_LIMITS), f"{context}.counts")
        parsed_counts: dict[str, int] = {}
        for field, maximum in SEARCH_CYCLE_LIMITS.items():
            value = require_nonnegative_integer(counts.get(field), f"{context}.counts.{field}")
            if value > maximum:
                raise DiscoveryValidationError(
                    f"{context}.counts.{field} exceeds funnel limit {maximum}"
                )
            parsed_counts[field] = value
        if not (
            parsed_counts["raw_question_programs"]
            >= parsed_counts["quick_screens"]
            >= parsed_counts["collision_screens"]
            >= parsed_counts["full_hostile_audits"]
            >= parsed_counts["machine_cards"]
        ):
            raise DiscoveryValidationError(f"{context}.counts violate funnel monotonicity")

        dispositions = require_mapping(
            cycle.get("final_dispositions"),
            f"{context}.final_dispositions",
        )
        require_exact_fields(dispositions, SEARCH_FINAL_DISPOSITIONS, f"{context}.final_dispositions")
        parsed_dispositions = {
            field: require_nonnegative_integer(
                dispositions.get(field),
                f"{context}.final_dispositions.{field}",
            )
            for field in SEARCH_FINAL_DISPOSITIONS
        }
        if sum(parsed_dispositions.values()) != parsed_counts["raw_question_programs"]:
            raise DiscoveryValidationError(f"{context} final dispositions do not sum to raw questions")
        if parsed_dispositions["portfolio_pruned"] != (
            parsed_counts["raw_question_programs"] - parsed_counts["quick_screens"]
        ):
            raise DiscoveryValidationError(f"{context} portfolio-pruned count is inconsistent")
        deferred_at_f1 = require_nonnegative_integer(
            cycle.get("deferred_at_f1", 0), f"{context}.deferred_at_f1"
        )
        if deferred_at_f1 > parsed_dispositions["deferred"]:
            raise DiscoveryValidationError(f"{context} F1 deferrals exceed total deferrals")
        if (
            parsed_dispositions["quick_closed"]
            + parsed_dispositions["deduplicated"]
            + deferred_at_f1
        ) != (
            parsed_counts["quick_screens"] - parsed_counts["collision_screens"]
        ):
            raise DiscoveryValidationError(f"{context} quick-screen dispositions are inconsistent")
        if (
            parsed_dispositions["collision_closed"]
            + parsed_dispositions["deferred"]
            - deferred_at_f1
        ) != (
            parsed_counts["collision_screens"] - parsed_counts["full_hostile_audits"]
        ):
            raise DiscoveryValidationError(f"{context} collision-screen dispositions are inconsistent")
        if parsed_dispositions["full_closed"] + parsed_dispositions["advanced"] != (
            parsed_counts["full_hostile_audits"]
        ):
            raise DiscoveryValidationError(f"{context} full-audit dispositions are inconsistent")
        if parsed_dispositions["advanced"] != parsed_counts["machine_cards"]:
            raise DiscoveryValidationError(f"{context} advanced count must equal machine cards")

        for field, expected_keys in (
            ("source_lane_counts", SEARCH_SOURCE_LANES),
            ("archetype_counts", SEARCH_TOPIC_ARCHETYPES),
        ):
            distribution = require_mapping(cycle.get(field), f"{context}.{field}")
            require_exact_fields(distribution, expected_keys, f"{context}.{field}")
            total = sum(
                require_nonnegative_integer(value, f"{context}.{field}.{key}")
                for key, value in distribution.items()
            )
            if total != parsed_counts["raw_question_programs"]:
                raise DiscoveryValidationError(f"{context}.{field} does not sum to raw questions")

        efficiency = require_mapping(cycle.get("efficiency"), f"{context}.efficiency")
        require_exact_fields(efficiency, efficiency_fields, f"{context}.efficiency")
        for field in efficiency_fields:
            require_nonnegative_integer(efficiency.get(field), f"{context}.efficiency.{field}")
        if efficiency.get("simulator_runs") != 0 or efficiency.get("outcome_assets_accessed") != 0:
            raise DiscoveryValidationError(f"{context} paper-only search used outcomes or simulation")

        survivors = require_string_list(
            cycle.get("surviving_program_ids"),
            f"{context}.surviving_program_ids",
        )
        if len(survivors) != parsed_dispositions["advanced"] + parsed_dispositions["deferred"]:
            raise DiscoveryValidationError(f"{context} survivor ids do not match dispositions")
        for survivor in survivors:
            require_id(survivor, f"{context}.surviving_program_ids")

        quality = require_mapping(cycle.get("record_quality"), f"{context}.record_quality")
        require_exact_fields(quality, record_quality_fields, f"{context}.record_quality")
        for field in ("all_raw_questions_recorded", "stage_decisions_recorded"):
            if require_bool(quality.get(field), f"{context}.record_quality.{field}") is not True:
                raise DiscoveryValidationError(f"{context}.record_quality.{field} must be true")
        if require_nonnegative_integer(
            quality.get("probability_only_terminalizations"),
            f"{context}.record_quality.probability_only_terminalizations",
        ) != 0:
            raise DiscoveryValidationError(f"{context} terminalized a question by probability alone")
        require_string(cycle.get("notes"), f"{context}.notes")
        raw_total += parsed_counts["raw_question_programs"]
        card_total += parsed_counts["machine_cards"]
    return len(cycle_ids), raw_total, card_total


def validate_reentry_trigger_ledger(
    repo_root: Path,
    ledger_ref: str,
    route_ids: set[str],
    route_failure_codes: Mapping[str, set[str]],
    family_ids: set[str],
    known_evidence: Mapping[str, EvidenceMeta],
) -> tuple[int, int]:
    path = safe_repo_path(repo_root, ledger_ref, "re-entry trigger ledger")
    root = load_yaml(path, "re-entry trigger ledger")
    require_exact_fields(
        root,
        {"schema_version", "policy_id", "entries"},
        "re-entry trigger ledger",
    )
    require_schema_version_one(
        root.get("schema_version"),
        "re-entry trigger ledger.schema_version",
    )
    if root.get("policy_id") != "ecomd_search_family_reentry_v1":
        raise DiscoveryValidationError("re-entry trigger ledger policy id differs from protocol")

    entry_fields = {
        "id",
        "recorded_at",
        "source_kind",
        "evidence_refs",
        "related_route_ids",
        "related_failure_family_ids",
        "capability_claim",
        "audited_claims",
        "decision",
        "removed_blockers",
        "remaining_blockers",
        "candidate_harvest_authorized",
        "exact_reentry_scope",
        "next_review_condition",
        "result_ref",
        "outcome_accessed",
        "supersedes_entry_ids",
    }
    claim_fields = {"id", "claim", "verdict", "evidence_refs"}
    entry_ids: set[str] = set()
    qualified_count = 0
    previous_recorded_at: datetime | None = None
    for index, raw_entry in enumerate(
        require_list(root.get("entries"), "re-entry trigger ledger.entries")
    ):
        context = f"re-entry trigger ledger.entries[{index}]"
        entry = require_mapping(raw_entry, context)
        require_exact_fields(entry, entry_fields, context)
        entry_id = require_id(entry.get("id"), f"{context}.id")
        if entry_id in entry_ids:
            raise DiscoveryValidationError(f"duplicate re-entry trigger id: {entry_id}")
        recorded_at = require_utc_timestamp(entry.get("recorded_at"), f"{context}.recorded_at")
        if previous_recorded_at is not None and recorded_at < previous_recorded_at:
            raise DiscoveryValidationError("re-entry trigger entries must be chronological")
        previous_recorded_at = recorded_at

        source_kind = require_string(entry.get("source_kind"), f"{context}.source_kind")
        if source_kind not in REENTRY_TRIGGER_SOURCE_KINDS:
            raise DiscoveryValidationError(f"{context}.source_kind is unknown")
        validate_evidence_refs(
            entry.get("evidence_refs"),
            f"{context}.evidence_refs",
            known_evidence,
            allow_empty=False,
        )
        related_routes = set(
            require_string_list(
                entry.get("related_route_ids"),
                f"{context}.related_route_ids",
                allow_empty=False,
            )
        )
        unknown_routes = related_routes - route_ids
        if unknown_routes:
            raise DiscoveryValidationError(
                f"{context} has unknown related routes: {sorted(unknown_routes)}"
            )
        related_families = set(
            require_string_list(
                entry.get("related_failure_family_ids"),
                f"{context}.related_failure_family_ids",
                allow_empty=False,
            )
        )
        unknown_families = related_families - family_ids
        if unknown_families:
            raise DiscoveryValidationError(
                f"{context} has unknown failure families: {sorted(unknown_families)}"
            )
        require_string(entry.get("capability_claim"), f"{context}.capability_claim")

        claim_verdicts: list[str] = []
        claim_ids: set[str] = set()
        for claim_index, raw_claim in enumerate(
            require_list(entry.get("audited_claims"), f"{context}.audited_claims")
        ):
            claim_context = f"{context}.audited_claims[{claim_index}]"
            claim = require_mapping(raw_claim, claim_context)
            require_exact_fields(claim, claim_fields, claim_context)
            claim_id = require_id(claim.get("id"), f"{claim_context}.id")
            if claim_id in claim_ids:
                raise DiscoveryValidationError(f"{context} has duplicate audited claim {claim_id}")
            claim_ids.add(claim_id)
            require_string(claim.get("claim"), f"{claim_context}.claim")
            verdict = require_string(claim.get("verdict"), f"{claim_context}.verdict")
            if verdict not in REENTRY_TRIGGER_CLAIM_VERDICTS:
                raise DiscoveryValidationError(f"{claim_context}.verdict is unknown")
            claim_verdicts.append(verdict)
            validate_evidence_refs(
                claim.get("evidence_refs"),
                f"{claim_context}.evidence_refs",
                known_evidence,
                allow_empty=False,
            )
        if not claim_ids:
            raise DiscoveryValidationError(f"{context}.audited_claims cannot be empty")

        decision = require_string(entry.get("decision"), f"{context}.decision")
        if decision not in REENTRY_TRIGGER_DECISIONS:
            raise DiscoveryValidationError(f"{context}.decision is unknown")
        removed = set(
            require_string_list(
                entry.get("removed_blockers"),
                f"{context}.removed_blockers",
            )
        )
        remaining = set(
            require_string_list(
                entry.get("remaining_blockers"),
                f"{context}.remaining_blockers",
                allow_empty=False,
            )
        )
        for blocker in removed | remaining:
            require_id(blocker, f"{context}.blocker")
        overlap = removed & remaining
        if overlap:
            raise DiscoveryValidationError(
                f"{context} lists blockers as both removed and remaining: {sorted(overlap)}"
            )
        recorded_route_blockers = set().union(
            *(route_failure_codes[route_id] for route_id in related_routes)
        )
        unknown_removed = removed - recorded_route_blockers
        if unknown_removed:
            raise DiscoveryValidationError(
                f"{context} claims to remove unrecorded blockers: {sorted(unknown_removed)}"
            )
        authorized = require_bool(
            entry.get("candidate_harvest_authorized"),
            f"{context}.candidate_harvest_authorized",
        )
        if authorized != (decision == "qualified_trigger"):
            raise DiscoveryValidationError(
                f"{context} may authorize candidate harvesting only for a qualified trigger"
            )
        reentry_scope = require_string(
            entry.get("exact_reentry_scope"),
            f"{context}.exact_reentry_scope",
        )
        if authorized:
            qualified_count += 1
            if not removed or "satisfied" not in claim_verdicts:
                raise DiscoveryValidationError(
                    f"{context} qualified trigger must remove a blocker with a satisfied audited claim"
                )
            if reentry_scope == "none":
                raise DiscoveryValidationError(f"{context} qualified trigger needs a bounded scope")
        elif reentry_scope != "none":
            raise DiscoveryValidationError(
                f"{context} non-trigger must set exact_reentry_scope to none"
            )
        if decision == "not_trigger" and removed:
            raise DiscoveryValidationError(f"{context} non-trigger cannot remove a blocker")
        if decision == "partial_capability" and not ({"partial", "satisfied"} & set(claim_verdicts)):
            raise DiscoveryValidationError(
                f"{context} partial capability needs a partial or satisfied audited claim"
            )

        require_string(
            entry.get("next_review_condition"),
            f"{context}.next_review_condition",
        )
        result_ref = require_string(entry.get("result_ref"), f"{context}.result_ref")
        safe_repo_path(repo_root, result_ref, f"{context}.result_ref")
        if require_bool(entry.get("outcome_accessed"), f"{context}.outcome_accessed"):
            raise DiscoveryValidationError(f"{context} cannot inspect outcomes during trigger audit")
        supersedes = require_string_list(
            entry.get("supersedes_entry_ids"),
            f"{context}.supersedes_entry_ids",
        )
        if len(supersedes) != len(set(supersedes)):
            raise DiscoveryValidationError(f"{context} has duplicate superseded entries")
        unknown_superseded = set(supersedes) - entry_ids
        if unknown_superseded:
            raise DiscoveryValidationError(
                f"{context} supersedes unknown or later entries: {sorted(unknown_superseded)}"
            )
        entry_ids.add(entry_id)
    return len(entry_ids), qualified_count


def load_failure_families(repo_root: Path, route_ids: set[str]) -> set[str]:
    path = repo_root / "research" / "discovery" / "failure_families.yaml"
    root = load_yaml(path, "failure families")
    require_schema_version_one(root.get("schema_version"), "failure families.schema_version")
    ids: set[str] = set()
    expected = {"id", "definition", "canonical_route_ids", "mandatory_test", "reopen_evidence"}
    for index, raw_family in enumerate(require_list(root.get("families"), "failure families.families")):
        context = f"failure families.families[{index}]"
        family = require_mapping(raw_family, context)
        require_exact_fields(family, expected, context)
        family_id = require_id(family.get("id"), f"{context}.id")
        if family_id in ids:
            raise DiscoveryValidationError(f"duplicate failure family id: {family_id}")
        ids.add(family_id)
        routes = require_string_list(
            family.get("canonical_route_ids"),
            f"{context}.canonical_route_ids",
            allow_empty=False,
        )
        unknown = set(routes) - route_ids
        if unknown:
            raise DiscoveryValidationError(f"{context} has unknown canonical routes: {sorted(unknown)}")
        require_string(family.get("definition"), f"{context}.definition")
        require_string(family.get("mandatory_test"), f"{context}.mandatory_test")
        require_string(family.get("reopen_evidence"), f"{context}.reopen_evidence")
    return ids


def load_decision_history(
    repo_root: Path,
    known_evidence: Mapping[str, EvidenceMeta],
) -> tuple[dict[str, str], int]:
    path = repo_root / "research" / "discovery" / "decision_history.yaml"
    root = load_yaml(path, "decision history")
    require_schema_version_one(root.get("schema_version"), "decision history.schema_version")
    latest_status: dict[str, str] = {}
    previous_target: dict[str, str] = {}
    expected = {
        "card_id",
        "transitioned_at",
        "from_status",
        "to_status",
        "prior_card_sha256",
        "prior_decision_sha256",
        "rationale_artifact",
        "evidence_refs",
    }
    transitions = require_list(root.get("transitions"), "decision history.transitions")
    for index, raw_transition in enumerate(transitions):
        context = f"decision history.transitions[{index}]"
        transition = require_mapping(raw_transition, context)
        require_exact_fields(transition, expected, context)
        card_id = require_id(transition.get("card_id"), f"{context}.card_id")
        require_date(transition.get("transitioned_at"), f"{context}.transitioned_at")
        from_status = require_string(transition.get("from_status"), f"{context}.from_status")
        to_status = require_string(transition.get("to_status"), f"{context}.to_status")
        if from_status not in CARD_STATUSES or to_status not in CARD_STATUSES:
            raise DiscoveryValidationError(f"{context} contains an unknown status")
        if from_status == to_status:
            raise DiscoveryValidationError(f"{context} must change status")
        if card_id in previous_target and previous_target[card_id] != from_status:
            raise DiscoveryValidationError(f"{context} does not continue the prior status chain")
        for field in ("prior_card_sha256", "prior_decision_sha256"):
            digest = require_string(transition.get(field), f"{context}.{field}")
            if SHA256_PATTERN.fullmatch(digest) is None:
                raise DiscoveryValidationError(f"{context}.{field} is not a SHA-256 digest")
        artifact = require_string(transition.get("rationale_artifact"), f"{context}.rationale_artifact")
        safe_repo_path(repo_root, artifact, f"{context}.rationale_artifact")
        validate_evidence_refs(
            transition.get("evidence_refs"),
            f"{context}.evidence_refs",
            known_evidence,
            allow_empty=False,
        )
        previous_target[card_id] = to_status
        latest_status[card_id] = to_status
    return latest_status, len(transitions)


def validate_novelty_manifest(
    path: Path,
    card_id: str,
    evidence: Mapping[str, EvidenceMeta],
    minimum_primary: int,
    status: str,
) -> int:
    root = load_yaml(path, f"novelty manifest for {card_id}")
    expected = {
        "schema_version",
        "card_id",
        "cutoff_date",
        "databases",
        "queries",
        "inclusion_rules",
        "exclusion_rules",
        "works",
        "unresolved_direct_collisions",
    }
    require_exact_fields(root, expected, f"novelty manifest for {card_id}")
    require_schema_version_one(root.get("schema_version"), f"novelty manifest for {card_id}.schema_version")
    if root.get("card_id") != card_id:
        raise DiscoveryValidationError(f"novelty manifest identity mismatch for {card_id}")
    require_date(root.get("cutoff_date"), f"{card_id}.novelty.cutoff_date")
    for field in ("databases", "queries", "inclusion_rules", "exclusion_rules"):
        require_string_list(root.get(field), f"{card_id}.novelty.{field}", allow_empty=False)
    work_ids: set[str] = set()
    primary_count = 0
    works = require_list(root.get("works"), f"{card_id}.novelty.works")
    work_fields = {
        "id",
        "title",
        "year",
        "classification",
        "directness",
        "claim_overlap",
        "disposition",
        "evidence_ref",
        "primary",
    }
    for index, raw_work in enumerate(works):
        context = f"{card_id}.novelty.works[{index}]"
        work = require_mapping(raw_work, context)
        require_exact_fields(work, work_fields, context)
        work_id = require_id(work.get("id"), f"{context}.id")
        if work_id in work_ids:
            raise DiscoveryValidationError(f"duplicate novelty work id: {work_id}")
        work_ids.add(work_id)
        require_string(work.get("title"), f"{context}.title")
        year = work.get("year")
        if type(year) is not int or not 1900 <= year <= 2100:
            raise DiscoveryValidationError(f"{context}.year is invalid")
        classification = require_string(work.get("classification"), f"{context}.classification")
        if classification not in NOVELTY_CLASSIFICATIONS:
            raise DiscoveryValidationError(f"{context}.classification is unknown")
        for field in ("directness", "claim_overlap", "disposition"):
            require_string(work.get(field), f"{context}.{field}")
        validate_evidence_refs(
            [work.get("evidence_ref")],
            f"{context}.evidence_ref",
            evidence,
            allow_empty=False,
        )
        if require_bool(work.get("primary"), f"{context}.primary"):
            primary_count += 1
    unresolved = require_string_list(
        root.get("unresolved_direct_collisions"),
        f"{card_id}.novelty.unresolved_direct_collisions",
    )
    if not set(unresolved) <= work_ids:
        raise DiscoveryValidationError(f"{card_id} novelty has unknown unresolved work ids")
    if status != "screening" and primary_count < minimum_primary:
        raise DiscoveryValidationError(
            f"{card_id} has {primary_count} primary works, below minimum {minimum_primary}"
        )
    if status == "active" and unresolved:
        raise DiscoveryValidationError(f"active card {card_id} has unresolved direct collisions")
    return primary_count


def validate_probability_range(value: object, context: str) -> tuple[float, float]:
    mapping = require_mapping(value, context)
    lower = require_probability(mapping.get("lower"), f"{context}.lower")
    upper = require_probability(mapping.get("upper"), f"{context}.upper")
    if lower > upper:
        raise DiscoveryValidationError(f"{context}.lower exceeds upper")
    return lower, upper


def validate_card(
    path: Path,
    repo_root: Path,
    card_schema: Mapping[str, object],
    route_statuses: Mapping[str, str],
    known_evidence: Mapping[str, EvidenceMeta],
    family_ids: set[str],
    activation_floor: float,
    minimum_primary: int,
    forbidden_before_active: set[str],
) -> tuple[str, str, int]:
    card = load_yaml(path, f"topic card {path.name}")
    validate_json_instance(card_schema, card, f"topic card {path.name}")
    require_exact_fields(card, CARD_FIELDS, f"topic card {path.name}")
    require_schema_version_one(card.get("schema_version"), f"{path.name}.schema_version")
    card_id = require_id(card.get("id"), f"{path.name}.id")
    if path.stem != card_id:
        raise DiscoveryValidationError(f"card filename must equal id: {card_id}")
    require_string(card.get("title"), f"{card_id}.title")
    created_at = require_date(card.get("created_at"), f"{card_id}.created_at")
    status = require_string(card.get("status"), f"{card_id}.status")
    if status not in CARD_STATUSES:
        raise DiscoveryValidationError(f"{card_id}.status is unknown: {status}")
    stage = require_string(card.get("stage"), f"{card_id}.stage")
    if stage not in STAGES:
        raise DiscoveryValidationError(f"{card_id}.stage is unknown: {stage}")
    if status == "failed_closed":
        closed_at = require_date(card.get("closed_at"), f"{card_id}.closed_at")
        if closed_at < created_at:
            raise DiscoveryValidationError(f"{card_id}.closed_at precedes created_at")
    elif card.get("closed_at") is not None:
        raise DiscoveryValidationError(f"{card_id}.closed_at must be null for {status}")

    parent_ids = require_string_list(
        card.get("parent_route_ids"), f"{card_id}.parent_route_ids", allow_empty=False
    )
    unknown_parents = set(parent_ids) - set(route_statuses)
    if unknown_parents:
        raise DiscoveryValidationError(f"{card_id} has unknown parent routes: {sorted(unknown_parents)}")

    scope = require_mapping(card.get("scope"), f"{card_id}.scope")
    for field in ("scientific_domain", "target_venues"):
        require_string_list(scope.get(field), f"{card_id}.scope.{field}", allow_empty=False)
    require_string(scope.get("outcome_access"), f"{card_id}.scope.outcome_access")

    object_spec = require_mapping(card.get("object"), f"{card_id}.object")
    for field in ("native_state", "intervention", "observable"):
        require_string(object_spec.get(field), f"{card_id}.object.{field}")
    require_string_list(
        object_spec.get("invariances"), f"{card_id}.object.invariances", allow_empty=False
    )
    claim = require_mapping(card.get("claim"), f"{card_id}.claim")
    for field in ("exact_question", "falsifiable_statement", "theorem_or_phenomenon"):
        require_string(claim.get(field), f"{card_id}.claim.{field}")
    require_string_list(
        claim.get("explicit_nonclaims"), f"{card_id}.claim.explicit_nonclaims", allow_empty=False
    )

    novelty_raw = require_string(card.get("novelty_manifest"), f"{card_id}.novelty_manifest")
    novelty_path = safe_repo_path(repo_root, novelty_raw, f"{card_id}.novelty_manifest")
    primary_count = validate_novelty_manifest(
        novelty_path, card_id, known_evidence, minimum_primary, status
    )

    killer_ids: set[str] = set()
    killer_statuses: list[str] = []
    killer_fields = {
        "id",
        "type",
        "construction",
        "claim_prediction",
        "kill_condition",
        "status",
        "evidence_refs",
    }
    killers = require_list(card.get("killer_tests"), f"{card_id}.killer_tests")
    if stage in {"D_minus_1", "D0", "D1", "D2"} and len(killers) < 2:
        raise DiscoveryValidationError(f"{card_id} must have at least two killer tests")
    killer_ref_counts: list[int] = []
    for index, raw_killer in enumerate(killers):
        context = f"{card_id}.killer_tests[{index}]"
        killer = require_mapping(raw_killer, context)
        require_exact_fields(killer, killer_fields, context)
        killer_id = require_id(killer.get("id"), f"{context}.id")
        if killer_id in killer_ids:
            raise DiscoveryValidationError(f"duplicate killer id in {card_id}: {killer_id}")
        killer_ids.add(killer_id)
        killer_type = require_string(killer.get("type"), f"{context}.type")
        if killer_type not in KILLER_TYPES:
            raise DiscoveryValidationError(f"{context}.type is unknown")
        for field in ("construction", "claim_prediction", "kill_condition"):
            require_string(killer.get(field), f"{context}.{field}")
        killer_status = require_string(killer.get("status"), f"{context}.status")
        if killer_status not in KILLER_STATUSES:
            raise DiscoveryValidationError(f"{context}.status is unknown")
        killer_statuses.append(killer_status)
        refs = validate_evidence_refs(
            killer.get("evidence_refs"),
            f"{context}.evidence_refs",
            known_evidence,
        )
        killer_ref_counts.append(len(refs))

    failure_reuse = require_list(card.get("failure_reuse"), f"{card_id}.failure_reuse")
    blocked_families: list[str] = []
    seen_families: set[str] = set()
    failure_fields = {
        "family_id",
        "disposition",
        "distinguishing_test_ref",
        "source_route_ids",
    }
    for index, raw_reuse in enumerate(failure_reuse):
        context = f"{card_id}.failure_reuse[{index}]"
        reuse = require_mapping(raw_reuse, context)
        require_exact_fields(reuse, failure_fields, context)
        family_id = require_id(reuse.get("family_id"), f"{context}.family_id")
        if family_id not in family_ids or family_id in seen_families:
            raise DiscoveryValidationError(f"{context}.family_id is unknown or duplicated")
        seen_families.add(family_id)
        disposition = require_string(reuse.get("disposition"), f"{context}.disposition")
        if disposition not in FAILURE_DISPOSITIONS:
            raise DiscoveryValidationError(f"{context}.disposition is unknown")
        if disposition == "blocked":
            blocked_families.append(family_id)
        test_ref = require_id(
            reuse.get("distinguishing_test_ref"), f"{context}.distinguishing_test_ref"
        )
        if test_ref not in killer_ids:
            raise DiscoveryValidationError(f"{context} references unknown killer test {test_ref}")
        source_routes = require_string_list(
            reuse.get("source_route_ids"), f"{context}.source_route_ids", allow_empty=False
        )
        unknown_routes = set(source_routes) - set(route_statuses)
        if unknown_routes:
            raise DiscoveryValidationError(f"{context} has unknown source routes: {sorted(unknown_routes)}")

    contracts = require_mapping(card.get("contracts"), f"{card_id}.contracts")
    simulators = require_list(contracts.get("simulators"), f"{card_id}.contracts.simulators")
    qualified_lineages: set[str] = set()
    simulator_fields = {
        "id",
        "lineage_group",
        "repository",
        "version",
        "license",
        "state_mapping",
        "intervention_mapping",
        "observable_mapping",
        "status",
    }
    for index, raw_simulator in enumerate(simulators):
        context = f"{card_id}.contracts.simulators[{index}]"
        simulator = require_mapping(raw_simulator, context)
        require_exact_fields(simulator, simulator_fields, context)
        require_id(simulator.get("id"), f"{context}.id")
        lineage = require_id(simulator.get("lineage_group"), f"{context}.lineage_group")
        repository = require_string(simulator.get("repository"), f"{context}.repository")
        if not repository.startswith("https://"):
            raise DiscoveryValidationError(f"{context}.repository must use HTTPS")
        for field in (
            "version",
            "license",
            "state_mapping",
            "intervention_mapping",
            "observable_mapping",
        ):
            require_string(simulator.get(field), f"{context}.{field}")
        simulator_status = require_string(simulator.get("status"), f"{context}.status")
        if simulator_status not in SIMULATOR_STATUSES:
            raise DiscoveryValidationError(f"{context}.status is unknown")
        if simulator_status == "qualified":
            if lineage in qualified_lineages:
                raise DiscoveryValidationError(f"qualified simulator lineage is duplicated: {lineage}")
            qualified_lineages.add(lineage)

    bridge = require_mapping(contracts.get("real_data_bridge"), f"{card_id}.contracts.real_data_bridge")
    bridge_fields = {
        "status",
        "source",
        "version",
        "observable_mapping",
        "intervention_mapping",
        "license",
        "stop_condition",
    }
    require_exact_fields(bridge, bridge_fields, f"{card_id}.contracts.real_data_bridge")
    bridge_status = require_string(bridge.get("status"), f"{card_id}.real_data_bridge.status")
    if bridge_status not in REAL_BRIDGE_STATUSES:
        raise DiscoveryValidationError(f"{card_id}.real_data_bridge.status is unknown")
    for field in bridge_fields - {"status"}:
        require_string(bridge.get(field), f"{card_id}.real_data_bridge.{field}")

    probabilities = require_mapping(card.get("probabilities"), f"{card_id}.probabilities")
    hostile = require_mapping(probabilities.get("hostile_t0"), f"{card_id}.probabilities.hostile_t0")
    hostile_lower, hostile_upper = validate_probability_range(
        hostile, f"{card_id}.probabilities.hostile_t0"
    )
    point = require_probability(hostile.get("point"), f"{card_id}.probabilities.hostile_t0.point")
    if not hostile_lower <= point <= hostile_upper:
        raise DiscoveryValidationError(f"{card_id} hostile T0 point is outside its interval")
    complete = require_mapping(
        probabilities.get("complete_by_venue"), f"{card_id}.probabilities.complete_by_venue"
    )
    if not complete:
        raise DiscoveryValidationError(f"{card_id} complete_by_venue must not be empty")
    for venue, interval in complete.items():
        require_string(venue, f"{card_id}.complete_by_venue key")
        validate_probability_range(interval, f"{card_id}.complete_by_venue.{venue}")

    contamination = require_mapping(card.get("contamination_control"), f"{card_id}.contamination_control")
    contamination_fields = {
        "exploration_sources",
        "confirmation_holdout",
        "multiplicity_control",
        "provenance",
        "status",
    }
    require_exact_fields(contamination, contamination_fields, f"{card_id}.contamination_control")
    for field in contamination_fields:
        require_string(contamination.get(field), f"{card_id}.contamination_control.{field}")

    evidence_uses = require_mapping(card.get("evidence_uses"), f"{card_id}.evidence_uses")
    evidence_use_fields = {
        "sandbox_motivation_refs",
        "d2_confirmation_refs",
        "paper_claim_refs",
    }
    require_exact_fields(evidence_uses, evidence_use_fields, f"{card_id}.evidence_uses")
    validate_evidence_refs(
        evidence_uses.get("sandbox_motivation_refs"),
        f"{card_id}.evidence_uses.sandbox_motivation_refs",
        known_evidence,
        allow_tainted=True,
        require_tainted=True,
    )
    validate_evidence_refs(
        evidence_uses.get("d2_confirmation_refs"),
        f"{card_id}.evidence_uses.d2_confirmation_refs",
        known_evidence,
    )
    validate_evidence_refs(
        evidence_uses.get("paper_claim_refs"),
        f"{card_id}.evidence_uses.paper_claim_refs",
        known_evidence,
    )

    authorization = require_mapping(card.get("authorization"), f"{card_id}.authorization")
    authorization_fields = {
        "authorized_actions",
        "forbidden_actions",
        "outcome_blind",
        "budget_boundary",
    }
    require_exact_fields(authorization, authorization_fields, f"{card_id}.authorization")
    authorized = require_string_list(
        authorization.get("authorized_actions"), f"{card_id}.authorization.authorized_actions"
    )
    forbidden = set(
        require_string_list(
            authorization.get("forbidden_actions"),
            f"{card_id}.authorization.forbidden_actions",
            allow_empty=False,
        )
    )
    require_bool(authorization.get("outcome_blind"), f"{card_id}.authorization.outcome_blind")
    require_string(authorization.get("budget_boundary"), f"{card_id}.authorization.budget_boundary")
    if status in {"candidate", "parked"}:
        disallowed = set(authorized) - OUTCOME_BLIND_ACTIONS
        if disallowed:
            raise DiscoveryValidationError(
                f"{status} card {card_id} authorizes non-outcome-blind actions: {sorted(disallowed)}"
            )
        missing_forbidden = forbidden_before_active - forbidden
        if missing_forbidden:
            raise DiscoveryValidationError(
                f"{status} card {card_id} lacks forbidden actions: {sorted(missing_forbidden)}"
            )

    if status == "active":
        if hostile_lower < activation_floor:
            raise DiscoveryValidationError(
                f"active card {card_id} hostile T0 lower bound is below {activation_floor}"
            )
        if killer_statuses != ["survived"] * len(killer_statuses):
            raise DiscoveryValidationError(f"active card {card_id} has a killer test not survived")
        if any(count == 0 for count in killer_ref_counts):
            raise DiscoveryValidationError(
                f"active card {card_id} has a survived killer without clean evidence"
            )
        if len(qualified_lineages) < 2:
            raise DiscoveryValidationError(f"active card {card_id} has fewer than two qualified lineages")
        if bridge_status != "qualified":
            raise DiscoveryValidationError(f"active card {card_id} lacks a qualified real-data bridge")
        if blocked_families:
            raise DiscoveryValidationError(
                f"active card {card_id} has blocked failure families: {sorted(blocked_families)}"
            )
        if contamination.get("status") != "frozen":
            raise DiscoveryValidationError(f"active card {card_id} contamination control is not frozen")
        if authorization.get("outcome_blind") is not True:
            raise DiscoveryValidationError(f"active card {card_id} decision was not outcome-blind")
        if not authorized:
            raise DiscoveryValidationError(f"active card {card_id} has no explicit authorization")

    if status in DECIDED_STATUSES:
        decision_raw = require_string(card.get("decision_ref"), f"{card_id}.decision_ref")
        decision_path = safe_repo_path(repo_root, decision_raw, f"{card_id}.decision_ref")
        decision = load_yaml(decision_path, f"decision for {card_id}")
        require_exact_fields(decision, DECISION_FIELDS, f"decision for {card_id}")
        require_schema_version_one(
            decision.get("schema_version"),
            f"decision for {card_id}.schema_version",
        )
        if decision.get("card_id") != card_id or decision.get("status") != status:
            raise DiscoveryValidationError(f"decision/card status mismatch for {card_id}")
        if decision.get("stage") != stage:
            raise DiscoveryValidationError(f"decision/card stage mismatch for {card_id}")
        require_date(decision.get("decided_at"), f"decision for {card_id}.decided_at")
        if require_bool(decision.get("outcome_accessed"), f"decision for {card_id}.outcome_accessed"):
            raise DiscoveryValidationError(f"D-minus-1 decision for {card_id} accessed outcomes")
        declared_hash = require_string(
            decision.get("card_sha256"), f"decision for {card_id}.card_sha256"
        )
        if SHA256_PATTERN.fullmatch(declared_hash) is None:
            raise DiscoveryValidationError(f"decision for {card_id} has invalid card_sha256")
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if declared_hash != actual_hash:
            raise DiscoveryValidationError(f"decision for {card_id} card_sha256 mismatch")
        kg_node_id = require_id(decision.get("kg_node_id"), f"decision for {card_id}.kg_node_id")
        if kg_node_id != card_id:
            raise DiscoveryValidationError(f"decision for {card_id} must use matching kg_node_id")
        expected_kg_status = KG_STATUS_MAP[status]
        if route_statuses.get(kg_node_id) != expected_kg_status:
            raise DiscoveryValidationError(f"card/KG status mismatch for {card_id}")
        require_string(decision.get("rationale"), f"decision for {card_id}.rationale")
        decision_authorized = require_string_list(
            decision.get("authorized_actions"), f"decision for {card_id}.authorized_actions"
        )
        decision_forbidden = require_string_list(
            decision.get("forbidden_actions"),
            f"decision for {card_id}.forbidden_actions",
            allow_empty=False,
        )
        if decision_authorized != authorized or set(decision_forbidden) != forbidden:
            raise DiscoveryValidationError(f"decision/card authorization mismatch for {card_id}")
        validate_evidence_refs(
            decision.get("evidence_refs"),
            f"decision for {card_id}.evidence_refs",
            known_evidence,
            allow_empty=False,
        )
        reopen = require_string_list(
            decision.get("reopen_conditions"), f"decision for {card_id}.reopen_conditions"
        )
        if status in {"parked", "failed_closed"} and not reopen:
            raise DiscoveryValidationError(f"decision for {card_id} needs reopen conditions")
    elif card.get("decision_ref") is not None:
        raise DiscoveryValidationError(f"screening card {card_id} cannot have a decision_ref")

    return card_id, status, primary_count


def read_partition_members(path: Path, expected_count: int, context: str) -> frozenset[str]:
    raw = path.read_bytes()
    if not raw or not raw.endswith(b"\n") or b"\r" in raw or b"\x00" in raw:
        raise DiscoveryValidationError(
            f"{context} must be nonempty UTF-8 with LF endings and a final newline"
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DiscoveryValidationError(f"{context} is not UTF-8") from exc
    members = text[:-1].split("\n")
    if any(not item or item != item.strip() for item in members):
        raise DiscoveryValidationError(f"{context} contains empty or padded unit ids")
    if members != sorted(members, key=lambda item: item.encode("utf-8")):
        raise DiscoveryValidationError(f"{context} unit ids must be bytewise sorted")
    if len(members) != len(set(members)):
        raise DiscoveryValidationError(f"{context} contains duplicate unit ids")
    if len(members) != expected_count:
        raise DiscoveryValidationError(
            f"{context} member count {len(members)} differs from {expected_count}"
        )
    return frozenset(members)


def validate_partition_v2(
    path: Path,
    repo_root: Path,
    schema: Mapping[str, object],
    sandbox_id: str,
    asset_fingerprint: str,
    expected_input_root: Path,
) -> tuple[str, frozenset[str], frozenset[str]]:
    partition = load_yaml(path, f"partition for {sandbox_id}")
    validate_json_instance(schema, partition, f"partition for {sandbox_id}")
    require_schema_version_one(
        partition.get("schema_version"),
        f"partition for {sandbox_id}.schema_version",
    )
    if partition.get("sandbox_id") != sandbox_id:
        raise DiscoveryValidationError(f"partition identity mismatch for {sandbox_id}")
    if partition.get("asset_fingerprint_sha256") != asset_fingerprint:
        raise DiscoveryValidationError(f"partition asset fingerprint mismatch for {sandbox_id}")
    namespace = require_string(
        partition.get("unit_namespace"),
        f"partition for {sandbox_id}.unit_namespace",
    )
    split_ids: set[str] = set()
    member_refs: set[str] = set()
    exploration: set[str] = set()
    confirmation: set[str] = set()
    exploration_count = 0
    confirmation_count = 0
    all_units: set[str] = set()
    for index, raw_split in enumerate(
        require_list(partition.get("splits"), f"partition for {sandbox_id}.splits")
    ):
        context = f"partition for {sandbox_id}.splits[{index}]"
        split = require_mapping(raw_split, context)
        split_id = require_id(split.get("id"), f"{context}.id")
        if split_id in split_ids:
            raise DiscoveryValidationError(f"duplicate split id in partition for {sandbox_id}")
        split_ids.add(split_id)
        role = require_string(split.get("role"), f"{context}.role")
        raw_ref = require_string(split.get("members_ref"), f"{context}.members_ref")
        if raw_ref in member_refs:
            raise DiscoveryValidationError(f"duplicate member ref in partition for {sandbox_id}")
        member_refs.add(raw_ref)
        member_path = safe_repo_path(repo_root, raw_ref, f"{context}.members_ref")
        try:
            member_path.relative_to(expected_input_root / "members")
        except ValueError as exc:
            raise DiscoveryValidationError(
                f"{context}.members_ref must live under sandbox_inputs/{sandbox_id}/members"
            ) from exc
        digest = require_sha256(split.get("members_sha256"), f"{context}.members_sha256")
        if hashlib.sha256(member_path.read_bytes()).hexdigest() != digest:
            raise DiscoveryValidationError(f"{context}.members_sha256 mismatch")
        count = require_positive_integer(split.get("member_count"), f"{context}.member_count")
        members = set(read_partition_members(member_path, count, context))
        overlap = all_units & members
        if overlap:
            raise DiscoveryValidationError(
                f"partition for {sandbox_id} has units in more than one split: {sorted(overlap)[:3]}"
            )
        all_units.update(members)
        if role == "exploration":
            exploration_count += 1
            exploration.update(members)
        elif role == "confirmation":
            confirmation_count += 1
            confirmation.update(members)
        else:
            raise DiscoveryValidationError(f"{context}.role is unknown")
    if exploration_count != 1 or confirmation_count < 1:
        raise DiscoveryValidationError(
            f"partition for {sandbox_id} needs exactly one exploration and at least one confirmation split"
        )
    return namespace, frozenset(exploration), frozenset(confirmation)


def validate_branch_request_v1(
    value: object,
    repo_root: Path,
    schema: Mapping[str, object],
    sandbox_id: str,
    branch_id: str,
    exploration_units: frozenset[str],
    artifact_root: Path,
    reservation: Mapping[str, int],
    context: str,
) -> Mapping[str, object]:
    _, request_path, _ = require_digest_ref(repo_root, value, f"{context}.request")
    branch_root = artifact_root / "branches" / branch_id
    expected_request = branch_root / "request.yaml"
    if request_path != expected_request:
        raise DiscoveryValidationError(f"{context}.request must use the canonical branch path")
    request = load_yaml(request_path, f"branch request for {sandbox_id}/{branch_id}")
    validate_json_instance(
        schema,
        request,
        f"branch request for {sandbox_id}/{branch_id}",
    )
    require_exact_fields(
        request,
        SANDBOX_BRANCH_REQUEST_FIELDS,
        f"branch request for {sandbox_id}/{branch_id}",
    )
    require_schema_version_one(
        request.get("schema_version"),
        f"branch request for {sandbox_id}/{branch_id}.schema_version",
    )
    if request.get("sandbox_id") != sandbox_id or request.get("branch_id") != branch_id:
        raise DiscoveryValidationError(f"branch request identity mismatch for {sandbox_id}/{branch_id}")
    require_id(
        request.get("hypothesis_id"),
        f"branch request for {sandbox_id}/{branch_id}.hypothesis_id",
    )
    for field in ("hypothesis", "falsifier"):
        require_string(
            request.get(field),
            f"branch request for {sandbox_id}/{branch_id}.{field}",
        )
    require_id(
        request.get("multiplicity_family_id"),
        f"branch request for {sandbox_id}/{branch_id}.multiplicity_family_id",
    )
    require_string_list(
        request.get("test_ids"),
        f"branch request for {sandbox_id}/{branch_id}.test_ids",
        allow_empty=False,
    )
    unit_ids = require_string_list(
        request.get("unit_ids"),
        f"branch request for {sandbox_id}/{branch_id}.unit_ids",
        allow_empty=False,
    )
    outside_exploration = set(unit_ids) - exploration_units
    if outside_exploration:
        raise DiscoveryValidationError(
            f"branch request for {sandbox_id}/{branch_id} uses non-exploration units: "
            f"{sorted(outside_exploration)[:3]}"
        )
    cpu_seconds = require_positive_integer(
        request.get("cpu_seconds"),
        f"branch request for {sandbox_id}/{branch_id}.cpu_seconds",
    )
    output_bytes = require_positive_integer(
        request.get("output_bytes"),
        f"branch request for {sandbox_id}/{branch_id}.output_bytes",
    )
    if cpu_seconds > reservation["cpu_seconds"]:
        raise DiscoveryValidationError("branch request CPU budget exceeds sandbox reservation")
    if output_bytes > reservation["storage_bytes"]:
        raise DiscoveryValidationError("branch request output budget exceeds sandbox reservation")
    for field, expected_name in (
        ("code_manifest", "code_manifest.json"),
        ("config", "config.yaml"),
    ):
        _, referenced_path, _ = require_digest_ref(
            repo_root,
            request.get(field),
            f"branch request for {sandbox_id}/{branch_id}.{field}",
        )
        if referenced_path != branch_root / expected_name:
            raise DiscoveryValidationError(
                f"branch request for {sandbox_id}/{branch_id}.{field} is not canonical"
            )
        if field == "config":
            config = load_yaml(referenced_path, f"branch config for {sandbox_id}/{branch_id}")
            config_units = require_string_list(
                config.get("unit_ids"),
                f"branch config for {sandbox_id}/{branch_id}.unit_ids",
                allow_empty=False,
            )
            if config_units != unit_ids:
                raise DiscoveryValidationError(
                    f"branch config/request unit mismatch for {sandbox_id}/{branch_id}"
                )
    return request


def load_canonical_event_log(path: Path, context: str) -> list[Mapping[str, object]]:
    raw = path.read_bytes()
    if not raw or not raw.endswith(b"\n") or b"\r" in raw:
        raise DiscoveryValidationError(f"{context} must be nonempty canonical JSONL with LF endings")
    entries: list[Mapping[str, object]] = []
    previous_digest: str | None = None
    for index, raw_line in enumerate(raw.splitlines()):
        line_context = f"{context}[{index}]"
        try:
            loaded = cast(object, json.loads(raw_line.decode("utf-8")))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DiscoveryValidationError(f"{line_context} is not UTF-8 JSON") from exc
        entry = require_mapping(loaded, line_context)
        if canonical_json_bytes(entry) != raw_line:
            raise DiscoveryValidationError(f"{line_context} is not canonical compact JSON")
        require_schema_version_one(entry.get("schema_version"), f"{line_context}.schema_version")
        sequence = entry.get("seq")
        if type(sequence) is not int or sequence != index:
            raise DiscoveryValidationError(f"{line_context}.seq must equal {index}")
        declared_previous = entry.get("previous_entry_sha256")
        if index == 0:
            if declared_previous is not None:
                raise DiscoveryValidationError(f"{line_context}.previous_entry_sha256 must be null")
        elif declared_previous != previous_digest:
            raise DiscoveryValidationError(f"{line_context}.previous_entry_sha256 breaks the chain")
        declared_digest = require_sha256(entry.get("entry_sha256"), f"{line_context}.entry_sha256")
        actual_digest = sha256_mapping_without(entry, "entry_sha256")
        if declared_digest != actual_digest:
            raise DiscoveryValidationError(f"{line_context}.entry_sha256 mismatch")
        previous_digest = declared_digest
        entries.append(entry)
    return entries


def require_artifact_digest(
    repo_root: Path,
    value: object,
    context: str,
    artifact_root: Path,
    *,
    require_bytes: bool,
) -> tuple[str, Path, str, int | None]:
    artifact = require_mapping(value, context)
    fields = {"ref", "sha256", "bytes"} if require_bytes else {"ref", "sha256"}
    require_exact_fields(artifact, fields, context)
    raw_ref = require_string(artifact.get("ref"), f"{context}.ref")
    path = safe_repo_path(repo_root, raw_ref, f"{context}.ref")
    try:
        path.relative_to(artifact_root)
    except ValueError as exc:
        raise DiscoveryValidationError(f"{context}.ref must live under artifact_root") from exc
    digest = require_sha256(artifact.get("sha256"), f"{context}.sha256")
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise DiscoveryValidationError(f"{context}.sha256 mismatch")
    size: int | None = None
    if require_bytes:
        size = require_nonnegative_integer(artifact.get("bytes"), f"{context}.bytes")
        if path.stat().st_size != size:
            raise DiscoveryValidationError(f"{context}.bytes mismatch")
    return raw_ref, path, digest, size


def validate_receipt_v2(
    path: Path,
    sandbox_id: str,
    branch_id: str,
    context: str,
    execution_contract: SandboxExecutionContract,
) -> tuple[dict[str, int], datetime, datetime, str]:
    try:
        raw = path.read_bytes()
        receipt_obj = cast(object, json.loads(raw.decode("utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        raise DiscoveryValidationError(f"cannot load {context}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise DiscoveryValidationError(f"cannot load {context}: not UTF-8") from exc
    receipt = require_mapping(receipt_obj, context)
    if canonical_json_bytes(receipt) != raw:
        raise DiscoveryValidationError(f"{context} must be canonical compact JSON")
    expected = {
        "schema_version",
        "sandbox_id",
        "branch_id",
        "started_at",
        "finished_at",
        "cpu_seconds",
        "storage_bytes",
        "monetary_cost_usd_micros",
        "gpu_seconds",
        "run_status",
        "container_exit_code",
        "wall_seconds",
        "executor",
        "launcher_sha256",
        "incident_handler_sha256",
        "image_digest",
        "network",
        "root_filesystem",
        "repository_tree_mount",
        "input_channel",
        "confirmation_materialization",
        "output_channel",
        "secrets",
        "device_access",
    }
    require_exact_fields(receipt, expected, context)
    require_schema_version_one(receipt.get("schema_version"), f"{context}.schema_version")
    if receipt.get("sandbox_id") != sandbox_id or receipt.get("branch_id") != branch_id:
        raise DiscoveryValidationError(f"{context} identity mismatch")
    expected_execution = {
        "executor": execution_contract.executor,
        "launcher_sha256": execution_contract.launcher_sha256,
        "incident_handler_sha256": execution_contract.incident_handler_sha256,
        "image_digest": execution_contract.image_digest,
        "network": execution_contract.network,
        "root_filesystem": execution_contract.root_filesystem,
        "repository_tree_mount": execution_contract.repository_tree_mount,
        "input_channel": execution_contract.input_channel,
        "confirmation_materialization": execution_contract.confirmation_materialization,
        "output_channel": execution_contract.output_channel,
        "secrets": execution_contract.secrets,
        "device_access": execution_contract.device_access,
    }
    for field, expected_value in expected_execution.items():
        if receipt.get(field) != expected_value:
            raise DiscoveryValidationError(f"{context}.{field} differs from execution contract")
    run_status = require_string(receipt.get("run_status"), f"{context}.run_status")
    if run_status not in {"completed", "container_failed", "timeout", "output_limit"}:
        raise DiscoveryValidationError(f"{context}.run_status is invalid")
    exit_code = receipt.get("container_exit_code")
    if exit_code is not None and type(exit_code) is not int:
        raise DiscoveryValidationError(f"{context}.container_exit_code must be integer or null")
    if run_status == "completed" and exit_code != 0:
        raise DiscoveryValidationError(f"{context} completed without a zero exit code")
    wall_seconds = require_nonnegative_integer(
        receipt.get("wall_seconds"), f"{context}.wall_seconds"
    )
    started = require_utc_timestamp(receipt.get("started_at"), f"{context}.started_at")
    finished = require_utc_timestamp(receipt.get("finished_at"), f"{context}.finished_at")
    if finished < started:
        raise DiscoveryValidationError(f"{context}.finished_at precedes started_at")
    usage = {
        "cpu_seconds": require_nonnegative_integer(
            receipt.get("cpu_seconds"), f"{context}.cpu_seconds"
        ),
        "storage_bytes": require_nonnegative_integer(
            receipt.get("storage_bytes"), f"{context}.storage_bytes"
        ),
        "monetary_cost_usd_micros": require_nonnegative_integer(
            receipt.get("monetary_cost_usd_micros"),
            f"{context}.monetary_cost_usd_micros",
        ),
        "gpu_seconds": require_nonnegative_integer(
            receipt.get("gpu_seconds"), f"{context}.gpu_seconds"
        ),
    }
    if usage["monetary_cost_usd_micros"] != 0 or usage["gpu_seconds"] != 0:
        raise DiscoveryValidationError(f"{context} reports forbidden monetary or GPU use")
    if usage["cpu_seconds"] != wall_seconds:
        raise DiscoveryValidationError(f"{context}.cpu_seconds must equal charged one-CPU wall time")
    timestamp_elapsed = max(0, math.ceil((finished - started).total_seconds()))
    if abs(timestamp_elapsed - wall_seconds) > 1:
        raise DiscoveryValidationError(f"{context}.wall_seconds disagrees with receipt timestamps")
    return usage, started, finished, run_status


def tree_file_bytes(path: Path, context: str) -> int:
    if not path.is_dir() or path.is_symlink():
        raise DiscoveryValidationError(f"{context} must be a real directory")
    total = 0
    for child in path.rglob("*"):
        if child.is_symlink():
            raise DiscoveryValidationError(f"{context} cannot contain symlinks")
        if child.is_file():
            total += child.stat().st_size
        elif not child.is_dir():
            raise DiscoveryValidationError(f"{context} contains a non-file entry")
    return total


def run_git_bytes(repo_root: Path, args: list[str], context: str) -> bytes:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        raise DiscoveryValidationError(f"cannot run git for {context}: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise DiscoveryValidationError(f"git failed for {context}: {detail}")
    return completed.stdout


def git_tree_files(repo_root: Path, base_ref: str, prefix: str) -> list[str]:
    raw = run_git_bytes(
        repo_root,
        ["ls-tree", "-r", "--name-only", "-z", base_ref, "--", prefix],
        f"protected tree {base_ref}:{prefix}",
    )
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DiscoveryValidationError(
            f"protected tree {base_ref}:{prefix} contains a non-UTF-8 path"
        ) from exc
    return [path for path in decoded.split("\0") if path]


def git_file_bytes(repo_root: Path, base_ref: str, relative_path: str) -> bytes:
    return run_git_bytes(
        repo_root,
        ["show", f"{base_ref}:{relative_path}"],
        f"protected file {base_ref}:{relative_path}",
    )


def yaml_mapping_from_bytes(raw: bytes, context: str) -> Mapping[str, object]:
    try:
        loaded = cast(object, yaml.safe_load(raw.decode("utf-8")))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        raise DiscoveryValidationError(f"cannot parse {context}: {exc}") from exc
    return require_mapping(loaded, context)


def validate_protected_sandbox_history(repo_root: Path, base_ref: str) -> str:
    require_string(base_ref, "protected base ref")
    run_git_bytes(
        repo_root,
        ["rev-parse", "--verify", f"{base_ref}^{{commit}}"],
        f"protected base revision {base_ref}",
    )
    sandbox_prefix = "research/discovery/sandboxes"
    base_manifest_paths = git_tree_files(repo_root, base_ref, sandbox_prefix)
    base_sandbox_ids: set[str] = set()
    expected_parent = PurePosixPath(sandbox_prefix)
    for relative_path in base_manifest_paths:
        parsed = PurePosixPath(relative_path)
        if parsed.parent != expected_parent or parsed.suffix != ".yaml":
            continue
        base_sandbox_ids.add(parsed.stem)

    current_sandbox_dir = repo_root / sandbox_prefix
    current_sandbox_ids = {
        path.stem for path in current_sandbox_dir.glob("*.yaml") if path.is_file()
    }
    removed = base_sandbox_ids - current_sandbox_ids
    if removed:
        raise DiscoveryValidationError(
            f"protected base sandboxes were deleted: {sorted(removed)}"
        )

    for sandbox_id in sorted(base_sandbox_ids):
        manifest_ref = f"{sandbox_prefix}/{sandbox_id}.yaml"
        decision_ref = f"research/discovery/sandbox_decisions/{sandbox_id}.yaml"
        ledger_ref = f"research/discovery/sandbox_artifacts/{sandbox_id}/events.jsonl"
        exact_refs = [manifest_ref, decision_ref]
        exact_refs.extend(
            git_tree_files(
                repo_root,
                base_ref,
                f"research/discovery/sandbox_inputs/{sandbox_id}",
            )
        )
        exact_refs.extend(
            path
            for path in git_tree_files(
                repo_root,
                base_ref,
                f"research/discovery/sandbox_artifacts/{sandbox_id}",
            )
            if path != ledger_ref
        )
        for relative_path in exact_refs:
            current_path = repo_root / relative_path
            if current_path.is_symlink() or not current_path.is_file():
                raise DiscoveryValidationError(
                    f"protected sandbox file was removed or replaced: {relative_path}"
                )
            if current_path.read_bytes() != git_file_bytes(repo_root, base_ref, relative_path):
                raise DiscoveryValidationError(
                    f"protected sandbox file was rewritten: {relative_path}"
                )

        current_ledger = repo_root / ledger_ref
        if current_ledger.is_symlink() or not current_ledger.is_file():
            raise DiscoveryValidationError(f"protected sandbox ledger is missing: {ledger_ref}")
        base_ledger = git_file_bytes(repo_root, base_ref, ledger_ref)
        if not current_ledger.read_bytes().startswith(base_ledger):
            raise DiscoveryValidationError(
                f"sandbox ledger no longer has the protected base as an exact byte prefix: {sandbox_id}"
            )

    current_taint_entries = load_sandbox_taint_registry(repo_root)
    taint_ref = "research/discovery/sandbox_taint_registry.yaml"
    base_discovery_files = set(git_tree_files(repo_root, base_ref, "research/discovery"))
    if taint_ref in base_discovery_files:
        base_taint = yaml_mapping_from_bytes(
            git_file_bytes(repo_root, base_ref, taint_ref),
            f"protected taint registry {base_ref}",
        )
        require_schema_version_one(
            base_taint.get("schema_version"),
            f"protected taint registry {base_ref}.schema_version",
        )
        base_taint_entries = require_list(
            base_taint.get("sandbox_results"),
            f"protected taint registry {base_ref}.sandbox_results",
        )
        if current_taint_entries[: len(base_taint_entries)] != base_taint_entries:
            raise DiscoveryValidationError(
                "sandbox taint registry does not preserve the protected entry prefix"
            )

    forecast_ref = "research/discovery/forecast_ledger.yaml"
    forecast_history_status = "introduced after protected base"
    if forecast_ref in base_discovery_files:
        base_forecast = yaml_mapping_from_bytes(
            git_file_bytes(repo_root, base_ref, forecast_ref),
            f"protected forecast ledger {base_ref}",
        )
        current_forecast = load_yaml(repo_root / forecast_ref, "current forecast ledger")
        for field in ("schema_version", "floor_review_target_id"):
            if current_forecast.get(field) != base_forecast.get(field):
                raise DiscoveryValidationError(
                    f"forecast ledger rewrote protected field {field}"
                )
        for field in ("target_definitions", "forecasts", "resolutions"):
            base_entries = require_list(
                base_forecast.get(field),
                f"protected forecast ledger {base_ref}.{field}",
            )
            current_entries = require_list(
                current_forecast.get(field),
                f"current forecast ledger.{field}",
            )
            if current_entries[: len(base_entries)] != base_entries:
                raise DiscoveryValidationError(
                    f"forecast ledger does not preserve the protected {field} prefix"
                )
        forecast_history_status = "prefixes preserved"

    search_ref = "research/discovery/search_cycle_ledger.yaml"
    search_history_status = "introduced after protected base"
    if search_ref in base_discovery_files:
        base_search = yaml_mapping_from_bytes(
            git_file_bytes(repo_root, base_ref, search_ref),
            f"protected search-cycle ledger {base_ref}",
        )
        current_search = load_yaml(repo_root / search_ref, "current search-cycle ledger")
        for field in ("schema_version", "policy_id", "scope_start_cycle", "historical_baseline"):
            if current_search.get(field) != base_search.get(field):
                raise DiscoveryValidationError(
                    f"search-cycle ledger rewrote protected field {field}"
                )
        base_cycles = require_list(
            base_search.get("cycles"),
            f"protected search-cycle ledger {base_ref}.cycles",
        )
        current_cycles = require_list(
            current_search.get("cycles"),
            "current search-cycle ledger.cycles",
        )
        if current_cycles[: len(base_cycles)] != base_cycles:
            raise DiscoveryValidationError(
                "search-cycle ledger does not preserve the protected cycles prefix"
            )
        search_history_status = "prefix preserved"

    trigger_ref = "research/discovery/reentry_trigger_ledger.yaml"
    trigger_history_status = "introduced after protected base"
    if trigger_ref in base_discovery_files:
        base_trigger = yaml_mapping_from_bytes(
            git_file_bytes(repo_root, base_ref, trigger_ref),
            f"protected re-entry trigger ledger {base_ref}",
        )
        current_trigger = load_yaml(repo_root / trigger_ref, "current re-entry trigger ledger")
        for field in ("schema_version", "policy_id"):
            if current_trigger.get(field) != base_trigger.get(field):
                raise DiscoveryValidationError(
                    f"re-entry trigger ledger rewrote protected field {field}"
                )
        base_trigger_entries = require_list(
            base_trigger.get("entries"),
            f"protected re-entry trigger ledger {base_ref}.entries",
        )
        current_trigger_entries = require_list(
            current_trigger.get("entries"),
            "current re-entry trigger ledger.entries",
        )
        if current_trigger_entries[: len(base_trigger_entries)] != base_trigger_entries:
            raise DiscoveryValidationError(
                "re-entry trigger ledger does not preserve the protected entries prefix"
            )
        trigger_history_status = "prefix preserved"

    new_sandbox_ids = current_sandbox_ids - base_sandbox_ids
    tainted_sandbox_ids = {
        require_id(entry.get("sandbox_id"), "sandbox taint registry sandbox_id")
        for entry in current_taint_entries
    }
    for sandbox_id in sorted(new_sandbox_ids):
        ledger_path = (
            repo_root
            / "research"
            / "discovery"
            / "sandbox_artifacts"
            / sandbox_id
            / "events.jsonl"
        )
        entries = load_canonical_event_log(
            ledger_path,
            f"new-sandbox authorization ledger for {sandbox_id}",
        )
        if len(entries) != 1 or entries[0].get("event_type") != "authorized":
            raise DiscoveryValidationError(
                f"new sandbox {sandbox_id} must be committed as authorization-only before execution"
            )
        artifact_root = ledger_path.parent
        artifact_files = {
            path.relative_to(artifact_root).as_posix()
            for path in artifact_root.rglob("*")
            if path.is_file()
        }
        if artifact_files != {"events.jsonl"}:
            raise DiscoveryValidationError(
                f"new sandbox {sandbox_id} contains execution artifacts in its authorization change"
            )
        if sandbox_id in tainted_sandbox_ids:
            raise DiscoveryValidationError(
                f"new sandbox {sandbox_id} cannot have a terminal result in its authorization change"
            )

    return (
        f"Protected sandbox history OK against {base_ref}: "
        f"{len(base_sandbox_ids)} inherited, {len(new_sandbox_ids)} authorization-only new; "
        f"forecast ledger {forecast_history_status}; "
        f"search-cycle ledger {search_history_status}; "
        f"re-entry trigger ledger {trigger_history_status}"
    )


def validate_sandbox_v2(
    path: Path,
    repo_root: Path,
    sandbox_schema: Mapping[str, object],
    partition_schema: Mapping[str, object],
    decision_schema: Mapping[str, object],
    result_schema: Mapping[str, object],
    branch_request_schema: Mapping[str, object],
    runtime_incident_schema: Mapping[str, object],
    route_ids: set[str],
    clean_evidence_ids: set[str],
    policy: Mapping[str, object],
    as_of: datetime,
) -> SandboxRecord:
    context = f"exploration sandbox {path.name}"
    sandbox = load_yaml(path, context)
    validate_json_instance(sandbox_schema, sandbox, context)
    if sandbox.get("schema_version") != 2 or type(sandbox.get("schema_version")) is not int:
        raise DiscoveryValidationError(f"{context}.schema_version must be integer 2")
    require_exact_fields(sandbox, SANDBOX_FIELDS, context)
    sandbox_id = require_id(sandbox.get("id"), f"{context}.id")
    if path.stem != sandbox_id:
        raise DiscoveryValidationError(f"sandbox filename must equal id: {sandbox_id}")
    campaign_id = require_id(sandbox.get("campaign_id"), f"{sandbox_id}.campaign_id")
    created_at = require_utc_timestamp(sandbox.get("created_at"), f"{sandbox_id}.created_at")
    expires_at = require_utc_timestamp(sandbox.get("expires_at"), f"{sandbox_id}.expires_at")
    if not created_at < expires_at:
        raise DiscoveryValidationError(f"{sandbox_id}.expires_at must follow created_at")
    if (expires_at - created_at).total_seconds() > SANDBOX_HARD_MAX_TTL_SECONDS:
        raise DiscoveryValidationError(f"{sandbox_id} exceeds the seven-day sandbox TTL")
    if as_of.tzinfo is None or as_of.utcoffset() != timedelta(0):
        raise DiscoveryValidationError("sandbox validation as_of must be timezone-aware UTC")
    require_string(sandbox.get("purpose"), f"{sandbox_id}.purpose")
    parent_ids = require_string_list(
        sandbox.get("parent_route_ids"),
        f"{sandbox_id}.parent_route_ids",
        allow_empty=False,
    )
    unknown_parents = set(parent_ids) - route_ids
    if unknown_parents:
        raise DiscoveryValidationError(
            f"{sandbox_id} has unknown parent routes: {sorted(unknown_parents)}"
        )

    raw_input_root = repo_root / "research" / "discovery" / "sandbox_inputs" / sandbox_id
    raw_artifact_root = repo_root / "research" / "discovery" / "sandbox_artifacts" / sandbox_id
    if raw_input_root.is_symlink() or raw_artifact_root.is_symlink():
        raise DiscoveryValidationError(f"{sandbox_id} sandbox roots cannot be symlinks")
    input_root = raw_input_root.resolve()
    artifact_root = raw_artifact_root.resolve()
    asset = require_mapping(sandbox.get("asset"), f"{sandbox_id}.asset")
    asset_key = require_id(asset.get("key"), f"{sandbox_id}.asset.key")
    kind = require_string(asset.get("kind"), f"{sandbox_id}.asset.kind")
    source = require_string(asset.get("source"), f"{sandbox_id}.asset.source")
    version = require_string(asset.get("version"), f"{sandbox_id}.asset.version")
    require_string(asset.get("license"), f"{sandbox_id}.asset.license")
    asset_fingerprint = require_sha256(
        asset.get("fingerprint_sha256"), f"{sandbox_id}.asset.fingerprint_sha256"
    )
    for field in ("state_or_observation_coverage", "intervention_or_search_space"):
        require_string(asset.get(field), f"{sandbox_id}.asset.{field}")
    evidence_refs = require_string_list(
        asset.get("evidence_refs"),
        f"{sandbox_id}.asset.evidence_refs",
        allow_empty=False,
    )
    unknown_or_tainted = set(evidence_refs) - clean_evidence_ids
    if unknown_or_tainted:
        raise DiscoveryValidationError(
            f"{sandbox_id}.asset has unknown or tainted evidence refs: {sorted(unknown_or_tainted)}"
        )
    for field in ("provenance", "snapshot_manifest"):
        _, referenced_path, _ = require_digest_ref(
            repo_root,
            asset.get(field),
            f"{sandbox_id}.asset.{field}",
        )
        try:
            referenced_path.relative_to(input_root)
        except ValueError as exc:
            raise DiscoveryValidationError(
                f"{sandbox_id}.asset.{field}.ref must live under sandbox_inputs/{sandbox_id}"
            ) from exc
    snapshot = require_mapping(asset.get("snapshot_manifest"), f"{sandbox_id}.asset.snapshot_manifest")
    snapshot_sha = require_sha256(
        snapshot.get("sha256"), f"{sandbox_id}.asset.snapshot_manifest.sha256"
    )
    fingerprint_payload: Mapping[str, object] = {
        "asset_key": asset_key,
        "kind": kind,
        "snapshot_sha256": snapshot_sha,
        "source": source,
        "version": version,
    }
    expected_fingerprint = hashlib.sha256(canonical_json_bytes(fingerprint_payload)).hexdigest()
    if asset_fingerprint != expected_fingerprint:
        raise DiscoveryValidationError(f"{sandbox_id}.asset.fingerprint_sha256 mismatch")

    _, partition_path, partition_sha = require_digest_ref(
        repo_root,
        sandbox.get("partition"),
        f"{sandbox_id}.partition",
    )
    try:
        partition_path.relative_to(input_root)
    except ValueError as exc:
        raise DiscoveryValidationError(
            f"{sandbox_id}.partition.ref must live under sandbox_inputs/{sandbox_id}"
        ) from exc
    namespace, exploration_units, confirmation_units = validate_partition_v2(
        partition_path,
        repo_root,
        partition_schema,
        sandbox_id,
        asset_fingerprint,
        input_root,
    )

    confirmation_contract = require_mapping(
        sandbox.get("confirmation_contract"), f"{sandbox_id}.confirmation_contract"
    )
    require_exact_fields(
        confirmation_contract,
        SANDBOX_CONFIRMATION_FIELDS,
        f"{sandbox_id}.confirmation_contract",
    )
    confirmation_mode = require_string(
        confirmation_contract.get("mode"), f"{sandbox_id}.confirmation_contract.mode"
    )
    if kind == "synthetic_simulator":
        if confirmation_mode != "future_public_randomness":
            raise DiscoveryValidationError(
                f"{sandbox_id} synthetic confirmation must use future public randomness"
            )
        _, derivation_path, _ = require_digest_ref(
            repo_root,
            confirmation_contract.get("derivation"),
            f"{sandbox_id}.confirmation_contract.derivation",
        )
        try:
            derivation_path.relative_to(input_root)
        except ValueError as exc:
            raise DiscoveryValidationError(
                f"{sandbox_id}.confirmation_contract.derivation must live under sandbox inputs"
            ) from exc
    elif confirmation_mode != "preexisting_unmounted":
        raise DiscoveryValidationError(
            f"{sandbox_id} nonsynthetic confirmation must be preexisting and unmounted"
        )
    elif confirmation_contract.get("derivation") is not None:
        raise DiscoveryValidationError(
            f"{sandbox_id}.confirmation_contract.derivation must be null for existing data"
        )
    if require_bool(
        confirmation_contract.get("outcomes_materialized"),
        f"{sandbox_id}.confirmation_contract.outcomes_materialized",
    ):
        raise DiscoveryValidationError(
            f"{sandbox_id} confirmation outcomes cannot be materialized at authorization"
        )
    if confirmation_contract.get("release_condition") != "after_sandbox_terminal_and_d0_freeze":
        raise DiscoveryValidationError(
            f"{sandbox_id}.confirmation_contract.release_condition is invalid"
        )
    require_string(
        confirmation_contract.get("controller"),
        f"{sandbox_id}.confirmation_contract.controller",
    )

    reservation_raw = require_mapping(sandbox.get("reservation"), f"{sandbox_id}.reservation")
    reservation_limits = {
        "cpu_seconds": SANDBOX_HARD_MAX_CPU_SECONDS,
        "storage_bytes": SANDBOX_HARD_MAX_STORAGE_BYTES,
        "monetary_cost_usd_micros": SANDBOX_HARD_MAX_MONETARY_COST_USD_MICROS,
        "gpu_seconds": SANDBOX_HARD_MAX_GPU_SECONDS,
        "branches": SANDBOX_HARD_MAX_BRANCHES,
    }
    reservation: dict[str, int] = {}
    for field, limit in reservation_limits.items():
        value = require_nonnegative_integer(
            reservation_raw.get(field), f"{sandbox_id}.reservation.{field}"
        )
        if field in {"cpu_seconds", "storage_bytes", "branches"} and value == 0:
            raise DiscoveryValidationError(f"{sandbox_id}.reservation.{field} must be positive")
        if value > limit:
            raise DiscoveryValidationError(
                f"{sandbox_id}.reservation.{field} exceeds hard limit {limit}"
            )
        reservation[field] = value

    authorization = require_mapping(
        sandbox.get("authorization"), f"{sandbox_id}.authorization"
    )
    allowed_actions = set(
        require_string_list(
            authorization.get("allowed_actions"),
            f"{sandbox_id}.authorization.allowed_actions",
            allow_empty=False,
        )
    )
    if not allowed_actions <= SANDBOX_ACTIONS:
        raise DiscoveryValidationError(f"{sandbox_id} authorizes an unknown sandbox action")
    forbidden_actions = set(
        require_string_list(
            authorization.get("forbidden_actions"),
            f"{sandbox_id}.authorization.forbidden_actions",
            allow_empty=False,
        )
    )
    if not forbidden_actions.issuperset(SANDBOX_REQUIRED_FORBIDDEN_ACTIONS):
        raise DiscoveryValidationError(f"{sandbox_id} omits required forbidden actions")
    protocol_allowed = set(
        require_string_list(policy.get("allowed_actions"), "protocol.sandbox.allowed_actions")
    )
    if not allowed_actions <= protocol_allowed:
        raise DiscoveryValidationError(f"{sandbox_id} exceeds protocol allowed actions")

    execution_raw = require_mapping(
        sandbox.get("execution_contract"), f"{sandbox_id}.execution_contract"
    )
    require_exact_fields(
        execution_raw,
        SANDBOX_EXECUTION_FIELDS,
        f"{sandbox_id}.execution_contract",
    )
    executor = require_string(
        execution_raw.get("executor"), f"{sandbox_id}.execution_contract.executor"
    )
    if executor != "oci_container":
        raise DiscoveryValidationError(f"{sandbox_id} must use the OCI sandbox executor")
    # A terminal sandbox's execution contract is historical: once its ledger
    # records a state transition, the pinned bytes only need to stay auditable
    # in git history, not byte-present in the live working tree.
    terminal_ledger = sandbox_ledger_is_terminal(artifact_root)
    _, _, launcher_sha256 = require_digest_ref(
        repo_root,
        execution_raw.get("launcher"),
        f"{sandbox_id}.execution_contract.launcher",
        allow_committed_match=terminal_ledger,
    )
    _, _, incident_handler_sha256 = require_digest_ref(
        repo_root,
        execution_raw.get("incident_handler"),
        f"{sandbox_id}.execution_contract.incident_handler",
        allow_committed_match=terminal_ledger,
    )
    image_digest = require_oci_image_digest(
        execution_raw.get("image_digest"),
        f"{sandbox_id}.execution_contract.image_digest",
    )
    required_execution_values = {
        "network": "none",
        "root_filesystem": "read_only",
        "repository_tree_mount": "none",
        "input_channel": "read_only_config_with_enumerated_units_only",
        "confirmation_materialization": "not_generated_not_staged_not_mounted",
        "output_channel": "bounded_stdout_tar",
        "secrets": "none",
        "device_access": "cpu_only",
    }
    execution_values: dict[str, str] = {}
    for field, expected in required_execution_values.items():
        declared_value = require_string(
            execution_raw.get(field), f"{sandbox_id}.execution_contract.{field}"
        )
        if declared_value != expected:
            raise DiscoveryValidationError(
                f"{sandbox_id}.execution_contract.{field} must equal {expected}"
            )
        execution_values[field] = declared_value
    execution_contract = SandboxExecutionContract(
        executor=executor,
        launcher_sha256=launcher_sha256,
        incident_handler_sha256=incident_handler_sha256,
        image_digest=image_digest,
        network=execution_values["network"],
        root_filesystem=execution_values["root_filesystem"],
        repository_tree_mount=execution_values["repository_tree_mount"],
        input_channel=execution_values["input_channel"],
        confirmation_materialization=execution_values["confirmation_materialization"],
        output_channel=execution_values["output_channel"],
        secrets=execution_values["secrets"],
        device_access=execution_values["device_access"],
    )

    integrity = require_mapping(sandbox.get("integrity"), f"{sandbox_id}.integrity")
    ledger_ref = require_string(integrity.get("ledger_ref"), f"{sandbox_id}.integrity.ledger_ref")
    ledger_path = safe_repo_path(repo_root, ledger_ref, f"{sandbox_id}.integrity.ledger_ref")
    expected_ledger = artifact_root / "events.jsonl"
    if ledger_path != expected_ledger:
        raise DiscoveryValidationError(
            f"{sandbox_id}.integrity.ledger_ref must be sandbox_artifacts/{sandbox_id}/events.jsonl"
        )
    if integrity.get("stop_rule") != "first_of_budget_expiry_forbidden_access_or_manual_close":
        raise DiscoveryValidationError(f"{sandbox_id}.integrity.stop_rule is invalid")
    if integrity.get("result_disposition") != "child_card_d_minus_3_only":
        raise DiscoveryValidationError(f"{sandbox_id}.integrity.result_disposition is invalid")

    decision_ref = require_string(sandbox.get("decision_ref"), f"{sandbox_id}.decision_ref")
    decision_path = safe_repo_path(repo_root, decision_ref, f"{sandbox_id}.decision_ref")
    expected_decision = (
        repo_root / "research" / "discovery" / "sandbox_decisions" / f"{sandbox_id}.yaml"
    ).resolve()
    if decision_path != expected_decision:
        raise DiscoveryValidationError(f"{sandbox_id}.decision_ref is not canonical")
    decision = load_yaml(decision_path, f"sandbox decision for {sandbox_id}")
    validate_json_instance(decision_schema, decision, f"sandbox decision for {sandbox_id}")
    require_exact_fields(
        decision,
        SANDBOX_DECISION_FIELDS,
        f"sandbox decision for {sandbox_id}",
    )
    if decision.get("sandbox_id") != sandbox_id or decision.get("decision") != "authorized":
        raise DiscoveryValidationError(f"sandbox decision identity mismatch for {sandbox_id}")
    manifest_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if decision.get("manifest_sha256") != manifest_sha:
        raise DiscoveryValidationError(f"sandbox decision for {sandbox_id} manifest hash mismatch")
    decided_at = require_utc_timestamp(
        decision.get("decided_at"), f"sandbox decision for {sandbox_id}.decided_at"
    )
    if not created_at <= decided_at < expires_at:
        raise DiscoveryValidationError(f"sandbox decision time lies outside {sandbox_id} window")
    require_string(decision.get("authorized_by"), f"sandbox decision for {sandbox_id}.authorized_by")
    require_string(decision.get("rationale"), f"sandbox decision for {sandbox_id}.rationale")

    entries = load_canonical_event_log(ledger_path, f"event ledger for {sandbox_id}")
    first = entries[0]
    authorized_fields = {
        "schema_version",
        "seq",
        "event_type",
        "occurred_at",
        "manifest_sha256",
        "previous_entry_sha256",
        "entry_sha256",
    }
    require_exact_fields(first, authorized_fields, f"event ledger for {sandbox_id}[0]")
    if first.get("event_type") != "authorized" or first.get("manifest_sha256") != manifest_sha:
        raise DiscoveryValidationError(f"event ledger for {sandbox_id} lacks a valid genesis")
    first_time = require_utc_timestamp(
        first.get("occurred_at"), f"event ledger for {sandbox_id}[0].occurred_at"
    )
    if first_time != decided_at:
        raise DiscoveryValidationError("event ledger genesis time differs from decision time")
    if first_time > as_of:
        raise DiscoveryValidationError(f"event ledger genesis for {sandbox_id} is in the future")
    if decision.get("genesis_entry_sha256") != first.get("entry_sha256"):
        raise DiscoveryValidationError(f"sandbox decision for {sandbox_id} genesis hash mismatch")

    opened: dict[str, datetime] = {}
    branch_budgets: dict[str, tuple[int, int]] = {}
    finished: set[str] = set()
    quarantined: set[str] = set()
    usage = {
        "cpu_seconds": 0,
        "storage_bytes": 0,
        "monetary_cost_usd_micros": 0,
        "gpu_seconds": 0,
    }
    terminal_state: str | None = None
    result_ref: str | None = None
    result_sha: str | None = None
    previous_time = first_time
    for index, entry in enumerate(entries[1:], start=1):
        entry_context = f"event ledger for {sandbox_id}[{index}]"
        if terminal_state is not None:
            raise DiscoveryValidationError(f"{entry_context} appears after a terminal transition")
        event_type = require_string(entry.get("event_type"), f"{entry_context}.event_type")
        occurred_at = require_utc_timestamp(entry.get("occurred_at"), f"{entry_context}.occurred_at")
        if occurred_at < previous_time:
            raise DiscoveryValidationError(f"{entry_context}.occurred_at is not monotone")
        if occurred_at > as_of:
            raise DiscoveryValidationError(f"{entry_context}.occurred_at is in the future")
        previous_time = occurred_at
        common = {
            "schema_version",
            "seq",
            "event_type",
            "occurred_at",
            "previous_entry_sha256",
            "entry_sha256",
        }
        if event_type == "branch_opened":
            request_entry_fields = SANDBOX_BRANCH_REQUEST_FIELDS - {"schema_version", "sandbox_id"}
            optional_launcher_fields = {"launcher_base_ref", "launcher_base_commit"} & set(entry)
            fields = common | request_entry_fields | {"request"} | optional_launcher_fields
            require_exact_fields(entry, fields, entry_context)
            if "launcher_base_ref" in entry:
                require_string(
                    entry.get("launcher_base_ref"), f"{entry_context}.launcher_base_ref"
                )
            if "launcher_base_commit" in entry:
                launcher_base_commit = require_string(
                    entry.get("launcher_base_commit"),
                    f"{entry_context}.launcher_base_commit",
                )
                if not (
                    len(launcher_base_commit) in {40, 64}
                    and all(c in "0123456789abcdef" for c in launcher_base_commit)
                ):
                    raise DiscoveryValidationError(
                        f"{entry_context}.launcher_base_commit is not a git commit id"
                    )
            if occurred_at >= expires_at:
                raise DiscoveryValidationError(f"{entry_context} opened at or after expiry")
            branch_id = require_id(entry.get("branch_id"), f"{entry_context}.branch_id")
            if branch_id in opened:
                raise DiscoveryValidationError(f"duplicate branch id in {sandbox_id}: {branch_id}")
            request = validate_branch_request_v1(
                entry.get("request"),
                repo_root,
                branch_request_schema,
                sandbox_id,
                branch_id,
                exploration_units,
                artifact_root,
                reservation,
                entry_context,
            )
            for field in request_entry_fields:
                if entry.get(field) != request.get(field):
                    raise DiscoveryValidationError(
                        f"{entry_context}.{field} differs from the frozen branch request"
                    )
            branch_budgets[branch_id] = (
                require_positive_integer(request.get("cpu_seconds"), f"{entry_context}.cpu_seconds"),
                require_positive_integer(request.get("output_bytes"), f"{entry_context}.output_bytes"),
            )
            opened[branch_id] = occurred_at
        elif event_type == "branch_finished":
            fields = common | {"branch_id", "receipt", "artifacts"}
            require_exact_fields(entry, fields, entry_context)
            if occurred_at >= expires_at:
                raise DiscoveryValidationError(f"{entry_context} finished at or after expiry")
            branch_id = require_id(entry.get("branch_id"), f"{entry_context}.branch_id")
            if branch_id not in opened or branch_id in finished or branch_id in quarantined:
                raise DiscoveryValidationError(f"{entry_context} references an unopened or finished branch")
            receipt_ref, receipt_path, _, _ = require_artifact_digest(
                repo_root,
                entry.get("receipt"),
                f"{entry_context}.receipt",
                artifact_root,
                require_bytes=False,
            )
            if not receipt_ref.endswith("/receipt.json"):
                raise DiscoveryValidationError(f"{entry_context}.receipt must end in receipt.json")
            branch_root = artifact_root / "branches" / branch_id
            if receipt_path != branch_root / "receipt.json":
                raise DiscoveryValidationError(
                    f"{entry_context}.receipt must use the canonical branch path"
                )
            receipt_usage, receipt_started, receipt_finished, run_status = validate_receipt_v2(
                receipt_path,
                sandbox_id,
                branch_id,
                f"receipt for {sandbox_id}/{branch_id}",
                execution_contract,
            )
            branch_cpu_limit, branch_output_limit = branch_budgets[branch_id]
            if receipt_usage["cpu_seconds"] > branch_cpu_limit:
                raise DiscoveryValidationError(
                    f"receipt for {sandbox_id}/{branch_id} exceeds its branch CPU budget"
                )
            if receipt_usage["storage_bytes"] > branch_output_limit + SANDBOX_STDERR_LIMIT_BYTES:
                raise DiscoveryValidationError(
                    f"receipt for {sandbox_id}/{branch_id} exceeds its branch output budget"
                )
            if receipt_started < opened[branch_id] or receipt_finished > occurred_at:
                raise DiscoveryValidationError(
                    f"receipt for {sandbox_id}/{branch_id} lies outside its branch event window"
                )
            for field, value in receipt_usage.items():
                usage[field] += value
            artifact_storage = 0
            artifact_names: set[str] = set()
            artifact_sizes: dict[str, int] = {}
            for artifact_index, artifact in enumerate(
                require_list(entry.get("artifacts"), f"{entry_context}.artifacts")
            ):
                _, artifact_path, _, artifact_bytes = require_artifact_digest(
                    repo_root,
                    artifact,
                    f"{entry_context}.artifacts[{artifact_index}]",
                    artifact_root,
                    require_bytes=True,
                )
                if artifact_path.parent != branch_root:
                    raise DiscoveryValidationError(
                        f"{entry_context}.artifacts[{artifact_index}] is outside its branch root"
                    )
                if artifact_path.name in artifact_names:
                    raise DiscoveryValidationError(f"{entry_context}.artifacts contains duplicates")
                artifact_names.add(artifact_path.name)
                size = cast(int, artifact_bytes)
                artifact_sizes[artifact_path.name] = size
                artifact_storage += size
            allowed_names = (
                {"bundle.tar", "stderr.log"}
                if run_status == "completed"
                else {"bundle.tar.partial", "stderr.log"}
            )
            if not artifact_names <= allowed_names:
                raise DiscoveryValidationError(
                    f"{entry_context}.artifacts do not match run_status {run_status}"
                )
            if run_status == "completed" and "bundle.tar" not in artifact_names:
                raise DiscoveryValidationError(f"{entry_context} completed without bundle.tar")
            bundle_name = "bundle.tar" if run_status == "completed" else "bundle.tar.partial"
            if artifact_sizes.get(bundle_name, 0) > branch_output_limit:
                raise DiscoveryValidationError(
                    f"receipt for {sandbox_id}/{branch_id} exceeds its stdout bundle budget"
                )
            if artifact_sizes.get("stderr.log", 0) > SANDBOX_STDERR_LIMIT_BYTES:
                raise DiscoveryValidationError(
                    f"receipt for {sandbox_id}/{branch_id} exceeds its stderr budget"
                )
            if receipt_usage["storage_bytes"] != artifact_storage:
                raise DiscoveryValidationError(
                    f"receipt for {sandbox_id}/{branch_id}.storage_bytes differs from artifacts"
                )
            finished.add(branch_id)
        elif event_type == "branch_quarantined":
            fields = common | {"branch_id", "incident", "charged_usage"}
            require_exact_fields(entry, fields, entry_context)
            branch_id = require_id(entry.get("branch_id"), f"{entry_context}.branch_id")
            if branch_id not in opened or branch_id in finished or branch_id in quarantined:
                raise DiscoveryValidationError(
                    f"{entry_context} references an unopened or already resolved branch"
                )
            branch_root = artifact_root / "branches" / branch_id
            _, incident_path, _, _ = require_artifact_digest(
                repo_root,
                entry.get("incident"),
                f"{entry_context}.incident",
                artifact_root,
                require_bytes=False,
            )
            if incident_path != branch_root / "runtime_incident.json":
                raise DiscoveryValidationError(
                    f"{entry_context}.incident must use the canonical branch path"
                )
            incident = load_canonical_json_mapping(
                incident_path,
                f"runtime incident for {sandbox_id}/{branch_id}",
            )
            validate_json_instance(
                runtime_incident_schema,
                incident,
                f"runtime incident for {sandbox_id}/{branch_id}",
            )
            if incident.get("sandbox_id") != sandbox_id or incident.get("branch_id") != branch_id:
                raise DiscoveryValidationError(
                    f"runtime incident identity mismatch for {sandbox_id}/{branch_id}"
                )
            if require_utc_timestamp(
                incident.get("recorded_at"),
                f"runtime incident for {sandbox_id}/{branch_id}.recorded_at",
            ) != occurred_at:
                raise DiscoveryValidationError(
                    f"runtime incident time mismatch for {sandbox_id}/{branch_id}"
                )
            require_string(
                incident.get("reason"),
                f"runtime incident for {sandbox_id}/{branch_id}.reason",
            )
            require_string(
                incident.get("operator"),
                f"runtime incident for {sandbox_id}/{branch_id}.operator",
            )
            charged = require_mapping(entry.get("charged_usage"), f"{entry_context}.charged_usage")
            incident_charged = require_mapping(
                incident.get("charged_usage"),
                f"runtime incident for {sandbox_id}/{branch_id}.charged_usage",
            )
            charged_fields = {
                "cpu_seconds",
                "storage_bytes",
                "monetary_cost_usd_micros",
                "gpu_seconds",
            }
            require_exact_fields(charged, charged_fields, f"{entry_context}.charged_usage")
            require_exact_fields(
                incident_charged,
                charged_fields,
                f"runtime incident for {sandbox_id}/{branch_id}.charged_usage",
            )
            if dict(charged) != dict(incident_charged):
                raise DiscoveryValidationError(
                    f"{entry_context}.charged_usage differs from the incident report"
                )
            branch_cpu_limit, branch_output_limit = branch_budgets[branch_id]
            expected_charge = {
                "cpu_seconds": branch_cpu_limit,
                "storage_bytes": branch_output_limit + SANDBOX_STDERR_LIMIT_BYTES,
                "monetary_cost_usd_micros": 0,
                "gpu_seconds": 0,
            }
            if dict(charged) != expected_charge:
                raise DiscoveryValidationError(
                    f"{entry_context}.charged_usage must reserve the full ambiguous branch budget"
                )
            for field, value in expected_charge.items():
                usage[field] += value
            quarantined.add(branch_id)
        elif event_type == "state_transition":
            fields = common | {"from_state", "to_state", "reason", "result"}
            require_exact_fields(entry, fields, entry_context)
            if entry.get("from_state") != "authorized":
                raise DiscoveryValidationError(f"{entry_context}.from_state must be authorized")
            to_state = require_string(entry.get("to_state"), f"{entry_context}.to_state")
            if to_state not in {"closed", "exhausted", "quarantined"}:
                raise DiscoveryValidationError(f"{entry_context}.to_state is invalid")
            resolved_branches = finished | quarantined
            if set(opened) != resolved_branches:
                raise DiscoveryValidationError(f"{entry_context} has unfinished branches")
            if quarantined and to_state != "quarantined":
                raise DiscoveryValidationError(
                    f"{entry_context} must quarantine a sandbox with an ambiguous branch"
                )
            if to_state == "quarantined" and not quarantined:
                raise DiscoveryValidationError(
                    f"{entry_context} cannot quarantine without a branch incident"
                )
            require_string(entry.get("reason"), f"{entry_context}.reason")
            result_ref, result_path, result_sha, _ = require_artifact_digest(
                repo_root,
                entry.get("result"),
                f"{entry_context}.result",
                artifact_root,
                require_bytes=False,
            )
            expected_result = artifact_root / "result.yaml"
            if result_path != expected_result:
                raise DiscoveryValidationError(f"{entry_context}.result must be result.yaml")
            result = load_yaml(result_path, f"sandbox result for {sandbox_id}")
            validate_json_instance(result_schema, result, f"sandbox result for {sandbox_id}")
            if result.get("sandbox_id") != sandbox_id or result.get("campaign_id") != campaign_id:
                raise DiscoveryValidationError(f"sandbox result identity mismatch for {sandbox_id}")
            if result.get("manifest_sha256") != manifest_sha:
                raise DiscoveryValidationError(f"sandbox result manifest hash mismatch for {sandbox_id}")
            if result.get("partition_sha256") != partition_sha:
                raise DiscoveryValidationError(f"sandbox result partition hash mismatch for {sandbox_id}")
            if to_state == "quarantined" and result.get("outcome_status") != "quarantined":
                raise DiscoveryValidationError(
                    f"quarantined sandbox result status mismatch for {sandbox_id}"
                )
            if to_state != "quarantined" and result.get("outcome_status") == "quarantined":
                raise DiscoveryValidationError(
                    f"non-quarantined sandbox has a quarantined result for {sandbox_id}"
                )
            if require_utc_timestamp(
                result.get("created_at"), f"sandbox result for {sandbox_id}.created_at"
            ) != occurred_at:
                raise DiscoveryValidationError(f"sandbox result time mismatch for {sandbox_id}")
            if result.get("ledger_head_before_terminal_sha256") != entry.get(
                "previous_entry_sha256"
            ):
                raise DiscoveryValidationError(f"sandbox result ledger head mismatch for {sandbox_id}")
            result_branches = require_string_list(
                result.get("branch_ids"), f"sandbox result for {sandbox_id}.branch_ids"
            )
            if set(result_branches) != resolved_branches:
                raise DiscoveryValidationError(f"sandbox result branch ids mismatch for {sandbox_id}")
            result_usage = require_mapping(
                result.get("usage"), f"sandbox result for {sandbox_id}.usage"
            )
            for field in usage:
                if require_nonnegative_integer(
                    result_usage.get(field), f"sandbox result for {sandbox_id}.usage.{field}"
                ) != usage[field]:
                    raise DiscoveryValidationError(
                        f"sandbox result usage mismatch for {sandbox_id}: {field}"
                    )
            if require_nonnegative_integer(
                result_usage.get("branches"), f"sandbox result for {sandbox_id}.usage.branches"
            ) != len(resolved_branches):
                raise DiscoveryValidationError(f"sandbox result branch count mismatch for {sandbox_id}")
            for artifact_index, artifact in enumerate(
                require_list(result.get("artifacts"), f"sandbox result for {sandbox_id}.artifacts")
            ):
                require_artifact_digest(
                    repo_root,
                    artifact,
                    f"sandbox result for {sandbox_id}.artifacts[{artifact_index}]",
                    artifact_root,
                    require_bytes=True,
                )
            terminal_state = to_state
        else:
            raise DiscoveryValidationError(f"{entry_context}.event_type is unknown")

    usage_with_branches = {**usage, "branches": len(opened)}
    for field, actual_usage in usage_with_branches.items():
        if actual_usage > reservation[field]:
            raise DiscoveryValidationError(f"{sandbox_id} actual {field} exceeds reservation")
    if terminal_state is None:
        if as_of < decided_at:
            raise DiscoveryValidationError(f"{sandbox_id} authorization is in the future")
        if as_of >= expires_at:
            raise DiscoveryValidationError(
                f"expired sandbox {sandbox_id} lacks a terminal result and taint disposition"
            )
        effective_state = "authorized"
    else:
        effective_state = terminal_state
    measured_storage = tree_file_bytes(input_root, f"sandbox input tree for {sandbox_id}")
    measured_storage += tree_file_bytes(artifact_root, f"sandbox artifact tree for {sandbox_id}")
    if measured_storage > reservation["storage_bytes"]:
        raise DiscoveryValidationError(
            f"{sandbox_id} measured storage exceeds its reservation"
        )
    if effective_state not in SANDBOX_EFFECTIVE_STATES:
        raise DiscoveryValidationError(f"{sandbox_id} has an invalid effective state")
    return SandboxRecord(
        sandbox_id=sandbox_id,
        campaign_id=campaign_id,
        parent_route_ids=frozenset(parent_ids),
        asset_fingerprint=asset_fingerprint,
        unit_namespace=namespace,
        exploration_units=exploration_units,
        confirmation_units=confirmation_units,
        reservation=reservation,
        effective_state=effective_state,
        manifest_sha256=manifest_sha,
        partition_sha256=partition_sha,
        artifact_root=artifact_root,
        result_ref=result_ref,
        result_sha256=result_sha,
    )


def validate_sandbox_collection(records: list[SandboxRecord]) -> None:
    asset_campaign: dict[str, str] = {}
    campaign_asset: dict[str, str] = {}
    live_assets: set[str] = set()
    campaign_reservations: dict[str, dict[str, int]] = {}
    exposures: dict[tuple[str, str], tuple[str, str]] = {}
    limits = {
        "cpu_seconds": SANDBOX_HARD_MAX_CPU_SECONDS,
        "storage_bytes": SANDBOX_HARD_MAX_STORAGE_BYTES,
        "monetary_cost_usd_micros": SANDBOX_HARD_MAX_MONETARY_COST_USD_MICROS,
        "gpu_seconds": SANDBOX_HARD_MAX_GPU_SECONDS,
        "branches": SANDBOX_HARD_MAX_BRANCHES,
    }
    for record in records:
        prior_campaign = asset_campaign.setdefault(record.asset_fingerprint, record.campaign_id)
        if prior_campaign != record.campaign_id:
            raise DiscoveryValidationError(
                f"asset {record.asset_fingerprint} appears in more than one sandbox campaign"
            )
        prior_asset = campaign_asset.setdefault(record.campaign_id, record.asset_fingerprint)
        if prior_asset != record.asset_fingerprint:
            raise DiscoveryValidationError(
                f"sandbox campaign {record.campaign_id} contains more than one asset"
            )
        if record.effective_state == "authorized":
            if record.asset_fingerprint in live_assets:
                raise DiscoveryValidationError(
                    f"asset {record.asset_fingerprint} has more than one live sandbox"
                )
            live_assets.add(record.asset_fingerprint)

        totals = campaign_reservations.setdefault(
            record.campaign_id,
            {field: 0 for field in limits},
        )
        for field, limit in limits.items():
            totals[field] += record.reservation[field]
            if totals[field] > limit:
                raise DiscoveryValidationError(
                    f"sandbox campaign {record.campaign_id} exceeds cumulative {field} limit"
                )

        for role, units in (
            ("exploration", record.exploration_units),
            ("confirmation", record.confirmation_units),
        ):
            for unit in units:
                key = (record.unit_namespace, unit)
                prior = exposures.get(key)
                if prior is None:
                    exposures[key] = (record.campaign_id, role)
                    continue
                prior_campaign_id, prior_role = prior
                if prior_campaign_id != record.campaign_id:
                    raise DiscoveryValidationError(
                        f"unit {record.unit_namespace}:{unit} appears across sandbox campaigns"
                    )
                if prior_role != role:
                    raise DiscoveryValidationError(
                        f"unit {record.unit_namespace}:{unit} changes exploration/confirmation role"
                    )


def materialize_tainted_evidence(
    raw_entries: list[Mapping[str, object]],
    records: list[SandboxRecord],
    clean_evidence: Mapping[str, EvidenceMeta],
) -> dict[str, EvidenceMeta]:
    by_sandbox = {record.sandbox_id: record for record in records}
    tainted: dict[str, EvidenceMeta] = {}
    registered_sandboxes: set[str] = set()
    for index, entry in enumerate(raw_entries):
        context = f"sandbox taint registry.sandbox_results[{index}]"
        evidence_id = require_id(entry.get("id"), f"{context}.id")
        sandbox_id = require_id(entry.get("sandbox_id"), f"{context}.sandbox_id")
        if evidence_id != f"{sandbox_id}_result":
            raise DiscoveryValidationError(
                f"{context}.id must be the canonical <sandbox_id>_result id"
            )
        if evidence_id in clean_evidence or evidence_id in tainted:
            raise DiscoveryValidationError(f"evidence id collision: {evidence_id}")
        record = by_sandbox.get(sandbox_id)
        if record is None:
            raise DiscoveryValidationError(f"{context} references unknown sandbox {sandbox_id}")
        if record.effective_state not in {"closed", "exhausted", "quarantined"}:
            raise DiscoveryValidationError(f"{context} references a nonterminal sandbox")
        artifact_ref = require_string(entry.get("artifact_ref"), f"{context}.artifact_ref")
        artifact_sha = require_sha256(entry.get("artifact_sha256"), f"{context}.artifact_sha256")
        if artifact_ref != record.result_ref or artifact_sha != record.result_sha256:
            raise DiscoveryValidationError(f"{context} does not match the terminal sandbox result")
        registered_sandboxes.add(sandbox_id)
        tainted[evidence_id] = EvidenceMeta(
            epistemic_class="sandbox_exploratory_tainted",
            sandbox_id=sandbox_id,
            artifact_ref=artifact_ref,
            artifact_sha256=artifact_sha,
        )

    terminal_sandboxes = {
        record.sandbox_id
        for record in records
        if record.effective_state in {"closed", "exhausted", "quarantined"}
    }
    missing = terminal_sandboxes - registered_sandboxes
    if missing:
        raise DiscoveryValidationError(
            f"terminal sandboxes lack taint-registry results: {sorted(missing)}"
        )
    return tainted


def validate_discovery(
    repo_root: Path,
    *,
    as_of: datetime | None = None,
    base_ref: str | None = None,
) -> str:
    current_time = datetime.now(UTC) if as_of is None else as_of
    (
        _,
        activation_floor,
        minimum_primary,
        forbidden,
        sandbox_policy,
        forecast_ledger_ref,
        _,
        search_cycle_ledger_ref,
        reentry_trigger_ledger_ref,
    ) = load_protocol(repo_root)
    search_cycle_count, search_question_count, search_card_count = validate_search_cycle_ledger(
        repo_root,
        search_cycle_ledger_ref,
    )
    route_statuses, route_locator_ids, route_failure_codes = load_route_registry(repo_root)
    external_evidence = load_evidence_registry(repo_root)
    route_evidence = {
        locator_id: EvidenceMeta(epistemic_class="clean_route_locator")
        for locator_id in route_locator_ids
    }
    collisions = set(external_evidence) & set(route_evidence)
    if collisions:
        raise DiscoveryValidationError(
            f"evidence registry ids collide with route locators: {sorted(collisions)}"
    )
    clean_evidence = {**external_evidence, **route_evidence}
    family_ids = load_failure_families(repo_root, set(route_statuses))
    trigger_count, qualified_trigger_count = validate_reentry_trigger_ledger(
        repo_root,
        reentry_trigger_ledger_ref,
        set(route_statuses),
        route_failure_codes,
        family_ids,
        clean_evidence,
    )
    forecast_count, resolution_count, floor_resolution_count = validate_forecast_ledger(
        repo_root,
        forecast_ledger_ref,
        route_statuses,
        clean_evidence,
        activation_floor,
    )

    discovery_root = repo_root / "research" / "discovery"
    card_schema = load_json_schema(
        discovery_root / "topic_card.schema.json",
        "topic card JSON schema",
    )
    sandbox_schema = load_json_schema(
        discovery_root / "exploration_sandbox.schema.json",
        "exploration sandbox JSON schema",
    )
    partition_schema = load_json_schema(
        discovery_root / "exploration_partition.schema.json",
        "exploration partition JSON schema",
    )
    sandbox_decision_schema = load_json_schema(
        discovery_root / "exploration_sandbox_decision.schema.json",
        "exploration sandbox decision JSON schema",
    )
    sandbox_result_schema = load_json_schema(
        discovery_root / "exploration_sandbox_result.schema.json",
        "exploration sandbox result JSON schema",
    )
    branch_request_schema = load_json_schema(
        discovery_root / "exploration_branch_request.schema.json",
        "exploration branch request JSON schema",
    )
    runtime_incident_schema = load_json_schema(
        discovery_root / "exploration_runtime_incident.schema.json",
        "exploration runtime incident JSON schema",
    )

    sandbox_paths = sorted((discovery_root / "sandboxes").glob("*.yaml"))
    sandbox_records: list[SandboxRecord] = []
    sandbox_ids: set[str] = set()
    sandbox_status_counts: dict[str, int] = {}
    for path in sandbox_paths:
        record = validate_sandbox_v2(
            path,
            repo_root,
            sandbox_schema,
            partition_schema,
            sandbox_decision_schema,
            sandbox_result_schema,
            branch_request_schema,
            runtime_incident_schema,
            set(route_statuses),
            set(clean_evidence),
            sandbox_policy,
            current_time,
        )
        if record.sandbox_id in sandbox_ids:
            raise DiscoveryValidationError(f"duplicate sandbox id: {record.sandbox_id}")
        sandbox_ids.add(record.sandbox_id)
        sandbox_records.append(record)
        sandbox_status_counts[record.effective_state] = (
            sandbox_status_counts.get(record.effective_state, 0) + 1
        )
    validate_sandbox_collection(sandbox_records)
    tainted_evidence = materialize_tainted_evidence(
        load_sandbox_taint_registry(repo_root),
        sandbox_records,
        clean_evidence,
    )
    known_evidence = {**clean_evidence, **tainted_evidence}
    transition_statuses, transition_count = load_decision_history(repo_root, clean_evidence)

    cards_dir = discovery_root / "cards"
    card_paths = sorted(cards_dir.glob("*.yaml"))
    if not card_paths:
        raise DiscoveryValidationError("no discovery topic cards found")
    card_ids: set[str] = set()
    status_counts: dict[str, int] = {}
    primary_total = 0
    for path in card_paths:
        card_id, status, primary_count = validate_card(
            path,
            repo_root,
            card_schema,
            route_statuses,
            known_evidence,
            family_ids,
            activation_floor,
            minimum_primary,
            forbidden,
        )
        if card_id in card_ids:
            raise DiscoveryValidationError(f"duplicate card id: {card_id}")
        card_ids.add(card_id)
        status_counts[status] = status_counts.get(status, 0) + 1
        primary_total += primary_count

    unknown_transition_cards = set(transition_statuses) - card_ids
    if unknown_transition_cards:
        raise DiscoveryValidationError(
            f"decision history has unknown cards: {sorted(unknown_transition_cards)}"
        )
    for card_id, status in transition_statuses.items():
        card_path = cards_dir / f"{card_id}.yaml"
        current = require_string(
            load_yaml(card_path, f"topic card {card_id}").get("status"),
            f"topic card {card_id}.status",
        )
        if current != status:
            raise DiscoveryValidationError(
                f"decision history/card status mismatch for {card_id}: {status} != {current}"
            )

    counts = ", ".join(f"{status}={count}" for status, count in sorted(status_counts.items()))
    sandbox_counts = ", ".join(
        f"{status}={count}" for status, count in sorted(sandbox_status_counts.items())
    )
    sandbox_summary = sandbox_counts if sandbox_counts else "none"
    summary = (
        "Discovery governance OK: "
        f"{len(card_ids)} cards ({counts}), {len(external_evidence)} evidence records, "
        f"{len(tainted_evidence)} sandbox-tainted results, "
        f"{len(family_ids)} failure families, {primary_total} primary-work assignments, "
        f"{transition_count} status transitions, {len(sandbox_ids)} exploration sandboxes "
        f"({sandbox_summary}), {forecast_count} prospective forecasts "
        f"({resolution_count} resolved; {floor_resolution_count} T0-floor resolutions), "
        f"{trigger_count} re-entry trigger audits ({qualified_trigger_count} qualified), "
        f"{search_cycle_count} prospective search cycles "
        f"({search_question_count} raw questions; {search_card_count} cards)"
    )
    if base_ref is not None:
        history_summary = validate_protected_sandbox_history(repo_root, base_ref)
        summary = f"{summary}\n{history_summary}"
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate EcoMD research-discovery governance")
    parser.add_argument(
        "--base-ref",
        help="Git revision whose sandbox records must remain an immutable prefix",
    )
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    try:
        print(validate_discovery(repo_root, base_ref=args.base_ref))
    except DiscoveryValidationError as exc:
        print(f"Discovery governance INVALID: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
