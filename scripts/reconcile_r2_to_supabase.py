"""Reconcile Supabase checkpoint catalog against R2 object inventory.

Use case: H20 ran `python -m ecomd.data.checkpoint_sync sync` without
`.env.supabase` configured. Checkpoints were uploaded to R2 but Supabase
catalog wasn't updated. This script:

  1. Lists R2 objects under `checkpoints/` prefix (HTTP cheap)
  2. For each R2 key, builds a CheckpointRecord using LOCAL metadata
     (config.yaml + training_log.json + on-disk file stat) — sha256 is
     read from R2 object Metadata (set when uploaded), no local hashing.
  3. Filters out R2 keys whose local file is missing (orphans in R2)
  4. Upserts to Supabase in batches of 500

Faster than `checkpoint_sync sync` because it skips:
  - SHA256-ing 6861 local files (~10 minutes)
  - 6861 sequential head_object calls (~10 minutes)
  - Re-uploading already-present objects (no-op but timed)

If R2 object doesn't carry a sha256 in Metadata, we fall back to ETag (R2
sets ETag = MD5 for small files, multipart for big ones — not a stable
hash but better than nothing).

Usage:
    conda run -n ecophys python scripts/reconcile_r2_to_supabase.py \\
        --prefix checkpoints/ --batch-size 500 [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

import requests

from ecomd.data.checkpoint_sync import (
    CheckpointRecord,
    SupabaseConfig,
    _experiment_dir,
    _load_config_for_result,
    _load_training_summary,
    _optional_int,
    _optional_str,
    load_env_files,
    sha256_file,
)
from ecomd.data.r2_sync import R2Config, _client, _find_project_root

log = logging.getLogger("reconcile_r2_to_supabase")

REPO = _find_project_root()


def list_r2_objects(prefix: str, cfg: R2Config) -> Iterable[dict]:
    client = _client(cfg)
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=cfg.bucket, Prefix=prefix):
        for obj in page.get("Contents") or []:
            yield obj


def head_metadata(client, bucket: str, key: str) -> dict[str, str]:
    try:
        resp = client.head_object(Bucket=bucket, Key=key)
    except Exception as exc:  # noqa: BLE001
        log.debug("head_object failed for %s: %s", key, exc)
        return {}
    meta = {str(k).lower(): v for k, v in (resp.get("Metadata") or {}).items()}
    meta["_size"] = int(resp.get("ContentLength", 0))
    meta["_etag"] = (resp.get("ETag") or "").strip('"')
    return meta


def build_record_from_local(
    r2_key: str,
    r2_bucket: str,
    local_path: Path,
    size_bytes: int,
    sha256: str,
) -> CheckpointRecord | None:
    if not local_path.exists():
        return None
    rel = local_path.resolve().relative_to(REPO.resolve()).as_posix()
    result_dir = local_path.parent.relative_to(REPO).as_posix()
    experiment_dir = _experiment_dir(local_path, REPO)
    config = _load_config_for_result(local_path.parent, REPO)
    training = config.get("training", {}) if isinstance(config, dict) else {}
    simulator = config.get("simulator", {}) if isinstance(config, dict) else {}
    return CheckpointRecord(
        local_path=rel,
        r2_bucket=r2_bucket,
        r2_key=r2_key,
        size_bytes=size_bytes,
        sha256=sha256,
        experiment_dir=experiment_dir,
        result_dir=result_dir,
        checkpoint_name=local_path.name,
        seed=_optional_int(training.get("seed")) if isinstance(training, dict) else None,
        target_dataset=_optional_str(training.get("target_dataset")) if isinstance(training, dict) else None,
        target_period=_optional_str(training.get("target_period")) if isinstance(training, dict) else None,
        n_agents=_optional_int(simulator.get("n_agents")) if isinstance(simulator, dict) else None,
        config=config,
        training_summary=_load_training_summary(local_path.parent),
        uploaded_at=datetime.now(UTC).isoformat(),
        upload_status="ok",
    )


def upsert_batch(records: list[CheckpointRecord], cfg: SupabaseConfig, dry_run: bool) -> None:
    if not records:
        return
    payload = [r.supabase_payload() for r in records]
    if dry_run:
        log.info("DRY upsert %d rows", len(records))
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
        timeout=120,
    )
    if resp.status_code >= 300:
        raise RuntimeError(
            f"Supabase upsert failed: HTTP {resp.status_code}: {resp.text[:500]}"
        )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prefix", default="checkpoints/")
    p.add_argument("--batch-size", type=int, default=500)
    p.add_argument("--head-objects", action="store_true",
                   help="Also call head_object for each R2 key to get sha256 from Metadata (slow)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--log-level", default="INFO")
    args = p.parse_args()

    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")

    load_env_files()
    r2 = R2Config.from_env()
    sb = SupabaseConfig.from_env(allow_missing=args.dry_run)
    log.info("R2 bucket=%s prefix=%s | Supabase=%s table=%s", r2.bucket, args.prefix, sb.url, sb.table)

    client = _client(r2)

    seen = 0
    matched = 0
    missing_local = 0
    batch: list[CheckpointRecord] = []
    total_upserted = 0

    for obj in list_r2_objects(args.prefix, r2):
        seen += 1
        key = obj["Key"]
        size_bytes = int(obj.get("Size", 0))
        etag = (obj.get("ETag") or "").strip('"')

        local_rel = key
        if local_rel.startswith(f"{args.prefix.rstrip('/')}/"):
            local_rel = local_rel[len(args.prefix.rstrip('/')) + 1:]
        local_path = REPO / local_rel

        if not local_path.exists():
            missing_local += 1
            log.debug("local missing for %s", key)
            continue

        sha256 = ""
        if args.head_objects:
            md = head_metadata(client, r2.bucket, key)
            sha256 = md.get("sha256", "")
        if not sha256 or len(sha256) != 64:
            sha256 = sha256_file(local_path)

        rec = build_record_from_local(
            r2_key=key, r2_bucket=r2.bucket, local_path=local_path,
            size_bytes=size_bytes, sha256=sha256,
        )
        if rec is None:
            missing_local += 1
            continue

        matched += 1
        batch.append(rec)
        if len(batch) >= args.batch_size:
            log.info("upserting batch of %d (total seen=%d, matched=%d, missing_local=%d)",
                     len(batch), seen, matched, missing_local)
            upsert_batch(batch, sb, args.dry_run)
            total_upserted += len(batch)
            batch = []

    if batch:
        log.info("upserting final batch of %d", len(batch))
        upsert_batch(batch, sb, args.dry_run)
        total_upserted += len(batch)

    log.info(
        "DONE  R2 objects seen=%d  matched-local=%d  missing-local=%d  upserted=%d",
        seen, matched, missing_local, total_upserted,
    )


if __name__ == "__main__":
    main()
