from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import h5py
import numpy as np
import pytest
import torch
from omegaconf import OmegaConf

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from analyze_constraint_iclr_pdebench_cns import (  # noqa: E402
    analyze_cns_records,
    validate_cns_records,
)
from analyze_constraint_iclr_pdebench_cns_enforcement_cube import (  # noqa: E402
    analyze_cns_enforcement_cube,
    canonical_object_sha256,
    validate_cns_cube_records,
)
from constraint_iclr_common import (  # noqa: E402
    count_trainable_parameters,
    sha256_file,
)
from launch_constraint_iclr_pdebench_cns import (  # noqa: E402
    WORKER_SEEDS,
    build_cns_command,
)
from merge_constraint_iclr_pdebench_cns import merge_cns_shards  # noqa: E402
from prepare_constraint_iclr_pdebench_cns import (  # noqa: E402
    LOCK_SCHEMA_VERSION,
    inspect_cns_dataset,
    scan_cns_dataset,
)
from run_constraint_iclr_pdebench_cns import (  # noqa: E402
    build_cns_model,
    evaluate_cns_rollout,
    extract_cns_windows,
    load_cns_trajectories,
    model_state_sha256,
    project_density,
    restrict_cns_numpy,
    restrict_cns_torch,
    run_cns,
    train_cns_model,
    validate_cns_seed_assignment,
)
from run_constraint_iclr_pdebench_cns_enforcement_cube import (  # noqa: E402
    run_cns_cube,
)


def _write_cns(
    path: Path, *, trajectories: int = 8, times: int = 7, resolution: int = 16
) -> dict[str, object]:
    rng = np.random.default_rng(81)
    density0 = rng.uniform(0.8, 1.2, size=(trajectories, resolution)).astype(
        np.float32
    )
    pressure0 = rng.uniform(0.5, 1.5, size=(trajectories, resolution)).astype(
        np.float32
    )
    velocity0 = rng.normal(0.0, 0.2, size=(trajectories, resolution)).astype(
        np.float32
    )
    density = np.stack(
        [np.roll(density0, time, axis=-1) for time in range(times)], axis=1
    )
    pressure = np.stack(
        [np.roll(pressure0, 2 * time, axis=-1) for time in range(times)], axis=1
    )
    velocity = np.stack(
        [np.roll(velocity0, 3 * time, axis=-1) for time in range(times)], axis=1
    )
    with h5py.File(path, "w") as handle:
        handle.create_dataset("density", data=density)
        handle.create_dataset("pressure", data=pressure)
        handle.create_dataset("Vx", data=velocity)
        handle.create_dataset(
            "x-coordinate",
            data=-1.0 + (np.arange(resolution, dtype=np.float32) + 0.5)
            * (2.0 / resolution),
        )
        handle.create_dataset(
            "t-coordinate", data=np.arange(times, dtype=np.float32) * 0.1
        )
        handle.attrs["eta"] = 0.01
        handle.attrs["zeta"] = 0.01
    return {
        "expected_bytes": path.stat().st_size,
        "expected_sha256": sha256_file(path),
        "fields": ["density", "pressure", "Vx"],
        "expected_shape": [trajectories, times, resolution],
        "expected_dtype": "float32",
        "expected_x_start": -1.0 + 1.0 / resolution,
        "expected_x_period": 2.0,
        "expected_t_start": 0.0,
        "expected_t_stop": (times - 1) * 0.1,
        "coordinate_atol": 2e-6,
        "expected_eta": 0.01,
        "expected_zeta": 0.01,
        "attribute_atol": 1e-7,
        "invariant_field": "density",
        "max_abs_mean_drift": 1e-6,
        "invariant_spatial_strides": [1, 2, 4],
        "restriction_method": "block_average",
        "restriction_identity_atol": 1e-6,
        "scan_chunk_trajectories": 3,
    }


def test_cns_public_dataset_gate_checks_all_fields_and_density_invariant(
    tmp_path: Path,
) -> None:
    path = tmp_path / "cns.hdf5"
    config = _write_cns(path)
    inspection = inspect_cns_dataset(path, config)
    assert inspection["sha256"] == sha256_file(path)
    assert inspection["hdf5"]["admitted"] is True
    assert inspection["hdf5"]["restriction_identity_passed"] is True
    assert set(inspection["hdf5"]["field_abs_maxima"]) == {
        "density",
        "pressure",
        "Vx",
    }


def test_cns_gate_rejects_density_drift(tmp_path: Path) -> None:
    path = tmp_path / "cns-drift.hdf5"
    config = _write_cns(path)
    with h5py.File(path, "r+") as handle:
        handle["density"][0, 2, :] += np.float32(0.01)
    with pytest.raises(RuntimeError, match="invariant gate failed"):
        scan_cns_dataset(path, config)


def test_cns_gate_rejects_nonfinite_noninvariant_field(tmp_path: Path) -> None:
    path = tmp_path / "cns-nonfinite.hdf5"
    config = _write_cns(path)
    with h5py.File(path, "r+") as handle:
        handle["pressure"][3, 1, 2] = np.float32(np.nan)
    with pytest.raises(RuntimeError, match="pressure contains a non-finite"):
        scan_cns_dataset(path, config)


def test_cns_gate_rejects_coordinate_contract_change(tmp_path: Path) -> None:
    path = tmp_path / "cns-coordinate.hdf5"
    config = _write_cns(path)
    with h5py.File(path, "r+") as handle:
        handle["x-coordinate"][:] += np.float32(0.25)
    with pytest.raises(RuntimeError, match="coordinate start"):
        scan_cns_dataset(path, config)


def _small_model_config() -> dict[str, object]:
    return {
        "history": 2,
        "channels": 3,
        "channel_names": ["density", "pressure", "Vx"],
        "invariant_channel": 0,
        "modes": 2,
        "width": 6,
        "padding": 1,
        "projection_width": 8,
    }


def test_cns_loader_and_restriction_preserve_channel_order_and_density_mean(
    tmp_path: Path,
) -> None:
    path = tmp_path / "cns-loader.hdf5"
    _write_cns(path, trajectories=5, times=7, resolution=16)
    loaded = load_cns_trajectories(
        path,
        [3, 1],
        fields=["density", "pressure", "Vx"],
        temporal_stride=2,
        spatial_stride=4,
        restriction_method="block_average",
        read_chunk=1,
    )
    with h5py.File(path, "r") as handle:
        native = np.stack(
            [
                np.asarray(handle[field][[1, 3], ::2], dtype=np.float32)
                for field in ("density", "pressure", "Vx")
            ],
            axis=-1,
        )[[1, 0]]
    expected = restrict_cns_numpy(native, 4, "block_average")
    torch.testing.assert_close(loaded, torch.from_numpy(expected))
    native_tensor = torch.from_numpy(native)
    restricted = restrict_cns_torch(native_tensor, 4, "block_average")
    torch.testing.assert_close(
        restricted[..., 0].mean(dim=-1),
        native_tensor[..., 0].mean(dim=-1),
        atol=2e-7,
        rtol=0.0,
    )


def test_cns_factorial_models_are_parameter_matched_and_hard_conserve_density() -> None:
    model_config = _small_model_config()
    models = {
        mechanism: build_cns_model(model_config, mechanism)
        for mechanism in ("free", "free_res", "hard_abs", "hard")
    }
    assert len({count_trainable_parameters(model) for model in models.values()}) == 1
    digests = []
    for mechanism in models:
        torch.manual_seed(317)
        digests.append(model_state_sha256(build_cns_model(model_config, mechanism)))
    assert len(set(digests)) == 1

    history = torch.randn(4, 16, 2, 3, generator=torch.Generator().manual_seed(52))
    grid = torch.linspace(-1.0, 1.0, 16)
    previous_density_mean = history[..., -1, 0].mean(dim=-1)
    for mechanism in ("hard_abs", "hard"):
        prediction = models[mechanism](history, grid)
        torch.testing.assert_close(
            prediction[..., 0].mean(dim=-1),
            previous_density_mean,
            atol=3e-7,
            rtol=0.0,
        )


def test_cns_projection_changes_only_density_mean_error() -> None:
    generator = torch.Generator().manual_seed(71)
    previous = torch.randn(5, 24, 3, generator=generator)
    prediction = torch.randn(5, 24, 3, generator=generator)
    target = torch.randn(5, 24, 3, generator=generator)
    projected = project_density(previous, prediction, 0)
    torch.testing.assert_close(projected[..., 1:], prediction[..., 1:])
    torch.testing.assert_close(
        projected[..., 0].mean(dim=-1),
        previous[..., 0].mean(dim=-1),
        atol=2e-7,
        rtol=0.0,
    )
    free_error = prediction[..., 0] - target[..., 0]
    projected_error = projected[..., 0] - target[..., 0]
    torch.testing.assert_close(
        free_error - free_error.mean(dim=-1, keepdim=True),
        projected_error - projected_error.mean(dim=-1, keepdim=True),
        atol=5e-7,
        rtol=0.0,
    )


def test_cns_window_extraction_training_and_rollout_are_finite(tmp_path: Path) -> None:
    generator = torch.Generator().manual_seed(93)
    trajectories = torch.randn(6, 7, 8, 3, generator=generator)
    density_mean = trajectories[:, :1, :, 0].mean(dim=-1, keepdim=True)
    trajectories[..., 0] += density_mean - trajectories[..., 0].mean(
        dim=-1, keepdim=True
    )
    row_indices = torch.tensor([1, 4])
    target_indices = torch.tensor([4, 5, 4, 5, 4, 5])
    inputs, targets = extract_cns_windows(
        trajectories, row_indices, target_indices, history=2
    )
    torch.testing.assert_close(inputs[0], trajectories[1, 3:5].permute(1, 0, 2))
    torch.testing.assert_close(targets[0], trajectories[1, 5])

    model = build_cns_model(_small_model_config(), "hard")
    checkpoint = tmp_path / "tiny.pt"
    report = train_cns_model(
        model=model,
        trajectories=trajectories,
        grid=torch.linspace(-1.0, 1.0, 8),
        training_cfg={
            "epochs": 2,
            "batch_size": 3,
            "learning_rate": 0.001,
            "weight_decay": 0.0,
            "scheduler_step": 1,
            "scheduler_gamma": 0.5,
            "checkpoint_every_epochs": 1,
        },
        seed=4999,
        run_id="tiny-cns",
        checkpoint_path=checkpoint,
        device=torch.device("cpu"),
    )
    assert report["completed_epochs"] == 2
    assert checkpoint.is_file()
    metrics = evaluate_cns_rollout(
        model=model,
        trajectories=trajectories,
        grid=torch.linspace(-1.0, 1.0, 8),
        horizons=[1, 3],
        batch_size=2,
        field_names=["density", "pressure", "Vx"],
        device=torch.device("cpu"),
        projected=False,
    )
    assert set(metrics) == {"1", "3"}
    assert all(
        np.isfinite(value)
        for horizon_metrics in metrics.values()
        for value in horizon_metrics.values()
    )
    assert max(
        horizon_metrics["max_abs_invariant_drift"]
        for horizon_metrics in metrics.values()
    ) < 2e-6


def _cns_analysis_fixture() -> tuple[list[dict[str, object]], dict[str, object]]:
    seeds = list(range(5000, 5030))
    cases = ["id_r256", "ood_r512", "ood_r1024"]
    horizons = [1, 4, 16, 31]
    paths = {
        "active": "configs/constraint_iclr/cns.yaml",
        "protocol": "papers/proposal/cns.md",
        "source": "experiments/cns-source.json",
        "decision": "research/discovery/decisions/cns.yaml",
        "lock": "experiments/cns-lock.json",
        "model_decision": "research/discovery/decisions/cns-model.yaml",
    }
    source_manifest = {path: "a" * 64 for path in paths.values()}
    values = {
        "free": 4.0,
        "free_res": 2.0,
        "hard_abs": 2.5,
        "hard": 2.0,
        "projection": 4.0,
    }
    records: list[dict[str, object]] = []
    for seed in seeds:
        free_checkpoint = {
            "path": f"checkpoints/{seed}-free.pt",
            "sha256": f"{seed:064x}",
            "bytes": 100,
        }
        for mechanism, value in values.items():
            checkpoint = (
                free_checkpoint
                if mechanism == "projection"
                else {
                    "path": f"checkpoints/{seed}-{mechanism}.pt",
                    "sha256": f"{seed + len(mechanism):064x}",
                    "bytes": 100,
                }
            )
            if mechanism == "free":
                checkpoint = free_checkpoint
            run_id = f"cns-{seed}-{mechanism}"
            records.append(
                {
                    "schema_version": "constraint-iclr-pdebench-cns-v1",
                    "stage": "cns_factorial_confirmation",
                    "benchmark_id": "cns-fixture",
                    "protocol_sha256": "b" * 64,
                    "data_lock_sha256": "c" * 64,
                    "seed": seed,
                    "mechanism": mechanism,
                    "run_id": run_id,
                    "derived_from": (
                        f"cns-{seed}-free" if mechanism == "projection" else None
                    ),
                    "training_index_sha256": f"subset-{seed}",
                    "training_subset": {
                        "count": 2048,
                        "index_sha256": f"subset-{seed}",
                    },
                    "initialization_sha256": f"{seed:064x}",
                    "compute": {
                        "trainable_parameters": 1234,
                        "optimization_runs": 0 if mechanism == "projection" else 1,
                    },
                    "cases": {
                        case: {
                            str(horizon): {
                                "density_conserving_rmse": value,
                                "total_rmse": value + 0.2,
                                "density_rmse": value + 0.1,
                                "pressure_rmse": value + 0.3,
                                "Vx_rmse": value + 0.4,
                                "mean_abs_invariant_drift": 0.0,
                                "max_abs_invariant_drift": 0.0,
                            }
                            for horizon in horizons
                        }
                        for case in cases
                    },
                    "checkpoint": checkpoint,
                    "provenance": {
                        "git_head": "d" * 40,
                        "git_dirty": True,
                        "source_sha256": source_manifest,
                    },
                }
            )
    config: dict[str, object] = {
        "stage": "cns_factorial_confirmation",
        "benchmark_id": "cns-fixture",
        "active_config_path": paths["active"],
        "protocol_path": paths["protocol"],
        "protocol_sha256": "b" * 64,
        "source_metadata_path": paths["source"],
        "data_decision_path": paths["decision"],
        "model_decision_path": paths["model_decision"],
        "expected_git_head": "d" * 40,
        "expected_git_dirty": True,
        "dataset": {"lock_path": paths["lock"], "lock_sha256": "c" * 64},
        "seeds": seeds,
        "evaluation": {
            "case_names": cases,
            "horizons": horizons,
            "primary_case": "ood_r512",
            "primary_horizon": 16,
            "primary_metric": "density_conserving_rmse",
        },
        "factorial_analysis": {
            "bootstrap_draws": 300,
            "sign_flip_draws": 300,
            "confidence_nonzero": 0.95,
            "confidence_equivalence": 0.90,
            "sesoi_fraction_of_free_res": 0.10,
            "invariant_drift_atol": 0.0001,
            "shapley_efficiency_atol": 1e-12,
        },
    }
    return records, config


def test_cns_analyzer_detects_material_path_dependence_and_shapley_efficiency() -> None:
    records, config = _cns_analysis_fixture()
    result = analyze_cns_records(records, config)
    assert result["record_count"] == 150
    assert result["integrity_gates_passed"] is True
    assert result["primary"]["interaction"]["mean"] == pytest.approx(1.5)
    assert (
        result["primary"]["interaction"]["classification"]
        == "material_nonadditivity"
    )
    assert result["primary"]["max_abs_shapley_efficiency_error"] <= 1e-12


def test_cns_analyzer_rejects_unpaired_subset_and_projection_checkpoint() -> None:
    records, config = _cns_analysis_fixture()
    wrong_subset = copy.deepcopy(records)
    next(
        record
        for record in wrong_subset
        if record["seed"] == 5000 and record["mechanism"] == "hard"
    )["training_subset"]["index_sha256"] = "wrong"
    with pytest.raises(RuntimeError, match=r"training-index mismatch|unpaired CNS"):
        validate_cns_records(wrong_subset, config)

    wrong_checkpoint = copy.deepcopy(records)
    next(
        record
        for record in wrong_checkpoint
        if record["seed"] == 5000 and record["mechanism"] == "projection"
    )["checkpoint"] = {"path": "wrong.pt", "sha256": "e" * 64, "bytes": 1}
    with pytest.raises(RuntimeError, match="projection checkpoint mismatch"):
        validate_cns_records(wrong_checkpoint, config)


def test_cns_runner_one_seed_smoke_produces_four_trained_and_one_derived_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dataset_path = tmp_path / "cns-smoke.hdf5"
    dataset_contract = _write_cns(
        dataset_path, trajectories=8, times=7, resolution=16
    )
    benchmark_id = "cns-smoke-fixture"
    active_path = tmp_path / "active.yaml"
    protocol_path = tmp_path / "protocol.md"
    source_path = tmp_path / "source.json"
    decision_path = tmp_path / "decision.yaml"
    for path, contents in (
        (active_path, "stage: cns_factorial_smoke\n"),
        (protocol_path, "frozen smoke protocol\n"),
        (source_path, "{}\n"),
        (decision_path, "decision: admitted\n"),
    ):
        path.write_text(contents, encoding="utf-8")

    inspection = inspect_cns_dataset(dataset_path, dataset_contract)
    lock_path = tmp_path / "data-lock.json"
    lock = {
        "schema_version": LOCK_SCHEMA_VERSION,
        "benchmark_id": benchmark_id,
        "protocol": {
            "path": str(protocol_path),
            "sha256": sha256_file(protocol_path),
        },
        "source_metadata": {
            "path": str(source_path),
            "sha256": sha256_file(source_path),
        },
        "data_decision": {
            "path": str(decision_path),
            "sha256": sha256_file(decision_path),
        },
        "inspection": inspection,
    }
    lock_path.write_text(
        json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    output_path = tmp_path / "records.jsonl"
    checkpoint_dir = tmp_path / "checkpoints"
    git_head = "86dd76ee0127c5eb7945a5806bdad74548c62459"
    config = OmegaConf.create(
        {
            "stage": "cns_factorial_smoke",
            "benchmark_id": benchmark_id,
            "active_config_path": str(active_path),
            "expected_git_head": git_head,
            "expected_git_dirty": True,
            "dataset": {
                **dataset_contract,
                "path": str(dataset_path),
                "lock_path": str(lock_path),
                "lock_sha256": sha256_file(lock_path),
            },
            "split": {
                "confirmation_start": 0,
                "confirmation_count": 2,
                "train_pool_start": 2,
                "train_pool_stop": 8,
                "train_trajectories_per_seed": 4,
            },
            "model": _small_model_config(),
            "training": {
                "epochs": 1,
                "batch_size": 2,
                "learning_rate": 0.001,
                "weight_decay": 0.0,
                "scheduler_step": 1,
                "scheduler_gamma": 0.5,
                "temporal_stride": 2,
                "spatial_stride": 4,
                "restriction_method": "block_average",
                "checkpoint_every_epochs": 1,
            },
            "evaluation": {
                "spatial_strides": [1],
                "restriction_method": "block_average",
                "case_names": ["id_r16"],
                "horizons": [1],
                "batch_size": 2,
                "primary_case": "id_r16",
                "primary_horizon": 1,
                "primary_metric": "density_conserving_rmse",
            },
            "mechanisms": ["free", "free_res", "hard_abs", "hard"],
            "seeds": [4999],
            "device": "cpu",
            "output": str(output_path),
            "checkpoint_dir": str(checkpoint_dir),
            "protocol_path": str(protocol_path),
            "protocol_sha256": sha256_file(protocol_path),
            "source_metadata_path": str(source_path),
            "source_metadata_sha256": sha256_file(source_path),
            "data_decision_path": str(decision_path),
            "data_decision_sha256": sha256_file(decision_path),
            "model_decision_path": None,
            "model_decision_sha256": None,
            "factorial_analysis": {
                "bootstrap_draws": 200,
                "sign_flip_draws": 200,
                "confidence_nonzero": 0.95,
                "confidence_equivalence": 0.90,
                "sesoi_fraction_of_free_res": 0.10,
                "invariant_drift_atol": 0.0001,
                "shapley_efficiency_atol": 1e-12,
            },
        }
    )
    monkeypatch.setenv("ECOPHYS_GIT_HEAD", git_head)
    monkeypatch.setenv("ECOPHYS_DIRTY", "1")
    run_cns(config)
    records = [json.loads(line) for line in output_path.read_text().splitlines()]
    assert len(records) == 5
    assert {record["mechanism"] for record in records} == {
        "free",
        "projection",
        "free_res",
        "hard_abs",
        "hard",
    }
    indexed = validate_cns_records(
        records, OmegaConf.to_container(config, resolve=True)
    )
    assert indexed[(4999, "projection")]["compute"]["optimization_runs"] == 0
    assert indexed[(4999, "projection")]["checkpoint"] == indexed[
        (4999, "free")
    ]["checkpoint"]

    cube_protocol_path = tmp_path / "cube-protocol.md"
    cube_decision_path = tmp_path / "cube-decision.yaml"
    cube_protocol_path.write_text("frozen cube smoke\n", encoding="utf-8")
    cube_decision_path.write_text("decision: frozen\n", encoding="utf-8")
    core_analysis_path = tmp_path / "core-analysis.json"
    core_analysis_path.write_text(
        json.dumps(
            {
                "input_sha256": sha256_file(output_path),
                "integrity_gates_passed": True,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    cube_output_path = tmp_path / "cube.jsonl"
    checkpoint_lock_path = tmp_path / "checkpoint-lock.json"
    cube_config = OmegaConf.merge(
        config,
        {
            "cube": {
                "stage": "cns_enforcement_cube_smoke",
                "schema_version": "constraint-iclr-pdebench-cns-enforcement-cube-v1",
                "output": str(cube_output_path),
                "checkpoint_lock": str(checkpoint_lock_path),
                "core_analysis": str(core_analysis_path),
                "protocol_path": str(cube_protocol_path),
                "protocol_sha256": sha256_file(cube_protocol_path),
                "decision_path": str(cube_decision_path),
                "decision_sha256": sha256_file(cube_decision_path),
                "trained_parent_mechanisms": [
                    "free",
                    "free_res",
                    "hard_abs",
                    "hard",
                ],
                "derived_mechanisms": [
                    "projection_res",
                    "hard_abs_unprojected",
                    "hard_res_unprojected",
                ],
                "expected_core_records": 5,
                "expected_trained_checkpoints": 4,
                "expected_derived_records": 3,
                "checkpoint_schema_version": "constraint-iclr-pdebench-cns-v1",
                "checkpoint_lock_schema_version": (
                    "constraint-iclr-pdebench-cns-checkpoint-lock-v1"
                ),
                "checkpoint_completed_epochs": 1,
                "primary_metric": "density_conserving_rmse",
                "algebra_atol": 1e-12,
            }
        },
    )
    run_cns_cube(cube_config)
    derived = [
        json.loads(line) for line in cube_output_path.read_text().splitlines()
    ]
    assert len(derived) == 3
    assert all(record["compute"]["optimization_runs"] == 0 for record in derived)
    checkpoint_lock = json.loads(checkpoint_lock_path.read_text(encoding="utf-8"))
    resolved_cube = OmegaConf.to_container(cube_config, resolve=True)
    validated_core, validated_derived = validate_cns_cube_records(
        derived,
        records,
        checkpoint_lock,
        resolved_cube,
        core_records_sha256=sha256_file(output_path),
        core_analysis_sha256=sha256_file(core_analysis_path),
        checkpoint_lock_sha256=sha256_file(checkpoint_lock_path),
    )
    assert len(validated_core) == 5
    assert len(validated_derived) == 3

    tampered = copy.deepcopy(derived)
    tampered[0]["compute"]["optimization_runs"] = 1
    with pytest.raises(RuntimeError, match="nonzero optimization_runs"):
        validate_cns_cube_records(
            tampered,
            records,
            checkpoint_lock,
            resolved_cube,
            core_records_sha256=sha256_file(output_path),
            core_analysis_sha256=sha256_file(core_analysis_path),
            checkpoint_lock_sha256=sha256_file(checkpoint_lock_path),
        )


def _cns_cube_analysis_fixture() -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, object],
    dict[str, object],
]:
    core_records, config = _cns_analysis_fixture()
    cube_protocol = "papers/proposal/cns-cube.md"
    cube_decision = "research/discovery/decisions/cns-cube.yaml"
    checkpoint_lock_path = "experiments/cns-checkpoint-lock.json"
    config["cube"] = {
        "stage": "cns_enforcement_cube_confirmation",
        "schema_version": "constraint-iclr-pdebench-cns-enforcement-cube-v1",
        "protocol_path": cube_protocol,
        "protocol_sha256": "e" * 64,
        "decision_path": cube_decision,
        "decision_sha256": "f" * 64,
        "checkpoint_lock": checkpoint_lock_path,
        "trained_parent_mechanisms": ["free", "free_res", "hard_abs", "hard"],
        "derived_mechanisms": [
            "projection_res",
            "hard_abs_unprojected",
            "hard_res_unprojected",
        ],
        "expected_core_records": 150,
        "expected_trained_checkpoints": 120,
        "expected_derived_records": 90,
        "checkpoint_schema_version": "constraint-iclr-pdebench-cns-v1",
        "checkpoint_lock_schema_version": (
            "constraint-iclr-pdebench-cns-checkpoint-lock-v1"
        ),
        "checkpoint_completed_epochs": 200,
        "primary_metric": "density_conserving_rmse",
        "algebra_atol": 1e-12,
    }
    core = {
        (int(record["seed"]), str(record["mechanism"])): record
        for record in core_records
    }
    checkpoint_lock: dict[str, object] = {
        "schema_version": config["cube"]["checkpoint_lock_schema_version"],
        "benchmark_id": config["benchmark_id"],
        "core_records": {
            "path": "experiments/cns-core.jsonl",
            "sha256": "1" * 64,
            "record_count": 150,
        },
        "core_analysis": {
            "path": "experiments/cns-core-analysis.json",
            "sha256": "2" * 64,
        },
        "factorial_protocol_sha256": config["protocol_sha256"],
        "cube_protocol_sha256": config["cube"]["protocol_sha256"],
        "cube_decision_sha256": config["cube"]["decision_sha256"],
        "checkpoints": [
            {
                "seed": seed,
                "mechanism": mechanism,
                "run_id": core[(seed, mechanism)]["run_id"],
                "path": core[(seed, mechanism)]["checkpoint"]["path"],
                "bytes": core[(seed, mechanism)]["checkpoint"]["bytes"],
                "sha256": core[(seed, mechanism)]["checkpoint"]["sha256"],
                "payload_schema_version": "constraint-iclr-pdebench-cns-v1",
                "completed_epochs": 200,
            }
            for seed in config["seeds"]
            for mechanism in ("free", "free_res", "hard_abs", "hard")
        ],
    }
    source_manifest = copy.deepcopy(
        core_records[0]["provenance"]["source_sha256"]
    )
    source_manifest.update(
        {
            cube_protocol: "e" * 64,
            cube_decision: "f" * 64,
            checkpoint_lock_path: "3" * 64,
        }
    )
    specifications = {
        "projection_res": ("free_res", "free_res", True, 3.0),
        "hard_abs_unprojected": ("hard_abs", "free", False, 3.2),
        "hard_res_unprojected": ("hard", "free_res", False, 2.2),
    }
    derived_records: list[dict[str, object]] = []
    for seed in config["seeds"]:
        for mechanism, (
            parent_mechanism,
            forward_map,
            projected,
            long_horizon_value,
        ) in specifications.items():
            parent = core[(seed, parent_mechanism)]
            checkpoint = parent["checkpoint"]
            cases = {}
            for case in config["evaluation"]["case_names"]:
                horizons = {}
                for horizon in config["evaluation"]["horizons"]:
                    value = (
                        parent["cases"][case]["1"]["density_conserving_rmse"]
                        if horizon == 1
                        else long_horizon_value
                    )
                    horizons[str(horizon)] = {
                        "density_conserving_rmse": value,
                        "total_rmse": value + 0.2,
                        "density_rmse": value + 0.1,
                        "pressure_rmse": value + 0.3,
                        "Vx_rmse": value + 0.4,
                        "mean_abs_invariant_drift": 0.0,
                        "max_abs_invariant_drift": 0.0,
                    }
                cases[case] = horizons
            derived_records.append(
                {
                    "schema_version": config["cube"]["schema_version"],
                    "stage": config["cube"]["stage"],
                    "benchmark_id": config["benchmark_id"],
                    "dataset_sha256": "4" * 64,
                    "data_lock_sha256": config["dataset"]["lock_sha256"],
                    "factorial_protocol_sha256": config["protocol_sha256"],
                    "cube_protocol_sha256": config["cube"]["protocol_sha256"],
                    "cube_decision_sha256": config["cube"]["decision_sha256"],
                    "core_records_sha256": "1" * 64,
                    "core_analysis_sha256": "2" * 64,
                    "checkpoint_lock_sha256": "3" * 64,
                    "seed": seed,
                    "mechanism": mechanism,
                    "run_id": f"cns-cube-{seed}-{mechanism}",
                    "parent_run_id": parent["run_id"],
                    "forward_map": forward_map,
                    "inference_projected": projected,
                    "derived_from": parent["run_id"],
                    "training_index_sha256": parent["training_index_sha256"],
                    "initialization_sha256": parent["initialization_sha256"],
                    "parent": {
                        "run_id": parent["run_id"],
                        "mechanism": parent_mechanism,
                        "checkpoint_path": checkpoint["path"],
                        "checkpoint_sha256": checkpoint["sha256"],
                        "checkpoint_bytes": checkpoint["bytes"],
                        "training_index_sha256": parent[
                            "training_index_sha256"
                        ],
                        "initialization_sha256": parent["initialization_sha256"],
                        "provenance_sha256": canonical_object_sha256(
                            parent["provenance"]
                        ),
                    },
                    "compute": {
                        "trainable_parameters": 1234,
                        "examples_seen": 0,
                        "proxy": 0,
                        "training_runtime_seconds": 0.0,
                        "evaluation_runtime_seconds": 1.0,
                        "peak_gpu_memory_bytes": None,
                        "optimization_runs": 0,
                    },
                    "cases": cases,
                    "provenance": {
                        "git_head": config["expected_git_head"],
                        "git_dirty": config["expected_git_dirty"],
                        "source_sha256": source_manifest,
                    },
                }
            )
    return derived_records, core_records, checkpoint_lock, config


def test_cns_cube_analyzer_recovers_three_way_effect_and_rejects_parent_tamper() -> None:
    derived, core, checkpoint_lock, config = _cns_cube_analysis_fixture()
    result = analyze_cns_enforcement_cube(
        derived,
        core,
        checkpoint_lock,
        config,
        core_records_sha256="1" * 64,
        core_analysis_sha256="2" * 64,
        checkpoint_lock_sha256="3" * 64,
    )
    assert result["derived_record_count"] == 90
    assert result["checkpoint_count"] == 120
    assert result["primary"]["three_way_interaction"]["mean"] == pytest.approx(
        0.5
    )
    assert result["primary"]["max_abs_three_way_path_identity_error"] <= 1e-12
    assert result["primary"]["max_abs_shapley_efficiency_error"] <= 1e-12

    tampered = copy.deepcopy(derived)
    tampered[0]["parent"]["checkpoint_sha256"] = "0" * 64
    with pytest.raises(RuntimeError, match="parent checkpoint_sha256"):
        validate_cns_cube_records(
            tampered,
            core,
            checkpoint_lock,
            config,
            core_records_sha256="1" * 64,
            core_analysis_sha256="2" * 64,
            checkpoint_lock_sha256="3" * 64,
        )


def test_cns_distributed_seed_partition_and_launcher_are_exact() -> None:
    shards = {name: list(seeds) for name, seeds in WORKER_SEEDS.items()}
    resolved = {
        "stage": "cns_factorial_confirmation",
        "seeds": shards["v100a"],
        "formal_seed_universe": list(range(5000, 5030)),
        "formal_seed_shards": shards,
        "worker_id": "v100a",
    }
    assert validate_cns_seed_assignment(resolved) == list(range(5000, 5015))
    command = build_cns_command(Path("/repo"), "formal", "v100b")
    assert "pdebench_cns_eta0p01_factorial_distributed_20260902" in command
    assert "worker_id=v100b" in command
    assert f"seeds=[{','.join(map(str, range(5015, 5030)))}]" in command

    wrong = copy.deepcopy(resolved)
    wrong["formal_seed_shards"]["v100b"][0] = 5014
    with pytest.raises(RuntimeError, match="partition 5000--5029 exactly"):
        validate_cns_seed_assignment(wrong)


def test_cns_shard_merge_requires_exact_150_records_and_one_source_manifest(
    tmp_path: Path,
) -> None:
    mechanisms = ["free", "projection", "free_res", "hard_abs", "hard"]
    source_manifest = {"frozen": "a" * 64}

    def record(seed: int, mechanism: str) -> dict[str, object]:
        return {
            "seed": seed,
            "mechanism": mechanism,
            "run_id": f"{seed}-{mechanism}",
            "stage": "cns_factorial_confirmation",
            "benchmark_id": (
                "pdebench_cns_eta0.01_zeta0.01_periodic_fno_factorial_v1"
            ),
            "provenance": {"source_sha256": source_manifest},
        }

    shard_paths = [tmp_path / "v100a.jsonl", tmp_path / "v100b.jsonl"]
    for path, seeds in zip(
        shard_paths, (range(5000, 5015), range(5015, 5030)), strict=True
    ):
        path.write_text(
            "\n".join(
                json.dumps(record(seed, mechanism))
                for seed in reversed(list(seeds))
                for mechanism in reversed(mechanisms)
            )
            + "\n",
            encoding="utf-8",
        )
    output = tmp_path / "merged.jsonl"
    merge_cns_shards(shard_paths, output)
    merged = [json.loads(line) for line in output.read_text().splitlines()]
    assert len(merged) == 150
    assert [(item["seed"], item["mechanism"]) for item in merged[:5]] == [
        (5000, mechanism) for mechanism in mechanisms
    ]

    bad = tmp_path / "bad.jsonl"
    bad_records = [record(seed, mechanism) for seed in range(5015, 5030) for mechanism in mechanisms]
    bad_records[0]["provenance"] = {"source_sha256": {"changed": "b" * 64}}
    bad.write_text(
        "\n".join(json.dumps(item) for item in bad_records) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="one source manifest"):
        merge_cns_shards([shard_paths[0], bad], tmp_path / "bad-merged.jsonl")
