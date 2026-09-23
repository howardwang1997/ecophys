"""Train the ratified recurrent lineage using fixed training-partition units."""
from __future__ import annotations

import argparse
import fcntl
import json
import math
from pathlib import Path
from typing import Any

import yaml

import train_stage1_d0s3 as training

DECISION = "pi_gamma_l2_units_revision_20260923"
REVISION = "l2_training_units_v1"


def require_decision(repo: Path) -> str:
    path = repo / "research/discovery/decisions" / f"{DECISION}.yaml"
    decision = yaml.safe_load(path.read_text())
    if (decision["decision_id"], decision["status"], decision["model_revision"]) != (
            DECISION, "ratified", REVISION):
        raise RuntimeError("L2 revision requires its ratified decision")
    return training.sha256_file(path)


def prepare_units(repo: Path, data: Path, seed: int, n_train: int) -> dict[str, Any]:
    import torch
    from ecomd.models.unit_fact_surrogate import fit_training_units

    manifest_path = data / "train_episodes_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for key, value in {"seed_root": seed, "lineage": "l2", "axis": "id", "kernel": "fifo",
                       "n_train": n_train, "episode_start": 64}.items():
        if manifest[key] != value:
            raise RuntimeError(f"training partition mismatch: {key}")
    if [row["episode_index"] for row in manifest["episodes"]] != list(range(64, 64 + n_train)):
        raise RuntimeError("training episodes differ from the authorized window")
    for row in manifest["episodes"]:
        path = data / row["file"]
        if path.parent != data or training.sha256_file(path) != row["file_sha256"]:
            raise RuntimeError(f"training episode hash mismatch: {row['file']}")
    batches = training.SeedBatches(data)
    units = fit_training_units([
        batches.shuffled(bucket, torch.arange(bucket["n_episodes"])) for bucket in batches.buckets
    ])
    return {"revision": REVISION, "decision": DECISION, "decision_sha256": require_decision(repo),
            "seed": seed, "n_train": n_train, "episode_start": 64,
            "training_manifest_sha256": training.sha256_file(manifest_path),
            "values": {key: value.tolist() for key, value in units.items()}}


def accept_job(job: dict[str, Any]) -> dict[str, Any]:
    from ecomd.training.lock_checkpoint import load_lock_checkpoint

    directory = Path(job["job_dir"])
    locked = load_lock_checkpoint(directory / "checkpoint.lock")
    metadata = locked.payload["execution_metadata"]
    for key in ("block_id", "lineage", "arm_id", "device", "n_train", "n_iters",
                "episode_start", "through_m_coordinate_mode", "production_constants_decision", "git_sha"):
        if metadata[key] != job[key]:
            raise RuntimeError(f"revised L2 checkpoint differs: {key}")
    units_sha = training.sha256_bytes(training.canonical_bytes(job["l2_units"]))
    if (locked.payload["sim_config"].get("l2_units") != job["l2_units"]
            or metadata.get("l2_revision") != REVISION
            or metadata.get("l2_units_sha256") != units_sha
            or metadata.get("fifo_allocation_cache") is not True):
        raise RuntimeError("revised L2 unit/runtime binding differs")
    for key in ("coordinate", "enforcement"):
        if locked.payload["sim_config"][key] != job["arm"][key]:
            raise RuntimeError(f"revised L2 arm differs: {key}")
    if locked.sidecar.binding["seed_root"] != job["seed_root"] or locked.payload["iter_idx"] != job["n_iters"]:
        raise RuntimeError("revised L2 seed or iteration differs")
    record = json.loads((directory / "training_record.json").read_text())
    log = json.loads((directory / "training_log.json").read_text())
    if (record["checkpoint_lock_sha256"] != locked.sidecar.checkpoint_sha256
            or log["checkpoint_sha256"] != locked.sidecar.checkpoint_sha256
            or record["train_manifest_sha256"] != job["l2_units"]["training_manifest_sha256"]):
        raise RuntimeError("revised L2 training record binding differs")
    if not all(math.isfinite(record["metrics"][key]) for key in (
            "first_total", "final_total", "final_c5_endpoint", "final_grad_norm")):
        raise RuntimeError("nonfinite revised L2 training")
    receipt = {"seed": job["seed_root"], "arm_id": job["arm_id"], "block_id": job["block_id"],
               "revision": REVISION, "decision": DECISION, "git_sha": job["git_sha"],
               "checkpoint_sha256": locked.sidecar.checkpoint_sha256, "units_sha256": units_sha,
               "training_manifest_sha256": record["train_manifest_sha256"],
               "wall_seconds": metadata["wall_seconds"]}
    training.atomic_write_bytes(directory / "acceptance_receipt.json", training.canonical_bytes(receipt))
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--parent-train-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--seeds", default="12000:12030")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    repo, out = args.repo_root.resolve(), args.out_dir.resolve()
    training.ensure_repo(repo)
    import torch

    torch.set_num_threads(1)
    if not torch.cuda.is_available():
        raise RuntimeError("the approved B3 training device is CUDA")
    training.enforce_freeze_pins(repo)
    decision_sha = require_decision(repo)
    if out == args.parent_train_dir.resolve() or args.parent_train_dir.resolve() in out.parents:
        raise RuntimeError("new B3 output must be separate from the old training tree")
    seeds = list(range(*map(int, args.seeds.split(":"))))
    if not seeds or any(seed not in range(12000, 12030) for seed in seeds):
        raise ValueError("B3 seeds must be within 12000:12030")
    n_train, n_iters, block = 4096, 100, "B3"
    if args.preflight:
        seeds, n_train, block = [2026092304], 32, "DEV_L2_UNITS_CUDA"
    out.mkdir(parents=True, exist_ok=True)
    all_receipts = []
    for seed in seeds:
        seed_dir = out / block / f"seed_{seed:08d}"
        seed_dir.mkdir(parents=True, exist_ok=True)
        with (seed_dir / "execution.lock").open("a") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            data = training.train_data_dir(args.parent_train_dir, seed)
            if args.preflight:
                data = out / "private_development_data"
                training.stage_seed_episodes({"job": {
                    "repo_root": str(repo), "dir": str(data), "seed_root": seed, "lineage": "l2",
                    "episode_start": 64, "n_train": n_train, "workers": 2,
                    "config": training.load_dgp_config(repo),
                }})
            else:
                parent = args.parent_train_dir / "B3/arm_absolute_raw" / f"seed_{seed:06d}/training_record.json"
                anchor = json.loads(parent.read_text())
                if (anchor["seed"] != seed or anchor["train_manifest_sha256"] !=
                        training.sha256_file(data / "train_episodes_manifest.json")):
                    raise RuntimeError("parent data-manifest anchor differs")
            units = prepare_units(repo, data, seed, n_train)
            encoded = training.canonical_bytes(units)
            units_path = seed_dir / "units.json"
            if units_path.exists() and units_path.read_bytes() != encoded:
                raise RuntimeError("training unit constants changed on resume")
            training.atomic_write_bytes(units_path, encoded)
            if args.check_only:
                print(json.dumps({"seed": seed, "training_inputs_accepted": True}), flush=True)
                continue
            receipts = []
            for arm_id in training.ARM_IDS:
                job = {
                    "repo_root": str(repo), "arm": training.load_arm(repo, arm_id), "arm_id": arm_id,
                    "lineage": "l2", "block_id": block, "seed_root": seed, "n_train": n_train,
                    "n_iters": n_iters, "episode_start": 64, "through_m_coordinate_mode": "differentiated",
                    "device": "cuda", "train_dir": str(data),
                    "job_dir": str(out / block / f"arm_{arm_id}" / f"seed_{seed:06d}"),
                    "progress_dir": str(out / "private_progress" / arm_id / f"seed_{seed:06d}"),
                    "git_sha": training.git_head(repo), "production_constants_decision": DECISION,
                    "l2_units": units, "cache_fifo": True,
                }
                checkpoint = Path(job["job_dir"]) / "checkpoint.lock"
                if not checkpoint.exists():
                    print(json.dumps({"started_seed": seed, "arm": arm_id, "block": block}), flush=True)
                    training.train_one(job)
                receipt = accept_job(job)
                if args.preflight:
                    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
                    history = payload["rank_runtimes"][0]["history"]
                    ratio = sum(row["total"] for row in history[-10:]) / (10 * history[0]["total"])
                    if (not all(math.isfinite(row[key]) for row in history for key in ("total", "grad_norm"))
                            or not any(row["grad_norm"] > 0 for row in history) or ratio > 0.99):
                        raise RuntimeError(f"V100 development training gate failed: {arm_id}")
                    receipt["private_development_loss_ratio"] = ratio
                receipts.append(receipt)
                print(json.dumps({"accepted_seed": seed, "arm": arm_id,
                                  "wall_seconds": receipt["wall_seconds"]}), flush=True)
            training.atomic_write_bytes(seed_dir / "training_manifest.json", training.canonical_bytes({
                "revision": REVISION, "decision": DECISION, "decision_sha256": decision_sha,
                "seed": seed, "block_id": block, "jobs": receipts,
            }))
            all_receipts.extend(receipts)
    if args.preflight:
        training.atomic_write_bytes(out / "preflight_receipt.json", training.canonical_bytes({
            "role": "private_V100_development", "passed": len(all_receipts) == 4,
            "git_sha": training.git_head(repo), "decision_sha256": decision_sha, "jobs": all_receipts,
        }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
