"""Provenance contract for the zero-source-request panel plumbing repair."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import cast

import yaml

from ecomd.research.aemo_row_conformance import file_sha256

SCHEMA_VERSION = "ecophys-aemo-bundle-stability-panel-repair/v1"
MATERIALIZATION_SCHEMA_VERSION = "ecophys-aemo-bundle-stability-panel-repair-materialization/v1"
SOURCE_MANIFEST_PATH = "data/manifests/aemo_bundle_stability_panel_repair_v1.yaml"
EXPECTED_MANIFEST_SHA256 = "cff318e41a59cb277d691c60186765cd8968c168de78b31f6eac199b28e08690"
EXPECTED_CANONICAL_SHA256 = "84631e4b0b064ba8831cb2ab5b63e0511a495e78900f072368f3033af2328b52"
EXPECTED_PARENT_COMMIT = "0ac261fe0032042b75a87c65ac597a1c6c864a55"
EXPECTED_OBJECT_COUNT = 10
EXPECTED_STAGED_BYTES = 71_350_764
ORIGINAL_MANIFEST_PATH = "data/manifests/aemo_bundle_stability_panel_v1.yaml"
ORIGINAL_DOWNLOAD_PATH = "experiments/v14_aemo_bundle_stability_panel/artifacts/download_receipt.json"
ORIGINAL_RETENTION_PATH = "experiments/v14_aemo_bundle_stability_panel/artifacts/retention_receipt.json"
ORIGINAL_FAILURE_PATH = "experiments/v14_aemo_bundle_stability_panel/artifacts/analysis_failure.json"
EXPECTED_ORIGINAL_HASHES = {
    ORIGINAL_MANIFEST_PATH: ("a155a7be423b7b2ec0e84024df3e52d88b065706dc24df11a171e90c6b206dc9"),
    ORIGINAL_DOWNLOAD_PATH: ("5a9735d0a427bdc5f34e99bb4933dd5ce2c08ffa4ece65d5f108a01ab7b2fabc"),
    ORIGINAL_RETENTION_PATH: ("1eba9a2d9440c2e44edc9af99a236f9500707b1f9c592f9e6e086d69b10776c7"),
    ORIGINAL_FAILURE_PATH: ("0b1d4fa9229997f8be220eda0c9e4bb6319191c13981d658fb222493b8c756f1"),
}


def load_repair_manifest(path: str | Path) -> dict[str, object]:
    """Load the frozen repair manifest."""

    payload: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("repair manifest root must be a mapping")
    return cast(dict[str, object], payload)


def manifest_sha256(path: str | Path) -> str:
    """Hash exact repair-manifest bytes."""

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_manifest_sha256(manifest: Mapping[str, object]) -> str:
    """Hash parsed repair-manifest content."""

    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _utc(value: object) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        parsed = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError:
        return False
    return parsed.tzinfo == UTC


def _sha(value: object, length: int = 64) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in "0123456789abcdef" for character in value)
    )


def _safe_relative(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts


def validate_repair_manifest(manifest: Mapping[str, object], *, source_sha256: str) -> tuple[str, ...]:
    """Validate that repair scope and retained bytes are exactly frozen."""

    errors: list[str] = []
    if source_sha256 != EXPECTED_MANIFEST_SHA256:
        errors.append("repair manifest byte SHA changed")
    if canonical_manifest_sha256(manifest) != EXPECTED_CANONICAL_SHA256:
        errors.append("repair manifest content changed")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append("repair schema changed")
    if manifest.get("parent_commit") != EXPECTED_PARENT_COMMIT:
        errors.append("repair parent commit changed")
    if not _utc(manifest.get("frozen_at")):
        errors.append("repair frozen_at is invalid")
    contract = manifest.get("repair_contract")
    if not isinstance(contract, Mapping):
        errors.append("repair_contract must be a mapping")
    elif (
        contract.get("new_aemo_source_request_count") != 0
        or contract.get("replacement_allowed") is not False
        or contract.get("object_bytes_unchanged") is not True
        or contract.get("table_contracts_unchanged") is not True
        or contract.get("relation_contract_unchanged") is not True
        or contract.get("day_gates_unchanged") is not True
        or contract.get("panel_gates_unchanged") is not True
        or contract.get("claim_boundary_unchanged") is not True
        or contract.get("parser_preflight_required") is not True
    ):
        errors.append("repair boundary changed")
    objects = manifest.get("objects")
    if not isinstance(objects, list) or len(objects) != EXPECTED_OBJECT_COUNT:
        errors.append("repair object count changed")
        objects = []
    object_ids = [cast(Mapping[str, object], item).get("object_id") for item in objects]
    filenames = [cast(Mapping[str, object], item).get("expected_filename") for item in objects]
    if len(set(object_ids)) != len(object_ids):
        errors.append("repair object IDs are not unique")
    if len(set(filenames)) != len(filenames):
        errors.append("repair filenames are not unique")
    for index, raw in enumerate(objects):
        item = cast(Mapping[str, object], raw)
        if item.get("r2_bucket") != "ecophys":
            errors.append(f"objects[{index}] bucket changed")
        if not _sha(item.get("sha256")):
            errors.append(f"objects[{index}] SHA is invalid")
    if sum(cast(int, cast(Mapping[str, object], item)["expected_bytes"]) for item in objects) != (
        EXPECTED_STAGED_BYTES
    ):
        errors.append("repair byte total changed")
    resources = manifest.get("resource_contract")
    if not isinstance(resources, Mapping) or (
        resources.get("exact_object_count") != EXPECTED_OBJECT_COUNT
        or resources.get("exact_staged_compressed_bytes") != EXPECTED_STAGED_BYTES
        or resources.get("maximum_total_data_rows_per_day") != 4_000_000
        or resources.get("gpu_allowed") is not False
        or resources.get("paid_data_allowed") is not False
    ):
        errors.append("repair resource contract changed")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, Mapping) or any(not _safe_relative(value) for value in outputs.values()):
        errors.append("repair output paths are unsafe")
    return tuple(errors)


def validate_original_provenance(root: str | Path) -> tuple[str, ...]:
    """Verify every v1 artifact that makes content-blind repair admissible."""

    errors: list[str] = []
    repository = Path(root)
    for relative, expected_sha in EXPECTED_ORIGINAL_HASHES.items():
        path = repository / relative
        if not path.is_file():
            errors.append(f"original artifact absent: {relative}")
        elif file_sha256(path) != expected_sha:
            errors.append(f"original artifact changed: {relative}")
    if not errors:
        failure: object = json.loads((repository / ORIGINAL_FAILURE_PATH).read_text(encoding="utf-8"))
        if not isinstance(failure, dict) or (
            failure.get("decision") != "FAIL_PANEL_IMPLEMENTATION_PRE_PARSE"
            or failure.get("archive_open_attempt_count") != 0
            or failure.get("market_content_observed") is not False
        ):
            errors.append("original failure no longer proves pre-content status")
    return tuple(errors)


def load_materialization_receipt(path: str | Path) -> dict[str, object]:
    """Load the repair R2 materialization receipt."""

    payload: object = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("materialization receipt root must be a mapping")
    return cast(dict[str, object], payload)


def validate_materialization_receipt(
    receipt: Mapping[str, object], manifest: Mapping[str, object]
) -> tuple[str, ...]:
    """Validate all ten R2-only materializations and zero source requests."""

    errors: list[str] = []
    if receipt.get("schema_version") != MATERIALIZATION_SCHEMA_VERSION:
        errors.append("materialization schema changed")
    if not _utc(receipt.get("generated_at")):
        errors.append("materialization generated_at is invalid")
    if not _sha(receipt.get("protocol_git_commit"), 40):
        errors.append("materialization protocol commit is invalid")
    if receipt.get("source_manifest") != SOURCE_MANIFEST_PATH:
        errors.append("materialization source manifest changed")
    if receipt.get("source_manifest_sha256") != EXPECTED_MANIFEST_SHA256:
        errors.append("materialization manifest SHA changed")
    if receipt.get("aemo_source_request_count") != 0:
        errors.append("repair made a forbidden AEMO source request")
    if receipt.get("zip_opened") is not False or receipt.get("csv_rows_opened") is not False:
        errors.append("repair accessed content before materialization")
    objects = receipt.get("objects")
    specs = cast(list[dict[str, object]], manifest["objects"])
    if not isinstance(objects, list) or len(objects) != len(specs):
        errors.append("materialization object count changed")
        return tuple(errors)
    for index, (raw, spec) in enumerate(zip(objects, specs, strict=True)):
        if not isinstance(raw, Mapping):
            errors.append(f"materialization objects[{index}] is invalid")
            continue
        if raw.get("object_id") != spec["object_id"]:
            errors.append(f"materialization objects[{index}] order changed")
        if raw.get("r2_key") != spec["r2_key"]:
            errors.append(f"materialization objects[{index}] R2 key changed")
        if raw.get("observed_bytes") != spec["expected_bytes"]:
            errors.append(f"materialization objects[{index}] bytes changed")
        if raw.get("sha256") != spec["sha256"]:
            errors.append(f"materialization objects[{index}] SHA changed")
        if raw.get("remote_content_length") != spec["expected_bytes"]:
            errors.append(f"materialization objects[{index}] remote bytes changed")
        if raw.get("remote_metadata_sha256") != spec["sha256"]:
            errors.append(f"materialization objects[{index}] remote SHA changed")
        if raw.get("source_get_performed") is not False:
            errors.append(f"materialization objects[{index}] used source GET")
        if raw.get("verified") is not True:
            errors.append(f"materialization objects[{index}] is not verified")
    if receipt.get("all_verified") is not True:
        errors.append("materialization overall decision did not pass")
    return tuple(errors)


def verify_local_materializations(
    raw_root: str | Path,
    receipt: Mapping[str, object],
    manifest: Mapping[str, object],
) -> tuple[str, ...]:
    """Verify local bytes after R2-only repair materialization."""

    errors: list[str] = []
    root = Path(raw_root)
    objects = cast(list[dict[str, object]], receipt["objects"])
    specs = cast(list[dict[str, object]], manifest["objects"])
    for index, (item, spec) in enumerate(zip(objects, specs, strict=True)):
        path = root / cast(str, spec["expected_filename"])
        if not path.is_file():
            errors.append(f"local repair object {index} is absent")
            continue
        if path.stat().st_size != item["observed_bytes"]:
            errors.append(f"local repair object {index} bytes changed")
        elif file_sha256(path) != item["sha256"]:
            errors.append(f"local repair object {index} SHA changed")
    return tuple(errors)
