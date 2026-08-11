#!/usr/bin/env python3
"""Run one isolated formal seed shard for Experiment 141."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import platform
import socket
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import numpy as np
import scipy

from ecomd.market_world.evaluation import read_json, run_evaluation_shard
from ecomd.market_world.protocol import load_protocol
from ecomd.market_world.provenance import require_clean_repository, research_code_sha256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/market_world/intervention_feasibility_v1.yaml",
    )
    arguments = parser.parse_args()
    if arguments.output.exists():
        raise FileExistsError(f"refusing to overwrite {arguments.output}")

    commit = require_clean_repository(ROOT)
    protocol = load_protocol(arguments.config)
    fit_bundle = read_json(arguments.fit)
    if fit_bundle["config_sha256"] != protocol.config_sha256:
        raise RuntimeError("development fit and formal config hashes disagree")
    code_hash = research_code_sha256(ROOT)
    if fit_bundle["research_code_sha256"] != code_hash:
        raise RuntimeError("research code changed after the development fit")

    started = datetime.now(UTC)
    output = run_evaluation_shard(protocol, fit_bundle, arguments.shard)
    output["ownership"] = {
        "git_commit": commit,
        "fit_source_commit": fit_bundle["source_commit"],
        "research_code_sha256": code_hash,
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "started_at_utc": started.isoformat(),
        "finished_at_utc": datetime.now(UTC).isoformat(),
        "wall_seconds": (datetime.now(UTC) - started).total_seconds(),
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "shard": output["shard"],
                "rows": len(cast(list[object], output["rows"])),
                "anchor_sha256": output["anchor_sha256"],
                "wall_seconds": cast(dict[str, object], output["ownership"])["wall_seconds"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
