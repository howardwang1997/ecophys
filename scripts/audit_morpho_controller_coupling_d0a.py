"""Run the frozen outcome-blind Morpho deployment-identity audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
import urllib.error
import urllib.request
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from ecomd.data.morpho_deployment_identity import (
    assess_deployment_identity,
    parse_allocator_registry,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def _load_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("D0A config must be an object")
    return payload


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _fetch_json(
    url: str,
    *,
    timeout_seconds: float,
    maximum_attempts: int,
    retry_backoff_seconds: float,
) -> tuple[dict[str, Any], bytes, int]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "EcoPhys-D0A/1"},
    )
    last_error: Exception | None = None
    for attempt in range(maximum_attempts):
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                raw = response.read()
                status = int(response.status)
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError("allocator endpoint returned a non-object JSON value")
            return payload, raw, status
        except (OSError, ValueError, urllib.error.URLError) as error:
            last_error = error
            if attempt + 1 < maximum_attempts:
                time.sleep(retry_backoff_seconds * (attempt + 1))
    raise RuntimeError(f"allocator endpoint failed after {maximum_attempts} attempts: {url}") from last_error


def _flatten_public_allocators(config: Mapping[str, Any]) -> list[str]:
    groups = config.get("official_public_allocators")
    if not isinstance(groups, Mapping):
        raise ValueError("official_public_allocators must be an object")
    addresses: list[str] = []
    for values in groups.values():
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            raise ValueError("public allocator groups must contain address strings")
        addresses.extend(values)
    return addresses


def run_audit(config_path: Path, output_path: Path) -> dict[str, Any]:
    """Execute D0A and write only sanitized deployment-role metadata."""
    config = _load_config(config_path)
    contract = config.get("contract")
    if not isinstance(contract, Mapping) or contract.get("status") != (
        "frozen_before_allocator_role_queries_or_reallocation_history"
    ):
        raise ValueError("D0A contract is not frozen")
    if _git("status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("formal D0A requires a clean worktree")

    api = config["api"]
    candidates_config = config["candidates"]
    hard_gates = config["hard_gates"]
    if not isinstance(api, Mapping) or not isinstance(candidates_config, list):
        raise ValueError("D0A API or candidate configuration is malformed")
    if len(candidates_config) > int(api["maximum_requests"]):
        raise ValueError("candidate list exceeds the frozen request cap")

    assessed_candidates: list[dict[str, Any]] = []
    retrievals: list[dict[str, Any]] = []
    for candidate in candidates_config:
        if not isinstance(candidate, Mapping):
            raise ValueError("candidate must be an object")
        endpoint = str(candidate["allocator_endpoint"])
        if any(forbidden in endpoint.lower() for forbidden in config["forbidden_endpoints"]):
            raise ValueError(f"candidate endpoint contains a forbidden path: {endpoint}")
        payload, raw, status = _fetch_json(
            endpoint,
            timeout_seconds=float(api["request_timeout_seconds"]),
            maximum_attempts=int(api["maximum_attempts"]),
            retry_backoff_seconds=float(api["retry_backoff_seconds"]),
        )
        records = parse_allocator_registry(payload)
        assessed_candidates.append({**dict(candidate), "allocator_records": records})
        retrievals.append(
            {
                "operator": str(candidate["operator"]),
                "vault_address": str(candidate["vault_address"]).lower(),
                "http_status": status,
                "response_sha256": hashlib.sha256(raw).hexdigest(),
                "allocator_record_count": len(records),
            }
        )

    assessment = assess_deployment_identity(
        assessed_candidates,
        public_allocator_addresses=_flatten_public_allocators(config),
        required_candidate_count=int(hard_gates["required_candidate_count"]),
        minimum_independent_operator_clusters=int(hard_gates["minimum_independent_operator_clusters"]),
        minimum_distinct_nonpublic_allocator_addresses=int(
            hard_gates["minimum_distinct_nonpublic_allocator_addresses"]
        ),
        minimum_distinct_policy_families=int(hard_gates["minimum_distinct_policy_families"]),
    )
    metadata_by_operator = {item["operator"]: item for item in assessment["candidates"]}
    sanitized_candidates: list[dict[str, Any]] = []
    for candidate in candidates_config:
        operator = str(candidate["operator"])
        sanitized_candidates.append(
            {
                "operator": operator,
                "anchor_name": str(candidate["anchor_name"]),
                "policy_family": str(candidate["policy_family"]),
                "chain_id": int(candidate["chain_id"]),
                "vault_version": str(candidate["vault_version"]),
                "vault_address": str(candidate["vault_address"]).lower(),
                "evidence_urls": list(candidate["evidence"]),
                **metadata_by_operator[operator],
            }
        )

    body: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": "morpho_controller_coupling_d0a_v1",
        "created_utc": datetime.now(UTC).isoformat(),
        "repository": {
            "git_sha": _git("rev-parse", "HEAD"),
            "worktree_clean_before_run": True,
        },
        "config": {
            "path": str(config_path.relative_to(REPO_ROOT)),
            "sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        },
        "retrievals": retrievals,
        "candidates": sanitized_candidates,
        "counts": assessment["counts"],
        "gates": assessment["gates"],
        "identity_gate_pass": assessment["pass"],
        "scientific_decision": (
            "d0a_pass_to_separately_frozen_d0b_support_audit"
            if assessment["pass"]
            else "d0a_fail_close_field_route_before_reallocation_history"
        ),
        "data_contract": {
            "queries": "three_fixed_current_allocator_role_endpoints_only",
            "raw_responses_retained": False,
            "market_outcomes_used": False,
            "gpu_used": False,
            "forbidden_data_untouched": list(config["forbidden_data"]),
        },
        "claim_limit": (
            "A pass establishes public documentary and current role support only; it does not identify historical "
            "transactions, exact strategy code, activity, causal effects, or NMI/NCS fit."
        ),
    }
    body["canonical_payload_sha256"] = _canonical_sha256(body)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return body


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "configs/empirical_physics/morpho_controller_coupling_d0a_v1.yaml",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "results/empirical_physics/morpho_controller_coupling_d0a_v1.json",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = run_audit(args.config.resolve(), args.output.resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
