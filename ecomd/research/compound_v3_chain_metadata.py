"""Chain-metadata-only conformance audit for Compound III mainnet markets."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import requests
import yaml

MANIFEST_SCHEMA_VERSION = "ecophys-compound-v3-chain-metadata-preflight/v1"
ARTIFACT_SCHEMA_VERSION = "ecophys-compound-v3-chain-metadata-audit/v1"
STAGE = "chain_deployment_metadata_only"
IMPLEMENTATION_SLOT = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
ADMIN_SLOT = "0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103"
GETTER_CONTRACT = {
    "base_token": {"selector": "0xc55dae63", "return_type": "address"},
    "governor": {"selector": "0x0c340a24", "return_type": "address"},
    "pause_guardian": {"selector": "0x24a3d622", "return_type": "address"},
    "num_assets": {"selector": "0xa46fe83b", "return_type": "uint"},
}
ALLOWED_METHODS = frozenset(
    {"eth_chainId", "eth_getBlockByNumber", "eth_getCode", "eth_getStorageAt", "eth_call"}
)
EXPECTED_METHOD_COUNTS = {
    "eth_call": 24,
    "eth_chainId": 1,
    "eth_getBlockByNumber": 2,
    "eth_getCode": 18,
    "eth_getStorageAt": 16,
}
REQUIRED_GATES = frozenset(
    {
        "access_boundary",
        "chain_id",
        "configurator_proxy",
        "current_admin_slots",
        "current_getters",
        "current_implementation_code",
        "current_proxy_code",
        "finalized_header",
        "historical_archive_state",
        "historical_header",
        "request_caps",
        "source_artifact",
    }
)
ACCESS_FLAGS = frozenset(
    {
        "account_balance_calls_used",
        "account_mapping_storage_used",
        "chain_rpc_used",
        "eth_get_logs_used",
        "external_workers_used",
        "gpu_used",
        "governance_transaction_or_receipt_used",
        "paid_data_used",
        "participant_action_rows_opened",
        "price_or_oracle_calls_used",
        "raw_rpc_payloads_retained",
        "realized_response_rows_opened",
    }
)
TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "audit_id",
        "as_of",
        "stage",
        "access_boundary",
        "source_result",
        "rpc",
        "proxy_slots",
        "getters",
        "markets",
        "configurator",
        "archive_check",
        "gates",
        "decision_policy",
        "limitations",
    }
)
SOURCE_RESULT_KEYS = frozenset({"path", "sha256", "source_commit"})
RPC_KEYS = frozenset(
    {
        "url",
        "documentation_url",
        "user_agent",
        "maximum_requests_per_second",
        "maximum_transport_retries",
        "maximum_http_attempts",
        "maximum_response_bytes",
        "allowed_methods",
        "snapshot_block_tag",
    }
)
MARKET_KEYS = frozenset(
    {
        "market_id",
        "proxy",
        "expected_base_token",
        "expected_governor",
        "expected_pause_guardian",
    }
)
CONFIGURATOR_KEYS = frozenset({"proxy"})
ARCHIVE_KEYS = frozenset({"block_number", "market_ids"})
DECISION_KEYS = frozenset({"all_gates_required", "pass", "fail", "authorized_next_stage"})
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
GIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ADDRESS_PATTERN = re.compile(r"^0x[0-9a-fA-F]{40}$")
SELECTOR_PATTERN = re.compile(r"^0x[0-9a-f]{8}$")
HASH_PATTERN = re.compile(r"^0x[0-9a-fA-F]{64}$")


def canonical_json_sha256(value: object) -> str:
    """Return the project-stable SHA-256 of a JSON-safe value."""

    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_chain_metadata_preflight(path: str | Path) -> dict[str, object]:
    """Load the frozen chain-metadata manifest."""

    raw: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("chain-metadata preflight root must be a mapping")
    return cast(dict[str, object], raw)


def _mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _mapping_list(value: object) -> list[Mapping[str, object]] | None:
    if not isinstance(value, list):
        return None
    result: list[Mapping[str, object]] = []
    for item in value:
        mapped = _mapping(item)
        if mapped is None:
            return None
        result.append(mapped)
    return result


def _string(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _string_list(value: object, *, path: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not value or any(_string(item) is None for item in value):
        errors.append(f"{path} must be a non-empty list of strings")
        return []
    return [cast(str, item).strip() for item in value]


def normalize_address(value: object, *, path: str) -> str:
    """Validate and normalize an EVM address."""

    if not isinstance(value, str) or ADDRESS_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{path} must be a 20-byte hexadecimal address")
    return value.lower()


def _validate_address(value: object, *, path: str, errors: list[str]) -> None:
    try:
        normalize_address(value, path=path)
    except ValueError as exc:
        errors.append(str(exc))


def validate_chain_metadata_preflight(manifest: Mapping[str, object]) -> list[str]:
    """Return deterministic structural and forbidden-access violations."""

    errors: list[str] = []
    if set(manifest) != TOP_LEVEL_KEYS:
        errors.append(f"top level must contain exactly {sorted(TOP_LEVEL_KEYS)}")
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        errors.append(f"schema_version must equal {MANIFEST_SCHEMA_VERSION}")
    audit_id = _string(manifest.get("audit_id"))
    if audit_id is None or ID_PATTERN.fullmatch(audit_id) is None:
        errors.append("audit_id must be a stable lowercase identifier")
    as_of = _string(manifest.get("as_of"))
    if as_of is None or DATE_PATTERN.fullmatch(as_of) is None:
        errors.append("as_of must be an ISO date")
    if manifest.get("stage") != STAGE:
        errors.append(f"stage must equal {STAGE}")

    boundary = _mapping(manifest.get("access_boundary"))
    if boundary is None or set(boundary) != ACCESS_FLAGS:
        errors.append(f"access_boundary must contain exactly {sorted(ACCESS_FLAGS)}")
        boundary = {}
    for flag in ACCESS_FLAGS - {"chain_rpc_used"}:
        if boundary.get(flag) is not False:
            errors.append(f"access_boundary.{flag} must be false")
    if boundary.get("chain_rpc_used") is not True:
        errors.append("access_boundary.chain_rpc_used must be true and disclosed")

    source = _mapping(manifest.get("source_result"))
    if source is None or set(source) != SOURCE_RESULT_KEYS:
        errors.append(f"source_result must contain exactly {sorted(SOURCE_RESULT_KEYS)}")
        source = {}
    path = _string(source.get("path"))
    if path is None or Path(path).is_absolute() or ".." in Path(path).parts:
        errors.append("source_result.path must be a normalized relative path")
    source_hash = _string(source.get("sha256"))
    if source_hash is None or SHA256_PATTERN.fullmatch(source_hash) is None:
        errors.append("source_result.sha256 must be a lowercase SHA-256")
    source_commit = _string(source.get("source_commit"))
    if source_commit is None or GIT_SHA_PATTERN.fullmatch(source_commit) is None:
        errors.append("source_result.source_commit must be a full lowercase Git SHA")

    rpc = _mapping(manifest.get("rpc"))
    if rpc is None or set(rpc) != RPC_KEYS:
        errors.append(f"rpc must contain exactly {sorted(RPC_KEYS)}")
        rpc = {}
    if rpc.get("url") != "https://eth.blockscout.com/api/eth-rpc":
        errors.append("rpc.url must equal the frozen no-key Ethereum endpoint")
    if rpc.get("documentation_url") != "https://docs.blockscout.com/devs/apis/rpc/eth-rpc":
        errors.append("rpc.documentation_url must equal the frozen provider documentation")
    if _string(rpc.get("user_agent")) is None:
        errors.append("rpc.user_agent must be non-empty")
    rate = rpc.get("maximum_requests_per_second")
    if not isinstance(rate, (int, float)) or isinstance(rate, bool) or not (0 < float(rate) <= 2):
        errors.append("rpc.maximum_requests_per_second must be in (0, 2]")
    for key, minimum, maximum in (
        ("maximum_transport_retries", 0, 2),
        ("maximum_http_attempts", 61, 80),
        ("maximum_response_bytes", 1, 8 * 1024 * 1024),
    ):
        value = rpc.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or not (minimum <= value <= maximum):
            errors.append(f"rpc.{key} must be an integer in [{minimum}, {maximum}]")
    allowed_methods = set(_string_list(rpc.get("allowed_methods"), path="rpc.allowed_methods", errors=errors))
    if allowed_methods != ALLOWED_METHODS:
        errors.append(f"rpc.allowed_methods must equal {sorted(ALLOWED_METHODS)}")
    if rpc.get("snapshot_block_tag") != "finalized":
        errors.append("rpc.snapshot_block_tag must equal finalized")

    slots = _mapping(manifest.get("proxy_slots"))
    if slots is None or set(slots) != {"implementation", "admin"}:
        errors.append("proxy_slots must contain exactly implementation and admin")
        slots = {}
    if slots.get("implementation") != IMPLEMENTATION_SLOT:
        errors.append("proxy_slots.implementation must equal ERC-1967")
    if slots.get("admin") != ADMIN_SLOT:
        errors.append("proxy_slots.admin must equal ERC-1967")

    getters = _mapping(manifest.get("getters"))
    if getters is None or set(getters) != set(GETTER_CONTRACT):
        errors.append(f"getters must contain exactly {sorted(GETTER_CONTRACT)}")
        getters = {}
    for getter_id, expected in GETTER_CONTRACT.items():
        getter = _mapping(getters.get(getter_id))
        if getter is None or set(getter) != {"selector", "return_type"}:
            errors.append(f"getters.{getter_id} must contain selector and return_type")
            continue
        selector = _string(getter.get("selector"))
        if selector is None or SELECTOR_PATTERN.fullmatch(selector) is None:
            errors.append(f"getters.{getter_id}.selector must be four lowercase bytes")
        if dict(getter) != expected:
            errors.append(f"getters.{getter_id} must equal the frozen selector contract")

    markets = _mapping_list(manifest.get("markets"))
    if not markets or len(markets) != 6:
        errors.append("markets must contain exactly six mappings")
        markets = []
    market_ids: set[str] = set()
    proxies: set[str] = set()
    for index, market in enumerate(markets):
        market_path = f"markets[{index}]"
        if set(market) != MARKET_KEYS:
            errors.append(f"{market_path} must contain exactly {sorted(MARKET_KEYS)}")
        market_id = _string(market.get("market_id"))
        if market_id is None or ID_PATTERN.fullmatch(market_id) is None or market_id in market_ids:
            errors.append(f"{market_path}.market_id must be unique and stable")
        else:
            market_ids.add(market_id)
        for key in ("proxy", "expected_base_token", "expected_governor", "expected_pause_guardian"):
            _validate_address(market.get(key), path=f"{market_path}.{key}", errors=errors)
        proxy = _string(market.get("proxy"))
        if proxy is not None:
            lowered = proxy.lower()
            if lowered in proxies:
                errors.append(f"{market_path}.proxy must be unique")
            proxies.add(lowered)

    configurator = _mapping(manifest.get("configurator"))
    if configurator is None or set(configurator) != CONFIGURATOR_KEYS:
        errors.append(f"configurator must contain exactly {sorted(CONFIGURATOR_KEYS)}")
        configurator = {}
    _validate_address(configurator.get("proxy"), path="configurator.proxy", errors=errors)

    archive = _mapping(manifest.get("archive_check"))
    if archive is None or set(archive) != ARCHIVE_KEYS:
        errors.append(f"archive_check must contain exactly {sorted(ARCHIVE_KEYS)}")
        archive = {}
    if archive.get("block_number") != 17_000_000:
        errors.append("archive_check.block_number must equal 17000000")
    archive_ids = _string_list(archive.get("market_ids"), path="archive_check.market_ids", errors=errors)
    if archive_ids != ["mainnet_usdc", "mainnet_weth"]:
        errors.append("archive_check.market_ids must equal the frozen oldest-market pair")
    if not set(archive_ids).issubset(market_ids):
        errors.append("archive_check.market_ids must reference declared markets")

    gates = _string_list(manifest.get("gates"), path="gates", errors=errors)
    if set(gates) != REQUIRED_GATES or len(gates) != len(REQUIRED_GATES):
        errors.append(f"gates must contain exactly {sorted(REQUIRED_GATES)}")
    policy = _mapping(manifest.get("decision_policy"))
    if policy is None or set(policy) != DECISION_KEYS:
        errors.append(f"decision_policy must contain exactly {sorted(DECISION_KEYS)}")
        policy = {}
    if policy.get("all_gates_required") is not True:
        errors.append("decision_policy.all_gates_required must be true")
    for key in ("pass", "fail", "authorized_next_stage"):
        if _string(policy.get(key)) is None:
            errors.append(f"decision_policy.{key} must be non-empty")
    _string_list(manifest.get("limitations"), path="limitations", errors=errors)
    return sorted(errors)


def _hex_bytes(value: object, *, path: str) -> bytes:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"{path} must be 0x-prefixed hexadecimal bytes")
    body = value[2:]
    if len(body) % 2 or re.fullmatch(r"[0-9a-fA-F]*", body) is None:
        raise ValueError(f"{path} must contain complete hexadecimal bytes")
    return bytes.fromhex(body)


def decode_word_address(value: object, *, path: str) -> str:
    """Decode one canonical ABI or storage address word."""

    word = _hex_bytes(value, path=path)
    if len(word) != 32 or any(word[:12]):
        raise ValueError(f"{path} must be a canonical 32-byte address word")
    address = "0x" + word[12:].hex()
    if address == "0x" + "00" * 20:
        raise ValueError(f"{path} cannot contain the zero address")
    return address


def decode_word_uint(value: object, *, path: str) -> int:
    """Decode one canonical ABI unsigned-integer word."""

    word = _hex_bytes(value, path=path)
    if len(word) != 32:
        raise ValueError(f"{path} must be one 32-byte ABI word")
    return int.from_bytes(word, "big")


def _block_record(value: object, *, path: str) -> dict[str, object]:
    block = _mapping(value)
    if block is None:
        raise ValueError(f"{path} must be a block mapping")
    number = block.get("number")
    timestamp = block.get("timestamp")
    block_hash = block.get("hash")
    parent_hash = block.get("parentHash")
    if not isinstance(number, str) or not isinstance(timestamp, str):
        raise ValueError(f"{path} number and timestamp must be JSON-RPC quantities")
    if not isinstance(block_hash, str) or HASH_PATTERN.fullmatch(block_hash) is None:
        raise ValueError(f"{path}.hash must be a 32-byte hash")
    if not isinstance(parent_hash, str) or HASH_PATTERN.fullmatch(parent_hash) is None:
        raise ValueError(f"{path}.parentHash must be a 32-byte hash")
    number_int = int(number, 16)
    timestamp_int = int(timestamp, 16)
    return {
        "number": number_int,
        "number_hex": hex(number_int),
        "hash": block_hash.lower(),
        "parent_hash": parent_hash.lower(),
        "timestamp_unix": timestamp_int,
        "timestamp_utc": datetime.fromtimestamp(timestamp_int, UTC).isoformat().replace("+00:00", "Z"),
    }


def _code_record(value: object, *, path: str) -> dict[str, object]:
    code = _hex_bytes(value, path=path)
    return {"byte_count": len(code), "sha256": hashlib.sha256(code).hexdigest(), "nonempty": bool(code)}


class RpcCollector:
    """Capped JSON-RPC client retaining request/response hashes, not raw bodies."""

    def __init__(
        self,
        *,
        url: str,
        user_agent: str,
        maximum_requests_per_second: float,
        maximum_transport_retries: int,
        maximum_http_attempts: int,
        maximum_response_bytes: int,
    ) -> None:
        self._url = url
        self._minimum_interval = 1.0 / maximum_requests_per_second
        self._maximum_transport_retries = maximum_transport_retries
        self._maximum_http_attempts = maximum_http_attempts
        self._maximum_response_bytes = maximum_response_bytes
        self._last_start: float | None = None
        self._next_id = 1
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})
        self.http_attempts = 0
        self.response_bytes = 0
        self.records: list[dict[str, object]] = []

    def call(self, label: str, method: str, params: Sequence[object]) -> object:
        """Call one frozen method within all transport caps."""

        if method not in ALLOWED_METHODS:
            raise ValueError(f"forbidden JSON-RPC method: {method}")
        request_id = self._next_id
        self._next_id += 1
        request = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": list(params)}
        prior_errors: list[str] = []
        for attempt in range(self._maximum_transport_retries + 1):
            if self.http_attempts >= self._maximum_http_attempts:
                raise RuntimeError("maximum HTTP-attempt cap reached")
            if self._last_start is not None:
                time.sleep(max(0.0, self._minimum_interval - (time.monotonic() - self._last_start)))
            self._last_start = time.monotonic()
            self.http_attempts += 1
            try:
                response = self._session.post(self._url, json=request, timeout=60.0)
                body = response.content
                self.response_bytes += len(body)
                if self.response_bytes > self._maximum_response_bytes:
                    raise RuntimeError("maximum response-byte cap exceeded")
                response.raise_for_status()
                envelope: object = response.json()
            except RuntimeError:
                raise
            except (requests.RequestException, ValueError) as exc:
                prior_errors.append(f"{type(exc).__name__}: {exc}")
            else:
                mapped = _mapping(envelope)
                if mapped is None:
                    prior_errors.append("RPC response is not a mapping")
                elif mapped.get("error") is not None:
                    prior_errors.append(f"RPC error: {mapped['error']}")
                elif "result" not in mapped or mapped.get("result") is None:
                    prior_errors.append("RPC result is missing or null")
                else:
                    result = mapped["result"]
                    self.records.append(
                        {
                            "request_index": len(self.records),
                            "label": label,
                            "method": method,
                            "params": list(params),
                            "request_sha256": canonical_json_sha256(request),
                            "response_sha256": canonical_json_sha256(mapped),
                            "result_sha256": canonical_json_sha256(result),
                            "response_byte_count": len(body),
                            "attempt_count": attempt + 1,
                            "prior_errors": list(prior_errors),
                            "retrieved_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                        }
                    )
                    return result
            if attempt < self._maximum_transport_retries:
                time.sleep(float(attempt + 1))
        raise RuntimeError(f"{label} failed after all attempts: {prior_errors}")


def _getter_record(
    rpc: RpcCollector,
    *,
    market_id: str,
    proxy: str,
    block_hex: str,
    getter_id: str,
    getter: Mapping[str, object],
) -> object:
    result = rpc.call(
        f"current.{market_id}.getter.{getter_id}",
        "eth_call",
        [{"to": proxy, "data": getter["selector"]}, block_hex],
    )
    if getter["return_type"] == "address":
        return decode_word_address(result, path=f"{market_id}.{getter_id}")
    return decode_word_uint(result, path=f"{market_id}.{getter_id}")


def evaluate_chain_metadata(
    manifest: Mapping[str, object],
    *,
    source_artifact_matches: bool,
    chain_id: object,
    finalized_block: Mapping[str, object],
    market_records: Sequence[Mapping[str, object]],
    configurator_record: Mapping[str, object],
    archive_block: Mapping[str, object],
    archive_records: Sequence[Mapping[str, object]],
    request_summary: Mapping[str, object],
) -> dict[str, bool]:
    """Evaluate the twelve frozen conjunctive gates from normalized metadata."""

    markets = cast(Sequence[Mapping[str, object]], manifest["markets"])
    expected_by_id = {cast(str, market["market_id"]): market for market in markets}
    current_proxy_code = len(market_records) == len(markets) and all(
        cast(Mapping[str, object], record["proxy_code"])["nonempty"] is True
        for record in market_records
    )
    current_implementation = len(market_records) == len(markets) and all(
        cast(Mapping[str, object], record["implementation_code"])["nonempty"] is True
        and isinstance(record["implementation"], str)
        for record in market_records
    )
    current_admin = len(market_records) == len(markets) and all(
        isinstance(record["admin"], str) for record in market_records
    )
    getters_ok = len(market_records) == len(markets)
    for record in market_records:
        market_id = cast(str, record["market_id"])
        expected = expected_by_id.get(market_id)
        if expected is None:
            getters_ok = False
            continue
        getters = cast(Mapping[str, object], record["getters"])
        getters_ok = getters_ok and (
            getters.get("base_token") == normalize_address(expected["expected_base_token"], path="base")
            and getters.get("governor") == normalize_address(expected["expected_governor"], path="governor")
            and getters.get("pause_guardian")
            == normalize_address(expected["expected_pause_guardian"], path="pause_guardian")
            and isinstance(getters.get("num_assets"), int)
            and 1 <= cast(int, getters["num_assets"]) <= 24
        )
    configurator_ok = (
        cast(Mapping[str, object], configurator_record["proxy_code"])["nonempty"] is True
        and cast(Mapping[str, object], configurator_record["implementation_code"])["nonempty"] is True
        and isinstance(configurator_record["implementation"], str)
        and isinstance(configurator_record["admin"], str)
    )
    current_by_id = {cast(str, record["market_id"]): record for record in market_records}
    archive_ok = len(archive_records) == 2
    for record in archive_records:
        market_id = cast(str, record["market_id"])
        current = current_by_id.get(market_id)
        archive_ok = archive_ok and current is not None
        if current is None:
            continue
        archive_ok = archive_ok and (
            cast(Mapping[str, object], record["proxy_code"])["nonempty"] is True
            and record["proxy_code"] == current["proxy_code"]
            and cast(Mapping[str, object], record["implementation_code"])["nonempty"] is True
            and isinstance(record["implementation"], str)
        )
    rpc = cast(Mapping[str, object], manifest["rpc"])
    request_caps = (
        isinstance(request_summary.get("successful_request_count"), int)
        and request_summary["successful_request_count"] == 61
        and cast(int, request_summary["http_attempt_count"]) <= cast(int, rpc["maximum_http_attempts"])
        and cast(int, request_summary["response_byte_count"]) <= cast(int, rpc["maximum_response_bytes"])
        and request_summary["method_counts"] == EXPECTED_METHOD_COUNTS
    )
    boundary = cast(Mapping[str, object], manifest["access_boundary"])
    access_ok = boundary.get("chain_rpc_used") is True and all(
        value is False for key, value in boundary.items() if key != "chain_rpc_used"
    )
    return {
        "source_artifact": source_artifact_matches,
        "chain_id": chain_id == "0x1",
        "finalized_header": cast(int, finalized_block.get("number", 0)) > 17_000_000,
        "current_proxy_code": current_proxy_code,
        "current_implementation_code": current_implementation,
        "current_admin_slots": current_admin,
        "current_getters": getters_ok,
        "configurator_proxy": configurator_ok,
        "historical_header": archive_block.get("number") == 17_000_000
        and cast(int, archive_block.get("timestamp_unix", 0))
        < cast(int, finalized_block.get("timestamp_unix", 0)),
        "historical_archive_state": archive_ok,
        "request_caps": request_caps,
        "access_boundary": access_ok,
    }


def collect_chain_metadata(manifest: Mapping[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Collect exactly the frozen non-account chain metadata."""

    errors = validate_chain_metadata_preflight(manifest)
    if errors:
        raise ValueError("invalid chain metadata preflight: " + "; ".join(errors))
    source = cast(Mapping[str, object], manifest["source_result"])
    source_path = Path(cast(str, source["path"]))
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    source_matches = source_hash == source["sha256"]
    if not source_matches:
        raise RuntimeError("committed source-result artifact differs from the frozen hash")

    rpc_config = cast(Mapping[str, object], manifest["rpc"])
    rpc = RpcCollector(
        url=cast(str, rpc_config["url"]),
        user_agent=cast(str, rpc_config["user_agent"]),
        maximum_requests_per_second=float(cast(float, rpc_config["maximum_requests_per_second"])),
        maximum_transport_retries=cast(int, rpc_config["maximum_transport_retries"]),
        maximum_http_attempts=cast(int, rpc_config["maximum_http_attempts"]),
        maximum_response_bytes=cast(int, rpc_config["maximum_response_bytes"]),
    )
    chain_id = rpc.call("chain_id", "eth_chainId", [])
    finalized_block = _block_record(
        rpc.call("finalized_block", "eth_getBlockByNumber", [rpc_config["snapshot_block_tag"], False]),
        path="finalized_block",
    )
    block_hex = cast(str, finalized_block["number_hex"])
    slots = cast(Mapping[str, object], manifest["proxy_slots"])
    getters = cast(Mapping[str, Mapping[str, object]], manifest["getters"])
    markets = cast(Sequence[Mapping[str, object]], manifest["markets"])
    market_records: list[dict[str, object]] = []
    for market in markets:
        market_id = cast(str, market["market_id"])
        proxy = normalize_address(market["proxy"], path=f"{market_id}.proxy")
        proxy_code = _code_record(
            rpc.call(f"current.{market_id}.proxy_code", "eth_getCode", [proxy, block_hex]),
            path=f"{market_id}.proxy_code",
        )
        implementation = decode_word_address(
            rpc.call(
                f"current.{market_id}.implementation_slot",
                "eth_getStorageAt",
                [proxy, slots["implementation"], block_hex],
            ),
            path=f"{market_id}.implementation_slot",
        )
        admin = decode_word_address(
            rpc.call(
                f"current.{market_id}.admin_slot",
                "eth_getStorageAt",
                [proxy, slots["admin"], block_hex],
            ),
            path=f"{market_id}.admin_slot",
        )
        implementation_code = _code_record(
            rpc.call(
                f"current.{market_id}.implementation_code",
                "eth_getCode",
                [implementation, block_hex],
            ),
            path=f"{market_id}.implementation_code",
        )
        getter_values = {
            getter_id: _getter_record(
                rpc,
                market_id=market_id,
                proxy=proxy,
                block_hex=block_hex,
                getter_id=getter_id,
                getter=getter,
            )
            for getter_id, getter in getters.items()
        }
        market_records.append(
            {
                "market_id": market_id,
                "proxy": proxy,
                "snapshot_block": finalized_block["number"],
                "proxy_code": proxy_code,
                "implementation": implementation,
                "implementation_code": implementation_code,
                "admin": admin,
                "getters": getter_values,
            }
        )

    configurator = cast(Mapping[str, object], manifest["configurator"])
    configurator_proxy = normalize_address(configurator["proxy"], path="configurator.proxy")
    configurator_code = _code_record(
        rpc.call("current.configurator.proxy_code", "eth_getCode", [configurator_proxy, block_hex]),
        path="configurator.proxy_code",
    )
    configurator_implementation = decode_word_address(
        rpc.call(
            "current.configurator.implementation_slot",
            "eth_getStorageAt",
            [configurator_proxy, slots["implementation"], block_hex],
        ),
        path="configurator.implementation_slot",
    )
    configurator_admin = decode_word_address(
        rpc.call(
            "current.configurator.admin_slot",
            "eth_getStorageAt",
            [configurator_proxy, slots["admin"], block_hex],
        ),
        path="configurator.admin_slot",
    )
    configurator_implementation_code = _code_record(
        rpc.call(
            "current.configurator.implementation_code",
            "eth_getCode",
            [configurator_implementation, block_hex],
        ),
        path="configurator.implementation_code",
    )
    configurator_record = {
        "proxy": configurator_proxy,
        "snapshot_block": finalized_block["number"],
        "proxy_code": configurator_code,
        "implementation": configurator_implementation,
        "implementation_code": configurator_implementation_code,
        "admin": configurator_admin,
    }

    archive = cast(Mapping[str, object], manifest["archive_check"])
    archive_number = cast(int, archive["block_number"])
    archive_hex = hex(archive_number)
    archive_block = _block_record(
        rpc.call("archive.block", "eth_getBlockByNumber", [archive_hex, False]),
        path="archive_block",
    )
    market_by_id = {cast(str, market["market_id"]): market for market in markets}
    archive_records: list[dict[str, object]] = []
    for market_id in cast(Sequence[str], archive["market_ids"]):
        market = market_by_id[market_id]
        proxy = normalize_address(market["proxy"], path=f"{market_id}.proxy")
        proxy_code = _code_record(
            rpc.call(f"archive.{market_id}.proxy_code", "eth_getCode", [proxy, archive_hex]),
            path=f"archive.{market_id}.proxy_code",
        )
        implementation = decode_word_address(
            rpc.call(
                f"archive.{market_id}.implementation_slot",
                "eth_getStorageAt",
                [proxy, slots["implementation"], archive_hex],
            ),
            path=f"archive.{market_id}.implementation_slot",
        )
        implementation_code = _code_record(
            rpc.call(
                f"archive.{market_id}.implementation_code",
                "eth_getCode",
                [implementation, archive_hex],
            ),
            path=f"archive.{market_id}.implementation_code",
        )
        archive_records.append(
            {
                "market_id": market_id,
                "proxy": proxy,
                "block_number": archive_number,
                "proxy_code": proxy_code,
                "implementation": implementation,
                "implementation_code": implementation_code,
            }
        )

    method_counts = Counter(cast(str, record["method"]) for record in rpc.records)
    request_summary = {
        "successful_request_count": len(rpc.records),
        "http_attempt_count": rpc.http_attempts,
        "response_byte_count": rpc.response_bytes,
        "method_counts": dict(sorted(method_counts.items())),
        "all_one_attempt": all(record["attempt_count"] == 1 for record in rpc.records),
    }
    gates = evaluate_chain_metadata(
        manifest,
        source_artifact_matches=source_matches,
        chain_id=chain_id,
        finalized_block=finalized_block,
        market_records=market_records,
        configurator_record=configurator_record,
        archive_block=archive_block,
        archive_records=archive_records,
        request_summary=request_summary,
    )
    policy = cast(Mapping[str, object], manifest["decision_policy"])
    passed = set(gates) == REQUIRED_GATES and all(gates.values())
    summary = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": manifest["audit_id"],
        "as_of": manifest["as_of"],
        "source_result": {"path": source["path"], "sha256": source_hash},
        "rpc": {
            "url": rpc_config["url"],
            "documentation_url": rpc_config["documentation_url"],
            "raw_payloads_retained": False,
        },
        "chain_id": chain_id,
        "finalized_block": finalized_block,
        "markets": market_records,
        "market_totals": {
            "market_count": len(market_records),
            "unique_proxy_code_hashes": len(
                {cast(Mapping[str, object], item["proxy_code"])["sha256"] for item in market_records}
            ),
            "unique_implementation_addresses": len({item["implementation"] for item in market_records}),
            "unique_implementation_code_hashes": len(
                {
                    cast(Mapping[str, object], item["implementation_code"])["sha256"]
                    for item in market_records
                }
            ),
            "unique_admin_addresses": len({item["admin"] for item in market_records}),
            "num_assets_total": sum(
                cast(int, cast(Mapping[str, object], item["getters"])["num_assets"])
                for item in market_records
            ),
        },
        "configurator": configurator_record,
        "archive_block": archive_block,
        "archive_markets": archive_records,
        "request_summary": request_summary,
        "access_boundary": manifest["access_boundary"],
        "gates": gates,
        "gate_counts": {"pass": sum(gates.values()), "fail": sum(not value for value in gates.values())},
        "decision": policy["pass"] if passed else policy["fail"],
        "authorized_next_stage": policy["authorized_next_stage"] if passed else None,
        "limitations": manifest["limitations"],
    }
    return summary, rpc.records


def _git_value(root: Path, args: Sequence[str]) -> str:
    result = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--response-hashes", type=Path, required=True)
    parser.add_argument("--collection-commit")
    return parser


def main() -> None:
    """Run the frozen chain-metadata audit from a clean exact worktree."""

    args = _build_parser().parse_args()
    for output in (args.summary, args.response_hashes):
        if output.exists():
            raise FileExistsError(f"refusing to overwrite {output}")
    root = Path.cwd()
    current_commit = _git_value(root, ["rev-parse", "HEAD"])
    if _git_value(root, ["status", "--porcelain"]):
        raise RuntimeError("collection worktree must be clean")
    if args.collection_commit is not None and args.collection_commit != current_commit:
        raise ValueError("collection commit must equal the clean worktree HEAD")
    manifest = load_chain_metadata_preflight(args.manifest)
    summary, response_records = collect_chain_metadata(manifest)
    summary["collection_commit"] = current_commit
    summary["manifest_sha256"] = hashlib.sha256(args.manifest.read_bytes()).hexdigest()
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.response_hashes.parent.mkdir(parents=True, exist_ok=True)
    _write_json(args.response_hashes, response_records)
    _write_json(args.summary, summary)
    print(json.dumps({"decision": summary["decision"], "requests": len(response_records)}, sort_keys=True))


if __name__ == "__main__":
    main()
