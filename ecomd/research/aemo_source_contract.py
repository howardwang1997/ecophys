"""Channel-scoped AEMO source contracts for clustered reform boundaries."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

import yaml

from ecomd.research.aemo_prefix_headers import audit_prefix_response

SCHEMA_VERSION = "ecophys-aemo-source-contract/v1"
SUMMARY_SCHEMA_VERSION = "ecophys-aemo-source-contract-summary/v1"
PARENT_COMMIT = "2cfe229afc182a67907d38bec53c1a741f276988"
RANGE_BYTES = 262_144
MAX_UNCOMPRESSED_PREFIX = 65_536
DELIVERY_CHANNEL = "PUBLIC_MONTHLY_ARCHIVE"
ARCHIVE_FAMILY = "MMSDM_Historical_Data_SQLLoader/PUBLIC_DVD"
EXPECTED_ROLES = (
    "BIDDAYOFFER",
    "BIDPEROFFER",
    "DISPATCHOFFERTRK",
    "DISPATCHLOAD",
    "DUDETAILSUMMARY",
)
EXCLUDED_MONTHS = (
    "2020-09",
    "2021-03",
    "2021-09",
    "2022-04",
    "2025-01",
    "2025-07",
)
EXPECTED_SAMPLES = {
    "pre-bridge-prefix-2021-02": (
        "2021-02",
        "A0_30_MINUTE_ONLY",
        "O0_LEGACY_REPORTS",
        "PRE_REPORTING_BRIDGE",
    ),
    "post-v51-prefix-2021-11": (
        "2021-11",
        "A3_5MS_PLUS_WDR",
        "O4_V51_CLUSTERED_RELEASE",
        "POST_V51_WDR",
    ),
}
EXPECTED_HEADERS = {
    ("pre-bridge-prefix-2021-02", "BIDDAYOFFER"): ("OFFER", "BIDDAYOFFER", "2"),
    ("pre-bridge-prefix-2021-02", "BIDPEROFFER"): ("OFFER", "BIDPEROFFER", "1"),
    ("pre-bridge-prefix-2021-02", "DISPATCHOFFERTRK"): (
        "DISPATCH",
        "OFFERTRK",
        "1",
    ),
    ("pre-bridge-prefix-2021-02", "DISPATCHLOAD"): (
        "DISPATCH",
        "UNIT_SOLUTION",
        "2",
    ),
    ("pre-bridge-prefix-2021-02", "DUDETAILSUMMARY"): (
        "PARTICIPANT_REGISTRATION",
        "DUDETAILSUMMARY",
        "4",
    ),
    ("post-v51-prefix-2021-11", "BIDDAYOFFER"): ("BIDS", "BIDDAYOFFER", "1"),
    ("post-v51-prefix-2021-11", "BIDPEROFFER"): ("BIDS", "BIDOFFERPERIOD", "1"),
    ("post-v51-prefix-2021-11", "DISPATCHOFFERTRK"): (
        "DISPATCH",
        "OFFERTRK",
        "1",
    ),
    ("post-v51-prefix-2021-11", "DISPATCHLOAD"): (
        "DISPATCH",
        "UNIT_SOLUTION",
        "3",
    ),
    ("post-v51-prefix-2021-11", "DUDETAILSUMMARY"): (
        "PARTICIPANT_REGISTRATION",
        "DUDETAILSUMMARY",
        "5",
    ),
}
EXPECTED_REQUIRED_FIELDS = {
    ("pre-bridge-prefix-2021-02", "BIDDAYOFFER"): (
        "SETTLEMENTDATE",
        "DUID",
        "BIDTYPE",
        "PARTICIPANTID",
        "OFFERDATE",
        "VERSIONNO",
        "ENTRYTYPE",
        "PRICEBAND1",
        "PRICEBAND10",
    ),
    ("pre-bridge-prefix-2021-02", "BIDPEROFFER"): (
        "SETTLEMENTDATE",
        "OFFERDATE",
        "PERIODID",
        "VERSIONNO",
        "DUID",
        "BIDTYPE",
        "MAXAVAIL",
        "ROCUP",
        "ROCDOWN",
        "BANDAVAIL1",
        "BANDAVAIL10",
    ),
    ("pre-bridge-prefix-2021-02", "DISPATCHOFFERTRK"): (
        "SETTLEMENTDATE",
        "DUID",
        "BIDTYPE",
        "BIDSETTLEMENTDATE",
        "BIDOFFERDATE",
    ),
    ("pre-bridge-prefix-2021-02", "DISPATCHLOAD"): (
        "SETTLEMENTDATE",
        "RUNNO",
        "DUID",
        "INTERVENTION",
        "INITIALMW",
        "TOTALCLEARED",
        "AVAILABILITY",
    ),
    ("pre-bridge-prefix-2021-02", "DUDETAILSUMMARY"): (
        "DUID",
        "START_DATE",
        "END_DATE",
        "DISPATCHTYPE",
        "REGIONID",
        "PARTICIPANTID",
        "SCHEDULE_TYPE",
    ),
    ("post-v51-prefix-2021-11", "BIDDAYOFFER"): (
        "SETTLEMENTDATE",
        "DUID",
        "BIDTYPE",
        "PARTICIPANTID",
        "OFFERDATE",
        "VERSIONNO",
        "ENTRYTYPE",
        "REBID_EVENT_TIME",
        "REFERENCE_ID",
        "PRICEBAND1",
        "PRICEBAND10",
    ),
    ("post-v51-prefix-2021-11", "BIDPEROFFER"): (
        "TRADINGDATE",
        "OFFERDATETIME",
        "PERIODID",
        "DUID",
        "BIDTYPE",
        "MAXAVAIL",
        "RAMPUPRATE",
        "RAMPDOWNRATE",
        "BANDAVAIL1",
        "BANDAVAIL10",
    ),
    ("post-v51-prefix-2021-11", "DISPATCHOFFERTRK"): (
        "SETTLEMENTDATE",
        "DUID",
        "BIDTYPE",
        "BIDSETTLEMENTDATE",
        "BIDOFFERDATE",
    ),
    ("post-v51-prefix-2021-11", "DISPATCHLOAD"): (
        "SETTLEMENTDATE",
        "RUNNO",
        "DUID",
        "INTERVENTION",
        "INITIALMW",
        "TOTALCLEARED",
        "AVAILABILITY",
        "DISPATCHMODETIME",
    ),
    ("post-v51-prefix-2021-11", "DUDETAILSUMMARY"): (
        "DUID",
        "START_DATE",
        "END_DATE",
        "DISPATCHTYPE",
        "DISPATCHSUBTYPE",
        "REGIONID",
        "PARTICIPANTID",
        "SCHEDULE_TYPE",
    ),
}
EXPECTED_FORBIDDEN_FIELDS = {
    ("pre-bridge-prefix-2021-02", "DISPATCHLOAD"): ("DISPATCHMODETIME",),
    ("pre-bridge-prefix-2021-02", "DUDETAILSUMMARY"): ("DISPATCHSUBTYPE",),
}
EXPECTED_SENSITIVITY_CLASS = {
    "BIDDAYOFFER": "DELIVERY_CHANNEL_VERSION",
    "BIDPEROFFER": "DELIVERY_CHANNEL_VERSION",
    "DISPATCHOFFERTRK": "STABLE_APPLIED_OFFER_LINK",
    "DISPATCHLOAD": "FAST_START_STATE_OBSERVABILITY",
    "DUDETAILSUMMARY": "WDR_IDENTITY_OBSERVABILITY",
}
EXPECTED_SELECTION = {
    "rule": "nearest_complete_calendar_month_outside_each_boundary",
    "anchors": [
        {
            "sample_label": "pre-bridge-prefix-2021-02",
            "boundary": "2021-03-08",
            "side": "before",
            "selected_month": "2021-02",
        },
        {
            "sample_label": "post-v51-prefix-2021-11",
            "boundary": "2021-10-24",
            "side": "after",
            "selected_month": "2021-11",
        },
    ],
    "excluded_months": list(EXCLUDED_MONTHS),
    "no_replacement": True,
    "selected_zip_prefix_or_csv_previously_accessed_before_freeze": False,
    "mixed_boundary_month_allowed": False,
}
EXPECTED_TIMELINE = {
    "mechanism_intervals": [
        {
            "phase": "A0_30_MINUTE_ONLY",
            "start": None,
            "end_exclusive": "2021-04-01",
        },
        {
            "phase": "A1_DUAL_INTERFACE_EQUALITY_CONSTRAINED",
            "start": "2021-04-01",
            "end_exclusive": "2021-10-01",
        },
        {
            "phase": "A2_5MS_ONLY_PRE_WDR",
            "start": "2021-10-01",
            "end_exclusive": "2021-10-24",
        },
        {
            "phase": "A3_5MS_PLUS_WDR",
            "start": "2021-10-24",
            "end_exclusive": None,
        },
    ],
    "observation_intervals": [
        {
            "phase": "O0_LEGACY_REPORTS",
            "start": None,
            "end_exclusive": "2021-03-08",
        },
        {
            "phase": "O1_COMPATIBILITY_BRIDGE",
            "start": "2021-03-08",
            "end_exclusive": "2021-04-01",
        },
        {
            "phase": "O2_DUAL_REPORT_GENERATIONS",
            "start": "2021-04-01",
            "end_exclusive": "2021-10-01",
        },
        {
            "phase": "O3_5MS_PRE_V51",
            "start": "2021-10-01",
            "end_exclusive": "2021-10-24",
        },
        {
            "phase": "O4_V51_CLUSTERED_RELEASE",
            "start": "2021-10-24",
            "end_exclusive": None,
        },
    ],
}
EXPECTED_PROVENANCE_LIMITS = {
    "participant_bid_interface_during_transition": "PARTIALLY_IDENTIFIED",
    "public_report_shape_as_interface_proxy_allowed": False,
    "submission_method_visibility": "PRIVATE_DECLARED_BUT_UNPOPULATED",
    "value_based_interface_imputation_allowed": False,
}
ROOT_KEYS = frozenset(
    {
        "schema_version",
        "sample_id",
        "frozen_at",
        "parent_commit",
        "scientific_role",
        "prior_evidence",
        "selection",
        "timeline",
        "provenance_limits",
        "range_contract",
        "objects",
        "gates",
        "outputs",
    }
)
OBJECT_KEYS = frozenset(
    {
        "object_id",
        "sample_label",
        "month",
        "mechanism_phase",
        "observation_phase",
        "version_basis",
        "delivery_channel",
        "archive_family",
        "archive_file_id",
        "logical_role",
        "sensitivity_class",
        "url",
        "expected_member",
        "expected_package",
        "expected_table",
        "expected_version",
        "required_fields",
        "forbidden_fields",
    }
)


def load_source_contract_manifest(path: str | Path) -> dict[str, object]:
    """Load an AEMO source-contract manifest at an object-typed boundary."""

    payload: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("AEMO source-contract manifest root must be a mapping")
    return cast(dict[str, object], payload)


def manifest_sha256(path: str | Path) -> str:
    """Hash exact source-contract manifest bytes."""

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def adjacent_complete_month(boundary: str, side: str) -> str:
    """Select the nearest complete calendar month strictly outside a boundary month."""

    parsed = date.fromisoformat(boundary)
    first_of_boundary_month = parsed.replace(day=1)
    if side == "before":
        selected = first_of_boundary_month - timedelta(days=1)
    elif side == "after":
        if first_of_boundary_month.month == 12:
            selected = date(first_of_boundary_month.year + 1, 1, 1)
        else:
            selected = date(first_of_boundary_month.year, first_of_boundary_month.month + 1, 1)
    else:
        raise ValueError("side must be before or after")
    return selected.strftime("%Y-%m")


def _text(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _utc(value: object) -> bool:
    text = _text(value)
    if text is None or not text.endswith("Z"):
        return False
    try:
        parsed = datetime.fromisoformat(text.removesuffix("Z") + "+00:00")
    except ValueError:
        return False
    return parsed.tzinfo == UTC


def _sha(value: object, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in "0123456789abcdef" for character in value)
    )


def validate_source_contract_manifest(manifest: Mapping[str, object]) -> tuple[str, ...]:
    """Validate the frozen timeline, channel identity, samples and header contracts."""

    errors: list[str] = []
    if set(manifest) != ROOT_KEYS:
        errors.append("root keys changed")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if manifest.get("sample_id") != "aemo-channel-clustered-reform-prefix-validation-v1":
        errors.append("sample_id changed")
    if manifest.get("scientific_role") != "development_only_channel_scoped_prefix_validation":
        errors.append("scientific_role changed")
    if not _utc(manifest.get("frozen_at")):
        errors.append("frozen_at must be UTC")
    if manifest.get("parent_commit") != PARENT_COMMIT:
        errors.append("parent_commit changed")
    prior = manifest.get("prior_evidence")
    if not isinstance(prior, Mapping) or dict(prior) != {
        "preserved_failure_commit": "9f9e7e657e8616b77150d7f8b48e46aeb422e0e7",
        "preserved_failure_decision": "FAIL_VERSION_CLOCK_CONTRACT",
        "preserved_failure_summary_sha256": "d1d0be04b398584d44d0f495760c627760a75d07fceb2bccc2f041a9a8c6ce21",
        "official_classification_commit": PARENT_COMMIT,
        "official_classification_decision": "ASYNC_MECHANISM_OBSERVATION_TOPOLOGY_REQUIRED",
    }:
        errors.append("prior evidence changed")
    selection = manifest.get("selection")
    if not isinstance(selection, Mapping) or dict(selection) != EXPECTED_SELECTION:
        errors.append("selection changed")
    else:
        anchors = cast(list[dict[str, object]], selection["anchors"])
        for index, anchor in enumerate(anchors):
            boundary = cast(str, anchor["boundary"])
            side = cast(str, anchor["side"])
            selected = cast(str, anchor["selected_month"])
            if adjacent_complete_month(boundary, side) != selected:
                errors.append(f"selection anchor {index} is not mechanically derived")
            if selected in EXCLUDED_MONTHS or selected == "2021-10":
                errors.append(f"selection anchor {index} uses an excluded or mixed month")
    if manifest.get("timeline") != EXPECTED_TIMELINE:
        errors.append("timeline changed")
    if manifest.get("provenance_limits") != EXPECTED_PROVENANCE_LIMITS:
        errors.append("provenance limits changed")
    range_contract = manifest.get("range_contract")
    if not isinstance(range_contract, Mapping) or dict(range_contract) != {
        "request_header": "Range: bytes=0-262143",
        "required_http_status": 206,
        "maximum_response_bytes": RANGE_BYTES,
        "maximum_uncompressed_prefix_bytes": MAX_UNCOMPRESSED_PREFIX,
        "full_download_fallback_allowed": False,
        "data_row_before_information_header_allowed": False,
    }:
        errors.append("range contract changed")

    objects = manifest.get("objects")
    observed_pairs: list[tuple[str, str]] = []
    if not isinstance(objects, list) or len(objects) != 10:
        errors.append("objects must contain exactly ten entries")
    else:
        identifiers: set[str] = set()
        for index, raw_object in enumerate(objects):
            if not isinstance(raw_object, Mapping):
                errors.append(f"objects[{index}] must be a mapping")
                continue
            item = cast(Mapping[str, object], raw_object)
            if set(item) != OBJECT_KEYS:
                errors.append(f"objects[{index}] has unexpected keys")
            object_id = _text(item.get("object_id"))
            if object_id is None or object_id in identifiers:
                errors.append(f"objects[{index}].object_id must be unique")
            else:
                identifiers.add(object_id)
            sample = _text(item.get("sample_label"))
            role = _text(item.get("logical_role"))
            if sample is None or sample not in EXPECTED_SAMPLES:
                errors.append(f"objects[{index}].sample_label is invalid")
                continue
            if role is None or role not in EXPECTED_ROLES:
                errors.append(f"objects[{index}].logical_role is invalid")
                continue
            observed_pairs.append((sample, role))
            month, mechanism, observation, version_basis = EXPECTED_SAMPLES[sample]
            expected_values = {
                "month": month,
                "mechanism_phase": mechanism,
                "observation_phase": observation,
                "version_basis": version_basis,
                "delivery_channel": DELIVERY_CHANNEL,
                "archive_family": ARCHIVE_FAMILY,
                "archive_file_id": f"PUBLIC_DVD_{role}",
                "sensitivity_class": EXPECTED_SENSITIVITY_CLASS[role],
            }
            for key, expected in expected_values.items():
                if item.get(key) != expected:
                    errors.append(f"objects[{index}].{key} changed")
            package, table, version = EXPECTED_HEADERS[(sample, role)]
            if item.get("expected_package") != package:
                errors.append(f"objects[{index}].expected_package changed")
            if item.get("expected_table") != table:
                errors.append(f"objects[{index}].expected_table changed")
            if item.get("expected_version") != version:
                errors.append(f"objects[{index}].expected_version changed")
            required = item.get("required_fields")
            if required != list(EXPECTED_REQUIRED_FIELDS[(sample, role)]):
                errors.append(f"objects[{index}].required_fields changed")
            forbidden = item.get("forbidden_fields")
            if forbidden != list(EXPECTED_FORBIDDEN_FIELDS.get((sample, role), ())):
                errors.append(f"objects[{index}].forbidden_fields changed")
            compact_month = month.replace("-", "")
            expected_stem = f"PUBLIC_DVD_{role}_{compact_month}010000"
            url = _text(item.get("url"))
            if url is None:
                errors.append(f"objects[{index}].url is invalid")
            else:
                parsed = urlparse(url)
                if (
                    parsed.scheme != "https"
                    or parsed.hostname != "www.nemweb.com.au"
                    or parsed.query
                    or parsed.fragment
                    or f"/MMSDM_{month.replace('-', '_')}/" not in parsed.path
                    or "/MMSDM_Historical_Data_SQLLoader/DATA/" not in parsed.path
                    or not parsed.path.endswith(expected_stem + ".zip")
                ):
                    errors.append(f"objects[{index}].url is outside the frozen AEMO boundary")
            if item.get("expected_member") != expected_stem + ".CSV":
                errors.append(f"objects[{index}].expected_member changed")
        expected_pairs = {
            (sample, role) for sample in EXPECTED_SAMPLES for role in EXPECTED_ROLES
        }
        if set(observed_pairs) != expected_pairs or len(observed_pairs) != len(expected_pairs):
            errors.append("objects must cover every sample/role pair exactly once")

    gates = manifest.get("gates")
    if not isinstance(gates, Mapping) or dict(gates) != {
        "required_http_206": 10,
        "required_zip_prefix_parse": 10,
        "required_source_contract_pass": 10,
        "row_access_allowed_after_pass": False,
        "full_archive_download_allowed_after_pass": False,
        "gpu_allowed": False,
        "paid_data_allowed": False,
        "replacement_allowed": False,
    }:
        errors.append("gates changed")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, Mapping) or dict(outputs) != {
        "summary": "experiments/v14_aemo_source_contract_audit/artifacts/summary.json"
    }:
        errors.append("outputs changed")
    return tuple(errors)


def audit_source_contract_response(
    spec: Mapping[str, object],
    *,
    http_status: int | None,
    content: bytes,
    response_headers: Mapping[str, str],
    retrieved_at: str,
    transport_error: str | None,
) -> dict[str, object]:
    """Audit one prefix and enforce version-specific field absence as well as presence."""

    audit = audit_prefix_response(
        spec,
        http_status=http_status,
        content=content,
        response_headers=response_headers,
        retrieved_at=retrieved_at,
        transport_error=transport_error,
    )
    errors = cast(list[str], audit["errors"])
    parsed = audit.get("parsed")
    forbidden_present: list[str] = []
    if isinstance(parsed, Mapping):
        fields = set(cast(list[str], parsed["header_fields"]))
        forbidden = set(cast(list[str], spec["forbidden_fields"]))
        forbidden_present = sorted(fields & forbidden)
        if forbidden_present:
            errors.append(f"forbidden fields present: {forbidden_present}")
    source_contract_pass = not errors
    audit.update(
        {
            "delivery_channel": spec.get("delivery_channel"),
            "archive_family": spec.get("archive_family"),
            "archive_file_id": spec.get("archive_file_id"),
            "version_basis": spec.get("version_basis"),
            "sensitivity_class": spec.get("sensitivity_class"),
            "forbidden_fields_present": forbidden_present,
            "source_contract_pass": source_contract_pass,
            "header_contract_pass": source_contract_pass,
        }
    )
    return audit


def summarize_source_contract_audit(
    audits: Sequence[Mapping[str, object]],
    *,
    source_manifest: str,
    source_manifest_sha256: str,
    collector_git_commit: str,
    generated_at: str,
) -> dict[str, object]:
    """Summarize the exact ten-object channel-scoped source-contract audit."""

    expected = 10
    http_count = sum(item.get("http_status") == 206 for item in audits)
    parse_count = sum(item.get("zip_prefix_parse") is True for item in audits)
    contract_count = sum(item.get("source_contract_pass") is True for item in audits)
    no_forbidden_count = sum(not item.get("forbidden_fields_present") for item in audits)
    full_archive_downloaded = any(
        item.get("full_archive_downloaded") is True for item in audits
    )
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "source_manifest": source_manifest,
        "source_manifest_sha256": source_manifest_sha256,
        "collector_git_commit": collector_git_commit,
        "generated_at": generated_at,
        "expected_count": expected,
        "observed_count": len(audits),
        "http_206_count": http_count,
        "zip_prefix_parse_count": parse_count,
        "source_contract_pass_count": contract_count,
        "forbidden_field_absence_count": no_forbidden_count,
        "total_response_bytes": sum(
            cast(int, item.get("response_bytes", 0)) for item in audits
        ),
        "pass": (
            len(audits) == expected
            and http_count == expected
            and parse_count == expected
            and contract_count == expected
            and no_forbidden_count == expected
            and not full_archive_downloaded
        ),
        "audits": list(audits),
        "data_row_opened": False,
        "full_archive_downloaded": full_archive_downloaded,
        "gpu_used": False,
        "paid_data_used": False,
    }
