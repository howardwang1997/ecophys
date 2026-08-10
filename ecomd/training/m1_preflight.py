"""Fail-closed preflight for the frozen EcoMD v1 M1 reference training."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from ..data.yfinance_provenance import (
    repository_state,
    sha256_file,
    verify_audited_daily_manifest,
)
from ..eval.m1_contract import load_and_validate_m1_protocol
from .m0_contract import validate_m0_config


@dataclass(frozen=True)
class M1Preflight:
    protocol: dict[str, Any]
    data_manifest: dict[str, Any]
    execution_metadata: dict[str, Any]
    first_segment_stop_after_iter: int
    final_iter: int
    expected_parameter_count: int


def run_m1_preflight(
    *,
    config_path: Path,
    protocol_path: Path,
    manifest_path: Path,
    repo_root: Path,
) -> M1Preflight:
    """Validate immutable code/config/data bindings before CUDA initialization."""
    state = repository_state(repo_root)
    if not state["clean"]:
        raise RuntimeError(f"formal M1 training requires a clean worktree: {state['status_entries']}")

    config_payload = yaml.safe_load(config_path.read_text())
    if not isinstance(config_payload, dict):
        raise ValueError("M0 config must be a YAML mapping")
    validate_m0_config(config_payload)
    protocol = load_and_validate_m1_protocol(protocol_path, repo_root)
    contract = protocol["contract"]
    data = protocol["data"]
    training = protocol["training"]
    if sha256_file(config_path) != contract["m0_config_sha256"]:
        raise ValueError("provided M0 config does not match the protocol hash")

    frozen_manifest_path = (repo_root / str(data["manifest_path"])).resolve()
    if manifest_path.resolve() != frozen_manifest_path:
        raise ValueError(
            f"provided manifest path {manifest_path.resolve()} != frozen {frozen_manifest_path}"
        )
    manifest = verify_audited_daily_manifest(
        manifest_path,
        repo_root / "data/raw/yfinance",
        expected_manifest_sha256=str(data["manifest_sha256"]),
        expected_dataset_id=str(data["dataset_id"]),
    )
    train_splits = [record for record in manifest["audit"]["splits"] if record["name"] == "train"]
    if len(train_splits) != 1:
        raise ValueError("data manifest must contain exactly one train split")
    train_split = train_splits[0]
    if (int(train_split["year_lo"]), int(train_split["year_hi"])) != (2015, 2018):
        raise ValueError("M1 train split years changed")

    metadata = {
        "schema_version": 1,
        "run_id": "ecomd_v1_m1_spx_seed0",
        "git_sha": str(state["git_sha"]),
        "m0_config_sha256": sha256_file(config_path),
        "m1_protocol_sha256": sha256_file(protocol_path),
        "data_manifest_sha256": sha256_file(manifest_path),
        "data_canonical_payload_sha256": str(manifest["canonical_payload_sha256"]),
        "dataset_id": str(manifest["dataset_id"]),
        "train_return_float64_le_sha256": str(train_split["return_float64_le_sha256"]),
        "train_return_rows": int(train_split["return_rows"]),
    }
    return M1Preflight(
        protocol=protocol,
        data_manifest=manifest,
        execution_metadata=metadata,
        first_segment_stop_after_iter=int(training["first_segment_stop_after_iter"]),
        final_iter=int(training["final_iter"]),
        expected_parameter_count=int(contract["expected_parameter_count"]),
    )


def validate_m1_training_phase(
    preflight: M1Preflight,
    *,
    checkpoint_path: Path,
    resume: bool,
    stop_after_iter: int | None,
) -> tuple[int, int]:
    """Return the frozen segment bounds after checking checkpoint presence."""
    if resume:
        if not checkpoint_path.is_file():
            raise FileNotFoundError("M1 resume requires an existing checkpoint")
        if stop_after_iter is not None:
            raise ValueError("M1 resume segment must run to the frozen final iteration")
        return preflight.first_segment_stop_after_iter, preflight.final_iter
    if checkpoint_path.exists():
        raise FileExistsError("M1 first segment refuses an existing checkpoint")
    if stop_after_iter != preflight.first_segment_stop_after_iter:
        raise ValueError(
            "M1 first segment stop must equal "
            f"{preflight.first_segment_stop_after_iter}, got {stop_after_iter}"
        )
    return 0, preflight.first_segment_stop_after_iter


__all__ = ["M1Preflight", "run_m1_preflight", "validate_m1_training_phase"]
