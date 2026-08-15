"""Frozen fresh-day confirmation of the AEMO set-valued offer bridge."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import cast
from urllib.parse import unquote, urlparse

import yaml

from ecomd.research.aemo_row_conformance import (
    file_sha256,
    parse_aemo_timestamp,
    table_contracts_by_role,
)

SCHEMA_VERSION = "ecophys-aemo-bundle-confirmation/v1"
DOWNLOAD_SCHEMA_VERSION = "ecophys-aemo-bundle-confirmation-download/v1"
RETENTION_SCHEMA_VERSION = "ecophys-aemo-bundle-confirmation-retention/v1"
SUMMARY_SCHEMA_VERSION = "ecophys-aemo-bundle-confirmation-summary/v1"
SOURCE_MANIFEST_PATH = "data/manifests/aemo_bundle_confirmation_v1.yaml"
PARENT_COMMIT = "2063146c395a1c0104166d6d4ef03604a385e499"
SAMPLE_DATE = "2026-07-07"
EXPECTED_COMPRESSED_BYTES = 18_244_129

EXPECTED_DEVELOPMENT_PROVENANCE = {
    "e1a_decision": "FAIL_MODERN_ROW_CONFORMANCE_SMOKE",
    "e1a_summary_sha256": ("fc422654de5c64a91e71b8dcceb22612f406092cdf6a36900859072041a6668b"),
    "diagnostic_status": "POST_HOC_DEVELOPMENT_DIAGNOSTIC_NO_GATE_DECISION",
    "diagnostic_summary_sha256": ("d8b4bb0ffe6ede3fadf00cdac68c6851568fab132b6e2c94162c8bb4317cfaa2"),
    "development_market_date": "2026-06-16",
    "observed_bundle_rule": "one_candidate_or_exact_unique_GEN_LOAD_pair",
    "e1a_failure_overridden": False,
}

EXPECTED_SELECTION = {
    "rule": "first_tuesday_of_first_complete_calendar_month_after_development_month",
    "development_month": "2026-06",
    "first_complete_later_month": "2026-07",
    "selected_market_date": SAMPLE_DATE,
    "selection_inputs": "directory_metadata_only_no_zip_or_market_row",
    "target_event": False,
    "causal_outcome": False,
    "no_replacement": True,
    "identity_snapshot_not_reused_from_development": True,
}

EXPECTED_SOURCE_METADATA = {
    "bidmove_listing": "https://www.nemweb.com.au/Reports/CURRENT/Bidmove_Complete/",
    "bidmove_listing_sha256": ("37885534285a2039fc8bfea5f1b3592204358467c6d363557c713d8d5980c97f"),
    "next_day_dispatch_listing": ("https://www.nemweb.com.au/Reports/CURRENT/Next_Day_Dispatch/"),
    "next_day_dispatch_listing_sha256": ("a527bbbdebff3a54993b4aaed019cee96f9a9233019ba00bbb06302ff524ed4e"),
    "monthly_identity_listing": (
        "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/"
        "2026/MMSDM_2026_07/MMSDM_Historical_Data_SQLLoader/DATA/"
    ),
    "monthly_identity_listing_sha256": ("79beb058dde1c30616036b21fcd5efa875e93f2f961a0d7f7496b2ae063b5721"),
    "official_bdu_participant_impact": (
        "https://tech-specs.docs.public.aemo.com.au/Content/TSP_EMMSDM53_April2024/Participant_Impact.htm"
    ),
    "official_bidding_dispatch": (
        "https://tech-specs.docs.public.aemo.com.au/Content/TSP_EMMS_June2024/Bidding_and_Dispatch.htm"
    ),
}

EXPECTED_OBJECTS: list[dict[str, object]] = [
    {
        "object_id": "bidmove-complete-2026-07-07",
        "source_role": "BIDMOVE_COMPLETE",
        "url": (
            "https://www.nemweb.com.au/Reports/CURRENT/Bidmove_Complete/"
            "PUBLIC_BIDMOVE_COMPLETE_20260707_0000000526370718.zip"
        ),
        "expected_filename": "PUBLIC_BIDMOVE_COMPLETE_20260707_0000000526370718.zip",
        "expected_bytes": 9_224_570,
        "maximum_uncompressed_bytes": 536_870_912,
        "required_table_roles": ["BIDDAYOFFER_D", "BIDPEROFFER_D"],
        "r2_key": (
            "raw/aemo/v14_bundle_confirmation/market_date=2026-07-07/"
            "PUBLIC_BIDMOVE_COMPLETE_20260707_0000000526370718.zip"
        ),
    },
    {
        "object_id": "next-day-dispatch-2026-07-07",
        "source_role": "NEXT_DAY_DISPATCH",
        "url": (
            "https://www.nemweb.com.au/Reports/CURRENT/Next_Day_Dispatch/"
            "PUBLIC_NEXT_DAY_DISPATCH_20260707_0000000526367103.zip"
        ),
        "expected_filename": ("PUBLIC_NEXT_DAY_DISPATCH_20260707_0000000526367103.zip"),
        "expected_bytes": 8_641_259,
        "maximum_uncompressed_bytes": 536_870_912,
        "required_table_roles": ["DISPATCHOFFERTRK", "DISPATCHLOAD"],
        "r2_key": (
            "raw/aemo/v14_bundle_confirmation/market_date=2026-07-07/"
            "PUBLIC_NEXT_DAY_DISPATCH_20260707_0000000526367103.zip"
        ),
    },
    {
        "object_id": "dudetailsummary-2026-07",
        "source_role": "DUDETAILSUMMARY_MONTHLY_SNAPSHOT",
        "url": (
            "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/"
            "2026/MMSDM_2026_07/MMSDM_Historical_Data_SQLLoader/DATA/"
            "PUBLIC_ARCHIVE%23DUDETAILSUMMARY%23FILE01%23202607010000.zip"
        ),
        "expected_filename": ("PUBLIC_ARCHIVE#DUDETAILSUMMARY#FILE01#202607010000.zip"),
        "expected_bytes": 378_300,
        "maximum_uncompressed_bytes": 33_554_432,
        "required_table_roles": ["DUDETAILSUMMARY"],
        "r2_key": (
            "raw/aemo/v14_bundle_confirmation/market_date=2026-07-07/"
            "PUBLIC_ARCHIVE#DUDETAILSUMMARY#FILE01#202607010000.zip"
        ),
    },
]


def _table(
    logical_role: str,
    source_object_id: str,
    expected_package: str,
    expected_table: str,
    expected_version: str,
    required_fields: list[str],
    primary_key: list[str],
) -> dict[str, object]:
    return {
        "logical_role": logical_role,
        "source_object_id": source_object_id,
        "expected_package": expected_package,
        "expected_table": expected_table,
        "expected_version": expected_version,
        "required_fields": required_fields,
        "primary_key": primary_key,
    }


EXPECTED_TABLES = [
    _table(
        "BIDDAYOFFER_D",
        "bidmove-complete-2026-07-07",
        "BID",
        "BIDDAYOFFER_D",
        "3",
        [
            "SETTLEMENTDATE",
            "DUID",
            "BIDTYPE",
            "DIRECTION",
            "BIDSETTLEMENTDATE",
            "OFFERDATE",
            "PARTICIPANTID",
        ],
        ["SETTLEMENTDATE", "BIDTYPE", "DUID", "DIRECTION"],
    ),
    _table(
        "BIDPEROFFER_D",
        "bidmove-complete-2026-07-07",
        "BID",
        "BIDPEROFFER_D",
        "4",
        [
            "SETTLEMENTDATE",
            "DUID",
            "BIDTYPE",
            "DIRECTION",
            "INTERVAL_DATETIME",
            "BIDSETTLEMENTDATE",
            "OFFERDATE",
            "VERSIONNO",
            "MAXAVAIL",
        ],
        [
            "SETTLEMENTDATE",
            "BIDTYPE",
            "DUID",
            "DIRECTION",
            "INTERVAL_DATETIME",
        ],
    ),
    _table(
        "DISPATCHOFFERTRK",
        "next-day-dispatch-2026-07-07",
        "DISPATCH",
        "OFFERTRK",
        "1",
        [
            "SETTLEMENTDATE",
            "DUID",
            "BIDTYPE",
            "BIDSETTLEMENTDATE",
            "BIDOFFERDATE",
        ],
        ["SETTLEMENTDATE", "DUID", "BIDTYPE"],
    ),
    _table(
        "DISPATCHLOAD",
        "next-day-dispatch-2026-07-07",
        "DISPATCH",
        "UNIT_SOLUTION",
        "6",
        [
            "SETTLEMENTDATE",
            "RUNNO",
            "DUID",
            "INTERVENTION",
            "INITIALMW",
            "TOTALCLEARED",
        ],
        ["SETTLEMENTDATE", "RUNNO", "DUID", "INTERVENTION"],
    ),
    _table(
        "DUDETAILSUMMARY",
        "dudetailsummary-2026-07",
        "PARTICIPANT_REGISTRATION",
        "DUDETAILSUMMARY",
        "7",
        [
            "DUID",
            "START_DATE",
            "END_DATE",
            "DISPATCHTYPE",
            "REGIONID",
            "PARTICIPANTID",
            "DISPATCHSUBTYPE",
        ],
        ["DUID", "START_DATE"],
    ),
]

EXPECTED_TIME_CONTRACT = {
    "timezone_semantics": "AEMO_MARKET_TIME_AS_PUBLISHED_NO_UTC_CONVERSION",
    "market_date_field_value": SAMPLE_DATE,
    "dispatch_interval_start_inclusive": "2026-07-07T04:05:00",
    "dispatch_interval_end_inclusive": "2026-07-08T04:00:00",
    "identity_interval": "START_DATE <= SETTLEMENTDATE < END_DATE",
}
EXPECTED_RELATION_CONTRACT = {
    "tracker_period_key": [
        "SETTLEMENTDATE=INTERVAL_DATETIME",
        "DUID=DUID",
        "BIDTYPE=BIDTYPE",
        "BIDSETTLEMENTDATE=BIDSETTLEMENTDATE",
        "BIDOFFERDATE=OFFERDATE",
    ],
    "allowed_candidate_cardinalities": [1, 2],
    "allowed_single_directions": ["BIDIRECTIONAL", "GEN", "LOAD"],
    "exact_pair_directions": ["GEN", "LOAD"],
    "exact_pair_identity_dispatchtype": "BIDIRECTIONAL",
    "allowed_pair_bidtypes": ["ENERGY", "LOWERREG", "RAISEREG"],
    "pair_must_be_nonempty": True,
    "realized_dispatch_may_select_offer_leg": False,
    "action_representation": "set_valued_applied_offer_version_bundle",
}
EXPECTED_BASE_JOIN_CONTRACT = {
    "bid_period_to_day_parent": ["SETTLEMENTDATE", "DUID", "BIDTYPE", "DIRECTION"],
    "tracker_to_physical_dispatch": ["SETTLEMENTDATE", "DUID"],
    "physical_dispatch_filter": {"RUNNO": 1, "INTERVENTION": 0},
    "dispatch_to_identity": ["DUID", "effective_half_open_interval"],
}
EXPECTED_RESOURCE_CONTRACT = {
    "exact_compressed_bytes": EXPECTED_COMPRESSED_BYTES,
    "maximum_total_uncompressed_bytes": 1_107_296_256,
    "maximum_total_data_rows": 4_000_000,
    "cpu_only": True,
    "gpu_allowed": False,
    "paid_data_allowed": False,
    "remote_worker_required": False,
}
EXPECTED_RETENTION_CONTRACT = {
    "bucket": "ecophys",
    "prefix": "raw/aemo/v14_bundle_confirmation/market_date=2026-07-07/",
    "upload_before_any_csv_row_parse": True,
    "remote_sha256_metadata_required": True,
    "overwrite_mismatched_remote_object_allowed": False,
    "raw_rows_committed_to_git": False,
}
EXPECTED_GATES = {
    "required_object_count": 3,
    "required_r2_verified_count": 3,
    "required_archive_crc_count": 3,
    "required_table_count": 5,
    "required_nonempty_table_count": 5,
    "maximum_total_data_rows": 4_000_000,
    "timestamp_parse_rate_min": 1.0,
    "primary_key_duplicate_count_max": 0,
    "bid_market_date_rate_min": 1.0,
    "dispatch_window_rate_min": 1.0,
    "bid_period_parent_match_rate_min": 1.0,
    "tracker_offer_reference_rate_min": 1.0,
    "tracker_relation_coverage_rate_min": 1.0,
    "tracker_dispatch_match_rate_min": 1.0,
    "dispatch_identity_match_rate_min": 1.0,
    "dispatch_identity_overlap_count_max": 0,
    "invalid_candidate_cardinality_count_max": 0,
    "invalid_single_direction_count_max": 0,
    "invalid_pair_direction_count_max": 0,
    "duplicate_pair_direction_count_max": 0,
    "invalid_pair_identity_count_max": 0,
    "invalid_pair_bidtype_count_max": 0,
    "minimum_pair_count": 1,
    "causal_claim_allowed": False,
    "model_claim_allowed": False,
}
EXPECTED_OUTPUTS = {
    "raw_root": "artifacts/v14_aemo_bundle_confirmation/raw",
    "download_receipt": ("experiments/v14_aemo_bundle_confirmation/artifacts/download_receipt.json"),
    "retention_receipt": ("experiments/v14_aemo_bundle_confirmation/artifacts/retention_receipt.json"),
    "summary": "experiments/v14_aemo_bundle_confirmation/artifacts/summary.json",
}
ROOT_KEYS = frozenset(
    {
        "schema_version",
        "sample_id",
        "frozen_at",
        "parent_commit",
        "scientific_role",
        "development_provenance",
        "selection",
        "source_metadata",
        "objects",
        "table_contracts",
        "time_contract",
        "relation_contract",
        "base_join_contract",
        "resource_contract",
        "retention_contract",
        "gates",
        "outputs",
    }
)


def load_bundle_manifest(path: str | Path) -> dict[str, object]:
    """Load the frozen E1b bundle-confirmation manifest."""

    payload: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("AEMO bundle-confirmation manifest root must be a mapping")
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


def _sha(value: object, length: int) -> bool:
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


def validate_bundle_manifest(manifest: Mapping[str, object]) -> tuple[str, ...]:
    """Validate the exact fresh selection, sources and relation-level gates."""

    errors: list[str] = []
    if set(manifest) != ROOT_KEYS:
        errors.append("root keys changed")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version changed")
    if manifest.get("sample_id") != "aemo-fresh-direction-bundle-confirmation-2026-07-07-v1":
        errors.append("sample_id changed")
    if manifest.get("parent_commit") != PARENT_COMMIT:
        errors.append("parent_commit changed")
    if manifest.get("scientific_role") != ("confirmation_only_modern_set_valued_applied_offer_bridge"):
        errors.append("scientific_role changed")
    if not _utc(manifest.get("frozen_at")):
        errors.append("frozen_at must be UTC")
    if manifest.get("development_provenance") != EXPECTED_DEVELOPMENT_PROVENANCE:
        errors.append("development_provenance changed")
    if manifest.get("selection") != EXPECTED_SELECTION:
        errors.append("selection changed")

    source_metadata = manifest.get("source_metadata")
    if not isinstance(source_metadata, Mapping):
        errors.append("source_metadata must be a mapping")
    else:
        observed = dict(source_metadata)
        audited_at = observed.pop("audited_at", None)
        if not _utc(audited_at):
            errors.append("source_metadata.audited_at must be UTC")
        if observed != EXPECTED_SOURCE_METADATA:
            errors.append("source_metadata changed")

    if manifest.get("objects") != EXPECTED_OBJECTS:
        errors.append("objects changed")
    else:
        for index, item in enumerate(EXPECTED_OBJECTS):
            parsed = urlparse(cast(str, item["url"]))
            if (
                parsed.scheme != "https"
                or parsed.hostname != "www.nemweb.com.au"
                or unquote(Path(parsed.path).name) != item["expected_filename"]
            ):
                errors.append(f"objects[{index}].url is outside the frozen boundary")
    if manifest.get("table_contracts") != EXPECTED_TABLES:
        errors.append("table_contracts changed")
    if manifest.get("time_contract") != EXPECTED_TIME_CONTRACT:
        errors.append("time_contract changed")
    if manifest.get("relation_contract") != EXPECTED_RELATION_CONTRACT:
        errors.append("relation_contract changed")
    if manifest.get("base_join_contract") != EXPECTED_BASE_JOIN_CONTRACT:
        errors.append("base_join_contract changed")
    if manifest.get("resource_contract") != EXPECTED_RESOURCE_CONTRACT:
        errors.append("resource_contract changed")
    if manifest.get("retention_contract") != EXPECTED_RETENTION_CONTRACT:
        errors.append("retention_contract changed")
    if manifest.get("gates") != EXPECTED_GATES:
        errors.append("gates changed")
    if manifest.get("outputs") != EXPECTED_OUTPUTS:
        errors.append("outputs changed")
    elif any(not _safe_relative(value) for value in EXPECTED_OUTPUTS.values()):
        errors.append("output paths are unsafe")
    if sum(cast(int, item["expected_bytes"]) for item in EXPECTED_OBJECTS) != (EXPECTED_COMPRESSED_BYTES):
        errors.append("internal compressed-byte contract is inconsistent")
    return tuple(errors)


def _load_json(path: str | Path) -> dict[str, object]:
    payload: object = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"receipt root must be a mapping: {path}")
    return cast(dict[str, object], payload)


def load_download_receipt(path: str | Path) -> dict[str, object]:
    """Load an E1b download receipt."""

    return _load_json(path)


def load_retention_receipt(path: str | Path) -> dict[str, object]:
    """Load an E1b R2 receipt."""

    return _load_json(path)


def validate_download_receipt(
    receipt: Mapping[str, object], manifest: Mapping[str, object]
) -> tuple[str, ...]:
    """Validate one-shot opaque downloads."""

    errors: list[str] = []
    if receipt.get("schema_version") != DOWNLOAD_SCHEMA_VERSION:
        errors.append("download schema changed")
    if not _utc(receipt.get("generated_at")):
        errors.append("download generated_at is invalid")
    if not _sha(receipt.get("protocol_git_commit"), 40):
        errors.append("download protocol commit is invalid")
    if receipt.get("source_manifest") != SOURCE_MANIFEST_PATH:
        errors.append("download source manifest changed")
    if not _sha(receipt.get("source_manifest_sha256"), 64):
        errors.append("download manifest SHA is invalid")
    if receipt.get("request_policy") != ("exactly_one_get_per_frozen_object_no_retry_no_replacement"):
        errors.append("download request policy changed")
    if receipt.get("zip_opened") is not False or receipt.get("csv_rows_opened") is not False:
        errors.append("download claims content access before retention")
    objects = receipt.get("objects")
    specs = cast(list[dict[str, object]], manifest["objects"])
    if not isinstance(objects, list) or len(objects) != len(specs):
        errors.append("download object count changed")
        return tuple(errors)
    for index, (raw, spec) in enumerate(zip(objects, specs, strict=True)):
        if not isinstance(raw, Mapping):
            errors.append(f"download objects[{index}] is invalid")
            continue
        if raw.get("object_id") != spec["object_id"]:
            errors.append(f"download objects[{index}] order changed")
        if raw.get("request_count") != 1 or raw.get("http_status") != 200:
            errors.append(f"download objects[{index}] request failed")
        if raw.get("expected_bytes") != spec["expected_bytes"]:
            errors.append(f"download objects[{index}] expected bytes changed")
        if raw.get("observed_bytes") != spec["expected_bytes"]:
            errors.append(f"download objects[{index}] observed bytes mismatch")
        if not _sha(raw.get("sha256"), 64):
            errors.append(f"download objects[{index}] SHA is invalid")
        if raw.get("download_pass") is not True:
            errors.append(f"download objects[{index}] did not pass")
    if receipt.get("pass") is not True:
        errors.append("download overall decision did not pass")
    return tuple(errors)


def validate_retention_receipt(
    retention: Mapping[str, object],
    download: Mapping[str, object],
    manifest: Mapping[str, object],
) -> tuple[str, ...]:
    """Validate R2 size/SHA retention before parsing."""

    errors: list[str] = []
    if retention.get("schema_version") != RETENTION_SCHEMA_VERSION:
        errors.append("retention schema changed")
    if not _utc(retention.get("generated_at")):
        errors.append("retention generated_at is invalid")
    if retention.get("protocol_git_commit") != download.get("protocol_git_commit"):
        errors.append("retention protocol commit differs from download")
    if retention.get("source_manifest") != SOURCE_MANIFEST_PATH:
        errors.append("retention source manifest changed")
    if retention.get("source_manifest_sha256") != download.get("source_manifest_sha256"):
        errors.append("retention manifest SHA differs from download")
    if retention.get("zip_opened") is not False or retention.get("csv_rows_opened") is not False:
        errors.append("retention claims content access before verification")
    contract = cast(dict[str, object], manifest["retention_contract"])
    if retention.get("bucket") != contract["bucket"]:
        errors.append("retention bucket changed")
    if retention.get("prefix") != contract["prefix"]:
        errors.append("retention prefix changed")
    retained = retention.get("objects")
    downloaded = download.get("objects")
    specs = cast(list[dict[str, object]], manifest["objects"])
    if not isinstance(retained, list) or not isinstance(downloaded, list):
        errors.append("retention objects are invalid")
        return tuple(errors)
    if len(retained) != len(specs) or len(downloaded) != len(specs):
        errors.append("retention object count changed")
        return tuple(errors)
    for index, (raw_retained, raw_downloaded, spec) in enumerate(
        zip(retained, downloaded, specs, strict=True)
    ):
        if not isinstance(raw_retained, Mapping) or not isinstance(raw_downloaded, Mapping):
            errors.append(f"retention objects[{index}] is invalid")
            continue
        if raw_retained.get("object_id") != spec["object_id"]:
            errors.append(f"retention objects[{index}] order changed")
        if raw_retained.get("r2_key") != spec["r2_key"]:
            errors.append(f"retention objects[{index}] R2 key changed")
        if raw_retained.get("observed_bytes") != raw_downloaded.get("observed_bytes"):
            errors.append(f"retention objects[{index}] local bytes changed")
        if raw_retained.get("sha256") != raw_downloaded.get("sha256"):
            errors.append(f"retention objects[{index}] local SHA changed")
        if raw_retained.get("remote_content_length") != raw_downloaded.get("observed_bytes"):
            errors.append(f"retention objects[{index}] remote bytes mismatch")
        if raw_retained.get("remote_metadata_sha256") != raw_downloaded.get("sha256"):
            errors.append(f"retention objects[{index}] remote SHA mismatch")
        if raw_retained.get("verified") is not True:
            errors.append(f"retention objects[{index}] is not verified")
    if retention.get("all_verified") is not True:
        errors.append("retention overall decision did not pass")
    return tuple(errors)


def verify_local_downloads(
    raw_root: str | Path,
    download: Mapping[str, object],
    manifest: Mapping[str, object],
) -> tuple[str, ...]:
    """Verify local E1b inputs against the receipt."""

    errors: list[str] = []
    root = Path(raw_root)
    objects = cast(list[dict[str, object]], download["objects"])
    specs = cast(list[dict[str, object]], manifest["objects"])
    for index, (item, spec) in enumerate(zip(objects, specs, strict=True)):
        path = root / cast(str, spec["expected_filename"])
        if not path.is_file():
            errors.append(f"local object {index} is absent")
            continue
        if path.stat().st_size != item["observed_bytes"]:
            errors.append(f"local object {index} byte count changed")
        elif file_sha256(path) != item["sha256"]:
            errors.append(f"local object {index} SHA changed")
    return tuple(errors)


def _canonical_timestamp(value: str) -> str | None:
    parsed = parse_aemo_timestamp(value)
    return parsed.isoformat(timespec="microseconds") if parsed is not None else None


def _integer_equals(value: str, expected: int) -> bool:
    try:
        return Decimal(value.strip()) == expected
    except InvalidOperation:
        return False


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _duplicates(rows: Sequence[Mapping[str, str]], fields: Sequence[str]) -> int:
    seen: set[tuple[str, ...]] = set()
    count = 0
    for row in rows:
        key = tuple(row.get(field, "") for field in fields)
        if key in seen:
            count += 1
        else:
            seen.add(key)
    return count


def _period_key(row: Mapping[str, str]) -> tuple[str, str, str, str, str] | None:
    interval = _canonical_timestamp(row.get("INTERVAL_DATETIME", ""))
    bid_date = _canonical_timestamp(row.get("BIDSETTLEMENTDATE", ""))
    offer = _canonical_timestamp(row.get("OFFERDATE", ""))
    if interval is None or bid_date is None or offer is None:
        return None
    return interval, row.get("DUID", ""), row.get("BIDTYPE", ""), bid_date, offer


def _tracker_key(row: Mapping[str, str]) -> tuple[str, str, str, str, str] | None:
    interval = _canonical_timestamp(row.get("SETTLEMENTDATE", ""))
    bid_date = _canonical_timestamp(row.get("BIDSETTLEMENTDATE", ""))
    offer = _canonical_timestamp(row.get("BIDOFFERDATE", ""))
    if interval is None or bid_date is None or offer is None:
        return None
    return interval, row.get("DUID", ""), row.get("BIDTYPE", ""), bid_date, offer


def _timestamp_counts(
    tables: Mapping[str, Sequence[Mapping[str, str]]],
) -> tuple[int, int]:
    fields: dict[str, tuple[tuple[str, bool], ...]] = {
        "BIDDAYOFFER_D": (
            ("SETTLEMENTDATE", True),
            ("BIDSETTLEMENTDATE", True),
            ("OFFERDATE", True),
        ),
        "BIDPEROFFER_D": (
            ("SETTLEMENTDATE", True),
            ("INTERVAL_DATETIME", True),
            ("BIDSETTLEMENTDATE", True),
            ("OFFERDATE", True),
        ),
        "DISPATCHOFFERTRK": (
            ("SETTLEMENTDATE", True),
            ("BIDSETTLEMENTDATE", False),
            ("BIDOFFERDATE", False),
        ),
        "DISPATCHLOAD": (("SETTLEMENTDATE", True),),
        "DUDETAILSUMMARY": (("START_DATE", True), ("END_DATE", True)),
    }
    parsed_count = 0
    expected_count = 0
    for role, specifications in fields.items():
        for row in tables[role]:
            for field, required in specifications:
                value = row.get(field, "")
                if not required and not value.strip():
                    continue
                expected_count += 1
                if parse_aemo_timestamp(value) is not None:
                    parsed_count += 1
    return parsed_count, expected_count


def summarize_bundle_confirmation(
    tables: Mapping[str, Sequence[Mapping[str, str]]],
    archive_observations: Sequence[Mapping[str, object]],
    manifest: Mapping[str, object],
    download: Mapping[str, object],
    retention: Mapping[str, object],
    *,
    source_manifest_sha256: str,
    analyzer_git_commit: str,
    generated_at: str,
) -> dict[str, object]:
    """Evaluate the frozen fresh-day relation and supporting data-plane gates."""

    contracts = table_contracts_by_role(manifest)
    counts = {role: len(tables[role]) for role in contracts}
    total_target_rows = sum(counts.values())
    total_data_rows = sum(cast(int, item["total_data_rows"]) for item in archive_observations)
    archive_pass_count = sum(item.get("pass") is True for item in archive_observations)
    crc_pass_count = sum(item.get("zip_crc_pass") is True for item in archive_observations)
    exact_byte_count = sum(item.get("exact_byte_match") is True for item in archive_observations)
    header_pass_count = sum(
        header.get("header_present") is True and not header.get("missing_required_fields")
        for item in archive_observations
        for header in cast(list[dict[str, object]], item["headers"])
    )
    nonempty_count = sum(count > 0 for count in counts.values())

    timestamp_parsed, timestamp_expected = _timestamp_counts(tables)
    timestamp_rate = _rate(timestamp_parsed, timestamp_expected)
    duplicates_by_role = {
        role: _duplicates(tables[role], cast(list[str], contract["primary_key"]))
        for role, contract in contracts.items()
    }
    duplicate_count = sum(duplicates_by_role.values())

    selected_date = date.fromisoformat(SAMPLE_DATE)
    bid_rows = list(tables["BIDDAYOFFER_D"]) + list(tables["BIDPEROFFER_D"])
    bid_date_matches = sum(
        parsed is not None and parsed.date() == selected_date
        for row in bid_rows
        if (parsed := parse_aemo_timestamp(row.get("SETTLEMENTDATE", ""))) is not None
    )
    bid_date_rate = _rate(bid_date_matches, len(bid_rows))

    time_contract = cast(dict[str, object], manifest["time_contract"])
    window_start = datetime.fromisoformat(cast(str, time_contract["dispatch_interval_start_inclusive"]))
    window_end = datetime.fromisoformat(cast(str, time_contract["dispatch_interval_end_inclusive"]))
    interval_fields = {
        "BIDPEROFFER_D": "INTERVAL_DATETIME",
        "DISPATCHOFFERTRK": "SETTLEMENTDATE",
        "DISPATCHLOAD": "SETTLEMENTDATE",
    }
    window_expected = 0
    window_matches = 0
    for role, field in interval_fields.items():
        for row in tables[role]:
            window_expected += 1
            timestamp = parse_aemo_timestamp(row.get(field, ""))
            if timestamp is not None and window_start <= timestamp <= window_end:
                window_matches += 1
    window_rate = _rate(window_matches, window_expected)

    day_keys = {
        (
            row.get("SETTLEMENTDATE", ""),
            row.get("DUID", ""),
            row.get("BIDTYPE", ""),
            row.get("DIRECTION", ""),
        )
        for row in tables["BIDDAYOFFER_D"]
    }
    period_parent_matches = sum(
        (
            row.get("SETTLEMENTDATE", ""),
            row.get("DUID", ""),
            row.get("BIDTYPE", ""),
            row.get("DIRECTION", ""),
        )
        in day_keys
        for row in tables["BIDPEROFFER_D"]
    )
    period_parent_rate = _rate(period_parent_matches, counts["BIDPEROFFER_D"])

    period_index: defaultdict[tuple[str, str, str, str, str], list[str]] = defaultdict(list)
    for row in tables["BIDPEROFFER_D"]:
        key = _period_key(row)
        if key is not None:
            period_index[key].append(row.get("DIRECTION", "") or "<EMPTY>")

    identity_intervals: defaultdict[str, list[tuple[datetime, datetime, str]]] = defaultdict(list)
    for row in tables["DUDETAILSUMMARY"]:
        start = parse_aemo_timestamp(row.get("START_DATE", ""))
        end = parse_aemo_timestamp(row.get("END_DATE", ""))
        if start is not None and end is not None and start < end:
            identity_intervals[row.get("DUID", "")].append((start, end, row.get("DISPATCHTYPE", "")))

    relation_contract = cast(dict[str, object], manifest["relation_contract"])
    allowed_cardinalities = set(cast(list[int], relation_contract["allowed_candidate_cardinalities"]))
    allowed_single = set(cast(list[str], relation_contract["allowed_single_directions"]))
    exact_pair = set(cast(list[str], relation_contract["exact_pair_directions"]))
    required_pair_identity = cast(str, relation_contract["exact_pair_identity_dispatchtype"])
    allowed_pair_bidtypes = set(cast(list[str], relation_contract["allowed_pair_bidtypes"]))
    tracker_count = counts["DISPATCHOFFERTRK"]
    reference_count = 0
    relation_match_count = 0
    candidate_cardinality: Counter[str] = Counter()
    direction_sets: Counter[str] = Counter()
    pair_bidtypes: Counter[str] = Counter()
    pair_count = 0
    pair_duids: set[str] = set()
    invalid_cardinality = 0
    invalid_single_direction = 0
    invalid_pair_direction = 0
    duplicate_pair_direction = 0
    invalid_pair_identity = 0
    invalid_pair_bidtype = 0
    tracker_keys: list[tuple[str, str]] = []

    for row in tables["DISPATCHOFFERTRK"]:
        key = _tracker_key(row)
        if key is None:
            candidate_cardinality["INVALID_REFERENCE"] += 1
            invalid_cardinality += 1
            continue
        reference_count += 1
        tracker_keys.append((key[0], key[1]))
        directions = period_index.get(key, [])
        cardinality = len(directions)
        candidate_cardinality[str(cardinality)] += 1
        direction_sets["|".join(sorted(set(directions))) if directions else "<NONE>"] += 1
        if cardinality > 0:
            relation_match_count += 1
        if cardinality not in allowed_cardinalities:
            invalid_cardinality += 1
            continue
        if cardinality == 1:
            if directions[0] not in allowed_single:
                invalid_single_direction += 1
            continue
        pair_count += 1
        pair_duids.add(key[1])
        pair_bidtypes[row.get("BIDTYPE", "") or "<EMPTY>"] += 1
        if set(directions) != exact_pair:
            invalid_pair_direction += 1
        if len(directions) != len(set(directions)):
            duplicate_pair_direction += 1
        if row.get("BIDTYPE", "") not in allowed_pair_bidtypes:
            invalid_pair_bidtype += 1
        interval = datetime.fromisoformat(key[0])
        identities = [
            dispatch_type
            for start, end, dispatch_type in identity_intervals.get(key[1], [])
            if start <= interval < end
        ]
        if len(identities) != 1 or identities[0] != required_pair_identity:
            invalid_pair_identity += 1

    reference_rate = _rate(reference_count, tracker_count)
    relation_coverage_rate = _rate(relation_match_count, tracker_count)

    physical_dispatch_keys = {
        (dispatch_timestamp, row.get("DUID", ""))
        for row in tables["DISPATCHLOAD"]
        if _integer_equals(row.get("RUNNO", ""), 1)
        and _integer_equals(row.get("INTERVENTION", ""), 0)
        and (dispatch_timestamp := _canonical_timestamp(row.get("SETTLEMENTDATE", ""))) is not None
    }
    tracker_dispatch_matches = sum(key in physical_dispatch_keys for key in tracker_keys)
    tracker_dispatch_rate = _rate(tracker_dispatch_matches, len(tracker_keys))

    identity_matches = 0
    identity_overlaps = 0
    for interval_text, duid in physical_dispatch_keys:
        timestamp = datetime.fromisoformat(interval_text)
        matches = sum(start <= timestamp < end for start, end, _ in identity_intervals.get(duid, []))
        if matches:
            identity_matches += 1
        if matches > 1:
            identity_overlaps += 1
    identity_rate = _rate(identity_matches, len(physical_dispatch_keys))

    downloaded = cast(list[dict[str, object]], download["objects"])
    retained = cast(list[dict[str, object]], retention["objects"])
    download_pass_count = sum(item.get("download_pass") is True for item in downloaded)
    r2_verified_count = sum(item.get("verified") is True for item in retained)
    thresholds = cast(dict[str, object], manifest["gates"])
    gates: dict[str, bool] = {
        "exact_download_object_count": download_pass_count == cast(int, thresholds["required_object_count"]),
        "exact_archive_byte_count": exact_byte_count == cast(int, thresholds["required_object_count"]),
        "r2_retention_verified": r2_verified_count == cast(int, thresholds["required_r2_verified_count"]),
        "archive_crc": crc_pass_count == cast(int, thresholds["required_archive_crc_count"]),
        "archive_parse": archive_pass_count == cast(int, thresholds["required_object_count"]),
        "required_headers": header_pass_count == cast(int, thresholds["required_table_count"]),
        "required_tables_nonempty": nonempty_count == cast(int, thresholds["required_nonempty_table_count"]),
        "row_cap": total_data_rows <= cast(int, thresholds["maximum_total_data_rows"]),
        "timestamp_parse": timestamp_rate >= cast(float, thresholds["timestamp_parse_rate_min"]),
        "primary_key_uniqueness": duplicate_count <= cast(int, thresholds["primary_key_duplicate_count_max"]),
        "bid_market_date": bid_date_rate >= cast(float, thresholds["bid_market_date_rate_min"]),
        "dispatch_market_window": window_rate >= cast(float, thresholds["dispatch_window_rate_min"]),
        "bid_period_parent_join": period_parent_rate
        >= cast(float, thresholds["bid_period_parent_match_rate_min"]),
        "tracker_offer_reference": reference_rate
        >= cast(float, thresholds["tracker_offer_reference_rate_min"]),
        "tracker_relation_coverage": relation_coverage_rate
        >= cast(float, thresholds["tracker_relation_coverage_rate_min"]),
        "tracker_dispatch_join": tracker_dispatch_rate
        >= cast(float, thresholds["tracker_dispatch_match_rate_min"]),
        "dispatch_identity_join": identity_rate
        >= cast(float, thresholds["dispatch_identity_match_rate_min"]),
        "identity_nonoverlap": identity_overlaps
        <= cast(int, thresholds["dispatch_identity_overlap_count_max"]),
        "candidate_cardinality": invalid_cardinality
        <= cast(int, thresholds["invalid_candidate_cardinality_count_max"]),
        "single_direction_domain": invalid_single_direction
        <= cast(int, thresholds["invalid_single_direction_count_max"]),
        "pair_direction_exactness": invalid_pair_direction
        <= cast(int, thresholds["invalid_pair_direction_count_max"]),
        "pair_direction_uniqueness": duplicate_pair_direction
        <= cast(int, thresholds["duplicate_pair_direction_count_max"]),
        "pair_effective_identity": invalid_pair_identity
        <= cast(int, thresholds["invalid_pair_identity_count_max"]),
        "pair_bidtype_domain": invalid_pair_bidtype
        <= cast(int, thresholds["invalid_pair_bidtype_count_max"]),
        "pair_nonempty": pair_count >= cast(int, thresholds["minimum_pair_count"]),
    }
    overall_pass = all(gates.values())
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "generated_at": generated_at,
        "analyzer_git_commit": analyzer_git_commit,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": source_manifest_sha256,
        "sample_date": SAMPLE_DATE,
        "scientific_role": manifest["scientific_role"],
        "decision": (
            "PASS_FRESH_SET_VALUED_OFFER_BRIDGE_CONFIRMATION"
            if overall_pass
            else "FAIL_FRESH_SET_VALUED_OFFER_BRIDGE_CONFIRMATION"
        ),
        "pass": overall_pass,
        "raw": {
            "download_pass_count": download_pass_count,
            "r2_verified_count": r2_verified_count,
            "archive_parse_pass_count": archive_pass_count,
            "archive_crc_pass_count": crc_pass_count,
            "exact_archive_byte_count": exact_byte_count,
            "compressed_bytes": sum(cast(int, item["observed_bytes"]) for item in downloaded),
            "archive_sha256": {cast(str, item["object_id"]): item["sha256"] for item in downloaded},
        },
        "tables": {
            "row_counts": counts,
            "total_target_rows": total_target_rows,
            "total_data_rows_all_tables": total_data_rows,
            "required_header_pass_count": header_pass_count,
            "primary_key_duplicates": duplicates_by_role,
            "primary_key_duplicate_count": duplicate_count,
        },
        "timestamps": {
            "parsed_count": timestamp_parsed,
            "expected_count": timestamp_expected,
            "parse_rate": timestamp_rate,
            "bid_market_date_match_count": bid_date_matches,
            "bid_market_date_expected_count": len(bid_rows),
            "bid_market_date_rate": bid_date_rate,
            "dispatch_window_match_count": window_matches,
            "dispatch_window_expected_count": window_expected,
            "dispatch_window_rate": window_rate,
        },
        "base_joins": {
            "bid_period_parent_match_count": period_parent_matches,
            "bid_period_parent_expected_count": counts["BIDPEROFFER_D"],
            "bid_period_parent_match_rate": period_parent_rate,
            "tracker_dispatch_match_count": tracker_dispatch_matches,
            "tracker_dispatch_expected_count": len(tracker_keys),
            "tracker_dispatch_match_rate": tracker_dispatch_rate,
            "dispatch_identity_match_count": identity_matches,
            "dispatch_identity_expected_count": len(physical_dispatch_keys),
            "dispatch_identity_match_rate": identity_rate,
            "dispatch_identity_overlap_count": identity_overlaps,
        },
        "relation": {
            "tracker_count": tracker_count,
            "valid_offer_reference_count": reference_count,
            "offer_reference_rate": reference_rate,
            "relation_match_count": relation_match_count,
            "relation_coverage_rate": relation_coverage_rate,
            "candidate_cardinality": dict(sorted(candidate_cardinality.items())),
            "direction_sets": dict(sorted(direction_sets.items())),
            "pair_count": pair_count,
            "pair_unique_duid_count": len(pair_duids),
            "pair_bidtypes": dict(sorted(pair_bidtypes.items())),
            "invalid_candidate_cardinality_count": invalid_cardinality,
            "invalid_single_direction_count": invalid_single_direction,
            "invalid_pair_direction_count": invalid_pair_direction,
            "duplicate_pair_direction_count": duplicate_pair_direction,
            "invalid_pair_identity_count": invalid_pair_identity,
            "invalid_pair_bidtype_count": invalid_pair_bidtype,
            "realized_dispatch_used_to_select_leg": False,
        },
        "archive_observations": [dict(item) for item in archive_observations],
        "gates": gates,
        "claim_boundary": {
            "validates": "fresh-day modern set-valued applied-offer relation",
            "does_not_validate": [
                "raw submissions or rejected actions",
                "historical table-version equivalence",
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
