from __future__ import annotations

import copy
import sys
from pathlib import Path

import h5py
import numpy as np
import pytest
import torch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from analyze_constraint_iclr_pdebench_swe import (  # noqa: E402
    analyze_swe_records,
    validate_swe_records,
)
from analyze_constraint_iclr_pdebench_swe_enforcement_cube import (  # noqa: E402
    DERIVED_SPEC,
    _roundoff_tolerance,
    analyze_swe_enforcement_cube,
    canonical_object_sha256,
    swe_cube_seed_effects,
    validate_swe_cube_records,
)
from constraint_iclr_common import sha256_file  # noqa: E402
from launch_constraint_iclr_pdebench_swe import (  # noqa: E402
    WORKER_SEEDS,
    build_swe_command,
)
from merge_constraint_iclr_pdebench_swe import merge_swe_shards  # noqa: E402
from prepare_constraint_iclr_pdebench_swe import (  # noqa: E402
    inspect_swe_dataset,
    md5_file,
    restrict_swe_numpy,
    scan_swe_dataset,
)
from run_constraint_iclr_pdebench_swe import (  # noqa: E402
    build_swe_model,
    evaluate_swe_rollout,
    extract_swe_windows,
    load_swe_trajectories,
    model_state_sha256,
    project_swe_mass,
    restrict_swe_torch,
    train_swe_model,
    validate_swe_seed_assignment,
)


def _write_swe(path: Path, groups: int = 1) -> dict[str, object]:
    x = -2.5 + (np.arange(128, dtype=np.float32) + 0.5) * np.float32(5.0 / 128.0)
    y = x.copy()
    t = np.linspace(0.0, 1.0, 101, dtype=np.float32)
    xx, yy = np.meshgrid(x, y, indexing="ij")
    initial = (
        np.float32(1.25)
        + np.float32(0.1)
        * np.cos(np.float32(2.0 * np.pi / 5.0) * xx)
        * np.cos(np.float32(2.0 * np.pi / 5.0) * yy)
    ).astype(np.float32)
    with h5py.File(path, "w") as handle:
        for index in range(groups):
            name = str(index).zfill(4)
            values = np.stack(
                [np.roll(initial, shift=time, axis=0) for time in range(101)],
                axis=0,
            )[..., None]
            handle.create_dataset(f"{name}/data", data=values, dtype="f")
            handle.create_dataset(f"{name}/grid/x", data=x, dtype="f")
            handle.create_dataset(f"{name}/grid/y", data=y, dtype="f")
            handle.create_dataset(f"{name}/grid/t", data=t, dtype="f")
    return {
        "expected_bytes": path.stat().st_size,
        "expected_md5": md5_file(path),
        "expected_sha256": sha256_file(path),
        "expected_groups": groups,
        "group_name_width": 4,
        "data_key": "data",
        "expected_shape": [101, 128, 128, 1],
        "expected_dtype": "float32",
        "expected_x_start": -2.48046875,
        "expected_x_stop": 2.48046875,
        "expected_y_start": -2.48046875,
        "expected_y_stop": 2.48046875,
        "expected_spatial_spacing": 0.0390625,
        "expected_t_start": 0.0,
        "expected_t_stop": 1.0,
        "expected_temporal_spacing": 0.01,
        "coordinate_atol": 1e-6,
        "require_strict_positive": True,
        "max_abs_mean_drift": 5e-5,
        "invariant_spatial_factors": [1, 2],
        "restriction_method": "block_average",
        "restriction_identity_atol": 1e-6,
        "scan_chunk_trajectories": 1,
    }


def test_swe_gate_checks_checksum_schema_conservation_and_positivity(
    tmp_path: Path,
) -> None:
    path = tmp_path / "swe.h5"
    config = _write_swe(path)
    inspection = inspect_swe_dataset(path, config)
    assert inspection["md5"] == md5_file(path)
    assert inspection["sha256"] == sha256_file(path)
    assert inspection["hdf5"]["admitted"] is True
    assert inspection["hdf5"]["strictly_positive"] is True
    assert inspection["hdf5"]["restriction_identity_passed"] is True


def test_swe_block_average_preserves_mean_on_both_axes() -> None:
    rng = np.random.default_rng(902)
    values = rng.normal(size=(3, 5, 16, 20)).astype(np.float32)
    restricted = restrict_swe_numpy(values, 4, "block_average")
    assert restricted.shape == (3, 5, 4, 5)
    np.testing.assert_allclose(
        restricted.mean(axis=(-2, -1)),
        values.mean(axis=(-2, -1)),
        atol=1e-6,
    )


def test_swe_gate_rejects_mass_drift(tmp_path: Path) -> None:
    path = tmp_path / "swe-drift.h5"
    config = _write_swe(path)
    with h5py.File(path, "r+") as handle:
        handle["0000/data"][10, :, :, 0] += np.float32(0.01)
    with pytest.raises(RuntimeError, match="invariant gate failed"):
        scan_swe_dataset(path, config)


def test_swe_gate_rejects_nonpositive_depth(tmp_path: Path) -> None:
    path = tmp_path / "swe-negative.h5"
    config = _write_swe(path)
    with h5py.File(path, "r+") as handle:
        handle["0000/data"][3, 4, 5, 0] = np.float32(0.0)
    with pytest.raises(RuntimeError, match="non-positive depth"):
        scan_swe_dataset(path, config)


def test_swe_gate_rejects_coordinate_difference_between_groups(
    tmp_path: Path,
) -> None:
    path = tmp_path / "swe-coordinate.h5"
    config = _write_swe(path, groups=2)
    with h5py.File(path, "r+") as handle:
        handle["0001/grid/x"][0] += np.float32(0.01)
    with pytest.raises(RuntimeError, match="differs from group 0000"):
        scan_swe_dataset(path, config)


def _write_small_swe(path: Path, *, groups: int = 5, times: int = 7, resolution: int = 16) -> None:
    x = -2.5 + (np.arange(resolution, dtype=np.float32) + 0.5) * np.float32(5.0 / resolution)
    t = np.linspace(0.0, 0.6, times, dtype=np.float32)
    with h5py.File(path, "w") as handle:
        for index in range(groups):
            rng = np.random.default_rng(100 + index)
            initial = rng.uniform(0.8, 1.4, size=(resolution, resolution)).astype(np.float32)
            values = np.stack(
                [np.roll(initial, shift=time, axis=0) for time in range(times)],
                axis=0,
            )[..., None]
            handle.create_dataset(f"{index:04d}/data", data=values)
            handle.create_dataset(f"{index:04d}/grid/x", data=x)
            handle.create_dataset(f"{index:04d}/grid/y", data=x)
            handle.create_dataset(f"{index:04d}/grid/t", data=t)


def _small_model_config() -> dict[str, object]:
    return {
        "history": 2,
        "modes_x": 2,
        "modes_y": 2,
        "width": 6,
        "padding": 1,
        "projection_width": 8,
        "coordinate_lower": -2.5,
        "coordinate_upper": 2.5,
    }


def test_swe_loader_and_torch_restriction_preserve_order_and_mean(
    tmp_path: Path,
) -> None:
    path = tmp_path / "small-swe.h5"
    _write_small_swe(path)
    loaded = load_swe_trajectories(
        path,
        [3, 1, 4],
        temporal_stride=1,
        spatial_factor=2,
        restriction_method="block_average",
    )
    assert loaded.shape == (3, 7, 8, 8)
    with h5py.File(path, "r") as handle:
        expected_first = np.asarray(handle["0003/data"])[..., 0]
    np.testing.assert_allclose(
        loaded[0].mean(dim=(-2, -1)).numpy(),
        expected_first.mean(axis=(-2, -1)),
        atol=1e-6,
    )
    native = torch.from_numpy(expected_first)
    torch_restricted = restrict_swe_torch(native, 2, "block_average")
    numpy_restricted = restrict_swe_numpy(expected_first, 2, "block_average")
    np.testing.assert_allclose(torch_restricted.numpy(), numpy_restricted, atol=1e-7)


def test_swe_equal_parameter_arms_and_exact_hard_mass() -> None:
    grid = torch.linspace(-2.25, 2.25, 8)
    history = torch.randn(3, 8, 8, 2)
    parameter_counts = []
    hashes = []
    for mechanism in ("free", "free_res", "hard_abs", "hard"):
        torch.manual_seed(33)
        model = build_swe_model(_small_model_config(), mechanism)
        parameter_counts.append(sum(value.numel() for value in model.parameters()))
        hashes.append(model_state_sha256(model))
        prediction = model(history, grid, grid)
        assert prediction.shape == (3, 8, 8)
        if mechanism in {"hard_abs", "hard"}:
            torch.testing.assert_close(
                prediction.mean(dim=(-2, -1)),
                history[..., -1].mean(dim=(-2, -1)),
                atol=2e-6,
                rtol=0.0,
            )
    assert len(set(parameter_counts)) == 1
    assert len(set(hashes)) == 1


def test_swe_projection_preserves_one_step_mean_centered_error() -> None:
    previous = torch.rand(4, 12, 12)
    prediction = torch.randn(4, 12, 12)
    target = torch.rand(4, 12, 12)
    projected = project_swe_mass(previous, prediction)
    free_error = prediction - target
    projected_error = projected - target
    free_centered = free_error - free_error.mean(dim=(-2, -1), keepdim=True)
    projected_centered = projected_error - projected_error.mean(dim=(-2, -1), keepdim=True)
    torch.testing.assert_close(free_centered, projected_centered, atol=5e-7, rtol=0.0)
    torch.testing.assert_close(
        projected.mean(dim=(-2, -1)),
        previous.mean(dim=(-2, -1)),
        atol=5e-7,
        rtol=0.0,
    )


def test_swe_train_and_rollout_emit_positivity_metrics(tmp_path: Path) -> None:
    torch.manual_seed(44)
    model = build_swe_model(_small_model_config(), "free_res")
    initial = torch.rand(6, 8, 8) + 0.8
    trajectories = torch.stack([torch.roll(initial, shifts=time, dims=-1) for time in range(7)], dim=1)
    grid = torch.linspace(-2.25, 2.25, 8)
    checkpoint = tmp_path / "swe.pt"
    report = train_swe_model(
        model=model,
        trajectories=trajectories,
        grid_x=grid,
        grid_y=grid,
        training_cfg={
            "epochs": 2,
            "batch_size": 3,
            "learning_rate": 0.001,
            "weight_decay": 0.0,
            "scheduler_step": 1,
            "scheduler_gamma": 0.5,
            "checkpoint_every_epochs": 1,
        },
        seed=5999,
        run_id="small-swe",
        checkpoint_path=checkpoint,
        device=torch.device("cpu"),
    )
    assert report["completed_epochs"] == 2
    cases = evaluate_swe_rollout(
        model=model,
        trajectories=trajectories,
        grid_x=grid,
        grid_y=grid,
        horizons=[1, 2],
        batch_size=3,
        device=torch.device("cpu"),
        projected=True,
    )
    assert set(cases) == {"1", "2"}
    for metrics in cases.values():
        assert 0.0 <= metrics["negative_depth_fraction"] <= 1.0
        assert metrics["mean_negative_depth_deficit"] >= 0.0
        assert abs(metrics["max_abs_invariant_drift"]) < 2e-6


def test_swe_seed_shards_must_partition_formal_universe() -> None:
    resolved = {
        "stage": "swe_factorial_confirmation",
        "seeds": list(range(6000, 6015)),
        "formal_seed_universe": list(range(6000, 6030)),
        "formal_seed_shards": {
            "v100a": list(range(6000, 6015)),
            "v100b": list(range(6015, 6030)),
        },
        "worker_id": "v100a",
    }
    assert validate_swe_seed_assignment(resolved) == list(range(6000, 6015))
    broken = dict(resolved)
    broken["seeds"] = list(range(6001, 6015))
    with pytest.raises(RuntimeError, match="differ from its frozen shard"):
        validate_swe_seed_assignment(broken)


def test_extract_swe_windows_uses_per_trajectory_targets() -> None:
    trajectories = torch.arange(4 * 6 * 3 * 2).reshape(4, 6, 3, 2).float()
    rows = torch.tensor([3, 1])
    targets = torch.tensor([2, 3, 4, 5])
    inputs, output = extract_swe_windows(trajectories, rows, targets, history=2)
    assert inputs.shape == (2, 3, 2, 2)
    torch.testing.assert_close(output[0], trajectories[3, 5])
    torch.testing.assert_close(output[1], trajectories[1, 3])


def _analysis_fixture() -> tuple[list[dict[str, object]], dict[str, object]]:
    lock_sha = "a" * 64
    config: dict[str, object] = {
        "stage": "swe_factorial_smoke",
        "benchmark_id": "swe-test",
        "seeds": [1, 2],
        "active_config_path": "config.yaml",
        "protocol_path": "protocol.md",
        "protocol_sha256": "b" * 64,
        "source_metadata_path": "source.json",
        "data_decision_path": "data.yaml",
        "transport_decision_path": "transport.yaml",
        "expected_git_head": "c" * 40,
        "expected_git_dirty": True,
        "dataset": {"lock_path": "lock.json", "lock_sha256": lock_sha},
        "evaluation": {
            "case_names": ["id_r64", "ood_r128"],
            "horizons": [1, 2],
            "primary_case": "ood_r128",
            "primary_horizon": 2,
            "primary_metric": "conserving_rmse",
        },
        "factorial_analysis": {
            "bootstrap_draws": 200,
            "sign_flip_draws": 200,
            "confidence_nonzero": 0.95,
            "confidence_equivalence": 0.90,
            "sesoi_fraction_of_free_res": 0.10,
            "invariant_drift_atol": 1e-4,
            "shapley_efficiency_atol": 1e-12,
        },
    }
    sources = {
        path: "d" * 64
        for path in (
            "config.yaml",
            "protocol.md",
            "source.json",
            "data.yaml",
            "transport.yaml",
            "lock.json",
        )
    }
    mechanism_value = {
        "free": 1.20,
        "free_res": 1.00,
        "hard_abs": 0.95,
        "hard": 0.90,
        "projection": 1.20,
    }
    records: list[dict[str, object]] = []
    for seed in (1, 2):
        free_checkpoint = {
            "path": f"free-{seed}.pt",
            "sha256": "e" * 64,
            "bytes": 100,
        }
        for mechanism, base in mechanism_value.items():
            checkpoint = (
                free_checkpoint
                if mechanism in {"free", "projection"}
                else {
                    "path": f"{mechanism}-{seed}.pt",
                    "sha256": "f" * 64,
                    "bytes": 100,
                }
            )
            cases: dict[str, object] = {}
            for case in ("id_r64", "ood_r128"):
                cases[case] = {}
                for horizon in (1, 2):
                    value = base + 0.01 * seed + 0.02 * horizon
                    if mechanism == "projection" and horizon == 1:
                        value = mechanism_value["free"] + 0.01 * seed + 0.02
                    cases[case][str(horizon)] = {
                        "conserving_rmse": value,
                        "total_rmse": value + 0.1,
                        "mean_abs_invariant_drift": 0.0,
                        "max_abs_invariant_drift": 0.0,
                        "mean_abs_target_invariant_drift": 1e-7,
                        "max_abs_target_invariant_drift": 2e-7,
                        "negative_depth_fraction": 0.01,
                        "mean_negative_depth_deficit": 0.001,
                        "minimum_predicted_depth": -0.1,
                    }
            records.append(
                {
                    "schema_version": "constraint-iclr-pdebench-swe-v1",
                    "stage": "swe_factorial_smoke",
                    "benchmark_id": "swe-test",
                    "protocol_sha256": "b" * 64,
                    "data_lock_sha256": lock_sha,
                    "seed": seed,
                    "mechanism": mechanism,
                    "run_id": f"{seed}-{mechanism}",
                    "derived_from": f"{seed}-free" if mechanism == "projection" else None,
                    "training_index_sha256": f"subset-{seed}",
                    "training_subset": {"index_sha256": f"subset-{seed}"},
                    "initialization_sha256": f"init-{seed}",
                    "compute": {
                        "trainable_parameters": 50,
                        "optimization_runs": 0 if mechanism == "projection" else 1,
                    },
                    "cases": cases,
                    "checkpoint": checkpoint,
                    "provenance": {
                        "git_head": "c" * 40,
                        "git_dirty": True,
                        "source_sha256": sources,
                    },
                }
            )
    return records, config


def test_swe_factorial_analyzer_validates_and_adjudicates() -> None:
    records, config = _analysis_fixture()
    indexed = validate_swe_records(records, config)
    assert len(indexed) == 10
    analysis = analyze_swe_records(records, config)
    assert analysis["record_count"] == 10
    assert len(analysis["all_cases"]) == 4
    assert analysis["integrity_gates_passed"] is True
    assert "negative_depth_fraction" in analysis["primary_descriptive_table"]["free"]


def test_swe_factorial_analyzer_rejects_duplicate_run_id() -> None:
    records, config = _analysis_fixture()
    records[1]["run_id"] = records[0]["run_id"]
    with pytest.raises(RuntimeError, match="duplicate SWE run ID"):
        validate_swe_records(records, config)


def test_swe_factorial_analyzer_rejects_invalid_positivity_metric() -> None:
    records, config = _analysis_fixture()
    broken = copy.deepcopy(records)
    broken[0]["cases"]["id_r64"]["1"]["negative_depth_fraction"] = 1.1
    with pytest.raises(RuntimeError, match="invalid SWE negative-depth fraction"):
        validate_swe_records(broken, config)


def _cube_fixture() -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, object],
    dict[str, object],
]:
    core, config = _analysis_fixture()
    config["cube"] = {
        "stage": "swe_enforcement_cube_smoke",
        "schema_version": "constraint-iclr-pdebench-swe-enforcement-cube-v1",
        "derived_mechanisms": list(DERIVED_SPEC),
        "trained_parent_mechanisms": ["free", "free_res", "hard_abs", "hard"],
        "expected_core_records": 10,
        "expected_trained_checkpoints": 8,
        "expected_derived_records": 6,
        "checkpoint_schema_version": "constraint-iclr-pdebench-swe-v1",
        "checkpoint_completed_epochs": 2,
        "primary_metric": "conserving_rmse",
        "algebra_atol": 1e-12,
        "protocol_path": "cube-protocol.md",
        "protocol_sha256": "1" * 64,
        "decision_path": "cube-decision.yaml",
        "decision_sha256": "2" * 64,
        "checkpoint_lock": "checkpoint-lock.json",
        "checkpoint_lock_schema_version": "swe-lock-v1",
        "tradeoff": {
            "case": "ood_r128",
            "horizon": 2,
            "conservation_metric": "max_abs_invariant_drift",
            "positivity_metric": "mean_negative_depth_deficit",
            "secondary_positivity_metric": "negative_depth_fraction",
            "confidence": 0.95,
        },
    }
    core_index = {(int(record["seed"]), str(record["mechanism"])): record for record in core}
    checkpoint_entries = []
    for seed in (1, 2):
        for mechanism in ("free", "free_res", "hard_abs", "hard"):
            parent = core_index[(seed, mechanism)]
            checkpoint = parent["checkpoint"]
            checkpoint_entries.append(
                {
                    "seed": seed,
                    "mechanism": mechanism,
                    "run_id": parent["run_id"],
                    "path": checkpoint["path"],
                    "bytes": checkpoint["bytes"],
                    "sha256": checkpoint["sha256"],
                    "payload_schema_version": "constraint-iclr-pdebench-swe-v1",
                    "completed_epochs": 2,
                }
            )
    checkpoint_lock = {
        "schema_version": "swe-lock-v1",
        "benchmark_id": "swe-test",
        "core_records": {"sha256": "3" * 64, "record_count": 10},
        "core_analysis": {"sha256": "4" * 64},
        "factorial_protocol_sha256": "b" * 64,
        "cube_protocol_sha256": "1" * 64,
        "cube_decision_sha256": "2" * 64,
        "checkpoints": checkpoint_entries,
    }
    derived_sources = {
        "cube-protocol.md": "1" * 64,
        "cube-decision.yaml": "2" * 64,
        "checkpoint-lock.json": "5" * 64,
        "lock.json": "a" * 64,
    }
    derived: list[dict[str, object]] = []
    for seed in (1, 2):
        for mechanism, spec in DERIVED_SPEC.items():
            parent = core_index[(seed, str(spec["parent"]))]
            checkpoint = parent["checkpoint"]
            cases = copy.deepcopy(parent["cases"])
            for case in ("id_r64", "ood_r128"):
                for horizon in (1, 2):
                    if horizon > 1:
                        metrics = cases[case][str(horizon)]
                        metrics["conserving_rmse"] += {
                            "projection_res": -0.03,
                            "hard_abs_unprojected": 0.02,
                            "hard_res_unprojected": 0.01,
                        }[mechanism]
                    if bool(spec["inference_projected"]):
                        cases[case][str(horizon)]["max_abs_invariant_drift"] = 0.0
            derived.append(
                {
                    "schema_version": "constraint-iclr-pdebench-swe-enforcement-cube-v1",
                    "stage": "swe_enforcement_cube_smoke",
                    "benchmark_id": "swe-test",
                    "dataset_sha256": "6" * 64,
                    "data_lock_sha256": "a" * 64,
                    "factorial_protocol_sha256": "b" * 64,
                    "cube_protocol_sha256": "1" * 64,
                    "cube_decision_sha256": "2" * 64,
                    "core_records_sha256": "3" * 64,
                    "core_analysis_sha256": "4" * 64,
                    "checkpoint_lock_sha256": "5" * 64,
                    "seed": seed,
                    "mechanism": mechanism,
                    "run_id": f"cube-{seed}-{mechanism}",
                    "parent_run_id": parent["run_id"],
                    "forward_map": spec["forward_map"],
                    "inference_projected": spec["inference_projected"],
                    "derived_from": parent["run_id"],
                    "training_index_sha256": parent["training_index_sha256"],
                    "initialization_sha256": parent["initialization_sha256"],
                    "parent": {
                        "run_id": parent["run_id"],
                        "mechanism": spec["parent"],
                        "checkpoint_path": checkpoint["path"],
                        "checkpoint_sha256": checkpoint["sha256"],
                        "checkpoint_bytes": checkpoint["bytes"],
                        "training_index_sha256": parent["training_index_sha256"],
                        "initialization_sha256": parent["initialization_sha256"],
                        "provenance_sha256": canonical_object_sha256(parent["provenance"]),
                    },
                    "compute": {
                        "trainable_parameters": 50,
                        "optimization_runs": 0,
                        "examples_seen": 0,
                        "proxy": 0,
                        "training_runtime_seconds": 0.0,
                    },
                    "cases": cases,
                    "provenance": {
                        "git_head": "c" * 40,
                        "git_dirty": True,
                        "source_sha256": derived_sources,
                    },
                }
            )
    return derived, core, checkpoint_lock, config


def test_swe_enforcement_cube_validates_algebra_and_secondary_outcomes() -> None:
    derived, core, checkpoint_lock, config = _cube_fixture()
    core_index, derived_index = validate_swe_cube_records(
        derived,
        core,
        checkpoint_lock,
        config,
        core_records_sha256="3" * 64,
        core_analysis_sha256="4" * 64,
        checkpoint_lock_sha256="5" * 64,
    )
    effects = swe_cube_seed_effects(
        core_index,
        derived_index,
        [1, 2],
        "ood_r128",
        2,
        "conserving_rmse",
    )
    np.testing.assert_allclose(effects["J"], effects["J_inference_path"], atol=1e-12)
    np.testing.assert_allclose(
        effects["phi_train"] + effects["phi_infer"],
        effects["I_bundle"],
        atol=1e-12,
    )
    np.testing.assert_allclose(
        effects["infer_free_train"],
        0.5 * (effects["infer_A_t0"] + effects["infer_R_t0"]),
        atol=1e-12,
    )
    np.testing.assert_allclose(
        effects["main_infer"],
        0.5 * (effects["infer_free_train"] + effects["infer_hard_train"]),
        atol=1e-12,
    )
    analysis = analyze_swe_enforcement_cube(
        derived,
        core,
        checkpoint_lock,
        config,
        core_records_sha256="3" * 64,
        core_analysis_sha256="4" * 64,
        checkpoint_lock_sha256="5" * 64,
    )
    assert analysis["derived_record_count"] == 6
    assert "negative_depth_fraction" in analysis["secondary_primary_case"]
    tradeoff = analysis["conservation_positivity_tradeoff"]
    assert tradeoff["case"] == "ood_r128"
    assert tradeoff["horizon"] == 2
    assert tradeoff["metrics"]["positivity"]["metric"] == ("mean_negative_depth_deficit")
    assert tradeoff["classification"] in {
        "conservation_gain_not_resolved",
        "resolved_conservation_positivity_tradeoff",
        "resolved_conservation_positivity_synergy",
        "conservation_gain_with_unresolved_positivity_effect",
    }


def test_swe_cube_roundoff_bound_scales_with_cancelling_operands() -> None:
    operands = (
        np.asarray([1.0e12, -1.0e12]),
        np.asarray([-1.0e12, 1.0e12]),
        np.asarray([1.0e12, 1.0e12]),
        np.asarray([-1.0e12, -1.0e12]),
    )
    tolerance = _roundoff_tolerance(1.0e-12, *operands)
    assert tolerance > 1.0e-2
    assert tolerance < 1.0


def test_swe_enforcement_cube_rejects_nonzero_optimization() -> None:
    derived, core, checkpoint_lock, config = _cube_fixture()
    derived[0]["compute"]["optimization_runs"] = 1
    with pytest.raises(RuntimeError, match="nonzero optimization_runs"):
        validate_swe_cube_records(
            derived,
            core,
            checkpoint_lock,
            config,
            core_records_sha256="3" * 64,
            core_analysis_sha256="4" * 64,
            checkpoint_lock_sha256="5" * 64,
        )


def test_swe_launcher_freezes_preflight_and_worker_shards(tmp_path: Path) -> None:
    preflight = build_swe_command(tmp_path, "preflight")
    assert any(item == "seeds=[5999]" for item in preflight)
    assert any(item == "training.epochs=1" for item in preflight)
    formal = build_swe_command(tmp_path, "formal", "v100a")
    assert any(item == f"seeds={WORKER_SEEDS['v100a']}".replace(" ", "") for item in formal)
    assert any(item == "worker_id=v100a" for item in formal)


def test_swe_merge_requires_exact_disjoint_coverage() -> None:
    records, config = _analysis_fixture()
    config["formal_seed_shards"] = {"v100a": [1], "v100b": [2]}
    config["formal_seed_universe"] = [1, 2]
    shards = {
        "v100a": [record for record in records if int(record["seed"]) == 1],
        "v100b": [record for record in records if int(record["seed"]) == 2],
    }
    merged = merge_swe_shards(shards, config)
    assert len(merged) == 10
    broken = copy.deepcopy(shards)
    broken["v100b"][0]["run_id"] = broken["v100a"][0]["run_id"]
    with pytest.raises(RuntimeError, match="duplicate SWE run ID across shards"):
        merge_swe_shards(broken, config)
