"""Checkpoint offload utility for Cloudflare R2 + Supabase.

The binary checkpoint files live in R2. Supabase stores the catalog metadata
needed to find, verify, and clean up local copies safely.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qs, unquote

import requests

from ecomd.data.r2_sync import R2Config, _client, _find_project_root, _guess_mime, _load_env_file

log = logging.getLogger("checkpoint_sync")

_DEFAULT_TABLE = "checkpoints"
_ENV_FILE_NAMES = (".env.r2", ".env.supabase", ".env")


@dataclass(frozen=True)
class SupabaseConfig:
    url: str
    service_role_key: str
    table: str = _DEFAULT_TABLE

    @classmethod
    def from_env(cls, allow_missing: bool = False) -> "SupabaseConfig":
        load_env_files()
        missing = [k for k in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY") if not os.environ.get(k)]
        if missing:
            if allow_missing:
                return cls(url="https://dry-run.supabase.local", service_role_key="dry-run")
            raise RuntimeError(
                f"missing Supabase env vars: {missing}. Copy .env.supabase.example to .env.supabase and fill it in"
            )
        return cls(
            url=os.environ["SUPABASE_URL"].rstrip("/"),
            service_role_key=os.environ["SUPABASE_SERVICE_ROLE_KEY"],
            table=os.environ.get("SUPABASE_CHECKPOINT_TABLE", _DEFAULT_TABLE),
        )


@dataclass(frozen=True)
class CheckpointRecord:
    local_path: str
    r2_bucket: str
    r2_key: str
    size_bytes: int
    sha256: str
    experiment_dir: str
    result_dir: str
    checkpoint_name: str
    seed: int | None
    target_dataset: str | None
    target_period: str | None
    n_agents: int | None
    config: dict[str, Any] | None
    training_summary: dict[str, Any] | None
    uploaded_at: str | None = None
    upload_status: str = "pending"
    error_message: str | None = None

    def supabase_payload(self) -> dict[str, Any]:
        return asdict(self)


def load_env_files() -> None:
    root = _find_project_root()
    for name in _ENV_FILE_NAMES:
        path = root / name
        if path.is_file():
            _load_env_file_override(path)


def _load_env_file_override(path: Path) -> None:
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if v:
            os.environ[k] = v


def discover_checkpoints(root: Path, pattern: str = "checkpoint*.pt") -> list[Path]:
    root = root.resolve()
    if root.is_file():
        return [root]
    if not root.is_dir():
        raise FileNotFoundError(root)
    return sorted(p for p in root.rglob(pattern) if p.is_file())


def make_r2_key(path: Path, repo_root: Path, prefix: str = "checkpoints/") -> str:
    rel = path.resolve().relative_to(repo_root.resolve()).as_posix()
    clean_prefix = prefix.strip("/")
    return f"{clean_prefix}/{rel}" if clean_prefix else rel


def build_record(path: Path, repo_root: Path, r2_bucket: str, r2_key: str) -> CheckpointRecord:
    rel = path.resolve().relative_to(repo_root.resolve()).as_posix()
    stat = path.stat()
    result_dir = path.parent.relative_to(repo_root).as_posix()
    experiment_dir = _experiment_dir(path, repo_root)
    config = _load_config_for_result(path.parent, repo_root)
    training = config.get("training", {}) if isinstance(config, dict) else {}
    simulator = config.get("simulator", {}) if isinstance(config, dict) else {}
    return CheckpointRecord(
        local_path=rel,
        r2_bucket=r2_bucket,
        r2_key=r2_key,
        size_bytes=stat.st_size,
        sha256=sha256_file(path),
        experiment_dir=experiment_dir,
        result_dir=result_dir,
        checkpoint_name=path.name,
        seed=_optional_int(training.get("seed")) if isinstance(training, dict) else None,
        target_dataset=_optional_str(training.get("target_dataset")) if isinstance(training, dict) else None,
        target_period=_optional_str(training.get("target_period")) if isinstance(training, dict) else None,
        n_agents=_optional_int(simulator.get("n_agents")) if isinstance(simulator, dict) else None,
        config=config,
        training_summary=_load_training_summary(path.parent),
    )


def sha256_file(path: Path, chunk_size: int = 8 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def upload_checkpoint(path: Path, record: CheckpointRecord, dry_run: bool = False) -> bool:
    cfg = R2Config.from_env()
    if record.r2_bucket != cfg.bucket:
        raise RuntimeError(f"record bucket {record.r2_bucket!r} does not match configured R2 bucket {cfg.bucket!r}")
    if dry_run:
        log.info("DRY put %s -> r2://%s/%s", path, cfg.bucket, record.r2_key)
        return True
    client = _client(cfg)
    if remote_matches(client, cfg.bucket, record.r2_key, record.size_bytes, record.sha256):
        log.info("skip r2://%s/%s (already uploaded)", cfg.bucket, record.r2_key)
        return False
    client.upload_file(
        str(path),
        cfg.bucket,
        record.r2_key,
        ExtraArgs={
            "ContentType": _guess_mime(path),
            "Metadata": {
                "sha256": record.sha256,
                "local_path": record.local_path,
            },
        },
    )
    log.info("put r2://%s/%s", cfg.bucket, record.r2_key)
    return True


def remote_matches(client: Any, bucket: str, key: str, size_bytes: int, sha256: str) -> bool:
    try:
        resp = client.head_object(Bucket=bucket, Key=key)
    except Exception:  # noqa: BLE001
        return False
    if int(resp.get("ContentLength", -1)) != size_bytes:
        return False
    meta = {str(k).lower(): v for k, v in resp.get("Metadata", {}).items()}
    remote_sha = meta.get("sha256")
    return remote_sha in (None, sha256)


def upsert_supabase(records: list[CheckpointRecord], cfg: SupabaseConfig, dry_run: bool = False) -> None:
    if not records:
        return
    payload = [r.supabase_payload() for r in records]
    if dry_run:
        log.info("DRY upsert %d Supabase rows into %s", len(records), cfg.table)
        return
    url = f"{cfg.url}/rest/v1/{cfg.table}"
    resp = requests.post(
        url,
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


def apply_supabase_migration(path: Path) -> None:
    load_env_files()
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("missing DATABASE_URL in .env.supabase; service role keys cannot create tables")
    if not path.is_file():
        raise FileNotFoundError(path)
    sql = path.read_text()
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError("missing psycopg; install with `pip install -e '.[supabase]'`") from exc
    try:
        with psycopg.connect(**_database_url_kwargs(database_url, supabase_url=os.environ.get("SUPABASE_URL"))) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
    except psycopg.OperationalError as exc:
        msg = str(exc)
        if "password authentication failed" in msg:
            hint = (
                "Could not authenticate to Supabase Postgres. Check that DATABASE_URL uses the database password "
                "from Project Settings > Database, not the service role key, and that pooler usernames include "
                "the project ref as postgres.<project-ref>."
            )
        else:
            hint = (
                "Could not connect to Supabase Postgres. If DATABASE_URL uses "
                "db.<project-ref>.supabase.co:5432, replace it with the Supabase "
                "IPv4-compatible pooler connection string from Project Settings > Database."
            )
        raise RuntimeError(f"{hint}\nOriginal error: {exc}") from exc


def _database_url_kwargs(database_url: str, supabase_url: str | None = None) -> dict[str, Any]:
    """Parse Supabase Postgres URLs while tolerating unescaped password chars."""
    if "://" not in database_url:
        raise ValueError("DATABASE_URL must start with postgresql:// or postgres://")
    _, rest = database_url.split("://", 1)
    if "@" not in rest:
        raise ValueError("DATABASE_URL must include user/password and host")
    userpass, host_part = rest.rsplit("@", 1)
    if ":" not in userpass:
        raise ValueError("DATABASE_URL must include a password")
    user, password = userpass.split(":", 1)

    host_db, _, query = host_part.partition("?")
    host_port, _, dbname = host_db.partition("/")
    host = host_port
    port = None
    if host_port.startswith("[") and "]" in host_port:
        host, _, port_part = host_port[1:].partition("]")
        port_part = port_part.removeprefix(":")
        port = int(port_part) if port_part else None
    elif ":" in host_port:
        host, port_part = host_port.rsplit(":", 1)
        port = int(port_part)

    parsed_user = unquote(user)
    if "pooler.supabase.com" in host and parsed_user == "postgres":
        project_ref = _project_ref_from_supabase_url(supabase_url)
        if project_ref:
            parsed_user = f"postgres.{project_ref}"

    params: dict[str, Any] = {
        "user": parsed_user,
        "password": unquote(password),
        "host": host,
        "dbname": dbname or "postgres",
        "sslmode": "require",
    }
    if port is not None:
        params["port"] = port
    query_params = parse_qs(query)
    if "sslmode" in query_params and query_params["sslmode"]:
        params["sslmode"] = query_params["sslmode"][0]
    return params


def _project_ref_from_supabase_url(supabase_url: str | None) -> str | None:
    if not supabase_url:
        return None
    host = supabase_url.split("://", 1)[-1].split("/", 1)[0]
    if host.endswith(".supabase.co"):
        return host.removesuffix(".supabase.co")
    return None


def cleanup_verified(records: list[CheckpointRecord], dry_run: bool = False) -> int:
    cfg = R2Config.from_env()
    if dry_run:
        count = 0
        for record in records:
            path = _find_project_root() / record.local_path
            if path.is_file():
                log.info("DRY verify r2://%s/%s then delete %s", cfg.bucket, record.r2_key, record.local_path)
                count += 1
        return count
    client = _client(cfg)
    deleted = 0
    for record in records:
        path = _find_project_root() / record.local_path
        if not path.is_file():
            continue
        if not remote_matches(client, cfg.bucket, record.r2_key, record.size_bytes, record.sha256):
            log.warning("keep %s (R2 object missing or mismatched)", record.local_path)
            continue
        if dry_run:
            log.info("DRY delete %s", record.local_path)
            deleted += 1
            continue
        path.unlink()
        log.info("deleted %s", record.local_path)
        deleted += 1
    return deleted


def git_rm_cached(records: list[CheckpointRecord], dry_run: bool = False) -> int:
    """Remove tracked checkpoint files from the Git index while keeping worktree files."""
    import subprocess

    paths = [r.local_path for r in records if _is_tracked(r.local_path)]
    if not paths:
        return 0
    if dry_run:
        for path in paths:
            log.info("DRY git rm --cached -- %s", path)
        return len(paths)
    repo_root = _find_project_root()
    for batch in _chunks(paths, 200):
        subprocess.run(["git", "rm", "--cached", "--quiet", "--", *batch], cwd=repo_root, check=True)
    return len(paths)


def _is_tracked(path: str) -> bool:
    import subprocess

    repo_root = _find_project_root()
    proc = subprocess.run(["git", "ls-files", "--error-unmatch", "--", path], cwd=repo_root, capture_output=True)
    return proc.returncode == 0


def _experiment_dir(path: Path, repo_root: Path) -> str:
    rel_parts = path.resolve().relative_to(repo_root.resolve()).parts
    if len(rel_parts) >= 2 and rel_parts[0] == "experiments":
        return "/".join(rel_parts[:2])
    return str(path.parent.relative_to(repo_root))


def _load_config_for_result(result_dir: Path, repo_root: Path) -> dict[str, Any] | None:
    exp_dir = repo_root / _experiment_dir(result_dir / "checkpoint.pt", repo_root)
    candidates = _config_candidates(result_dir, exp_dir)
    for candidate in candidates:
        data = _read_yaml(candidate)
        if data is not None:
            return data
    return None


def _config_candidates(result_dir: Path, exp_dir: Path) -> Iterable[Path]:
    result_name = result_dir.name
    if result_name.startswith("results_"):
        suffix = result_name.removeprefix("results_")
        yield exp_dir / f"config_{suffix}.yaml"
    yield exp_dir / "config.yaml"
    yield from sorted(exp_dir.glob("config*.yaml"))


def _read_yaml(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        import yaml
    except ImportError:
        return {"_config_path": path.name}
    data = yaml.safe_load(path.read_text()) or {}
    if isinstance(data, dict):
        return data
    return {"_config_path": path.name, "_raw_type": type(data).__name__}


def _load_training_summary(result_dir: Path) -> dict[str, Any] | None:
    path = result_dir / "training_log.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return {"error": str(exc)}
    if not isinstance(data, dict):
        return {"raw_type": type(data).__name__}
    history = data.get("history")
    summary: dict[str, Any] = {
        "training_log": path.name,
        "targets": data.get("targets"),
    }
    if isinstance(history, list):
        summary["history_len"] = len(history)
        if history:
            summary["first"] = history[0]
            summary["last"] = history[-1]
    return summary


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value: Any) -> str | None:
    return str(value) if value is not None else None


def _chunks(seq: list[str], size: int) -> Iterable[list[str]]:
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def _records_for_args(args: argparse.Namespace) -> list[CheckpointRecord]:
    repo_root = _find_project_root()
    r2_cfg = R2Config.from_env()
    paths = discover_checkpoints(repo_root / args.root, args.pattern)
    if args.limit is not None:
        paths = paths[: args.limit]
    return [
        build_record(path, repo_root=repo_root, r2_bucket=r2_cfg.bucket, r2_key=make_r2_key(path, repo_root, args.prefix))
        for path in paths
    ]


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--log-level", default="INFO")
    p.add_argument("--root", default="experiments")
    p.add_argument("--pattern", default="checkpoint*.pt")
    p.add_argument("--prefix", default="checkpoints/")
    p.add_argument("--limit", type=int)
    sub = p.add_subparsers(dest="cmd", required=True)

    scan = sub.add_parser("scan", help="scan local checkpoints")
    scan.add_argument("--json", action="store_true", help="emit JSON records")

    sync = sub.add_parser("sync", help="upload checkpoints and upsert Supabase rows")
    sync.add_argument("--dry-run", action="store_true")
    sync.add_argument("--delete-local", action="store_true", help="delete verified local checkpoints after sync")
    sync.add_argument("--git-rm-cached", action="store_true", help="remove tracked checkpoints from the Git index")

    cleanup = sub.add_parser("cleanup", help="delete local checkpoints that are verified in R2")
    cleanup.add_argument("--dry-run", action="store_true")

    git_rm = sub.add_parser("git-rm-cached", help="remove tracked checkpoints from Git index")
    git_rm.add_argument("--dry-run", action="store_true")

    migrate = sub.add_parser("migrate", help="apply the Supabase checkpoints table migration")
    migrate.add_argument(
        "--sql",
        type=Path,
        default=_find_project_root() / "supabase" / "migrations" / "001_create_checkpoints.sql",
    )

    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    if args.cmd == "migrate":
        apply_supabase_migration(args.sql)
        print(f"applied migration: {args.sql}")
        return 0

    records = _records_for_args(args)

    if args.cmd == "scan":
        if args.json:
            print(json.dumps([r.supabase_payload() for r in records], indent=2, sort_keys=True))
        else:
            total = sum(r.size_bytes for r in records)
            print(f"found {len(records)} checkpoints ({total / (1024 ** 3):.2f} GiB)")
            for record in records[:10]:
                print(f"{record.local_path} -> r2://{record.r2_bucket}/{record.r2_key}")
        return 0

    if args.cmd == "sync":
        supabase_cfg = SupabaseConfig.from_env(allow_missing=args.dry_run)
        now = datetime.now(UTC).isoformat()
        synced: list[CheckpointRecord] = []
        failed = 0
        for record in records:
            path = _find_project_root() / record.local_path
            try:
                upload_checkpoint(path, record, dry_run=args.dry_run)
                synced.append(record.__class__(**{**record.supabase_payload(), "uploaded_at": now, "upload_status": "uploaded"}))
            except Exception as exc:  # noqa: BLE001
                failed += 1
                log.exception("failed to upload %s", record.local_path)
                synced.append(record.__class__(**{**record.supabase_payload(), "upload_status": "failed", "error_message": str(exc)}))
        upsert_supabase(synced, supabase_cfg, dry_run=args.dry_run)
        if args.git_rm_cached:
            log.info("removed %d checkpoint paths from Git index", git_rm_cached(synced, dry_run=args.dry_run))
        if args.delete_local:
            log.info("deleted %d verified local checkpoints", cleanup_verified(synced, dry_run=args.dry_run))
        return 1 if failed else 0

    if args.cmd == "cleanup":
        deleted = cleanup_verified(records, dry_run=args.dry_run)
        print(f"deleted {deleted} local checkpoints" if not args.dry_run else f"would delete {deleted} local checkpoints")
        return 0

    if args.cmd == "git-rm-cached":
        removed = git_rm_cached(records, dry_run=args.dry_run)
        print(f"removed {removed} checkpoint paths from Git index" if not args.dry_run else f"would remove {removed} paths")
        return 0

    raise AssertionError(args.cmd)


if __name__ == "__main__":
    sys.exit(main())
