from __future__ import annotations

import json
import sys
import tarfile
from pathlib import Path

import pytest
import torch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from constraint_iclr_common import sha256_file  # noqa: E402
from package_constraint_iclr_pdebench_unet_shard import (  # noqa: E402
    package_completed_shard,
    validate_completed_shard,
)


def _completed_v100a_shard(root: Path) -> Path:
    checkpoint_dir = (
        root
        / "experiments/constraint_attribution_iclr/pdebench/"
        "unet_factorial_checkpoints_v100a_20260902"
    )
    checkpoint_dir.mkdir(parents=True)
    records: list[dict[str, object]] = []
    for seed in range(7000, 7015):
        checkpoints: dict[str, dict[str, object]] = {}
        for mechanism in ("free", "free_res", "hard_abs", "hard"):
            run_id = f"{seed}-{mechanism}"
            path = checkpoint_dir / f"{run_id}.pt"
            torch.save(
                {
                    "schema_version": "constraint-iclr-pdebench-v1",
                    "run_id": run_id,
                    "completed_epochs": 200,
                    "model_state_dict": {"weight": torch.tensor([seed])},
                },
                path,
            )
            checkpoints[mechanism] = {
                "path": str(path.relative_to(root)),
                "completed_epochs": 200,
            }
            records.append(
                {
                    "stage": "factorial_confirmation",
                    "benchmark_id": "pdebench_advection_beta0.4_unet_factorial_v1",
                    "seed": seed,
                    "mechanism": mechanism,
                    "run_id": run_id,
                    "checkpoint": checkpoints[mechanism],
                }
            )
        records.append(
            {
                "stage": "factorial_confirmation",
                "benchmark_id": "pdebench_advection_beta0.4_unet_factorial_v1",
                "seed": seed,
                "mechanism": "projection",
                "run_id": f"{seed}-projection",
                "checkpoint": checkpoints["free"],
            }
        )
    input_path = (
        root
        / "experiments/constraint_attribution_iclr/pdebench/"
        "unet_factorial_v100a_20260902.jsonl"
    )
    input_path.write_text(
        "".join(json.dumps(record) + "\n" for record in records), encoding="utf-8"
    )
    return input_path


def test_unet_shard_package_contains_exact_final_checkpoints(
    tmp_path: Path,
) -> None:
    input_path = _completed_v100a_shard(tmp_path)
    archive_path = tmp_path / "unet-v100a.tar.gz"
    manifest_path = (
        tmp_path
        / "experiments/constraint_attribution_iclr/pdebench/"
        "unet_v100a_transfer_manifest_20260903.json"
    )
    sidecar_path = tmp_path / "unet-v100a.tar.gz.sha256"
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


def test_unet_shard_validation_rejects_wrong_checkpoint_run_id(
    tmp_path: Path,
) -> None:
    input_path = _completed_v100a_shard(tmp_path)
    _, checkpoints = validate_completed_shard(
        root=tmp_path, input_path=input_path, worker_id="v100a"
    )
    changed = tmp_path / checkpoints[0]["path"]
    payload = torch.load(changed, map_location="cpu", weights_only=False)
    payload["run_id"] = "wrong"
    torch.save(payload, changed)
    with pytest.raises(RuntimeError, match="run ID mismatch"):
        validate_completed_shard(
            root=tmp_path, input_path=input_path, worker_id="v100a"
        )
