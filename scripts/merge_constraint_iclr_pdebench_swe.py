"""Merge the two frozen shallow-water formal shards by exact run ID."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from analyze_constraint_iclr_pdebench import load_config, read_records
from analyze_constraint_iclr_pdebench_swe import validate_swe_records
from constraint_iclr_common import sha256_file

SHARD_NAMES = ("v100a", "v100b")


def merge_swe_shards(
    shard_records: dict[str, list[dict[str, Any]]], config: dict[str, Any]
) -> list[dict[str, Any]]:
    expected_seeds = {
        str(name): [int(value) for value in values]
        for name, values in config["formal_seed_shards"].items()
    }
    if set(shard_records) != set(SHARD_NAMES):
        raise RuntimeError("SWE merge requires exactly the registered two shards")
    merged: list[dict[str, Any]] = []
    run_ids: set[str] = set()
    for name in SHARD_NAMES:
        records = shard_records[name]
        expected_count = 5 * len(expected_seeds[name])
        if len(records) != expected_count:
            raise RuntimeError(
                f"SWE shard {name} has {len(records)} records, expected {expected_count}"
            )
        observed_seeds = {int(record["seed"]) for record in records}
        if observed_seeds != set(expected_seeds[name]):
            raise RuntimeError(f"SWE shard {name} has the wrong seed coverage")
        for record in records:
            run_id = str(record["run_id"])
            if run_id in run_ids:
                raise RuntimeError(f"duplicate SWE run ID across shards: {run_id}")
            run_ids.add(run_id)
            merged.append(record)
    merged.sort(key=lambda record: (int(record["seed"]), str(record["mechanism"])))
    validation_config = dict(config)
    validation_config["seeds"] = [int(value) for value in config["formal_seed_universe"]]
    validate_swe_records(merged, validation_config)
    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(
            "configs/constraint_iclr/"
            "pdebench_swe_rdb_factorial_distributed_20260902.yaml"
        ),
    )
    parser.add_argument("--v100a", type=Path, required=True)
    parser.add_argument("--v100b", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "experiments/constraint_attribution_iclr/pdebench/"
            "swe_factorial_confirmation_20260902.jsonl"
        ),
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]

    def resolved(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    config_path = resolved(args.config)
    config = load_config(config_path)
    shard_paths = {"v100a": resolved(args.v100a), "v100b": resolved(args.v100b)}
    records = merge_swe_shards(
        {name: read_records(path) for name, path in shard_paths.items()}, config
    )
    output_path = resolved(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(
        "".join(
            json.dumps(record, sort_keys=True, allow_nan=False) + "\n"
            for record in records
        ),
        encoding="utf-8",
    )
    os.replace(temporary, output_path)
    print(f"records={len(records)}")
    print(f"output={output_path}")
    print(f"sha256={sha256_file(output_path)}")


if __name__ == "__main__":
    main()
