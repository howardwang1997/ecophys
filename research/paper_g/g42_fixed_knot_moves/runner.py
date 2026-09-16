"""g42 sandbox image entry point. Do not invoke outside an authorized OCI branch."""

from __future__ import annotations

import io
import json
import os
import sys
import tarfile
from pathlib import Path
from typing import Any

from .model import run_unit


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text())
    if not isinstance(config, dict):
        raise ValueError("configuration must be a mapping")
    return config


def execute(config: dict[str, Any]) -> dict[str, Any]:
    if config.get("epistemic_class") != "sandbox_exploratory_tainted":
        raise ValueError("missing exploratory label")
    units = config["units"]
    unit_ids = config["unit_ids"]
    if sorted(units) != sorted(unit_ids) or len(set(unit_ids)) != len(unit_ids):
        raise ValueError("branch unit membership mismatch")
    reports: dict[str, Any] = {}
    for unit_id in unit_ids:
        unit_config = units[unit_id]
        if unit_config.get("unit_id") != unit_id:
            raise ValueError("unit envelope key/body unit_id mismatch")
        if (
            unit_config.get("branch_id") != config["branch_id"]
            or unit_config.get("epistemic_class") != config["epistemic_class"]
        ):
            raise ValueError("unit envelope identity mismatch")
        reports[unit_id] = run_unit(unit_config)
    return {
        "branch_id": config["branch_id"],
        "epistemic_class": config["epistemic_class"],
        "units": reports,
    }


def main() -> None:
    if not os.environ.get("ECOMD_DX_SANDBOX_ID") or not os.environ.get(
        "ECOMD_DX_BRANCH_ID"
    ):
        raise RuntimeError("use the governed OCI launcher")
    config_path = Path(os.environ["ECOMD_DX_CONFIG"])
    config = load_config(config_path)
    if (
        config.get("mode") in {"normal", "sleep", "invalid_tar"}
        and "unit_ids" not in config
    ):
        from .oci_probe import main as probe_main

        raise SystemExit(probe_main())
    if config["branch_id"] != os.environ["ECOMD_DX_BRANCH_ID"]:
        raise ValueError("runtime branch identity mismatch")
    report = execute(config)
    # JSON forbids non-finite values so no unusable scientific report can be
    # accepted.
    data = json.dumps(report, sort_keys=True, allow_nan=False).encode()
    with tarfile.open(fileobj=sys.stdout.buffer, mode="w|") as archive:
        member = tarfile.TarInfo("exploratory_response.json")
        member.size = len(data)
        member.mode = 0o444
        member.mtime = 0
        archive.addfile(member, io.BytesIO(data))


if __name__ == "__main__":
    main()
