#!/usr/bin/env python3
"""Freeze Experiment 141 parameters from development seeds only."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ecomd.market_world.fitting import run_development_fit
from ecomd.market_world.protocol import load_protocol
from ecomd.market_world.provenance import require_clean_repository, research_code_sha256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/market_world/intervention_feasibility_v1.yaml",
    )
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.output.exists():
        raise FileExistsError(f"refusing to overwrite {arguments.output}")

    source_commit = require_clean_repository(ROOT)
    protocol = load_protocol(arguments.config)
    started = datetime.now(UTC)
    development_fit = run_development_fit(protocol)
    bundle = {
        "schema": "exp141-development-fit-v1",
        "experiment": protocol.experiment,
        "protocol_version": protocol.protocol_version,
        "config_sha256": protocol.config_sha256,
        "source_commit": source_commit,
        "research_code_sha256": research_code_sha256(ROOT),
        "created_at_utc": datetime.now(UTC).isoformat(),
        "wall_seconds": (datetime.now(UTC) - started).total_seconds(),
        "development_fit": development_fit,
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n")
    print(json.dumps(bundle["development_fit"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
