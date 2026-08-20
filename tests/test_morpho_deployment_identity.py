from __future__ import annotations

import pytest

from ecomd.data.morpho_deployment_identity import (
    assess_deployment_identity,
    normalize_address,
    parse_allocator_graphql_response,
    parse_allocator_registry,
)


def _tx(index: int) -> str:
    return "0x" + f"{index:064x}"


def _candidate(operator: str, policy: str, address: str) -> dict[str, object]:
    return {
        "operator": operator,
        "policy_family": policy,
        "operator_authored_automation_binding": True,
        "allocator_records": [{"address": address, "tx_hash": _tx(1)}],
    }


def test_parse_allocator_registry_keeps_only_policy_identity() -> None:
    payload = {
        "data": [
            {
                "address": "0x1111111111111111111111111111111111111111",
                "tx_hash": _tx(7),
                "ignored": {"amount": "forbidden"},
            }
        ],
        "pagination": {"next_cursor": None},
    }
    assert parse_allocator_registry(payload) == [
        {
            "address": "0x1111111111111111111111111111111111111111",
            "tx_hash": _tx(7),
        }
    ]


def test_parse_allocator_registry_rejects_duplicates() -> None:
    record = {
        "address": "0x1111111111111111111111111111111111111111",
        "tx_hash": _tx(3),
    }
    with pytest.raises(ValueError, match="duplicate"):
        parse_allocator_registry({"data": [record, record]})


@pytest.mark.parametrize(
    ("version", "entity_field", "allocators"),
    [
        (
            "v1",
            "vaultByAddress",
            [{"address": "0x1111111111111111111111111111111111111111"}],
        ),
        (
            "v2",
            "vaultV2ByAddress",
            [{"allocator": {"address": "0x1111111111111111111111111111111111111111"}}],
        ),
    ],
)
def test_parse_allocator_graphql_response(
    version: str, entity_field: str, allocators: list[dict[str, object]]
) -> None:
    address = "0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    payload = {
        "data": {
            entity_field: {
                "address": address,
                "name": "Anchor",
                "allocators": allocators,
                "ignored_market_state": {"totalAssets": "forbidden"},
            }
        }
    }
    name, records = parse_allocator_graphql_response(
        payload,
        entity_field=entity_field,
        vault_version=version,
        expected_vault_address=address,
    )
    assert name == "Anchor"
    assert records == [{"address": "0x1111111111111111111111111111111111111111"}]


def test_parse_allocator_graphql_response_rejects_wrong_vault() -> None:
    with pytest.raises(ValueError, match="wrong vault"):
        parse_allocator_graphql_response(
            {
                "data": {
                    "vaultByAddress": {
                        "address": "0x2222222222222222222222222222222222222222",
                        "name": "Wrong",
                        "allocators": [],
                    }
                }
            },
            entity_field="vaultByAddress",
            vault_version="v1",
            expected_vault_address="0x1111111111111111111111111111111111111111",
        )


def test_assessment_passes_three_distinct_documented_clusters() -> None:
    candidates = [
        _candidate("a", "p1", "0x1111111111111111111111111111111111111111"),
        _candidate("b", "p2", "0x2222222222222222222222222222222222222222"),
        _candidate("c", "p3", "0x3333333333333333333333333333333333333333"),
    ]
    result = assess_deployment_identity(
        candidates,
        public_allocator_addresses=["0x9999999999999999999999999999999999999999"],
        required_candidate_count=3,
        minimum_independent_operator_clusters=3,
        minimum_distinct_nonpublic_allocator_addresses=3,
        minimum_distinct_policy_families=2,
    )
    assert result["pass"] is True
    assert all(result["gates"].values())


def test_public_allocator_is_excluded_without_losing_unique_private_role() -> None:
    public = "0x9999999999999999999999999999999999999999"
    candidate = _candidate("a", "p1", "0x1111111111111111111111111111111111111111")
    candidate["allocator_records"] = [
        {"address": public, "tx_hash": _tx(1)},
        {
            "address": "0x1111111111111111111111111111111111111111",
            "tx_hash": _tx(2),
        },
    ]
    result = assess_deployment_identity(
        [candidate],
        public_allocator_addresses=[public],
        required_candidate_count=1,
        minimum_independent_operator_clusters=1,
        minimum_distinct_nonpublic_allocator_addresses=1,
        minimum_distinct_policy_families=1,
    )
    assert result["pass"] is True
    assert result["candidates"][0]["public_allocator_count"] == 1


@pytest.mark.parametrize(
    ("mutation", "failed_gate"),
    [
        ("ambiguous", "one_nonpublic_allocator_per_anchor"),
        ("shared", "distinct_nonpublic_allocator_addresses"),
        ("undocumented", "operator_authored_automation_bindings"),
    ],
)
def test_assessment_fails_identity_shortcuts(mutation: str, failed_gate: str) -> None:
    candidates = [
        _candidate("a", "p1", "0x1111111111111111111111111111111111111111"),
        _candidate("b", "p2", "0x2222222222222222222222222222222222222222"),
        _candidate("c", "p3", "0x3333333333333333333333333333333333333333"),
    ]
    if mutation == "ambiguous":
        candidates[0]["allocator_records"] = [
            {"address": "0x1111111111111111111111111111111111111111", "tx_hash": _tx(1)},
            {"address": "0x4444444444444444444444444444444444444444", "tx_hash": _tx(2)},
        ]
    elif mutation == "shared":
        candidates[1]["allocator_records"] = candidates[0]["allocator_records"]
    else:
        candidates[2]["operator_authored_automation_binding"] = False
    result = assess_deployment_identity(
        candidates,
        public_allocator_addresses=[],
        required_candidate_count=3,
        minimum_independent_operator_clusters=3,
        minimum_distinct_nonpublic_allocator_addresses=3,
        minimum_distinct_policy_families=2,
    )
    assert result["pass"] is False
    assert result["gates"][failed_gate] is False


def test_normalize_address_rejects_non_address() -> None:
    with pytest.raises(ValueError, match="invalid EVM address"):
        normalize_address("0x1234")
