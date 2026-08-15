from __future__ import annotations

import copy
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

import pytest

import ecomd.research.aemo_row_conformance as row_conformance
from ecomd.research.aemo_bundle_stability_panel import (
    SOURCE_MANIFEST_PATH as ORIGINAL_MANIFEST_PATH,
)
from ecomd.research.aemo_bundle_stability_panel import (
    build_day_manifest,
    load_panel_manifest,
)
from ecomd.research.aemo_bundle_stability_repair import (
    EXPECTED_MANIFEST_SHA256,
    EXPECTED_OBJECT_COUNT,
    EXPECTED_STAGED_BYTES,
    MATERIALIZATION_SCHEMA_VERSION,
    SOURCE_MANIFEST_PATH,
    load_repair_manifest,
    manifest_sha256,
    validate_materialization_receipt,
    validate_original_provenance,
    validate_repair_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / SOURCE_MANIFEST_PATH


def _receipt(manifest: dict[str, object]) -> dict[str, object]:
    objects = cast(list[dict[str, object]], manifest["objects"])
    return {
        "schema_version": MATERIALIZATION_SCHEMA_VERSION,
        "generated_at": "2026-08-15T05:25:00Z",
        "protocol_git_commit": "a" * 40,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "aemo_source_request_count": 0,
        "objects": [
            {
                "object_id": item["object_id"],
                "r2_key": item["r2_key"],
                "observed_bytes": item["expected_bytes"],
                "sha256": item["sha256"],
                "remote_content_length": item["expected_bytes"],
                "remote_metadata_sha256": item["sha256"],
                "source_get_performed": False,
                "verified": True,
            }
            for item in objects
        ],
        "all_verified": True,
        "zip_opened": False,
        "csv_rows_opened": False,
    }


def test_repair_manifest_and_original_failure_chain_are_exact() -> None:
    manifest = load_repair_manifest(MANIFEST)

    assert manifest_sha256(MANIFEST) == EXPECTED_MANIFEST_SHA256
    assert validate_repair_manifest(manifest, source_sha256=manifest_sha256(MANIFEST)) == ()
    assert validate_original_provenance(ROOT) == ()
    objects = cast(list[dict[str, object]], manifest["objects"])
    assert len(objects) == EXPECTED_OBJECT_COUNT
    assert sum(cast(int, item["expected_bytes"]) for item in objects) == (EXPECTED_STAGED_BYTES)


def test_repair_manifest_rejects_any_scope_mutation() -> None:
    invalid = copy.deepcopy(load_repair_manifest(MANIFEST))
    cast(dict[str, object], invalid["repair_contract"])["new_aemo_source_request_count"] = 1

    errors = validate_repair_manifest(invalid, source_sha256=manifest_sha256(MANIFEST))

    assert "repair manifest content changed" in errors
    assert "repair boundary changed" in errors


def test_day_manifest_contains_only_the_missing_frozen_resource_cap() -> None:
    panel = load_panel_manifest(ROOT / ORIGINAL_MANIFEST_PATH)
    day = cast(list[dict[str, object]], panel["days"])[0]

    projected = build_day_manifest(panel, day)

    assert projected["resource_contract"] == {"maximum_total_data_rows": 4_000_000}


def test_parser_entry_preflight_reaches_all_three_archive_calls(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    panel = load_panel_manifest(ROOT / ORIGINAL_MANIFEST_PATH)
    day = cast(list[dict[str, object]], panel["days"])[0]
    projected = build_day_manifest(panel, day)
    calls: list[tuple[int, int]] = []

    def fake_parse(
        archive_path: str | Path,
        table_contracts: Sequence[Mapping[str, object]],
        *,
        maximum_uncompressed_bytes: int,
        maximum_data_rows: int,
    ) -> tuple[dict[str, list[dict[str, str]]], dict[str, object]]:
        del archive_path
        calls.append((maximum_uncompressed_bytes, maximum_data_rows))
        return (
            {cast(str, contract["logical_role"]): [] for contract in table_contracts},
            {
                "archive_bytes": 0,
                "total_data_rows": 0,
                "headers": [],
                "pass": True,
            },
        )

    monkeypatch.setattr(row_conformance, "parse_mmsdm_archive", fake_parse)

    tables, observations = row_conformance.parse_conformance_archives(tmp_path, projected)

    assert len(calls) == 3
    assert all(maximum_rows == 4_000_000 for _, maximum_rows in calls)
    assert set(tables) == {
        "BIDDAYOFFER_D",
        "BIDPEROFFER_D",
        "DISPATCHOFFERTRK",
        "DISPATCHLOAD",
        "DUDETAILSUMMARY",
    }
    assert len(observations) == 3


def test_materialization_receipt_requires_zero_source_requests() -> None:
    manifest = load_repair_manifest(MANIFEST)
    receipt = _receipt(manifest)

    assert validate_materialization_receipt(receipt, manifest) == ()
    receipt["aemo_source_request_count"] = 1

    assert "repair made a forbidden AEMO source request" in (
        validate_materialization_receipt(receipt, manifest)
    )


def test_repair_object_bytes_match_preserved_v1_retention() -> None:
    repair = load_repair_manifest(MANIFEST)
    original_receipt = cast(
        dict[str, object],
        json.loads(
            (ROOT / "experiments/v14_aemo_bundle_stability_panel/artifacts/retention_receipt.json").read_text(
                encoding="utf-8"
            )
        ),
    )
    repair_objects = {
        cast(str, item["object_id"]): (item["expected_bytes"], item["sha256"])
        for item in cast(list[dict[str, object]], repair["objects"])
    }
    original_objects = {
        cast(str, item["object_id"]): (item["observed_bytes"], item["sha256"])
        for item in cast(list[dict[str, object]], original_receipt["objects"])
    }

    assert repair_objects == original_objects
