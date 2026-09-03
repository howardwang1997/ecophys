from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.build_paper_d_supplement import (
    CubeBlock,
    build_manifest,
    create_archive,
    sha256_file,
    validate_cube_block,
)


def _write_jsonl(path: Path, count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps({"run_id": index}) + "\n" for index in range(count)),
        encoding="utf-8",
    )


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
