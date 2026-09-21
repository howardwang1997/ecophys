#!/usr/bin/env python3
"""Assemble/merge a D0-S3 block manifest from per-job artifacts.

Two uses:
* close-out of a halted block (B3): every present job is recorded and the
  missing cells are disclosed under ``halt`` citing the PI decision id;
* merged manifest of a block completed by several concurrent drivers (B1,
  hosts ts+bts): per-driver ``block_manifest.json`` files are
  last-writer-wins subsets and are never used; this tool rebuilds the
  block-level manifest from the authoritative per-job
  ``training_record.json`` + ``training_log.json`` pairs.

Entries reproduce the training driver's manifest-entry shape exactly
(train_stage1_d0s3.py train_one return), so downstream analyzers see one
uniform manifest schema whether single-driver or merged.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA = "ecomd-d0s3-train-runtime-v1"
ARM_IDS = ("absolute_raw", "increment_raw", "absolute_through_m", "increment_through_m")
FREEZE_COMMIT = "f4e61bafed21f12a6ec73dbe82b9ed4ea87bdd37"
FREEZE_SHA256 = "fd4a40b0306d415cef9a8a41b8e94e5afb21126e4e3d7ff99097e066f9981f57"


def canonical_bytes(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def load_job(block_root: Path, arm_id: str, seed_root: int) -> dict | None:
    job_dir = block_root / f"arm_{arm_id}" / f"seed_{seed_root:06d}"
    record_path = job_dir / "training_record.json"
    log_path = job_dir / "training_log.json"
    if not record_path.exists() or not log_path.exists():
        return None
    record = json.loads(record_path.read_text())
    log = json.loads(log_path.read_text())
    metrics = record["metrics"]
    return {
        "arm_id": arm_id,
        "seed_root": seed_root,
        "block_id": record["block_id"],
        "checkpoint": str(job_dir / "checkpoint.lock"),
        "checkpoint_sha256": log["checkpoint_sha256"],
        "lock_chain_sha256": log["lock_chain_sha256"],
        "record": str(record_path),
        "record_key": record["record_key"],
        "final_total": metrics["final_total"],
        "final_c5_endpoint": metrics["final_c5_endpoint"],
        "finite_final": metrics["finite_final"],
        "wall_seconds": metrics["wall_seconds"],
        "_git_sha": record["git_sha"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--block-dir", required=True, type=Path,
                        help="directory containing arm_*/seed_* job dirs")
    parser.add_argument("--block-id", required=True)
    parser.add_argument("--lineage", required=True, choices=["l1", "l2"])
    parser.add_argument("--seeds", required=True, help="seed range START:STOP (exclusive)")
    parser.add_argument("--arms", default=",".join(ARM_IDS))
    parser.add_argument("--n-train", type=int, required=True)
    parser.add_argument("--n-iters", type=int, required=True)
    parser.add_argument("--through-m-coordinate-mode", default="differentiated")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--production-constants-decision", required=True)
    parser.add_argument("--hosts", default="",
                        help="comma-separated host labels recorded in the manifest")
    parser.add_argument("--halt-decision", default=None,
                        help="PI decision id authorizing the halt (close-out mode)")
    parser.add_argument("--halt-reason", default="")
    parser.add_argument("--halted-cells", default="",
                        help="comma list of ARM=START:STOP ranges intentionally not run")
    args = parser.parse_args(argv)

    seeds = range(*(int(x) for x in args.seeds.split(":")))
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    entries: list[dict] = []
    missing: list[dict] = []
    git_shas: dict[str, int] = {}
    for arm_id in arms:
        for seed_root in seeds:
            entry = load_job(args.block_dir, arm_id, seed_root)
            if entry is None:
                missing.append({"arm_id": arm_id, "seed_root": seed_root})
                continue
            sha = entry.pop("_git_sha")
            git_shas[sha] = git_shas.get(sha, 0) + 1
            entries.append(entry)

    if args.halt_decision and not missing:
        raise RuntimeError("close-out mode with zero missing cells -- use the driver manifest")
    if missing and not args.halt_decision:
        raise RuntimeError(
            f"{len(missing)} job(s) missing and no --halt-decision given: "
            + ", ".join(f"{m['arm_id']}:{m['seed_root']}" for m in missing[:5])
        )
    if len(git_shas) != 1:
        raise RuntimeError(f"jobs were trained under mixed git shas: {sorted(git_shas)}")

    manifest: dict = {
        "schema_version": SCHEMA,
        "manifest_mode": "halted_closeout" if args.halt_decision else "merged_from_per_job_records",
        "campaign_id": "alpha_cube_d0_20260919",
        "block_id": args.block_id,
        "lineage": args.lineage,
        "dgp_variant": "lab-asset-v3",
        "training_axis": "id",
        "training_kernel": "fifo",
        "seed_start": min(seeds),
        "seed_stop_inclusive": max(seeds),
        "arms": arms,
        "production_constants": {
            "n_train": args.n_train,
            "n_iters": args.n_iters,
            "episode_start": 64,
            "through_m_coordinate_mode": args.through_m_coordinate_mode,
            "device": args.device,
            "lr": 3e-4,
            "grad_clip": 1.0,
            "channel_scales": [1.0, 1.0],
            "decision": args.production_constants_decision,
        },
        "freeze_commit": FREEZE_COMMIT,
        "freeze_sha256": FREEZE_SHA256,
        "git_sha": next(iter(git_shas)),
        "corpus_window_reserved": list(range(0, 64)),
        "jobs": entries,
    }
    if args.hosts:
        manifest["hosts"] = [h.strip() for h in args.hosts.split(",") if h.strip()]
    if args.halt_decision:
        manifest["halt"] = {
            "decision": args.halt_decision,
            "reason": args.halt_reason,
            "halted_ranges": args.halted_cells,
            "missing_cells_count": len(missing),
            "missing_cells": missing,
            "note": (
                "cells listed here were intentionally not executed; no absent cell "
                "may be reported as a trained comparison (see the decision record)"
            ),
        }

    out = args.block_dir / "block_manifest.json"
    tmp = out.with_name("block_manifest.json.tmp")
    tmp.write_bytes(canonical_bytes(manifest))
    tmp.replace(out)
    print(f"manifest: {out} jobs={len(entries)} missing={len(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
