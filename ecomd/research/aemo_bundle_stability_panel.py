"""Frozen within-version multi-day stability panel for the AEMO bundle bridge."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import cast
from urllib.parse import unquote, urlparse

import yaml

from ecomd.research.aemo_bundle_confirmation import (
    EXPECTED_GATES,
    EXPECTED_RELATION_CONTRACT,
)
from ecomd.research.aemo_row_conformance import file_sha256

SCHEMA_VERSION = "ecophys-aemo-bundle-stability-panel/v1"
DOWNLOAD_SCHEMA_VERSION = "ecophys-aemo-bundle-stability-panel-download/v1"
RETENTION_SCHEMA_VERSION = "ecophys-aemo-bundle-stability-panel-retention/v1"
DAY_SUMMARY_SCHEMA_VERSION = "ecophys-aemo-bundle-stability-panel-day/v1"
SUMMARY_SCHEMA_VERSION = "ecophys-aemo-bundle-stability-panel-summary/v1"
SOURCE_MANIFEST_PATH = "data/manifests/aemo_bundle_stability_panel_v1.yaml"
EXPECTED_MANIFEST_SHA256 = "a155a7be423b7b2ec0e84024df3e52d88b065706dc24df11a171e90c6b206dc9"
EXPECTED_CANONICAL_SHA256 = "6020041732fabd21d7ecf1f381d3bb00530d5420d800ba5d6079d0926347aa2b"
EXPECTED_PARENT_COMMIT = "1854f2d0f77c4cfd4475edfb83856534a8ea91b9"
EXPECTED_DATES = ("2026-06-23", "2026-06-30", "2026-07-14", "2026-07-28")
EXPECTED_NEW_BYTES = 70_593_936
EXPECTED_REUSED_BYTES = 756_828
EXPECTED_STAGED_BYTES = 71_350_764
EXPECTED_NEW_OBJECT_COUNT = 8
EXPECTED_REUSED_OBJECT_COUNT = 2


def load_panel_manifest(path: str | Path) -> dict[str, object]:
    """Load the frozen panel manifest."""

    payload: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("AEMO bundle-stability manifest root must be a mapping")
    return cast(dict[str, object], payload)


def manifest_sha256(path: str | Path) -> str:
    """Hash exact manifest bytes."""

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_manifest_sha256(manifest: Mapping[str, object]) -> str:
    """Hash the parsed manifest independently of YAML formatting."""

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


def _object_index(
    items: Sequence[Mapping[str, object]],
) -> dict[str, Mapping[str, object]]:
    return {cast(str, item["object_id"]): item for item in items}


def validate_panel_manifest(manifest: Mapping[str, object], *, source_sha256: str) -> tuple[str, ...]:
    """Validate the exact frozen bytes and core panel semantics."""

    errors: list[str] = []
    if source_sha256 != EXPECTED_MANIFEST_SHA256:
        errors.append("manifest byte SHA changed")
    if canonical_manifest_sha256(manifest) != EXPECTED_CANONICAL_SHA256:
        errors.append("manifest content changed")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version changed")
    if manifest.get("parent_commit") != EXPECTED_PARENT_COMMIT:
        errors.append("parent_commit changed")
    if not _utc(manifest.get("frozen_at")):
        errors.append("frozen_at must be UTC")

    selection = manifest.get("selection")
    if not isinstance(selection, Mapping):
        errors.append("selection must be a mapping")
    else:
        if tuple(selection.get("selected_dates", ())) != EXPECTED_DATES:
            errors.append("selected_dates changed")
        if selection.get("previously_accessed_dates_excluded") != [
            "2026-06-16",
            "2026-07-07",
        ]:
            errors.append("accessed-date exclusions changed")
        if selection.get("row_content_used_for_selection") is not False:
            errors.append("selection used row content")
        if selection.get("no_replacement") is not True:
            errors.append("replacement prohibition changed")

    new_objects = manifest.get("new_objects")
    reused_objects = manifest.get("reused_objects")
    if not isinstance(new_objects, list) or len(new_objects) != EXPECTED_NEW_OBJECT_COUNT:
        errors.append("new object count changed")
        new_objects = []
    if not isinstance(reused_objects, list) or len(reused_objects) != EXPECTED_REUSED_OBJECT_COUNT:
        errors.append("reused object count changed")
        reused_objects = []
    all_items = [cast(Mapping[str, object], item) for item in [*new_objects, *reused_objects]]
    object_ids = [item.get("object_id") for item in all_items]
    filenames = [item.get("expected_filename") for item in all_items]
    if len(set(object_ids)) != len(object_ids):
        errors.append("object IDs are not unique")
    if len(set(filenames)) != len(filenames):
        errors.append("filenames are not unique")
    for index, item in enumerate(cast(list[dict[str, object]], new_objects)):
        parsed = urlparse(cast(str, item.get("url", "")))
        if (
            parsed.scheme != "https"
            or parsed.hostname != "www.nemweb.com.au"
            or unquote(Path(parsed.path).name) != item.get("expected_filename")
        ):
            errors.append(f"new_objects[{index}].url is outside the frozen boundary")
    for index, item in enumerate(cast(list[dict[str, object]], reused_objects)):
        if item.get("source_get_forbidden") is not True:
            errors.append(f"reused_objects[{index}] source GET is not forbidden")
        if not _sha(item.get("sha256")):
            errors.append(f"reused_objects[{index}] SHA is invalid")

    if sum(cast(int, item["expected_bytes"]) for item in new_objects) != EXPECTED_NEW_BYTES:
        errors.append("new compressed-byte total changed")
    if sum(cast(int, item["expected_bytes"]) for item in reused_objects) != EXPECTED_REUSED_BYTES:
        errors.append("reused compressed-byte total changed")
    resources = manifest.get("resource_contract")
    if not isinstance(resources, Mapping):
        errors.append("resource_contract must be a mapping")
    elif (
        resources.get("exact_new_compressed_bytes") != EXPECTED_NEW_BYTES
        or resources.get("exact_reused_compressed_bytes") != EXPECTED_REUSED_BYTES
        or resources.get("exact_staged_compressed_bytes") != EXPECTED_STAGED_BYTES
        or resources.get("gpu_allowed") is not False
        or resources.get("paid_data_allowed") is not False
    ):
        errors.append("resource contract changed")

    days = manifest.get("days")
    if not isinstance(days, list) or len(days) != len(EXPECTED_DATES):
        errors.append("day count changed")
    else:
        day_dates = tuple(cast(str, cast(Mapping[str, object], item).get("market_date")) for item in days)
        if day_dates != EXPECTED_DATES:
            errors.append("day order changed")
        known_ids = set(object_ids)
        for index, raw_day in enumerate(days):
            day = cast(Mapping[str, object], raw_day)
            for field in (
                "bidmove_object_id",
                "dispatch_object_id",
                "identity_object_id",
            ):
                if day.get(field) not in known_ids:
                    errors.append(f"days[{index}].{field} is unknown")

    outputs = manifest.get("outputs")
    if not isinstance(outputs, Mapping) or any(not _safe_relative(value) for value in outputs.values()):
        errors.append("output paths are unsafe")
    return tuple(errors)


def _load_json(path: str | Path) -> dict[str, object]:
    payload: object = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"receipt root must be a mapping: {path}")
    return cast(dict[str, object], payload)


def load_download_receipt(path: str | Path) -> dict[str, object]:
    """Load the source-download receipt."""

    return _load_json(path)


def load_retention_receipt(path: str | Path) -> dict[str, object]:
    """Load the R2 retention/materialization receipt."""

    return _load_json(path)


def validate_download_receipt(
    receipt: Mapping[str, object], manifest: Mapping[str, object]
) -> tuple[str, ...]:
    """Validate the eight unique opaque source requests."""

    errors: list[str] = []
    if receipt.get("schema_version") != DOWNLOAD_SCHEMA_VERSION:
        errors.append("download schema changed")
    if not _utc(receipt.get("generated_at")):
        errors.append("download generated_at is invalid")
    if not _sha(receipt.get("protocol_git_commit"), 40):
        errors.append("download protocol commit is invalid")
    if receipt.get("source_manifest") != SOURCE_MANIFEST_PATH:
        errors.append("download source manifest changed")
    if receipt.get("source_manifest_sha256") != EXPECTED_MANIFEST_SHA256:
        errors.append("download manifest SHA changed")
    if receipt.get("request_policy") != ("exactly_one_get_per_new_object_no_retry_no_replacement"):
        errors.append("download request policy changed")
    if receipt.get("zip_opened") is not False or receipt.get("csv_rows_opened") is not False:
        errors.append("download claims content access before retention")
    objects = receipt.get("objects")
    specs = cast(list[dict[str, object]], manifest["new_objects"])
    if not isinstance(objects, list) or len(objects) != len(specs):
        errors.append("download object count changed")
        return tuple(errors)
    for index, (raw, spec) in enumerate(zip(objects, specs, strict=True)):
        if not isinstance(raw, Mapping):
            errors.append(f"download objects[{index}] is invalid")
            continue
        if raw.get("object_id") != spec["object_id"]:
            errors.append(f"download objects[{index}] order changed")
        if raw.get("url") != spec["url"] or raw.get("local_filename") != spec["expected_filename"]:
            errors.append(f"download objects[{index}] identity changed")
        if raw.get("request_count") != 1 or raw.get("http_status") != 200:
            errors.append(f"download objects[{index}] request failed")
        if raw.get("observed_bytes") != spec["expected_bytes"]:
            errors.append(f"download objects[{index}] bytes mismatch")
        if not _sha(raw.get("sha256")) or raw.get("download_pass") is not True:
            errors.append(f"download objects[{index}] integrity failed")
        if raw.get("zip_opened") is not False or raw.get("csv_rows_opened") is not False:
            errors.append(f"download objects[{index}] content was accessed")
    if receipt.get("pass") is not True:
        errors.append("download overall decision did not pass")
    return tuple(errors)


def validate_retention_receipt(
    retention: Mapping[str, object],
    download: Mapping[str, object],
    manifest: Mapping[str, object],
) -> tuple[str, ...]:
    """Validate new-object retention and prior-identity R2 materialization."""

    errors: list[str] = []
    if retention.get("schema_version") != RETENTION_SCHEMA_VERSION:
        errors.append("retention schema changed")
    if not _utc(retention.get("generated_at")):
        errors.append("retention generated_at is invalid")
    if retention.get("protocol_git_commit") != download.get("protocol_git_commit"):
        errors.append("retention protocol commit differs from download")
    if retention.get("source_manifest") != SOURCE_MANIFEST_PATH:
        errors.append("retention source manifest changed")
    if retention.get("source_manifest_sha256") != EXPECTED_MANIFEST_SHA256:
        errors.append("retention manifest SHA changed")
    if retention.get("zip_opened") is not False or retention.get("csv_rows_opened") is not False:
        errors.append("retention claims content access before verification")
    retained = retention.get("objects")
    new_specs = cast(list[dict[str, object]], manifest["new_objects"])
    reused_specs = cast(list[dict[str, object]], manifest["reused_objects"])
    specs = [*new_specs, *reused_specs]
    if not isinstance(retained, list) or len(retained) != len(specs):
        errors.append("retention object count changed")
        return tuple(errors)
    downloaded = _object_index(cast(list[Mapping[str, object]], download.get("objects", [])))
    for index, (raw, spec) in enumerate(zip(retained, specs, strict=True)):
        if not isinstance(raw, Mapping):
            errors.append(f"retention objects[{index}] is invalid")
            continue
        object_id = cast(str, spec["object_id"])
        if raw.get("object_id") != object_id:
            errors.append(f"retention objects[{index}] order changed")
        if raw.get("observed_bytes") != spec["expected_bytes"]:
            errors.append(f"retention objects[{index}] local bytes mismatch")
        expected_sha = downloaded[object_id].get("sha256") if object_id in downloaded else spec.get("sha256")
        if raw.get("sha256") != expected_sha:
            errors.append(f"retention objects[{index}] local SHA mismatch")
        if raw.get("remote_content_length") != spec["expected_bytes"]:
            errors.append(f"retention objects[{index}] remote bytes mismatch")
        if raw.get("remote_metadata_sha256") != expected_sha:
            errors.append(f"retention objects[{index}] remote SHA mismatch")
        if raw.get("verified") is not True:
            errors.append(f"retention objects[{index}] is not verified")
        if object_id in downloaded:
            if raw.get("materialization") != "source_download_uploaded_to_frozen_r2":
                errors.append(f"retention objects[{index}] new-object path changed")
        elif (
            raw.get("materialization") != "verified_prior_r2_download_no_source_get"
            or raw.get("source_get_performed") is not False
        ):
            errors.append(f"retention objects[{index}] reuse path changed")
    if retention.get("all_verified") is not True:
        errors.append("retention overall decision did not pass")
    return tuple(errors)


def verify_local_materializations(
    raw_root: str | Path,
    retention: Mapping[str, object],
    manifest: Mapping[str, object],
) -> tuple[str, ...]:
    """Verify every staged local object against the retention receipt."""

    errors: list[str] = []
    root = Path(raw_root)
    specs = [
        *cast(list[dict[str, object]], manifest["new_objects"]),
        *cast(list[dict[str, object]], manifest["reused_objects"]),
    ]
    retained = cast(list[dict[str, object]], retention["objects"])
    for index, (spec, item) in enumerate(zip(specs, retained, strict=True)):
        path = root / cast(str, spec["expected_filename"])
        if not path.is_file():
            errors.append(f"local object {index} is absent")
            continue
        if path.stat().st_size != item["observed_bytes"]:
            errors.append(f"local object {index} byte count changed")
        elif file_sha256(path) != item["sha256"]:
            errors.append(f"local object {index} SHA changed")
    return tuple(errors)


def day_input_specs(manifest: Mapping[str, object], day: Mapping[str, object]) -> list[dict[str, object]]:
    """Resolve the exact three input objects for one panel day."""

    new_index = _object_index(cast(list[Mapping[str, object]], manifest["new_objects"]))
    reused_index = _object_index(cast(list[Mapping[str, object]], manifest["reused_objects"]))
    return [
        dict(new_index[cast(str, day["bidmove_object_id"])]),
        dict(new_index[cast(str, day["dispatch_object_id"])]),
        dict(reused_index[cast(str, day["identity_object_id"])]),
    ]


def build_day_manifest(manifest: Mapping[str, object], day: Mapping[str, object]) -> dict[str, object]:
    """Build the generic three-object manifest consumed by the proven parser."""

    objects = day_input_specs(manifest, day)
    role_sources = {
        "BIDDAYOFFER_D": objects[0]["object_id"],
        "BIDPEROFFER_D": objects[0]["object_id"],
        "DISPATCHOFFERTRK": objects[1]["object_id"],
        "DISPATCHLOAD": objects[1]["object_id"],
        "DUDETAILSUMMARY": objects[2]["object_id"],
    }
    table_contracts = copy.deepcopy(cast(list[dict[str, object]], manifest["table_contract_templates"]))
    for contract in table_contracts:
        contract["source_object_id"] = role_sources[cast(str, contract["logical_role"])]
    return {
        "scientific_role": manifest["scientific_role"],
        "objects": objects,
        "table_contracts": table_contracts,
        "time_contract": {
            "timezone_semantics": "AEMO_MARKET_TIME_AS_PUBLISHED_NO_UTC_CONVERSION",
            "market_date_field_value": day["market_date"],
            "dispatch_interval_start_inclusive": day["interval_start_inclusive"],
            "dispatch_interval_end_inclusive": day["interval_end_inclusive"],
            "identity_interval": "START_DATE <= SETTLEMENTDATE < END_DATE",
        },
        "relation_contract": EXPECTED_RELATION_CONTRACT,
        "gates": EXPECTED_GATES,
    }


def build_day_receipts(
    manifest: Mapping[str, object],
    day: Mapping[str, object],
    download: Mapping[str, object],
    retention: Mapping[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    """Project panel provenance into the three-object day summarizer contract."""

    specs = day_input_specs(manifest, day)
    downloaded = _object_index(cast(list[Mapping[str, object]], download["objects"]))
    retained = _object_index(cast(list[Mapping[str, object]], retention["objects"]))
    projected_downloads: list[dict[str, object]] = []
    projected_retentions: list[dict[str, object]] = []
    for spec in specs:
        object_id = cast(str, spec["object_id"])
        retained_item = retained[object_id]
        source_item = downloaded.get(object_id)
        projected_downloads.append(
            {
                "object_id": object_id,
                "observed_bytes": retained_item["observed_bytes"],
                "sha256": retained_item["sha256"],
                "download_pass": (
                    source_item.get("download_pass") is True
                    if source_item is not None
                    else retained_item.get("verified") is True
                ),
            }
        )
        projected_retentions.append(
            {
                "object_id": object_id,
                "verified": retained_item["verified"],
            }
        )
    return {"objects": projected_downloads}, {"objects": projected_retentions}


def summarize_panel(
    day_summaries: Sequence[Mapping[str, object]],
    manifest: Mapping[str, object],
    download: Mapping[str, object],
    retention: Mapping[str, object],
    *,
    source_manifest_sha256: str,
    analyzer_git_commit: str,
    generated_at: str,
) -> dict[str, object]:
    """Aggregate immutable per-day decisions without refitting the relation rule."""

    new_objects = cast(list[dict[str, object]], download["objects"])
    retained = cast(list[dict[str, object]], retention["objects"])
    passing_days = sum(summary.get("pass") is True for summary in day_summaries)
    panel_gates = cast(dict[str, object], manifest["panel_gates"])
    gates = {
        "new_object_count": len(new_objects) == cast(int, panel_gates["required_new_object_count"]),
        "reused_object_count": len(retained) - len(new_objects)
        == cast(int, panel_gates["required_reused_object_count"]),
        "all_materializations_verified": all(item.get("verified") is True for item in retained),
        "day_count": len(day_summaries) == cast(int, panel_gates["required_day_count"]),
        "all_days_pass": passing_days == cast(int, panel_gates["required_passing_day_count"]),
        "zero_failed_days": len(day_summaries) - passing_days
        <= cast(int, panel_gates["maximum_failed_day_count"]),
        "relation_rule_frozen": panel_gates["relation_rule_change_allowed"] is False,
        "claim_boundary_frozen": (
            panel_gates["cross_version_claim_allowed"] is False
            and panel_gates["causal_claim_allowed"] is False
            and panel_gates["model_claim_allowed"] is False
        ),
    }
    overall_pass = all(gates.values())

    cardinalities: Counter[str] = Counter()
    directions: Counter[str] = Counter()
    bidtypes: Counter[str] = Counter()
    tracker_total = 0
    pair_total = 0
    target_rows = 0
    data_rows = 0
    timestamps = 0
    day_metrics: list[dict[str, object]] = []
    for summary in day_summaries:
        relation = cast(Mapping[str, object], summary["relation"])
        tables = cast(Mapping[str, object], summary["tables"])
        time_metrics = cast(Mapping[str, object], summary["timestamps"])
        cardinalities.update(cast(Mapping[str, int], relation["candidate_cardinality"]))
        directions.update(cast(Mapping[str, int], relation["direction_sets"]))
        bidtypes.update(cast(Mapping[str, int], relation["pair_bidtypes"]))
        tracker_count = cast(int, relation["tracker_count"])
        pair_count = cast(int, relation["pair_count"])
        tracker_total += tracker_count
        pair_total += pair_count
        target_rows += cast(int, tables["total_target_rows"])
        data_rows += cast(int, tables["total_data_rows_all_tables"])
        timestamps += cast(int, time_metrics["expected_count"])
        day_metrics.append(
            {
                "market_date": summary["sample_date"],
                "pass": summary["pass"],
                "tracker_count": tracker_count,
                "pair_count": pair_count,
                "pair_rate": pair_count / tracker_count if tracker_count else 0.0,
                "relation_violation_count": sum(
                    cast(int, relation[field])
                    for field in (
                        "invalid_candidate_cardinality_count",
                        "invalid_single_direction_count",
                        "invalid_pair_direction_count",
                        "duplicate_pair_direction_count",
                        "invalid_pair_identity_count",
                        "invalid_pair_bidtype_count",
                    )
                ),
            }
        )

    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "generated_at": generated_at,
        "analyzer_git_commit": analyzer_git_commit,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": source_manifest_sha256,
        "scientific_role": manifest["scientific_role"],
        "decision": (
            "PASS_MODERN_BUNDLE_STABILITY_PANEL" if overall_pass else "FAIL_MODERN_BUNDLE_STABILITY_PANEL"
        ),
        "pass": overall_pass,
        "gates": gates,
        "raw": {
            "new_object_count": len(new_objects),
            "reused_object_count": len(retained) - len(new_objects),
            "new_compressed_bytes": sum(cast(int, item["observed_bytes"]) for item in new_objects),
            "staged_compressed_bytes": sum(cast(int, item["observed_bytes"]) for item in retained),
        },
        "aggregate": {
            "passing_day_count": passing_days,
            "day_count": len(day_summaries),
            "total_target_rows": target_rows,
            "total_data_rows_all_tables": data_rows,
            "contracted_timestamp_count": timestamps,
            "tracker_count": tracker_total,
            "pair_count": pair_total,
            "pair_rate": pair_total / tracker_total if tracker_total else 0.0,
            "candidate_cardinality": dict(sorted(cardinalities.items())),
            "direction_sets": dict(sorted(directions.items())),
            "pair_bidtypes": dict(sorted(bidtypes.items())),
        },
        "days": day_metrics,
        "day_summaries": [dict(summary) for summary in day_summaries],
        "claim_boundary": {
            "validates": "within-version modern multi-day observation-bridge stability",
            "does_not_validate": [
                "historical table-version portability",
                "raw submissions or rejected actions",
                "dispatch optimization replay",
                "causal adaptation",
                "model prediction or policy fidelity",
            ],
        },
        "gpu_used": False,
        "paid_data_used": False,
        "target_outcome_used": False,
        "model_run": False,
    }
