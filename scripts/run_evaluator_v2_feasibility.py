"""Run the frozen evaluator-v2 real-data qualification study on CPU."""

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
    sha256_float64,
)
from ecomd.eval.evaluator_v2 import SplitSeries, evaluate_feasibility

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DATASET_ID = "evaluator_v2_yahoo_daily_four_markets_2005_2024"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def verify_bound_inputs(
    protocol: dict[str, Any],
    manifest_path: Path,
    data_root: Path,
) -> dict[str, Any]:
    """Fail closed unless protocol, manifest, and every physical shard agree."""
    data_contract = _mapping(protocol.get("data"), "protocol.data")
    if data_contract.get("manifest_binding_status") != (
        "bound_after_result_blind_acquisition_before_metric_outputs"
    ):
        raise ValueError("protocol manifest is not bound for metric computation")
    expected_file_sha = str(data_contract["manifest_file_sha256"])
    if sha256_file(manifest_path) != expected_file_sha:
        raise ValueError("bound manifest file SHA-256 mismatch")
    manifest = _load_json_object(manifest_path)
    if manifest.get("dataset_id") != EXPECTED_DATASET_ID:
        raise ValueError("manifest dataset_id mismatch")
    actual_canonical_sha = canonical_payload_sha256(manifest)
    if manifest.get("canonical_payload_sha256") != actual_canonical_sha:
        raise ValueError("manifest canonical self-hash mismatch")
    if data_contract.get("manifest_canonical_payload_sha256") != actual_canonical_sha:
        raise ValueError("protocol/manifest canonical hash mismatch")
    manifest_repository = _mapping(manifest.get("repository"), "manifest.repository")
    if manifest_repository.get("git_sha") != data_contract.get(
        "acquisition_protocol_git_sha"
    ):
        raise ValueError("manifest acquisition commit mismatch")
    manifest_code = _mapping(manifest.get("code"), "manifest.code")
    if manifest_code.get("protocol_sha256") != data_contract.get(
        "acquisition_protocol_sha256"
    ):
        raise ValueError("manifest pre-acquisition protocol hash mismatch")
    policy = _mapping(manifest.get("policy"), "manifest.policy")
    if policy.get("sealed_2020_not_used_for_training_or_selection") is not True:
        raise ValueError("sealed-period policy missing")
    if policy.get("manifest_contains_prices_or_returns") is not False:
        raise ValueError("manifest no-values policy missing")

    audits = _mapping(manifest.get("audits"), "manifest.audits")
    expected_symbols = {str(symbol) for symbol in cast(list[object], data_contract["symbols"])}
    if set(audits) != expected_symbols:
        raise ValueError("manifest symbol set differs from protocol")
    expected_paths: set[str] = set()
    resolved_root = data_root.resolve()
    for symbol, raw_audit in audits.items():
        audit = _mapping(raw_audit, f"manifest.audits.{symbol}")
        files = _records(audit.get("files"), f"manifest.audits.{symbol}.files")
        for record in files:
            relative = str(record["relative_path"])
            if relative in expected_paths:
                raise ValueError(f"duplicate manifest path: {relative}")
            expected_paths.add(relative)
            path = (data_root / relative).resolve()
            if not path.is_relative_to(resolved_root):
                raise ValueError(f"manifest path escapes data root: {relative}")
            if not path.is_file():
                raise FileNotFoundError(path)
            if path.stat().st_size != int(record["bytes"]):
                raise ValueError(f"file-size mismatch: {relative}")
            if sha256_file(path) != str(record["sha256"]):
                raise ValueError(f"file SHA-256 mismatch: {relative}")
    actual_paths = {
        str(path.relative_to(data_root)) for path in data_root.rglob("*.parquet")
    }
    if actual_paths != expected_paths:
        raise ValueError("physical parquet set differs from bound manifest")
    return manifest


def load_unsealed_series(
    protocol: dict[str, Any],
    manifest: dict[str, Any],
    data_root: Path,
) -> dict[str, dict[str, SplitSeries]]:
    """Load declared non-sealed splits and verify their derived-return hashes."""
    data_contract = _mapping(protocol.get("data"), "protocol.data")
    split_years = _mapping(data_contract.get("splits"), "protocol.data.splits")
    audits = _mapping(manifest.get("audits"), "manifest.audits")
    series_by_symbol: dict[str, dict[str, SplitSeries]] = {}
    for raw_symbol in cast(list[object], data_contract["symbols"]):
        symbol = str(raw_symbol)
        audit = _mapping(audits[symbol], f"manifest.audits.{symbol}")
        file_records = _records(audit.get("files"), f"manifest.audits.{symbol}.files")
        files_by_year = {int(record["year"]): record for record in file_records}
        manifest_splits = {
            str(record["name"]): record
            for record in _records(
                audit.get("splits"), f"manifest.audits.{symbol}.splits"
            )
        }
        symbol_series: dict[str, SplitSeries] = {}
        for split_name, raw_bounds in split_years.items():
            if split_name == "sealed_crash":
                continue
            bounds = cast(list[object], raw_bounds)
            year_lo, year_hi = int(str(bounds[0])), int(str(bounds[1]))
            frames: list[pd.DataFrame] = []
            for year in range(year_lo, year_hi + 1):
                record = files_by_year[year]
                path = data_root / str(record["relative_path"])
                frames.append(read_single_parquet(path))
            frame = pd.concat(frames, ignore_index=True)
            timestamps = pd.to_datetime(frame["timestamp"], utc=True)
            order = np.argsort(timestamps.to_numpy())
            frame = frame.iloc[order].reset_index(drop=True)
            timestamps = pd.to_datetime(frame["timestamp"], utc=True)
            if not timestamps.is_monotonic_increasing or bool(timestamps.duplicated().any()):
                raise ValueError(f"{symbol}/{split_name} timestamps are not unique/ordered")
            if set(frame["symbol"].astype(str).unique()) != {symbol}:
                raise ValueError(f"{symbol}/{split_name} has a symbol mismatch")
            prices = frame["adjusted_close"].to_numpy(dtype=np.float64)
            if not np.all(np.isfinite(prices)) or np.any(prices <= 0.0):
                raise ValueError(f"{symbol}/{split_name} has invalid adjusted_close")
            returns = np.diff(np.log(prices))
            expected_return_sha = str(manifest_splits[split_name]["return_float64_le_sha256"])
            if sha256_float64(returns) != expected_return_sha:
                raise ValueError(f"{symbol}/{split_name} derived-return SHA mismatch")
            volume = frame["volume"].to_numpy(dtype=np.float64)[1:]
            if volume.size != returns.size:
                raise ValueError(f"{symbol}/{split_name} return/volume alignment failed")
            symbol_series[split_name] = SplitSeries(returns=returns, volume=volume)
        series_by_symbol[symbol] = symbol_series
    return series_by_symbol


def run(
    *,
    protocol_path: Path,
    manifest_path: Path,
    data_root: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Verify committed inputs, execute the CPU study, and atomically write JSON."""
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite formal output: {output_path}")
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    if temporary.exists():
        raise FileExistsError(f"refusing to overwrite stale formal temporary: {temporary}")
    state = repository_state(REPO_ROOT)
    if not state["clean"]:
        raise RuntimeError("formal evaluator-v2 run requires a clean worktree")
    upstream = subprocess.run(
        ["git", "rev-parse", "@{u}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if upstream != state["git_sha"]:
        raise RuntimeError("formal evaluator-v2 source commit must already be pushed")
    protocol = _load_yaml_object(protocol_path)
    compute = _mapping(protocol.get("compute"), "protocol.compute")
    if compute != {
        "cpu_only": True,
        "gpu_forbidden": True,
        "paid_data_forbidden": True,
        "h20_forbidden": True,
    }:
        raise ValueError("compute policy differs from frozen CPU-only contract")
    manifest = verify_bound_inputs(protocol, manifest_path, data_root)
    series = load_unsealed_series(protocol, manifest, data_root)
    started = _utc_now()
    evaluation = evaluate_feasibility(series, protocol)
    finished = _utc_now()
    payload: dict[str, Any] = {
        "schema_version": 1,
        "status": "formal_evaluator_v2_feasibility_complete",
        "contract": {
            "name": _mapping(protocol["contract"], "protocol.contract")["name"],
            "version": _mapping(protocol["contract"], "protocol.contract")["version"],
            "purpose": _mapping(protocol["contract"], "protocol.contract")["purpose"],
        },
        "run": {
            "started_at_utc": started,
            "finished_at_utc": finished,
            "command_template": (
                "conda run -n ecophys python -m scripts.run_evaluator_v2_feasibility "
                "--data-root <bound-internal-root> --output <fresh-result.json>"
            ),
            "cpu_only": True,
            "gpu_used": False,
        },
        "repository": {**state, "upstream_sha": upstream},
        "bindings": {
            "protocol_path": str(protocol_path.relative_to(REPO_ROOT)),
            "protocol_sha256": sha256_file(protocol_path),
            "manifest_path": str(manifest_path.relative_to(REPO_ROOT)),
            "manifest_file_sha256": sha256_file(manifest_path),
            "manifest_canonical_payload_sha256": manifest[
                "canonical_payload_sha256"
            ],
            "dataset_id": manifest["dataset_id"],
            "data_root_publicly_redistributed": False,
            "sealed_split_parsed_for_metrics": False,
        },
        "code": {
            "evaluator_v2_sha256": sha256_file(
                REPO_ROOT / "ecomd/eval/evaluator_v2.py"
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
            "arch": importlib.metadata.version("arch"),
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


def _load_json_object(path: Path) -> dict[str, Any]:
    return _mapping(json.loads(path.read_text()), str(path))


def _load_yaml_object(path: Path) -> dict[str, Any]:
    return _mapping(yaml.safe_load(path.read_text()), str(path))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--protocol",
        type=Path,
        default=REPO_ROOT / "configs/evaluator_v2/feasibility_v1.yaml",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT
        / "data/manifests/evaluator_v2_free_daily_2005_2024.json",
    )
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = run(
        protocol_path=args.protocol.resolve(),
        manifest_path=args.manifest.resolve(),
        data_root=args.data_root.resolve(),
        output_path=args.output.resolve(),
    )
    print(
        json.dumps(
            {
                "canonical_payload_sha256": payload["canonical_payload_sha256"],
                "eligible_metric_names": payload["evaluation"][
                    "eligible_metric_names"
                ],
                "output": str(args.output.resolve()),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
