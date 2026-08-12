from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping

import pytest

from ecomd.research.fee_controller_oracle import (
    EIP7918_SPEC_COMMIT,
    BlobSchedule,
    HeaderState,
    active_blob_schedule,
    calculate_blob_base_fee,
    calculate_excess_blob_gas,
    calculate_execution_base_fee,
    check_gas_limit,
    fake_exponential,
    reserve_is_active,
    validate_fixture_members,
)

SOURCE_COMMIT = "87aba1a38a476b31f819a2390eb481527e6dc683"


def test_fake_exponential_and_blob_fee_are_integer_exact() -> None:
    schedule = BlobSchedule(6, 9, 5_007_716)
    assert fake_exponential(1, 0, 5_007_716) == 1
    assert fake_exponential(3, 0, 5_007_716) == 3
    assert calculate_blob_base_fee(0, schedule) == 1
    assert calculate_blob_base_fee(5_007_716, schedule) == 2
    with pytest.raises(ValueError):
        fake_exponential(1, 1, 0)


def test_execution_base_fee_covers_all_integer_branches() -> None:
    gas_limit = 10_000_000
    assert check_gas_limit(gas_limit, gas_limit)
    assert calculate_execution_base_fee(gas_limit, gas_limit, 5_000_000, 100) == 100
    assert calculate_execution_base_fee(gas_limit, gas_limit, 10_000_000, 100) == 112
    assert calculate_execution_base_fee(gas_limit, gas_limit, 0, 100) == 88
    assert calculate_execution_base_fee(gas_limit, gas_limit, 5_000_001, 1) == 2
    assert not check_gas_limit(gas_limit + gas_limit // 1024, gas_limit)


def test_eip7918_strict_boundary_lower_bound_and_reserve_increment() -> None:
    schedule = BlobSchedule(6, 9, 5_007_716)
    below_target = HeaderState(10_000_000, 0, 100, 0, 0, 0)
    assert calculate_excess_blob_gas(below_target, schedule) == 0

    equality = HeaderState(
        10_000_000,
        0,
        16,
        schedule.gas_per_blob * 6,
        0,
        0,
    )
    assert calculate_blob_base_fee(equality.excess_blob_gas, schedule) == 1
    assert not reserve_is_active(equality, schedule)
    assert calculate_excess_blob_gas(equality, schedule) == 0

    reserve = HeaderState(
        10_000_000,
        0,
        17,
        schedule.gas_per_blob * 6,
        0,
        0,
    )
    assert reserve_is_active(reserve, schedule)
    assert calculate_excess_blob_gas(reserve, schedule) == schedule.gas_per_blob * 2


def test_schedule_transition_uses_new_parameters_without_rescaling_state() -> None:
    schedules = {
        "Osaka": BlobSchedule(6, 9, 5_007_716),
        "BPO1": BlobSchedule(10, 15, 8_346_193),
        "BPO2": BlobSchedule(14, 21, 11_684_671),
    }
    before_name, before = active_blob_schedule(
        "OsakaToBPO1AtTime15k", 14_999, schedules
    )
    after_name, after = active_blob_schedule(
        "OsakaToBPO1AtTime15k", 15_000, schedules
    )
    assert before_name == "Osaka"
    assert before.target_blobs == 6
    assert after_name == "BPO1"
    assert after.target_blobs == 10
    parent = HeaderState(10_000_000, 0, 0, 0, 10 * 2**17, 14_999)
    assert calculate_excess_blob_gas(parent, after) == 0


def _synthetic_config(path: str, payload: bytes) -> dict[str, object]:
    return {
        "schema_version": "ecophys-fee-controller-oracle/v1",
        "experiment_id": "test",
        "decision_pass": "PROTOCOL_ORACLE_CONFORMANCE_PASS",
        "decision_fail": "IMPLEMENTATION_OR_SPEC_FAILURE",
        "archive": {"source_commit": SOURCE_COMMIT},
        "constants": {
            "gas_per_blob": 2**17,
            "blob_base_cost": 2**13,
            "min_blob_base_fee": 1,
            "execution_elasticity_multiplier": 2,
            "execution_base_fee_change_denominator": 8,
            "bpo_transition_timestamp": 15_000,
            "blob_base_fee_contract_code": "0x4a600055",
        },
        "members": [
            {
                "path": path,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "expected_cases": 1,
                "expected_blocks": 1,
            }
        ],
        "expected_totals": {
            "members": 1,
            "cases": 1,
            "blocks": 1,
            "transactions": 1,
            "blob_transactions": 1,
        },
        "expected_networks": ["Osaka"],
    }


def _synthetic_fixture(*, excess_delta: int = 0) -> bytes:
    schedule = BlobSchedule(6, 9, 5_007_716)
    parent = HeaderState(10_000_000, 5_000_000, 100, 6 * 2**17, 0, 0)
    current_excess = calculate_excess_blob_gas(parent, schedule) + excess_delta
    current_blob_fee = calculate_blob_base_fee(current_excess, schedule)
    fixture: Mapping[str, object] = {
        "case": {
            "_info": {
                "url": f"https://github.com/ethereum/execution-specs/blob/{SOURCE_COMMIT}/test.py",
                "reference-spec-version": EIP7918_SPEC_COMMIT,
            },
            "config": {
                "network": "Osaka",
                "blobSchedule": {
                    "Osaka": {
                        "target": "0x06",
                        "max": "0x09",
                        "baseFeeUpdateFraction": "0x4c6964",
                    }
                },
            },
            "genesisBlockHeader": {
                "gasLimit": "0x989680",
                "gasUsed": "0x4c4b40",
                "baseFeePerGas": "0x64",
                "blobGasUsed": "0xc0000",
                "excessBlobGas": "0x00",
                "timestamp": "0x00",
            },
            "blocks": [
                {
                    "blockHeader": {
                        "gasLimit": "0x989680",
                        "gasUsed": "0x00",
                        "baseFeePerGas": "0x64",
                        "blobGasUsed": "0x20000",
                        "excessBlobGas": hex(current_excess),
                        "timestamp": "0x0c",
                    },
                    "transactions": [{"blobVersionedHashes": ["0x01"]}],
                }
            ],
            "postState": {
                "0x01": {
                    "code": "0x4a600055",
                    "storage": {"0x00": hex(current_blob_fee)},
                }
            },
        }
    }
    return json.dumps(fixture, sort_keys=True).encode()


def test_synthetic_fixture_contract_passes_and_detects_header_mismatch() -> None:
    path = "fixture.json"
    good_payload = _synthetic_fixture()
    good = validate_fixture_members(_synthetic_config(path, good_payload), {path: good_payload})
    assert good["decision"] == "PROTOCOL_ORACLE_CONFORMANCE_PASS"
    assert good["mismatch_count"] == 0
    assert good["counts"] == {
        "members": 1,
        "cases": 1,
        "blocks": 1,
        "transactions": 1,
        "blob_transactions": 1,
        "execution_base_fee_comparisons": 1,
        "excess_blob_gas_comparisons": 1,
        "blob_base_fee_observations": 1,
    }

    bad_payload = _synthetic_fixture(excess_delta=1)
    bad = validate_fixture_members(_synthetic_config(path, bad_payload), {path: bad_payload})
    assert bad["decision"] == "IMPLEMENTATION_OR_SPEC_FAILURE"
    assert any(
        mismatch["field"] == "excessBlobGas"
        for mismatch in bad["mismatches"]
    )


def test_import_locks_accelerators_and_numerical_threads() -> None:
    assert os.environ["CUDA_VISIBLE_DEVICES"] == "-1"
    assert os.environ["ROCR_VISIBLE_DEVICES"] == "-1"
    for variable in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        assert os.environ[variable] == "1"
