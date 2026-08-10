"""Run the frozen Binance taker-flow response feasibility study on CPU."""

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

from ecomd.data.binance_ingest import _parse_zip
from ecomd.data.yfinance_provenance import (
    canonical_payload_sha256,
    repository_state,
    sha256_file,
)
from ecomd.physics.taker_flow_response import (
    MinuteMonth,
    evaluate_taker_flow_response,
)
from scripts.acquire_binance_taker_flow_q1 import validate_kline_frame

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOL = (
    REPO_ROOT / "configs/empirical_physics/taker_flow_response_feasibility_v1.yaml"
)
SOURCE_RESULT = (
    REPO_ROOT / "results/empirical_physics/regime_memory_exploratory_v1.json"
)
EXPECTED_DATASET_ID = "binance_spot_1m_q1_2024_taker_flow"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def verify_bound_inputs(
    protocol: dict[str, Any],
    manifest_path: Path,
    data_root: Path,
) -> dict[str, Any]:
    """Verify manifest binding and every archive/checksum byte before parsing values."""
    data = _mapping(protocol["data"], "data")
    if data["manifest_binding_status"] != (
        "bound_after_result_blind_acquisition_before_response_outputs"
    ):
        raise ValueError("Binance manifest is not bound for response analysis")
    if sha256_file(manifest_path) != data["manifest_file_sha256"]:
        raise ValueError("Binance manifest file hash mismatch")
    manifest = _load_json(manifest_path)
    if manifest.get("dataset_id") != EXPECTED_DATASET_ID:
        raise ValueError("Binance manifest dataset_id mismatch")
    canonical = canonical_payload_sha256(manifest)
    if manifest.get("canonical_payload_sha256") != canonical:
        raise ValueError("Binance manifest self-hash mismatch")
    if data["manifest_canonical_payload_sha256"] != canonical:
        raise ValueError("protocol/manifest canonical hash mismatch")
    repository = _mapping(manifest["repository"], "manifest.repository")
    if repository["git_sha"] != data["acquisition_protocol_git_sha"]:
        raise ValueError("acquisition commit mismatch")
    code = _mapping(manifest["code"], "manifest.code")
    if code["protocol_sha256"] != data["acquisition_protocol_sha256"]:
        raise ValueError("pre-acquisition protocol hash mismatch")
    policy = _mapping(manifest["policy"], "manifest.policy")
    expected_policy = {
        "universe_and_dates_frozen_before_acquisition": True,
        "official_checksum_required": True,
        "monthly_daily_crosscheck_required": True,
        "manifest_contains_price_flow_or_response_values": False,
        "raw_bytes_committed_or_publicly_redistributed": False,
        "response_metrics_computed_during_acquisition": False,
    }
    if policy != expected_policy:
        raise ValueError("manifest acquisition policy changed")
    summary = _mapping(manifest["summary"], "manifest.summary")
    if summary != {
        "monthly_archives": 9,
        "daily_crosscheck_archives": 27,
        "physical_files_including_checksums": 72,
        "all_official_checksums_passed": True,
        "all_monthly_daily_crosschecks_passed": True,
    }:
        raise ValueError("manifest summary differs from the frozen acquisition")
    records = [
        *_records(manifest["monthly_archives"], "monthly_archives"),
        *_records(manifest["daily_crosschecks"], "daily_crosschecks"),
    ]
    expected_paths: set[str] = set()
    resolved_root = data_root.resolve()
    for record in records:
        if record["sha256"] != record["official_checksum_sha256"]:
            raise ValueError("an archive differs from its official checksum")
        for path_key, hash_key in (
            ("relative_path", "sha256"),
            ("checksum_relative_path", "checksum_file_sha256"),
        ):
            relative = str(record[path_key])
            if relative in expected_paths:
                raise ValueError(f"duplicate manifest path: {relative}")
            expected_paths.add(relative)
            path = (data_root / relative).resolve()
            if not path.is_relative_to(resolved_root) or not path.is_file():
                raise ValueError(f"missing or escaping manifest path: {relative}")
            if sha256_file(path) != record[hash_key]:
                raise ValueError(f"physical file hash mismatch: {relative}")
        archive = data_root / str(record["relative_path"])
        if archive.stat().st_size != int(record["bytes"]):
            raise ValueError("physical archive byte size mismatch")
    actual_paths = {
        str(path.relative_to(data_root)) for path in data_root.rglob("*") if path.is_file()
    }
    if actual_paths != expected_paths:
        raise ValueError("physical Binance file set differs from manifest")
    return manifest


def load_minute_series(
    protocol: dict[str, Any],
    manifest: dict[str, Any],
    data_root: Path,
) -> dict[str, dict[str, MinuteMonth]]:
    """Parse only the nine bound monthly archives into exact day matrices."""
    data = _mapping(protocol["data"], "data")
    symbols = [str(value) for value in cast(list[object], data["symbols"])]
    months = [str(value) for value in cast(list[object], data["months"])]
    records = _records(manifest["monthly_archives"], "monthly_archives")
    lookup = {(str(record["symbol"]), str(record["month"])): record for record in records}
    if set(lookup) != {(symbol, month) for symbol in symbols for month in months}:
        raise ValueError("monthly archive registry differs from the frozen panel")
    series: dict[str, dict[str, MinuteMonth]] = {}
    for symbol in symbols:
        series[symbol] = {}
        for month in months:
            record = lookup[(symbol, month)]
            path = data_root / str(record["relative_path"])
            frame = _parse_zip(path.read_bytes())
            validate_kline_frame(
                frame,
                start_ms=int(record["first_open_time_ms"]),
                expected_rows=int(record["rows"]),
            )
            rows = len(frame)
            if rows % 1440 != 0:
                raise ValueError(f"{symbol}/{month} cannot reshape into UTC days")
            day_count = rows // 1440
            dates = tuple(
                value.strftime("%Y-%m-%d")
                for value in pd.date_range(
                    start=f"{month}-01", periods=day_count, freq="D", tz="UTC"
                )
            )
            series[symbol][month] = MinuteMonth(
                symbol=symbol,
                month=month,
                dates=dates,
                close=frame["close"].to_numpy(dtype=np.float64).reshape(day_count, 1440),
                quote_volume=frame["quote_volume"]
                .to_numpy(dtype=np.float64)
                .reshape(day_count, 1440),
                taker_buy_quote=frame["taker_buy_quote"]
                .to_numpy(dtype=np.float64)
                .reshape(day_count, 1440),
            )
    return series


def run(
    *,
    protocol_path: Path,
    manifest_path: Path,
    data_root: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Execute the sole frozen feasibility run from clean pushed source."""
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite formal output: {output_path}")
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    if temporary.exists():
        raise FileExistsError(f"refusing to overwrite stale temporary: {temporary}")
    state = repository_state(REPO_ROOT)
    if not state["clean"]:
        raise RuntimeError("formal taker-flow run requires a clean worktree")
    upstream = subprocess.run(
        ["git", "rev-parse", "@{u}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if upstream != state["git_sha"]:
        raise RuntimeError("formal taker-flow source commit must already be pushed")
    protocol = _load_yaml(protocol_path)
    if _mapping(protocol["compute"], "compute") != {
        "acquisition_and_analysis_cpu_only": True,
        "gpu_forbidden": True,
        "paid_data_forbidden": True,
        "h20_forbidden": True,
    }:
        raise ValueError("compute policy differs from the frozen contract")
    manifest = verify_bound_inputs(protocol, manifest_path, data_root)
    source_result = _load_json(SOURCE_RESULT)
    contract = _mapping(protocol["contract"], "contract")
    if sha256_file(SOURCE_RESULT) != contract["source_regime_result_file_sha256"]:
        raise ValueError("source regime-result file hash mismatch")
    if canonical_payload_sha256(source_result) != contract[
        "source_regime_result_canonical_sha256"
    ]:
        raise ValueError("source regime-result canonical hash mismatch")
    started = _utc_now()
    series = load_minute_series(protocol, manifest, data_root)
    evaluation = evaluate_taker_flow_response(series, protocol)
    finished = _utc_now()
    payload: dict[str, Any] = {
        "schema_version": 1,
        "status": "formal_taker_flow_response_feasibility_complete",
        "contract": {
            "name": contract["name"],
            "version": contract["version"],
            "purpose": contract["purpose"],
            "evidence_class": contract["evidence_class"],
            "pre_output_protocol_correction": contract[
                "pre_output_protocol_correction"
            ],
        },
        "run": {
            "started_at_utc": started,
            "finished_at_utc": finished,
            "command_template": (
                "conda run -n ecophys python -m scripts.run_taker_flow_response_feasibility "
                "--data-root <bound-root> --output <result.json>"
            ),
            "cpu_only": True,
            "gpu_used": False,
        },
        "repository": {**state, "upstream_sha": upstream},
        "bindings": {
            "protocol_path": str(protocol_path.relative_to(REPO_ROOT)),
            "analysis_protocol_sha256": sha256_file(protocol_path),
            "manifest_path": str(manifest_path.relative_to(REPO_ROOT)),
            "manifest_file_sha256": sha256_file(manifest_path),
            "manifest_canonical_payload_sha256": manifest[
                "canonical_payload_sha256"
            ],
            "acquisition_protocol_git_sha": manifest["repository"]["git_sha"],
            "acquisition_protocol_sha256": manifest["code"]["protocol_sha256"],
            "source_regime_result_path": str(SOURCE_RESULT.relative_to(REPO_ROOT)),
            "source_regime_result_file_sha256": sha256_file(SOURCE_RESULT),
            "source_regime_result_canonical_payload_sha256": source_result[
                "canonical_payload_sha256"
            ],
            "raw_data_publicly_redistributed": False,
        },
        "code": {
            "taker_flow_response_sha256": sha256_file(
                REPO_ROOT / "ecomd/physics/taker_flow_response.py"
            ),
            "runner_sha256": sha256_file(Path(__file__).resolve()),
            "acquisition_validator_sha256": sha256_file(
                REPO_ROOT / "scripts/acquire_binance_taker_flow_q1.py"
            ),
            "binance_parser_sha256": sha256_file(
                REPO_ROOT / "ecomd/data/binance_ingest.py"
            ),
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": importlib.metadata.version("numpy"),
            "pandas": importlib.metadata.version("pandas"),
            "pyarrow": importlib.metadata.version("pyarrow"),
        },
        "data": {
            "symbols": _mapping(protocol["data"], "data")["symbols"],
            "months": _mapping(protocol["data"], "data")["months"],
            "monthly_archives": 9,
            "all_official_checksums_and_crosschecks_passed": True,
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


def _load_json(path: Path) -> dict[str, Any]:
    return _mapping(json.loads(path.read_text()), str(path))


def _load_yaml(path: Path) -> dict[str, Any]:
    return _mapping(yaml.safe_load(path.read_text()), str(path))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT
        / "data/manifests/binance_spot_1m_q1_2024_taker_flow.json",
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
                "decision": payload["evaluation"]["decision"],
                "feasibility_passed": payload["evaluation"]["feasibility_passed"],
                "primary_gate_clauses": payload["evaluation"][
                    "primary_gate_clauses"
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
