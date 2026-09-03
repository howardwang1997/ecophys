from __future__ import annotations

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

from analyze_constraint_iclr_pdebench import (  # noqa: E402
    analyze_comparison,
    load_config,
    paired_sign_flip_pvalue,
    validate_records,
)
from analyze_constraint_iclr_pdebench_enforcement_cube import (  # noqa: E402
    analyze_enforcement_cube,
    canonical_object_sha256,
    validate_cube_records,
)
from analyze_constraint_iclr_pdebench_factorial import (  # noqa: E402
    analyze_factorial_records,
    validate_factorial_records,
)
from analyze_constraint_iclr_pdebench_gradient_coupling import (  # noqa: E402
    analyze_gradient_coupling,
    spearman_bootstrap,
    validate_diagnostic_records,
)
from analyze_constraint_iclr_pdebench_gradient_coupling_v4 import (  # noqa: E402
    analyze_gradient_coupling_v4,
)
from constraint_iclr_common import count_trainable_parameters, sha256_file  # noqa: E402
from launch_constraint_iclr_pdebench import build_command  # noqa: E402
from launch_constraint_iclr_pdebench_burgers_factorial import (  # noqa: E402
    build_burgers_factorial_command,
)
from launch_constraint_iclr_pdebench_burgers_factorial_distributed import (  # noqa: E402
    WORKER_SEEDS,
    build_distributed_burgers_command,
)
from launch_constraint_iclr_pdebench_factorial import (  # noqa: E402
    build_factorial_command,
)
from merge_constraint_iclr_pdebench_factorial import merge_shards  # noqa: E402
from run_constraint_iclr_pdebench_enforcement_cube import (  # noqa: E402
    run_cube,
)
from run_constraint_iclr_pdebench_fno import (  # noqa: E402
    FNO1d,
    evaluate_rollout,
    extract_windows,
    hash_file_dual,
    inspect_public_dataset,
    load_trajectories,
    model_state_sha256,
    project_mass,
    projection_identity_max_error,
    restrict_grid,
    restrict_spatial_numpy,
    restrict_spatial_torch,
    run,
    scan_public_dataset,
    select_training_indices,
    train_model,
    validate_data_lock,
)
from run_constraint_iclr_pdebench_gradient_coupling import (  # noqa: E402
    channel_losses,
    exact_one_adam_step,
    gradient_coupling,
)
from run_constraint_iclr_pdebench_gradient_coupling import (  # noqa: E402
    run as run_gradient_coupling,
)


def _write_synthetic_hdf5(
    path: Path, *, trajectories: int = 12, times: int = 14, resolution: int = 32
) -> dict[str, object]:
    rng = np.random.default_rng(41)
    initial = rng.normal(size=(trajectories, resolution)).astype(np.float32)
    tensor = np.stack(
        [np.roll(initial, 4 * time_index, axis=-1) for time_index in range(times)],
        axis=1,
    )
    with h5py.File(path, "w") as handle:
        handle.create_dataset("tensor", data=tensor)
        handle.create_dataset(
            "x-coordinate", data=np.arange(resolution, dtype=np.float32) / resolution
        )
        handle.create_dataset(
            "t-coordinate", data=np.arange(times, dtype=np.float32) * 0.1
        )
    hashes = hash_file_dual(path)
    return {
        "expected_bytes": path.stat().st_size,
        "expected_md5": hashes["md5"],
        "expected_shape": [trajectories, times, resolution],
        "expected_dtype": "float32",
        "expected_x_start": 0.0,
        "expected_x_period": 1.0,
        "expected_t_start": 0.0,
        "expected_t_stop": (times - 1) * 0.1,
        "coordinate_atol": 2e-6,
        "max_abs_mean_drift": 1e-6,
        "invariant_spatial_strides": [1, 2, 4],
        "scan_chunk_trajectories": 3,
    }


def test_public_dataset_integrity_and_invariant_gate(tmp_path: Path) -> None:
    path = tmp_path / "synthetic.hdf5"
    config = _write_synthetic_hdf5(path)
    inspection = inspect_public_dataset(path, config)
    assert inspection["hdf5"]["admitted"] is True
    assert inspection["hdf5"]["shape"] == [12, 14, 32]
    assert inspection["sha256"] == hash_file_dual(path)["sha256"]


def test_public_dataset_invariant_gate_rejects_drift(tmp_path: Path) -> None:
    path = tmp_path / "drifting.hdf5"
    config = _write_synthetic_hdf5(path)
    with h5py.File(path, "r+") as handle:
        handle["tensor"][0, 1, :] += np.float32(0.01)
    with pytest.raises(RuntimeError, match="invariant gate failed"):
        scan_public_dataset(path, config)


def test_streaming_loader_preserves_requested_order_and_strides(tmp_path: Path) -> None:
    path = tmp_path / "synthetic.hdf5"
    _write_synthetic_hdf5(path)
    loaded = load_trajectories(
        path, [7, 2, 10], temporal_stride=2, spatial_stride=4, read_chunk=2
    )
    with h5py.File(path, "r") as handle:
        expected = np.asarray(handle["tensor"][[2, 7, 10], ::2, ::4])[[1, 0, 2]]
    torch.testing.assert_close(loaded, torch.from_numpy(expected))


def test_block_average_restriction_preserves_global_mean() -> None:
    rng = np.random.default_rng(123)
    values = rng.normal(size=(4, 7, 32)).astype(np.float32)
    native_means = values.mean(axis=-1, dtype=np.float64)
    for factor in (2, 4):
        restricted = restrict_spatial_numpy(values, factor, "block_average")
        np.testing.assert_allclose(
            restricted.mean(axis=-1, dtype=np.float64), native_means, atol=1e-7, rtol=0.0
        )
        torch_restricted = restrict_spatial_torch(
            torch.from_numpy(values), factor, "block_average"
        )
        torch.testing.assert_close(
            torch_restricted,
            torch.from_numpy(restricted),
            atol=1e-7,
            rtol=0.0,
        )
    grid = torch.arange(32, dtype=torch.float32) / 32 + 1 / 64
    restricted_grid = restrict_grid(grid, 4, "block_average")
    torch.testing.assert_close(restricted_grid[0], torch.tensor(0.0625))


def test_block_average_dataset_gate_and_streaming_loader(tmp_path: Path) -> None:
    path = tmp_path / "block.hdf5"
    config = _write_synthetic_hdf5(path)
    config["restriction_method"] = "block_average"
    config["restriction_identity_atol"] = 1e-6
    report = scan_public_dataset(path, config)
    assert report["admitted"] is True
    assert report["restriction_identity_passed"] is True
    loaded = load_trajectories(
        path,
        [0, 3],
        temporal_stride=2,
        spatial_stride=4,
        restriction_method="block_average",
    )
    with h5py.File(path, "r") as handle:
        native = np.asarray(handle["tensor"][[0, 3], ::2, :], dtype=np.float32)
    expected = restrict_spatial_numpy(native, 4, "block_average")
    torch.testing.assert_close(loaded, torch.from_numpy(expected))


def test_training_subset_is_deterministic_namespaced_and_in_pool() -> None:
    split = {
        "train_pool_start": 100,
        "train_pool_stop": 200,
        "train_trajectories_per_seed": 30,
    }
    first = select_training_indices(2000, split)
    second = select_training_indices(2000, split)
    other = select_training_indices(2001, split)
    np.testing.assert_array_equal(first, second)
    assert not np.array_equal(first, other)
    assert len(np.unique(first)) == 30
    assert first.min() >= 100 and first.max() < 200


def _small_model(mechanism: str) -> FNO1d:
    return FNO1d(
        history=3,
        modes=4,
        width=8,
        padding=2,
        projection_width=16,
        mechanism=mechanism,
    )


def test_fno_arms_have_equal_parameters_and_hard_preserves_mass() -> None:
    models = [
        _small_model(mode)
        for mode in ("free", "free_res", "hard_abs", "hard", "soft30")
    ]
    assert len({count_trainable_parameters(model) for model in models}) == 1
    history = torch.randn(5, 32, 3, generator=torch.Generator().manual_seed(9))
    grid = torch.arange(32, dtype=torch.float32) / 32
    for model in (models[2], models[3]):
        output = model(history, grid)
        torch.testing.assert_close(
            output.mean(dim=-1), history[..., -1].mean(dim=-1), atol=2e-7, rtol=0.0
        )


def test_factorial_cells_share_initial_parameter_tensor_digest() -> None:
    digests = []
    for mechanism in ("free", "free_res", "hard_abs", "hard"):
        torch.manual_seed(123)
        digests.append(model_state_sha256(_small_model(mechanism)))
    assert len(set(digests)) == 1


def test_projection_changes_only_the_invariant_error_channel() -> None:
    generator = torch.Generator().manual_seed(17)
    previous = torch.randn(6, 24, generator=generator)
    prediction = torch.randn(6, 24, generator=generator)
    target = torch.randn(6, 24, generator=generator)
    projected = project_mass(previous, prediction)
    raw_error = prediction - target
    projected_error = projected - target
    raw_conserving = raw_error - raw_error.mean(dim=-1, keepdim=True)
    projected_conserving = projected_error - projected_error.mean(dim=-1, keepdim=True)
    torch.testing.assert_close(raw_conserving, projected_conserving, atol=5e-7, rtol=0.0)
    torch.testing.assert_close(
        projected.mean(dim=-1), previous.mean(dim=-1), atol=2e-7, rtol=0.0
    )


def test_gradient_channel_loss_decomposition_and_coupling_are_finite() -> None:
    model = torch.nn.Linear(3, 4, bias=True)
    inputs = torch.randn(5, 3, generator=torch.Generator().manual_seed(90))
    targets = torch.randn(5, 4, generator=torch.Generator().manual_seed(91))
    prediction = model(inputs)
    total, conserving, violating = channel_losses(prediction, targets)
    torch.testing.assert_close(total, conserving + violating, atol=1e-7, rtol=1e-6)
    diagnostics = gradient_coupling(model, conserving, violating)
    assert diagnostics["q_norm"] > 0.0
    assert diagnostics["p_norm"] > 0.0
    assert -1.0 <= diagnostics["cosine"] <= 1.0


def test_exact_one_step_uses_matched_coordinate_specific_fno_cells() -> None:
    model_cfg = {
        "history": 2,
        "modes": 2,
        "width": 4,
        "padding": 1,
        "projection_width": 8,
    }
    training_cfg = {"learning_rate": 0.001, "weight_decay": 0.0001}
    inputs = torch.randn(3, 16, 2, generator=torch.Generator().manual_seed(92))
    targets = torch.randn(3, 16, generator=torch.Generator().manual_seed(93))
    grid = torch.arange(16, dtype=torch.float32) / 16
    torch.manual_seed(94)
    initial_model = FNO1d(mechanism="free", **model_cfg)
    initial_state = {
        name: value.detach().clone()
        for name, value in initial_model.state_dict().items()
    }
    for coordinate in ("absolute", "residual"):
        report = exact_one_adam_step(
            initial_state=initial_state,
            model_cfg=model_cfg,
            training_cfg=training_cfg,
            coordinate=coordinate,
            inputs=inputs,
            targets=targets,
            grid=grid,
        )
        assert all(np.isfinite(value) for value in report.values())
        assert report["one_step_enforcement_credit"] == pytest.approx(
            report["free_conserving_loss_after"]
            - report["hard_conserving_loss_after"]
        )


def test_gradient_coupling_runner_smoke_writes_paired_coordinates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ECOPHYS_GIT_HEAD", "d" * 40)
    monkeypatch.setenv("ECOPHYS_DIRTY", "1")
    dataset_path = tmp_path / "gradient-smoke.hdf5"
    dataset_config = _write_synthetic_hdf5(
        dataset_path, trajectories=10, times=21, resolution=16
    )
    dataset_config.update(
        {"restriction_method": "block_average", "restriction_identity_atol": 1e-6}
    )
    inspection = inspect_public_dataset(dataset_path, dataset_config)
    lock_path = tmp_path / "gradient-lock.json"
    lock_path.write_text(
        json.dumps(
            {
                "schema_version": "constraint-iclr-pdebench-data-lock-v1",
                "benchmark_id": "synthetic-gradient",
                "inspection": inspection,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    protocol_path = tmp_path / "gradient-protocol.md"
    protocol_path.write_text("frozen gradient protocol\n", encoding="utf-8")
    decision_path = tmp_path / "gradient-decision.yaml"
    decision_path.write_text("status: authorized\n", encoding="utf-8")
    output_path = tmp_path / "gradient.jsonl"
    config = OmegaConf.create(
        {
            "stage": "factorial_confirmation",
            "diagnostic_stage": "gradient_coupling",
            "benchmark_id": "synthetic-gradient",
            "expected_git_head": "d" * 40,
            "expected_git_dirty": True,
            "dataset": {
                "path": str(dataset_path),
                **dataset_config,
                "lock_path": str(lock_path),
                "lock_sha256": sha256_file(lock_path),
            },
            "split": {
                "train_pool_start": 2,
                "train_pool_stop": 10,
                "train_trajectories_per_seed": 4,
            },
            "model": {
                "history": 2,
                "modes": 2,
                "width": 4,
                "padding": 1,
                "projection_width": 8,
            },
            "training": {
                "batch_size": 2,
                "learning_rate": 0.001,
                "weight_decay": 0.0001,
                "temporal_stride": 5,
                "spatial_stride": 4,
                "restriction_method": "block_average",
            },
            "mechanisms": ["free", "free_res", "hard_abs", "hard"],
            "seeds": [5],
            "device": "cpu",
            "output": "unused-factorial.jsonl",
            "protocol_path": str(protocol_path),
            "protocol_sha256": sha256_file(protocol_path),
            "gradient_output": str(output_path),
            "gradient_protocol_path": str(protocol_path),
            "gradient_protocol_sha256": sha256_file(protocol_path),
            "gradient_decision_path": str(decision_path),
            "gradient_source_artifact_paths": [],
        }
    )
    run_gradient_coupling(config)
    records = [json.loads(line) for line in output_path.read_text().splitlines()]
    assert [record["coordinate"] for record in records] == ["absolute", "residual"]
    assert records[0]["initialization_sha256"] == records[1]["initialization_sha256"]
    assert records[0]["batch"] == records[1]["batch"]
    assert all(
        np.isfinite(record["one_step"]["one_step_enforcement_credit"])
        for record in records
    )


def test_window_extraction_uses_preceding_history() -> None:
    values = torch.arange(2 * 6 * 4, dtype=torch.float32).reshape(2, 6, 4)
    inputs, targets = extract_windows(
        values,
        row_indices=torch.tensor([1, 0]),
        target_indices=torch.tensor([4, 5]),
        history=3,
    )
    torch.testing.assert_close(inputs[0].T, values[1, 2:5])
    torch.testing.assert_close(targets[0], values[1, 5])
    torch.testing.assert_close(inputs[1].T, values[0, 1:4])
    torch.testing.assert_close(targets[1], values[0, 4])


def test_tiny_training_checkpoint_and_rollout_are_finite(tmp_path: Path) -> None:
    generator = torch.Generator().manual_seed(33)
    initial = torch.randn(8, 16, generator=generator)
    trajectories = torch.stack(
        [torch.roll(initial, shifts=time_index, dims=-1) for time_index in range(7)], dim=1
    )
    grid = torch.arange(16, dtype=torch.float32) / 16
    torch.manual_seed(2)
    model = FNO1d(
        history=2,
        modes=3,
        width=4,
        padding=1,
        projection_width=8,
        mechanism="hard",
    )
    checkpoint = tmp_path / "tiny.pt"
    report = train_model(
        model=model,
        mechanism="hard",
        trajectories=trajectories,
        grid=grid,
        training_cfg={
            "epochs": 2,
            "batch_size": 4,
            "learning_rate": 0.001,
            "weight_decay": 0.0001,
            "scheduler_step": 1,
            "scheduler_gamma": 0.5,
            "checkpoint_every_epochs": 1,
        },
        soft_weight=30.0,
        seed=1999,
        run_id="tiny-run",
        checkpoint_path=checkpoint,
        device=torch.device("cpu"),
    )
    assert checkpoint.is_file()
    assert report["completed_epochs"] == 2
    metrics = evaluate_rollout(
        model=model,
        trajectories=trajectories,
        grid=grid,
        history=2,
        horizons=[1, 4],
        batch_size=4,
        device=torch.device("cpu"),
        projected=False,
    )
    assert set(metrics) == {"1", "4"}
    assert all(np.isfinite(value) for result in metrics.values() for value in result.values())
    assert metrics["4"]["max_abs_invariant_drift"] < 2e-6


def test_end_to_end_runner_smoke_writes_free_and_projection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ECOPHYS_GIT_HEAD", "d" * 40)
    monkeypatch.setenv("ECOPHYS_DIRTY", "1")
    root = Path(__file__).resolve().parents[1]
    dataset_path = tmp_path / "smoke.hdf5"
    dataset_config = _write_synthetic_hdf5(dataset_path, times=21)
    output_path = tmp_path / "smoke.jsonl"
    config = OmegaConf.create(
        {
            "stage": "smoke",
            "benchmark_id": "synthetic-advection",
            "dataset": {
                "path": str(dataset_path),
                **dataset_config,
                "restriction_method": "block_average",
                "restriction_identity_atol": 1e-6,
            },
            "split": {
                "confirmation_start": 0,
                "confirmation_count": 2,
                "train_pool_start": 2,
                "train_pool_stop": 10,
                "train_trajectories_per_seed": 4,
            },
            "model": {
                "history": 2,
                "modes": 2,
                "width": 4,
                "padding": 1,
                "projection_width": 8,
            },
            "training": {
                "epochs": 1,
                "batch_size": 2,
                "learning_rate": 0.001,
                "weight_decay": 0.0001,
                "scheduler_step": 1,
                "scheduler_gamma": 0.5,
                "temporal_stride": 5,
                "spatial_stride": 4,
                "restriction_method": "block_average",
                "checkpoint_every_epochs": 1,
            },
            "evaluation": {
                "spatial_strides": [4, 2, 1],
                "restriction_method": "block_average",
                "case_names": ["id_r8", "ood_r16", "ood_r32"],
                "horizons": [1, 2],
                "batch_size": 2,
                "primary_case": "ood_r16",
                "primary_horizon": 2,
            },
            "mechanisms": ["free"],
            "soft_weight": 30.0,
            "seeds": [5],
            "device": "cpu",
            "output": str(output_path),
            "checkpoint_dir": str(tmp_path / "checkpoints"),
            "protocol_path": None,
            "protocol_sha256": None,
            "decision_path": None,
            "incident_path": str(
                root
                / "experiments/constraint_attribution_iclr/deployment/"
                "pilot_ood_accidental_exposure_20260831.yaml"
            ),
        }
    )
    run(config)
    records = [json.loads(line) for line in output_path.read_text().splitlines()]
    assert [record["mechanism"] for record in records] == ["free", "projection"]
    assert records[1]["derived_from"] == records[0]["run_id"]
    assert all(record["stage"] == "smoke" for record in records)


def test_end_to_end_factorial_smoke_writes_four_trained_cells(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ECOPHYS_GIT_HEAD", "d" * 40)
    monkeypatch.setenv("ECOPHYS_DIRTY", "1")
    root = Path(__file__).resolve().parents[1]
    dataset_path = tmp_path / "factorial-smoke.hdf5"
    dataset_config = _write_synthetic_hdf5(
        dataset_path, trajectories=10, times=21, resolution=16
    )
    output_path = tmp_path / "factorial-smoke.jsonl"
    config = OmegaConf.create(
        {
            "stage": "smoke",
            "benchmark_id": "synthetic-factorial",
            "dataset": {
                "path": str(dataset_path),
                **dataset_config,
                "restriction_method": "block_average",
                "restriction_identity_atol": 1e-6,
            },
            "split": {
                "confirmation_start": 0,
                "confirmation_count": 2,
                "train_pool_start": 2,
                "train_pool_stop": 10,
                "train_trajectories_per_seed": 4,
            },
            "model": {
                "history": 2,
                "modes": 2,
                "width": 4,
                "padding": 1,
                "projection_width": 8,
            },
            "training": {
                "epochs": 1,
                "batch_size": 2,
                "learning_rate": 0.001,
                "weight_decay": 0.0001,
                "scheduler_step": 1,
                "scheduler_gamma": 0.5,
                "temporal_stride": 5,
                "spatial_stride": 4,
                "restriction_method": "block_average",
                "checkpoint_every_epochs": 1,
            },
            "evaluation": {
                "spatial_strides": [4, 2, 1],
                "restriction_method": "block_average",
                "case_names": ["id_r4", "ood_r8", "ood_r16"],
                "horizons": [1],
                "batch_size": 2,
                "primary_case": "ood_r8",
                "primary_horizon": 1,
            },
            "mechanisms": ["free", "free_res", "hard_abs", "hard"],
            "soft_weight": 30.0,
            "seeds": [5],
            "device": "cpu",
            "output": str(output_path),
            "checkpoint_dir": str(tmp_path / "factorial-checkpoints"),
            "protocol_path": None,
            "protocol_sha256": None,
            "decision_path": None,
            "incident_path": str(
                root
                / "experiments/constraint_attribution_iclr/deployment/"
                "pilot_ood_accidental_exposure_20260831.yaml"
            ),
        }
    )
    run(config)
    records = [json.loads(line) for line in output_path.read_text().splitlines()]
    assert {record["mechanism"] for record in records} == {
        "free",
        "free_res",
        "hard_abs",
        "hard",
        "projection",
    }
    trained = [record for record in records if record["mechanism"] != "projection"]
    assert len({record["initialization_sha256"] for record in trained}) == 1
    for record in records:
        if record["mechanism"] in {"hard_abs", "hard", "projection"}:
            assert all(
                metrics["max_abs_invariant_drift"] < 1e-5
                for case in record["cases"].values()
                for metrics in case.values()
            )


def test_free_projection_horizon_one_identity_gate() -> None:
    generator = torch.Generator().manual_seed(52)
    trajectories = torch.randn(6, 6, 16, generator=generator)
    grid = torch.arange(16, dtype=torch.float32) / 16
    model = FNO1d(
        history=2,
        modes=3,
        width=4,
        padding=1,
        projection_width=8,
        mechanism="free",
    )
    error = projection_identity_max_error(
        model=model,
        trajectories=trajectories,
        grid=grid,
        history=2,
        batch_size=3,
        device=torch.device("cpu"),
    )
    assert error < 5e-7


def test_data_lock_binds_exact_dataset_bytes(tmp_path: Path) -> None:
    root = tmp_path
    dataset = root / "dataset.hdf5"
    config = _write_synthetic_hdf5(dataset)
    inspection = inspect_public_dataset(dataset, config)
    lock = {
        "schema_version": "constraint-iclr-pdebench-data-lock-v1",
        "benchmark_id": "synthetic",
        "inspection": inspection,
    }
    lock_path = root / "lock.json"
    lock_path.write_text(json.dumps(lock, sort_keys=True) + "\n", encoding="utf-8")
    resolved = {
        "benchmark_id": "synthetic",
        "dataset": {"lock_path": "lock.json", "lock_sha256": sha256_file(lock_path)},
    }
    returned_path, returned_hash, returned_lock = validate_data_lock(
        root=root, resolved=resolved, dataset_path=dataset
    )
    assert returned_path == lock_path
    assert returned_hash == sha256_file(lock_path)
    assert returned_lock["inspection"]["sha256"] == inspection["sha256"]


def test_frozen_config_has_thirty_new_seeds_and_primary_case() -> None:
    root = Path(__file__).resolve().parents[1]
    config = OmegaConf.to_container(
        OmegaConf.load(root / "configs/constraint_iclr/pdebench_advection_fno_v2.yaml"),
        resolve=True,
    )
    assert config["seeds"] == list(range(2000, 2030))
    assert config["mechanisms"] == ["free", "free_res", "hard", "soft30"]
    assert config["evaluation"]["primary_case"] == "ood_r512"
    assert config["evaluation"]["primary_horizon"] == 16
    assert config["dataset"]["file_id"] == 255674
    assert config["dataset"]["expected_md5"] == "d595bbfd2c659df995a93cd40d6ea568"


def test_v2_config_changes_only_to_conservative_restriction() -> None:
    root = Path(__file__).resolve().parents[1]
    config = OmegaConf.to_container(
        OmegaConf.load(root / "configs/constraint_iclr/pdebench_advection_fno_v2.yaml"),
        resolve=True,
    )
    assert config["benchmark_id"] == "pdebench_advection_beta0.4_fno_v2"
    assert config["dataset"]["restriction_method"] == "block_average"
    assert config["training"]["restriction_method"] == "block_average"
    assert config["evaluation"]["restriction_method"] == "block_average"
    assert config["dataset"]["restriction_identity_atol"] == pytest.approx(1e-6)
    assert config["seeds"] == list(range(2000, 2030))
    assert config["evaluation"]["primary_case"] == "ood_r512"


def test_v2_launcher_keeps_preflight_excluded_and_formal_unmodified() -> None:
    root = Path("/experiment")
    formal = build_command(root, "pdebench_advection_fno_v2_confirmation", "formal")
    assert formal == [
        sys.executable,
        "/experiment/scripts/run_constraint_iclr_pdebench_fno.py",
        "--config-name",
        "pdebench_advection_fno_v2_confirmation",
    ]
    preflight = build_command(
        root, "pdebench_advection_fno_v2_confirmation", "preflight"
    )
    joined = " ".join(preflight)
    assert "stage=external_preflight" in joined
    assert "seeds=[1999]" in joined
    assert "split.confirmation_start=9000" in joined
    assert "training.epochs=1" in joined
    assert "preflight_v2.jsonl" in joined
    assert "2000" not in joined


def test_v2_confirmation_overlay_binds_exact_data_lock() -> None:
    root = Path(__file__).resolve().parents[1]
    config = load_config(
        root / "configs/constraint_iclr/pdebench_advection_fno_v2_confirmation.yaml"
    )
    assert config["dataset"]["lock_sha256"] == (
        "78705fc8f0c342bc5f937756fce93ab60c660acbb24d15a5ea90a620f7890687"
    )
    assert config["dataset"]["restriction_method"] == "block_average"
    assert config["seeds"] == list(range(2000, 2030))


def test_factorial_config_is_fresh_fully_crossed_and_bound() -> None:
    root = Path(__file__).resolve().parents[1]
    config = load_config(
        root
        / "configs/constraint_iclr/pdebench_advection_fno_factorial_20260901.yaml"
    )
    assert config["stage"] == "factorial_confirmation"
    assert config["mechanisms"] == ["free", "free_res", "hard_abs", "hard"]
    assert config["seeds"] == list(range(3000, 3030))
    assert config["preflight_seed"] == 2999
    assert config["dataset"]["lock_benchmark_id"] == (
        "pdebench_advection_beta0.4_fno_v2"
    )
    assert config["data_lock_protocol_sha256"] == (
        "01d300410364b07e779c2c2462cdd60f720a24a86622675f4df0f7c604724307"
    )
    assert config["protocol_sha256"] == sha256_file(
        root
        / "papers/proposal/"
        "ecomd_constraint_attribution_iclr_pdebench_factorial_freeze_2026-09-01.md"
    )


def test_factorial_launcher_separates_excluded_preflight_and_formal() -> None:
    root = Path("/experiment")
    formal = build_factorial_command(root, "formal")
    assert formal == [
        sys.executable,
        "/experiment/scripts/run_constraint_iclr_pdebench_fno.py",
        "--config-name",
        "pdebench_advection_fno_factorial_20260901",
    ]
    preflight = " ".join(build_factorial_command(root, "preflight"))
    assert "stage=factorial_preflight" in preflight
    assert "seeds=[2999]" in preflight
    assert "training.epochs=1" in preflight
    assert "factorial_preflight_20260901.jsonl" in preflight
    assert "3000" not in preflight


def test_burgers_factorial_data_and_seed_choice_are_frozen() -> None:
    root = Path(__file__).resolve().parents[1]
    config = OmegaConf.to_container(
        OmegaConf.load(
            root / "configs/constraint_iclr/pdebench_burgers_nu0p01_factorial.yaml"
        ),
        resolve=True,
    )
    source = json.loads(
        (
            root
            / "experiments/constraint_attribution_iclr/pdebench/"
            "burgers_nu0p01_source_20260901.json"
        ).read_text(encoding="utf-8")
    )
    assert config["benchmark_id"] == "pdebench_burgers_nu0.01_fno_factorial_v1"
    assert config["dataset"]["file_id"] == 281363 == source["file_id"]
    assert config["dataset"]["expected_bytes"] == 8232968312 == source["filesize"]
    assert config["dataset"]["expected_md5"] == source["md5"]
    assert config["dataset"]["expected_x_start"] == pytest.approx(-0.9990234375)
    assert config["dataset"]["expected_x_period"] == pytest.approx(2.0)
    assert config["dataset"]["expected_sha256"] is None
    assert config["mechanisms"] == ["free", "free_res", "hard_abs", "hard"]
    assert config["seeds"] == list(range(4000, 4030))
    assert config["preflight_seed"] == 3999


def test_burgers_factorial_launcher_uses_only_frozen_config() -> None:
    root = Path("/experiment")
    formal = build_burgers_factorial_command(root, "formal")
    assert formal[-1] == "pdebench_burgers_nu0p01_factorial_confirmation"
    preflight = " ".join(build_burgers_factorial_command(root, "preflight"))
    assert "stage=factorial_preflight" in preflight
    assert "seeds=[3999]" in preflight
    assert "burgers_factorial_preflight_20260901.jsonl" in preflight
    assert "4000" not in preflight


def test_burgers_distributed_workers_partition_every_formal_seed_once() -> None:
    assert set(WORKER_SEEDS) == {"v100a", "v100b"}
    assert set(WORKER_SEEDS["v100a"]).isdisjoint(WORKER_SEEDS["v100b"])
    assert sorted((*WORKER_SEEDS["v100a"], *WORKER_SEEDS["v100b"])) == list(
        range(4000, 4030)
    )
    for worker in WORKER_SEEDS:
        command = " ".join(
            build_distributed_burgers_command(Path("/experiment"), worker)
        )
        assert "pdebench_burgers_nu0p01_factorial_confirmation" in command
        assert f"burgers_factorial_confirmation_{worker}_20260901.jsonl" in command
        assert f"burgers_factorial_checkpoints_{worker}_20260901" in command


def _analysis_record(seed: int, mechanism: str, value: float) -> dict[str, object]:
    return {
        "stage": "external_confirmation",
        "benchmark_id": "benchmark",
        "protocol_sha256": "a" * 64,
        "schema_amendment_sha256": "c" * 64,
        "data_lock_sha256": "b" * 64,
        "seed": seed,
        "mechanism": mechanism,
        "run_id": f"{seed}-{mechanism}",
        "derived_from": f"{seed}-free" if mechanism == "projection" else None,
        "training_subset": {"index_sha256": f"subset-{seed}"},
        "compute": {"trainable_parameters": 100},
        "cases": {"ood_r512": {"16": {"conserving_rmse": value}, "1": {"conserving_rmse": value}}},
    }


def test_frozen_analyzer_validates_pairs_and_primary_rule() -> None:
    seeds = list(range(2000, 2030))
    values = {"free": 2.0, "free_res": 1.0, "hard": 1.02, "soft30": 2.5, "projection": 2.0}
    records = [
        _analysis_record(seed, mechanism, value)
        for seed in seeds
        for mechanism, value in values.items()
    ]
    config = {
        "benchmark_id": "benchmark",
        "protocol_sha256": "a" * 64,
        "schema_amendment_sha256": "c" * 64,
        "dataset": {"lock_sha256": "b" * 64},
        "seeds": seeds,
        "evaluation": {"case_names": ["ood_r512"]},
    }
    indexed = validate_records(records, config)
    primary = analyze_comparison(indexed, seeds, "ood_r512", 16)
    assert primary["hard_free_res_equivalent"] is True
    assert primary["parameterization_effect_nonzero"] is True
    assert primary["attribution_rule_passed"] is True


def test_sign_flip_pvalue_is_deterministic() -> None:
    values = np.linspace(0.1, 0.4, 30)
    first = paired_sign_flip_pvalue(values, seed=7, draws=2_000)
    second = paired_sign_flip_pvalue(values, seed=7, draws=2_000)
    assert first == second
    assert first < 0.01


def _factorial_record(
    seed: int,
    mechanism: str,
    value: float,
    *,
    protocol_path: str,
    decision_path: str,
    lock_path: str,
) -> dict[str, object]:
    free_run_id = f"{seed}-free"
    return {
        "stage": "factorial_confirmation",
        "benchmark_id": "factorial-benchmark",
        "protocol_sha256": "a" * 64,
        "schema_amendment_sha256": "b" * 64,
        "data_lock_sha256": "c" * 64,
        "seed": seed,
        "mechanism": mechanism,
        "run_id": f"{seed}-{mechanism}",
        "derived_from": free_run_id if mechanism == "projection" else None,
        "training_index_sha256": f"subset-{seed}",
        "training_subset": {"index_sha256": f"subset-{seed}"},
        "initialization_sha256": f"{seed:064x}",
        "compute": {
            "trainable_parameters": 100,
            "optimization_runs": 0 if mechanism == "projection" else 1,
        },
        "cases": {
            "ood_r512": {
                "1": {
                    "conserving_rmse": value,
                    "total_rmse": value,
                    "mean_abs_invariant_drift": 0.0,
                    "max_abs_invariant_drift": 0.0,
                }
            }
        },
        "provenance": {
            "git_head": "d" * 40,
            "git_dirty": True,
            "source_sha256": {
                protocol_path: "a" * 64,
                decision_path: "e" * 64,
                lock_path: "c" * 64,
            },
        },
    }


def _factorial_analysis_fixture() -> tuple[list[dict[str, object]], dict[str, object]]:
    seeds = list(range(3000, 3030))
    protocol_path = "papers/proposal/factorial.md"
    decision_path = "research/discovery/decisions/factorial.yaml"
    lock_path = "experiments/data_lock.json"
    values = {
        "free": 4.0,
        "free_res": 2.0,
        "hard_abs": 2.5,
        "hard": 2.0,
        "projection": 4.0,
    }
    records = [
        _factorial_record(
            seed,
            mechanism,
            value,
            protocol_path=protocol_path,
            decision_path=decision_path,
            lock_path=lock_path,
        )
        for seed in seeds
        for mechanism, value in values.items()
    ]
    config: dict[str, object] = {
        "stage": "factorial_confirmation",
        "benchmark_id": "factorial-benchmark",
        "protocol_path": protocol_path,
        "protocol_sha256": "a" * 64,
        "decision_path": decision_path,
        "schema_amendment_sha256": "b" * 64,
        "expected_git_head": "d" * 40,
        "expected_git_dirty": True,
        "dataset": {"lock_path": lock_path, "lock_sha256": "c" * 64},
        "seeds": seeds,
        "evaluation": {
            "case_names": ["ood_r512"],
            "horizons": [1],
            "primary_case": "ood_r512",
            "primary_horizon": 1,
        },
        "factorial_analysis": {
            "bootstrap_draws": 2000,
            "sign_flip_draws": 2000,
            "confidence_nonzero": 0.95,
            "confidence_equivalence": 0.90,
            "sesoi_fraction_of_free_res": 0.10,
            "invariant_drift_atol": 0.0001,
            "shapley_efficiency_atol": 1e-12,
        },
    }
    return records, config


def test_factorial_analyzer_detects_material_path_dependence() -> None:
    records, config = _factorial_analysis_fixture()
    result = analyze_factorial_records(records, config)
    primary = result["primary"]
    assert result["record_count"] == 150
    assert primary["interaction"]["mean"] == pytest.approx(1.5)
    assert primary["interaction"]["classification"] == "material_nonadditivity"
    assert primary["credits"]["shapley_parameterization"]["mean"] == pytest.approx(
        1.25
    )
    assert primary["credits"]["shapley_enforcement"]["mean"] == pytest.approx(0.75)
    assert primary["max_abs_shapley_efficiency_error"] <= 1e-12


def test_factorial_analyzer_rejects_unpaired_initialization() -> None:
    records, config = _factorial_analysis_fixture()
    records[2]["initialization_sha256"] = "f" * 64
    with pytest.raises(RuntimeError, match="initialization digest"):
        validate_factorial_records(records, config)


def _cube_analysis_fixture() -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, object],
    dict[str, object],
    str,
    str,
    str,
]:
    core_records, config = _factorial_analysis_fixture()
    config["evaluation"] = {
        "case_names": ["ood_r512"],
        "horizons": [1, 16],
        "primary_case": "ood_r512",
        "primary_horizon": 16,
    }
    cube_protocol = "papers/proposal/cube.md"
    cube_runtime = "papers/proposal/cube-runtime.md"
    cube_decision = "research/discovery/decisions/cube.yaml"
    checkpoint_lock_path = "experiments/checkpoint-lock.json"
    config["cube"] = {
        "stage": "enforcement_cube_smoke",
        "schema_version": "constraint-iclr-pdebench-enforcement-cube-v1",
        "output": "experiments/cube.jsonl",
        "checkpoint_lock": checkpoint_lock_path,
        "core_analysis": "experiments/core-analysis.json",
        "protocol_path": cube_protocol,
        "protocol_sha256": "f" * 64,
        "runtime_amendment_path": cube_runtime,
        "runtime_amendment_sha256": "1" * 64,
        "decision_path": cube_decision,
        "decision_sha256": "2" * 64,
        "trained_parent_mechanisms": ["free", "free_res", "hard_abs", "hard"],
        "derived_mechanisms": [
            "projection_res",
            "hard_abs_unprojected",
            "hard_res_unprojected",
        ],
        "expected_core_records": 150,
        "expected_trained_checkpoints": 120,
        "expected_derived_records": 90,
        "checkpoint_schema_version": "constraint-iclr-pdebench-v1",
        "checkpoint_lock_schema_version": (
            "constraint-iclr-pdebench-checkpoint-lock-v1"
        ),
        "checkpoint_completed_epochs": 200,
        "algebra_atol": 1e-12,
    }
    values_h16 = {
        "free": 4.0,
        "free_res": 2.0,
        "projection": 3.5,
        "hard_abs": 2.5,
        "hard": 2.0,
    }
    trained = {"free", "free_res", "hard_abs", "hard"}
    for record in core_records:
        mechanism = str(record["mechanism"])
        h1 = float(record["cases"]["ood_r512"]["1"]["conserving_rmse"])
        record["cases"]["ood_r512"]["1"].update(
            {
                "total_rmse": h1,
                "mean_abs_invariant_drift": 0.0,
                "max_abs_invariant_drift": 0.0,
            }
        )
        record["cases"]["ood_r512"]["16"] = {
            "conserving_rmse": values_h16[mechanism],
            "total_rmse": values_h16[mechanism],
            "mean_abs_invariant_drift": 0.0,
            "max_abs_invariant_drift": 0.0,
        }
        if mechanism in trained:
            record["checkpoint"] = {
                "path": f"checkpoints/{record['run_id']}.pt"
            }

    core_records_sha256 = "3" * 64
    core_analysis_sha256 = "4" * 64
    checkpoint_lock_sha256 = "5" * 64
    checkpoints = []
    core_index = {
        (int(record["seed"]), str(record["mechanism"])): record
        for record in core_records
    }
    for seed in config["seeds"]:
        for mechanism in config["cube"]["trained_parent_mechanisms"]:
            parent = core_index[(seed, mechanism)]
            checkpoints.append(
                {
                    "seed": seed,
                    "mechanism": mechanism,
                    "run_id": parent["run_id"],
                    "path": parent["checkpoint"]["path"],
                    "bytes": 12345,
                    "sha256": f"{seed - 2999:064x}",
                    "payload_schema_version": "constraint-iclr-pdebench-v1",
                    "completed_epochs": 200,
                }
            )
    checkpoint_lock = {
        "schema_version": "constraint-iclr-pdebench-checkpoint-lock-v1",
        "benchmark_id": config["benchmark_id"],
        "core_records": {
            "path": "core.jsonl",
            "sha256": core_records_sha256,
            "record_count": 150,
        },
        "core_analysis": {
            "path": "core-analysis.json",
            "sha256": core_analysis_sha256,
        },
        "checkpoints": checkpoints,
    }
    checkpoint_index = {
        (int(entry["seed"]), str(entry["mechanism"])): entry
        for entry in checkpoints
    }
    derived_h16 = {
        "projection_res": 1.5,
        "hard_abs_unprojected": 3.0,
        "hard_res_unprojected": 2.0,
    }
    parent_for = {
        "projection_res": "free_res",
        "hard_abs_unprojected": "hard_abs",
        "hard_res_unprojected": "hard",
    }
    forward_for = {
        "projection_res": "free_res",
        "hard_abs_unprojected": "free",
        "hard_res_unprojected": "free_res",
    }
    projected_for = {
        "projection_res": True,
        "hard_abs_unprojected": False,
        "hard_res_unprojected": False,
    }
    source_manifest = {
        cube_protocol: "f" * 64,
        cube_runtime: "1" * 64,
        cube_decision: "2" * 64,
        checkpoint_lock_path: checkpoint_lock_sha256,
        str(config["dataset"]["lock_path"]): config["dataset"]["lock_sha256"],
    }
    derived_records = []
    for seed in config["seeds"]:
        for mechanism in config["cube"]["derived_mechanisms"]:
            parent_mechanism = parent_for[mechanism]
            parent = core_index[(seed, parent_mechanism)]
            checkpoint = checkpoint_index[(seed, parent_mechanism)]
            parent_h1 = float(
                parent["cases"]["ood_r512"]["1"]["conserving_rmse"]
            )
            derived_records.append(
                {
                    "schema_version": "constraint-iclr-pdebench-enforcement-cube-v1",
                    "stage": "enforcement_cube_smoke",
                    "benchmark_id": config["benchmark_id"],
                    "data_lock_sha256": config["dataset"]["lock_sha256"],
                    "factorial_protocol_sha256": config["protocol_sha256"],
                    "cube_protocol_sha256": "f" * 64,
                    "cube_runtime_amendment_sha256": "1" * 64,
                    "core_records_sha256": core_records_sha256,
                    "core_analysis_sha256": core_analysis_sha256,
                    "checkpoint_lock_sha256": checkpoint_lock_sha256,
                    "seed": seed,
                    "mechanism": mechanism,
                    "run_id": f"cube-{seed}-{mechanism}",
                    "derived_from": parent["run_id"],
                    "forward_map": forward_for[mechanism],
                    "inference_projected": projected_for[mechanism],
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
                        "initialization_sha256": parent[
                            "initialization_sha256"
                        ],
                        "provenance_sha256": canonical_object_sha256(
                            parent["provenance"]
                        ),
                    },
                    "compute": {
                        "trainable_parameters": 100,
                        "examples_seen": 0,
                        "proxy": 0,
                        "training_runtime_seconds": 0.0,
                        "evaluation_runtime_seconds": 1.0,
                        "peak_gpu_memory_bytes": None,
                        "optimization_runs": 0,
                    },
                    "cases": {
                        "ood_r512": {
                            "1": {
                                "conserving_rmse": parent_h1,
                                "total_rmse": parent_h1,
                                "mean_abs_invariant_drift": 0.0,
                                "max_abs_invariant_drift": 0.0,
                            },
                            "16": {
                                "conserving_rmse": derived_h16[mechanism],
                                "total_rmse": derived_h16[mechanism],
                                "mean_abs_invariant_drift": 0.0,
                                "max_abs_invariant_drift": 0.0,
                            },
                        }
                    },
                    "projection_identity_max_abs_by_case": (
                        {"ood_r512": 0.0}
                        if projected_for[mechanism]
                        else {}
                    ),
                    "provenance": {
                        "git_head": config["expected_git_head"],
                        "git_dirty": config["expected_git_dirty"],
                        "source_sha256": source_manifest,
                    },
                }
            )
    return (
        core_records,
        derived_records,
        checkpoint_lock,
        config,
        core_records_sha256,
        core_analysis_sha256,
        checkpoint_lock_sha256,
    )


def test_enforcement_cube_recovers_training_and_inference_credits() -> None:
    (
        core_records,
        derived_records,
        checkpoint_lock,
        config,
        core_sha256,
        core_analysis_sha256,
        checkpoint_lock_sha256,
    ) = _cube_analysis_fixture()
    result = analyze_enforcement_cube(
        derived_records,
        core_records,
        checkpoint_lock,
        config,
        core_records_sha256=core_sha256,
        core_analysis_sha256=core_analysis_sha256,
        checkpoint_lock_sha256=checkpoint_lock_sha256,
    )
    primary = result["primary"]
    assert result["derived_record_count"] == 90
    assert primary["effects"]["I_bundle"]["mean"] == pytest.approx(1.5)
    assert primary["effects"]["T0"]["mean"] == pytest.approx(1.0)
    assert primary["effects"]["T1"]["mean"] == pytest.approx(1.5)
    assert primary["effects"]["E0"]["mean"] == pytest.approx(0.0)
    assert primary["effects"]["E1"]["mean"] == pytest.approx(0.5)
    assert primary["effects"]["J"]["mean"] == pytest.approx(-0.5)
    assert primary["effects"]["phi_train"]["mean"] == pytest.approx(1.25)
    assert primary["effects"]["phi_infer"]["mean"] == pytest.approx(0.25)
    assert primary["max_abs_three_way_path_identity_error"] <= 1e-12
    assert primary["max_abs_shapley_efficiency_error"] <= 1e-12


def test_enforcement_cube_rejects_parent_checkpoint_tamper() -> None:
    (
        core_records,
        derived_records,
        checkpoint_lock,
        config,
        core_sha256,
        core_analysis_sha256,
        checkpoint_lock_sha256,
    ) = _cube_analysis_fixture()
    derived_records[0]["parent"]["checkpoint_sha256"] = "0" * 64
    with pytest.raises(RuntimeError, match="checkpoint_sha256"):
        validate_cube_records(
            derived_records,
            core_records,
            checkpoint_lock,
            config,
            core_records_sha256=core_sha256,
            core_analysis_sha256=core_analysis_sha256,
            checkpoint_lock_sha256=checkpoint_lock_sha256,
        )


def test_enforcement_cube_rejects_nonzero_optimization_or_missing_cell() -> None:
    (
        core_records,
        derived_records,
        checkpoint_lock,
        config,
        core_sha256,
        core_analysis_sha256,
        checkpoint_lock_sha256,
    ) = _cube_analysis_fixture()
    derived_records[0]["compute"]["optimization_runs"] = 1
    with pytest.raises(RuntimeError, match="nonzero optimization_runs"):
        validate_cube_records(
            derived_records,
            core_records,
            checkpoint_lock,
            config,
            core_records_sha256=core_sha256,
            core_analysis_sha256=core_analysis_sha256,
            checkpoint_lock_sha256=checkpoint_lock_sha256,
        )
    derived_records, *_ = _cube_analysis_fixture()[1:]
    with pytest.raises(RuntimeError, match="derived coverage mismatch"):
        validate_cube_records(
            derived_records[:-1],
            core_records,
            checkpoint_lock,
            config,
            core_records_sha256=core_sha256,
            core_analysis_sha256=core_analysis_sha256,
            checkpoint_lock_sha256=checkpoint_lock_sha256,
        )


def test_enforcement_cube_runner_end_to_end_uses_zero_training(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ECOPHYS_GIT_HEAD", "d" * 40)
    monkeypatch.setenv("ECOPHYS_DIRTY", "1")
    root = Path(__file__).resolve().parents[1]
    dataset_path = tmp_path / "cube-smoke.hdf5"
    dataset_config = _write_synthetic_hdf5(
        dataset_path, trajectories=10, times=21, resolution=16
    )
    dataset_config.update(
        {"restriction_method": "block_average", "restriction_identity_atol": 1e-6}
    )
    protocol_path = tmp_path / "factorial-protocol.md"
    schema_path = tmp_path / "schema.md"
    decision_path = tmp_path / "factorial-decision.yaml"
    schema_decision_path = tmp_path / "schema-decision.yaml"
    cube_protocol_path = tmp_path / "cube-protocol.md"
    cube_runtime_path = tmp_path / "cube-runtime.md"
    cube_decision_path = tmp_path / "cube-decision.yaml"
    for path, text in (
        (protocol_path, "factorial protocol\n"),
        (schema_path, "schema protocol\n"),
        (decision_path, "status: authorized\n"),
        (schema_decision_path, "status: authorized\n"),
        (cube_protocol_path, "cube protocol\n"),
        (cube_runtime_path, "cube runtime\n"),
        (cube_decision_path, "status: authorized\n"),
    ):
        path.write_text(text, encoding="utf-8")
    inspection = inspect_public_dataset(dataset_path, dataset_config)
    lock_path = tmp_path / "data-lock.json"
    lock = {
        "schema_version": "constraint-iclr-pdebench-data-lock-v1",
        "benchmark_id": "synthetic-cube",
        "protocol_sha256": sha256_file(protocol_path),
        "schema_amendment_sha256": sha256_file(schema_path),
        "inspection": inspection,
    }
    lock_path.write_text(
        json.dumps(lock, sort_keys=True) + "\n", encoding="utf-8"
    )
    core_path = tmp_path / "core.jsonl"
    checkpoint_dir = tmp_path / "checkpoints"
    core_analysis_path = tmp_path / "core-analysis.json"
    cube_output_path = tmp_path / "cube.jsonl"
    checkpoint_lock_path = tmp_path / "checkpoint-lock.json"
    config = OmegaConf.create(
        {
            "stage": "factorial_confirmation",
            "benchmark_id": "synthetic-cube",
            "data_lock_protocol_sha256": sha256_file(protocol_path),
            "expected_git_head": "d" * 40,
            "expected_git_dirty": True,
            "dataset": {
                "path": str(dataset_path),
                **dataset_config,
                "lock_path": str(lock_path),
                "lock_sha256": sha256_file(lock_path),
                "lock_benchmark_id": "synthetic-cube",
            },
            "split": {
                "confirmation_start": 0,
                "confirmation_count": 2,
                "train_pool_start": 2,
                "train_pool_stop": 10,
                "train_trajectories_per_seed": 4,
            },
            "model": {
                "history": 2,
                "modes": 2,
                "width": 4,
                "padding": 1,
                "projection_width": 8,
            },
            "training": {
                "epochs": 1,
                "batch_size": 2,
                "learning_rate": 0.001,
                "weight_decay": 0.0001,
                "scheduler_step": 1,
                "scheduler_gamma": 0.5,
                "temporal_stride": 5,
                "spatial_stride": 4,
                "restriction_method": "block_average",
                "checkpoint_every_epochs": 1,
            },
            "evaluation": {
                "spatial_strides": [4, 2, 1],
                "restriction_method": "block_average",
                "case_names": ["id_r4", "ood_r8", "ood_r16"],
                "horizons": [1, 2],
                "batch_size": 2,
                "primary_case": "ood_r8",
                "primary_horizon": 2,
            },
            "mechanisms": ["free", "free_res", "hard_abs", "hard"],
            "soft_weight": 30.0,
            "seeds": [5],
            "device": "cpu",
            "output": str(core_path),
            "checkpoint_dir": str(checkpoint_dir),
            "protocol_path": str(protocol_path),
            "protocol_sha256": sha256_file(protocol_path),
            "schema_amendment_path": str(schema_path),
            "schema_amendment_sha256": sha256_file(schema_path),
            "decision_path": str(decision_path),
            "schema_decision_path": str(schema_decision_path),
            "incident_path": str(
                root
                / "experiments/constraint_attribution_iclr/deployment/"
                "pilot_ood_accidental_exposure_20260831.yaml"
            ),
            "factorial_analysis": {
                "bootstrap_draws": 200,
                "sign_flip_draws": 200,
                "confidence_nonzero": 0.95,
                "confidence_equivalence": 0.90,
                "sesoi_fraction_of_free_res": 0.10,
                "invariant_drift_atol": 1e-5,
                "shapley_efficiency_atol": 1e-12,
            },
            "cube": {
                "stage": "enforcement_cube_smoke",
                "schema_version": (
                    "constraint-iclr-pdebench-enforcement-cube-v1"
                ),
                "output": str(cube_output_path),
                "checkpoint_lock": str(checkpoint_lock_path),
                "core_analysis": str(core_analysis_path),
                "protocol_path": str(cube_protocol_path),
                "protocol_sha256": sha256_file(cube_protocol_path),
                "runtime_amendment_path": str(cube_runtime_path),
                "runtime_amendment_sha256": sha256_file(cube_runtime_path),
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
                "checkpoint_schema_version": "constraint-iclr-pdebench-v1",
                "checkpoint_lock_schema_version": (
                    "constraint-iclr-pdebench-checkpoint-lock-v1"
                ),
                "checkpoint_completed_epochs": 1,
                "algebra_atol": 1e-12,
            },
        }
    )
    run(config)
    core_analysis_path.write_text(
        json.dumps(
            {
                "input_sha256": sha256_file(core_path),
                "integrity_gates_passed": True,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    run_cube(config)
    derived = [
        json.loads(line) for line in cube_output_path.read_text().splitlines()
    ]
    assert len(derived) == 3
    assert checkpoint_lock_path.is_file()
    assert all(record["compute"]["optimization_runs"] == 0 for record in derived)
    assert all(record["compute"]["examples_seen"] == 0 for record in derived)
    checkpoint_lock = json.loads(checkpoint_lock_path.read_text())
    validate_cube_records(
        derived,
        [json.loads(line) for line in core_path.read_text().splitlines()],
        checkpoint_lock,
        OmegaConf.to_container(config, resolve=True),
        core_records_sha256=sha256_file(core_path),
        core_analysis_sha256=sha256_file(core_analysis_path),
        checkpoint_lock_sha256=sha256_file(checkpoint_lock_path),
    )


def test_gradient_coupling_v4_targets_training_interaction_not_bundle() -> None:
    (
        core_records,
        cube_records,
        checkpoint_lock,
        config,
        core_sha256,
        core_analysis_sha256,
        checkpoint_lock_sha256,
    ) = _cube_analysis_fixture()
    gradient_protocol_path = "papers/proposal/gradient.md"
    gradient_decision_path = "research/discovery/decisions/gradient.yaml"
    config.update(
        {
            "gradient_protocol_path": gradient_protocol_path,
            "gradient_protocol_sha256": "g" * 64,
            "gradient_decision_path": gradient_decision_path,
        }
    )
    lock_path = str(config["dataset"]["lock_path"])
    diagnostic_records = []
    for index, seed in enumerate(config["seeds"]):
        shift = index * 0.002
        for record in core_records:
            if record["seed"] == seed and record["mechanism"] == "projection":
                record["cases"]["ood_r512"]["16"]["conserving_rmse"] += shift
                record["cases"]["ood_r512"]["16"]["total_rmse"] += shift
        for coordinate, credit in (
            ("absolute", 0.01 + shift),
            ("residual", 0.005),
        ):
            diagnostic_records.append(
                {
                    "schema_version": "constraint-iclr-gradient-coupling-v1",
                    "benchmark_id": config["benchmark_id"],
                    "data_lock_sha256": config["dataset"]["lock_sha256"],
                    "factorial_protocol_sha256": config["protocol_sha256"],
                    "gradient_protocol_sha256": config[
                        "gradient_protocol_sha256"
                    ],
                    "seed": seed,
                    "coordinate": coordinate,
                    "run_id": f"gradient-v4-{seed}-{coordinate}",
                    "batch": {
                        "same": seed,
                        "training_index_sha256": f"subset-{seed}",
                    },
                    "initialization_sha256": f"{seed:064x}",
                    "losses_before": {
                        "total": 0.3,
                        "conserving": 0.2,
                        "violating": 0.1,
                        "decomposition_abs_error": 0.0,
                    },
                    "gradients": {
                        "q_norm": 1.0,
                        "p_norm": 1.0,
                        "inner_product": -0.2,
                        "cosine": -0.2,
                    },
                    "one_step": {
                        "free_training_loss": 0.3,
                        "hard_training_loss": 0.2,
                        "free_conserving_loss_after": 1.0 + credit,
                        "hard_conserving_loss_after": 1.0,
                        "one_step_enforcement_credit": credit,
                    },
                    "provenance": {
                        "git_head": config["expected_git_head"],
                        "git_dirty": config["expected_git_dirty"],
                        "source_sha256": {
                            gradient_protocol_path: "g" * 64,
                            gradient_decision_path: "h" * 64,
                            lock_path: config["dataset"]["lock_sha256"],
                        },
                    },
                }
            )
    result = analyze_gradient_coupling_v4(
        diagnostic_records,
        core_records,
        cube_records,
        checkpoint_lock,
        config,
        factorial_records_sha256=core_sha256,
        factorial_analysis_sha256=core_analysis_sha256,
        checkpoint_lock_sha256=checkpoint_lock_sha256,
    )
    assert result["primary_mechanistic_association"]["rho"] == pytest.approx(1.0)
    assert result["primary_mechanistic_association"]["classification"] == (
        "positive_mechanism_support"
    )
    assert result["secondary_bundled_association"]["estimable"] is False


def test_gradient_coupling_analyzer_requires_pairs_and_recovers_positive_link() -> None:
    factorial_records, config = _factorial_analysis_fixture()
    gradient_protocol_path = "papers/proposal/gradient.md"
    gradient_decision_path = "research/discovery/decisions/gradient.yaml"
    config.update(
        {
            "gradient_protocol_path": gradient_protocol_path,
            "gradient_protocol_sha256": "g" * 64,
            "gradient_decision_path": gradient_decision_path,
        }
    )
    lock_path = str(config["dataset"]["lock_path"])
    diagnostic_records = []
    for index, seed in enumerate(config["seeds"]):
        d_absolute = 0.01 + index * 0.001
        d_residual = 0.005
        for coordinate, credit in (
            ("absolute", d_absolute),
            ("residual", d_residual),
        ):
            diagnostic_records.append(
                {
                    "schema_version": "constraint-iclr-gradient-coupling-v1",
                    "benchmark_id": config["benchmark_id"],
                    "data_lock_sha256": config["dataset"]["lock_sha256"],
                    "factorial_protocol_sha256": config["protocol_sha256"],
                    "gradient_protocol_sha256": config["gradient_protocol_sha256"],
                    "seed": seed,
                    "coordinate": coordinate,
                    "run_id": f"gradient-{seed}-{coordinate}",
                    "batch": {
                        "same": seed,
                        "training_index_sha256": f"subset-{seed}",
                    },
                    "initialization_sha256": f"{seed:064x}",
                    "losses_before": {
                        "total": 0.3,
                        "conserving": 0.2,
                        "violating": 0.1,
                        "decomposition_abs_error": 0.0,
                    },
                    "gradients": {
                        "q_norm": 1.0,
                        "p_norm": 1.0,
                        "inner_product": -0.2,
                        "cosine": -0.2,
                    },
                    "one_step": {
                        "free_training_loss": 0.3,
                        "hard_training_loss": 0.2,
                        "free_conserving_loss_after": 1.0 + credit,
                        "hard_conserving_loss_after": 1.0,
                        "one_step_enforcement_credit": credit,
                    },
                    "provenance": {
                        "git_head": config["expected_git_head"],
                        "git_dirty": config["expected_git_dirty"],
                        "source_sha256": {
                            gradient_protocol_path: "g" * 64,
                            gradient_decision_path: "h" * 64,
                            lock_path: config["dataset"]["lock_sha256"],
                        },
                    },
                }
            )
        shift = index * 0.002
        for record in factorial_records:
            if record["seed"] == seed and record["mechanism"] in {
                "free",
                "projection",
            }:
                record["cases"]["ood_r512"]["1"]["conserving_rmse"] += shift
                record["cases"]["ood_r512"]["1"]["total_rmse"] += shift
    indexed = validate_diagnostic_records(diagnostic_records, config)
    assert len(indexed) == 60
    result = analyze_gradient_coupling(
        diagnostic_records, factorial_records, config
    )
    assert result["record_count"] == 60
    association = result["primary_mechanistic_association"]
    assert association["rho"] == pytest.approx(1.0)
    assert association["classification"] == "positive_mechanism_support"

    wrong_subset = json.loads(json.dumps(diagnostic_records))
    wrong_subset[0]["batch"]["training_index_sha256"] = "wrong-subset"
    wrong_subset[1]["batch"]["training_index_sha256"] = "wrong-subset"
    with pytest.raises(RuntimeError, match="training-index mismatch"):
        analyze_gradient_coupling(wrong_subset, factorial_records, config)

    wrong_initialization = json.loads(json.dumps(diagnostic_records))
    wrong_initialization[0]["initialization_sha256"] = "0" * 64
    wrong_initialization[1]["initialization_sha256"] = "0" * 64
    with pytest.raises(RuntimeError, match="initialization mismatch"):
        analyze_gradient_coupling(wrong_initialization, factorial_records, config)

    split_source_manifest = json.loads(json.dumps(diagnostic_records))
    split_source_manifest[0]["provenance"]["source_sha256"]["unexpected.py"] = "x" * 64
    with pytest.raises(RuntimeError, match="one exact source"):
        validate_diagnostic_records(split_source_manifest, config)


def test_spearman_bootstrap_reranks_within_each_resample() -> None:
    x = np.asarray([0.0, 1.0, 3.0, 8.0, 9.0, 15.0])
    y = np.asarray([0.0, 4.0, 1.0, 5.0, 2.0, 3.0])
    draws = 4000
    seed = 713

    def average_ranks(values: np.ndarray) -> np.ndarray:
        order = np.argsort(values, kind="mergesort")
        ranks = np.empty(values.size, dtype=np.float64)
        start = 0
        while start < values.size:
            stop = start + 1
            while stop < values.size and values[order[stop]] == values[order[start]]:
                stop += 1
            ranks[order[start:stop]] = 0.5 * (start + stop - 1) + 1.0
            start = stop
        return ranks

    rng = np.random.default_rng(seed)
    indices = rng.integers(0, x.size, size=(draws, x.size))
    correlations = []
    for row in indices:
        ranks_x = average_ranks(x[row])
        ranks_y = average_ranks(y[row])
        if np.std(ranks_x) == 0.0 or np.std(ranks_y) == 0.0:
            continue
        correlations.append(float(np.corrcoef(ranks_x, ranks_y)[0, 1]))
    expected = np.quantile(np.asarray(correlations), [0.025, 0.975])

    result = spearman_bootstrap(x, y, draws=draws, seed=seed)
    assert result["estimable"] is True
    assert result["valid_bootstrap_draws"] == len(correlations)
    assert result["ci95"] == pytest.approx(expected, abs=1e-12)


def test_gradient_coupling_analyzer_rejects_unpaired_batches() -> None:
    _, config = _factorial_analysis_fixture()
    config.update(
        {
            "gradient_protocol_path": "gradient.md",
            "gradient_protocol_sha256": "g" * 64,
            "gradient_decision_path": "gradient.yaml",
        }
    )
    seed = config["seeds"][0]
    records = [
        {
            "schema_version": "constraint-iclr-gradient-coupling-v1",
            "benchmark_id": config["benchmark_id"],
            "data_lock_sha256": config["dataset"]["lock_sha256"],
            "factorial_protocol_sha256": config["protocol_sha256"],
            "gradient_protocol_sha256": config["gradient_protocol_sha256"],
            "seed": seed,
            "coordinate": coordinate,
            "run_id": f"{seed}-{coordinate}",
            "batch": {"different": coordinate},
            "initialization_sha256": "i" * 64,
            "losses_before": {"total": 0.3, "conserving": 0.2, "violating": 0.1},
            "gradients": {
                "q_norm": 1.0,
                "p_norm": 1.0,
                "inner_product": 0.0,
                "cosine": 0.0,
            },
            "one_step": {
                "free_conserving_loss_after": 0.2,
                "hard_conserving_loss_after": 0.2,
                "one_step_enforcement_credit": 0.0,
            },
            "provenance": {
                "git_head": config["expected_git_head"],
                "git_dirty": config["expected_git_dirty"],
                "source_sha256": {
                    config["gradient_protocol_path"]: "g" * 64,
                    config["gradient_decision_path"]: "h" * 64,
                    config["dataset"]["lock_path"]: "c" * 64,
                },
            },
        }
        for coordinate in ("absolute", "residual")
    ]
    with pytest.raises(RuntimeError, match="missing seed/coordinate pairs"):
        validate_diagnostic_records(records, config)


def test_factorial_shard_merge_preserves_lines_and_orders_seed_mechanism(
    tmp_path: Path,
) -> None:
    protocol_path = "papers/proposal/factorial.md"
    decision_path = "research/discovery/decisions/factorial.yaml"
    lock_path = "experiments/data_lock.json"
    values = {
        "free": 4.0,
        "projection": 4.0,
        "free_res": 2.0,
        "hard_abs": 2.5,
        "hard": 2.0,
    }
    records = {
        seed: [
            _factorial_record(
                seed,
                mechanism,
                value,
                protocol_path=protocol_path,
                decision_path=decision_path,
                lock_path=lock_path,
            )
            for mechanism, value in values.items()
        ]
        for seed in (1, 2)
    }
    shard_b = tmp_path / "b.jsonl"
    shard_a = tmp_path / "a.jsonl"
    shard_b.write_text(
        "\n".join(json.dumps(record) for record in reversed(records[2])) + "\n",
        encoding="utf-8",
    )
    shard_a.write_text(
        "\n".join(json.dumps(record) for record in reversed(records[1])) + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "merged.jsonl"
    merge_shards(
        [shard_b, shard_a],
        output,
        seeds=(1, 2),
        benchmark_id="factorial-benchmark",
    )
    merged = [json.loads(line) for line in output.read_text().splitlines()]
    assert [(record["seed"], record["mechanism"]) for record in merged] == [
        (seed, mechanism)
        for seed in (1, 2)
        for mechanism in ("free", "projection", "free_res", "hard_abs", "hard")
    ]
    merge_shards(
        [shard_a, shard_b],
        output,
        seeds=(1, 2),
        benchmark_id="factorial-benchmark",
    )

