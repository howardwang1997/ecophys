"""Bit-exact Ethereum fee-controller oracle and official-fixture validator."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import subprocess
import sys
import tarfile
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import yaml

SCHEMA_VERSION = "ecophys-fee-controller-oracle/v1"
FREEZE_SCHEMA_VERSION = "ecophys-fee-controller-oracle-freeze/v1"
RESULT_SCHEMA_VERSION = "ecophys-fee-controller-oracle-result/v1"
EIP7918_SPEC_COMMIT = "be1dbefafcb40879e3f6d231fad206c62f5b371b"
GAS_LIMIT_ADJUSTMENT_FACTOR = 1024
GAS_LIMIT_MINIMUM = 5000

EXPECTED_SCHEDULES: Mapping[str, tuple[int, int, int]] = {
    "Cancun": (3, 6, 3_338_477),
    "Prague": (6, 9, 5_007_716),
    "Osaka": (6, 9, 5_007_716),
    "BPO1": (10, 15, 8_346_193),
    "BPO2": (14, 21, 11_684_671),
}
EXPECTED_NETWORKS = frozenset(
    {"Osaka", "OsakaToBPO1AtTime15k", "BPO1ToBPO2AtTime15k"}
)

_NETWORK_AUDIT_EVENTS = frozenset(
    {
        "socket.bind",
        "socket.connect",
        "socket.getaddrinfo",
        "socket.gethostbyaddr",
        "socket.gethostbyname",
        "socket.sendto",
    }
)

for _accelerator_variable in ("CUDA_VISIBLE_DEVICES", "ROCR_VISIBLE_DEVICES"):
    os.environ[_accelerator_variable] = "-1"
for _thread_variable in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[_thread_variable] = "1"


@dataclass(frozen=True)
class BlobSchedule:
    """Integer parameters active for one blob-fee schedule."""

    target_blobs: int
    max_blobs: int
    update_fraction: int
    gas_per_blob: int = 2**17
    minimum_base_fee: int = 1
    blob_base_cost: int = 2**13

    def __post_init__(self) -> None:
        if self.target_blobs <= 0 or self.max_blobs <= self.target_blobs:
            raise ValueError("blob schedule requires 0 < target < maximum")
        if self.update_fraction <= 0 or self.gas_per_blob <= 0:
            raise ValueError("blob schedule fractions and gas units must be positive")
        if self.minimum_base_fee <= 0 or self.blob_base_cost <= 0:
            raise ValueError("blob fee constants must be positive")


@dataclass(frozen=True)
class HeaderState:
    """Controller-relevant fields of an execution header."""

    gas_limit: int
    gas_used: int
    execution_base_fee: int
    blob_gas_used: int
    excess_blob_gas: int
    timestamp: int

    def __post_init__(self) -> None:
        values = (
            self.gas_limit,
            self.gas_used,
            self.execution_base_fee,
            self.blob_gas_used,
            self.excess_blob_gas,
            self.timestamp,
        )
        if any(value < 0 for value in values):
            raise ValueError("header controller fields must be nonnegative")


def fake_exponential(factor: int, numerator: int, denominator: int) -> int:
    """Return the EIP-4844 integer Taylor exponential."""

    if factor < 0 or numerator < 0 or denominator <= 0:
        raise ValueError("fake_exponential requires nonnegative inputs and a positive denominator")
    iteration = 1
    output = 0
    numerator_accumulated = factor * denominator
    while numerator_accumulated > 0:
        output += numerator_accumulated
        numerator_accumulated = numerator_accumulated * numerator // (denominator * iteration)
        iteration += 1
    return output // denominator


def calculate_blob_base_fee(excess_blob_gas: int, schedule: BlobSchedule) -> int:
    """Calculate the EIP-4844 blob base fee for an excess state."""

    return fake_exponential(schedule.minimum_base_fee, excess_blob_gas, schedule.update_fraction)


def reserve_is_active(parent: HeaderState, schedule: BlobSchedule) -> bool:
    """Evaluate EIP-7918's strict execution-cost reserve inequality."""

    blob_fee = calculate_blob_base_fee(parent.excess_blob_gas, schedule)
    return (
        schedule.blob_base_cost * parent.execution_base_fee
        > schedule.gas_per_blob * blob_fee
    )


def calculate_excess_blob_gas(parent: HeaderState, schedule: BlobSchedule) -> int:
    """Calculate current excess blob gas with EIP-7918 integer semantics."""

    parent_blob_gas = parent.excess_blob_gas + parent.blob_gas_used
    target_blob_gas = schedule.gas_per_blob * schedule.target_blobs
    if parent_blob_gas < target_blob_gas:
        return 0
    if reserve_is_active(parent, schedule):
        schedule_delta = schedule.max_blobs - schedule.target_blobs
        return (
            parent.excess_blob_gas
            + parent.blob_gas_used * schedule_delta // schedule.max_blobs
        )
    return parent_blob_gas - target_blob_gas


def check_gas_limit(gas_limit: int, parent_gas_limit: int) -> bool:
    """Return whether an execution gas limit satisfies the consensus bounds."""

    if gas_limit < 0 or parent_gas_limit <= 0:
        return False
    maximum_delta = parent_gas_limit // GAS_LIMIT_ADJUSTMENT_FACTOR
    if gas_limit >= parent_gas_limit + maximum_delta:
        return False
    if gas_limit <= parent_gas_limit - maximum_delta:
        return False
    return gas_limit >= GAS_LIMIT_MINIMUM


def calculate_execution_base_fee(
    block_gas_limit: int,
    parent_gas_limit: int,
    parent_gas_used: int,
    parent_base_fee: int,
    *,
    elasticity_multiplier: int = 2,
    change_denominator: int = 8,
) -> int:
    """Calculate the EIP-1559 execution base fee with integer arithmetic."""

    if elasticity_multiplier <= 0 or change_denominator <= 0:
        raise ValueError("execution fee constants must be positive")
    if parent_gas_limit <= 0 or parent_gas_used < 0 or parent_base_fee < 0:
        raise ValueError("parent execution fields are invalid")
    if not check_gas_limit(block_gas_limit, parent_gas_limit):
        raise ValueError("block gas limit violates consensus bounds")
    parent_target = parent_gas_limit // elasticity_multiplier
    if parent_target <= 0:
        raise ValueError("parent gas target must be positive")
    if parent_gas_used == parent_target:
        return parent_base_fee
    if parent_gas_used > parent_target:
        used_delta = parent_gas_used - parent_target
        fee_delta = parent_base_fee * used_delta // parent_target // change_denominator
        return parent_base_fee + max(fee_delta, 1)
    used_delta = parent_target - parent_gas_used
    fee_delta = parent_base_fee * used_delta // parent_target // change_denominator
    return parent_base_fee - fee_delta


def active_blob_schedule(
    network: str,
    timestamp: int,
    schedules: Mapping[str, BlobSchedule],
    *,
    transition_timestamp: int = 15_000,
) -> tuple[str, BlobSchedule]:
    """Select the current schedule for the three preregistered fixture networks."""

    if network == "Osaka":
        name = "Osaka"
    elif network == "OsakaToBPO1AtTime15k":
        name = "BPO1" if timestamp >= transition_timestamp else "Osaka"
    elif network == "BPO1ToBPO2AtTime15k":
        name = "BPO2" if timestamp >= transition_timestamp else "BPO1"
    else:
        raise ValueError(f"unsupported fixture network: {network}")
    try:
        return name, schedules[name]
    except KeyError as error:
        raise ValueError(f"network {network} lacks schedule {name}") from error


def _mapping(value: object, *, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be a mapping")
    return cast(Mapping[str, object], value)


def _mapping_at(payload: Mapping[str, object], key: str) -> Mapping[str, object]:
    return _mapping(payload.get(key), name=key)


def _sequence(value: object, *, name: str) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{name} must be a sequence")
    return cast(Sequence[object], value)


def _string(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a nonempty string")
    return value


def _integer(payload: Mapping[str, object], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _quantity(value: object, *, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer quantity")
    if isinstance(value, int):
        result = value
    elif isinstance(value, str):
        try:
            result = int(value, 0)
        except ValueError as error:
            raise ValueError(f"{name} is not an integer quantity") from error
    else:
        raise ValueError(f"{name} must be an integer quantity")
    if result < 0:
        raise ValueError(f"{name} must be nonnegative")
    return result


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_yaml(path: Path) -> dict[str, object]:
    raw: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must contain a mapping")
    return cast(dict[str, object], raw)


def _header(payload: Mapping[str, object]) -> HeaderState:
    return HeaderState(
        gas_limit=_quantity(payload.get("gasLimit"), name="gasLimit"),
        gas_used=_quantity(payload.get("gasUsed"), name="gasUsed"),
        execution_base_fee=_quantity(payload.get("baseFeePerGas"), name="baseFeePerGas"),
        blob_gas_used=_quantity(payload.get("blobGasUsed"), name="blobGasUsed"),
        excess_blob_gas=_quantity(payload.get("excessBlobGas"), name="excessBlobGas"),
        timestamp=_quantity(payload.get("timestamp"), name="timestamp"),
    )


def _parse_schedules(
    fixture_config: Mapping[str, object], constants: Mapping[str, object]
) -> dict[str, BlobSchedule]:
    raw_schedules = _mapping_at(fixture_config, "blobSchedule")
    gas_per_blob = _integer(constants, "gas_per_blob")
    minimum_fee = _integer(constants, "min_blob_base_fee")
    blob_base_cost = _integer(constants, "blob_base_cost")
    schedules: dict[str, BlobSchedule] = {}
    for name, raw in raw_schedules.items():
        entry = _mapping(raw, name=f"blobSchedule.{name}")
        schedule = BlobSchedule(
            target_blobs=_quantity(entry.get("target"), name=f"{name}.target"),
            max_blobs=_quantity(entry.get("max"), name=f"{name}.max"),
            update_fraction=_quantity(
                entry.get("baseFeeUpdateFraction"), name=f"{name}.baseFeeUpdateFraction"
            ),
            gas_per_blob=gas_per_blob,
            minimum_base_fee=minimum_fee,
            blob_base_cost=blob_base_cost,
        )
        expected = EXPECTED_SCHEDULES.get(str(name))
        if expected is None:
            raise ValueError(f"unexpected blob schedule: {name}")
        actual = (schedule.target_blobs, schedule.max_blobs, schedule.update_fraction)
        if actual != expected:
            raise ValueError(f"schedule {name} differs from the official preregistered values")
        schedules[str(name)] = schedule
    return schedules


def _append_mismatch(
    mismatches: list[dict[str, object]],
    *,
    member: str,
    case: str,
    block_index: int | None,
    field: str,
    expected: object,
    actual: object,
) -> None:
    mismatches.append(
        {
            "member": member,
            "case": case,
            "block_index": block_index,
            "field": field,
            "expected": expected,
            "actual": actual,
        }
    )


def _dedicated_blob_fee_observations(
    case_payload: Mapping[str, object], contract_code: str
) -> list[int]:
    post_state = _mapping_at(case_payload, "postState")
    observations: list[int] = []
    for raw_account in post_state.values():
        account = _mapping(raw_account, name="postState account")
        if account.get("code") != contract_code:
            continue
        storage = _mapping_at(account, "storage")
        observations.append(_quantity(storage.get("0x00"), name="blob fee storage slot zero"))
    return observations


def validate_fixture_members(
    config: Mapping[str, object], member_payloads: Mapping[str, bytes]
) -> dict[str, object]:
    """Validate exact controller values in the selected fixture members."""

    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"config schema must be {SCHEMA_VERSION}")
    constants = _mapping_at(config, "constants")
    expected_totals = _mapping_at(config, "expected_totals")
    member_entries = _sequence(config.get("members"), name="members")
    transition_timestamp = _integer(constants, "bpo_transition_timestamp")
    elasticity = _integer(constants, "execution_elasticity_multiplier")
    fee_denominator = _integer(constants, "execution_base_fee_change_denominator")
    gas_per_blob = _integer(constants, "gas_per_blob")
    contract_code = _string(constants, "blob_base_fee_contract_code")
    source_commit = _string(_mapping_at(config, "archive"), "source_commit")

    mismatches: list[dict[str, object]] = []
    counts = {
        "members": 0,
        "cases": 0,
        "blocks": 0,
        "transactions": 0,
        "blob_transactions": 0,
        "execution_base_fee_comparisons": 0,
        "excess_blob_gas_comparisons": 0,
        "blob_base_fee_observations": 0,
    }
    networks: set[str] = set()
    schedule_names: set[str] = set()

    for raw_entry in member_entries:
        entry = _mapping(raw_entry, name="member entry")
        path = _string(entry, "path")
        payload = member_payloads.get(path)
        if payload is None:
            _append_mismatch(
                mismatches,
                member=path,
                case="",
                block_index=None,
                field="member_present",
                expected=True,
                actual=False,
            )
            continue
        counts["members"] += 1
        actual_member_hash = _sha256_bytes(payload)
        expected_member_hash = _string(entry, "sha256")
        if actual_member_hash != expected_member_hash:
            _append_mismatch(
                mismatches,
                member=path,
                case="",
                block_index=None,
                field="member_sha256",
                expected=expected_member_hash,
                actual=actual_member_hash,
            )
            continue
        if len(payload) != _integer(entry, "bytes"):
            _append_mismatch(
                mismatches,
                member=path,
                case="",
                block_index=None,
                field="member_bytes",
                expected=_integer(entry, "bytes"),
                actual=len(payload),
            )
        raw_document: object = json.loads(payload)
        document = _mapping(raw_document, name=path)
        if len(document) != _integer(entry, "expected_cases"):
            _append_mismatch(
                mismatches,
                member=path,
                case="",
                block_index=None,
                field="case_count",
                expected=_integer(entry, "expected_cases"),
                actual=len(document),
            )
        member_blocks = 0
        for case_name, raw_case in document.items():
            counts["cases"] += 1
            case = _mapping(raw_case, name=str(case_name))
            info = _mapping_at(case, "_info")
            info_url = _string(info, "url")
            if source_commit not in info_url:
                _append_mismatch(
                    mismatches,
                    member=path,
                    case=str(case_name),
                    block_index=None,
                    field="fixture_source_commit",
                    expected=source_commit,
                    actual=info_url,
                )
            spec_version = info.get("reference-spec-version")
            if spec_version != EIP7918_SPEC_COMMIT:
                _append_mismatch(
                    mismatches,
                    member=path,
                    case=str(case_name),
                    block_index=None,
                    field="eip7918_spec_commit",
                    expected=EIP7918_SPEC_COMMIT,
                    actual=spec_version,
                )
            fixture_config = _mapping_at(case, "config")
            network = _string(fixture_config, "network")
            networks.add(network)
            schedules = _parse_schedules(fixture_config, constants)
            parent = _header(_mapping_at(case, "genesisBlockHeader"))
            raw_blocks = _sequence(case.get("blocks"), name="blocks")
            member_blocks += len(raw_blocks)
            final_schedule: BlobSchedule | None = None
            final_header: HeaderState | None = None
            for block_index, raw_block in enumerate(raw_blocks):
                block = _mapping(raw_block, name="block")
                if "expectException" in block:
                    _append_mismatch(
                        mismatches,
                        member=path,
                        case=str(case_name),
                        block_index=block_index,
                        field="valid_block",
                        expected=True,
                        actual=False,
                    )
                    continue
                current = _header(_mapping_at(block, "blockHeader"))
                schedule_name, schedule = active_blob_schedule(
                    network,
                    current.timestamp,
                    schedules,
                    transition_timestamp=transition_timestamp,
                )
                schedule_names.add(schedule_name)
                expected_execution_fee = calculate_execution_base_fee(
                    current.gas_limit,
                    parent.gas_limit,
                    parent.gas_used,
                    parent.execution_base_fee,
                    elasticity_multiplier=elasticity,
                    change_denominator=fee_denominator,
                )
                counts["execution_base_fee_comparisons"] += 1
                if current.execution_base_fee != expected_execution_fee:
                    _append_mismatch(
                        mismatches,
                        member=path,
                        case=str(case_name),
                        block_index=block_index,
                        field="baseFeePerGas",
                        expected=expected_execution_fee,
                        actual=current.execution_base_fee,
                    )
                expected_excess = calculate_excess_blob_gas(parent, schedule)
                counts["excess_blob_gas_comparisons"] += 1
                if current.excess_blob_gas != expected_excess:
                    _append_mismatch(
                        mismatches,
                        member=path,
                        case=str(case_name),
                        block_index=block_index,
                        field="excessBlobGas",
                        expected=expected_excess,
                        actual=current.excess_blob_gas,
                    )
                transactions = _sequence(block.get("transactions", []), name="transactions")
                counts["transactions"] += len(transactions)
                block_blob_hashes = 0
                for raw_transaction in transactions:
                    transaction = _mapping(raw_transaction, name="transaction")
                    raw_hashes = transaction.get("blobVersionedHashes", [])
                    hashes = _sequence(raw_hashes, name="blobVersionedHashes")
                    if hashes:
                        counts["blob_transactions"] += 1
                        block_blob_hashes += len(hashes)
                expected_used = block_blob_hashes * gas_per_blob
                if current.blob_gas_used != expected_used:
                    _append_mismatch(
                        mismatches,
                        member=path,
                        case=str(case_name),
                        block_index=block_index,
                        field="blobGasUsed_from_transactions",
                        expected=expected_used,
                        actual=current.blob_gas_used,
                    )
                counts["blocks"] += 1
                parent = current
                final_header = current
                final_schedule = schedule
            if final_header is not None and final_schedule is not None:
                observed_fees = _dedicated_blob_fee_observations(case, contract_code)
                expected_blob_fee = calculate_blob_base_fee(
                    final_header.excess_blob_gas, final_schedule
                )
                for observed_fee in observed_fees:
                    counts["blob_base_fee_observations"] += 1
                    if observed_fee != expected_blob_fee:
                        _append_mismatch(
                            mismatches,
                            member=path,
                            case=str(case_name),
                            block_index=len(raw_blocks) - 1,
                            field="BLOBBASEFEE_storage",
                            expected=expected_blob_fee,
                            actual=observed_fee,
                        )
        if member_blocks != _integer(entry, "expected_blocks"):
            _append_mismatch(
                mismatches,
                member=path,
                case="",
                block_index=None,
                field="block_count",
                expected=_integer(entry, "expected_blocks"),
                actual=member_blocks,
            )

    for key in ("members", "cases", "blocks", "transactions", "blob_transactions"):
        expected = _integer(expected_totals, key)
        if counts[key] != expected:
            _append_mismatch(
                mismatches,
                member="",
                case="",
                block_index=None,
                field=f"total_{key}",
                expected=expected,
                actual=counts[key],
            )
    raw_expected_networks = config.get("expected_networks")
    required_networks = (
        {str(network) for network in _sequence(raw_expected_networks, name="expected_networks")}
        if raw_expected_networks is not None
        else set(EXPECTED_NETWORKS)
    )
    if networks != required_networks:
        _append_mismatch(
            mismatches,
            member="",
            case="",
            block_index=None,
            field="networks",
            expected=sorted(required_networks),
            actual=sorted(networks),
        )
    if counts["blob_base_fee_observations"] == 0:
        _append_mismatch(
            mismatches,
            member="",
            case="",
            block_index=None,
            field="blob_base_fee_observations_positive",
            expected=True,
            actual=False,
        )
    decision = _string(config, "decision_pass") if not mismatches else _string(config, "decision_fail")
    return {
        "decision": decision,
        "counts": counts,
        "networks": sorted(networks),
        "active_schedules": sorted(schedule_names),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "eip7918_spec_commit": EIP7918_SPEC_COMMIT,
    }


def _selected_member_payloads(
    archive_path: Path, selected_paths: set[str]
) -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    with tarfile.open(archive_path, mode="r|gz") as archive:
        for member in archive:
            if member.name not in selected_paths:
                continue
            if not member.isfile():
                raise ValueError(f"selected archive member is not a file: {member.name}")
            handle = archive.extractfile(member)
            if handle is None:
                raise ValueError(f"cannot read selected archive member: {member.name}")
            payloads[member.name] = handle.read()
            if len(payloads) == len(selected_paths):
                break
    return payloads


def evaluate_archive(config: Mapping[str, object], archive_path: Path) -> dict[str, object]:
    """Verify the official archive and evaluate its selected fixture members."""

    archive = _mapping_at(config, "archive")
    expected_size = _integer(archive, "bytes")
    expected_hash = _string(archive, "sha256")
    actual_size = archive_path.stat().st_size
    actual_hash = _sha256_file(archive_path)
    archive_mismatches: list[dict[str, object]] = []
    if actual_size != expected_size:
        archive_mismatches.append(
            {"field": "archive_bytes", "expected": expected_size, "actual": actual_size}
        )
    if actual_hash != expected_hash:
        archive_mismatches.append(
            {"field": "archive_sha256", "expected": expected_hash, "actual": actual_hash}
        )
    if archive_mismatches:
        return {
            "decision": _string(config, "decision_fail"),
            "archive": {"bytes": actual_size, "sha256": actual_hash},
            "counts": {},
            "networks": [],
            "active_schedules": [],
            "mismatch_count": len(archive_mismatches),
            "mismatches": archive_mismatches,
            "eip7918_spec_commit": EIP7918_SPEC_COMMIT,
        }
    member_entries = _sequence(config.get("members"), name="members")
    selected_paths = {
        _string(_mapping(entry, name="member entry"), "path") for entry in member_entries
    }
    payloads = _selected_member_payloads(archive_path, selected_paths)
    result = validate_fixture_members(config, payloads)
    result["archive"] = {"bytes": actual_size, "sha256": actual_hash}
    return result


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    )
    return completed.stdout.strip()


def _verify_freeze(root: Path, config_path: Path, freeze_path: Path) -> dict[str, object]:
    freeze = _load_yaml(freeze_path)
    if freeze.get("schema_version") != FREEZE_SCHEMA_VERSION:
        raise RuntimeError("Experiment 149 freeze schema mismatch")
    if freeze.get("formal_run_authorized") is not True:
        raise RuntimeError("Experiment 149 formal run is not authorized")
    if _git(root, "status", "--porcelain"):
        raise RuntimeError("Experiment 149 requires a clean committed checkout")
    for key in ("preregistration_commit", "implementation_commit"):
        commit = _string(freeze, key)
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
        )
    expected_paths: Mapping[str, Path] = {
        "config": config_path,
        "preregistration": config_path.parent / "PREREGISTRATION.md",
        "readme": config_path.parent / "README.md",
        "module": Path(__file__).resolve(),
        "test": root / "tests/test_fee_controller_oracle.py",
        "manifest": root / "data/manifests/ethereum_execution_fixtures_tests_v20_0_1.json",
    }
    files = _mapping_at(freeze, "files")
    for key, expected_path in expected_paths.items():
        entry = _mapping(files.get(key), name=f"files.{key}")
        recorded_path = (root / _string(entry, "path")).resolve()
        if recorded_path != expected_path.resolve():
            raise RuntimeError(f"Experiment 149 frozen path mismatch: {key}")
        if _sha256_file(recorded_path) != _string(entry, "sha256"):
            raise RuntimeError(f"Experiment 149 frozen hash mismatch: {key}")
    dependencies = _mapping_at(freeze, "dependencies")
    if platform.python_version() != _string(dependencies, "python"):
        raise RuntimeError("Experiment 149 Python version mismatch")
    if importlib.metadata.version("PyYAML") != _string(dependencies, "pyyaml"):
        raise RuntimeError("Experiment 149 PyYAML version mismatch")
    return freeze


def _network_audit_hook(event: str, _arguments: tuple[object, ...]) -> None:
    if event in _NETWORK_AUDIT_EVENTS:
        raise PermissionError(f"network disabled during Experiment 149: {event}")


def _peak_rss_gb() -> float:
    peak = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    if sys.platform != "darwin":
        peak *= 1024.0
    return peak / (1024.0**3)


def _atomic_write_json(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def run_formal(config_path: Path, archive_path: Path, output_path: Path) -> dict[str, object]:
    """Run the single frozen Experiment 149 protocol-conformance attempt."""

    root = Path(__file__).resolve().parents[2]
    resolved_config = config_path.resolve()
    if not resolved_config.is_relative_to(root):
        raise RuntimeError("Experiment 149 config must be inside the repository")
    expected_output = resolved_config.parent / "artifacts/raw/conformance.json"
    if output_path.resolve() != expected_output.resolve():
        raise RuntimeError("Experiment 149 output path differs from the preregistration")
    if output_path.exists():
        raise RuntimeError("Experiment 149 formal output already exists")
    config = _load_yaml(resolved_config)
    freeze_path = resolved_config.parent / "FREEZE.yaml"
    freeze = _verify_freeze(root, resolved_config, freeze_path)
    sys.addaudithook(_network_audit_hook)
    started = time.perf_counter()
    result = evaluate_archive(config, archive_path.resolve())
    elapsed = time.perf_counter() - started
    formal: dict[str, object] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "experiment_id": config.get("experiment_id"),
        "decision": result["decision"],
        "git_sha": _git(root, "rev-parse", "HEAD"),
        "preregistration_commit": freeze["preregistration_commit"],
        "implementation_commit": freeze["implementation_commit"],
        "config_sha256": _sha256_file(resolved_config),
        "module_sha256": _sha256_file(Path(__file__).resolve()),
        "fixture_result": result,
        "resources": {
            "runtime_seconds": elapsed,
            "peak_rss_gb": _peak_rss_gb(),
            "controller_processes": 1,
            "numerical_threads": 1,
            "network_calls": 0,
            "remote_hosts": 0,
            "gpu_hours": 0,
            "chain_outcome_files": 0,
        },
        "environment": {
            "python": platform.python_version(),
            "pyyaml": importlib.metadata.version("PyYAML"),
            "platform": platform.platform(),
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "rocr_visible_devices": os.environ.get("ROCR_VISIBLE_DEVICES"),
        },
    }
    _atomic_write_json(output_path, formal)
    return formal


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--fixture-archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line protocol-conformance validator."""

    arguments = _build_parser().parse_args(argv)
    formal = run_formal(arguments.config, arguments.fixture_archive, arguments.output)
    print(json.dumps(formal, indent=2, sort_keys=True))
    config = _load_yaml(arguments.config)
    return 0 if formal["decision"] == config.get("decision_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
