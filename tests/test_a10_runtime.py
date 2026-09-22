"""A10 pairing and private checkpoint checks on remote, nonproduction fixtures."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import torch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts/reexploration"))
import train_a10_d0s4 as audit
import train_stage1_d0s3 as training
import eval_a10_d0s4 as audit_eval


def test_paired_audit_loop_and_metadata(tmp_path: Path) -> None:
    torch.set_num_threads(1)
    data = tmp_path / "data"
    training.stage_seed_episodes({"job": {
        "repo_root": str(REPO), "seed_root": 999, "lineage": "l1",
        "config": training.load_dgp_config(REPO), "dir": str(data),
        "episode_start": 64, "n_train": 2, "workers": 1,
    }})
    arm = training.load_arm(REPO, audit.ARM_ID)
    parent_job = {
        "repo_root": str(REPO), "arm": arm, "arm_id": audit.ARM_ID,
        "lineage": "l1", "block_id": "B1", "seed_root": 999,
        "n_train": 2, "n_iters": 2, "episode_start": 64,
        "through_m_coordinate_mode": "differentiated", "device": "cpu",
        "train_dir": str(data), "job_dir": str(tmp_path / "st"),
        "git_sha": training.git_head(REPO), "production_constants_decision": "private_unit_fixture",
    }
    parent_entry = training.train_one(parent_job)
    audit_job = {
        **parent_job, "arm": {**arm, "estimator": "perturb_and_map"},
        "job_dir": str(tmp_path / "pam"), "st_checkpoint": str(tmp_path / "st/checkpoint.lock"),
        "st_checkpoint_sha256": parent_entry["checkpoint_sha256"],
    }
    training.train_one(audit_job)
    receipt = audit.accept_audit_job(audit_job)
    assert receipt["paired_config_except_estimator"] and receipt["paired_init_stream"]
    parent_record = json.loads((tmp_path / "st/training_record.json").read_text())
    record_path = tmp_path / "pam/training_record.json"
    first = record_path.read_bytes()
    record = json.loads(first)
    assert record["record_key"] != parent_record["record_key"]
    assert record["stream_hashes"] == parent_record["stream_hashes"]
    assert record["train_manifest_sha256"] == parent_record["train_manifest_sha256"]
    assert record["cell_id"] == audit.CELL_ID and record["estimator_id"] == "perturb_and_map"
    assert audit.accept_audit_job(audit_job) == receipt
    assert record_path.read_bytes() == first
    with pytest.raises(RuntimeError, match="parent checkpoint changed"):
        audit.accept_audit_job({**audit_job, "st_checkpoint_sha256": "0" * 64})
    record["metrics"]["final_total"] = float("inf")
    record_path.write_text(json.dumps(record))
    with pytest.raises(RuntimeError, match="nonfinite A10 training"):
        audit.accept_audit_job(audit_job)


def test_private_progress_checkpoint_cpu_load(tmp_path: Path) -> None:
    model = torch.nn.Linear(2, 1)
    optimizer = torch.optim.Adam(model.parameters())
    model(torch.ones(1, 2)).sum().backward()
    optimizer.step()
    path = tmp_path / "private_progress/latest.pt"
    training.save_progress_snapshot(path, model, optimizer, 7, {"scope": "unit_fixture"}, 999)
    saved = torch.load(path, map_location="cpu", weights_only=False)
    assert saved["role"] == "private_training_progress" and saved["resume_supported"] is False
    assert saved["iter_idx"] == 7 and saved["seed"] == 999
    assert saved["optimizer_state_dict"]["state"]
    assert all(torch.equal(saved["model_state_dict"][key], value) for key, value in model.state_dict().items())


def test_audit_record_replaces_parent_outcomes() -> None:
    parent = {
        "seed": 11000, "horizon": 4, "draw_index": 1, "axis": "id", "cell_id": audit.CELL_ID,
        "config_sha256": "parent-config", "checkpoint_lock_sha256": "parent-lock",
        "fixture_manifest_sha256": "shared-fixture", "metrics": {"endpoint_y": 999.0, "parent_only": 123},
    }
    result = {"error": torch.tensor([[2.0, 6.0]]), "n_window_rounds": 1}
    record = audit_eval.audit_record(parent, result, torch.tensor([2.0, 3.0]), "pam-lock", {"seed_root": 11000}, "code")
    assert record["metrics"]["endpoint_y"] == pytest.approx((2.5) ** 0.5)
    assert "parent_only" not in record["metrics"] and parent["metrics"]["endpoint_y"] == 999.0
    assert record["fixture_manifest_sha256"] == parent["fixture_manifest_sha256"]
    assert record["checkpoint_lock_sha256"] == "pam-lock" and record["record_class"] == "RC3"
    assert record["run_id"].endswith(".h04") and record["record_key"].startswith("B1.RC3.")
