from __future__ import annotations

import json
import sys
import tarfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.build_paper_d_supplement import (  # noqa: E402
    BASE_RELEASE_FILES,
    CubeBlock,
    artifact_payload,
    build_manifest,
    collect_provenance_sources,
    create_archive,
    sha256_bytes,
    sha256_file,
    validate_cube_block,
    validate_no_bulk_payloads,
)


def _write_jsonl(path: Path, count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps({"run_id": index}) + "\n" for index in range(count)),
        encoding="utf-8",
    )


def test_release_contract_includes_its_builder_test() -> None:
    assert Path("tests/test_build_paper_d_supplement.py") in BASE_RELEASE_FILES


def test_cube_block_requires_exact_coverage_and_hash_bindings(tmp_path: Path) -> None:
    block = CubeBlock(
        name="test",
        benchmark_id="registered-test",
        mandatory_cells=12,
        primary_case="ood_test",
        primary_horizon=16,
        core_config="core-config.yaml",
        cube_config="cube-config.yaml",
        core_records="core.jsonl",
        core_analysis="core-analysis.json",
        checkpoint_lock="lock.json",
        cube_records="cube.jsonl",
        cube_analysis="cube-analysis.json",
    )
    _write_jsonl(tmp_path / block.core_records, 150)
    _write_jsonl(tmp_path / block.cube_records, 90)
    (tmp_path / block.core_analysis).write_text("{}\n", encoding="utf-8")
    (tmp_path / block.checkpoint_lock).write_text("{}\n", encoding="utf-8")
    (tmp_path / block.core_config).write_text("core: true\n", encoding="utf-8")
    (tmp_path / block.cube_config).write_text("cube: true\n", encoding="utf-8")
    core_analysis = {
        "benchmark_id": block.benchmark_id,
        "record_count": 150,
        "integrity_gates_passed": True,
        "input_sha256": sha256_file(tmp_path / block.core_records),
        "config_sha256": sha256_file(tmp_path / block.core_config),
    }
    (tmp_path / block.core_analysis).write_text(
        json.dumps(core_analysis), encoding="utf-8"
    )
    analysis = {
        "benchmark_id": block.benchmark_id,
        "core_record_count": 150,
        "derived_record_count": 90,
        "checkpoint_count": 120,
        "integrity_gates_passed": True,
        "core_input_sha256": sha256_file(tmp_path / block.core_records),
        "core_analysis_sha256": sha256_file(tmp_path / block.core_analysis),
        "checkpoint_lock_sha256": sha256_file(tmp_path / block.checkpoint_lock),
        "derived_input_sha256": sha256_file(tmp_path / block.cube_records),
        "config_sha256": sha256_file(tmp_path / block.cube_config),
        "all_cases": [{} for _ in range(12)],
        "primary": {"case": "ood_test", "horizon": 16},
    }
    (tmp_path / block.cube_analysis).write_text(
        json.dumps(analysis), encoding="utf-8"
    )
    validate_cube_block(tmp_path, block)

    (tmp_path / block.core_analysis).write_text('{"changed": true}\n', encoding="utf-8")
    with pytest.raises(RuntimeError, match="binding mismatch"):
        validate_cube_block(tmp_path, block)


def test_release_archive_is_deterministic_and_normalized(tmp_path: Path) -> None:
    payload = tmp_path / "payload.txt"
    payload.write_text("evidence\n", encoding="utf-8")
    paths = [Path("payload.txt")]
    manifest = build_manifest(tmp_path, paths)
    manifest_payload = (json.dumps(manifest, sort_keys=True) + "\n").encode()
    first = tmp_path / "first.tar.gz"
    second = tmp_path / "second.tar.gz"
    create_archive(tmp_path, paths, manifest_payload, first)
    create_archive(tmp_path, paths, manifest_payload, second)
    assert sha256_file(first) == sha256_file(second)
    assert first.with_suffix(first.suffix + ".sha256").is_file()


def test_provenance_sources_are_hash_checked(tmp_path: Path) -> None:
    source = tmp_path / "source.py"
    source.write_text("value = 1\n", encoding="utf-8")
    records = tmp_path / "records.jsonl"
    records.write_text(
        json.dumps(
            {
                "provenance": {
                    "source_sha256": {"source.py": sha256_file(source)}
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    assert collect_provenance_sources(tmp_path, [Path("records.jsonl")]) == {
        Path("source.py")
    }
    source.write_text("value = 2\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="absent from current files and snapshots"):
        collect_provenance_sources(tmp_path, [Path("records.jsonl")])

    historical = tmp_path / "historical.py"
    historical.write_text("value = 1\n", encoding="utf-8")
    snapshot = tmp_path / "snapshot.tar.gz"
    with tarfile.open(snapshot, "w:gz") as archive:
        archive.add(historical, arcname="source.py")
    assert collect_provenance_sources(
        tmp_path, [Path("records.jsonl")], [Path("snapshot.tar.gz")]
    ) == set()


def test_double_blind_redaction_preserves_provenance_binding(tmp_path: Path) -> None:
    operator = "test" + "operator"
    source_bytes = (
        f"worker: {operator}@100.64.0.9\n"
        f"root: /home/{operator}/registered-run\n"
    ).encode()
    source_digest = sha256_bytes(source_bytes)
    source = tmp_path / "decision.yaml"
    source.write_bytes(source_bytes)
    snapshot = tmp_path / "snapshot.tar.gz"
    with tarfile.open(snapshot, "w:gz") as archive:
        archive.add(source, arcname="decision.yaml")
    records = tmp_path / "records.jsonl"
    records.write_text(
        json.dumps(
            {
                "provenance": {
                    "source_sha256": {"decision.yaml": source_digest}
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )

    released_snapshot, redactions = artifact_payload(
        tmp_path, Path("snapshot.tar.gz")
    )
    assert redactions
    assert operator.encode() not in released_snapshot
    manifest = build_manifest(tmp_path, [Path("snapshot.tar.gz")])
    assert manifest["schema_version"].endswith("-v2")
    assert manifest["files"][0]["redacted_for_double_blind"] is True
    assert operator not in json.dumps(manifest)
    redactions = manifest["double_blind_redactions"]
    snapshot.write_bytes(released_snapshot)
    assert artifact_payload(tmp_path, Path("snapshot.tar.gz")) == (
        released_snapshot,
        [],
    )
    source.unlink()
    assert collect_provenance_sources(
        tmp_path,
        [Path("records.jsonl")],
        [Path("snapshot.tar.gz")],
        redactions,
    ) == set()


def test_private_network_addresses_are_anonymized(tmp_path: Path) -> None:
    address = "100." + "80.236.112"
    receipt = tmp_path / "receipt.yaml"
    receipt.write_text(
        f"worker: root@{address}\nendpoint: {address}\n", encoding="utf-8"
    )
    payload, redactions = artifact_payload(tmp_path, Path("receipt.yaml"))
    assert address.encode() not in payload
    assert payload.count(b"redacted-host") == 2
    assert redactions[0]["categories"] == ["private_network_address"]


def test_release_rejects_direct_and_nested_checkpoint_bytes(tmp_path: Path) -> None:
    checkpoint = tmp_path / "weights.pt"
    checkpoint.write_bytes(b"weights")
    with pytest.raises(RuntimeError, match="forbidden model/data payload"):
        validate_no_bulk_payloads(tmp_path, [Path("weights.pt")])

    snapshot = tmp_path / "snapshot.tar.gz"
    with tarfile.open(snapshot, "w:gz") as archive:
        archive.add(checkpoint, arcname="checkpoints/weights.pt")
    with pytest.raises(RuntimeError, match="nested artifact"):
        validate_no_bulk_payloads(tmp_path, [Path("snapshot.tar.gz")])


def test_license_holder_is_anonymized(tmp_path: Path) -> None:
    holder = "test" + "holder"
    license_path = tmp_path / "LICENSE"
    license_path.write_text(
        f"MIT License\n\nCopyright (c) 2026 {holder}\n", encoding="utf-8"
    )
    payload, redactions = artifact_payload(tmp_path, Path("LICENSE"))
    assert holder.encode() not in payload
    assert b"Copyright (c) 2026 Anonymous Authors" in payload
    assert redactions[0]["categories"] == ["copyright_holder"]


def test_package_author_is_anonymized(tmp_path: Path) -> None:
    author = "Test" + " Researcher"
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        f'[project]\nname = "example"\nauthors = [{{ name = "{author}" }}]\n',
        encoding="utf-8",
    )
    payload, redactions = artifact_payload(tmp_path, Path("pyproject.toml"))
    assert author.encode() not in payload
    assert b'authors = [{ name = "Anonymous Authors" }]' in payload
    assert redactions[0]["categories"] == ["package_author"]


def test_manifest_refuses_to_redact_frozen_numerical_records(tmp_path: Path) -> None:
    records = tmp_path / "records.jsonl"
    private_path = "/home/" + "private-user/run"
    records.write_text(json.dumps({"path": private_path}) + "\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="frozen numerical record"):
        build_manifest(tmp_path, [Path("records.jsonl")])
