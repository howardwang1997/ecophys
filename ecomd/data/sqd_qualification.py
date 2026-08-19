"""Target-free qualification utilities for SQD EVM block streams."""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class BlockWindow:
    """Inclusive block interval selected without inspecting protocol events."""

    label: str
    first: int
    last: int


@dataclass(frozen=True)
class HttpRecord:
    """Auditable response metadata for one Portal request."""

    status_code: int
    latency_seconds: float
    attempts: int
    body_sha256: str
    payload: Any


def canonical_sha256(value: Any) -> str:
    """Hash a JSON-compatible value using a stable serialization."""

    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def parse_stream_payload(text: str) -> list[dict[str, Any]]:
    """Parse either a JSON array or SQD's newline-delimited block response."""

    stripped = text.strip()
    if not stripped:
        return []
    try:
        decoded = json.loads(stripped)
    except json.JSONDecodeError:
        decoded = [json.loads(line) for line in stripped.splitlines() if line.strip()]
    if isinstance(decoded, Mapping):
        decoded = [decoded]
    if not isinstance(decoded, list) or not all(isinstance(item, Mapping) for item in decoded):
        raise ValueError("SQD stream response must contain JSON block objects")
    return [dict(item) for item in decoded]


def select_block_windows(
    start_block: int,
    finalized_block: int,
    *,
    fractions: Sequence[float],
    width: int,
    near_head_lag: int,
) -> list[BlockWindow]:
    """Select deterministic historical and near-head windows from header bounds."""

    if start_block < 0 or finalized_block < start_block:
        raise ValueError("invalid dataset block bounds")
    if width <= 1:
        raise ValueError("window width must exceed one to test parent continuity")
    if near_head_lag < 0:
        raise ValueError("near-head lag must be nonnegative")
    span = finalized_block - start_block + 1
    if span < width:
        raise ValueError("dataset is shorter than the requested window")

    latest_first = finalized_block - width + 1
    candidates: list[tuple[str, int]] = []
    for fraction in fractions:
        if not 0.0 <= fraction <= 1.0:
            raise ValueError("sample fractions must be in [0, 1]")
        first = start_block + int(fraction * (span - width))
        candidates.append((f"fraction_{fraction:.3f}", first))
    candidates.append(("near_finalized", max(start_block, latest_first - near_head_lag)))

    windows: list[BlockWindow] = []
    occupied: set[tuple[int, int]] = set()
    for label, first in candidates:
        first = min(max(first, start_block), latest_first)
        interval = (first, first + width - 1)
        if interval in occupied:
            continue
        occupied.add(interval)
        windows.append(BlockWindow(label=label, first=interval[0], last=interval[1]))
    return windows


def validate_block_window(
    records: Sequence[Mapping[str, Any]], window: BlockWindow
) -> dict[str, Any]:
    """Validate complete numbering, unique hashes, and adjacent parent links."""

    headers = [record.get("header") for record in records]
    header_objects = [header for header in headers if isinstance(header, Mapping)]
    numbers = [header.get("number") for header in header_objects]
    hashes = [header.get("hash") for header in header_objects]
    parent_hashes = [header.get("parentHash") for header in header_objects]
    expected = list(range(window.first, window.last + 1))
    numbers_exact = numbers == expected
    hashes_valid = all(
        isinstance(value, str) and value.startswith("0x") and len(value) == 66
        for value in hashes
    )
    hashes_unique = len(set(hashes)) == len(hashes)
    parent_links_exact = all(parent_hashes[index] == hashes[index - 1] for index in range(1, len(hashes)))
    timestamps = [header.get("timestamp") for header in header_objects]
    timestamps_nondecreasing = all(
        isinstance(value, int) for value in timestamps
    ) and all(timestamps[index] >= timestamps[index - 1] for index in range(1, len(timestamps)))
    no_event_rows = all(
        not record.get(key)
        for record in records
        for key in ("logs", "transactions", "traces", "stateDiffs")
    )
    checks = {
        "record_count_exact": len(records) == len(expected),
        "headers_present": len(header_objects) == len(records),
        "numbers_exact": numbers_exact,
        "hashes_valid": hashes_valid,
        "hashes_unique": hashes_unique,
        "parent_links_exact": parent_links_exact,
        "timestamps_nondecreasing": timestamps_nondecreasing,
        "no_event_rows": no_event_rows,
    }
    return {
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "numbers": numbers,
        "hashes": hashes,
        "parent_hashes": parent_hashes,
        "timestamps": timestamps,
        "canonical_sha256": canonical_sha256(records),
    }


class SqdPortalClient:
    """Small retrying client limited to metadata, heads, and header-only streams."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout_seconds: float,
        max_attempts: int,
        retry_statuses: Iterable[int] = (429, 500, 502, 503, 529),
        session: requests.Session | None = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout must be positive")
        if max_attempts <= 0:
            raise ValueError("max attempts must be positive")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts
        self.retry_statuses = frozenset(retry_statuses)
        self.session = session or requests.Session()

    def _request(self, method: str, url: str, **kwargs: Any) -> tuple[requests.Response, int, float]:
        last_error: BaseException | None = None
        headers = {"Accept-Encoding": "identity", **kwargs.pop("headers", {})}
        for attempt in range(1, self.max_attempts + 1):
            started = time.perf_counter()
            try:
                response = self.session.request(
                    method,
                    url,
                    timeout=self.timeout_seconds,
                    headers=headers,
                    **kwargs,
                )
                latency = time.perf_counter() - started
                if response.status_code not in self.retry_statuses:
                    response.raise_for_status()
                    return response, attempt, latency
                last_error = requests.HTTPError(f"retryable status {response.status_code}")
            except requests.RequestException as error:
                latency = time.perf_counter() - started
                last_error = error
            if attempt < self.max_attempts:
                time.sleep(min(2.0 ** (attempt - 1), 4.0))
        raise RuntimeError(f"SQD request failed after {self.max_attempts} attempts") from last_error

    def get_json(self, dataset: str, endpoint: str) -> HttpRecord:
        """Read one public JSON metadata or head endpoint."""

        url = f"{self.base_url}/datasets/{dataset}/{endpoint.lstrip('/')}"
        response, attempts, latency = self._request("GET", url)
        return HttpRecord(
            status_code=response.status_code,
            latency_seconds=latency,
            attempts=attempts,
            body_sha256=hashlib.sha256(response.content).hexdigest(),
            payload=response.json(),
        )

    def get_finalized_headers(self, dataset: str, window: BlockWindow) -> HttpRecord:
        """Request only block headers; event collections are forbidden by construction."""

        url = f"{self.base_url}/datasets/{dataset}/finalized-stream"
        body = {
            "type": "evm",
            "fromBlock": window.first,
            "toBlock": window.last,
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
        response, attempts, latency = self._request(
            "POST", url, headers={"Content-Type": "application/json"}, json=body
        )
        return HttpRecord(
            status_code=response.status_code,
            latency_seconds=latency,
            attempts=attempts,
            body_sha256=hashlib.sha256(response.content).hexdigest(),
            payload=parse_stream_payload(response.text),
        )
