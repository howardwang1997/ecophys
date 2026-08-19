"""Run the frozen target-free SQD Portal qualification."""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import subprocess
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from omegaconf import OmegaConf

from ecomd.data.sqd_qualification import (
    SqdPortalClient,
    canonical_sha256,
    select_block_windows,
    validate_block_window,
)

ROOT = Path(__file__).resolve().parents[2]


def _integer_field(payload: Mapping[str, Any], *names: str) -> int:
    for name in names:
        value = payload.get(name)
        if isinstance(value, int):
            return value
    raise ValueError(f"missing integer field among {names}")


def _git_sha(explicit: str | None) -> str:
    if explicit:
        return explicit
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--git-sha")
    args = parser.parse_args()
    if args.num_shards <= 0 or not 0 <= args.shard_index < args.num_shards:
        raise ValueError("shard index must be in [0, num_shards)")

    cfg = OmegaConf.to_container(OmegaConf.load(args.config), resolve=True)
    if not isinstance(cfg, dict):
        raise ValueError("configuration must be a mapping")
    datasets = cfg["datasets"]
    if not isinstance(datasets, list) or not all(isinstance(item, str) for item in datasets):
        raise ValueError("datasets must be a string list")
    assigned = [name for index, name in enumerate(datasets) if index % args.num_shards == args.shard_index]
    client = SqdPortalClient(
        str(cfg["base_url"]),
        timeout_seconds=float(cfg["timeout_seconds"]),
        max_attempts=int(cfg["max_attempts"]),
    )

    network_results: dict[str, Any] = {}
    request_latencies: list[float] = []
    request_attempts: list[int] = []
    for dataset in assigned:
        metadata = client.get_json(dataset, "metadata")
        finalized = client.get_json(dataset, "finalized-head")
        request_latencies.extend((metadata.latency_seconds, finalized.latency_seconds))
        request_attempts.extend((metadata.attempts, finalized.attempts))
        if not isinstance(metadata.payload, Mapping) or not isinstance(finalized.payload, Mapping):
            raise ValueError(f"unexpected metadata/head schema for {dataset}")
        start_block = _integer_field(metadata.payload, "start_block", "startBlock")
        finalized_block = _integer_field(finalized.payload, "number", "height", "block_number")
        windows = select_block_windows(
            start_block,
            finalized_block,
            fractions=[float(value) for value in cfg["sample_fractions"]],
            width=int(cfg["window_width"]),
            near_head_lag=int(cfg["near_finalized_lag"]),
        )
        window_results: list[dict[str, Any]] = []
        for window in windows:
            repeats = [client.get_finalized_headers(dataset, window) for _ in range(int(cfg["repeats"]))]
            request_latencies.extend(record.latency_seconds for record in repeats)
            request_attempts.extend(record.attempts for record in repeats)
            validations = [validate_block_window(record.payload, window) for record in repeats]
            repeat_hashes = [validation["canonical_sha256"] for validation in validations]
            checks = {
                "each_repeat_valid": all(item["all_checks_pass"] for item in validations),
                "repeat_content_exact": len(set(repeat_hashes)) == 1,
            }
            window_results.append(
                {
                    "label": window.label,
                    "first": window.first,
                    "last": window.last,
                    "request": [
                        {
                            "status_code": item.status_code,
                            "latency_seconds": item.latency_seconds,
                            "attempts": item.attempts,
                            "body_sha256": item.body_sha256,
                        }
                        for item in repeats
                    ],
                    "validations": validations,
                    "checks": checks,
                    "all_checks_pass": all(checks.values()),
                }
            )
        network_results[dataset] = {
            "metadata": metadata.payload,
            "metadata_body_sha256": metadata.body_sha256,
            "finalized_head": finalized.payload,
            "finalized_head_body_sha256": finalized.body_sha256,
            "selected_windows": window_results,
            "all_checks_pass": all(item["all_checks_pass"] for item in window_results),
        }

    retry_fraction = sum(attempt > 1 for attempt in request_attempts) / len(request_attempts)
    median_latency = statistics.median(request_latencies)
    shard_checks = {
        "all_assigned_networks_present": set(network_results) == set(assigned),
        "all_network_checks_pass": all(item["all_checks_pass"] for item in network_results.values()),
        "retry_fraction_within_gate": retry_fraction <= float(cfg["maximum_retry_fraction"]),
        "median_latency_within_gate": median_latency <= float(cfg["maximum_median_latency_seconds"]),
    }
    payload = {
        "experiment": cfg["experiment"],
        "protocol": "Q0a header-only; no event rows requested",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_sha": _git_sha(args.git_sha),
        "platform": platform.platform(),
        "config_sha256": canonical_sha256(cfg),
        "shard_index": args.shard_index,
        "num_shards": args.num_shards,
        "assigned_datasets": assigned,
        "request_count": len(request_attempts),
        "retry_fraction": retry_fraction,
        "median_latency_seconds": median_latency,
        "networks": network_results,
        "checks": shard_checks,
        "all_checks_pass": all(shard_checks.values()),
        "interpretation": "source feasibility only; target extraction remains locked",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
