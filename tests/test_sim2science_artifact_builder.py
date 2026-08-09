from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def _load_builder() -> ModuleType:
    root = Path(__file__).resolve().parents[1]
    path = (
        root
        / "papers/paper_a_methods/workshops/sim2science/artifact/build_anonymous_artifact.py"
    )
    spec = importlib.util.spec_from_file_location("sim2science_artifact_builder", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sanitize_text_removes_review_identifiers() -> None:
    builder = _load_builder()
    text = (
        "/Users/researcher/project "
        "22a6e41628d7cca7688ecdf5513e5a5bb014e462 "
        "GPU-91ba8f02-b2d7-7aad-1ce7-71b9680029ab"
    )
    sanitized = builder.sanitize_text(text)
    assert "/Users/" not in sanitized
    assert "22a6e41628d7cca7688ecdf5513e5a5bb014e462" not in sanitized
    assert "GPU-91ba8f02" not in sanitized


def test_sanitize_text_preserves_user_path_string_literal() -> None:
    builder = _load_builder()
    source = 'assert "/Users/" not in sanitized\n'
    sanitized = builder.sanitize_text(source)
    assert sanitized == source
    ast.parse(sanitized)


def test_builder_refuses_overwrite(tmp_path: Path) -> None:
    builder = _load_builder()
    output = tmp_path / "artifact"
    output.mkdir()
    with pytest.raises(FileExistsError):
        builder.build(output, derived_root=None, allow_incomplete=True)


def test_review_artifact_excludes_simulator_and_training_source() -> None:
    builder = _load_builder()
    relative = {
        path.relative_to(builder.REPO_ROOT).as_posix()
        for path in builder.source_paths()
    }
    assert "ecomd/eval/stationarity_gate.py" in relative
    assert "experiments/127_workshop_claim_gates/analyze_learned_results.py" in relative
    assert "ecomd/models/ecomd.py" not in relative
    assert "ecomd/physics/integrator.py" not in relative
    assert "ecomd/training/train_distributed.py" not in relative
    assert "experiments/127_workshop_claim_gates/v100_worker.py" not in relative


def test_derived_copy_keeps_trajectories_but_excludes_checkpoints(tmp_path: Path) -> None:
    builder = _load_builder()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    (source / "trajectory.npz").write_bytes(b"trajectory")
    (source / "result.json").write_text("{}")
    (source / "checkpoint.pt").write_bytes(b"checkpoint")
    builder.copy_derived(source, destination)
    assert (destination / "derived/trajectory.npz").is_file()
    assert (destination / "derived/result.json").is_file()
    assert not (destination / "derived/checkpoint.pt").exists()
