from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from omegaconf import OmegaConf

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import analyze_constraint_iclr_confirmation_amended as amended_confirmation  # noqa: E402
import constraint_iclr_common as constraint_common  # noqa: E402
from analyze_constraint_iclr import (  # noqa: E402
    CONFIRMATION_SEEDS,
    select_pair,
    select_pilot,
    validate_confirmation_lock,
)
from analyze_constraint_iclr_confirmation_amended import (  # noqa: E402
    COMPLETE_SYSTEMS,
    expected_record_keys,
    validate_amended_confirmation,
)
from constraint_iclr_common import (  # noqa: E402
    bootstrap_mean_ci,
    pde_metrics,
    project_pde_output,
    stable_seed,
)
from launch_constraint_iclr_confirmation import build_commands as build_confirmation_commands  # noqa: E402
from launch_constraint_iclr_pilot import build_commands as build_pilot_commands  # noqa: E402
from run_constraint_iclr_market import (  # noqa: E402
    REGIMES,
    ContinuousDoubleAuction,
    FIFOBook,
    MarketLayout,
    Order,
    Trade,
    market_metrics,
    project_market_delta,
    project_market_output,
)
from run_constraint_iclr_pde import (  # noqa: E402
    MLP,
    UNet,
    make_samples_2d,
    spectral_step_1d,
    spectral_step_2d,
)


def test_stable_seed_is_deterministic_and_namespaced() -> None:
    assert stable_seed(100, "train") == stable_seed(100, "train")
    assert stable_seed(100, "train") != stable_seed(100, "test")
    assert stable_seed(100, "train") != stable_seed(101, "train")


def test_confirmation_partition_is_frozen_at_thirty_seeds() -> None:
    assert set(range(1000, 1030)) == CONFIRMATION_SEEDS


def test_provenance_requires_git_head(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("ECOPHYS_GIT_HEAD", raising=False)
    monkeypatch.delenv("ECOPHYS_DIRTY", raising=False)
    monkeypatch.setattr(constraint_common, "_git_output", lambda _root, _args: None)
    with pytest.raises(RuntimeError, match="ECOPHYS_GIT_HEAD"):
        constraint_common.provenance(root=tmp_path, resolved_config={}, source_files=[])


def test_provenance_requires_dirty_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ECOPHYS_GIT_HEAD", "a" * 40)
    monkeypatch.delenv("ECOPHYS_DIRTY", raising=False)
    monkeypatch.setattr(constraint_common, "_git_output", lambda _root, _args: None)
    with pytest.raises(RuntimeError, match="ECOPHYS_DIRTY"):
        constraint_common.provenance(root=tmp_path, resolved_config={}, source_files=[])


def test_provenance_accepts_explicit_remote_identity(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("ECOPHYS_GIT_HEAD", "b" * 40)
    monkeypatch.setenv("ECOPHYS_DIRTY", "1")
    monkeypatch.setattr(constraint_common, "_git_output", lambda _root, _args: None)
    result = constraint_common.provenance(root=tmp_path, resolved_config={}, source_files=[])
    assert result["git_head"] == "b" * 40
    assert result["git_dirty"] is True


def test_failure_artifact_verification_accepts_attested_identity_redaction(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    decision = tmp_path / "decision.yaml"
    incident = tmp_path / "incident.yaml"
    decision.write_text("host: root@100.80.0.1\n", encoding="utf-8")
    incident.write_text("home: /home/private-user/run\n", encoding="utf-8")
    decision_source = constraint_common.sha256_file(decision)
    incident_source = constraint_common.sha256_file(incident)
    decision.write_text("host: root@redacted-host\n", encoding="utf-8")
    incident.write_text("home: /home/anonymous/run\n", encoding="utf-8")
    decision_release = constraint_common.sha256_file(decision)
    incident_release = constraint_common.sha256_file(incident)
    monkeypatch.setattr(
        amended_confirmation, "EXPECTED_FAILURE_DECISION_SHA256", decision_source
    )
    monkeypatch.setattr(
        amended_confirmation,
        "FAILED_SYSTEMS",
        {
            "test": {
                "incident_path": "incident.yaml",
                "incident_sha256": incident_source,
            }
        },
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "double_blind_redactions": [
                    {
                        "archive_path": None,
                        "path": "decision.yaml",
                        "source_sha256": decision_source,
                        "released_sha256": decision_release,
                    },
                    {
                        "archive_path": None,
                        "path": "incident.yaml",
                        "source_sha256": incident_source,
                        "released_sha256": incident_release,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    result = amended_confirmation.verify_failure_artifacts(
        tmp_path, decision, manifest
    )
    assert result["failure_decision_sha256"] == decision_source
    assert "test" in result["declared_failures"]


def test_selection_lock_is_required_and_hash_checked(tmp_path: Path) -> None:
    lock_path = tmp_path / "pilot_lock.json"
    lock_path.write_text('{"schema_version":"constraint-iclr-lock-v1"}\n', encoding="utf-8")
    lock_sha256 = constraint_common.sha256_file(lock_path)
    resolved = {
        "stage": "confirmation",
        "selection_lock_path": lock_path.name,
        "selection_lock_sha256": lock_sha256,
    }
    assert constraint_common.validate_selection_lock(tmp_path, resolved) == lock_path
    with pytest.raises(RuntimeError, match="SHA-256 mismatch"):
        constraint_common.validate_selection_lock(
            tmp_path, {**resolved, "selection_lock_sha256": "0" * 64}
        )
    with pytest.raises(RuntimeError, match="requires selection_lock_path"):
        constraint_common.validate_selection_lock(tmp_path, {"stage": "confirmation"})
    assert constraint_common.validate_selection_lock(tmp_path, {"stage": "pilot"}) is None


def test_confirmation_analysis_rejects_wrong_lock_binding() -> None:
    expected = "a" * 64
    record = {
        "stage": "confirmation",
        "run_id": "run",
        "selection_lock_sha256": expected,
        "provenance": {
            "resolved_config": {"selection_lock_sha256": expected},
            "source_sha256": {"pilot_lock.json": expected},
        },
    }
    assert validate_confirmation_lock([record], expected) == []
    failures = validate_confirmation_lock([record], "b" * 64)
    assert len(failures) == 3


@pytest.mark.parametrize(
    ("system", "gamma"),
    [
        ("advection", 0.5),
        ("diffusion", 0.5),
        ("burgers", 0.5),
        ("contraction_near", 0.5),
        ("contraction_strong", 50.0),
    ],
)
def test_one_dimensional_truth_preserves_mean(system: str, gamma: float) -> None:
    generator = torch.Generator().manual_seed(7)
    inputs = torch.randn(4, 16, generator=generator)
    outputs = spectral_step_1d(
        inputs,
        system=system,
        c=1.0,
        nu=0.02,
        dt=0.1,
        gamma=gamma,
        burgers_substeps=4,
    )
    torch.testing.assert_close(outputs.mean(-1), inputs.mean(-1), atol=2e-7, rtol=0.0)


def test_two_dimensional_truth_preserves_mean() -> None:
    inputs = torch.randn(3, 8, 8, generator=torch.Generator().manual_seed(4))
    outputs = spectral_step_2d(inputs, c=1.0, nu=0.02, dt=0.1)
    torch.testing.assert_close(outputs.mean((-2, -1)), inputs.mean((-2, -1)), atol=2e-7, rtol=0.0)


def test_two_dimensional_sampler_is_real_and_finite() -> None:
    samples = make_samples_2d(16, 5, 0.1, np.random.default_rng(8))
    assert samples.shape == (5, 16, 16)
    assert torch.isfinite(samples).all()


def test_pde_projection_only_changes_invariant_channel() -> None:
    inputs = torch.randn(5, 12, generator=torch.Generator().manual_seed(1))
    targets = inputs * 0.7 + inputs.mean(-1, keepdim=True) * 0.3
    outputs = torch.randn(5, 12, generator=torch.Generator().manual_seed(2))
    projected = project_pde_output(inputs, outputs)
    torch.testing.assert_close(projected.mean(-1), inputs.mean(-1), atol=2e-7, rtol=0.0)
    before = pde_metrics(outputs, targets)
    after = pde_metrics(projected, targets)
    assert after["conserving_rmse"] == pytest.approx(before["conserving_rmse"], rel=1e-6)


def test_models_preserve_shape_and_hard_delta_mean() -> None:
    one_dimensional = torch.randn(2, 32)
    mlp = MLP(32, 16, "hard")
    mlp_output = mlp(one_dimensional)
    assert mlp_output.shape == one_dimensional.shape
    torch.testing.assert_close(mlp_output.mean(-1), one_dimensional.mean(-1), atol=2e-7, rtol=0.0)

    unet_1d = UNet(8, 1, "hard")
    output_1d = unet_1d(one_dimensional)
    assert output_1d.shape == one_dimensional.shape
    torch.testing.assert_close(output_1d.mean(-1), one_dimensional.mean(-1), atol=2e-7, rtol=0.0)

    two_dimensional = torch.randn(2, 16, 16)
    unet_2d = UNet(8, 2, "hard")
    output_2d = unet_2d(two_dimensional)
    assert output_2d.shape == two_dimensional.shape
    torch.testing.assert_close(
        output_2d.mean((-2, -1)),
        two_dimensional.mean((-2, -1)),
        atol=2e-7,
        rtol=0.0,
    )


def test_fifo_book_uses_price_then_time_priority() -> None:
    book = FIFOBook()
    assert book.submit(Order(agent=3, side="sell", price=100.0, sequence=1)) is None
    assert book.submit(Order(agent=4, side="sell", price=100.0, sequence=2)) is None
    trade = book.submit(Order(agent=0, side="buy", price=101.0, sequence=3))
    assert trade == Trade(buyer=0, seller=3, price=100.0, maker=3, taker=0)

    assert book.submit(Order(agent=5, side="sell", price=99.0, sequence=4)) is None
    trade = book.submit(Order(agent=1, side="buy", price=101.0, sequence=5))
    assert trade is not None
    assert trade.seller == 5
    assert trade.price == 99.0


def test_market_engine_conserves_cash_fee_and_inventory() -> None:
    engine = ContinuousDoubleAuction(
        n_agents=8,
        fee_rate=0.001,
        tick_size=0.1,
        regime=REGIMES["in_support"],
        rng=np.random.default_rng(19),
    )
    initial = engine.invariant_totals()
    trades = 0
    for _ in range(500):
        trades += engine.step() is not None
        assert engine.invariant_totals() == pytest.approx(initial, abs=1e-9, rel=0.0)
    assert trades > 0
    assert engine.fee_account > 0.0


def test_market_projection_only_changes_invariant_channels() -> None:
    layout = MarketLayout(8)
    generator = torch.Generator().manual_seed(9)
    inputs = torch.randn(6, layout.input_dim, generator=generator)
    target = inputs[:, : layout.dynamic_dim].clone()
    raw_output = torch.randn(6, layout.dynamic_dim, generator=generator)
    projected = project_market_output(inputs, raw_output, layout)
    delta = projected - inputs[:, : layout.dynamic_dim]
    assert torch.max(torch.abs(delta[:, layout.cash_slice].sum(-1) + delta[:, layout.fee_index])) < 1e-6
    assert torch.max(torch.abs(delta[:, layout.inventory_slice].sum(-1))) < 1e-6
    projected_error = project_market_delta(raw_output - target, layout)
    torch.testing.assert_close(projected - target, projected_error, atol=2e-6, rtol=0.0)
    before = market_metrics(raw_output, target, layout)
    after = market_metrics(projected, target, layout)
    assert after["conserving_rmse"] == pytest.approx(before["conserving_rmse"], rel=1e-6)


def _summary(config_id: str, identifier: float, compute: float) -> dict[str, object]:
    capacity, epochs, learning_rate = config_id.split("_")
    return {
        "cell": {
            "capacity": int(capacity[1:]),
            "epochs": int(epochs[1:]),
            "learning_rate": float(learning_rate[2:]),
            "config_id": config_id,
        },
        "id_rmse": identifier,
        "compute_proxy": compute,
        "seeds": [100, 101, 102],
    }


def test_selector_prioritizes_id_gap_without_reading_ood() -> None:
    summaries = {
        ("free", "c32_e100_lr0.001"): _summary("c32_e100_lr0.001", 1.0, 100.0),
        ("free", "c64_e100_lr0.001"): _summary("c64_e100_lr0.001", 0.5, 200.0),
        ("free_res", "c32_e100_lr0.001"): _summary("c32_e100_lr0.001", 1.04, 100.0),
        ("free_res", "c64_e100_lr0.001"): _summary("c64_e100_lr0.001", 0.7, 200.0),
    }
    selected = select_pair(summaries, "free", "free_res")
    assert selected["branch"] == "matched_id_compute"
    assert selected["left"]["cell"]["config_id"] == "c32_e100_lr0.001"


def test_selector_uses_same_cell_nonoverlap_branch() -> None:
    summaries = {
        ("free", "c32_e100_lr0.001"): _summary("c32_e100_lr0.001", 1.0, 100.0),
        ("free_res", "c32_e100_lr0.001"): _summary("c32_e100_lr0.001", 0.5, 100.0),
    }
    selected = select_pair(summaries, "free", "free_res")
    assert selected["branch"] == "fixed_compute_nonoverlap"
    assert selected["compute_relative_gap"] == 0.0


def test_pilot_selector_excludes_accidental_bc_learning_rate() -> None:
    records = []
    for learning_rate, free_error, residual_error in (
        (0.001, 1.0, 0.5),
        (0.003, 0.25, 0.25),
    ):
        config_id = f"c8_e100_lr{learning_rate:g}"
        for seed in (100, 101):
            for mechanism, identifier in (("free", free_error), ("free_res", residual_error)):
                records.append(
                    {
                        "stage": "pilot",
                        "family": "B",
                        "system": "advection",
                        "mechanism": mechanism,
                        "config_id": config_id,
                        "capacity": 8,
                        "epochs": 100,
                        "learning_rate": learning_rate,
                        "seed": seed,
                        "id_metrics": {"total_rmse": identifier},
                        "compute": {"proxy": 100.0},
                    }
                )
    selected = select_pilot(records)
    comparison = selected["systems"]["B:advection"]["comparisons"]["free__free_res"]
    assert comparison["branch"] == "fixed_compute_nonoverlap"
    assert comparison["left"]["cell"]["learning_rate"] == pytest.approx(0.001)
    assert selected["pilot_record_policy"]["excluded_records_by_family"]["B"] == 4


def test_paired_bootstrap_is_deterministic() -> None:
    differences = np.array([0.1, 0.2, 0.3, 0.4])
    first = bootstrap_mean_ci(differences, confidence=0.90, draws=2_000)
    second = bootstrap_mean_ci(differences, confidence=0.90, draws=2_000)
    assert first == second
    assert first[0] > 0.0


def test_pilot_launcher_builds_hydra_list_overrides(tmp_path: Path) -> None:
    manifest = {
        "workers": {
            "worker": [
                {
                    "name": "job",
                    "runner": "pde",
                    "config": "pde_pilot",
                    "overrides": {"family": "B", "capacity_grid": [8, 16]},
                }
            ]
        }
    }
    commands = build_pilot_commands(tmp_path, manifest, "worker")
    assert commands[0][0] == "job"
    assert "family=B" in commands[0][1]
    assert "capacity_grid=[8,16]" in commands[0][1]


def test_confirmation_launcher_uses_only_locked_jobs(tmp_path: Path) -> None:
    manifest = {
        "workers": {"worker": ["A:diffusion"]},
        "systems": {
            "A:diffusion": {
                "runner": "pde",
                "config": "pde_confirmation",
                "overrides": {"family": "A", "system": "diffusion"},
            }
        },
    }
    lock = {
        "systems": {
            "A:diffusion": {
                "confirmation_jobs": [
                    {
                        "mechanism": "hard",
                        "capacity": 64,
                        "epochs": 200,
                        "learning_rate": 0.003,
                        "config_id": "c64_e200_lr0.003",
                    }
                ]
            }
        }
    }
    commands = build_confirmation_commands(
        tmp_path,
        manifest,
        lock,
        "worker",
        lock_path=Path("experiments/constraint_attribution_iclr/pilot/final_lock.json"),
        lock_sha256="a" * 64,
    )
    assert len(commands) == 1
    assert "mechanisms=[hard]" in commands[0][1]
    assert "capacity_grid=[64]" in commands[0][1]
    assert "epochs_grid=[200]" in commands[0][1]
    assert (
        "selection_lock_path=experiments/constraint_attribution_iclr/pilot/final_lock.json"
        in commands[0][1]
    )
    assert f"selection_lock_sha256={'a' * 64}" in commands[0][1]


def test_v100a_failure_continuation_is_exactly_scoped() -> None:
    root = SCRIPTS.parent
    manifest_path = (
        root / "configs/constraint_iclr/confirmation_manifest_v100a_continuation_20260831.yaml"
    )
    original_path = root / "configs/constraint_iclr/confirmation_manifest.yaml"
    lock_path = (
        root
        / "experiments/constraint_attribution_iclr/pilot/pilot_lock_final_idonly_20260831.json"
    )
    manifest = OmegaConf.to_container(OmegaConf.load(manifest_path), resolve=True)
    original = OmegaConf.to_container(OmegaConf.load(original_path), resolve=True)
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert isinstance(manifest, dict)
    assert isinstance(original, dict)

    allowed = ["H:contraction_near", "H:contraction_strong", "M2:fifo_cda"]
    assert manifest["workers"] == {"v100a": allowed}
    assert set(manifest["systems"]) == set(allowed)
    for system_key in allowed:
        assert manifest["systems"][system_key] == original["systems"][system_key]

    commands = build_confirmation_commands(
        root,
        manifest,
        lock,
        "v100a",
        lock_path=lock_path.relative_to(root),
        lock_sha256=constraint_common.sha256_file(lock_path),
    )
    assert len(commands) == 18
    assert {name.split(":", 2)[0] for name, _ in commands} == {"H", "M2"}
    assert all("family=A" not in command for _, command in commands)


def test_v100b_c_continuation_is_exactly_scoped() -> None:
    root = SCRIPTS.parent
    manifest_path = (
        root
        / "configs/constraint_iclr/"
        "confirmation_manifest_v100b_c_continuation_20260901.yaml"
    )
    original_path = root / "configs/constraint_iclr/confirmation_manifest.yaml"
    lock_path = (
        root
        / "experiments/constraint_attribution_iclr/pilot/"
        "pilot_lock_final_idonly_20260831.json"
    )
    manifest = OmegaConf.to_container(OmegaConf.load(manifest_path), resolve=True)
    original = OmegaConf.to_container(OmegaConf.load(original_path), resolve=True)
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert isinstance(manifest, dict)
    assert isinstance(original, dict)
    assert manifest["workers"] == {"v100b": ["C:ad2d"]}
    assert manifest["systems"] == {"C:ad2d": original["systems"]["C:ad2d"]}

    commands = build_confirmation_commands(
        root,
        manifest,
        lock,
        "v100b",
        lock_path=lock_path.relative_to(root),
        lock_sha256=constraint_common.sha256_file(lock_path),
    )
    assert len(commands) == 6
    assert all(name.startswith("C:ad2d:") for name, _ in commands)
    assert all("family=C" in command and "system=ad2d" in command for _, command in commands)
    assert all("burgers" not in " ".join(command) for _, command in commands)


def test_amended_confirmation_expects_exactly_1830_records() -> None:
    root = SCRIPTS.parent
    lock = json.loads(
        (
            root
            / "experiments/constraint_attribution_iclr/pilot/"
            "pilot_lock_final_idonly_20260831.json"
        ).read_text(encoding="utf-8")
    )
    expected = expected_record_keys(lock, COMPLETE_SYSTEMS, range(1000, 1030))
    assert len(expected) == 1830
    assert not any(key[0].endswith("burgers") for key in expected)


def test_amended_confirmation_gate_rejects_missing_or_failed_records() -> None:
    lock_hash = "c" * 64
    lock = {
        "systems": {
            "A:advection": {
                "confirmation_jobs": [
                    {"mechanism": "free", "config_id": "c1"},
                    {"mechanism": "hard", "config_id": "c1"},
                ]
            },
            "A:burgers": {"confirmation_jobs": []},
        }
    }

    def record(seed: int, mechanism: str) -> dict[str, object]:
        return {
            "schema_version": "constraint-iclr-v1",
            "stage": "confirmation",
            "family": "A",
            "system": "advection",
            "mechanism": mechanism,
            "config_id": "c1",
            "seed": seed,
            "run_id": f"{seed}-{mechanism}",
            "selection_lock_sha256": lock_hash,
            "provenance": {
                "git_head": "d" * 40,
                "git_dirty": True,
                "source_sha256": {"lock.json": lock_hash},
                "command": ["runner"],
                "resolved_config": {"selection_lock_sha256": lock_hash},
                "hostname": "host",
                "python": "3.11",
                "torch": "2.3",
            },
        }

    records = [
        record(seed, mechanism)
        for seed in (1, 2)
        for mechanism in ("free", "projection", "hard")
    ]
    integrity = validate_amended_confirmation(
        records,
        lock,
        complete_systems=("A:advection",),
        failed_systems=("A:burgers",),
        seeds=(1, 2),
        expected_lock_sha256=lock_hash,
        expected_git_head="d" * 40,
    )
    assert integrity["record_count"] == 6
    with pytest.raises(RuntimeError, match="missing exact locked records"):
        validate_amended_confirmation(
            records[:-1],
            lock,
            complete_systems=("A:advection",),
            failed_systems=("A:burgers",),
            seeds=(1, 2),
            expected_lock_sha256=lock_hash,
            expected_git_head="d" * 40,
        )
    failed_record = {**record(1, "free"), "system": "burgers", "run_id": "failed"}
    with pytest.raises(RuntimeError, match="failed system unexpectedly has a record"):
        validate_amended_confirmation(
            [*records, failed_record],
            lock,
            complete_systems=("A:advection",),
            failed_systems=("A:burgers",),
            seeds=(1, 2),
            expected_lock_sha256=lock_hash,
            expected_git_head="d" * 40,
        )
