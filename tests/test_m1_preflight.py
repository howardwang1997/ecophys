from __future__ import annotations

from pathlib import Path

import pytest

from ecomd.training.m1_preflight import M1Preflight, validate_m1_training_phase


def _preflight() -> M1Preflight:
    return M1Preflight(
        protocol={},
        data_manifest={},
        execution_metadata={"run_id": "test"},
        first_segment_stop_after_iter=300,
        final_iter=600,
        expected_parameter_count=36_541,
    )


def test_m1_first_segment_requires_exact_boundary_and_no_checkpoint(tmp_path: Path) -> None:
    checkpoint = tmp_path / "checkpoint.pt"
    assert validate_m1_training_phase(
        _preflight(), checkpoint_path=checkpoint, resume=False, stop_after_iter=300
    ) == (0, 300)
    with pytest.raises(ValueError, match="stop must equal 300"):
        validate_m1_training_phase(
            _preflight(), checkpoint_path=checkpoint, resume=False, stop_after_iter=299
        )
    checkpoint.touch()
    with pytest.raises(FileExistsError, match="refuses an existing checkpoint"):
        validate_m1_training_phase(
            _preflight(), checkpoint_path=checkpoint, resume=False, stop_after_iter=300
        )


def test_m1_resume_requires_checkpoint_and_runs_to_final(tmp_path: Path) -> None:
    checkpoint = tmp_path / "checkpoint.pt"
    with pytest.raises(FileNotFoundError, match="requires an existing checkpoint"):
        validate_m1_training_phase(
            _preflight(), checkpoint_path=checkpoint, resume=True, stop_after_iter=None
        )
    checkpoint.touch()
    assert validate_m1_training_phase(
        _preflight(), checkpoint_path=checkpoint, resume=True, stop_after_iter=None
    ) == (300, 600)
    with pytest.raises(ValueError, match="run to the frozen final iteration"):
        validate_m1_training_phase(
            _preflight(), checkpoint_path=checkpoint, resume=True, stop_after_iter=500
        )
