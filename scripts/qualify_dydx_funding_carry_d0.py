"""Run the frozen outcome-blind dYdX fixed-carry D0 qualification."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ecomd.data.dydx_qualification import (
    EndpointKind,
    audit_funding_transition,
    canonical_sha256,
    extract_passed_perpetual_updates,
    row_identity_digests,
    summarize_response,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _git(*command: str) -> str:
    return subprocess.run(
        ["git", *command],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _build_session(retries: int) -> requests.Session:
    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        status=retries,
        allowed_methods=frozenset({"GET"}),
        status_forcelist=(429, 500, 502, 503, 504),
        backoff_factor=0.5,
        raise_on_status=False,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": "EcoPhys-D0-qualification/1.0"})
    return session


def _request(
    session: requests.Session,
    *,
    base_url: str,
    path: str,
    params: Mapping[str, Any],
    endpoint: EndpointKind,
    request_label: str,
    timeout_seconds: int,
) -> tuple[Mapping[str, Any], dict[str, Any]]:
    response = session.get(f"{base_url.rstrip('/')}/{path.lstrip('/')}", params=params, timeout=timeout_seconds)
    if response.status_code != 200:
        raise RuntimeError(f"{request_label} returned HTTP {response.status_code}")
    try:
        payload = response.json()
    except requests.JSONDecodeError as error:
        raise RuntimeError(f"{request_label} did not return JSON") from error
    if not isinstance(payload, Mapping):
        raise RuntimeError(f"{request_label} returned a non-object JSON payload")
    summary = summarize_response(
        payload,
        raw_body=response.content,
        endpoint=endpoint,
        request_label=request_label,
    )
    return payload, summary


def _probe_market(
    session: requests.Session,
    *,
    base_url: str,
    ticker: str,
    execution_height: int,
    execution_time: str,
    candle_window_minutes: int,
    post_height_offset: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    event_time = _parse_time(execution_time)
    label = ticker.replace("-", "_").lower()
    requests_to_run: list[tuple[str, str, EndpointKind, dict[str, Any]]] = [
        (
            f"{label}_trade_pre",
            f"trades/perpetualMarket/{ticker}",
            "trades",
            {"createdBeforeOrAtHeight": execution_height, "limit": 1},
        ),
        (
            f"{label}_trade_post",
            f"trades/perpetualMarket/{ticker}",
            "trades",
            {"createdBeforeOrAtHeight": execution_height + post_height_offset, "limit": 1},
        ),
        (
            f"{label}_candles",
            f"candles/perpetualMarkets/{ticker}",
            "candles",
            {
                "resolution": "1MIN",
                "fromISO": _iso(event_time - timedelta(minutes=candle_window_minutes)),
                "toISO": _iso(event_time + timedelta(minutes=candle_window_minutes)),
                "limit": 100,
            },
        ),
        (
            f"{label}_funding",
            f"historicalFunding/{ticker}",
            "historical_funding",
            {"effectiveBeforeOrAtHeight": execution_height, "limit": 1},
        ),
    ]
    summaries: dict[str, Any] = {}
    for request_label, path, endpoint, params in requests_to_run:
        _, summary = _request(
            session,
            base_url=base_url,
            path=path,
            params=params,
            endpoint=endpoint,
            request_label=request_label,
            timeout_seconds=timeout_seconds,
        )
        summaries[request_label] = summary
    return summaries


def _trade_pagination_probe(
    session: requests.Session,
    *,
    base_url: str,
    ticker: str,
    execution_height: int,
    page_size: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    pages: list[Mapping[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for page in (1, 2):
        payload, summary = _request(
            session,
            base_url=base_url,
            path=f"trades/perpetualMarket/{ticker}",
            params={
                "createdBeforeOrAtHeight": execution_height,
                "limit": page_size,
                "page": page,
            },
            endpoint="trades",
            request_label=f"{ticker.lower()}_trade_page_{page}",
            timeout_seconds=timeout_seconds,
        )
        pages.append(payload)
        summaries.append(summary)
    overlap = row_identity_digests(pages[0], "trades") & row_identity_digests(pages[1], "trades")
    return {
        "ticker": ticker,
        "page_size_requested": page_size,
        "page_summaries": summaries,
        "cross_page_identity_overlap_count": len(overlap),
        "retained_trade_ids": False,
        "retained_market_outcome_values": False,
    }


def _load_config(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text())
    if not isinstance(loaded, dict):
        raise ValueError("D0 config must be a mapping")
    return loaded


def qualify(config_path: Path, output_path: Path) -> dict[str, Any]:
    """Execute governance and Indexer metadata gates and write a sanitized manifest."""
    config = _load_config(config_path)
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status.strip():
        raise RuntimeError("formal D0 qualification requires a clean worktree")

    source = config["sources"]
    timeout_seconds = int(config["limits"]["request_timeout_seconds"])
    session = _build_session(int(config["limits"]["transport_retries"]))

    governance_params: dict[str, str | int] = {
        "pagination.limit": 500,
        "pagination.count_total": "true",
    }
    governance_response = session.get(
        source["cosmos_governance_url"],
        params=governance_params,
        timeout=timeout_seconds,
    )
    if governance_response.status_code != 200:
        raise RuntimeError(f"governance ledger returned HTTP {governance_response.status_code}")
    governance_payload = governance_response.json()
    proposals = governance_payload.get("proposals")
    if not isinstance(proposals, list):
        raise RuntimeError("governance ledger lacks proposals list")
    updates = extract_passed_perpetual_updates(proposals)

    transition_audits: dict[str, Any] = {}
    for event in config["events"]:
        proposal_id = int(event["proposal_id"])
        transition_audits[str(proposal_id)] = audit_funding_transition(
            updates,
            proposal_id=proposal_id,
            tickers=list(event["markets"]),
            expected_pre=int(event["expected_pre_default_funding_ppm"]),
            expected_post=int(event["expected_post_default_funding_ppm"]),
        )

    coverage: dict[str, Any] = {}
    for event in config["events"]:
        for ticker in event["markets"]:
            coverage[ticker] = _probe_market(
                session,
                base_url=source["indexer_base_url"],
                ticker=ticker,
                execution_height=int(event["execution_height"]),
                execution_time=str(event["execution_time"]),
                candle_window_minutes=int(config["coverage"]["candle_window_minutes_each_side"]),
                post_height_offset=int(config["coverage"]["trade_post_height_offset"]),
                timeout_seconds=timeout_seconds,
            )

    pagination = []
    by_proposal = {int(event["proposal_id"]): event for event in config["events"]}
    for probe in config["pagination_probes"]:
        event = by_proposal[int(probe["proposal_id"])]
        pagination.append(
            _trade_pagination_probe(
                session,
                base_url=source["indexer_base_url"],
                ticker=str(probe["ticker"]),
                execution_height=int(event["execution_height"]),
                page_size=int(config["coverage"]["trade_page_size"]),
                timeout_seconds=timeout_seconds,
            )
        )

    all_transitions_clean = all(
        row["clean"] for rows in transition_audits.values() for row in rows
    )
    summaries = [summary for market in coverage.values() for summary in market.values()]
    schema_complete = all(
        summary["row_count"] > 0
        and all(count == 0 for count in summary["missing_required_field_counts"].values())
        for summary in summaries
    )
    pagination_clean = all(
        probe["cross_page_identity_overlap_count"] == 0
        and all(page["row_count"] > 0 for page in probe["page_summaries"])
        for probe in pagination
    )
    decision = "pass" if all_transitions_clean and schema_complete and pagination_clean else "fail"
    payload: dict[str, Any] = {
        "schema_version": 1,
        "status": "formal_dydx_fixed_carry_d0_complete",
        "decision": decision,
        "run": {
            "completed_at_utc": datetime.now(UTC).isoformat(),
            "cpu_only": True,
            "gpu_used": False,
            "paid_data_used": False,
            "market_outcome_values_retained": False,
            "holdout_317_queried": False,
            "forward_220_window_queried": False,
        },
        "repository": {
            "branch": _git("branch", "--show-current"),
            "git_sha": _git("rev-parse", "HEAD"),
        },
        "environment": {"python": platform.python_version(), "requests": requests.__version__},
        "sources": {
            "cosmos_governance_url": source["cosmos_governance_url"],
            "indexer_base_url": source["indexer_base_url"],
            "governance_http_body_bytes": len(governance_response.content),
            "governance_raw_body_sha256": hashlib.sha256(governance_response.content).hexdigest(),
            "proposal_count": len(proposals),
            "passed_perpetual_update_count": len(updates),
            "raw_responses_persisted": False,
        },
        "gates": {
            "all_frozen_transitions_clean": all_transitions_clean,
            "all_probes_nonempty_and_schema_complete": schema_complete,
            "trade_pagination_has_no_cross_page_overlap": pagination_clean,
        },
        "transition_audits": transition_audits,
        "coverage": coverage,
        "pagination": pagination,
        "policy": {
            "result_contains_price_size_side_rate_or_ohlc_values": False,
            "response_hashes_are_retained_for_provenance": True,
            "raw_hosted_responses_are_not_written": True,
        },
    }
    payload["canonical_payload_sha256"] = canonical_sha256(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(output_path)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = qualify(args.config.resolve(), args.output.resolve())
    print(
        json.dumps(
            {
                "decision": payload["decision"],
                "markets_qualified": len(payload["coverage"]),
                "manifest": str(args.output.resolve()),
                "canonical_payload_sha256": payload["canonical_payload_sha256"],
                "market_outcome_values_retained": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if payload["decision"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
