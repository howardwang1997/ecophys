"""Deterministically merge the two disjoint frozen CNS formal JSONL shards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

MECHANISM_ORDER = {
    "free": 0,
    "projection": 1,
    "free_res": 2,
    "hard_abs": 3,
    "hard": 4,
}
FORMAL_SEEDS = tuple(range(5000, 5030))
BENCHMARK_ID = "pdebench_cns_eta0.01_zeta0.01_periodic_fno_factorial_v1"


def merge_cns_shards(paths: list[Path], output: Path) -> None:
    indexed: dict[tuple[int, str], tuple[str, dict[str, Any]]] = {}
    run_ids: set[str] = set()
    source_manifests: set[str] = set()
    for path in paths:
        for line_number, raw_line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not raw_line.strip():
                continue
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError as error:
                raise RuntimeError(f"invalid CNS JSONL {path}:{line_number}") from error
            key = (int(record.get("seed", -1)), str(record.get("mechanism")))
            run_id = str(record.get("run_id"))
            if key in indexed:
                raise RuntimeError(f"duplicate CNS seed/mechanism across shards: {key}")
            if run_id in run_ids:
                raise RuntimeError(f"duplicate CNS run ID across shards: {run_id}")
            if record.get("stage") != "cns_factorial_confirmation":
                raise RuntimeError(f"wrong CNS stage for {key}")
            if record.get("benchmark_id") != BENCHMARK_ID:
                raise RuntimeError(f"wrong CNS benchmark for {key}")
            sources = record.get("provenance", {}).get("source_sha256")
            if not isinstance(sources, dict):
                raise RuntimeError(f"missing CNS source manifest for {key}")
            source_manifests.add(json.dumps(sources, sort_keys=True))
            indexed[key] = (raw_line, record)
            run_ids.add(run_id)
    expected = {
        (seed, mechanism) for seed in FORMAL_SEEDS for mechanism in MECHANISM_ORDER
    }
    if set(indexed) != expected:
        raise RuntimeError(
            "wrong CNS shard coverage: "
            f"missing={sorted(expected.difference(indexed))}, "
            f"extra={sorted(set(indexed).difference(expected))}"
        )
    if len(source_manifests) != 1:
        raise RuntimeError("CNS worker shards do not share one source manifest")
    ordered = sorted(indexed, key=lambda item: (item[0], MECHANISM_ORDER[item[1]]))
    payload = "\n".join(indexed[key][0] for key in ordered) + "\n"
    if output.exists():
        if output.read_text(encoding="utf-8") == payload:
            return
        raise RuntimeError("refusing to overwrite a non-identical CNS merge")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    merge_cns_shards(args.inputs, args.output)
    print(f"merged={args.output}")


if __name__ == "__main__":
    main()
