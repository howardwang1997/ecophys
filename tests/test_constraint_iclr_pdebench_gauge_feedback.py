from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest
import torch
from torch import nn

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from analyze_constraint_iclr_pdebench import load_config, read_records  # noqa: E402
from analyze_constraint_iclr_pdebench_enforcement_cube import (  # noqa: E402
    canonical_object_sha256,
)
from analyze_constraint_iclr_pdebench_gauge_feedback import (  # noqa: E402
    _classify_ratio,
    analyze_gauge_feedback,
    validate_gauge_feedback_records,
)
from constraint_iclr_common import canonical_run_id, sha256_file  # noqa: E402
from constraint_iclr_gauge_identity import gauge_identity_gate  # noqa: E402
from run_constraint_iclr_pdebench_gauge_feedback import (  # noqa: E402
    _validate_parent_analysis_bindings,
    evaluate_gauge_feedback,
)

ROOT = Path(__file__).resolve().parents[1]


def _assert_source_or_attested_release_sha(path: Path, expected: str) -> None:
    current = sha256_file(path)
    if current == expected:
        return
    manifest_path = ROOT / "ARTIFACT_MANIFEST.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        relative = path.relative_to(ROOT).as_posix()
        for entry in manifest.get("double_blind_redactions", []):
            if (
                entry.get("archive_path") is None
                and entry.get("path") == relative
                and entry.get("source_sha256") == expected
                and entry.get("released_sha256") == current
            ):
                return
    assert current == expected


class _GaugeSensitiveTransition(nn.Module):
    def __init__(self, *, sensitive: bool) -> None:
        super().__init__()
        self.sensitive = sensitive

    def forward(self, history: torch.Tensor, grid: torch.Tensor) -> torch.Tensor:
        previous = history[..., -1]
        shape = grid - grid.mean()
        coefficient: torch.Tensor | float
        coefficient = previous.mean(dim=-1, keepdim=True) if self.sensitive else 1.0
        return previous + coefficient * shape + 0.5


def _toy_trajectories() -> torch.Tensor:
    grid = torch.linspace(0.0, 1.0, 8)
    base = torch.stack([grid + 0.1 * sample for sample in range(4)], dim=0)
    return torch.stack([base + 0.02 * time for time in range(5)], dim=1)


def test_direct_intervention_detects_only_gauge_to_q_transfer() -> None:
    trajectories = _toy_trajectories()
    grid = torch.linspace(0.0, 1.0, trajectories.shape[-1])
    sensitive = evaluate_gauge_feedback(
        model=_GaugeSensitiveTransition(sensitive=True),
        trajectories=trajectories,
        grid=grid,
        history=2,
        batch_size=2,
        device=torch.device("cpu"),
    )
    insensitive = evaluate_gauge_feedback(
        model=_GaugeSensitiveTransition(sensitive=False),
        trajectories=trajectories,
        grid=grid,
        history=2,
        batch_size=2,
        device=torch.device("cpu"),
    )
    assert sensitive["first_step_gauge_rmse"] > 0.0
    assert sensitive["feedback_rmse"] > 0.0
    assert sensitive["feedback_ratio"] > 0.0
    assert sensitive["step_one_q_identity_max_abs"] < 1e-6
    assert sensitive["step_one_gauge_nonconstant_max_abs"] < 1e-6
    assert sensitive["step_one_identity_scale_max_abs"] > 0.0
    assert insensitive["first_step_gauge_rmse"] > 0.0
    assert insensitive["feedback_rmse"] == pytest.approx(0.0, abs=1e-7)
    assert insensitive["feedback_ratio"] < 1e-6


def test_feedback_classification_uses_practical_threshold() -> None:
    assert _classify_ratio({"ci95": [0.11, 0.14], "ci90": [0.115, 0.135]}, 0.10) == "material_gauge_feedback"
    assert (
        _classify_ratio({"ci95": [0.01, 0.08], "ci90": [0.02, 0.07]}, 0.10)
        == "practically_negligible_gauge_feedback"
    )
    assert _classify_ratio({"ci95": [0.08, 0.13], "ci90": [0.09, 0.12]}, 0.10) == "unresolved"


def _validation_fixture() -> tuple[
    list[dict[str, Any]],
    dict[tuple[int, str], dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
]:
    config: dict[str, Any] = {
        "benchmark_id": "benchmark",
        "expected_git_head": "head",
        "expected_git_dirty": True,
        "active_config_path": "configs/gauge.yaml",
        "seeds": [1, 2],
        "dataset": {
            "expected_sha256": "dataset-sha",
            "lock_sha256": "data-lock-sha",
            "lock_path": "locks/data.json",
        },
        "cube": {"checkpoint_lock": "locks/checkpoints.json"},
        "evaluation": {"case_names": ["id", "ood"]},
        "gauge_feedback": {
            "schema_version": "gauge-v1",
            "stage": "gauge-stage",
            "parent_mechanisms": ["hard_abs", "hard"],
            "compatible_forward_maps": {
                "hard_abs": "free",
                "hard": "free_res",
            },
            "expected_records": 4,
            "identity_atol": 1e-6,
            "identity_roundoff_ulps": 2048,
            "identity_relative_baseline_atol": 0.001,
            "protocol_path": "protocol.md",
            "protocol_sha256": "protocol-sha",
            "decision_path": "decision.yaml",
            "decision_sha256": "decision-sha",
            "identity_runtime_amendment_path": "identity-amendment.md",
            "identity_runtime_amendment_sha256": "identity-amendment-sha",
            "identity_runtime_decision_path": "identity-decision.yaml",
            "identity_runtime_decision_sha256": "identity-decision-sha",
            "parent_core_records_sha256": "core-sha",
            "parent_core_analysis_sha256": "core-analysis-sha",
            "parent_cube_records_sha256": "cube-sha",
            "parent_cube_analysis_sha256": "cube-analysis-sha",
            "checkpoint_lock_sha256": "checkpoint-lock-sha",
        },
    }
    core: dict[tuple[int, str], dict[str, Any]] = {}
    checkpoints: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    source_hashes = {
        "configs/gauge.yaml": "config-sha",
        "protocol.md": "protocol-sha",
        "decision.yaml": "decision-sha",
        "identity-amendment.md": "identity-amendment-sha",
        "identity-decision.yaml": "identity-decision-sha",
        "locks/data.json": "data-lock-sha",
        "locks/checkpoints.json": "checkpoint-lock-sha",
    }
    for seed in config["seeds"]:
        for mechanism, forward_map in config["gauge_feedback"]["compatible_forward_maps"].items():
            parent = {
                "run_id": f"parent-{seed}-{mechanism}",
                "training_index_sha256": f"train-{seed}",
                "initialization_sha256": f"init-{seed}",
                "provenance": {"parent": f"{seed}-{mechanism}"},
            }
            core[(seed, mechanism)] = parent
            checkpoint = {
                "seed": seed,
                "mechanism": mechanism,
                "path": f"checkpoints/{seed}-{mechanism}.pt",
                "sha256": f"checkpoint-{seed}-{mechanism}",
                "bytes": 123,
            }
            checkpoints.append(checkpoint)
            expected_fields = {
                "schema_version": "gauge-v1",
                "stage": "gauge-stage",
                "benchmark_id": "benchmark",
                "dataset_sha256": "dataset-sha",
                "data_lock_sha256": "data-lock-sha",
                "gauge_protocol_sha256": "protocol-sha",
                "gauge_decision_sha256": "decision-sha",
                "gauge_identity_amendment_sha256": "identity-amendment-sha",
                "gauge_identity_decision_sha256": "identity-decision-sha",
                "core_records_sha256": "core-sha",
                "core_analysis_sha256": "core-analysis-sha",
                "cube_records_sha256": "cube-sha",
                "cube_analysis_sha256": "cube-analysis-sha",
                "checkpoint_lock_sha256": "checkpoint-lock-sha",
                "seed": seed,
                "mechanism": mechanism,
                "forward_map": forward_map,
                "parent_run_id": parent["run_id"],
            }
            metrics = {
                "feedback_rmse": 0.2,
                "projected_history_conserving_rmse": 1.0,
                "raw_history_conserving_rmse": 1.1,
                "feedback_ratio": 0.2,
                "first_step_gauge_rmse": 0.3,
                "step_one_q_identity_max_abs": 1e-8,
                "step_one_gauge_nonconstant_max_abs": 1e-8,
                "step_one_identity_scale_max_abs": 1.0,
            }
            records.append(
                {
                    **expected_fields,
                    "run_id": canonical_run_id(expected_fields),
                    "derived_from": parent["run_id"],
                    "training_index_sha256": parent["training_index_sha256"],
                    "initialization_sha256": parent["initialization_sha256"],
                    "parent": {
                        "run_id": parent["run_id"],
                        "mechanism": mechanism,
                        "checkpoint_path": checkpoint["path"],
                        "checkpoint_sha256": checkpoint["sha256"],
                        "checkpoint_bytes": checkpoint["bytes"],
                        "training_index_sha256": parent["training_index_sha256"],
                        "initialization_sha256": parent["initialization_sha256"],
                        "provenance_sha256": canonical_object_sha256(parent["provenance"]),
                    },
                    "compute": {
                        "optimization_runs": 0,
                        "examples_seen": 0,
                        "proxy": 0,
                        "training_runtime_seconds": 0.0,
                    },
                    "cases": {"id": dict(metrics), "ood": dict(metrics)},
                    "provenance": {
                        "git_head": "head",
                        "git_dirty": True,
                        "source_sha256": source_hashes,
                    },
                }
            )
    return records, core, {"checkpoints": checkpoints}, config


def test_gauge_feedback_record_integrity_rejects_ratio_rewrite() -> None:
    records, core, lock, config = _validation_fixture()
    validated = validate_gauge_feedback_records(records, core, lock, config)
    assert len(validated) == 4
    records[0]["cases"]["ood"]["feedback_ratio"] = 0.3
    with pytest.raises(RuntimeError, match="feedback ratio identity failed"):
        validate_gauge_feedback_records(records, core, lock, config)


def test_parent_analysis_binding_uses_emitted_cube_hash_fields() -> None:
    _validate_parent_analysis_bindings(
        core_analysis={
            "input_sha256": "core-sha",
            "integrity_gates_passed": True,
        },
        cube_analysis={
            "core_input_sha256": "core-sha",
            "derived_input_sha256": "cube-sha",
            "integrity_gates_passed": True,
        },
        core_records_sha256="core-sha",
        cube_records_sha256="cube-sha",
    )
    with pytest.raises(RuntimeError, match="parent cube analysis"):
        _validate_parent_analysis_bindings(
            core_analysis={
                "input_sha256": "core-sha",
                "integrity_gates_passed": True,
            },
            cube_analysis={
                "core_input_sha256": "core-sha",
                "derived_input_sha256": "rewritten-cube-sha",
                "integrity_gates_passed": True,
            },
            core_records_sha256="core-sha",
            cube_records_sha256="cube-sha",
        )


def test_gauge_identity_requires_roundoff_and_contamination_gates() -> None:
    config = {
        "identity_atol": 1e-6,
        "identity_roundoff_ulps": 2048,
        "identity_relative_baseline_atol": 0.001,
    }
    metrics = {
        "step_one_q_identity_max_abs": 1e-5,
        "step_one_gauge_nonconstant_max_abs": 8e-6,
        "step_one_identity_scale_max_abs": 100.0,
        "projected_history_conserving_rmse": 1.0,
    }
    tolerance, contamination, passed = gauge_identity_gate(metrics, config)
    assert tolerance > 1e-5
    assert contamination == pytest.approx(1e-5)
    assert passed is True
    metrics["projected_history_conserving_rmse"] = 0.001
    assert gauge_identity_gate(metrics, config)[2] is False


def test_frozen_gauge_protocol_and_decision_hashes() -> None:
    assert (
        sha256_file(
            ROOT / "papers/proposal/ecomd_constraint_attribution_iclr_gauge_feedback_freeze_2026-09-02.md"
        )
        == "04f712a51dfd22771c80bc22267f80a08eb9223e06eef86ce3acc007c679a7c5"
    )
    _assert_source_or_attested_release_sha(
        ROOT
        / "research/discovery/decisions/"
        "constraint_attribution_iclr_pdebench_gauge_feedback_20260902.yaml",
        "f973a419833aa12f7136ec7ba431a844d156e777003a563dd8d49003619549a0",
    )
    assert (
        sha256_file(
            ROOT / "papers/proposal/"
            "ecomd_constraint_attribution_iclr_gauge_identity_runtime_amendment_2026-09-02.md"
        )
        == "18b3c5bcf5858bd9605d989c2ea0fffbed0970d01d7469f17a6919fcf76cfc8a"
    )
    assert (
        sha256_file(
            ROOT / "research/discovery/decisions/"
            "constraint_attribution_iclr_gauge_identity_runtime_repair_20260902.yaml"
        )
        == "5e2cf3a2378f74a72426fb1926e65a52dc2a2040f8062ff06f9b21ea3d45dd73"
    )


def test_complete_analyzer_accepts_exact_real_parent_bindings() -> None:
    config_path = (
        ROOT / "configs/constraint_iclr/pdebench_advection_fno_gauge_feedback_identity_runtime_20260902.yaml"
    )
    config = load_config(config_path)
    config["gauge_feedback"]["bootstrap_draws"] = 200
    config["factorial_analysis"]["sign_flip_draws"] = 200
    gauge = config["gauge_feedback"]
    core_path = ROOT / config["output"]
    core_analysis_path = ROOT / config["cube"]["core_analysis"]
    cube_path = ROOT / gauge["parent_cube_records"]
    cube_analysis_path = ROOT / gauge["parent_cube_analysis"]
    lock_path = ROOT / config["cube"]["checkpoint_lock"]
    core_records = read_records(core_path)
    cube_records = read_records(cube_path)
    core = {
        (int(record["seed"]), str(record["mechanism"])): record
        for record in core_records
        if str(record["mechanism"]) in {"hard_abs", "hard"}
    }
    checkpoint_lock = json.loads(lock_path.read_text(encoding="utf-8"))
    checkpoints = {
        (int(entry["seed"]), str(entry["mechanism"])): entry for entry in checkpoint_lock["checkpoints"]
    }
    source_hashes = {
        config["active_config_path"]: "config-sha",
        gauge["protocol_path"]: gauge["protocol_sha256"],
        gauge["decision_path"]: gauge["decision_sha256"],
        gauge["identity_runtime_amendment_path"]: gauge["identity_runtime_amendment_sha256"],
        gauge["identity_runtime_decision_path"]: gauge["identity_runtime_decision_sha256"],
        config["dataset"]["lock_path"]: config["dataset"]["lock_sha256"],
        config["cube"]["checkpoint_lock"]: gauge["checkpoint_lock_sha256"],
    }
    records: list[dict[str, Any]] = []
    for seed in config["seeds"]:
        for mechanism, forward_map in gauge["compatible_forward_maps"].items():
            parent = core[(seed, mechanism)]
            checkpoint = checkpoints[(seed, mechanism)]
            identity = {
                "schema_version": gauge["schema_version"],
                "stage": gauge["stage"],
                "benchmark_id": config["benchmark_id"],
                "dataset_sha256": config["dataset"]["expected_sha256"],
                "data_lock_sha256": config["dataset"]["lock_sha256"],
                "gauge_protocol_sha256": gauge["protocol_sha256"],
                "gauge_decision_sha256": gauge["decision_sha256"],
                "gauge_identity_amendment_sha256": gauge["identity_runtime_amendment_sha256"],
                "gauge_identity_decision_sha256": gauge["identity_runtime_decision_sha256"],
                "core_records_sha256": gauge["parent_core_records_sha256"],
                "core_analysis_sha256": gauge["parent_core_analysis_sha256"],
                "cube_records_sha256": gauge["parent_cube_records_sha256"],
                "cube_analysis_sha256": gauge["parent_cube_analysis_sha256"],
                "checkpoint_lock_sha256": gauge["checkpoint_lock_sha256"],
                "seed": seed,
                "mechanism": mechanism,
                "forward_map": forward_map,
                "parent_run_id": parent["run_id"],
            }
            ratio = 0.20 + 0.001 * (seed - 3000) if mechanism == "hard_abs" else 0.16 + 0.0005 * (seed - 3000)
            metrics = {
                "feedback_rmse": ratio,
                "projected_history_conserving_rmse": 1.0,
                "raw_history_conserving_rmse": 1.0 + ratio,
                "feedback_ratio": ratio,
                "first_step_gauge_rmse": 0.5,
                "step_one_q_identity_max_abs": 1e-8,
                "step_one_gauge_nonconstant_max_abs": 1e-8,
                "step_one_identity_scale_max_abs": 1.0,
            }
            records.append(
                {
                    **identity,
                    "run_id": canonical_run_id(identity),
                    "derived_from": parent["run_id"],
                    "training_index_sha256": parent["training_index_sha256"],
                    "initialization_sha256": parent["initialization_sha256"],
                    "parent": {
                        "run_id": parent["run_id"],
                        "mechanism": mechanism,
                        "checkpoint_path": checkpoint["path"],
                        "checkpoint_sha256": checkpoint["sha256"],
                        "checkpoint_bytes": checkpoint["bytes"],
                        "training_index_sha256": parent["training_index_sha256"],
                        "initialization_sha256": parent["initialization_sha256"],
                        "provenance_sha256": canonical_object_sha256(parent["provenance"]),
                    },
                    "compute": {
                        "optimization_runs": 0,
                        "examples_seen": 0,
                        "proxy": 0,
                        "training_runtime_seconds": 0.0,
                    },
                    "cases": {case: dict(metrics) for case in config["evaluation"]["case_names"]},
                    "provenance": {
                        "git_head": config["expected_git_head"],
                        "git_dirty": config["expected_git_dirty"],
                        "source_sha256": source_hashes,
                    },
                }
            )
    analysis = analyze_gauge_feedback(
        records,
        core_records,
        cube_records,
        checkpoint_lock,
        config,
        core_records_sha256=sha256_file(core_path),
        core_analysis_sha256=sha256_file(core_analysis_path),
        checkpoint_lock_sha256=sha256_file(lock_path),
    )
    assert sha256_file(cube_analysis_path) == gauge["parent_cube_analysis_sha256"]
    assert analysis["record_count"] == 60
    assert analysis["integrity_gates_passed"] is True
    assert analysis["primary"]["classification"] == "material_gauge_feedback"
