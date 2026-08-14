from __future__ import annotations

import copy
from pathlib import Path

from ecomd.research.aemo_loader_controls import (
    audit_loader_control,
    load_loader_manifest,
    parse_loader_control,
    summarize_loader_audit,
    validate_loader_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/manifests/aemo_loader_control_audit_v3.yaml"


def _control(*, owner: str, target: str, filler: bool = False) -> str:
    trading_date = "TRADINGDATE FILLER" if filler else 'TRADINGDATE DATE "yyyy/mm/dd hh24:mi:ss"'
    return f"""-- Title: PUBLIC_DVD_BIDPEROFFER_202103.ctl
-- Special Instructions : 1. USER TO CONNECT AS {owner} owner
LOAD DATA
INFILE PUBLIC_DVD_BIDPEROFFER_202103010000.CSV
APPEND INTO TABLE {target}
WHEN (1:1) = 'D'
FIELDS TERMINATED BY ','
TRAILING NULLCOLS
(row_type FILLER,
report_type FILLER,
report_subtype FILLER,
report_version FILLER,
DUID CHAR(20),
{trading_date},
PERIODID FLOAT EXTERNAL)
-- End of Script
"""


def test_frozen_loader_manifest_is_valid_and_keeps_rows_locked() -> None:
    manifest = load_loader_manifest(MANIFEST)

    assert validate_loader_manifest(manifest) == ()
    assert manifest["gates"]["row_access_allowed_after_pass"] is False
    assert manifest["gates"]["archive_download_allowed_after_pass"] is False
    assert len(manifest["objects"]) == 6


def test_manifest_rejects_replacement_month() -> None:
    manifest = load_loader_manifest(MANIFEST)
    invalid = copy.deepcopy(manifest)
    invalid["objects"][0]["month"] = "2021-03"

    assert any("month changed" in error for error in validate_loader_manifest(invalid))


def test_parse_loader_control_preserves_target_and_filler_semantics() -> None:
    parsed = parse_loader_control(_control(owner="BIDPEROFFER", target="BIDPEROFFER", filler=True))

    assert parsed["owner"] == "BIDPEROFFER"
    assert parsed["target_table"] == "BIDPEROFFER"
    assert parsed["columns"][-3:] == ["DUID", "TRADINGDATE", "PERIODID"]
    assert parsed["filler_columns"] == [
        "ROW_TYPE",
        "REPORT_TYPE",
        "REPORT_SUBTYPE",
        "REPORT_VERSION",
        "TRADINGDATE",
    ]


def test_required_non_filler_column_cannot_be_silently_discarded() -> None:
    spec = {
        "object_id": "test",
        "sample_label": "test",
        "month": "2021-03",
        "mechanism_phase": "A0",
        "observation_phase": "O1",
        "logical_role": "BIDPEROFFER",
        "url": "https://www.nemweb.com.au/test.ctl",
        "expected_owner": "BIDPEROFFER",
        "expected_target_table": "BIDPEROFFER",
        "required_columns": ["DUID", "TRADINGDATE", "PERIODID"],
        "required_non_filler_columns": ["DUID", "TRADINGDATE", "PERIODID"],
    }

    audit = audit_loader_control(
        spec,
        http_status=200,
        content=_control(owner="BIDPEROFFER", target="BIDPEROFFER", filler=True).encode(),
        response_headers={},
        retrieved_at="2026-08-14T10:00:00Z",
        transport_error=None,
    )

    assert audit["parse_pass"] is True
    assert audit["contract_pass"] is False
    assert "required columns marked FILLER: ['TRADINGDATE']" in audit["errors"]


def test_summary_requires_all_six_contracts() -> None:
    audits = [
        {"http_status": 200, "parse_pass": True, "contract_pass": True} for _ in range(5)
    ]

    summary = summarize_loader_audit(
        audits,
        source_manifest="manifest.yaml",
        source_manifest_sha256="a" * 64,
        collector_git_commit="b" * 40,
        generated_at="2026-08-14T10:00:00Z",
    )

    assert summary["pass"] is False
    assert summary["row_opened"] is False
