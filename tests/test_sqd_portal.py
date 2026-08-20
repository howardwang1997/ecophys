from __future__ import annotations

import json
from typing import Any, cast

import pytest
import requests

from ecomd.data.sqd_portal import SqdPortalClient, SqdPortalError

ADDRESS = "0x" + "11" * 20
OTHER_ADDRESS = "0x" + "22" * 20
TOPIC = "0x" + "33" * 32
TOPIC_1 = "0x" + "34" * 32
TX_HASH = "0x" + "44" * 32
HASH_9 = "0x" + "09" * 32
HASH_10 = "0x" + "10" * 32
HASH_11 = "0x" + "11" * 32
HASH_12 = "0x" + "12" * 32


class _Response:
    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = json.dumps(payload)

    def json(self) -> Any:
        return self._payload

    def iter_lines(self, *, decode_unicode: bool) -> list[str]:
        assert decode_unicode is True
        if not isinstance(self._payload, list):
            return []
        return [json.dumps(line, separators=(",", ":")) for line in self._payload]


class _Session:
    def __init__(self, responses: list[_Response]) -> None:
        self.responses = responses
        self.calls: list[dict[str, Any]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> _Response:
        self.calls.append({"method": method, "url": url, **kwargs})
        if not self.responses:
            raise AssertionError("unexpected request")
        return self.responses.pop(0)


def _block(
    number: int, block_hash: str, parent_hash: str, logs: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    payload: dict[str, Any] = {"header": {"number": number, "hash": block_hash, "parentHash": parent_hash}}
    if logs is not None:
        payload["logs"] = logs
    return payload


def test_finalized_log_identities_follow_portal_cursor_and_parent_anchor() -> None:
    first = _Response(200, [_block(10, HASH_10, HASH_9)])
    second = _Response(
        200,
        [
            _block(
                11,
                HASH_11,
                HASH_10,
                [
                    {
                        "logIndex": 7,
                        "transactionIndex": 2,
                        "transactionHash": TX_HASH,
                        "address": ADDRESS,
                        "topics": [TOPIC],
                    }
                ],
            ),
            _block(12, HASH_12, HASH_11),
        ],
    )
    session = _Session([first, second])
    client = SqdPortalClient(
        "https://portal.example/datasets/ethereum-mainnet",
        session=cast(requests.Session, session),
    )

    events, stats = client.finalized_log_identities(
        addresses=[ADDRESS],
        topics=[TOPIC],
        from_block=10,
        to_block=12,
    )

    assert events == [
        {
            "block_number": 11,
            "block_hash": HASH_11,
            "transaction_hash": TX_HASH,
            "transaction_index": 2,
            "log_index": 7,
            "contract_address": ADDRESS,
            "topic0": TOPIC,
        }
    ]
    assert stats["page_count"] == 2
    assert stats["header_count"] == 3
    assert session.calls[0]["json"]["fromBlock"] == 10
    assert "parentBlockHash" not in session.calls[0]["json"]
    assert session.calls[1]["json"]["fromBlock"] == 11
    assert session.calls[1]["json"]["parentBlockHash"] == HASH_10


def test_finalized_log_identities_reject_log_outside_filter() -> None:
    response = _Response(
        200,
        [
            _block(
                10,
                HASH_10,
                HASH_9,
                [
                    {
                        "logIndex": 0,
                        "transactionIndex": 0,
                        "transactionHash": TX_HASH,
                        "address": OTHER_ADDRESS,
                        "topics": [TOPIC],
                    }
                ],
            )
        ],
    )
    client = SqdPortalClient(
        "https://portal.example/datasets/ethereum-mainnet",
        session=cast(requests.Session, _Session([response])),
    )

    with pytest.raises(SqdPortalError, match="outside the frozen filter"):
        client.finalized_log_identities(
            addresses=[ADDRESS],
            topics=[TOPIC],
            from_block=10,
            to_block=10,
        )


def test_finalized_log_identities_can_retain_topics_and_timestamp() -> None:
    response = _Response(
        200,
        [
            {
                "header": {
                    "number": 10,
                    "hash": HASH_10,
                    "parentHash": HASH_9,
                    "timestamp": 1234,
                },
                "logs": [
                    {
                        "logIndex": 0,
                        "transactionIndex": 0,
                        "transactionHash": TX_HASH,
                        "address": ADDRESS,
                        "topics": [TOPIC, TOPIC_1],
                    }
                ],
            }
        ],
    )
    session = _Session([response])
    client = SqdPortalClient(
        "https://portal.example/datasets/ethereum-mainnet",
        session=cast(requests.Session, session),
    )

    events, _ = client.finalized_log_identities(
        addresses=[ADDRESS],
        topics=[TOPIC],
        from_block=10,
        to_block=10,
        include_topics=True,
        include_block_timestamp=True,
    )

    assert events[0]["topics"] == [TOPIC, TOPIC_1]
    assert events[0]["block_timestamp"] == 1234
    assert session.calls[0]["json"]["fields"]["block"]["timestamp"] is True


def test_portal_retries_overload_status(monkeypatch: pytest.MonkeyPatch) -> None:
    session = _Session(
        [
            _Response(529, {"error": {"code": "overloaded"}}),
            _Response(200, {"dataset": "ethereum-mainnet", "start_block": 0}),
        ]
    )
    monkeypatch.setattr("ecomd.data.sqd_portal.time.sleep", lambda _: None)
    client = SqdPortalClient(
        "https://portal.example/datasets/ethereum-mainnet",
        retry_attempts=1,
        session=cast(requests.Session, session),
    )

    assert client.metadata()["dataset"] == "ethereum-mainnet"
    assert client.request_count == 2
    assert client.retry_count == 1


def test_finalized_block_header_requires_exact_requested_block() -> None:
    response = _Response(
        200,
        [
            {
                "header": {
                    "number": 12,
                    "hash": HASH_12,
                    "parentHash": HASH_11,
                    "timestamp": 1234,
                }
            }
        ],
    )
    session = _Session([response])
    client = SqdPortalClient(
        "https://portal.example/datasets/ethereum-mainnet",
        session=cast(requests.Session, session),
    )

    assert client.finalized_block_header(12) == {
        "number": 12,
        "hash": HASH_12,
        "parentHash": HASH_11,
        "timestamp": 1234,
    }
    assert session.calls[0]["json"]["includeAllBlocks"] is True
