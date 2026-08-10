"""Run frozen unseen-instrument evaluator-v2 confirmation on CPU."""

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

import yaml

from ecomd.data.yfinance_provenance import (
    canonical_payload_sha256,
    repository_state,
    sha256_file,
)
from ecomd.eval.fresh_market_confirmation import evaluate_fresh_market_confirmation
from scripts.run_evaluator_v2_feasibility import load_unsealed_series

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DATASET_ID = "evaluator_v2_fresh_markets_daily_2005_2024"
SOURCE_SAMPLE_COMPLEXITY_RESULT = (
    REPO_ROOT / "results/evaluator_v2/sample_complexity_v1.json"
)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def verify_fresh_bound_inputs(
    protocol: dict[str, Any],
    manifest_path: Path,
    data_root: Path,
) -> dict[str, Any]:
    """Verify universe binding and every raw shard without parsing sealed values."""
    data_contract = _mapping(protocol["data"], "data")
    if data_contract["manifest_binding_status"] != (
        "bound_after_result_blind_acquisition_before_metric_outputs"
    ):
        raise ValueError("fresh-market manifest is not bound")
    if sha256_file(manifest_path) != data_contract["manifest_file_sha256"]:
        raise ValueError("fresh-market manifest file hash mismatch")
    manifest = _load_json_object(manifest_path)
    if manifest.get("dataset_id") != EXPECTED_DATASET_ID:
        raise ValueError("fresh-market dataset_id mismatch")
    canonical = canonical_payload_sha256(manifest)
    if manifest.get("canonical_payload_sha256") != canonical:
        raise ValueError("fresh-market manifest self-hash mismatch")
    if data_contract["manifest_canonical_payload_sha256"] != canonical:
        raise ValueError("protocol/manifest canonical hash mismatch")
    repository = _mapping(manifest["repository"], "manifest.repository")
    if repository["git_sha"] != data_contract["acquisition_protocol_git_sha"]:
        raise ValueError("acquisition commit mismatch")
    code = _mapping(manifest["code"], "manifest.code")
    if code["protocol_sha256"] != data_contract["acquisition_protocol_sha256"]:
        raise ValueError("pre-acquisition protocol hash mismatch")
    policy = _mapping(manifest["policy"], "manifest.policy")
    if policy != {
        "instrument_universe_frozen_before_acquisition": True,
        "manifest_contains_prices_or_returns": False,
        "raw_bytes_committed_or_publicly_redistributed": False,
        "sealed_2020_not_used_for_training_or_selection": True,
        "time_split_only": True,
    }:
        raise ValueError("fresh-market manifest policy changed")
    audits = _mapping(manifest["audits"], "manifest.audits")
    expected_symbols = {
        str(value) for value in cast(list[object], data_contract["all_symbols"])
    }
    if set(audits) != expected_symbols:
        raise ValueError("fresh-market symbol set mismatch")
    expected_paths: set[str] = set()
    resolved_root = data_root.resolve()
    for symbol, raw_audit in audits.items():
        audit = _mapping(raw_audit, f"manifest.audits.{symbol}")
        for record in _records(audit["files"], f"manifest.audits.{symbol}.files"):
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
                raise ValueError(f"raw shard size mismatch: {relative}")
            if sha256_file(path) != str(record["sha256"]):
                raise ValueError(f"raw shard hash mismatch: {relative}")
    actual_paths = {
        str(path.relative_to(data_root)) for path in data_root.rglob("*.parquet")
    }
    if actual_paths != expected_paths:
        raise ValueError("physical fresh-market parquet set differs from manifest")
    return manifest


def run(
    *,
    protocol_path: Path,
    manifest_path: Path,
    data_root: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Verify committed inputs, execute confirmation, and write one formal result."""
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite formal output: {output_path}")
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    if temporary.exists():
        raise FileExistsError(f"refusing to overwrite stale temporary: {temporary}")
    state = repository_state(REPO_ROOT)
    if not state["clean"]:
        raise RuntimeError("formal fresh-market run requires a clean worktree")
    upstream = subprocess.run(
        ["git", "rev-parse", "@{u}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if upstream != state["git_sha"]:
        raise RuntimeError("formal fresh-market source commit must be pushed")
    protocol = _load_yaml_object(protocol_path)
    if _mapping(protocol["compute"], "compute") != {
        "cpu_only": True,
        "gpu_forbidden": True,
        "paid_data_forbidden": True,
        "h20_forbidden": True,
    }:
        raise ValueError("compute policy differs from frozen contract")
    manifest = verify_fresh_bound_inputs(protocol, manifest_path, data_root)
    source_result = _load_json_object(SOURCE_SAMPLE_COMPLEXITY_RESULT)
    contract = _mapping(protocol["contract"], "contract")
    if canonical_payload_sha256(source_result) != contract[
        "source_sample_complexity_result_canonical_sha256"
    ]:
        raise ValueError("source sample-complexity result hash mismatch")
    loader_protocol = {
        **protocol,
        "data": {
            **_mapping(protocol["data"], "data"),
            "symbols": _mapping(protocol["data"], "data")["all_symbols"],
        },
    }
    series = load_unsealed_series(loader_protocol, manifest, data_root)
    started = _utc_now()
    evaluation = evaluate_fresh_market_confirmation(series, protocol)
    finished = _utc_now()
    payload: dict[str, Any] = {
        "schema_version": 1,
        "status": "formal_evaluator_v2_fresh_market_confirmation_complete",
        "contract": {
            "name": contract["name"],
            "version": contract["version"],
            "purpose": contract["purpose"],
            "instrument_holdout_not_independent_macro_time_holdout": contract[
                "instrument_holdout_not_independent_macro_time_holdout"
            ],
        },
        "run": {
            "started_at_utc": started,
            "finished_at_utc": finished,
            "command_template": (
                "conda run -n ecophys python -m scripts.run_evaluator_v2_fresh_market_confirmation "
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
            "source_sample_complexity_result_path": str(
                SOURCE_SAMPLE_COMPLEXITY_RESULT.relative_to(REPO_ROOT)
            ),
            "source_sample_complexity_result_file_sha256": sha256_file(
                SOURCE_SAMPLE_COMPLEXITY_RESULT
            ),
            "source_sample_complexity_result_canonical_sha256": source_result[
                "canonical_payload_sha256"
            ],
            "sealed_split_parsed_for_metrics": False,
            "raw_data_publicly_redistributed": False,
        },
        "code": {
            "confirmation_evaluator_sha256": sha256_file(
                REPO_ROOT / "ecomd/eval/fresh_market_confirmation.py"
            ),
            "evaluator_primitives_sha256": sha256_file(
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
        default=REPO_ROOT
        / "configs/evaluator_v2/fresh_market_confirmation_v1.yaml",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT
        / "data/manifests/evaluator_v2_fresh_markets_daily_2005_2024.json",
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
                "core_suite_qualified": payload["evaluation"][
                    "core_suite_qualified"
                ],
                "metric_decisions": payload["evaluation"]["metric_decisions"],
                "model_scoring_or_training_authorized": payload["evaluation"][
                    "model_scoring_or_training_authorized"
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
