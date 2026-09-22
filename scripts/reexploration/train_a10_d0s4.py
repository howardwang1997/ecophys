#!/usr/bin/env python3
"""Train the frozen A10 audit with the Stage-1 loop and paired B1 inputs."""
from __future__ import annotations

import argparse
import fcntl
import json
import math
from pathlib import Path
from typing import Any

import yaml

import train_stage1_d0s3 as training

AUDIT_ID = "A10"
ARM_ID = "increment_through_m"
CELL_ID = "increment-through_m-raw"
TRAIN_DECISION = "pi_d0s3_train_constants_20260921"


def prepare_job(repo: Path, parent: Path, out: Path, seed: int) -> dict[str, Any]:
    training.enforce_freeze_pins(repo)
    audit = yaml.safe_load((repo / "configs/reexploration/audit/a10.yaml").read_text())
    if not (audit["seed_start"] <= seed <= audit["seed_stop_inclusive"]):
        raise ValueError(f"seed outside A10 namespace: {seed}")
    if (audit["audit_id"], audit["parent_block"], audit["lineage_id"], audit["coordinate"],
            audit["enforcement"], audit["inference_enforcement"], audit["estimator"]) != (
            "A10", "B1", "l1", "increment", "through_m", "raw", "perturb_and_map"):
        raise RuntimeError("A10 config differs from the frozen audit cell")
    training.load_surface(repo)
    from ecomd.training.lock_checkpoint import load_lock_checkpoint

    st_dir = parent / "B1" / f"arm_{ARM_ID}" / f"seed_{seed:06d}"
    record = json.loads((st_dir / "training_record.json").read_text())
    locked = load_lock_checkpoint(st_dir / "checkpoint.lock")
    metadata = locked.payload["execution_metadata"]
    for key, value in {
        "block_id": "B1", "arm_id": ARM_ID, "lineage": "l1", "device": "cuda",
        "n_train": 2048, "episode_start": 64, "n_iters": 100,
        "through_m_coordinate_mode": "differentiated", "production_constants_decision": TRAIN_DECISION,
    }.items():
        if metadata[key] != value:
            raise RuntimeError(f"parent training constant mismatch: {key}")
    if record["seed"] != seed or record["checkpoint_lock_sha256"] != locked.sidecar.checkpoint_sha256:
        raise RuntimeError("parent seed or checkpoint binding mismatch")
    data_dir = training.train_data_dir(parent, seed)
    data_manifest = data_dir / "train_episodes_manifest.json"
    if training.sha256_file(data_manifest) != record["train_manifest_sha256"]:
        raise RuntimeError(f"paired training manifest differs for seed {seed}")
    data = json.loads(data_manifest.read_text())
    if [e["episode_index"] for e in data["episodes"]] != list(range(64, 2112)):
        raise RuntimeError("paired training episode window differs")
    for entry in data["episodes"]:
        path = data_dir / entry["file"]
        if path.parent != data_dir or training.sha256_file(path) != entry["file_sha256"]:
            raise RuntimeError(f"paired training episode hash mismatch: {entry['file']}")
    arm = training.load_arm(repo, ARM_ID)
    if arm["estimator"] != "straight_through":
        raise RuntimeError("parent arm must use straight_through")
    arm = {**arm, "estimator": audit["estimator"]}
    return {
        "repo_root": str(repo), "arm": arm, "arm_id": ARM_ID, "lineage": "l1", "block_id": "B1",
        "seed_root": seed, "n_train": metadata["n_train"], "n_iters": metadata["n_iters"],
        "episode_start": metadata["episode_start"], "through_m_coordinate_mode": metadata["through_m_coordinate_mode"],
        "device": "cuda", "train_dir": str(data_dir),
        "job_dir": str(out / "B1" / f"arm_{ARM_ID}" / f"seed_{seed:06d}"),
        "progress_dir": str(out / "private_progress" / f"seed_{seed:06d}"),
        "git_sha": training.git_head(repo), "production_constants_decision": TRAIN_DECISION,
        "st_checkpoint": str(st_dir / "checkpoint.lock"),
        "st_checkpoint_sha256": locked.sidecar.checkpoint_sha256,
    }


def accept_audit_job(job: dict[str, Any]) -> dict[str, Any]:
    import torch
    from ecomd.training.lock_checkpoint import load_lock_checkpoint
    from ecomd.training.train_fact_surrogate import derive_substream_seeds

    folder = Path(job["job_dir"])
    parent = load_lock_checkpoint(job["st_checkpoint"])
    audited = load_lock_checkpoint(folder / "checkpoint.lock")
    if parent.sidecar.checkpoint_sha256 != job["st_checkpoint_sha256"]:
        raise RuntimeError("parent checkpoint changed after preparation")
    expected_config = {**parent.payload["sim_config"], "estimator": "perturb_and_map"}
    if audited.payload["sim_config"] != expected_config:
        raise RuntimeError("audit training changed a setting other than estimator")
    for key in ("seed_root", "corpus_hash", "prestate_hash", "manifest_hash", "allocation_rule", "n_draws", "iter_idx"):
        if audited.sidecar.binding[key] != parent.sidecar.binding[key]:
            raise RuntimeError(f"audit pairing differs: {key}")
    if not torch.equal(parent.generators["init"].get_state(), audited.generators["init"].get_state()):
        raise RuntimeError("audit initialization stream differs from parent")
    seed = job["seed_root"]
    record = json.loads((folder / "training_record.json").read_text())
    if not record["metrics"]["finite_final"] or not all(
            math.isfinite(record["metrics"][key]) for key in ("final_total", "final_c5_endpoint")):
        raise RuntimeError(f"nonfinite A10 training endpoint: seed {seed}")
    record.update(
        cell_id=CELL_ID, run_id=f"B1.audit_training.A10.{seed:05d}",
        record_key=f"B1.training.train.id.00.{CELL_ID}.{seed:05d}.00",
        estimator_id="perturb_and_map",
        estimator_seed_provenance={
            "seed_root": seed, "train_kernel_seed": derive_substream_seeds(seed)["train_kernel"],
            "derivation": "TrainKernelStream(seed_root), child (3, call_index), second uint32 for PAM noise",
        },
    )
    log = json.loads((folder / "training_log.json").read_text())
    log.update(run_id=record["run_id"], record_key=record["record_key"])
    training.atomic_write_bytes(folder / "training_record.json", training.canonical_bytes(record))
    training.atomic_write_bytes(folder / "training_log.json", training.canonical_bytes(log))
    receipt = {
        "audit_id": AUDIT_ID, "parent_block": "B1", "seed": seed,
        "parent_checkpoint_sha256": parent.sidecar.checkpoint_sha256,
        "checkpoint_sha256": audited.sidecar.checkpoint_sha256,
        "training_manifest_sha256": record["train_manifest_sha256"],
        "paired_config_except_estimator": True, "paired_init_stream": True,
        "training_record_sha256": training.sha256_file(folder / "training_record.json"),
        "git_sha": audited.payload["execution_metadata"]["git_sha"],
    }
    training.atomic_write_bytes(folder / "audit_receipt.json", training.canonical_bytes(receipt))
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--parent-train-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--seeds", required=True)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args(argv)
    seeds = list(training.parse_seed_range(args.seeds))
    if not seeds:
        parser.error("empty seed range")
    repo, parent, out = args.repo_root.resolve(), args.parent_train_dir.resolve(), args.out_dir.resolve()
    jobs = [prepare_job(repo, parent, out, seed) for seed in seeds]
    print(json.dumps({"audit_id": AUDIT_ID, "paired_jobs_ready": len(jobs), "seeds": seeds}), flush=True)
    if args.check_only:
        return 0
    import torch
    torch.set_num_threads(1)
    if not torch.cuda.is_available():
        raise RuntimeError("A10 production requires the authorized V100 CUDA worker")
    receipts = []
    for job in jobs:
        folder = Path(job["job_dir"])
        folder.mkdir(parents=True, exist_ok=True)
        with (folder / "execution.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if not (folder / "audit_receipt.json").exists():
                if (folder / "checkpoint.lock").exists() or (folder / "training_record.json").exists():
                    raise RuntimeError(f"incomplete existing audit job requires inspection: {folder}")
                training.train_one(job)
            receipt = accept_audit_job(job)
            receipts.append(receipt)
            print(json.dumps({"audit_id": AUDIT_ID, "completed_seed": job["seed_root"], "checkpoint_sha256": receipt["checkpoint_sha256"]}), flush=True)
    training.atomic_write_bytes(out / f"audit_manifest_{seeds[0]}_{seeds[-1]}.json", training.canonical_bytes(receipts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
