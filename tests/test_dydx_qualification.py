from __future__ import annotations

import json

from ecomd.data.dydx_qualification import (
    audit_funding_transition,
    extract_passed_perpetual_updates,
    summarize_daily_activity,
    summarize_response,
)


def test_trade_summary_retains_schema_not_outcomes() -> None:
    payload = {
        "trades": [
            {
                "id": "event-secret-a",
                "side": "BUY",
                "size": "3.0",
                "price": "101.25",
                "type": "LIMIT",
                "createdAt": "2025-11-14T12:07:35.000Z",
                "createdAtHeight": "63326125",
            },
            {
                "id": "event-secret-b",
                "side": "SELL",
                "size": "2.0",
                "price": "99.75",
                "type": "MARKET",
                "createdAt": "2025-11-14T12:07:36.000Z",
                "createdAtHeight": "63326126",
            },
        ],
        "pageSize": 2,
        "totalResults": 10,
        "offset": 0,
    }
    summary = summarize_response(
        payload,
        raw_body=json.dumps(payload).encode(),
        endpoint="trades",
        request_label="fixture",
    )
    encoded = json.dumps(summary)
    assert summary["row_count"] == 2
    assert summary["minimum_height"] == 63326125
    assert summary["maximum_height"] == 63326126
    assert summary["missing_required_field_counts"] == {
        key: 0 for key in sorted({"id", "side", "size", "price", "type", "createdAt", "createdAtHeight"})
    }
    for forbidden in ("BUY", "SELL", "101.25", "99.75", "3.0", "2.0", "event-secret"):
        assert forbidden not in encoded


def test_governance_audit_requires_funding_only_change() -> None:
    base = {
        "id": 7,
        "ticker": "TEST-USD",
        "market_id": 7,
        "atomic_resolution": -6,
        "liquidity_tier": 2,
        "market_type": "PERPETUAL_MARKET_TYPE_CROSS",
    }
    proposals = [
        {
            "id": "10",
            "status": "PROPOSAL_STATUS_PASSED",
            "voting_end_time": "2025-01-01T00:00:00Z",
            "messages": [
                {
                    "@type": "/dydxprotocol.perpetuals.MsgUpdatePerpetualParams",
                    "authority": "dydx1gov",
                    "perpetual_params": {**base, "default_funding_ppm": 100},
                }
            ],
        },
        {
            "id": "11",
            "status": "PROPOSAL_STATUS_PASSED",
            "voting_end_time": "2025-02-01T00:00:00Z",
            "messages": [
                {
                    "@type": "/dydxprotocol.perpetuals.MsgUpdatePerpetualParams",
                    "authority": "dydx1gov",
                    "perpetual_params": {**base, "default_funding_ppm": 0},
                }
            ],
        },
    ]
    updates = extract_passed_perpetual_updates(proposals)
    audit = audit_funding_transition(
        updates,
        proposal_id=11,
        tickers=["TEST-USD"],
        expected_pre=100,
        expected_post=0,
    )
    assert audit == [
        {
            "ticker": "TEST-USD",
            "pre_proposal_id": 10,
            "post_proposal_id": 11,
            "pre_default_funding_ppm": 100,
            "post_default_funding_ppm": 0,
            "changed_payload_fields": ["default_funding_ppm"],
            "clean": True,
        }
    ]


def test_daily_activity_summary_retains_only_gate_values() -> None:
    payload = {
        "candles": [
            {
                "startedAt": "2025-01-01T00:00:00.000Z",
                "ticker": "TEST-USD",
                "resolution": "1DAY",
                "trades": 101,
                "open": "SECRET_OPEN",
                "high": "SECRET_HIGH",
                "low": "SECRET_LOW",
                "close": "SECRET_CLOSE",
                "baseTokenVolume": "SECRET_VOLUME",
                "usdVolume": "SECRET_USD_VOLUME",
                "startingOpenInterest": "SECRET_OI",
            },
            {
                "startedAt": "2025-01-02T00:00:00.000Z",
                "ticker": "TEST-USD",
                "resolution": "1DAY",
                "trades": 99,
                "open": "ANOTHER_SECRET",
            },
        ]
    }
    summary = summarize_daily_activity(
        payload,
        raw_body=json.dumps(payload).encode(),
        start_inclusive="2025-01-01T00:00:00Z",
        end_exclusive="2025-01-03T00:00:00Z",
        minimum_trades_per_day=100,
        minimum_eligible_days=1,
    )
    encoded = json.dumps(summary)
    assert summary["daily_trade_counts"] == {"2025-01-01": 101, "2025-01-02": 99}
    assert summary["days_meeting_activity_floor"] == 1
    assert summary["activity_eligible"] is True
    for forbidden in (
        "SECRET_OPEN",
        "SECRET_HIGH",
        "SECRET_LOW",
        "SECRET_CLOSE",
        "SECRET_VOLUME",
        "SECRET_USD_VOLUME",
        "SECRET_OI",
        "ANOTHER_SECRET",
    ):
        assert forbidden not in encoded
