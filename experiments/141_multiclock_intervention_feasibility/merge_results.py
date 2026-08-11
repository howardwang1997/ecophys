#!/usr/bin/env python3
"""Blindly merge Experiment 141 seed shards."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ecomd.market_world.evaluation import merge_scientific_shards, read_json
from ecomd.market_world.protocol import load_protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fit", type=Path, required=True)
    parser.add_argument("--shards", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/market_world/intervention_feasibility_v1.yaml",
    )
    arguments = parser.parse_args()
    if arguments.output.exists():
        raise FileExistsError(f"refusing to overwrite {arguments.output}")
    protocol = load_protocol(arguments.config)
    fit_bundle = read_json(arguments.fit)
    shards = [read_json(path) for path in arguments.shards]
    result = merge_scientific_shards(protocol, fit_bundle, shards)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
