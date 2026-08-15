"""Input-side dynamic-RHS reconstruction audit for two production NEMDE cases."""

from __future__ import annotations

import binascii
import copy
import hashlib
import json
import math
import struct
import subprocess
import tempfile
import zlib
from collections import Counter
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, cast

import yaml

SCHEMA_VERSION = "ecophys-aemo-nemde-rhs-reconstruction/v1"
MATERIALIZATION_SCHEMA_VERSION = "ecophys-aemo-nemde-rhs-materialization/v1"
SUMMARY_SCHEMA_VERSION = "ecophys-aemo-nemde-rhs-summary/v1"
SOURCE_MANIFEST_PATH = "data/manifests/aemo_nemde_rhs_reconstruction_v1.yaml"
EXPECTED_PARENT_COMMIT = "eb53bfa4eb02f9b80ebe53c4b876fdd3e927a61f"
NEMPY_COMMIT = "2d3cef0e5545c820067fecddfa2e2fd984ac5583"
RANGE_BYTES = 1_048_576
LOCAL_HEADER = struct.Struct("<4s5H3I2H")
LOCAL_SIGNATURE = b"PK\x03\x04"
SENTINELS = ("-1e100", "1e100")
ENGINE_SOURCE_HASHES = {
    "src/nempy/historical_inputs/rhs_calculator.py": (
        "eac0760c8c139a307355e229bfe2c6387a0daa50b87177aa8c3faa6eab8dd18a"
    ),
    "src/nempy/historical_inputs/xml_cache.py": (
        "e9233ed62dbc5f59bb0496f3abe20faf480c54768b5b45da46aacda70a0eff76"
    ),
}
EXPECTED_OBJECTS: tuple[dict[str, object], ...] = (
    {
        "object_id": "pre-5ms-nemde-xml-2021-01-01-144",
        "market_date": "2021-01-01",
        "mechanism_phase": "A0_30_MINUTE_ONLY",
        "r2_key": "raw/aemo/v14_nemde_xml_conformance/NEMSPDOutputs_2021010114400.loaded.range-57637442-58686017.bin",
        "expected_filename": "NEMSPDOutputs_2021010114400.loaded.range-57637442-58686017.bin",
        "range_sha256": "200ecb76f773bfdb227d69a3197cd32d5b7f34829631616892df8ce24d618d63",
        "range_bytes": RANGE_BYTES,
        "member_name": "NEMSPDOutputs_2021010114400.loaded",
        "member_flags": 0,
        "compression_method": 8,
        "crc32": "11f971a8",
        "compressed_bytes": 404_030,
        "uncompressed_bytes": 7_851_704,
        "xml_sha256": "63f5af1d9cce6b4cd6503bb4e7e86564ea9ab9a576c3556f96fe31d3a75d0bff",
    },
    {
        "object_id": "post-5ms-nemde-xml-2021-12-01-144",
        "market_date": "2021-12-01",
        "mechanism_phase": "A3_5MS_PLUS_WDR",
        "r2_key": "raw/aemo/v14_nemde_xml_conformance/NEMSPDOutputs_2021120114400.loaded.range-65590506-66639081.bin",
        "expected_filename": "NEMSPDOutputs_2021120114400.loaded.range-65590506-66639081.bin",
        "range_sha256": "9b7f027a2e79128e1eb45309d112b16d74217cf6cd14caa72318616e1254e042",
        "range_bytes": RANGE_BYTES,
        "member_name": "NEMSPDOutputs_2021120114400.loaded",
        "member_flags": 0,
        "compression_method": 8,
        "crc32": "ebbea93d",
        "compressed_bytes": 459_136,
        "uncompressed_bytes": 8_895_016,
        "xml_sha256": "18b7a9f4ae4627a51241a03869533b12b94afc3589a1a02269e34dfe929bd5e0",
    },
)


def file_sha256(path: str | Path) -> str:
    """Hash a local file without loading it all into memory."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: str | Path) -> dict[str, object]:
    """Load the frozen RHS manifest."""

    payload: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("RHS manifest root must be a mapping")
    return cast(dict[str, object], payload)


def load_json(path: str | Path) -> dict[str, object]:
    """Load a JSON mapping."""

    payload: object = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be a mapping")
    return cast(dict[str, object], payload)


def manifest_sha256(path: str | Path) -> str:
    """Hash exact manifest bytes."""

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


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


def validate_manifest(manifest: Mapping[str, object]) -> tuple[str, ...]:
    """Validate the exact two-case, R2-only reconstruction boundary."""

    errors: list[str] = []
    expected_root = {
        "schema_version",
        "sample_id",
        "frozen_at",
        "parent_commit",
        "scientific_role",
        "prior_xml_result",
        "selection",
        "source_access_contract",
        "objects",
        "engine_contract",
        "reference_contract",
        "sentinel_contract",
        "metrics",
        "claim_locks",
        "outputs",
    }
    if set(manifest) != expected_root:
        errors.append("manifest root keys changed")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append("manifest schema changed")
    if manifest.get("parent_commit") != EXPECTED_PARENT_COMMIT:
        errors.append("manifest parent commit changed")
    if not _utc(manifest.get("frozen_at")):
        errors.append("manifest frozen_at is invalid")
    if manifest.get("scientific_role") != "development_only_input_side_dynamic_rhs_reconstructibility":
        errors.append("scientific role changed")
    prior = manifest.get("prior_xml_result")
    if not isinstance(prior, Mapping) or dict(prior) != {
        "protocol_commit": "9f44bb4431b57564608848cb5b577b7b1e58fa9b",
        "result_commit": "a203661f93c1a1c4684652e551ad015455f5d948",
        "decision": "PASS_NEMDE_XML_CONFORMANCE",
        "source_manifest_sha256": "25e06b7049f662edc21e1f74c5b0c3d676de9c8a4b3f3b4309a3ab3d1ac40cb5",
        "retention_receipt_sha256": "b36f59936deddf927957308a32a4cf150b6dfe1c7c71c78dfbeaea7e43b07609",
        "summary_sha256": "f48d86b8f7837956fa5813e8719a712d543ade3e795fa1ad691036bd096bb7cd",
    }:
        errors.append("prior XML result changed")
    selection = manifest.get("selection")
    if not isinstance(selection, Mapping) or dict(selection) != {
        "rule": "exact_two_consumed_interval_144_cases_from_prior_conformance",
        "dates": ["2021-01-01", "2021-12-01"],
        "held_out_status": "development_consumed_not_eligible_for_confirmation",
        "replacement_allowed": False,
    }:
        errors.append("selection contract changed")
    access = manifest.get("source_access_contract")
    if not isinstance(access, Mapping) or dict(access) != {
        "new_aemo_request_count": 0,
        "r2_bucket": "ecophys",
        "exact_r2_object_count": 2,
        "exact_total_materialized_bytes": 2 * RANGE_BYTES,
        "mismatched_remote_overwrite_allowed": False,
        "source_fallback_allowed": False,
        "raw_ranges_or_xml_committed_to_git": False,
    }:
        errors.append("source access contract changed")
    objects = manifest.get("objects")
    if not isinstance(objects, list) or objects != list(EXPECTED_OBJECTS):
        errors.append("object contract changed")
    engine = manifest.get("engine_contract")
    if not isinstance(engine, Mapping) or dict(engine) != {
        "repository": "https://github.com/UNSW-CEEM/nempy.git",
        "commit": NEMPY_COMMIT,
        "package_version": "3.0.3",
        "license": "BSD-3-Clause",
        "clean_checkout_required": True,
        "source_files": ENGINE_SOURCE_HASHES,
        "runtime": {
            "python": "3.11",
            "xmltodict": "0.12.0",
            "mathematical_solver_required": False,
        },
    }:
        errors.append("engine contract changed")
    reference = manifest.get("reference_contract")
    if not isinstance(reference, Mapping) or dict(reference) != {
        "section": "NemSpdOutputs/ConstraintSolution",
        "intervention": "0",
        "duplicate_constraint_id_allowed": False,
        "nonfinite_rhs_allowed": False,
        "reference_access_role": "scoring_only_after_predictions",
        "individual_rhs_values_committed_to_git": False,
    }:
        errors.append("reference contract changed")
    sentinel = manifest.get("sentinel_contract")
    if not isinstance(sentinel, Mapping) or dict(sentinel) != {
        "field": "NemSpdOutputs/ConstraintSolution/@RHS",
        "sentinel_a": SENTINELS[0],
        "sentinel_b": SENTINELS[1],
        "replace_all_output_constraint_rhs": True,
        "input_document_mutation_allowed": False,
        "equation_selection": "all_input_dynamic_rhs_equations_sorted_by_constraint_id",
        "exception_filtering_allowed": False,
        "retry_or_equation_repair_allowed": False,
        "exact_success_value_match_required": True,
        "matching_success_or_error_outcome_required": True,
    }:
        errors.append("sentinel contract changed")
    metrics = manifest.get("metrics")
    if not isinstance(metrics, Mapping) or dict(metrics) != {
        "normalized_error": "abs_prediction_minus_reference_over_max_one_abs_reference",
        "quantile_method": "linear_type_7",
        "per_case_gates": {
            "minimum_dynamic_equation_count": 1,
            "minimum_reference_coverage": 1.0,
            "minimum_evaluation_coverage": 0.95,
            "minimum_sentinel_outcome_match_rate": 1.0,
            "minimum_sentinel_success_value_match_rate": 1.0,
            "maximum_median_normalized_error": 1.0e-8,
            "maximum_p95_normalized_error": 1.0e-3,
        },
        "aggregate_rule": "both_cases_must_pass_every_gate",
        "maximum_error_is_report_only": True,
    }:
        errors.append("metric contract changed")
    locks = manifest.get("claim_locks")
    if not isinstance(locks, Mapping) or dict(locks) != {
        "input_side_dynamic_rhs_component_claim_allowed_on_pass": True,
        "full_input_only_replay_claim_allowed": False,
        "counterfactual_mechanism_claim_allowed": False,
        "participant_adaptation_claim_allowed": False,
        "causal_claim_allowed": False,
        "experiment_156_allowed": False,
        "gpu_allowed": False,
        "paid_data_allowed": False,
        "raw_redistribution_allowed": False,
    }:
        errors.append("claim locks changed")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, Mapping) or set(outputs) != {
        "raw_root",
        "materialization_receipt",
        "summary",
    }:
        errors.append("output contract changed")
    elif any(not _safe_relative(value) for value in outputs.values()):
        errors.append("output path is unsafe")
    return tuple(errors)


def validate_materialization_receipt(
    receipt: Mapping[str, object], manifest: Mapping[str, object]
) -> tuple[str, ...]:
    """Validate exact R2-only materialization without source fallback."""

    errors: list[str] = []
    if receipt.get("schema_version") != MATERIALIZATION_SCHEMA_VERSION:
        errors.append("materialization schema changed")
    if not _utc(receipt.get("generated_at")) or not _sha(receipt.get("protocol_git_commit"), 40):
        errors.append("materialization provenance is invalid")
    if receipt.get("source_manifest") != SOURCE_MANIFEST_PATH or not _sha(
        receipt.get("source_manifest_sha256")
    ):
        errors.append("materialization manifest provenance changed")
    if receipt.get("bucket") != "ecophys" or receipt.get("new_aemo_request_count") != 0:
        errors.append("materialization source boundary changed")
    raw_objects = receipt.get("objects")
    specs = cast(list[dict[str, object]], manifest["objects"])
    if not isinstance(raw_objects, list) or len(raw_objects) != len(specs):
        errors.append("materialization object count changed")
        return tuple(errors)
    for index, (raw, spec) in enumerate(zip(raw_objects, specs, strict=True)):
        if not isinstance(raw, Mapping):
            errors.append(f"materialization object {index} is invalid")
            continue
        expected_sha = spec["range_sha256"]
        if raw.get("object_id") != spec["object_id"] or raw.get("r2_key") != spec["r2_key"]:
            errors.append(f"materialization object {index} identity changed")
        if raw.get("local_filename") != spec["expected_filename"]:
            errors.append(f"materialization object {index} filename changed")
        if (
            raw.get("remote_content_length") != RANGE_BYTES
            or raw.get("remote_metadata_sha256") != expected_sha
            or raw.get("local_bytes") != RANGE_BYTES
            or raw.get("local_sha256") != expected_sha
            or raw.get("verified") is not True
        ):
            errors.append(f"materialization object {index} was not hash-verified")
        if raw.get("local_header_opened") is not False or raw.get("xml_opened") is not False:
            errors.append(f"materialization object {index} accessed content")
    if receipt.get("all_verified") is not True:
        errors.append("materialization did not verify every object")
    return tuple(errors)


def verify_local_ranges(
    raw_root: str | Path, receipt: Mapping[str, object], manifest: Mapping[str, object]
) -> tuple[str, ...]:
    """Verify materialized ranges against frozen hashes."""

    errors: list[str] = []
    materialized = cast(list[dict[str, object]], receipt["objects"])
    specs = cast(list[dict[str, object]], manifest["objects"])
    for index, (item, spec) in enumerate(zip(materialized, specs, strict=True)):
        path = Path(raw_root) / cast(str, spec["expected_filename"])
        if not path.is_file():
            errors.append(f"local range {index} is absent")
        elif (
            path.stat().st_size != RANGE_BYTES
            or file_sha256(path) != spec["range_sha256"]
            or item.get("local_sha256") != spec["range_sha256"]
        ):
            errors.append(f"local range {index} differs from frozen hash")
    return tuple(errors)


def extract_member_xml(path: str | Path, spec: Mapping[str, object]) -> bytes:
    """Extract one frozen raw-deflate member after exact header, size and CRC checks."""

    data = Path(path).read_bytes()
    if len(data) != RANGE_BYTES or len(data) < LOCAL_HEADER.size:
        raise ValueError("range byte count differs from contract")
    (
        signature,
        _version_needed,
        flags,
        method,
        _modified_time,
        _modified_date,
        crc32,
        compressed_bytes,
        uncompressed_bytes,
        filename_bytes,
        extra_bytes,
    ) = LOCAL_HEADER.unpack_from(data)
    if signature != LOCAL_SIGNATURE:
        raise ValueError("local ZIP header signature changed")
    name_end = LOCAL_HEADER.size + filename_bytes
    payload_start = name_end + extra_bytes
    payload_end = payload_start + compressed_bytes
    if payload_end > len(data):
        raise ValueError("member payload exceeds frozen range")
    encoding = "utf-8" if flags & 0x800 else "cp437"
    member_name = data[LOCAL_HEADER.size : name_end].decode(encoding)
    expected_crc = int(cast(str, spec["crc32"]), 16)
    if (
        member_name != spec["member_name"]
        or flags != spec["member_flags"]
        or method != spec["compression_method"]
        or crc32 != expected_crc
        or compressed_bytes != spec["compressed_bytes"]
        or uncompressed_bytes != spec["uncompressed_bytes"]
    ):
        raise ValueError("local ZIP member metadata differs from contract")
    inflater = zlib.decompressobj(-zlib.MAX_WBITS)
    xml_bytes = inflater.decompress(data[payload_start:payload_end]) + inflater.flush()
    if (
        not inflater.eof
        or inflater.unconsumed_tail
        or inflater.unused_data
        or len(xml_bytes) != uncompressed_bytes
    ):
        raise ValueError("raw-deflate stream did not terminate at frozen size")
    observed_crc = binascii.crc32(xml_bytes) & 0xFFFFFFFF
    if observed_crc != expected_crc:
        raise ValueError("XML CRC differs from contract")
    if hashlib.sha256(xml_bytes).hexdigest() != spec["xml_sha256"]:
        raise ValueError("XML SHA differs from prior conformance result")
    if b"<!DOCTYPE" in xml_bytes.upper() or b"<!ENTITY" in xml_bytes.upper():
        raise ValueError("prohibited DTD/entity token present")
    return xml_bytes


def _constraint_solutions(document: Mapping[str, Any]) -> list[dict[str, Any]]:
    root = document.get("NEMSPDCaseFile")
    if not isinstance(root, Mapping):
        raise ValueError("NEMSPDCaseFile root is absent")
    outputs = root.get("NemSpdOutputs")
    if not isinstance(outputs, Mapping):
        raise ValueError("NemSpdOutputs is absent")
    raw = outputs.get("ConstraintSolution")
    if isinstance(raw, Mapping):
        return [cast(dict[str, Any], raw)]
    if isinstance(raw, list) and all(isinstance(item, dict) for item in raw):
        return cast(list[dict[str, Any]], raw)
    raise ValueError("ConstraintSolution collection is invalid")


def seal_reference_and_make_sentinels(
    document: Mapping[str, Any],
) -> tuple[dict[str, float], dict[str, Any], dict[str, Any], int]:
    """Seal intervention-zero references and replace every output RHS in two copies."""

    references: dict[str, float] = {}
    for row in _constraint_solutions(document):
        if str(row.get("@Intervention")) != "0":
            continue
        constraint_id = row.get("@ConstraintID")
        raw_rhs = row.get("@RHS")
        if not isinstance(constraint_id, str) or raw_rhs is None:
            raise ValueError("reference constraint identity or RHS is absent")
        if constraint_id in references:
            raise ValueError(f"duplicate intervention-zero constraint: {constraint_id}")
        value = float(raw_rhs)
        if not math.isfinite(value):
            raise ValueError(f"nonfinite production RHS: {constraint_id}")
        references[constraint_id] = value
    if not references:
        raise ValueError("no intervention-zero production RHS references")

    copies = [
        cast(dict[str, Any], copy.deepcopy(document)),
        cast(dict[str, Any], copy.deepcopy(document)),
    ]
    replacement_counts: list[int] = []
    for sentinel, copied in zip(SENTINELS, copies, strict=True):
        rows = _constraint_solutions(copied)
        replaced = 0
        for row in rows:
            if "@RHS" not in row:
                raise ValueError("output constraint lacks @RHS")
            row["@RHS"] = sentinel
            replaced += 1
        replacement_counts.append(replaced)
    if replacement_counts[0] != replacement_counts[1] or replacement_counts[0] == 0:
        raise ValueError("sentinel replacement count is inconsistent")
    return references, copies[0], copies[1], replacement_counts[0]


def audit_engine_checkout(root: str | Path) -> dict[str, object]:
    """Verify the exact clean Nempy commit and source hashes."""

    engine_root = Path(root)
    result: dict[str, object] = {
        "repository": "https://github.com/UNSW-CEEM/nempy.git",
        "expected_commit": NEMPY_COMMIT,
        "observed_commit": None,
        "clean": False,
        "source_hashes": {},
        "pass": False,
    }
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=engine_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=engine_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        checkout_clean = status == ""
        observed_hashes = {relative: file_sha256(engine_root / relative) for relative in ENGINE_SOURCE_HASHES}
    except (OSError, subprocess.CalledProcessError) as error:
        result["error"] = f"{type(error).__name__}: {error}"
        return result
    result.update(
        {
            "observed_commit": commit,
            "clean": checkout_clean,
            "source_hashes": observed_hashes,
            "pass": (commit == NEMPY_COMMIT and checkout_clean and observed_hashes == ENGINE_SOURCE_HASHES),
        }
    )
    return result


def evaluate_rhs_document(
    document: Mapping[str, Any], xml_cache_class: type[Any], rhs_calculator_class: type[Any]
) -> list[dict[str, object]]:
    """Evaluate every input-side dynamic RHS equation once, retaining all failures."""

    with tempfile.TemporaryDirectory(prefix="ecophys-nempy-rhs-") as cache:
        manager = xml_cache_class(cache)
        manager.xml = document
        engine = rhs_calculator_class(manager)
        raw_equations = engine.rhs_constraint_equations
        if not isinstance(raw_equations, Mapping):
            raise TypeError("Nempy RHS equation inventory is not a mapping")
        results: list[dict[str, object]] = []
        for constraint_id in sorted(str(key) for key in raw_equations):
            try:
                raw_value = engine.compute_constraint_rhs(constraint_id)
                value = float(raw_value)
                if not math.isfinite(value):
                    raise ValueError("computed RHS is nonfinite")
                results.append(
                    {
                        "constraint_id": constraint_id,
                        "status": "ok",
                        "value": value,
                        "value_hex": value.hex(),
                    }
                )
            except Exception as error:
                results.append(
                    {
                        "constraint_id": constraint_id,
                        "status": "error",
                        "error_type": type(error).__name__,
                        "error_message": str(error)[:500],
                    }
                )
    return results


def _quantile(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * probability
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    weight = index - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def score_case(
    spec: Mapping[str, object],
    references: Mapping[str, float],
    sentinel_a: list[dict[str, object]],
    sentinel_b: list[dict[str, object]],
    replacement_count: int,
) -> dict[str, object]:
    """Apply frozen coverage, sentinel-invariance and normalized-error gates."""

    by_a = {cast(str, item["constraint_id"]): item for item in sentinel_a}
    by_b = {cast(str, item["constraint_id"]): item for item in sentinel_b}
    equation_ids = sorted(set(by_a) | set(by_b))
    outcome_matches = 0
    both_success = 0
    exact_value_matches = 0
    reference_available = 0
    scored = 0
    absolute_errors: list[float] = []
    normalized_errors: list[float] = []
    failed_ids: list[str] = []
    error_types: Counter[str] = Counter()
    for constraint_id in equation_ids:
        left = by_a.get(constraint_id)
        right = by_b.get(constraint_id)
        left_status = left.get("status") if left else "missing"
        right_status = right.get("status") if right else "missing"
        if left_status == right_status:
            outcome_matches += 1
        if constraint_id in references:
            reference_available += 1
        if left is None or right is None or left_status != "ok" or right_status != "ok":
            failed_ids.append(constraint_id)
            for item in (left, right):
                if item is not None and item.get("status") == "error":
                    error_types[cast(str, item.get("error_type", "UnknownError"))] += 1
            continue
        both_success += 1
        if left["value_hex"] == right["value_hex"]:
            exact_value_matches += 1
        else:
            failed_ids.append(constraint_id)
            continue
        if constraint_id not in references:
            continue
        prediction = cast(float, left["value"])
        reference = references[constraint_id]
        absolute = abs(prediction - reference)
        normalized = absolute / max(1.0, abs(reference))
        absolute_errors.append(absolute)
        normalized_errors.append(normalized)
        scored += 1

    count = len(equation_ids)
    reference_coverage = reference_available / count if count else 0.0
    evaluation_coverage = scored / count if count else 0.0
    outcome_match_rate = outcome_matches / count if count else 0.0
    value_match_rate = exact_value_matches / both_success if both_success else 0.0
    median_normalized = _quantile(normalized_errors, 0.5)
    p95_normalized = _quantile(normalized_errors, 0.95)
    gates = {
        "minimum_dynamic_equation_count": count >= 1,
        "minimum_reference_coverage": reference_coverage >= 1.0,
        "minimum_evaluation_coverage": evaluation_coverage >= 0.95,
        "minimum_sentinel_outcome_match_rate": outcome_match_rate >= 1.0,
        "minimum_sentinel_success_value_match_rate": value_match_rate >= 1.0,
        "maximum_median_normalized_error": (median_normalized is not None and median_normalized <= 1.0e-8),
        "maximum_p95_normalized_error": (p95_normalized is not None and p95_normalized <= 1.0e-3),
    }
    return {
        "object_id": spec["object_id"],
        "market_date": spec["market_date"],
        "mechanism_phase": spec["mechanism_phase"],
        "production_reference_count": len(references),
        "output_rhs_replacement_count_per_sentinel": replacement_count,
        "dynamic_equation_count": count,
        "reference_available_count": reference_available,
        "both_sentinel_success_count": both_success,
        "sentinel_exact_value_match_count": exact_value_matches,
        "scored_count": scored,
        "reference_coverage": reference_coverage,
        "evaluation_coverage": evaluation_coverage,
        "sentinel_outcome_match_rate": outcome_match_rate,
        "sentinel_success_value_match_rate": value_match_rate,
        "errors": {
            "absolute_median": _quantile(absolute_errors, 0.5),
            "absolute_p95": _quantile(absolute_errors, 0.95),
            "absolute_max": max(absolute_errors) if absolute_errors else None,
            "normalized_median": median_normalized,
            "normalized_p95": p95_normalized,
            "normalized_p99": _quantile(normalized_errors, 0.99),
            "normalized_max": max(normalized_errors) if normalized_errors else None,
        },
        "failed_constraint_ids": failed_ids,
        "error_type_counts_across_sentinels": dict(sorted(error_types.items())),
        "gates": gates,
        "pass": all(gates.values()),
    }


def summarize_reconstruction(
    cases: list[dict[str, object]],
    receipt: Mapping[str, object],
    engine_audit: Mapping[str, object],
    *,
    source_manifest_sha256: str,
    analyzer_git_commit: str,
    generated_at: str,
) -> dict[str, object]:
    """Produce the immutable aggregate decision and keep downstream claims locked."""

    objects = receipt.get("objects")
    verified_count = (
        sum(item.get("verified") is True for item in objects)
        if isinstance(objects, list) and all(isinstance(item, Mapping) for item in objects)
        else 0
    )
    sentinel_integrity = len(cases) == 2 and all(
        case.get("sentinel_outcome_match_rate") == 1.0
        and case.get("sentinel_success_value_match_rate") == 1.0
        for case in cases
    )
    integrity_pass = verified_count == 2 and engine_audit.get("pass") is True and sentinel_integrity
    scientific_pass = integrity_pass and all(case.get("pass") is True for case in cases)
    if scientific_pass:
        decision = "PASS_INPUT_SIDE_DYNAMIC_RHS_RECONSTRUCTION"
    elif integrity_pass:
        decision = "PARTIAL_INPUT_SIDE_DYNAMIC_RHS_RECONSTRUCTION"
    else:
        decision = "FAIL_INPUT_SIDE_DYNAMIC_RHS_INTEGRITY"
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "generated_at": generated_at,
        "analyzer_git_commit": analyzer_git_commit,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": source_manifest_sha256,
        "decision": decision,
        "pass": scientific_pass,
        "integrity_pass": integrity_pass,
        "counts": {
            "case_count": len(cases),
            "r2_verified_count": verified_count,
            "case_pass_count": sum(case.get("pass") is True for case in cases),
        },
        "engine": dict(engine_audit),
        "cases": cases,
        "claim_boundary": {
            "input_side_dynamic_rhs_component_validated": scientific_pass,
            "one_day_alignment_design_unlocked": scientific_pass,
            "full_input_only_replay_validated": False,
            "counterfactual_mechanism_validated": False,
            "participant_adaptation_validated": False,
            "causal_or_model_claim_allowed": False,
            "experiment_156_allowed": False,
            "raw_redistribution_allowed": False,
        },
        "resources": {
            "new_aemo_requests": 0,
            "r2_materialized_bytes": 2 * RANGE_BYTES,
            "gpu_hours": 0,
            "paid_data_spend": 0,
            "mathematical_solver_used": False,
        },
    }
