#!/usr/bin/env python3
"""Prove a 64 KiB AEMO-style ZIP prefix budget without network access."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import cast
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ecomd.research.aemo_prefix_headers import audit_prefix_response

RANGE_BYTES = 65_536
SYNTHETIC_MEMBER = "PUBLIC_DVD_DISPATCHOFFERTRK_PREFIX_BUDGET_STRESS_202112010000.CSV"
PRIOR_SUMMARIES = {
    "experiments/v14_aemo_prefix_header_audit/artifacts/summary.json": (
        "d1d0be04b398584d44d0f495760c627760a75d07fceb2bccc2f041a9a8c6ce21"
    ),
    "experiments/v14_aemo_source_contract_audit/artifacts/summary.json": (
        "e7abbcf530d8d75a0f69c5885dfcbdc74a84f743ff9a7134754e6e8b28d8a239"
    ),
}


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def build_synthetic_archive() -> bytes:
    """Build a deterministic large deflated CSV with its information row first."""

    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["C", "SYNTHETIC", "PREFIX_BUDGET", "1", "OFFLINE_ONLY"])
    fields = [f"FIELD_{index:03d}" for index in range(128)]
    writer.writerow(["I", "DISPATCH", "OFFERTRK", "1", *fields])
    for row_index in range(4_096):
        values = [
            hashlib.sha256(f"{row_index}:{column}".encode()).hexdigest()
            for column in range(4)
        ]
        writer.writerow(["D", "DISPATCH", "OFFERTRK", "1", *values])

    archive_buffer = io.BytesIO()
    member = ZipInfo(SYNTHETIC_MEMBER, date_time=(2020, 1, 1, 0, 0, 0))
    member.compress_type = ZIP_DEFLATED
    member.create_system = 3
    member.external_attr = 0o600 << 16
    with ZipFile(archive_buffer, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        archive.writestr(member, buffer.getvalue(), compress_type=ZIP_DEFLATED, compresslevel=6)
    return archive_buffer.getvalue()


def _prior_prefix_metrics(root: Path) -> dict[str, object]:
    offsets: list[int] = []
    pre_header_rows: list[int] = []
    field_counts: list[int] = []
    object_count = 0
    sources: list[dict[str, object]] = []
    for relative_path, expected_sha256 in PRIOR_SUMMARIES.items():
        path = root / relative_path
        payload = path.read_bytes()
        observed_sha256 = _sha256(payload)
        if observed_sha256 != expected_sha256:
            raise RuntimeError(f"preserved summary hash changed: {relative_path}")
        summary = cast(Mapping[str, object], json.loads(payload))
        audits = cast(list[Mapping[str, object]], summary["audits"])
        for audit in audits:
            parsed = cast(Mapping[str, object], audit["parsed"])
            offsets.append(cast(int, parsed["data_offset"]))
            pre_header_rows.append(cast(int, parsed["non_data_rows_before_header"]))
            field_counts.append(len(cast(list[str], parsed["header_fields"])))
        object_count += len(audits)
        sources.append(
            {
                "path": relative_path,
                "sha256": observed_sha256,
                "object_count": len(audits),
            }
        )
    return {
        "sources": sources,
        "object_count": object_count,
        "maximum_data_offset": max(offsets),
        "maximum_non_data_rows_before_header": max(pre_header_rows),
        "maximum_header_field_count": max(field_counts),
    }


def build_prefix_budget_proof(root: Path = ROOT) -> dict[str, object]:
    """Return deterministic evidence for the repaired compressed-prefix budget."""

    prior = _prior_prefix_metrics(root)
    archive = build_synthetic_archive()
    if len(archive) <= RANGE_BYTES:
        raise RuntimeError("synthetic archive does not exceed the proposed prefix budget")
    prefix = archive[:RANGE_BYTES]
    content_range = f"bytes 0-{RANGE_BYTES - 1}/{len(archive)}"
    spec: dict[str, object] = {
        "object_id": "synthetic-prefix-budget-proof",
        "sample_label": "offline-only",
        "month": "2021-12",
        "mechanism_phase": "A3_5MS_PLUS_WDR",
        "observation_phase": "O4_V51_CLUSTERED_RELEASE",
        "logical_role": "DISPATCHOFFERTRK",
        "url": "synthetic://offline-only",
        "expected_member": SYNTHETIC_MEMBER,
        "expected_package": "DISPATCH",
        "expected_table": "OFFERTRK",
        "expected_version": "1",
        "required_fields": ["FIELD_000", "FIELD_127"],
    }
    audit = audit_prefix_response(
        spec,
        http_status=206,
        content=prefix,
        response_headers={"Content-Range": content_range},
        retrieved_at="offline-deterministic-proof",
        transport_error=None,
    )
    parsed = cast(Mapping[str, object], audit["parsed"])
    stress_dominates_observed_shape = (
        cast(int, parsed["data_offset"]) >= cast(int, prior["maximum_data_offset"])
        and cast(int, parsed["non_data_rows_before_header"])
        >= cast(int, prior["maximum_non_data_rows_before_header"])
        and len(cast(list[str], parsed["header_fields"]))
        >= cast(int, prior["maximum_header_field_count"])
    )
    passed = (
        audit["header_contract_pass"] is True
        and audit["zip_prefix_parse"] is True
        and audit["data_row_opened"] is False
        and audit["full_archive_downloaded"] is False
        and len(prefix) == RANGE_BYTES
        and stress_dominates_observed_shape
    )
    return {
        "schema_version": "ecophys-aemo-prefix-budget-proof/v1",
        "decision": "PASS_64_KIB_PREFIX_BUDGET" if passed else "FAIL_64_KIB_PREFIX_BUDGET",
        "pass": passed,
        "range_bytes": RANGE_BYTES,
        "request_header": f"Range: bytes=0-{RANGE_BYTES - 1}",
        "prior_prefix_metadata": prior,
        "synthetic_stress": {
            "member": SYNTHETIC_MEMBER,
            "archive_bytes": len(archive),
            "archive_sha256": _sha256(archive),
            "prefix_bytes": len(prefix),
            "prefix_sha256": _sha256(prefix),
            "content_range": content_range,
            "data_offset": parsed["data_offset"],
            "non_data_rows_before_header": parsed["non_data_rows_before_header"],
            "header_field_count": len(cast(list[str], parsed["header_fields"])),
            "zip_prefix_parse": audit["zip_prefix_parse"],
            "header_contract_pass": audit["header_contract_pass"],
            "data_row_opened": audit["data_row_opened"],
            "full_archive_downloaded": audit["full_archive_downloaded"],
        },
        "stress_dominates_observed_shape": stress_dominates_observed_shape,
        "network_used": False,
        "gpu_used": False,
        "paid_data_used": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT
        / "experiments/v14_aemo_source_contract_repair/artifacts/prefix_budget_proof.json",
    )
    arguments = parser.parse_args()
    if arguments.output.exists():
        raise FileExistsError(arguments.output)
    proof = build_prefix_budget_proof()
    if proof["pass"] is not True:
        raise RuntimeError("64 KiB offline prefix proof failed")
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(proof, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
