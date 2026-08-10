"""Acquire and audit the frozen free-data input for EcoMD v1 M1."""

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
SYMBOL = "^GSPC"
START = "2015-01-01"
END = "2025-01-01"
INTERVAL = "1d"
EXPECTED_YEARS = tuple(range(2015, 2025))
SPLITS = (
    TemporalSplit("train", "calibration_and_parameter_fit", 2015, 2018),
    TemporalSplit("validation", "report_only_model_selection_guard", 2019, 2019),
    TemporalSplit("sealed_crash_test", "final_crash_test_no_selection", 2020, 2020, sealed=True),
    TemporalSplit("temporal_test", "post_crash_temporal_test", 2021, 2024),
)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _manifest_sha(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def acquire(out_dir: Path, manifest_path: Path, *, allow_dirty: bool = False) -> dict[str, Any]:
    state = repository_state(REPO_ROOT)
    if not state["clean"] and not allow_dirty:
        raise RuntimeError("formal M1 acquisition requires a clean worktree")
    target_dir = out_dir / f"interval={INTERVAL}" / f"symbol={SYMBOL}"
    if target_dir.exists():
        raise FileExistsError(f"refusing to mix or overwrite an existing acquisition: {target_dir}")

    started = _utc_now()
    paths = ingest_one(
        SYMBOL,
        IngestConfig(
            symbols=(SYMBOL,),
            start=START,
            end=END,
            interval=INTERVAL,
            out_dir=out_dir,
            retries=3,
            sleep_between=0.5,
        ),
    )
    finished = _utc_now()
    if len(paths) != len(EXPECTED_YEARS):
        raise RuntimeError(f"expected {len(EXPECTED_YEARS)} shards, wrote {len(paths)}")

    audit = audit_daily_shards(
        out_dir,
        symbol=SYMBOL,
        interval=INTERVAL,
        expected_years=EXPECTED_YEARS,
        splits=SPLITS,
    )
    payload: dict[str, Any] = {
        "schema_version": 1,
        "dataset_id": "ecomd_v1_m1_spx_yahoo_daily_2015_2024",
        "status": "acquired_and_audited_no_values_disclosed",
        "source": {
            "provider": "Yahoo Finance",
            "access_library": "yfinance",
            "provider_landing_page": "https://finance.yahoo.com/quote/%5EGSPC/",
            "redistribution": "excluded_from_public_artifacts",
            "redistribution_reason": "third-party terms; repository MIT license covers code only",
        },
        "request": {
            "symbol": SYMBOL,
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
                "conda run -n ecophys python scripts/acquire_m1_spx_data.py "
                "--out-dir <internal-dir> --manifest <manifest.json>"
            ),
        },
        "repository": state,
        "code": {
            "ingest_sha256": sha256_file(REPO_ROOT / "ecomd/data/yfinance_ingest.py"),
            "audit_sha256": sha256_file(REPO_ROOT / "ecomd/data/yfinance_provenance.py"),
            "launcher_sha256": sha256_file(Path(__file__).resolve()),
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "yfinance": importlib.metadata.version("yfinance"),
            "pandas": importlib.metadata.version("pandas"),
            "numpy": importlib.metadata.version("numpy"),
            "pyarrow": importlib.metadata.version("pyarrow"),
        },
        "audit": audit,
        "policy": {
            "time_split_only": True,
            "sealed_2020_not_used_for_training_or_selection": True,
            "manifest_contains_prices_or_returns": False,
            "raw_bytes_committed_or_publicly_redistributed": False,
        },
    }
    payload["canonical_payload_sha256"] = _manifest_sha(payload)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(manifest_path)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--allow-dirty", action="store_true", help="debug only; never formal")
    args = parser.parse_args()
    payload = acquire(args.out_dir, args.manifest, allow_dirty=args.allow_dirty)
    print(
        json.dumps(
            {
                "manifest": str(args.manifest),
                "canonical_payload_sha256": payload["canonical_payload_sha256"],
                "files": len(payload["audit"]["files"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
