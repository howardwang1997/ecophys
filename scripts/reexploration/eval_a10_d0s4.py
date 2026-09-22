#!/usr/bin/env python3
"""Evaluate the frozen A10 raw-inference cell against its B1 fixture stream."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import eval_draws_d0s4 as evaluation

ARM_ID = "increment_through_m"
CELL_ID = "increment-through_m-raw"
RUNTIME_ID = "eval_a10_d0s4"


def audit_record(parent: dict[str, Any], result: dict[str, Any], scales: Any,
                 checkpoint_sha256: str, provenance: dict[str, Any], git_sha: str) -> dict[str, Any]:
    endpoint = evaluation.endpoint_y(result["error"], scales)
    error = result["error"]
    record = {key: value for key, value in parent.items() if key != "metrics"}
    seed, horizon, draw, axis = (parent[key] for key in ("seed", "horizon", "draw_index", "axis"))
    record.update(
        record_class="RC3",
        record_key=evaluation.record_key("B1", "RC3", "id", axis, horizon, CELL_ID, seed, draw),
        run_id=f"B1.audit.A10.{axis}.{CELL_ID}.{seed:05d}.{draw:02d}.h{horizon:02d}",
        checkpoint_lock_sha256=checkpoint_sha256, git_sha=git_sha,
        estimator_id="perturb_and_map", estimator_seed_provenance=provenance,
        config_sha256=evaluation.sha256_bytes(evaluation.canonical_bytes({
            "runtime": RUNTIME_ID, "parent_config_sha256": parent["config_sha256"],
            "checkpoint_lock_sha256": checkpoint_sha256, "training_estimator": "perturb_and_map",
            "inference_enforcement": "raw",
        })),
        metrics={
            "endpoint_y": endpoint, "n_window_rounds": result["n_window_rounds"],
            "max_abs_error_volume_units": float(error[:, 0].abs().max().item()),
            "max_abs_error_cash_ticks": float(error[:, 1].abs().max().item()),
            "finite": math.isfinite(endpoint),
        },
    )
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--audit-train-dir", required=True, type=Path)
    parser.add_argument("--parent-eval-dir", required=True, type=Path)
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--scales-json", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    repo = args.repo_root.resolve()
    evaluation.enforce_freeze_pins(repo)
    surface = evaluation.load_surface(repo)
    import torch
    from ecomd.training.lock_checkpoint import verify_lock

    torch.set_num_threads(1)
    parent_manifest = json.loads((args.parent_eval_dir / "eval_manifest.json").read_text())
    coverage = json.loads((args.parent_eval_dir / "coverage_receipt.json").read_text())
    if (coverage["counts"] != {"RC1": 61440, "RC2": 30720, "RC4": 120}
            or coverage["evaluation_manifest_sha256"] != evaluation.sha256_file(args.parent_eval_dir / "eval_manifest.json")
            or parent_manifest["horizon_mode"] != "chained"):
        raise RuntimeError("complete B1 parent evaluation required")
    if evaluation.sha256_file(args.scales_json) != "debb15a761d5b08cfb3a05428ddd9d5f820abe09d2480b552360ac9800735e0b":
        raise RuntimeError("A10 scales differ from the B1 seal")
    scales, scales_payload = evaluation.load_scales(args.scales_json)
    inventory_path = args.parent_eval_dir / "record_inventory.json"
    if evaluation.sha256_file(inventory_path) != coverage["inventory_sha256"]:
        raise RuntimeError("B1 record inventory hash mismatch")
    inventory = {row["file"]: row["sha256"] for row in json.loads(inventory_path.read_text())}
    block = args.audit_train_dir / "B1"
    receipts = {}
    for seed in range(11000, 11030):
        folder = block / f"arm_{ARM_ID}" / f"seed_{seed:06d}"
        receipt = json.loads((folder / "audit_receipt.json").read_text())
        verified = verify_lock(folder / "checkpoint.lock", deep=True)
        if not verified.ok or verified.sidecar is None or verified.sidecar.checkpoint_sha256 != receipt["checkpoint_sha256"]:
            raise RuntimeError(f"A10 checkpoint binding failed for seed {seed}")
        if (receipt["seed"] != seed or not receipt["paired_config_except_estimator"] or not receipt["paired_init_stream"]
                or evaluation.sha256_file(folder / "training_record.json") != receipt["training_record_sha256"]):
            raise RuntimeError(f"A10 pairing receipt failed for seed {seed}")
        receipts[seed] = (receipt, json.loads((folder / "training_record.json").read_text()))
    git_sha = evaluation.git_head(repo)
    if git_sha is None:
        raise RuntimeError("A10 evaluation requires a code commit")
    records = args.out_dir / "records"
    if records.exists() and any(records.iterdir()):
        raise RuntimeError("A10 evaluation output must be empty; inspect interrupted records before continuing")
    records.mkdir(parents=True, exist_ok=True)
    for seed in range(11000, 11030):
        receipt, training_record = receipts[seed]
        model, checkpoint_sha = evaluation.load_arm_surface(surface, block, ARM_ID, seed)
        for axis in ("id", "pop_2x", "tick_2x"):
            episodes, fixture_sha = evaluation.load_eval_episodes(args.corpus_root, axis, seed)
            for horizon in evaluation.HORIZONS:
                window = evaluation.horizon_window(episodes, horizon, "chained")
                hashes = evaluation.window_hash(episodes, window)
                # Raw inference ignores kernel draws; all 16 records share this result.
                result = evaluation.evaluate_cell(surface, model, None, episodes, window,
                                                  inference_enforcement="raw", coordinate="increment")
                for draw in range(1, 17):
                    key = evaluation.record_key("B1", "RC1", "id", axis, horizon, CELL_ID, seed, draw)
                    source = args.parent_eval_dir / "records" / f"{key}.json"
                    if evaluation.sha256_file(source) != inventory[source.name]:
                        raise RuntimeError(f"B1 parent record hash mismatch: {source.name}")
                    parent = json.loads(source.read_text())
                    if (parent["checkpoint_lock_sha256"] != receipt["parent_checkpoint_sha256"]
                            or parent["fixture_manifest_sha256"] != fixture_sha
                            or parent["stream_hashes"] != training_record["stream_hashes"]
                            or any(parent[field] != value for field, value in hashes.items())):
                        raise RuntimeError(f"A10/B1 fixture pairing mismatch: {source.name}")
                    record = audit_record(parent, result, scales, checkpoint_sha,
                                          training_record["estimator_seed_provenance"], git_sha)
                    if not record["metrics"]["finite"]:
                        raise RuntimeError(f"nonfinite A10 endpoint: seed {seed}, axis {axis}, horizon {horizon}")
                    evaluation.write_record(records, record)
                    if axis == "id":
                        duplicate = {**record, "axis": "kswap", "run_id": record["run_id"] + ".kswap",
                                     "record_key": evaluation.record_key("B1", "RC3", "id", "kswap", horizon, CELL_ID, seed, draw)}
                        evaluation.write_record(records, duplicate)
        print(json.dumps({"audit_id": "A10", "completed_seed": seed, "records_per_seed": 256}), flush=True)
    evaluation.validate_existing_record_ids(records)
    if len(list(records.glob("*.json"))) != 7680:
        raise RuntimeError("A10 must contain exactly 7680 RC3 records")
    manifest = {
        "audit_id": "A10", "record_class": "RC3", "record_count": 7680,
        "seeds": "11000:11030", "cell_id": CELL_ID, "git_sha": git_sha,
        "parent_eval_manifest_sha256": coverage["evaluation_manifest_sha256"],
        "scales": scales_payload, "horizon_mode": "chained", "k": 16,
        "config_binding": "sha256 canonical JSON of runtime, parent_config_sha256, audit checkpoint hash, training estimator and inference enforcement",
        "audit_receipts": [receipts[seed][0] for seed in range(11000, 11030)],
        "formal_analysis_executed": False,
    }
    evaluation.atomic_write_bytes(args.out_dir / "audit_eval_manifest.json", evaluation.canonical_bytes(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
