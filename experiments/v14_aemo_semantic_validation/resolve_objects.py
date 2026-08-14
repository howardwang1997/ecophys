#!/usr/bin/env python3
"""Resolve exact held-out AEMO object metadata using HEAD requests only."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import requests
import yaml

from ecomd.market_world.provenance import require_clean_repository
from ecomd.research.aemo_semantic_crosswalk import (
    load_crosswalk,
    manifest_sha256,
    resolve_head_metadata,
    utc_now,
    validate_crosswalk,
)

USER_AGENT = "EcoPhys-AEMO-semantic-validation/1.0"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "data/manifests/aemo_semantic_crosswalk_v2.yaml",
    )
    arguments = parser.parse_args()
    commit = require_clean_repository(ROOT)
    manifest = load_crosswalk(arguments.manifest)
    errors = validate_crosswalk(manifest)
    if errors:
        raise RuntimeError("invalid unresolved crosswalk: " + "; ".join(errors))
    outputs = cast(dict[str, object], manifest["outputs"])
    output_path = ROOT / cast(str, outputs["resolved_manifest"])
    if output_path.exists():
        raise FileExistsError(output_path)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    observations: list[dict[str, object]] = []
    for item in cast(list[dict[str, object]], manifest["objects"]):
        try:
            response = session.head(
                cast(str, item["url"]),
                timeout=(30.0, 120.0),
                allow_redirects=False,
            )
            length_text = response.headers.get("Content-Length")
            content_length = int(length_text) if length_text and length_text.isdigit() else None
            observation: dict[str, object] = {
                "object_id": item["object_id"],
                "http_status": response.status_code,
                "content_length": content_length,
                "etag": response.headers.get("ETag"),
                "last_modified": response.headers.get("Last-Modified"),
                "transport_error": None,
            }
            response.close()
        except requests.RequestException as error:
            observation = {
                "object_id": item["object_id"],
                "http_status": None,
                "content_length": None,
                "etag": None,
                "last_modified": None,
                "transport_error": f"{type(error).__name__}: {error}",
            }
        observations.append(observation)
        print(json.dumps(observation, sort_keys=True), flush=True)

    resolved = resolve_head_metadata(
        manifest,
        observations,
        source_manifest_sha256=manifest_sha256(arguments.manifest),
        resolved_at=utc_now(),
        resolver_git_commit=commit,
    )
    resolved_errors = validate_crosswalk(resolved)
    if resolved_errors:
        raise RuntimeError("generated resolved crosswalk is invalid: " + "; ".join(resolved_errors))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.safe_dump(resolved, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "resolved_manifest": output_path.relative_to(ROOT).as_posix(),
                "all_head_requests_pass": cast(dict[str, object], resolved["resolution"])[
                    "all_head_requests_pass"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
