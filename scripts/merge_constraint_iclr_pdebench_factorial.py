"""Deterministically merge disjoint frozen factorial JSONL worker shards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from analyze_constraint_iclr_pdebench import load_config

MECHANISM_ORDER = {
    "free": 0,
    "projection": 1,
    "free_res": 2,
    "hard_abs": 3,
    "hard": 4,
}


def load_shards(paths: list[Path]) -> dict[tuple[int, str], tuple[str, dict[str, Any]]]:
    indexed: dict[tuple[int, str], tuple[str, dict[str, Any]]] = {}
    run_ids: set[str] = set()
    for path in paths:
        for line_number, raw_line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not raw_line.strip():
                continue
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError as error:
                raise RuntimeError(f"invalid JSONL {path}:{line_number}: {error}") from error
            if not isinstance(record, dict):
                raise RuntimeError(f"non-object JSONL record at {path}:{line_number}")
            key = (int(record.get("seed", -1)), str(record.get("mechanism")))
            run_id = str(record.get("run_id"))
            if key in indexed:
                raise RuntimeError(f"duplicate seed/mechanism across shards: {key}")
            if run_id in run_ids:
                raise RuntimeError(f"duplicate run ID across shards: {run_id}")
            indexed[key] = (raw_line, record)
            run_ids.add(run_id)
    return indexed


def merge_shards(
    paths: list[Path],
    output: Path,
    *,
    seeds: tuple[int, ...] = tuple(range(4000, 4030)),
    benchmark_id: str = "pdebench_burgers_nu0.01_fno_factorial_v1",
) -> None:
    indexed = load_shards(paths)
    expected = {
        (seed, mechanism) for seed in seeds for mechanism in MECHANISM_ORDER
    }
    if set(indexed) != expected:
        missing = sorted(expected.difference(indexed))
        extra = sorted(set(indexed).difference(expected))
        raise RuntimeError(f"wrong shard coverage: missing={missing}, extra={extra}")
    for key, (_, record) in indexed.items():
        if record.get("stage") != "factorial_confirmation":
            raise RuntimeError(f"wrong stage for {key}")
        if record.get("benchmark_id") != benchmark_id:
            raise RuntimeError(f"wrong benchmark for {key}")

    ordered_keys = sorted(
        indexed, key=lambda item: (item[0], MECHANISM_ORDER[item[1]])
    )
    payload = "\n".join(indexed[key][0] for key in ordered_keys) + "\n"
    if output.exists():
        if output.read_text(encoding="utf-8") == payload:
            return
        raise RuntimeError(f"refusing to overwrite a non-identical merged file: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(output)


def registered_merge_settings(config: dict[str, Any]) -> tuple[tuple[int, ...], str]:
    seeds = tuple(int(value) for value in config.get("seeds", []))
    universe = tuple(int(value) for value in config.get("formal_seed_universe", []))
    shards = config.get("formal_seed_shards")
    if not seeds or seeds != universe:
        raise RuntimeError("registered merge requires seeds to equal formal_seed_universe")
    if not isinstance(shards, dict) or not shards:
        raise RuntimeError("registered merge requires formal_seed_shards")
    shard_seeds = [
        int(seed)
        for worker_seeds in shards.values()
        for seed in worker_seeds
    ]
    if len(shard_seeds) != len(set(shard_seeds)):
        raise RuntimeError("registered worker shards overlap")
    if set(shard_seeds) != set(universe):
        raise RuntimeError("registered worker shards do not partition the seed universe")
    benchmark_id = str(config.get("benchmark_id", ""))
    if not benchmark_id:
        raise RuntimeError("registered merge requires a benchmark_id")
    return seeds, benchmark_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--config",
        type=Path,
        help="derive the exact registered seed universe and benchmark from this config",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.config is None:
        merge_shards(args.inputs, args.output)
    else:
        seeds, benchmark_id = registered_merge_settings(load_config(args.config))
        merge_shards(
            args.inputs,
            args.output,
            seeds=seeds,
            benchmark_id=benchmark_id,
        )
    print(f"merged={args.output}")


if __name__ == "__main__":
    main()
