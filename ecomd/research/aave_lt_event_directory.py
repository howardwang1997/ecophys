"""Zero-account deployment, version, and LT-event directory for Aave V3 Ethereum."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path
from typing import cast

import requests
import yaml

from ecomd.research.compound_v3_chain_metadata import canonical_json_sha256

SCHEMA_VERSION = "ecophys-aave-v3-lt-event-directory/v1"
ARTIFACT_SCHEMA_VERSION = "ecophys-aave-v3-lt-event-directory-audit/v1"
AUDIT_ID = "aave_v3_ethereum_lt_event_directory_v1"
STAGE = "zero_account_deployment_version_and_configuration_event_directory"
AS_OF = "2026-08-16"

PROVIDER = "0x2f39d218133afab8f2b819b1066c7e434ad94e9e"
POOL = "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
CONFIGURATOR = "0x64b761d848206f447fe2dd461b0c635ec39ebb27"
ORACLE = "0x54586be62e3c3580375ae3723c145253060ca0c2"
ADDRESS_BOOK_POOL_IMPLEMENTATION = "0x728a138a4823392c2efa55e028d434f526fe03cf"
ADDRESS_BOOK_CONFIGURATOR_IMPLEMENTATION = "0xff42ce30054dce7dc7c1282a9a497aa58eabce99"
POOL_ID = "0x504f4f4c00000000000000000000000000000000000000000000000000000000"
CONFIGURATOR_ID = "0x504f4f4c5f434f4e464947555241544f52000000000000000000000000000000"
IMPLEMENTATION_SLOT = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"

FROZEN_PARENTS = {
    "a0_summary_path": "experiments/v14_aave_v3_liquidation_threshold_source_preflight/artifacts/summary.json",
    "a0_summary_sha256": "355928afb19ab4b4a8f6de0b786986e9aa4542e1394a3acac7b14dc1ebbc85e9",
    "a0_manifest_path": "data/manifests/aave_v3_liquidation_threshold_source_preflight_v1.yaml",
    "a0_manifest_sha256": "2656f0966d2e0c74b74eb2b147ef6e50bcb7838b078edef6e3552d66b2933ccc",
    "chain_summary_path": "experiments/v14_compound_v3_chain_metadata_preflight/artifacts_v2/summary.json",
    "chain_summary_sha256": "14f5b044d8c51e4323419b901a7f037c84c4af45083464e0daaefc561256c944",
    "expected_a0_decision": "PASS_SOURCE_EFFECT_IDENTITY_AUTHORIZE_AAVE_CHAIN_EVENT_INVENTORY_DESIGN_ONLY",
}
FROZEN_SOURCE_IDENTITY = {
    "aave_v3_origin_repository": "https://github.com/aave-dao/aave-v3-origin.git",
    "aave_v3_origin_commit": "cff15de6d1271b0c800fc001f4aea4c263e8a597",
    "aave_address_book_repository": "https://github.com/aave-dao/aave-address-book.git",
    "aave_address_book_commit": "70e2f303fe93616784148d6827df6644e5dda4db",
    "files": [
        {
            "repository": "aave_address_book",
            "path": "src/AaveV3Ethereum.sol",
            "git_blob": "9fc2e4533f0bd4d8e47a05f41ee539a688efe2d7",
            "sha256": "1a862b7389de3d59ee77680a8edb451a29e630a07813a0c5becdce65d730a22a",
        },
        {
            "repository": "aave_v3_origin",
            "path": "src/contracts/interfaces/IPoolAddressesProvider.sol",
            "git_blob": "c2c2a83d6c909f35bec510add4a2faf2848ef21f",
            "sha256": "6a44f3a913093d62dd072d1691cf605a76262f56da42cbecdcf80607d8aeef94",
        },
        {
            "repository": "aave_v3_origin",
            "path": "src/contracts/protocol/configuration/PoolAddressesProvider.sol",
            "git_blob": "009f4e5cc6cd396c16e5bd3960d472587d7a0756",
            "sha256": "134e0b3a2ac286d1a14459aae8a45541eed1877f3a043b7099e158d2332379a7",
        },
        {
            "repository": "aave_v3_origin",
            "path": "src/contracts/interfaces/IPoolConfigurator.sol",
            "git_blob": "6f66c1cdc6aa9f6bd263607502dc4b1305daf8b3",
            "sha256": "e84bcade8ae8bd981db571c25cab4f20f313b6e4800c4e0d8e9fff216b518da8",
        },
        {
            "repository": "aave_v3_origin",
            "path": "src/contracts/dependencies/openzeppelin/upgradeability/BaseUpgradeabilityProxy.sol",
            "git_blob": "aec817cb346ac6b178a806394c33a8ecc2145ce1",
            "sha256": "1b85e71d4ef4e473a7cd29c69f8f0845de7051d4f2aa2786ef1307893a93f04f",
        },
        {
            "repository": "aave_v3_origin",
            "path": "src/contracts/misc/aave-upgradeability/InitializableImmutableAdminUpgradeabilityProxy.sol",
            "git_blob": "6913a19d605892588baca1bd87e5044989a2b802",
            "sha256": "b9db086d3c390c3e3fac8dfdf5795204e4e1746695ff37d511fc43c6d92d2337",
        },
    ],
}
FROZEN_DEPLOYMENT: dict[str, object] = {
    "chain_id": "0x1",
    "pool_addresses_provider": PROVIDER,
    "pool_proxy": POOL,
    "pool_configurator_proxy": CONFIGURATOR,
    "price_oracle": ORACLE,
    "address_book_pool_implementation": ADDRESS_BOOK_POOL_IMPLEMENTATION,
    "address_book_pool_configurator_implementation": ADDRESS_BOOK_CONFIGURATOR_IMPLEMENTATION,
    "pool_id": POOL_ID,
    "pool_configurator_id": CONFIGURATOR_ID,
    "erc1967_implementation_slot": IMPLEMENTATION_SLOT,
    "getters": {
        "get_pool": "0x026b1d5f",
        "get_pool_configurator": "0x631adfca",
        "get_price_oracle": "0xfca513a8",
    },
}
EVENT_CONTRACT: dict[str, dict[str, str]] = {
    "collateral_configuration_changed": {
        "signature": "CollateralConfigurationChanged(address,uint256,uint256,uint256)",
        "topic0": "0x637febbda9275aea2e85c0ff690444c8d87eb2e8339bbede9715abcc89cb0995",
    },
    "upgraded": {
        "signature": "Upgraded(address)",
        "topic0": "0xbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b",
    },
    "pool_updated": {
        "signature": "PoolUpdated(address,address)",
        "topic0": "0x90affc163f1a2dfedcd36aa02ed992eeeba8100a4014f0b4cdc20ea265a66627",
    },
    "pool_configurator_updated": {
        "signature": "PoolConfiguratorUpdated(address,address)",
        "topic0": "0x8932892569eba59c8382a089d9b732d1f49272878775235761a2a6b0309cd465",
    },
    "proxy_created": {
        "signature": "ProxyCreated(bytes32,address,address)",
        "topic0": "0x4a465a9bd819d9662563c1e11ae958f8109e437e7f4bf1c6ef0b9a7b3f35d478",
    },
    "address_set": {
        "signature": "AddressSet(bytes32,address,address)",
        "topic0": "0x9ef0e8c8e52743bb38b83b17d9429141d494b8041ca6d616a6c77cebae9cd8b7",
    },
    "address_set_as_proxy": {
        "signature": "AddressSetAsProxy(bytes32,address,address,address)",
        "topic0": "0x3bbd45b5429b385e3fb37ad5cd1cd1435a3c8ec32196c7937597365a3fd3e99c",
    },
    "market_id_set": {
        "signature": "MarketIdSet(string,string)",
        "topic0": "0xe685c8cdecc6030c45030fd54778812cb84ed8e4467c38294403d68ba7860823",
    },
    "price_oracle_updated": {
        "signature": "PriceOracleUpdated(address,address)",
        "topic0": "0x56b5f80d8cac1479698aa7d01605fd6111e90b15fc4d2b377417f46034876cbd",
    },
    "acl_manager_updated": {
        "signature": "ACLManagerUpdated(address,address)",
        "topic0": "0xb30efa04327bb8a537d61cc1e5c48095345ad18ef7cc04e6bacf7dfb6caaf507",
    },
    "acl_admin_updated": {
        "signature": "ACLAdminUpdated(address,address)",
        "topic0": "0xe9cf53972264dc95304fd424458745019ddfca0e37ae8f703d74772c41ad115b",
    },
    "price_oracle_sentinel_updated": {
        "signature": "PriceOracleSentinelUpdated(address,address)",
        "topic0": "0x5326514eeca90494a14bedabcff812a0e683029ee85d1e23824d44fd14cd6ae7",
    },
    "pool_data_provider_updated": {
        "signature": "PoolDataProviderUpdated(address,address)",
        "topic0": "0xc853974cfbf81487a14a23565917bee63f527853bcb5fa54f2ae1cdf8a38356d",
    },
    "ownership_transferred": {
        "signature": "OwnershipTransferred(address,address)",
        "topic0": "0x8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0",
    },
}
FROZEN_DECISION_POLICY = {
    "all_gates_required": True,
    "pass": "PASS_AAVE_LT_EVENT_DIRECTORY_AUTHORIZE_ALL_CANDIDATE_MECHANICS_PROTOCOL_ONLY",
    "fail": "FAIL_AAVE_LT_EVENT_DIRECTORY_KEEP_ACCOUNTS_RESPONSES_AND_G1_LOCKED",
    "authorized_next_stage": "separately_frozen_all_candidate_historical_state_receipt_payload_source_preflight",
}
ALLOWED_METHODS = frozenset(
    {"eth_chainId", "eth_getBlockByNumber", "eth_getLogs", "eth_call", "eth_getStorageAt", "eth_getCode"}
)
REQUIRED_GATES = frozenset(
    {
        "parent_hashes_and_a0_decision",
        "frozen_source_identity",
        "ethereum_chain_id_replication",
        "fixed_window_header_replication",
        "exact_root_partition_plan",
        "complete_bounded_log_partitions",
        "strict_log_decoding",
        "no_duplicate_or_conflicting_logs",
        "provider_event_abi_complete",
        "provider_getter_source_conformance",
        "proxy_terminal_state_source_conformance",
        "complete_proxy_upgrade_crosswalk",
        "implementation_code_nonempty",
        "minimum_provisional_directory_support",
        "request_and_byte_caps",
        "zero_account_access_boundary",
    }
)
TRUE_ACCESS_KEYS = frozenset(
    {
        "chain_rpc_used",
        "official_deployment_source_opened",
        "provider_log_rows_opened",
        "configurator_log_rows_opened",
        "proxy_upgrade_log_rows_opened",
        "terminal_protocol_getters_and_slots_opened",
        "implementation_code_opened",
    }
)
FALSE_ACCESS_KEYS = frozenset(
    {
        "historical_reserve_configuration_opened",
        "governance_proposal_or_payload_rows_opened",
        "governance_transaction_or_receipt_rows_opened",
        "governance_call_trace_rows_opened",
        "account_state_rows_opened",
        "participant_action_rows_opened",
        "liquidation_rows_opened",
        "price_or_oracle_value_rows_opened",
        "realized_response_rows_opened",
        "raw_rpc_payloads_retained",
        "paid_data_used",
        "external_workers_used",
        "gpu_used",
    }
)
ADDRESS_PATTERN = re.compile(r"^0x[0-9a-fA-F]{40}$")
HASH_PATTERN = re.compile(r"^0x[0-9a-fA-F]{64}$")
DATA_PATTERN = re.compile(r"^0x(?:[0-9a-fA-F]{2})*$")
QUANTITY_PATTERN = re.compile(r"^0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)$")


def load_directory_manifest(path: str | Path) -> dict[str, object]:
    """Load an Aave event-directory manifest."""

    value: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("directory manifest root must be a mapping")
    return cast(dict[str, object], value)


def _mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _sequence(value: object) -> Sequence[object] | None:
    if isinstance(value, str) or not isinstance(value, Sequence):
        return None
    return cast(Sequence[object], value)


def normalize_address(value: object, *, path: str) -> str:
    """Return a canonical lower-case EVM address."""

    if not isinstance(value, str) or ADDRESS_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{path} must be a 20-byte address")
    return value.lower()


def normalize_hash(value: object, *, path: str) -> str:
    """Return a canonical lower-case 32-byte hash."""

    if not isinstance(value, str) or HASH_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{path} must be a 32-byte hash")
    return value.lower()


def normalize_data(value: object, *, path: str) -> str:
    """Return canonical even-length hex data."""

    if not isinstance(value, str) or DATA_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{path} must be even-length hex data")
    return value.lower()


def decode_quantity(value: object, *, path: str) -> int:
    """Decode a canonical non-negative JSON-RPC quantity."""

    if not isinstance(value, str) or QUANTITY_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{path} must be a canonical JSON-RPC quantity")
    return int(value, 16)


def split_inclusive_interval(from_block: int, to_block: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """Bisect one inclusive interval without overlap or omission."""

    if from_block >= to_block:
        raise ValueError("interval must contain at least two blocks")
    midpoint = (from_block + to_block) // 2
    return (from_block, midpoint), (midpoint + 1, to_block)


def root_intervals(from_block: int, to_block: int, block_count: int) -> tuple[tuple[int, int], ...]:
    """Create an exact inclusive root partition."""

    if from_block < 0 or to_block < from_block or block_count <= 0:
        raise ValueError("invalid root partition inputs")
    return tuple(
        (start, min(start + block_count - 1, to_block))
        for start in range(from_block, to_block + 1, block_count)
    )


def validate_directory_manifest(manifest: Mapping[str, object]) -> list[str]:
    """Validate immutable identifiers, access locks, and decision fields."""

    errors: list[str] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version differs from the frozen contract")
    if manifest.get("audit_id") != AUDIT_ID:
        errors.append("audit_id differs from the frozen contract")
    if manifest.get("as_of") != AS_OF or manifest.get("stage") != STAGE:
        errors.append("date or stage differs from the frozen contract")
    if manifest.get("parents") != FROZEN_PARENTS:
        errors.append("parents differ from the frozen artifact contract")
    if manifest.get("source_identity") != FROZEN_SOURCE_IDENTITY:
        errors.append("source_identity differs from the frozen contract")
    if manifest.get("deployment") != FROZEN_DEPLOYMENT:
        errors.append("deployment differs from the frozen address contract")
    if manifest.get("events") != EVENT_CONTRACT:
        errors.append("events differ from the frozen ABI contract")
    if manifest.get("decision_policy") != FROZEN_DECISION_POLICY:
        errors.append("decision_policy differs from the frozen contract")
    gates = _sequence(manifest.get("gates"))
    if gates is None or set(gates) != REQUIRED_GATES or len(gates) != len(REQUIRED_GATES):
        errors.append("gates differ from the frozen set")
    access = _mapping(manifest.get("access_boundary"))
    if access is None or set(access) != TRUE_ACCESS_KEYS | FALSE_ACCESS_KEYS:
        errors.append("access_boundary keys differ from the frozen contract")
    else:
        for key in sorted(TRUE_ACCESS_KEYS):
            if access.get(key) is not True:
                errors.append(f"{key} must be true")
        for key in sorted(FALSE_ACCESS_KEYS):
            if access.get(key) is not False:
                errors.append(f"{key} must be false")
    rpc = _mapping(manifest.get("rpc"))
    if rpc is None:
        errors.append("rpc must be a mapping")
    else:
        allowed = _sequence(rpc.get("allowed_methods"))
        if allowed is None or set(allowed) != ALLOWED_METHODS or len(allowed) != len(ALLOWED_METHODS):
            errors.append("allowed_methods differ from the frozen set")
        expected_rpc_values: dict[str, object] = {
            "maximum_requests_per_second_across_sources": 2,
            "maximum_transport_retries": 2,
            "maximum_http_attempts": 2000,
            "maximum_response_bytes": 268435456,
            "log_response_limit": 1000,
            "maximum_normalized_logs": 100000,
            "maximum_unique_implementations": 128,
            "root_partition_block_count": 250000,
            "raw_response_payloads_retained": False,
            "endpoint_substitution_after_freeze": False,
        }
        for key, expected in expected_rpc_values.items():
            if rpc.get(key) != expected:
                errors.append(f"rpc.{key} differs from the frozen value")
    window = _mapping(manifest.get("window"))
    expected_window = {
        "from_block": 0,
        "to_block": 25760572,
        "to_block_hash": "0xd2bb500d88a2c0fa956e04af3e6df36f8e60c4cd82307bcf71180cde466a4ca4",
        "expected_root_interval_count_per_stream": 104,
        "expected_log_stream_count": 3,
        "expected_root_log_query_count": 312,
    }
    if window != expected_window:
        errors.append("window differs from the frozen contract")
    rule = _mapping(manifest.get("directory_candidate_rule"))
    if rule is None:
        errors.append("directory_candidate_rule must be a mapping")
    else:
        expected_thresholds = {
            "minimum_provisional_candidates": 3,
            "minimum_distinct_assets": 2,
            "minimum_distinct_transactions": 3,
        }
        for key, expected in expected_thresholds.items():
            if rule.get(key) != expected:
                errors.append(f"directory_candidate_rule.{key} differs from the frozen value")
        for key, value in rule.items():
            if key not in expected_thresholds and value is not True:
                errors.append(f"directory_candidate_rule.{key} must be true")
    partition = _mapping(manifest.get("partition_rule"))
    if partition is None or not all(value is True or isinstance(value, str) for value in partition.values()):
        errors.append("partition_rule is malformed")
    return errors


def validate_parent_artifacts(manifest: Mapping[str, object], root: str | Path) -> list[str]:
    """Hash-check the A0 and fixed-chain-boundary parent artifacts."""

    errors: list[str] = []
    parents = _mapping(manifest.get("parents"))
    if parents is None:
        return ["parents must be a mapping"]
    root_path = Path(root)
    pairs = (
        ("a0_summary_path", "a0_summary_sha256"),
        ("a0_manifest_path", "a0_manifest_sha256"),
        ("chain_summary_path", "chain_summary_sha256"),
    )
    for path_key, hash_key in pairs:
        relative = parents.get(path_key)
        expected = parents.get(hash_key)
        if not isinstance(relative, str) or not isinstance(expected, str):
            errors.append(f"invalid parent fields {path_key}/{hash_key}")
            continue
        path = root_path / relative
        if not path.is_file():
            errors.append(f"missing parent artifact: {relative}")
            continue
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != expected:
            errors.append(f"parent hash mismatch: {relative}")
    a0_path = parents.get("a0_summary_path")
    if isinstance(a0_path, str) and (root_path / a0_path).is_file():
        try:
            a0_value: object = json.loads((root_path / a0_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot parse A0 summary: {exc}")
        else:
            a0 = _mapping(a0_value)
            if a0 is None or a0.get("decision") != parents.get("expected_a0_decision"):
                errors.append("A0 decision differs from the frozen passing decision")
    chain_path = parents.get("chain_summary_path")
    if isinstance(chain_path, str) and (root_path / chain_path).is_file():
        try:
            chain_value: object = json.loads((root_path / chain_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot parse chain summary: {exc}")
        else:
            chain = _mapping(chain_value)
            window = _mapping(manifest.get("window"))
            snapshot = _mapping(chain.get("snapshot_block")) if chain is not None else None
            if (
                chain is None
                or window is None
                or snapshot is None
                or snapshot.get("number") != window.get("to_block")
                or snapshot.get("hash") != window.get("to_block_hash")
            ):
                errors.append("chain parent does not reproduce the frozen end block")
    return errors


class RpcCollector:
    """Rate-limited JSON-RPC client retaining request and response hashes only."""

    def __init__(
        self,
        *,
        user_agent: str,
        maximum_requests_per_second: float,
        maximum_transport_retries: int,
        maximum_http_attempts: int,
        maximum_response_bytes: int,
    ) -> None:
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

    def call(self, *, url: str, label: str, method: str, params: Sequence[object]) -> object:
        """Issue one bounded request without retaining its raw response body."""

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
                response = self._session.post(url, json=request, timeout=60.0)
                body = response.content
                self.response_bytes += len(body)
                if self.response_bytes > self._maximum_response_bytes:
                    raise RuntimeError("maximum response-byte cap exceeded")
                response.raise_for_status()
                envelope_value: object = response.json()
            except RuntimeError:
                raise
            except (requests.RequestException, ValueError) as exc:
                prior_errors.append(f"{type(exc).__name__}: {exc}")
            else:
                envelope = _mapping(envelope_value)
                if envelope is None:
                    prior_errors.append("RPC response is not a mapping")
                elif envelope.get("error") is not None:
                    prior_errors.append(f"RPC error: {envelope['error']}")
                elif "result" not in envelope or envelope.get("result") is None:
                    prior_errors.append("RPC result is missing or null")
                else:
                    result = envelope["result"]
                    self.records.append(
                        {
                            "request_index": len(self.records),
                            "label": label,
                            "provider": "blockscout" if "blockscout" in url else "publicnode",
                            "method": method,
                            "params": list(params),
                            "request_sha256": canonical_json_sha256(request),
                            "response_body_sha256": hashlib.sha256(body).hexdigest(),
                            "response_canonical_json_sha256": canonical_json_sha256(envelope_value),
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


def _rpc_from_manifest(manifest: Mapping[str, object]) -> RpcCollector:
    rpc_config = cast(Mapping[str, object], manifest["rpc"])
    return RpcCollector(
        user_agent=cast(str, rpc_config["user_agent"]),
        maximum_requests_per_second=float(
            cast(int, rpc_config["maximum_requests_per_second_across_sources"])
        ),
        maximum_transport_retries=cast(int, rpc_config["maximum_transport_retries"]),
        maximum_http_attempts=cast(int, rpc_config["maximum_http_attempts"]),
        maximum_response_bytes=cast(int, rpc_config["maximum_response_bytes"]),
    )


def _topic_address(value: str, *, path: str) -> str:
    topic = normalize_hash(value, path=path)
    if topic[2:26] != "0" * 24:
        raise ValueError(f"{path} is not a canonical indexed address")
    return "0x" + topic[-40:]


def _data_words(data: str, *, count: int, path: str) -> tuple[str, ...]:
    normalized = normalize_data(data, path=path)
    if len(normalized) != 2 + count * 64:
        raise ValueError(f"{path} must contain exactly {count} ABI words")
    return tuple(normalized[2 + index * 64 : 2 + (index + 1) * 64] for index in range(count))


def _word_address(word: str, *, path: str) -> str:
    if len(word) != 64 or word[:24] != "0" * 24:
        raise ValueError(f"{path} is not a canonical ABI address word")
    return "0x" + word[-40:]


def _base_log(
    raw: Mapping[str, object],
    *,
    expected_address: str,
    role: str,
    from_block: int,
    to_block: int,
) -> tuple[dict[str, object], list[str], str]:
    address = normalize_address(raw.get("address"), path="log.address")
    if address != expected_address:
        raise ValueError("log address differs from the requested stream")
    block_number = decode_quantity(raw.get("blockNumber"), path="log.blockNumber")
    if not from_block <= block_number <= to_block:
        raise ValueError("log block lies outside the requested interval")
    topics_value = raw.get("topics")
    if not isinstance(topics_value, list) or not topics_value:
        raise ValueError("log topics must be a nonempty list")
    topics = [normalize_hash(value, path=f"log.topics[{index}]") for index, value in enumerate(topics_value)]
    data = normalize_data(raw.get("data"), path="log.data")
    removed = raw.get("removed", False)
    if removed is not False:
        raise ValueError("removed logs are forbidden")
    record = {
        "role": role,
        "address": address,
        "block_number": block_number,
        "block_hash": normalize_hash(raw.get("blockHash"), path="log.blockHash"),
        "transaction_hash": normalize_hash(raw.get("transactionHash"), path="log.transactionHash"),
        "transaction_index": decode_quantity(raw.get("transactionIndex"), path="log.transactionIndex"),
        "log_index": decode_quantity(raw.get("logIndex"), path="log.logIndex"),
        "topic0": topics[0],
    }
    return record, topics, data


def normalize_directory_log(
    raw: Mapping[str, object],
    *,
    expected_address: str,
    role: str,
    from_block: int,
    to_block: int,
) -> dict[str, object]:
    """Strictly decode provider, Configurator, and Pool upgrade log rows."""

    record, topics, data = _base_log(
        raw,
        expected_address=expected_address,
        role=role,
        from_block=from_block,
        to_block=to_block,
    )
    topic0 = topics[0]
    event_by_topic = {value["topic0"]: key for key, value in EVENT_CONTRACT.items()}
    event_type = event_by_topic.get(topic0)
    if role == "pool":
        if event_type != "upgraded" or len(topics) != 2 or data != "0x":
            raise ValueError("Pool stream must contain only canonical Upgraded logs")
        record.update({"event_type": "upgraded", "implementation": _topic_address(topics[1], path="upgrade")})
        return record
    if role == "configurator":
        if event_type == "upgraded":
            if len(topics) != 2 or data != "0x":
                raise ValueError("malformed Configurator Upgraded log")
            record.update(
                {"event_type": "upgraded", "implementation": _topic_address(topics[1], path="upgrade")}
            )
            return record
        if event_type == "collateral_configuration_changed":
            if len(topics) != 2:
                raise ValueError("CollateralConfigurationChanged must have one indexed asset")
            words = _data_words(data, count=3, path="collateral_configuration.data")
            record.update(
                {
                    "event_type": event_type,
                    "asset": _topic_address(topics[1], path="collateral_configuration.asset"),
                    "ltv": int(words[0], 16),
                    "liquidation_threshold": int(words[1], 16),
                    "liquidation_bonus": int(words[2], 16),
                }
            )
            return record
        record.update(
            {
                "event_type": "other_configurator",
                "topic_count": len(topics),
                "topics_sha256": canonical_json_sha256(topics),
                "data_byte_count": (len(data) - 2) // 2,
                "data_sha256": hashlib.sha256(bytes.fromhex(data[2:])).hexdigest(),
            }
        )
        return record
    if role != "provider":
        raise ValueError(f"unknown log role: {role}")
    pair_events = {
        "pool_updated",
        "pool_configurator_updated",
        "price_oracle_updated",
        "acl_manager_updated",
        "acl_admin_updated",
        "price_oracle_sentinel_updated",
        "pool_data_provider_updated",
        "ownership_transferred",
    }
    if event_type in pair_events:
        if len(topics) != 3 or data != "0x":
            raise ValueError(f"malformed provider {event_type} log")
        record.update(
            {
                "event_type": event_type,
                "old_address": _topic_address(topics[1], path=f"{event_type}.old"),
                "new_address": _topic_address(topics[2], path=f"{event_type}.new"),
            }
        )
        return record
    if event_type == "market_id_set":
        if len(topics) != 3 or data != "0x":
            raise ValueError("malformed MarketIdSet log")
        record.update(
            {"event_type": event_type, "old_market_id_hash": topics[1], "new_market_id_hash": topics[2]}
        )
        return record
    if event_type in {"proxy_created", "address_set"}:
        if len(topics) != 4 or data != "0x":
            raise ValueError(f"malformed provider {event_type} log")
        record.update(
            {
                "event_type": event_type,
                "id": topics[1],
                "proxy" if event_type == "proxy_created" else "old_address": _topic_address(
                    topics[2], path=f"{event_type}.value1"
                ),
                "implementation" if event_type == "proxy_created" else "new_address": _topic_address(
                    topics[3], path=f"{event_type}.value2"
                ),
            }
        )
        return record
    if event_type == "address_set_as_proxy":
        if len(topics) != 4:
            raise ValueError("malformed AddressSetAsProxy topic count")
        words = _data_words(data, count=1, path="address_set_as_proxy.data")
        record.update(
            {
                "event_type": event_type,
                "id": topics[1],
                "proxy": _topic_address(topics[2], path="address_set_as_proxy.proxy"),
                "old_implementation": _word_address(words[0], path="address_set_as_proxy.old_implementation"),
                "new_implementation": _topic_address(
                    topics[3], path="address_set_as_proxy.new_implementation"
                ),
            }
        )
        return record
    record.update(
        {
            "event_type": "unknown_provider",
            "topic_count": len(topics),
            "topics_sha256": canonical_json_sha256(topics),
            "data_byte_count": (len(data) - 2) // 2,
            "data_sha256": hashlib.sha256(bytes.fromhex(data[2:])).hexdigest(),
        }
    )
    return record


def deduplicate_logs(
    records: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], int, int]:
    """Deduplicate exact log identities and count conflicting observations."""

    by_identity: dict[tuple[object, object, object], dict[str, object]] = {}
    duplicate_count = 0
    conflict_count = 0
    for value in records:
        record = dict(value)
        identity = (record["block_hash"], record["transaction_hash"], record["log_index"])
        existing = by_identity.get(identity)
        if existing is None:
            by_identity[identity] = record
        elif existing == record:
            duplicate_count += 1
        else:
            conflict_count += 1
    ordered = sorted(
        by_identity.values(),
        key=lambda item: (
            cast(int, item["block_number"]),
            cast(int, item["transaction_index"]),
            cast(int, item["log_index"]),
            cast(str, item["address"]),
        ),
    )
    return ordered, duplicate_count, conflict_count


def provisional_directory_candidates(records: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    """Derive conservative LT-only rows from successive emitted configurations."""

    ordered = sorted(
        records,
        key=lambda item: (
            cast(int, item["block_number"]),
            cast(int, item["transaction_index"]),
            cast(int, item["log_index"]),
        ),
    )
    configurator_by_tx: Counter[str] = Counter(
        cast(str, item["transaction_hash"]) for item in ordered if item["role"] == "configurator"
    )
    deployment_or_upgrade_by_tx: Counter[str] = Counter(
        cast(str, item["transaction_hash"])
        for item in ordered
        if item["role"] == "provider" or item["event_type"] == "upgraded"
    )
    previous_by_asset: dict[str, Mapping[str, object]] = {}
    candidates: list[dict[str, object]] = []
    for item in ordered:
        if item["event_type"] != "collateral_configuration_changed":
            continue
        asset = cast(str, item["asset"])
        previous = previous_by_asset.get(asset)
        tx_hash = cast(str, item["transaction_hash"])
        checks = {
            "has_previous_emitted_configuration": previous is not None,
            "strict_positive_liquidation_threshold_decrease": previous is not None
            and 0 < cast(int, item["liquidation_threshold"]) < cast(int, previous["liquidation_threshold"]),
            "emitted_ltv_unchanged": previous is not None and item["ltv"] == previous["ltv"],
            "emitted_liquidation_bonus_unchanged": previous is not None
            and item["liquidation_bonus"] == previous["liquidation_bonus"],
            "exactly_one_configurator_log_in_transaction": configurator_by_tx[tx_hash] == 1,
            "no_provider_or_proxy_upgrade_log_in_transaction": deployment_or_upgrade_by_tx[tx_hash] == 0,
        }
        candidates.append(
            {
                "block_number": item["block_number"],
                "transaction_hash": tx_hash,
                "log_index": item["log_index"],
                "asset": asset,
                "previous_emitted_block_number": previous["block_number"] if previous is not None else None,
                "previous_emitted_transaction_hash": previous["transaction_hash"]
                if previous is not None
                else None,
                "old_emitted_ltv": previous["ltv"] if previous is not None else None,
                "new_emitted_ltv": item["ltv"],
                "old_emitted_liquidation_threshold": previous["liquidation_threshold"]
                if previous is not None
                else None,
                "new_emitted_liquidation_threshold": item["liquidation_threshold"],
                "old_emitted_liquidation_bonus": previous["liquidation_bonus"]
                if previous is not None
                else None,
                "new_emitted_liquidation_bonus": item["liquidation_bonus"],
                "checks": checks,
                "provisional_directory_candidate": all(checks.values()),
                "deferred_checks": [
                    "authoritative_t_minus_one_and_t_configuration",
                    "reserve_frozen_state",
                    "receipt_payload_and_call_path_isolation",
                    "config_engine_keep_current_normalization",
                    "emode_oracle_index_pause_and_grace_spillovers",
                    "historical_implementation_source_identity",
                    "proposal_mapping_and_untouched_confirmation_split",
                ],
            }
        )
        previous_by_asset[asset] = item
    return candidates


def _component_history(
    records: Sequence[Mapping[str, object]],
    *,
    component: str,
    component_id: str,
    proxy: str,
    terminal_implementation: str,
) -> dict[str, object]:
    provider_update_type = "pool_updated" if component == "pool" else "pool_configurator_updated"
    role = component
    creations = [
        item
        for item in records
        if item["role"] == "provider"
        and item["event_type"] == "proxy_created"
        and item.get("id") == component_id
    ]
    forbidden_sets = [
        item
        for item in records
        if item["role"] == "provider"
        and item["event_type"] == "address_set"
        and item.get("id") == component_id
    ]
    transitions: list[dict[str, object]] = []
    for item in records:
        if item["role"] != "provider":
            continue
        if item["event_type"] == provider_update_type:
            transitions.append(
                {
                    "block_number": item["block_number"],
                    "transaction_hash": item["transaction_hash"],
                    "log_index": item["log_index"],
                    "route": provider_update_type,
                    "old_implementation": item["old_address"],
                    "new_implementation": item["new_address"],
                }
            )
        elif item["event_type"] == "address_set_as_proxy" and item.get("id") == component_id:
            transitions.append(
                {
                    "block_number": item["block_number"],
                    "transaction_hash": item["transaction_hash"],
                    "log_index": item["log_index"],
                    "route": "address_set_as_proxy",
                    "old_implementation": item["old_implementation"],
                    "new_implementation": item["new_implementation"],
                    "declared_proxy": item["proxy"],
                }
            )
    transitions.sort(
        key=lambda item: (
            cast(int, item["block_number"]),
            cast(int, item["log_index"]),
        )
    )
    upgrades = [item for item in records if item["role"] == role and item["event_type"] == "upgraded"]
    upgrades.sort(
        key=lambda item: (
            cast(int, item["block_number"]),
            cast(int, item["log_index"]),
        )
    )
    transition_keys = Counter((item["transaction_hash"], item["new_implementation"]) for item in transitions)
    upgrade_keys = Counter((item["transaction_hash"], item["implementation"]) for item in upgrades)
    continuity = bool(transitions) and transitions[0]["old_implementation"] == "0x" + "0" * 40
    for old, new in pairwise(transitions):
        continuity = continuity and old["new_implementation"] == new["old_implementation"]
    creation_matches = (
        len(creations) == 1
        and creations[0].get("proxy") == proxy
        and bool(transitions)
        and creations[0].get("transaction_hash") == transitions[0]["transaction_hash"]
        and creations[0].get("implementation") == transitions[0]["new_implementation"]
    )
    declared_proxies_match = all(
        item.get("route") != "address_set_as_proxy" or item.get("declared_proxy") == proxy
        for item in transitions
    )
    checks = {
        "one_matching_proxy_created": creation_matches,
        "no_direct_address_set_for_component_id": not forbidden_sets,
        "nonempty_transition_history": bool(transitions),
        "continuous_old_to_new_implementation_chain": continuity,
        "one_to_one_provider_transition_and_proxy_upgrade": transition_keys == upgrade_keys,
        "all_address_set_as_proxy_rows_name_expected_proxy": declared_proxies_match,
        "latest_history_matches_terminal_slot": bool(transitions)
        and transitions[-1]["new_implementation"] == terminal_implementation,
    }
    return {
        "component": component,
        "component_id": component_id,
        "proxy": proxy,
        "transition_count": len(transitions),
        "upgrade_count": len(upgrades),
        "proxy_created_count": len(creations),
        "forbidden_direct_address_set_count": len(forbidden_sets),
        "transitions": transitions,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _block_record(value: object, *, expected_number: int, path: str) -> dict[str, object]:
    block = _mapping(value)
    if block is None:
        raise ValueError(f"{path} must be a block mapping")
    number = decode_quantity(block.get("number"), path=f"{path}.number")
    if number != expected_number:
        raise ValueError(f"{path} number differs from the requested number")
    timestamp = decode_quantity(block.get("timestamp"), path=f"{path}.timestamp")
    return {
        "number": number,
        "hash": normalize_hash(block.get("hash"), path=f"{path}.hash"),
        "timestamp_unix": timestamp,
        "timestamp_utc": datetime.fromtimestamp(timestamp, UTC).isoformat().replace("+00:00", "Z"),
    }


def _call_address(value: object, *, path: str) -> str:
    data = normalize_data(value, path=path)
    words = _data_words(data, count=1, path=path)
    return _word_address(words[0], path=path)


def _storage_address(value: object, *, path: str) -> str:
    data = normalize_data(value, path=path)
    words = _data_words(data, count=1, path=path)
    return _word_address(words[0], path=path)


def _code_record(value: object, *, address: str, roles: Sequence[str]) -> dict[str, object]:
    data = normalize_data(value, path=f"code[{address}]")
    code = bytes.fromhex(data[2:])
    return {
        "address": address,
        "roles": sorted(roles),
        "byte_count": len(code),
        "sha256": hashlib.sha256(code).hexdigest(),
        "nonempty": bool(code),
    }


def _collect_log_stream(
    rpc: RpcCollector,
    *,
    url: str,
    address: str,
    role: str,
    intervals: Sequence[tuple[int, int]],
    topic0: str | None,
    response_limit: int,
    maximum_normalized_logs: int,
) -> tuple[list[dict[str, object]], int, int]:
    accepted: list[dict[str, object]] = []
    query_count = 0
    saturated_count = 0

    def visit(interval_from: int, interval_to: int, *, root_index: int, depth: int) -> None:
        nonlocal query_count, saturated_count
        query_count += 1
        log_filter: dict[str, object] = {
            "fromBlock": hex(interval_from),
            "toBlock": hex(interval_to),
            "address": address,
        }
        if topic0 is not None:
            log_filter["topics"] = [topic0]
        result_value = rpc.call(
            url=url,
            label=f"logs:{role}:{root_index}:{depth}:{interval_from}-{interval_to}",
            method="eth_getLogs",
            params=[log_filter],
        )
        if not isinstance(result_value, list):
            raise ValueError("eth_getLogs result must be a list")
        if len(result_value) > response_limit:
            raise RuntimeError("eth_getLogs response exceeded the documented limit")
        if len(result_value) == response_limit:
            saturated_count += 1
            if interval_from == interval_to:
                raise RuntimeError("single-block log response remains saturated")
            left, right = split_inclusive_interval(interval_from, interval_to)
            visit(*left, root_index=root_index, depth=depth + 1)
            visit(*right, root_index=root_index, depth=depth + 1)
            return
        for raw in result_value:
            mapped = _mapping(raw)
            if mapped is None:
                raise ValueError("eth_getLogs item must be a mapping")
            accepted.append(
                normalize_directory_log(
                    mapped,
                    expected_address=address,
                    role=role,
                    from_block=interval_from,
                    to_block=interval_to,
                )
            )
            if len(accepted) > maximum_normalized_logs:
                raise RuntimeError("maximum normalized-log cap exceeded")

    for index, interval in enumerate(intervals):
        visit(*interval, root_index=index, depth=0)
    return accepted, query_count, saturated_count


def collect_directory(
    manifest: Mapping[str, object],
    *,
    root: str | Path = ".",
    rpc: RpcCollector | None = None,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    """Collect the frozen zero-account event and implementation directory."""

    errors = validate_directory_manifest(manifest)
    errors.extend(validate_parent_artifacts(manifest, root))
    if errors:
        raise ValueError("invalid Aave directory manifest: " + "; ".join(sorted(set(errors))))
    rpc_config = cast(Mapping[str, object], manifest["rpc"])
    if rpc is None:
        rpc = _rpc_from_manifest(manifest)
    blockscout_url = cast(str, rpc_config["blockscout_rpc_url"])
    publicnode_url = cast(str, rpc_config["publicnode_rpc_url"])
    window = cast(Mapping[str, object], manifest["window"])
    from_block = cast(int, window["from_block"])
    to_block = cast(int, window["to_block"])
    block_tag = hex(to_block)
    chain_ids: dict[str, object] = {}
    headers: dict[str, dict[str, dict[str, object]]] = {}
    for provider_name, url in (("blockscout", blockscout_url), ("publicnode", publicnode_url)):
        chain_ids[provider_name] = rpc.call(
            url=url, label=f"{provider_name}:chain_id", method="eth_chainId", params=[]
        )
        start = _block_record(
            rpc.call(
                url=url,
                label=f"{provider_name}:window_start_header",
                method="eth_getBlockByNumber",
                params=[hex(from_block), False],
            ),
            expected_number=from_block,
            path=f"{provider_name}.window_start",
        )
        end = _block_record(
            rpc.call(
                url=url,
                label=f"{provider_name}:window_end_header",
                method="eth_getBlockByNumber",
                params=[block_tag, False],
            ),
            expected_number=to_block,
            path=f"{provider_name}.window_end",
        )
        headers[provider_name] = {"from_block": start, "to_block": end}
    intervals = root_intervals(
        from_block,
        to_block,
        cast(int, rpc_config["root_partition_block_count"]),
    )
    maximum_logs = cast(int, rpc_config["maximum_normalized_logs"])
    response_limit = cast(int, rpc_config["log_response_limit"])
    streams = (
        ("provider", PROVIDER, None),
        ("configurator", CONFIGURATOR, None),
        ("pool", POOL, EVENT_CONTRACT["upgraded"]["topic0"]),
    )
    raw_records: list[dict[str, object]] = []
    query_counts: dict[str, int] = {}
    saturated_counts: dict[str, int] = {}
    for role, address, topic0 in streams:
        stream_records, queries, saturated = _collect_log_stream(
            rpc,
            url=blockscout_url,
            address=address,
            role=role,
            intervals=intervals,
            topic0=topic0,
            response_limit=response_limit,
            maximum_normalized_logs=maximum_logs - len(raw_records),
        )
        raw_records.extend(stream_records)
        query_counts[role] = queries
        saturated_counts[role] = saturated
    records, duplicate_count, conflict_count = deduplicate_logs(raw_records)
    terminal_state: dict[str, str] = {}
    getter_calls = {
        "pool": "0x026b1d5f",
        "configurator": "0x631adfca",
        "oracle": "0xfca513a8",
    }
    for name, selector in getter_calls.items():
        terminal_state[name] = _call_address(
            rpc.call(
                url=blockscout_url,
                label=f"blockscout:terminal_getter:{name}",
                method="eth_call",
                params=[{"to": PROVIDER, "data": selector}, block_tag],
            ),
            path=f"blockscout.terminal_getter.{name}",
        )
    terminal_state["pool_implementation"] = _storage_address(
        rpc.call(
            url=blockscout_url,
            label="blockscout:terminal_slot:pool",
            method="eth_getStorageAt",
            params=[POOL, IMPLEMENTATION_SLOT, block_tag],
        ),
        path="blockscout.terminal_slot.pool",
    )
    terminal_state["configurator_implementation"] = _storage_address(
        rpc.call(
            url=blockscout_url,
            label="blockscout:terminal_slot:configurator",
            method="eth_getStorageAt",
            params=[CONFIGURATOR, IMPLEMENTATION_SLOT, block_tag],
        ),
        path="blockscout.terminal_slot.configurator",
    )
    pool_history = _component_history(
        records,
        component="pool",
        component_id=POOL_ID,
        proxy=POOL,
        terminal_implementation=terminal_state["pool_implementation"],
    )
    configurator_history = _component_history(
        records,
        component="configurator",
        component_id=CONFIGURATOR_ID,
        proxy=CONFIGURATOR,
        terminal_implementation=terminal_state["configurator_implementation"],
    )
    roles_by_code_address: dict[str, set[str]] = defaultdict(set)
    roles_by_code_address[PROVIDER].add("pool_addresses_provider")
    roles_by_code_address[POOL].add("pool_proxy")
    roles_by_code_address[CONFIGURATOR].add("pool_configurator_proxy")
    for history in (pool_history, configurator_history):
        component = cast(str, history["component"])
        transitions = cast(Sequence[Mapping[str, object]], history["transitions"])
        for transition in transitions:
            implementation = cast(str, transition["new_implementation"])
            roles_by_code_address[implementation].add(f"{component}_implementation")
    implementation_addresses = [
        address
        for address, roles in roles_by_code_address.items()
        if any(role.endswith("_implementation") for role in roles)
    ]
    if len(implementation_addresses) > cast(int, rpc_config["maximum_unique_implementations"]):
        raise RuntimeError("maximum unique implementation cap exceeded")
    code_inventory: list[dict[str, object]] = []
    for address in sorted(roles_by_code_address):
        code_inventory.append(
            _code_record(
                rpc.call(
                    url=blockscout_url,
                    label=f"blockscout:terminal_code:{address}",
                    method="eth_getCode",
                    params=[address, block_tag],
                ),
                address=address,
                roles=sorted(roles_by_code_address[address]),
            )
        )
    candidates = provisional_directory_candidates(records)
    provisional = [item for item in candidates if item["provisional_directory_candidate"] is True]
    provisional_assets = {cast(str, item["asset"]) for item in provisional}
    provisional_transactions = {cast(str, item["transaction_hash"]) for item in provisional}
    candidate_rule = cast(Mapping[str, object], manifest["directory_candidate_rule"])
    access = cast(Mapping[str, object], manifest["access_boundary"])
    access_ok = all(access[key] is True for key in TRUE_ACCESS_KEYS) and all(
        access[key] is False for key in FALSE_ACCESS_KEYS
    )
    provider_unknown_count = sum(item["event_type"] == "unknown_provider" for item in records)
    getter_conformant = all(
        (
            terminal_state["pool"] == POOL,
            terminal_state["configurator"] == CONFIGURATOR,
            terminal_state["oracle"] == ORACLE,
        )
    )
    slot_conformant = all(
        (
            terminal_state["pool_implementation"] == ADDRESS_BOOK_POOL_IMPLEMENTATION,
            terminal_state["configurator_implementation"] == ADDRESS_BOOK_CONFIGURATOR_IMPLEMENTATION,
        )
    )
    root_query_count = len(intervals) * len(streams)
    gates = {
        "parent_hashes_and_a0_decision": True,
        "frozen_source_identity": True,
        "ethereum_chain_id_replication": chain_ids == {"blockscout": "0x1", "publicnode": "0x1"},
        "fixed_window_header_replication": headers["blockscout"] == headers["publicnode"]
        and headers["blockscout"]["to_block"]["hash"] == window["to_block_hash"]
        and cast(int, headers["blockscout"]["from_block"]["timestamp_unix"])
        < cast(int, headers["blockscout"]["to_block"]["timestamp_unix"]),
        "exact_root_partition_plan": len(intervals) == window["expected_root_interval_count_per_stream"]
        and len(streams) == window["expected_log_stream_count"]
        and root_query_count == window["expected_root_log_query_count"],
        "complete_bounded_log_partitions": all(value >= len(intervals) for value in query_counts.values()),
        "strict_log_decoding": True,
        "no_duplicate_or_conflicting_logs": duplicate_count == 0 and conflict_count == 0,
        "provider_event_abi_complete": provider_unknown_count == 0,
        "provider_getter_source_conformance": getter_conformant,
        "proxy_terminal_state_source_conformance": slot_conformant,
        "complete_proxy_upgrade_crosswalk": pool_history["passed"] is True
        and configurator_history["passed"] is True,
        "implementation_code_nonempty": bool(code_inventory)
        and all(item["nonempty"] is True for item in code_inventory),
        "minimum_provisional_directory_support": len(provisional)
        >= cast(int, candidate_rule["minimum_provisional_candidates"])
        and len(provisional_assets) >= cast(int, candidate_rule["minimum_distinct_assets"])
        and len(provisional_transactions) >= cast(int, candidate_rule["minimum_distinct_transactions"]),
        "request_and_byte_caps": rpc.http_attempts <= cast(int, rpc_config["maximum_http_attempts"])
        and rpc.response_bytes <= cast(int, rpc_config["maximum_response_bytes"])
        and len(records) <= cast(int, rpc_config["maximum_normalized_logs"])
        and len(implementation_addresses) <= cast(int, rpc_config["maximum_unique_implementations"]),
        "zero_account_access_boundary": access_ok,
    }
    policy = cast(Mapping[str, object], manifest["decision_policy"])
    passed = set(gates) == REQUIRED_GATES and all(gates.values())
    event_counts = dict(sorted(Counter(cast(str, item["event_type"]) for item in records).items()))
    role_counts = dict(sorted(Counter(cast(str, item["role"]) for item in records).items()))
    method_counts = dict(sorted(Counter(cast(str, item["method"]) for item in rpc.records).items()))
    summary = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": manifest["audit_id"],
        "as_of": manifest["as_of"],
        "parents": manifest["parents"],
        "source_identity": manifest["source_identity"],
        "window": {
            "chain_ids": chain_ids,
            "headers": headers,
            "root_interval_count_per_stream": len(intervals),
            "log_stream_count": len(streams),
            "root_log_query_count": root_query_count,
        },
        "terminal_state": {"provider": "blockscout", "block_number": to_block, "values": terminal_state},
        "version_history": {"pool": pool_history, "configurator": configurator_history},
        "code_inventory": code_inventory,
        "event_directory": {
            "normalized_log_count": len(records),
            "role_counts": role_counts,
            "event_type_counts": event_counts,
            "duplicate_count": duplicate_count,
            "conflict_count": conflict_count,
            "unknown_provider_event_count": provider_unknown_count,
            "collateral_configuration_event_count": event_counts.get("collateral_configuration_changed", 0),
            "configuration_candidate_record_count": len(candidates),
            "provisional_directory_candidate_count": len(provisional),
            "provisional_distinct_asset_count": len(provisional_assets),
            "provisional_distinct_transaction_count": len(provisional_transactions),
            "configuration_candidate_records": candidates,
        },
        "request_summary": {
            "successful_request_count": len(rpc.records),
            "http_attempt_count": rpc.http_attempts,
            "response_byte_count": rpc.response_bytes,
            "method_counts": method_counts,
            "stream_query_counts": query_counts,
            "stream_saturated_query_counts": saturated_counts,
            "all_one_attempt": all(item["attempt_count"] == 1 for item in rpc.records),
        },
        "access_boundary": manifest["access_boundary"],
        "gates": gates,
        "gate_counts": {"pass": sum(gates.values()), "fail": sum(not value for value in gates.values())},
        "decision": policy["pass"] if passed else policy["fail"],
        "authorized_next_stage": policy["authorized_next_stage"] if passed else None,
        "limitations": manifest["limitations"],
    }
    return summary, records, rpc.records


def _git_value(root: Path, args: Sequence[str]) -> str:
    result = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--response-hashes", type=Path, required=True)
    parser.add_argument("--failure", type=Path, required=True)
    parser.add_argument("--collection-commit")
    return parser


def main() -> None:
    """Run the frozen directory once from an exact clean worktree."""

    args = _build_parser().parse_args()
    outputs = (args.summary, args.directory, args.response_hashes, args.failure)
    for output in outputs:
        if output.exists():
            raise FileExistsError(f"refusing to overwrite {output}")
    root = Path.cwd()
    current_commit = _git_value(root, ["rev-parse", "HEAD"])
    if _git_value(root, ["status", "--porcelain"]):
        raise RuntimeError("collection worktree must be clean")
    if args.collection_commit is not None and args.collection_commit != current_commit:
        raise ValueError("collection commit must equal the clean worktree HEAD")
    manifest = load_directory_manifest(args.manifest)
    rpc: RpcCollector | None = None
    try:
        errors = validate_directory_manifest(manifest)
        errors.extend(validate_parent_artifacts(manifest, root))
        if errors:
            raise ValueError("invalid Aave directory manifest: " + "; ".join(sorted(set(errors))))
        rpc = _rpc_from_manifest(manifest)
        summary, directory, responses = collect_directory(manifest, root=root, rpc=rpc)
    except Exception as exc:
        args.failure.parent.mkdir(parents=True, exist_ok=True)
        completed_responses = [] if rpc is None else rpc.records
        if rpc is not None:
            args.response_hashes.parent.mkdir(parents=True, exist_ok=True)
            _write_json(args.response_hashes, completed_responses)
        _write_json(
            args.failure,
            {
                "schema_version": "ecophys-aave-v3-lt-event-directory-failure/v1",
                "audit_id": manifest.get("audit_id"),
                "collection_commit": current_commit,
                "manifest_sha256": hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "successful_request_count_before_failure": len(completed_responses),
                "http_attempt_count_before_failure": 0 if rpc is None else rpc.http_attempts,
                "response_byte_count_before_failure": 0 if rpc is None else rpc.response_bytes,
                "decision": FROZEN_DECISION_POLICY["fail"],
                "authorized_next_stage": None,
            },
        )
        raise
    summary["collection_commit"] = current_commit
    summary["manifest_sha256"] = hashlib.sha256(args.manifest.read_bytes()).hexdigest()
    for output in (args.summary, args.directory, args.response_hashes):
        output.parent.mkdir(parents=True, exist_ok=True)
    _write_json(args.directory, directory)
    _write_json(args.response_hashes, responses)
    _write_json(args.summary, summary)
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "requests": len(responses),
                "logs": len(directory),
                "provisional_candidates": cast(Mapping[str, object], summary["event_directory"])[
                    "provisional_directory_candidate_count"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
