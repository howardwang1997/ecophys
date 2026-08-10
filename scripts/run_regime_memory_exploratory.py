"""Run the frozen lagged-regime volatility-memory study on bound free data."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd
import yaml

from ecomd.data.parquet_io import read_single_parquet
from ecomd.data.yfinance_provenance import (
    canonical_payload_sha256,
    repository_state,
    sha256_file,
)
from ecomd.physics.regime_memory import (
    HalfYearBlock,
    build_regime_rows,
    evaluate_regime_memory,
    make_half_year_block,
    period_key,
)
from scripts.run_evaluator_v2_feasibility import verify_bound_inputs
from scripts.run_evaluator_v2_fresh_market_confirmation import verify_fresh_bound_inputs

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOL = (
    REPO_ROOT / "configs/empirical_physics/regime_memory_exploratory_v1.yaml"
)
FIRST_SOURCE_PROTOCOL = REPO_ROOT / "configs/evaluator_v2/feasibility_v1.yaml"
SECOND_SOURCE_PROTOCOL = (
    REPO_ROOT / "configs/evaluator_v2/fresh_market_confirmation_v1.yaml"
)
SOURCE_RESULT = REPO_ROOT / "results/evaluator_v2/fresh_market_confirmation_v1.json"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def load_balanced_half_year_blocks(
    protocol: dict[str, Any],
    first_manifest: dict[str, Any],
    second_manifest: dict[str, Any],
    first_data_root: Path,
    second_data_root: Path,
) -> tuple[dict[str, dict[str, HalfYearBlock]], dict[str, Any]]:
    """Load only nonsealed values after verifying the coverage-only panel rule."""
    data = _mapping(protocol["data"], "data")
    periods = _mapping(protocol["periods"], "periods")
    all_symbols = [str(value) for value in cast(list[object], data["all_spent_symbols"])]
    balanced = {str(value) for value in cast(list[object], data["balanced_symbols"])}
    excluded = set(_mapping(data["coverage_excluded_symbols"], "coverage exclusions"))
    if balanced | excluded != set(all_symbols) or balanced & excluded:
        raise ValueError("balanced/excluded symbols do not partition all_spent_symbols")
    sealed_year = int(data["sealed_year"])
    return_length = int(periods["return_length"])
    manifest_by_symbol: dict[str, tuple[dict[str, Any], Path]] = {}
    for manifest, root in (
        (first_manifest, first_data_root),
        (second_manifest, second_data_root),
    ):
        audits = _mapping(manifest["audits"], "manifest.audits")
        for symbol in audits:
            if symbol in manifest_by_symbol:
                raise ValueError(f"duplicate symbol across manifests: {symbol}")
            manifest_by_symbol[symbol] = (manifest, root)
    if set(manifest_by_symbol) != set(all_symbols):
        raise ValueError("manifest union differs from all_spent_symbols")

    blocks: dict[str, dict[str, HalfYearBlock]] = {}
    coverage: dict[str, Any] = {}
    for symbol in all_symbols:
        manifest, root = manifest_by_symbol[symbol]
        audit = _mapping(_mapping(manifest["audits"], "audits")[symbol], symbol)
        records = _records(audit["files"], f"{symbol}.files")
        files_by_year = {int(record["year"]): record for record in records}
        symbol_counts: dict[str, int] = {}
        symbol_blocks: dict[str, HalfYearBlock] = {}
        for year in range(2005, 2025):
            if year == sealed_year:
                continue
            record = files_by_year[year]
            path = root / str(record["relative_path"])
            if symbol in balanced:
                frame = read_single_parquet(path)
                timestamps = pd.to_datetime(frame["timestamp"], utc=True)
                order = np.argsort(timestamps.to_numpy())
                frame = frame.iloc[order].reset_index(drop=True)
                timestamps = pd.to_datetime(frame["timestamp"], utc=True)
                if set(frame["symbol"].astype(str).unique()) != {symbol}:
                    raise ValueError(f"{symbol}/{year} has a symbol mismatch")
            else:
                frame = pd.read_parquet(path, columns=["timestamp"])
                timestamps = pd.to_datetime(frame["timestamp"], utc=True).sort_values(
                    ignore_index=True
                )
            if not timestamps.is_monotonic_increasing or bool(timestamps.duplicated().any()):
                raise ValueError(f"{symbol}/{year} timestamps are not unique/ordered")
            for half in (1, 2):
                period = period_key(year, half)
                mask = (
                    timestamps.dt.month <= 6
                    if half == 1
                    else timestamps.dt.month >= 7
                )
                available_returns = int(mask.sum()) - 1
                symbol_counts[period] = available_returns
                if symbol not in balanced:
                    continue
                half_frame = frame.loc[mask.to_numpy()].reset_index(drop=True)
                symbol_blocks[period] = make_half_year_block(
                    symbol,
                    period,
                    half_frame["adjusted_close"].to_numpy(dtype=np.float64),
                    half_frame["volume"].to_numpy(dtype=np.float64),
                    return_length=return_length,
                )
        eligible_periods = sum(
            count >= return_length for count in symbol_counts.values()
        )
        coverage[symbol] = {
            "nonsealed_half_years": len(symbol_counts),
            "eligible_half_years": eligible_periods,
            "minimum_available_returns": min(symbol_counts.values()),
            "maximum_available_returns": max(symbol_counts.values()),
            "balanced_panel_included": symbol in balanced,
        }
        if symbol in balanced:
            if eligible_periods != len(symbol_counts) or len(symbol_blocks) != 38:
                raise ValueError(f"balanced symbol fails exact coverage: {symbol}")
            blocks[symbol] = symbol_blocks
        elif eligible_periods == len(symbol_counts):
            raise ValueError(f"coverage-excluded symbol unexpectedly has complete coverage: {symbol}")
    return blocks, coverage


def run(
    *,
    protocol_path: Path,
    first_data_root: Path,
    second_data_root: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Verify frozen inputs, execute once from pushed source, and write atomically."""
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite formal output: {output_path}")
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    if temporary.exists():
        raise FileExistsError(f"refusing to overwrite stale temporary: {temporary}")
    state = repository_state(REPO_ROOT)
    if not state["clean"]:
        raise RuntimeError("formal regime-memory run requires a clean worktree")
    upstream = subprocess.run(
        ["git", "rev-parse", "@{u}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if upstream != state["git_sha"]:
        raise RuntimeError("formal regime-memory source commit must already be pushed")

    protocol = _load_yaml(protocol_path)
    if _mapping(protocol["compute"], "compute") != {
        "cpu_only": True,
        "gpu_forbidden": True,
        "paid_data_forbidden": True,
        "h20_forbidden": True,
    }:
        raise ValueError("compute policy differs from the frozen contract")
    data = _mapping(protocol["data"], "data")
    first_binding = _mapping(data["first_manifest"], "first_manifest")
    second_binding = _mapping(data["second_manifest"], "second_manifest")
    first_manifest_path = REPO_ROOT / str(first_binding["path"])
    second_manifest_path = REPO_ROOT / str(second_binding["path"])
    first_source_protocol = _load_yaml(FIRST_SOURCE_PROTOCOL)
    second_source_protocol = _load_yaml(SECOND_SOURCE_PROTOCOL)
    first_manifest = verify_bound_inputs(
        first_source_protocol, first_manifest_path, first_data_root
    )
    second_manifest = verify_fresh_bound_inputs(
        second_source_protocol, second_manifest_path, second_data_root
    )
    for binding, path, manifest in (
        (first_binding, first_manifest_path, first_manifest),
        (second_binding, second_manifest_path, second_manifest),
    ):
        if sha256_file(path) != binding["file_sha256"]:
            raise ValueError("protocol manifest file hash mismatch")
        if canonical_payload_sha256(manifest) != binding["canonical_payload_sha256"]:
            raise ValueError("protocol manifest canonical hash mismatch")
    source_result = _load_json(SOURCE_RESULT)
    contract = _mapping(protocol["contract"], "contract")
    if sha256_file(SOURCE_RESULT) != contract["source_fresh_result_file_sha256"]:
        raise ValueError("source fresh-result file hash mismatch")
    if canonical_payload_sha256(source_result) != contract[
        "source_fresh_result_canonical_sha256"
    ]:
        raise ValueError("source fresh-result canonical hash mismatch")

    started = _utc_now()
    blocks, coverage = load_balanced_half_year_blocks(
        protocol,
        first_manifest,
        second_manifest,
        first_data_root,
        second_data_root,
    )
    rows = build_regime_rows(blocks, protocol)
    evaluation = evaluate_regime_memory(rows, protocol)
    finished = _utc_now()
    payload: dict[str, Any] = {
        "schema_version": 1,
        "status": "formal_regime_memory_exploratory_complete",
        "contract": {
            "name": contract["name"],
            "version": contract["version"],
            "evidence_class": contract["evidence_class"],
            "purpose": contract["purpose"],
        },
        "run": {
            "started_at_utc": started,
            "finished_at_utc": finished,
            "command_template": (
                "conda run -n ecophys python -m scripts.run_regime_memory_exploratory "
                "--first-data-root <bound-root-1> --second-data-root <bound-root-2> "
                "--output <result.json>"
            ),
            "cpu_only": True,
            "gpu_used": False,
        },
        "repository": {**state, "upstream_sha": upstream},
        "bindings": {
            "protocol_path": str(protocol_path.relative_to(REPO_ROOT)),
            "protocol_sha256": sha256_file(protocol_path),
            "first_manifest_path": str(first_manifest_path.relative_to(REPO_ROOT)),
            "first_manifest_file_sha256": sha256_file(first_manifest_path),
            "first_manifest_canonical_payload_sha256": first_manifest[
                "canonical_payload_sha256"
            ],
            "second_manifest_path": str(second_manifest_path.relative_to(REPO_ROOT)),
            "second_manifest_file_sha256": sha256_file(second_manifest_path),
            "second_manifest_canonical_payload_sha256": second_manifest[
                "canonical_payload_sha256"
            ],
            "source_fresh_result_path": str(SOURCE_RESULT.relative_to(REPO_ROOT)),
            "source_fresh_result_file_sha256": sha256_file(SOURCE_RESULT),
            "source_fresh_result_canonical_payload_sha256": source_result[
                "canonical_payload_sha256"
            ],
            "sealed_2020_parsed_for_metrics": False,
            "raw_data_publicly_redistributed": False,
        },
        "code": {
            "regime_memory_sha256": sha256_file(
                REPO_ROOT / "ecomd/physics/regime_memory.py"
            ),
            "stylized_facts_sha256": sha256_file(
                REPO_ROOT / "ecomd/eval/stylized_facts.py"
            ),
            "runner_sha256": sha256_file(Path(__file__).resolve()),
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": importlib.metadata.version("numpy"),
            "scipy": importlib.metadata.version("scipy"),
            "pandas": importlib.metadata.version("pandas"),
            "pyarrow": importlib.metadata.version("pyarrow"),
        },
        "data": {
            "coverage_inventory": coverage,
            "balanced_symbol_count": len(blocks),
            "half_year_blocks_per_balanced_symbol": 38,
            "regime_rows": len(rows),
            "sealed_year_loaded": False,
        },
        "evaluation": evaluation,
    }
    payload["canonical_payload_sha256"] = canonical_payload_sha256(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(output_path)
    return payload


def _mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return cast(dict[str, Any], value)


def _records(value: object, name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not all(isinstance(record, dict) for record in value):
        raise ValueError(f"{name} must be a list of objects")
    return cast(list[dict[str, Any]], value)


def _load_yaml(path: Path) -> dict[str, Any]:
    return _mapping(yaml.safe_load(path.read_text()), str(path))


def _load_json(path: Path) -> dict[str, Any]:
    return _mapping(json.loads(path.read_text()), str(path))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--first-data-root", type=Path, required=True)
    parser.add_argument("--second-data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = run(
        protocol_path=args.protocol.resolve(),
        first_data_root=args.first_data_root.resolve(),
        second_data_root=args.second_data_root.resolve(),
        output_path=args.output.resolve(),
    )
    print(
        json.dumps(
            {
                "canonical_payload_sha256": payload["canonical_payload_sha256"],
                "decision": payload["evaluation"]["decision"],
                "primary_gate_clauses": payload["evaluation"][
                    "primary_gate_clauses"
                ],
                "primary_nominated": payload["evaluation"]["primary_nominated"],
                "output": str(args.output.resolve()),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
