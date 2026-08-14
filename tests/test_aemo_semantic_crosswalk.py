from __future__ import annotations

import copy
from pathlib import Path

from ecomd.research.aemo_semantic_crosswalk import (
    RESOLVED_STAGE,
    load_crosswalk,
    resolve_head_metadata,
    validate_crosswalk,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/manifests/aemo_semantic_crosswalk_v2.yaml"


def test_frozen_aemo_crosswalk_is_valid_and_unresolved() -> None:
    manifest = load_crosswalk(MANIFEST)

    assert validate_crosswalk(manifest) == ()
    assert manifest["gates"]["row_access_before_heldout_header_commit_allowed"] is False
    assert manifest["gates"]["gpu_allowed"] is False
    assert len(manifest["objects"]) == 10


def _observations(manifest: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            "object_id": item["object_id"],
            "http_status": 200,
            "content_length": 1000 + index,
            "etag": None,
            "last_modified": "Fri, 14 Aug 2026 00:00:00 GMT",
        }
        for index, item in enumerate(manifest["objects"])
    ]


def test_exact_ordered_head_resolution_produces_valid_manifest() -> None:
    manifest = load_crosswalk(MANIFEST)

    resolved = resolve_head_metadata(
        manifest,
        _observations(manifest),
        source_manifest_sha256="a" * 64,
        resolved_at="2026-08-14T08:30:00Z",
        resolver_git_commit="b" * 40,
    )

    assert validate_crosswalk(resolved) == ()
    assert resolved["stage"] == RESOLVED_STAGE
    assert resolved["resolution"]["all_head_requests_pass"] is True


def test_out_of_order_head_resolution_is_rejected() -> None:
    manifest = load_crosswalk(MANIFEST)
    observations = _observations(manifest)
    observations[0], observations[1] = observations[1], observations[0]

    try:
        resolve_head_metadata(
            manifest,
            observations,
            source_manifest_sha256="a" * 64,
            resolved_at="2026-08-14T08:30:00Z",
            resolver_git_commit="b" * 40,
        )
    except ValueError as error:
        assert "out of order" in str(error)
    else:
        raise AssertionError("out-of-order HEAD observations were accepted")


def test_discovery_month_cannot_be_reused_as_validation() -> None:
    manifest = load_crosswalk(MANIFEST)
    invalid = copy.deepcopy(manifest)
    invalid["selection"]["validation_samples"][0]["month"] = "2021-03"

    assert "held-out validation samples changed" in validate_crosswalk(invalid)


def test_crosswalk_sources_must_be_declared_required_fields() -> None:
    manifest = load_crosswalk(MANIFEST)
    invalid = copy.deepcopy(manifest)
    invalid["crosswalk"][0]["regimes"]["legacy_public_dvd"]["field_map"]["duid"]["sources"] = ["UNDECLARED"]

    assert any("sources is invalid" in error for error in validate_crosswalk(invalid))
