#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
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
SANDBOX_EFFECTIVE_STATES = {"authorized", "expired", "exhausted", "closed"}
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
    "image_digest",
    "network",
    "root_filesystem",
    "repository_mount",
    "exploration_mount",
    "confirmation_materialization",
    "output_mount",
    "secrets",
    "device_access",
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
    image_digest: str
    network: str
    root_filesystem: str
    repository_mount: str
    exploration_mount: str
    confirmation_materialization: str
    output_mount: str
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


def require_digest_ref(
    repo_root: Path,
    value: object,
    context: str,
) -> tuple[str, Path, str]:
    mapping = require_mapping(value, context)
    require_exact_fields(mapping, {"ref", "sha256"}, context)
    raw_ref = require_string(mapping.get("ref"), f"{context}.ref")
    path = safe_repo_path(repo_root, raw_ref, f"{context}.ref")
    digest = require_sha256(mapping.get("sha256"), f"{context}.sha256")
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise DiscoveryValidationError(f"{context}.sha256 mismatch")
    return raw_ref, path, digest


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


def load_route_registry(repo_root: Path) -> tuple[dict[str, str], set[str]]:
    path = repo_root / ".claude" / "memory" / "research_route_knowledge_graph.yaml"
    root = load_yaml(path, "route graph")
    statuses: dict[str, str] = {}
    locator_ids: set[str] = set()
    for index, raw_node in enumerate(require_list(root.get("nodes"), "route graph.nodes")):
        node = require_mapping(raw_node, f"route graph.nodes[{index}]")
        node_id = require_id(node.get("id"), f"route graph.nodes[{index}].id")
        status = require_string(node.get("status"), f"route graph.nodes[{index}].status")
        statuses[node_id] = status
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
    return statuses, locator_ids


def load_protocol(
    repo_root: Path,
) -> tuple[Mapping[str, object], float, int, set[str], Mapping[str, object]]:
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
        "require_confirmation_unmaterialized",
    ):
        if require_bool(sandbox.get(field), f"protocol.sandbox.{field}") is not True:
            raise DiscoveryValidationError(f"protocol sandbox {field} must be true")
    for field in ("scientific_claims_allowed", "route_activation_allowed"):
        if require_bool(sandbox.get(field), f"protocol.sandbox.{field}") is not False:
            raise DiscoveryValidationError(f"protocol sandbox {field} must be false")
    return protocol, floor, minimum_primary, forbidden, sandbox


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
) -> tuple[dict[str, int], datetime, datetime]:
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
        "executor",
        "launcher_sha256",
        "image_digest",
        "network",
        "root_filesystem",
        "repository_mount",
        "exploration_mount",
        "confirmation_materialization",
        "output_mount",
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
        "image_digest": execution_contract.image_digest,
        "network": execution_contract.network,
        "root_filesystem": execution_contract.root_filesystem,
        "repository_mount": execution_contract.repository_mount,
        "exploration_mount": execution_contract.exploration_mount,
        "confirmation_materialization": execution_contract.confirmation_materialization,
        "output_mount": execution_contract.output_mount,
        "secrets": execution_contract.secrets,
        "device_access": execution_contract.device_access,
    }
    for field, expected_value in expected_execution.items():
        if receipt.get(field) != expected_value:
            raise DiscoveryValidationError(f"{context}.{field} differs from execution contract")
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
    return usage, started, finished


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
        f"{len(base_sandbox_ids)} inherited, {len(new_sandbox_ids)} authorization-only new"
    )


def validate_sandbox_v2(
    path: Path,
    repo_root: Path,
    sandbox_schema: Mapping[str, object],
    partition_schema: Mapping[str, object],
    decision_schema: Mapping[str, object],
    result_schema: Mapping[str, object],
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
    _, _, launcher_sha256 = require_digest_ref(
        repo_root,
        execution_raw.get("launcher"),
        f"{sandbox_id}.execution_contract.launcher",
    )
    image_digest = require_oci_image_digest(
        execution_raw.get("image_digest"),
        f"{sandbox_id}.execution_contract.image_digest",
    )
    required_execution_values = {
        "network": "none",
        "root_filesystem": "read_only",
        "repository_mount": "none",
        "exploration_mount": "read_only_enumerated_units_only",
        "confirmation_materialization": "not_generated_not_staged_not_mounted",
        "output_mount": "sandbox_artifact_root_only",
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
        image_digest=image_digest,
        network=execution_values["network"],
        root_filesystem=execution_values["root_filesystem"],
        repository_mount=execution_values["repository_mount"],
        exploration_mount=execution_values["exploration_mount"],
        confirmation_materialization=execution_values["confirmation_materialization"],
        output_mount=execution_values["output_mount"],
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
    finished: set[str] = set()
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
            fields = common | {
                "branch_id",
                "hypothesis_id",
                "hypothesis",
                "falsifier",
                "multiplicity_family_id",
                "test_ids",
                "seed_ids",
                "code_manifest",
                "config",
            }
            require_exact_fields(entry, fields, entry_context)
            if occurred_at >= expires_at:
                raise DiscoveryValidationError(f"{entry_context} opened at or after expiry")
            branch_id = require_id(entry.get("branch_id"), f"{entry_context}.branch_id")
            if branch_id in opened:
                raise DiscoveryValidationError(f"duplicate branch id in {sandbox_id}: {branch_id}")
            opened[branch_id] = occurred_at
            require_id(entry.get("hypothesis_id"), f"{entry_context}.hypothesis_id")
            for field in ("hypothesis", "falsifier"):
                require_string(entry.get(field), f"{entry_context}.{field}")
            require_id(
                entry.get("multiplicity_family_id"),
                f"{entry_context}.multiplicity_family_id",
            )
            require_string_list(entry.get("test_ids"), f"{entry_context}.test_ids", allow_empty=False)
            seed_values = require_list(entry.get("seed_ids"), f"{entry_context}.seed_ids")
            seeds = [
                require_nonnegative_integer(seed, f"{entry_context}.seed_ids[{seed_index}]")
                for seed_index, seed in enumerate(seed_values)
            ]
            if not seeds or len(seeds) != len(set(seeds)):
                raise DiscoveryValidationError(f"{entry_context}.seed_ids must be nonempty and unique")
            require_digest_ref(repo_root, entry.get("code_manifest"), f"{entry_context}.code_manifest")
            require_digest_ref(repo_root, entry.get("config"), f"{entry_context}.config")
        elif event_type == "branch_finished":
            fields = common | {"branch_id", "receipt", "artifacts"}
            require_exact_fields(entry, fields, entry_context)
            if occurred_at >= expires_at:
                raise DiscoveryValidationError(f"{entry_context} finished at or after expiry")
            branch_id = require_id(entry.get("branch_id"), f"{entry_context}.branch_id")
            if branch_id not in opened or branch_id in finished:
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
            receipt_usage, receipt_started, receipt_finished = validate_receipt_v2(
                receipt_path,
                sandbox_id,
                branch_id,
                f"receipt for {sandbox_id}/{branch_id}",
                execution_contract,
            )
            if receipt_started < opened[branch_id] or receipt_finished > occurred_at:
                raise DiscoveryValidationError(
                    f"receipt for {sandbox_id}/{branch_id} lies outside its branch event window"
                )
            for field, value in receipt_usage.items():
                usage[field] += value
            for artifact_index, artifact in enumerate(
                require_list(entry.get("artifacts"), f"{entry_context}.artifacts")
            ):
                require_artifact_digest(
                    repo_root,
                    artifact,
                    f"{entry_context}.artifacts[{artifact_index}]",
                    artifact_root,
                    require_bytes=True,
                )
            finished.add(branch_id)
        elif event_type == "state_transition":
            fields = common | {"from_state", "to_state", "reason", "result"}
            require_exact_fields(entry, fields, entry_context)
            if entry.get("from_state") != "authorized":
                raise DiscoveryValidationError(f"{entry_context}.from_state must be authorized")
            to_state = require_string(entry.get("to_state"), f"{entry_context}.to_state")
            if to_state not in {"closed", "exhausted"}:
                raise DiscoveryValidationError(f"{entry_context}.to_state is invalid")
            if set(opened) != finished:
                raise DiscoveryValidationError(f"{entry_context} has unfinished branches")
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
            if set(result_branches) != finished:
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
            ) != len(finished):
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
        if record.effective_state not in {"closed", "exhausted"}:
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
        if record.effective_state in {"closed", "exhausted"}
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
    _, activation_floor, minimum_primary, forbidden, sandbox_policy = load_protocol(repo_root)
    route_statuses, route_locator_ids = load_route_registry(repo_root)
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
        f"({sandbox_summary})"
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
