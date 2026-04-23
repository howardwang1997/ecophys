"""Cloudflare R2 upload/download utility.

R2 is S3-API compatible; this module wraps boto3 with sensible defaults for our
bulk-transfer use case (multipart, checksums, batch directory sync).

Credentials are loaded from `<project-root>/.env.r2` (gitignored). Copy the
committed `.env.r2.example` to `.env.r2` and fill in values. Required keys:
    R2_ACCOUNT_ID
    R2_BUCKET              (default: ecophys)
    R2_ACCESS_KEY_ID
    R2_SECRET_ACCESS_KEY
    R2_ENDPOINT_URL        (default: https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com)

Project root is located by walking up from this file until a directory
containing `pyproject.toml` is found, so the tool works from any CWD.

Usage:
    # Mac → R2
    python -m ecomd.data.r2_sync upload ./data/processed/sp500_minute/ processed/sp500_minute/
    # R2 → H20
    python -m ecomd.data.r2_sync download processed/sp500_minute/ /AI4S/Users/howardwang/ecophys/processed/sp500_minute/
    # List
    python -m ecomd.data.r2_sync ls processed/
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

log = logging.getLogger("r2_sync")

_DEFAULT_BUCKET = "ecophys"
_ENV_FILE_NAMES = (".env.r2", ".env")  # searched in project root, in order


@dataclass(frozen=True)
class R2Config:
    account_id: str
    bucket: str
    access_key_id: str
    secret_access_key: str
    endpoint_url: str

    @classmethod
    def from_env(cls) -> "R2Config":
        env_path = _maybe_load_dotenv()
        missing = [k for k in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY") if not os.environ.get(k)]
        if missing:
            hint = (
                f"loaded {env_path}; fill in the missing keys"
                if env_path
                else f"no .env.r2 found under {_find_project_root()}; copy .env.r2.example to .env.r2 and fill it in"
            )
            raise RuntimeError(f"missing R2 env vars: {missing}. {hint}")
        account_id = os.environ["R2_ACCOUNT_ID"]
        return cls(
            account_id=account_id,
            bucket=os.environ.get("R2_BUCKET", _DEFAULT_BUCKET),
            access_key_id=os.environ["R2_ACCESS_KEY_ID"],
            secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
            endpoint_url=os.environ.get("R2_ENDPOINT_URL", f"https://{account_id}.r2.cloudflarestorage.com"),
        )


def _find_project_root() -> Path:
    """Walk up from this file until we find a dir containing pyproject.toml."""
    for p in (Path(__file__).resolve(), *Path(__file__).resolve().parents):
        if (p / "pyproject.toml").is_file():
            return p
    # Fall back to CWD if we can't find pyproject.toml (e.g. installed-only scenario)
    return Path.cwd()


def _maybe_load_dotenv() -> Path | None:
    """Load the first existing env file from the project root. Returns its path, or None."""
    root = _find_project_root()
    for name in _ENV_FILE_NAMES:
        p = root / name
        if p.is_file():
            _load_env_file(p)
            return p
    return None


def _load_env_file(path: Path) -> None:
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if not v:
            continue  # skip blank template entries so real env vars aren't overridden by ""
        os.environ.setdefault(k, v)


def _client(cfg: R2Config):
    import boto3  # lazy
    from botocore.config import Config as BotoConfig

    return boto3.client(
        "s3",
        endpoint_url=cfg.endpoint_url,
        aws_access_key_id=cfg.access_key_id,
        aws_secret_access_key=cfg.secret_access_key,
        region_name="auto",
        config=BotoConfig(
            signature_version="s3v4",
            retries={"max_attempts": 5, "mode": "standard"},
            s3={"addressing_style": "virtual"},
            max_pool_connections=32,
        ),
    )


# ─── Operations ────────────────────────────────────────────────────────────


def upload(local: Path, remote_prefix: str, cfg: R2Config | None = None, dry_run: bool = False) -> int:
    cfg = cfg or R2Config.from_env()
    client = _client(cfg)
    local = local.resolve()
    if local.is_file():
        pairs = [(local, _normalise_prefix(remote_prefix).rstrip("/") or local.name)]
    elif local.is_dir():
        pairs = list(_walk_for_upload(local, _normalise_prefix(remote_prefix)))
    else:
        raise FileNotFoundError(local)
    log.info("uploading %d objects to r2://%s/%s", len(pairs), cfg.bucket, _normalise_prefix(remote_prefix))
    for src, key in pairs:
        if dry_run:
            log.info("DRY  %s → r2://%s/%s", src, cfg.bucket, key)
            continue
        etag = _remote_etag(client, cfg.bucket, key)
        if etag and _matches_local(src, etag):
            log.info("skip %s (already in R2 with matching size/md5)", key)
            continue
        client.upload_file(str(src), cfg.bucket, key, ExtraArgs={"ContentType": _guess_mime(src)})
        log.info("put  r2://%s/%s (%s)", cfg.bucket, key, _human_size(src.stat().st_size))
    return len(pairs)


def download(remote_prefix: str, local: Path, cfg: R2Config | None = None, dry_run: bool = False) -> int:
    cfg = cfg or R2Config.from_env()
    client = _client(cfg)
    prefix = _normalise_prefix(remote_prefix)
    local = local.resolve()
    keys = list(_list_keys(client, cfg.bucket, prefix))
    if not keys:
        raise FileNotFoundError(f"no objects under r2://{cfg.bucket}/{prefix}")
    log.info("downloading %d objects from r2://%s/%s to %s", len(keys), cfg.bucket, prefix, local)
    local.mkdir(parents=True, exist_ok=True)
    for key in keys:
        rel = key[len(prefix):].lstrip("/")
        dst = local / rel if rel else local / Path(key).name
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dry_run:
            log.info("DRY  r2://%s/%s → %s", cfg.bucket, key, dst)
            continue
        etag = _remote_etag(client, cfg.bucket, key)
        if dst.is_file() and etag and _matches_local(dst, etag):
            log.info("skip %s (local matches)", rel)
            continue
        client.download_file(cfg.bucket, key, str(dst))
        log.info("got  %s", dst)
    return len(keys)


def list_keys(remote_prefix: str = "", cfg: R2Config | None = None) -> list[str]:
    cfg = cfg or R2Config.from_env()
    client = _client(cfg)
    return list(_list_keys(client, cfg.bucket, _normalise_prefix(remote_prefix)))


def delete(remote_prefix: str, cfg: R2Config | None = None, confirm: bool = False) -> int:
    """Delete all objects under prefix. Requires confirm=True to actually do it."""
    cfg = cfg or R2Config.from_env()
    client = _client(cfg)
    keys = list(_list_keys(client, cfg.bucket, _normalise_prefix(remote_prefix)))
    if not confirm:
        log.warning("would delete %d objects (pass --confirm to actually delete)", len(keys))
        return 0
    for batch in _chunks(keys, 1000):
        client.delete_objects(
            Bucket=cfg.bucket,
            Delete={"Objects": [{"Key": k} for k in batch], "Quiet": True},
        )
    log.info("deleted %d objects", len(keys))
    return len(keys)


# ─── Helpers ───────────────────────────────────────────────────────────────


def _walk_for_upload(root: Path, remote_prefix: str) -> Iterable[tuple[Path, str]]:
    remote_prefix = remote_prefix.rstrip("/")
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if p.name == ".DS_Store":
            continue
        rel = p.relative_to(root).as_posix()
        yield p, f"{remote_prefix}/{rel}" if remote_prefix else rel


def _list_keys(client, bucket: str, prefix: str) -> Iterable[str]:
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for item in page.get("Contents", []):
            yield item["Key"]


def _remote_etag(client, bucket: str, key: str) -> str | None:
    try:
        resp = client.head_object(Bucket=bucket, Key=key)
        return resp.get("ETag", "").strip('"')
    except Exception:  # noqa: BLE001
        return None


def _matches_local(path: Path, etag: str) -> bool:
    """Single-part uploads have ETag == hex md5. Multipart have "{md5}-{N}" which we can't match cheaply → skip."""
    if "-" in etag:
        return False
    try:
        h = hashlib.md5()  # noqa: S324 — S3 ETag uses md5 for single-part, not for security
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest() == etag
    except OSError:
        return False


def _normalise_prefix(prefix: str) -> str:
    prefix = prefix.lstrip("/")
    if prefix and not prefix.endswith("/") and "." not in Path(prefix).name:
        prefix = prefix + "/"
    return prefix


def _guess_mime(p: Path) -> str:
    ext = p.suffix.lower()
    return {
        ".parquet": "application/vnd.apache.parquet",
        ".json": "application/json",
        ".csv": "text/csv",
        ".md": "text/markdown",
        ".txt": "text/plain",
        ".zst": "application/zstd",
        ".gz": "application/gzip",
    }.get(ext, "application/octet-stream")


def _human_size(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024  # type: ignore[assignment]
    return f"{n:.1f}PB"


def _chunks(seq: list, size: int) -> Iterable[list]:
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


# ─── CLI ───────────────────────────────────────────────────────────────────


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--log-level", default="INFO")
    sub = p.add_subparsers(dest="cmd", required=True)

    pu = sub.add_parser("upload", help="local → R2")
    pu.add_argument("local", type=Path)
    pu.add_argument("remote_prefix", type=str)
    pu.add_argument("--dry-run", action="store_true")

    pd = sub.add_parser("download", help="R2 → local")
    pd.add_argument("remote_prefix", type=str)
    pd.add_argument("local", type=Path)
    pd.add_argument("--dry-run", action="store_true")

    pl = sub.add_parser("ls", help="list keys under prefix")
    pl.add_argument("remote_prefix", type=str, nargs="?", default="")

    pdel = sub.add_parser("delete", help="delete all keys under prefix")
    pdel.add_argument("remote_prefix", type=str)
    pdel.add_argument("--confirm", action="store_true")

    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    if args.cmd == "upload":
        upload(args.local, args.remote_prefix, dry_run=args.dry_run)
    elif args.cmd == "download":
        download(args.remote_prefix, args.local, dry_run=args.dry_run)
    elif args.cmd == "ls":
        for key in list_keys(args.remote_prefix):
            print(key)
    elif args.cmd == "delete":
        delete(args.remote_prefix, confirm=args.confirm)
    else:
        raise AssertionError(args.cmd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
