"""Run the frozen pre-period-only D1A activity screen for dYdX markets."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ecomd.data.dydx_qualification import canonical_sha256, summarize_daily_activity

REPO_ROOT = Path(__file__).resolve().parents[1]


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _session(retries: int) -> requests.Session:
    policy = Retry(
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
    session.mount("https://", HTTPAdapter(max_retries=policy))
    session.headers.update({"User-Agent": "EcoPhys-D1A-activity-screen/1.0"})
    return session


def _load(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError("D1A config must be a mapping")
    return payload


def screen(config_path: Path, output_path: Path) -> dict[str, Any]:
    """Apply the frozen activity rule and write no other candle outcome values."""
    dirty = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if dirty.strip():
        raise RuntimeError("formal D1A screen requires a clean worktree")
    config = _load(config_path)
    session = _session(int(config["limits"]["transport_retries"]))
    base_url = str(config["source"]["indexer_base_url"]).rstrip("/")
    timeout = int(config["limits"]["request_timeout_seconds"])
    minimum_trades = int(config["activity_rule"]["minimum_trades_per_day"])
    minimum_days = int(config["activity_rule"]["minimum_eligible_pre_days"])
    market_results: dict[str, Any] = {}

    for event in config["events"]:
        start = str(event["pre_start_inclusive"])
        end = str(event["pre_end_exclusive"])
        request_end = (
            datetime.fromisoformat(end.replace("Z", "+00:00")) - timedelta(seconds=1)
        ).isoformat()
        for ticker in event["markets"]:
            query_params: dict[str, str | int] = {
                "resolution": "1DAY",
                "fromISO": start,
                "toISO": request_end,
                "limit": 100,
            }
            response = session.get(
                f"{base_url}/candles/perpetualMarkets/{ticker}",
                params=query_params,
                timeout=timeout,
            )
            if response.status_code != 200:
                raise RuntimeError(f"activity probe for {ticker} returned HTTP {response.status_code}")
            payload = response.json()
            if not isinstance(payload, dict):
                raise RuntimeError(f"activity probe for {ticker} returned non-object JSON")
            result = summarize_daily_activity(
                payload,
                raw_body=response.content,
                start_inclusive=start,
                end_exclusive=end,
                minimum_trades_per_day=minimum_trades,
                minimum_eligible_days=minimum_days,
            )
            result["proposal_id"] = int(event["proposal_id"])
            market_results[str(ticker)] = result

    eligible = sorted(
        ticker for ticker, result in market_results.items() if result["activity_eligible"]
    )
    ineligible = sorted(set(market_results) - set(eligible))
    eligible_count = len(eligible)
    if eligible_count >= int(config["decision"]["proceed_minimum_markets"]):
        decision = "pass_proceed_to_separately_frozen_d1b"
    elif eligible_count >= int(config["decision"]["amber_minimum_markets"]):
        decision = "amber_redesign_before_any_tick_outcome"
    else:
        decision = "stop_dydx_only_before_bulk_ticks"

    result_payload: dict[str, Any] = {
        "schema_version": 1,
        "status": "formal_dydx_fixed_carry_d1a_complete",
        "decision": decision,
        "repository": {
            "branch": _git("branch", "--show-current"),
            "git_sha": _git("rev-parse", "HEAD"),
        },
        "source": {
            "indexer_base_url": base_url,
            "raw_responses_persisted": False,
            "requests_completed": len(market_results),
        },
        "activity_rule": config["activity_rule"],
        "eligible_market_count": eligible_count,
        "eligible_markets": eligible,
        "ineligible_markets": ineligible,
        "markets": market_results,
        "blinding": {
            "post_event_candles_queried": False,
            "trade_rows_queried": False,
            "proposal_317_queried": False,
            "proposal_220_window_queried": False,
            "retained_candle_fields": ["startedAt", "trades"],
            "retained_price_volume_ohlc_oi_or_midpoint_values": False,
        },
        "compute": {"cpu_only": True, "gpu_used": False, "paid_data_used": False},
    }
    result_payload["canonical_payload_sha256"] = canonical_sha256(result_payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(json.dumps(result_payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(output_path)
    return result_payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = screen(args.config.resolve(), args.output.resolve())
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "eligible_market_count": result["eligible_market_count"],
                "eligible_markets": result["eligible_markets"],
                "ineligible_markets": result["ineligible_markets"],
                "manifest": str(args.output.resolve()),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
