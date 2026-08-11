#!/usr/bin/env python3
"""Run the deterministic CUDA probe on one Experiment 141 worker."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import socket
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ecomd.market_world.hardware import run_cuda_probe
from ecomd.market_world.protocol import load_protocol
from ecomd.market_world.provenance import require_clean_repository, research_code_sha256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", choices=("v100-a", "v100-b", "rtx2060"), required=True)
    parser.add_argument("--device", type=int, default=0)
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
    result = run_cuda_probe(
        protocol.hardware_probe,
        worker=arguments.worker,
        device_index=arguments.device,
    )
    result["ownership"] = {
        "git_commit": commit,
        "research_code_sha256": research_code_sha256(ROOT),
        "config_sha256": protocol.config_sha256,
        "protocol_version": protocol.protocol_version,
        "hostname": socket.gethostname(),
        "finished_at_utc": datetime.now(UTC).isoformat(),
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "worker": result["worker"],
                "device": result["device"],
                "final_loss": result["final_loss"],
                "exact_resume": result["exact_resume"],
                "peak_reserved_fraction": result["peak_reserved_fraction"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
