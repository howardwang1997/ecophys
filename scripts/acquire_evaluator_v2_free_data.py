"""Acquire the frozen free daily-market input for evaluator-v2 feasibility."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ecomd.data.yfinance_ingest import IngestConfig, ingest_one
from ecomd.data.yfinance_provenance import (
    TemporalSplit,
    audit_daily_shards,
    repository_state,
    sha256_file,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SYMBOLS = ("^GSPC", "^NDX", "GLD", "EURUSD=X")
START = "2005-01-01"
END = "2025-01-01"
INTERVAL = "1d"
EXPECTED_YEARS = tuple(range(2005, 2025))
SPLITS = (
    TemporalSplit("reference", "estimator_center_only", 2005, 2009),
    TemporalSplit("conformal_calibration", "estimator_radius_only", 2010, 2014),
    TemporalSplit("confirmation", "independent_self_coverage", 2015, 2018),
    TemporalSplit("report_only_guard", "report_only_no_selection", 2019, 2019),
    TemporalSplit("sealed_crash", "sealed_no_selection", 2020, 2020, sealed=True),
    TemporalSplit("temporal_test", "independent_temporal_self_coverage", 2021, 2024),
)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _canonical_sha(payload: dict[str, Any]) -> str:
    canonical = dict(payload)
    canonical.pop("canonical_payload_sha256", None)
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def acquire(out_dir: Path, manifest_path: Path) -> dict[str, Any]:
    """Acquire every frozen symbol into a fresh root and write a no-values manifest."""
    state = repository_state(REPO_ROOT)
    if not state["clean"]:
        raise RuntimeError("formal evaluator-v2 acquisition requires a clean worktree")
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"refusing to mix or overwrite an acquisition: {out_dir}")

    started = _utc_now()
    for symbol in SYMBOLS:
        paths = ingest_one(
            symbol,
            IngestConfig(
                symbols=(symbol,),
                start=START,
                end=END,
                interval=INTERVAL,
                out_dir=out_dir,
                retries=3,
                sleep_between=0.5,
            ),
        )
        if len(paths) != len(EXPECTED_YEARS):
            raise RuntimeError(
                f"expected {len(EXPECTED_YEARS)} shards for {symbol}, wrote {len(paths)}"
            )
    finished = _utc_now()
    audits = {
        symbol: audit_daily_shards(
            out_dir,
            symbol=symbol,
            interval=INTERVAL,
            expected_years=EXPECTED_YEARS,
            splits=SPLITS,
        )
        for symbol in SYMBOLS
    }
    payload: dict[str, Any] = {
        "schema_version": 1,
        "dataset_id": "evaluator_v2_yahoo_daily_four_markets_2005_2024",
        "status": "acquired_and_audited_no_values_disclosed",
        "source": {
            "provider": "Yahoo Finance",
            "access_library": "yfinance",
            "redistribution": "excluded_from_public_artifacts",
            "redistribution_reason": "third-party terms; repository MIT license covers code only",
        },
        "request": {
            "symbols": list(SYMBOLS),
            "start_inclusive": START,
            "end_exclusive": END,
            "interval": INTERVAL,
            "auto_adjust": False,
            "actions": True,
            "progress": False,
            "threads": False,
        },
        "acquisition": {
            "started_at_utc": started,
            "finished_at_utc": finished,
            "command_template": (
                "conda run -n ecophys python -m scripts.acquire_evaluator_v2_free_data "
                "--out-dir <internal-dir> --manifest <manifest.json>"
            ),
        },
        "repository": state,
        "code": {
            "ingest_sha256": sha256_file(REPO_ROOT / "ecomd/data/yfinance_ingest.py"),
            "audit_sha256": sha256_file(REPO_ROOT / "ecomd/data/yfinance_provenance.py"),
            "launcher_sha256": sha256_file(Path(__file__).resolve()),
            "protocol_sha256": sha256_file(
                REPO_ROOT / "configs/evaluator_v2/feasibility_v1.yaml"
            ),
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "yfinance": importlib.metadata.version("yfinance"),
            "pandas": importlib.metadata.version("pandas"),
            "numpy": importlib.metadata.version("numpy"),
            "pyarrow": importlib.metadata.version("pyarrow"),
        },
        "expected_years": list(EXPECTED_YEARS),
        "audits": audits,
        "policy": {
            "time_split_only": True,
            "sealed_2020_not_used_for_training_or_selection": True,
            "manifest_contains_prices_or_returns": False,
            "raw_bytes_committed_or_publicly_redistributed": False,
        },
    }
    payload["canonical_payload_sha256"] = _canonical_sha(payload)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(manifest_path)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    payload = acquire(args.out_dir.resolve(), args.manifest.resolve())
    print(json.dumps({
        "manifest": str(args.manifest.resolve()),
        "canonical_payload_sha256": payload["canonical_payload_sha256"],
        "symbols": list(payload["audits"]),
        "files": sum(len(audit["files"]) for audit in payload["audits"].values()),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
