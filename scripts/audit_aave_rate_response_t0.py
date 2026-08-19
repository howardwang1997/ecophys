"""Run the frozen outcome-blind T0 audit for Aave rate-step spectroscopy."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ecomd.data.aave_qualification import (
    audit_asset_rate_change,
    canonical_sha256,
    find_payload_execution,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _load_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("T0 config must be a mapping")
    return payload


def _session(retries: int) -> requests.Session:
    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        status=retries,
        allowed_methods=frozenset({"GET", "POST"}),
        status_forcelist=(429, 500, 502, 503, 504),
        backoff_factor=0.5,
        raise_on_status=False,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": "EcoPhys-Aave-T0-audit/1.0"})
    return session


def _rpc(
    session: requests.Session,
    *,
    url: str,
    method: str,
    params: list[Any],
    request_id: int,
    timeout: int,
) -> Any:
    response = session.post(
        url,
        json={"jsonrpc": "2.0", "id": request_id, "method": method, "params": params},
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict) or "result" not in payload:
        raise RuntimeError(f"RPC {method} returned no result: {payload}")
    return payload["result"]


def _audit_zenodo(
    session: requests.Session,
    *,
    source: dict[str, Any],
    timeout: int,
) -> dict[str, Any]:
    record_response = session.get(str(source["record_api"]), timeout=timeout)
    try:
        record_body = record_response.json()
    except requests.JSONDecodeError:
        record_body = None
    search_params: dict[str, str | int] = {
        "q": f'metadata.title:"{source["title"]}"',
        "size": 20,
    }
    search_response = session.get(
        str(source["exact_title_search_api"]),
        params=search_params,
        timeout=timeout,
    )
    search_response.raise_for_status()
    search_body = search_response.json()
    total = search_body.get("hits", {}).get("total") if isinstance(search_body, dict) else None
    available = record_response.status_code == 200 and isinstance(record_body, dict)
    return {
        "doi": str(source["doi"]),
        "record_http_status": record_response.status_code,
        "record_body_sha256": hashlib.sha256(record_response.content).hexdigest(),
        "record_api_status": record_body.get("status") if isinstance(record_body, dict) else None,
        "record_api_message": record_body.get("message") if isinstance(record_body, dict) else None,
        "exact_title_search_total": total,
        "dataset_download_available": available,
        "bulk_dataset_download_attempted": False,
    }


def audit(
    config_path: Path,
    output_path: Path,
    governance_cache_root: Path,
    proposals_repository_root: Path,
) -> dict[str, Any]:
    """Audit only governance, source diffs, data availability, and RPC metadata."""
    dirty = _git(REPO_ROOT, "status", "--porcelain")
    if dirty:
        raise RuntimeError("formal T0 audit requires a clean EcoPhys worktree")
    config = _load_config(config_path)
    sources = config["sources"]
    governance_sha = _git(governance_cache_root, "rev-parse", "HEAD")
    proposals_sha = _git(proposals_repository_root, "rev-parse", "HEAD")
    if governance_sha != str(sources["governance_cache"]["expected_git_sha"]):
        raise RuntimeError(f"unexpected governance-cache SHA: {governance_sha}")
    if proposals_sha != str(sources["proposals_repository"]["expected_git_sha"]):
        raise RuntimeError(f"unexpected proposals-repository SHA: {proposals_sha}")

    assets = config["market"]["assets"]
    event_results: list[dict[str, Any]] = []
    for expected in config["events"]:
        proposal_id = int(expected["proposal_id"])
        execution = find_payload_execution(
            governance_cache_root,
            proposal_id=proposal_id,
            chain_id=int(config["market"]["chain_id"]),
        )
        checks = {
            "title": execution["title"] == str(expected["expected_title"]),
            "payload_id": execution["payload_id"] == int(expected["expected_payload_id"]),
            "implementation_commit": execution["implementation_commit"]
            == str(expected["implementation_commit"]),
            "implementation_directory": execution["implementation_directory"]
            == str(expected["implementation_directory"]),
        }
        if not all(checks.values()):
            raise RuntimeError(f"proposal {proposal_id} metadata mismatch: {checks}")
        markdown = _git(
            proposals_repository_root,
            "show",
            f"{expected['implementation_commit']}:{expected['diff_path']}",
        )
        asset_audits = [
            audit_asset_rate_change(
                markdown,
                symbol=symbol,
                expected_before_bps=int(expected["slope1_before_bps"]),
                expected_after_bps=int(expected["slope1_after_bps"]),
            )
            for symbol in sorted(assets)
        ]
        event_results.append(
            {
                **execution,
                "executed_at_utc": datetime.fromtimestamp(
                    execution["executed_at_unix"], UTC
                ).isoformat(),
                "diff_path": str(expected["diff_path"]),
                "diff_sha256": hashlib.sha256(markdown.encode()).hexdigest(),
                "metadata_checks": checks,
                "assets": asset_audits,
                "clean_for_selected_assets": all(
                    row["clean_singleton_configured_change"] for row in asset_audits
                ),
            }
        )

    timeout = int(config["limits"]["request_timeout_seconds"])
    session = _session(int(config["limits"]["transport_retries"]))
    rpc_url = str(sources["public_rpc"]["url"])
    chain_id = _rpc(
        session,
        url=rpc_url,
        method="eth_chainId",
        params=[],
        request_id=1,
        timeout=timeout,
    )
    topics: dict[str, str] = {}
    for request_id, (name, signature) in enumerate(config["event_topics"].items(), start=2):
        topics[name.removesuffix("_signature") + "_topic"] = str(
            _rpc(
                session,
                url=rpc_url,
                method="web3_sha3",
                params=["0x" + str(signature).encode().hex()],
                request_id=request_id,
                timeout=timeout,
            )
        )
    rpc_pass = chain_id == str(sources["public_rpc"]["expected_chain_id_hex"]) and all(
        len(topic) == 66 and topic.startswith("0x") for topic in topics.values()
    )
    zenodo = _audit_zenodo(
        session,
        source=sources["claimed_open_dataset"],
        timeout=timeout,
    )

    units = len(event_results) * len(assets)
    minimum_units = int(config["selection"]["minimum_units_before_activity_screen"])
    passed = (
        all(event["clean_for_selected_assets"] for event in event_results)
        and units >= minimum_units
        and rpc_pass
    )
    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "formal_aave_rate_response_t0_complete",
        "decision": (
            "pass_to_separately_committed_preperiod_activity_freeze"
            if passed
            else "stop_before_aave_activity_or_outcome_logs"
        ),
        "repository": {
            "branch": _git(REPO_ROOT, "branch", "--show-current"),
            "git_sha": _git(REPO_ROOT, "rev-parse", "HEAD"),
        },
        "official_sources": {
            "governance_cache_git_sha": governance_sha,
            "proposals_repository_git_sha": proposals_sha,
        },
        "claimed_open_dataset": zenodo,
        "public_rpc_metadata": {
            "url": rpc_url,
            "chain_id": chain_id,
            "event_topics": topics,
            "metadata_probe_pass": rpc_pass,
            "market_logs_queried": False,
        },
        "market": config["market"],
        "events": event_results,
        "selected_proposal_count": len(event_results),
        "selected_asset_count": len(assets),
        "singleton_market_event_unit_count": units,
        "minimum_units_before_activity_screen": minimum_units,
        "selection": config["selection"],
        "blinding": {
            "borrow_repay_logs_queried": False,
            "reserve_data_outcomes_queried": False,
            "position_balances_queried": False,
            "post_event_values_queried": False,
            "raw_market_responses_persisted": False,
        },
        "compute": {"cpu_only": True, "gpu_used": False, "paid_data_used": False},
    }
    result["canonical_payload_sha256"] = canonical_sha256(result)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output_path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--governance-cache-root", type=Path, required=True)
    parser.add_argument("--proposals-repository-root", type=Path, required=True)
    args = parser.parse_args()
    result = audit(
        args.config.resolve(),
        args.output.resolve(),
        args.governance_cache_root.resolve(),
        args.proposals_repository_root.resolve(),
    )
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "singleton_market_event_unit_count": result[
                    "singleton_market_event_unit_count"
                ],
                "claimed_open_dataset_available": result["claimed_open_dataset"][
                    "dataset_download_available"
                ],
                "manifest": str(args.output.resolve()),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
