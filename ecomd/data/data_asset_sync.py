"""Dataset shard offload utility for Cloudflare R2 + Supabase.

Use this for durable, searchable copies of open/reference data shards. The
binary data lives in R2; Supabase stores enough metadata for H20 to discover and
verify what to pull before eval/training.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

from ecomd.data.checkpoint_sync import SupabaseConfig, apply_supabase_migration, load_env_files, sha256_file
from ecomd.data.r2_sync import R2Config, _client, _find_project_root, _guess_mime

log = logging.getLogger("data_asset_sync")

_DEFAULT_TABLE = "data_assets"
_YFINANCE_SYMBOL_TO_DATASET = {
    "^GSPC": "spx",
    "SPY": "spy",
    "QQQ": "qqq",
    "IWM": "iwm",
    "^GDAXI": "dax",
    "^STOXX50E": "stoxx50",
    "^HSI": "hsi",
    "^N225": "nikkei",
    "GLD": "gold",
    "EURUSD=X": "eurusd",
    "^NDX": "ndx",
}


@dataclass(frozen=True)
class DataAssetRecord:
    local_path: str
    r2_bucket: str
    r2_key: str
    size_bytes: int
    sha256: str
    source: str
    dataset: str
    symbol: str | None
    market: str | None
    interval: str | None
    year: int | None
    month: int | None
    content_type: str | None
    uploaded_at: str | None = None
    upload_status: str = "pending"
    error_message: str | None = None
    metadata: dict[str, Any] | None = None

    def supabase_payload(self) -> dict[str, Any]:
        return asdict(self)


def discover_assets(root: Path, pattern: str = "*.parquet") -> list[Path]:
    root = root.resolve()
    if root.is_file():
        return [root]
    if not root.is_dir():
        raise FileNotFoundError(root)
    return sorted(p for p in root.rglob(pattern) if p.is_file())


def make_r2_key(path: Path, repo_root: Path, prefix: str = "") -> str:
    rel = path.resolve().relative_to((repo_root / "data").resolve()).as_posix()
    clean_prefix = prefix.strip("/")
    return f"{clean_prefix}/{rel}" if clean_prefix else rel


def build_record(path: Path, repo_root: Path, r2_bucket: str, r2_key: str) -> DataAssetRecord:
    rel = path.resolve().relative_to(repo_root.resolve()).as_posix()
    parsed = parse_asset_path(path, repo_root)
    return DataAssetRecord(
        local_path=rel,
        r2_bucket=r2_bucket,
        r2_key=r2_key,
        size_bytes=path.stat().st_size,
        sha256=sha256_file(path),
        content_type=_guess_mime(path),
        **parsed,
    )


def parse_asset_path(path: Path, repo_root: Path) -> dict[str, Any]:
    rel = path.resolve().relative_to(repo_root.resolve())
    parts = rel.parts
    if len(parts) >= 6 and parts[:3] == ("data", "raw", "yfinance"):
        interval = _part_value(parts[3], "interval")
        symbol = _part_value(parts[4], "symbol")
        return {
            "source": "yfinance",
            "dataset": _YFINANCE_SYMBOL_TO_DATASET.get(symbol or "", symbol or "unknown"),
            "symbol": symbol,
            "market": None,
            "interval": interval,
            "year": _int_part(path.stem, "year"),
            "month": None,
            "metadata": {"path_schema": "data/raw/yfinance/interval={interval}/symbol={symbol}/year={year}.parquet"},
        }
    if len(parts) >= 8 and parts[:3] == ("data", "raw", "binance"):
        return {
            "source": "binance",
            "dataset": (_part_value(parts[5], "symbol") or "unknown").lower(),
            "symbol": _part_value(parts[5], "symbol"),
            "market": _part_value(parts[3], "market"),
            "interval": _part_value(parts[4], "interval"),
            "year": _int_part(parts[6], "year"),
            "month": _int_part(path.stem, "month"),
            "metadata": {"path_schema": "data/raw/binance/market={market}/interval={interval}/symbol={symbol}/year={year}/month={month}.parquet"},
        }
    return {
        "source": "unknown",
        "dataset": "unknown",
        "symbol": None,
        "market": None,
        "interval": None,
        "year": None,
        "month": None,
        "metadata": {"relative_path": rel.as_posix()},
    }


def upload_asset(path: Path, record: DataAssetRecord, dry_run: bool = False) -> bool:
    cfg = R2Config.from_env()
    if record.r2_bucket != cfg.bucket:
        raise RuntimeError(f"record bucket {record.r2_bucket!r} does not match configured R2 bucket {cfg.bucket!r}")
    if dry_run:
        log.info("DRY put %s -> r2://%s/%s", path, cfg.bucket, record.r2_key)
        return True
    client = _client(cfg)
    if _remote_matches(client, cfg.bucket, record.r2_key, record.size_bytes, record.sha256):
        log.info("skip r2://%s/%s (already uploaded)", cfg.bucket, record.r2_key)
        return False
    client.upload_file(
        str(path),
        cfg.bucket,
        record.r2_key,
        ExtraArgs={
            "ContentType": record.content_type or _guess_mime(path),
            "Metadata": {"sha256": record.sha256, "local_path": record.local_path},
        },
    )
    log.info("put r2://%s/%s", cfg.bucket, record.r2_key)
    return True


def upsert_supabase(records: list[DataAssetRecord], cfg: SupabaseConfig, dry_run: bool = False) -> None:
    if not records:
        return
    payload = [r.supabase_payload() for r in records]
    if dry_run:
        log.info("DRY upsert %d Supabase rows into %s", len(records), cfg.table)
        return
    resp = requests.post(
        f"{cfg.url}/rest/v1/{cfg.table}",
        params={"on_conflict": "r2_bucket,r2_key"},
        headers={
            "apikey": cfg.service_role_key,
            "Authorization": f"Bearer {cfg.service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        },
        data=json.dumps(payload),
        timeout=60,
    )
    if resp.status_code >= 300:
        raise RuntimeError(f"Supabase upsert failed: HTTP {resp.status_code}: {resp.text[:500]}")


def _remote_matches(client: Any, bucket: str, key: str, size_bytes: int, sha256: str) -> bool:
    try:
        resp = client.head_object(Bucket=bucket, Key=key)
    except Exception:  # noqa: BLE001
        return False
    if int(resp.get("ContentLength", -1)) != size_bytes:
        return False
    meta = {str(k).lower(): v for k, v in resp.get("Metadata", {}).items()}
    remote_sha = meta.get("sha256")
    return remote_sha in (None, sha256)


def _part_value(part: str, key: str) -> str | None:
    prefix = f"{key}="
    return part[len(prefix):] if part.startswith(prefix) else None


def _int_part(part: str, key: str) -> int | None:
    value = _part_value(part, key)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cmd", choices=("scan", "sync", "migrate"))
    parser.add_argument("path", nargs="?", default="data/raw", help="file or directory to scan/sync")
    parser.add_argument("--pattern", default="*.parquet")
    parser.add_argument("--prefix", default="")
    parser.add_argument("--table", default=os.environ.get("SUPABASE_DATA_ASSETS_TABLE", _DEFAULT_TABLE))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    repo_root = _find_project_root()
    load_env_files()
    if args.cmd == "migrate":
        apply_supabase_migration(repo_root / "supabase" / "migrations" / "002_create_data_assets.sql")
        return 0

    r2_cfg = R2Config.from_env()
    paths = discover_assets((repo_root / args.path).resolve() if not Path(args.path).is_absolute() else Path(args.path), args.pattern)
    records = [build_record(p, repo_root, r2_cfg.bucket, make_r2_key(p, repo_root, args.prefix)) for p in paths]
    if args.cmd == "scan":
        for record in records:
            print(json.dumps(record.supabase_payload(), sort_keys=True))
        log.info("found %d assets", len(records))
        return 0

    supabase_cfg = SupabaseConfig.from_env(allow_missing=args.dry_run)
    supabase_cfg = SupabaseConfig(supabase_cfg.url, supabase_cfg.service_role_key, args.table)
    now = datetime.now(UTC).isoformat()
    synced: list[DataAssetRecord] = []
    for path, record in zip(paths, records, strict=True):
        try:
            upload_asset(path, record, dry_run=args.dry_run)
            synced.append(DataAssetRecord(**{**record.supabase_payload(), "uploaded_at": now, "upload_status": "uploaded"}))
        except Exception as exc:  # noqa: BLE001
            log.exception("failed to upload %s", path)
            synced.append(DataAssetRecord(**{**record.supabase_payload(), "upload_status": "failed", "error_message": str(exc)}))
    upsert_supabase(synced, supabase_cfg, dry_run=args.dry_run)
    log.info("synced %d assets", len(synced))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
