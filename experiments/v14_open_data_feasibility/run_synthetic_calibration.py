#!/usr/bin/env python3
"""Run the frozen V14 generated-data calibration from a clean commit."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import numpy as np
import scipy

from ecomd.market_world.provenance import require_clean_repository
from ecomd.research.open_data_calibration import (
    canonical_result_sha256,
    run_synthetic_calibration,
    settings_from_contract,
)
from ecomd.research.open_data_development import (
    contract_sha256,
    load_development_contract,
    validate_development_contract,
)


def implementation_sha256() -> str:
    paths = (
        ROOT / "data/manifests/open_data_development_sample_v1.yaml",
        ROOT / "ecomd/research/open_data_development.py",
        ROOT / "ecomd/research/open_data_calibration.py",
        ROOT / "experiments/v14_open_data_feasibility/PREREGISTRATION.md",
        ROOT / "experiments/v14_open_data_feasibility/run_synthetic_calibration.py",
    )
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT / "data/manifests/open_data_development_sample_v1.yaml",
    )
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.output.exists():
        raise FileExistsError(f"refusing to overwrite {arguments.output}")

    commit = require_clean_repository(ROOT)
    contract = load_development_contract(arguments.contract)
    errors = validate_development_contract(contract)
    if errors:
        raise RuntimeError("invalid development contract: " + "; ".join(errors))
    started = datetime.now(UTC)
    scientific = run_synthetic_calibration(settings_from_contract(contract))
    finished = datetime.now(UTC)
    bundle = {
        **scientific,
        "scientific_result_sha256": canonical_result_sha256(scientific),
        "ownership": {
            "git_commit": commit,
            "contract_sha256": contract_sha256(arguments.contract),
            "implementation_sha256": implementation_sha256(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "started_at_utc": started.isoformat(),
            "finished_at_utc": finished.isoformat(),
            "wall_seconds": (finished - started).total_seconds(),
        },
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "pass": bundle["pass"],
                "null": bundle["null"],
                "effect": bundle["effect"],
                "clock": bundle["clock"],
                "structural_contract": bundle["structural_contract"],
                "scientific_result_sha256": bundle["scientific_result_sha256"],
                "wall_seconds": bundle["ownership"]["wall_seconds"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
