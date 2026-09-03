from __future__ import annotations

import json
import sys
import tarfile
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from constraint_iclr_common import sha256_file  # noqa: E402
from package_constraint_iclr_pdebench_swe_shard import (  # noqa: E402
    package_completed_shard,
    validate_completed_shard,
)


def _completed_v100a_shard(root: Path) -> Path:
    checkpoint_dir = (
        root
        / "experiments/constraint_attribution_iclr/pdebench/"
        "swe_factorial_checkpoints_20260902"
    )
    checkpoint_dir.mkdir(parents=True)
    records: list[dict[str, object]] = []
    for seed in range(6000, 6015):
        checkpoints: dict[str, dict[str, object]] = {}
        for mechanism in ("free", "free_res", "hard_abs", "hard"):
            path = checkpoint_dir / f"{seed}-{mechanism}.pt"
            path.write_bytes(f"{seed}:{mechanism}".encode())
            checkpoints[mechanism] = {
                "path": str(path.relative_to(root)),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
            records.append(
                {
                    "seed": seed,
                    "mechanism": mechanism,
                    "run_id": f"{seed}-{mechanism}",
                    "checkpoint": checkpoints[mechanism],
                }
            )
        records.append(
            {
                "seed": seed,
                "mechanism": "projection",
                "run_id": f"{seed}-projection",
                "checkpoint": checkpoints["free"],
            }
        )
    input_path = (
        root
        / "experiments/constraint_attribution_iclr/pdebench/"
        "swe_factorial_v100a_20260902.jsonl"
    )
    input_path.write_text(
        "".join(json.dumps(record) + "\n" for record in records), encoding="utf-8"
    )
    return input_path


def test_completed_shard_package_contains_only_exact_referenced_files(
    tmp_path: Path,
) -> None:
    input_path = _completed_v100a_shard(tmp_path)
    archive_path = tmp_path / "transfer.tar.gz"
    manifest_path = (
        tmp_path
        / "experiments/constraint_attribution_iclr/pdebench/"
        "swe_v100a_transfer_manifest_20260902.json"
    )
    sidecar_path = tmp_path / "transfer.tar.gz.sha256"
    result = package_completed_shard(
        root=tmp_path,
        input_path=input_path,
        worker_id="v100a",
        archive_path=archive_path,
        manifest_path=manifest_path,
        sidecar_path=sidecar_path,
    )
    assert result["record_count"] == 75
    assert result["checkpoint_count"] == 60
    assert result["archive"]["members"] == 62
    assert sidecar_path.read_text(encoding="utf-8").startswith(
        sha256_file(archive_path)
    )
    with tarfile.open(archive_path, "r:gz") as archive:
        names = archive.getnames()
    assert len(names) == 62
    assert str(input_path.relative_to(tmp_path)) in names
    assert str(manifest_path.relative_to(tmp_path)) in names
    assert not any("._" in name for name in names)


def test_completed_shard_validation_rejects_changed_checkpoint(tmp_path: Path) -> None:
    input_path = _completed_v100a_shard(tmp_path)
    _, checkpoints = validate_completed_shard(
        root=tmp_path, input_path=input_path, worker_id="v100a"
    )
    changed = tmp_path / checkpoints[0]["path"]
    changed.write_bytes(b"changed")
    with pytest.raises(RuntimeError, match="checkpoint byte count changed"):
        validate_completed_shard(
            root=tmp_path, input_path=input_path, worker_id="v100a"
        )
