#!/usr/bin/env python3
"""Compute the frozen post-hoc exposure-routing description."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import yaml

from ecomd.market_world.provenance import require_clean_repository
from ecomd.research.exposure_routing import summarize_exposure_routing, validate_routing_contract
from ecomd.research.uniswap_v3_preperiod_support import load_jsonl


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_contract(path: Path) -> dict[str, object]:
    payload: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("routing contract root must be a mapping")
    return cast(dict[str, object], payload)


def _mapping(value: object, *, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be a mapping")
    return cast(Mapping[str, object], value)


def _validate_commit(repository: Path, value: str) -> None:
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise ValueError("analysis commit must be a full lowercase Git SHA")
    subprocess.run(
        ["git", "cat-file", "-e", f"{value}^{{commit}}"],
        cwd=repository,
        check=True,
        capture_output=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT / "data/manifests/uniswap_v3_exposure_routing_exploratory_v1.yaml",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=(
            ROOT
            / "experiments/v14_uniswap_v3_exposure_routing_exploratory/artifacts/exploratory_summary.json"
        ),
    )
    parser.add_argument("--analysis-commit")
    arguments = parser.parse_args()
    if arguments.output.exists():
        raise FileExistsError(f"refusing to overwrite {arguments.output}")

    current_commit = require_clean_repository(ROOT)
    analysis_commit = arguments.analysis_commit or current_commit
    _validate_commit(ROOT, analysis_commit)
    if analysis_commit != current_commit:
        raise ValueError("analysis commit must equal the clean worktree HEAD")

    contract = _load_contract(arguments.contract)
    parent = _mapping(contract.get("parent"), path="parent")
    census_path = ROOT / cast(str, parent["exposure_census"])
    summary_path = ROOT / cast(str, parent["summary"])
    census_sha256 = _hash_file(census_path)
    summary_sha256 = _hash_file(summary_path)
    errors = validate_routing_contract(
        contract,
        exposure_census_sha256=census_sha256,
        summary_sha256=summary_sha256,
    )
    if errors:
        raise RuntimeError("invalid frozen routing contract: " + "; ".join(errors))
    parent_summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if parent_summary.get("decision") != parent.get("u1r_decision_remains_binding"):
        raise RuntimeError("local parent summary decision differs from frozen U1R failure")

    rows = load_jsonl(census_path)
    first_treatment = {row.get("treatment_transaction_hash") for row in rows[:500]}
    second_treatment = {row.get("treatment_transaction_hash") for row in rows[500:]}
    if len(first_treatment) != 1 or len(second_treatment) != 1 or first_treatment == second_treatment:
        raise RuntimeError("U1R rows no longer form the exact two 500-pool propagation batches")
    metrics = _mapping(contract.get("metrics"), path="metrics")
    top_k_raw = metrics.get("top_k")
    if not isinstance(top_k_raw, list) or not all(isinstance(value, int) for value in top_k_raw):
        raise RuntimeError("metrics.top_k must be an integer list")
    output = summarize_exposure_routing(rows, top_k=cast(list[int], top_k_raw))
    output["ownership"] = {
        "analysis_git_commit": analysis_commit,
        "computed_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "contract_sha256": _hash_file(arguments.contract),
        "parent_exposure_census_sha256": census_sha256,
        "parent_summary_sha256": summary_sha256,
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
