"""Tests for the resumable experiment-127 V100 worker."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType


def _module() -> ModuleType:
    path = (
        Path(__file__).resolve().parents[1]
        / "experiments"
        / "127_workshop_claim_gates"
        / "v100_worker.py"
    )
    spec = importlib.util.spec_from_file_location("exp127_v100_worker", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_assignments_match_frozen_config_hashes() -> None:
    module = _module()
    repo_root = Path(__file__).resolve().parents[1]
    assignments = module._load_assignments(repo_root)
    assert len(assignments["jobs"]) == 10
    for job in assignments["jobs"]:
        assert module.sha256_file(repo_root / job["config"]) == job["config_sha256"]


def test_data_snapshot_validates() -> None:
    module = _module()
    repo_root = Path(__file__).resolve().parents[1]
    assets = module.validate_data_snapshot(repo_root)
    assert len(assets) == 5
    assert sum(asset["file_count"] for asset in assets) == 51


def test_rollout_completion_requires_files_and_count(tmp_path: Path) -> None:
    module = _module()
    trajectories = [tmp_path / "one.npz", tmp_path / "two.npz"]
    for path in trajectories:
        path.write_bytes(b"placeholder")
    merged = tmp_path / "inference_merged.json"
    merged.write_text(json.dumps({"n_total_rollouts": 2}))
    assert module._rollouts_complete(trajectories, merged, 2)
    merged.write_text(json.dumps({"n_total_rollouts": 1}))
    assert not module._rollouts_complete(trajectories, merged, 2)
