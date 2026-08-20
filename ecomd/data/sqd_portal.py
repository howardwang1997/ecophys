"""Strict client for finalized EVM log identities from an SQD Portal dataset."""

from __future__ import annotations

import json
import time
from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import urlparse

import requests


class SqdPortalError(RuntimeError):
    """Raised when an SQD Portal response cannot witness a frozen log interval."""


class SqdPortalClient:
    """Read finalized, filtered EVM blocks while preserving Portal cursor semantics."""

    def __init__(
        self,
        url: str,
        *,
        timeout_seconds: float = 60.0,
        retry_attempts: int = 4,
        retry_backoff_seconds: float = 1.0,
        session: requests.Session | None = None,
    ) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("SQD Portal dataset URL must be absolute HTTPS")
        if timeout_seconds <= 0:
            raise ValueError("SQD Portal timeout must be positive")
        if retry_attempts < 0 or retry_backoff_seconds < 0:
            raise ValueError("SQD Portal retry settings cannot be negative")
        self.url = url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.retry_attempts = retry_attempts
        self.retry_backoff_seconds = retry_backoff_seconds
        self.session = session or requests.Session()
        self.request_count = 0
        self.retry_count = 0
        self.bytes_received = 0

    def metadata(self) -> dict[str, Any]:
        """Return and minimally validate the dataset metadata document."""
        payload = self._get_json("metadata")
        if not isinstance(payload.get("dataset"), str):
            raise SqdPortalError("SQD Portal metadata has no dataset name")
        if not isinstance(payload.get("start_block"), int):
            raise SqdPortalError("SQD Portal metadata has no integer start block")
        return payload

    def finalized_head(self) -> dict[str, Any]:
        """Return a canonical finalized-head reference."""
        payload = self._get_json("finalized-head")
        number = payload.get("number")
        block_hash = payload.get("hash")
        if not isinstance(number, int) or number < 0:
            raise SqdPortalError("SQD Portal finalized head has an invalid number")
        if not _is_hash(block_hash):
            raise SqdPortalError("SQD Portal finalized head has an invalid hash")
        return {"number": number, "hash": str(block_hash).lower()}

    def finalized_block_header(self, block_number: int) -> dict[str, Any]:
        """Return one finalized block header, including its timestamp."""
        if block_number < 0:
            raise ValueError("SQD Portal block number cannot be negative")
        blocks = self._post_finalized_stream(
            {
                "type": "evm",
                "fromBlock": block_number,
                "toBlock": block_number,
                "includeAllBlocks": True,
                "fields": {
                    "block": {
                        "number": True,
                        "hash": True,
                        "parentHash": True,
                        "timestamp": True,
                    }
                },
            }
        )
        if len(blocks) != 1 or not isinstance(blocks[0].get("header"), Mapping):
            raise SqdPortalError("SQD Portal did not return exactly one requested block header")
        header = blocks[0]["header"]
        number = header.get("number")
        block_hash = header.get("hash")
        parent_hash = header.get("parentHash")
        timestamp = header.get("timestamp")
        if number != block_number or not isinstance(timestamp, int) or timestamp < 0:
            raise SqdPortalError("SQD Portal returned an invalid requested block header")
        return {
            "number": number,
            "hash": _normalize_hash(block_hash, label="block hash"),
            "parentHash": _normalize_hash(parent_hash, label="parent block hash"),
            "timestamp": timestamp,
        }

    def finalized_log_identities(
        self,
        *,
        addresses: Sequence[str],
        topics: Sequence[str],
        from_block: int,
        to_block: int,
    ) -> tuple[list[dict[str, Any]], dict[str, int]]:
        """Return sanitized log identity fields for one finalized inclusive interval."""
        if from_block < 0 or to_block < from_block:
            raise ValueError("SQD Portal block interval is invalid")
        normalized_addresses = {_normalize_address(value) for value in addresses}
        normalized_topics = {_normalize_hash(value, label="topic") for value in topics}
        if not normalized_addresses or not normalized_topics:
            raise ValueError("SQD Portal log filters cannot be empty")

        events: list[dict[str, Any]] = []
        seen: set[tuple[str, str, int, str, str]] = set()
        current = from_block
        parent_block_hash: str | None = None
        page_count = 0
        header_count = 0
        started_requests = self.request_count
        started_retries = self.retry_count
        started_bytes = self.bytes_received

        while current <= to_block:
            query: dict[str, Any] = {
                "type": "evm",
                "fromBlock": current,
                "toBlock": to_block,
                "fields": {
                    "block": {"number": True, "hash": True, "parentHash": True},
                    "log": {
                        "logIndex": True,
                        "transactionIndex": True,
                        "transactionHash": True,
                        "address": True,
                        "topics": True,
                    },
                },
                "logs": [
                    {
                        "address": sorted(normalized_addresses),
                        "topic0": sorted(normalized_topics),
                    }
                ],
            }
            if parent_block_hash is not None:
                query["parentBlockHash"] = parent_block_hash
            blocks = self._post_finalized_stream(query)
            page_count += 1
            if not blocks:
                raise SqdPortalError("SQD Portal returned an empty page before the frozen interval ended")

            previous_number: int | None = None
            previous_hash: str | None = None
            for raw_block in blocks:
                header = raw_block.get("header")
                if not isinstance(header, Mapping):
                    raise SqdPortalError("SQD Portal block has no header object")
                number = header.get("number")
                block_hash = header.get("hash")
                parent_hash = header.get("parentHash")
                if not isinstance(number, int) or not current <= number <= to_block:
                    raise SqdPortalError("SQD Portal block number is outside the requested page")
                if not _is_hash(block_hash) or not _is_hash(parent_hash):
                    raise SqdPortalError("SQD Portal block has an invalid hash")
                normalized_block_hash = str(block_hash).lower()
                normalized_parent_hash = str(parent_hash).lower()
                if previous_number is not None and number <= previous_number:
                    raise SqdPortalError("SQD Portal block numbers are not strictly increasing")
                if (
                    previous_number is not None
                    and number == previous_number + 1
                    and normalized_parent_hash != previous_hash
                ):
                    raise SqdPortalError("SQD Portal consecutive headers do not link")
                if (
                    parent_block_hash is not None
                    and number == current
                    and normalized_parent_hash != parent_block_hash
                ):
                    raise SqdPortalError("SQD Portal page does not extend its parent-block anchor")

                raw_logs = raw_block.get("logs", [])
                if not isinstance(raw_logs, list):
                    raise SqdPortalError("SQD Portal block logs are not a list")
                for raw_log in raw_logs:
                    event = _sanitize_log(
                        raw_log,
                        block_number=number,
                        block_hash=normalized_block_hash,
                        allowed_addresses=normalized_addresses,
                        allowed_topics=normalized_topics,
                    )
                    identity = (
                        str(event["block_hash"]),
                        str(event["transaction_hash"]),
                        int(event["log_index"]),
                        str(event["contract_address"]),
                        str(event["topic0"]),
                    )
                    if identity in seen:
                        raise SqdPortalError("SQD Portal returned a duplicate canonical log identity")
                    seen.add(identity)
                    events.append(event)

                previous_number = number
                previous_hash = normalized_block_hash
                header_count += 1

            if previous_number is None or previous_hash is None:
                raise SqdPortalError("SQD Portal page made no cursor progress")
            current = previous_number + 1
            parent_block_hash = previous_hash

        events.sort(
            key=lambda event: (
                int(event["block_number"]),
                int(event["transaction_index"]),
                int(event["log_index"]),
            )
        )
        return events, {
            "page_count": page_count,
            "header_count": header_count,
            "request_count": self.request_count - started_requests,
            "retry_count": self.retry_count - started_retries,
            "bytes_received": self.bytes_received - started_bytes,
        }

    def _get_json(self, path: str) -> dict[str, Any]:
        response = self._request("GET", f"{self.url}/{path}")
        try:
            payload = response.json()
        except requests.JSONDecodeError as error:
            raise SqdPortalError(f"SQD Portal {path} response is not JSON") from error
        if not isinstance(payload, dict):
            raise SqdPortalError(f"SQD Portal {path} response is not an object")
        return payload

    def _post_finalized_stream(self, query: Mapping[str, Any]) -> list[dict[str, Any]]:
        response = self._request(
            "POST",
            f"{self.url}/finalized-stream",
            json_body=query,
        )
        blocks: list[dict[str, Any]] = []
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
            self.bytes_received += len(line.encode("utf-8"))
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as error:
                raise SqdPortalError("SQD Portal stream contains invalid JSON") from error
            if not isinstance(payload, dict):
                raise SqdPortalError("SQD Portal stream line is not an object")
            blocks.append(payload)
        return blocks

    def _request(
        self,
        method: str,
        url: str,
        *,
        json_body: Mapping[str, Any] | None = None,
    ) -> requests.Response:
        last_error: Exception | None = None
        for attempt in range(self.retry_attempts + 1):
            self.request_count += 1
            try:
                response = self.session.request(
                    method,
                    url,
                    json=json_body,
                    stream=method == "POST",
                    timeout=self.timeout_seconds,
                    headers={"User-Agent": "EcoPhys-Liquity-D0/1"},
                )
            except requests.RequestException as error:
                last_error = error
            else:
                if response.status_code == 200:
                    return response
                last_error = SqdPortalError(f"SQD Portal HTTP {response.status_code}: {response.text[:500]}")
                if response.status_code not in {408, 425, 429, 500, 502, 503, 504, 529}:
                    raise last_error
            if attempt == self.retry_attempts:
                break
            self.retry_count += 1
            time.sleep(self.retry_backoff_seconds * 2**attempt)
        raise SqdPortalError("SQD Portal request exhausted retries") from last_error


def _sanitize_log(
    raw_log: Any,
    *,
    block_number: int,
    block_hash: str,
    allowed_addresses: set[str],
    allowed_topics: set[str],
) -> dict[str, Any]:
    if not isinstance(raw_log, Mapping):
        raise SqdPortalError("SQD Portal log is not an object")
    log_index = raw_log.get("logIndex")
    transaction_index = raw_log.get("transactionIndex")
    if not isinstance(log_index, int) or log_index < 0:
        raise SqdPortalError("SQD Portal logIndex is invalid")
    if not isinstance(transaction_index, int) or transaction_index < 0:
        raise SqdPortalError("SQD Portal transactionIndex is invalid")
    transaction_hash = _normalize_hash(raw_log.get("transactionHash"), label="transaction hash")
    address = _normalize_address(raw_log.get("address"))
    raw_topics = raw_log.get("topics")
    if not isinstance(raw_topics, list) or not raw_topics:
        raise SqdPortalError("SQD Portal log topics are invalid")
    topic0 = _normalize_hash(raw_topics[0], label="topic0")
    if address not in allowed_addresses or topic0 not in allowed_topics:
        raise SqdPortalError("SQD Portal returned a log outside the frozen filter")
    return {
        "block_number": block_number,
        "block_hash": block_hash,
        "transaction_hash": transaction_hash,
        "transaction_index": transaction_index,
        "log_index": log_index,
        "contract_address": address,
        "topic0": topic0,
    }


def _normalize_address(value: Any) -> str:
    text = str(value).lower()
    if len(text) != 42 or not text.startswith("0x"):
        raise SqdPortalError(f"invalid EVM address: {value}")
    try:
        bytes.fromhex(text[2:])
    except ValueError as error:
        raise SqdPortalError(f"invalid EVM address: {value}") from error
    return text


def _normalize_hash(value: Any, *, label: str) -> str:
    text = str(value).lower()
    if not _is_hash(text):
        raise SqdPortalError(f"invalid EVM {label}: {value}")
    return text


def _is_hash(value: Any) -> bool:
    text = str(value)
    if len(text) != 66 or not text.startswith("0x"):
        return False
    try:
        bytes.fromhex(text[2:])
    except ValueError:
        return False
    return True
