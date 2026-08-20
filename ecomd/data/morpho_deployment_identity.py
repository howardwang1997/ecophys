"""Outcome-blind deployment-identity checks for Morpho allocator studies."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

_ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
_TX_HASH_RE = re.compile(r"^0x[0-9a-fA-F]{64}$")


def normalize_address(value: str) -> str:
    """Return a validated lower-case EVM address."""
    if _ADDRESS_RE.fullmatch(value) is None:
        raise ValueError(f"invalid EVM address: {value!r}")
    return value.lower()


def parse_allocator_registry(payload: Mapping[str, Any]) -> list[dict[str, str]]:
    """Parse the policy-only fields returned by a Morpho allocator endpoint."""
    data = payload.get("data")
    if not isinstance(data, list):
        raise ValueError("allocator response data must be a list")

    parsed: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in data:
        if not isinstance(item, Mapping):
            raise ValueError("allocator response item must be an object")
        address_value = item.get("address")
        tx_hash_value = item.get("tx_hash")
        if not isinstance(address_value, str):
            raise ValueError("allocator address must be a string")
        if not isinstance(tx_hash_value, str) or _TX_HASH_RE.fullmatch(tx_hash_value) is None:
            raise ValueError("allocator role-grant transaction hash is invalid")
        address = normalize_address(address_value)
        if address in seen:
            raise ValueError(f"duplicate allocator address: {address}")
        seen.add(address)
        parsed.append({"address": address, "tx_hash": tx_hash_value.lower()})
    return sorted(parsed, key=lambda item: item["address"])


def parse_allocator_graphql_response(
    payload: Mapping[str, Any],
    *,
    entity_field: str,
    vault_version: str,
    expected_vault_address: str,
) -> tuple[str, list[dict[str, str]]]:
    """Parse one exact-vault GraphQL role response without market fields."""
    errors = payload.get("errors")
    if errors not in (None, []):
        raise ValueError("Morpho GraphQL response contains errors")
    data = payload.get("data")
    if not isinstance(data, Mapping):
        raise ValueError("Morpho GraphQL data must be an object")
    entity = data.get(entity_field)
    if not isinstance(entity, Mapping):
        raise ValueError(f"Morpho GraphQL entity is missing: {entity_field}")
    returned_address = entity.get("address")
    name = entity.get("name")
    allocators = entity.get("allocators")
    if not isinstance(returned_address, str) or normalize_address(returned_address) != normalize_address(
        expected_vault_address
    ):
        raise ValueError("Morpho GraphQL returned the wrong vault address")
    if not isinstance(name, str) or not name:
        raise ValueError("Morpho GraphQL vault name must be a nonempty string")
    if not isinstance(allocators, list):
        raise ValueError("Morpho GraphQL allocators must be a list")

    records: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in allocators:
        if not isinstance(item, Mapping):
            raise ValueError("Morpho GraphQL allocator item must be an object")
        if vault_version == "v1":
            address_value = item.get("address")
        elif vault_version == "v2":
            allocator = item.get("allocator")
            if not isinstance(allocator, Mapping):
                raise ValueError("Morpho V2 GraphQL allocator wrapper is missing")
            address_value = allocator.get("address")
        else:
            raise ValueError(f"unsupported vault version: {vault_version}")
        if not isinstance(address_value, str):
            raise ValueError("Morpho GraphQL allocator address must be a string")
        address = normalize_address(address_value)
        if address in seen:
            raise ValueError(f"duplicate allocator address: {address}")
        seen.add(address)
        records.append({"address": address})
    return name, sorted(records, key=lambda item: item["address"])


def assess_deployment_identity(
    candidates: Sequence[Mapping[str, Any]],
    *,
    public_allocator_addresses: Sequence[str],
    required_candidate_count: int,
    minimum_independent_operator_clusters: int,
    minimum_distinct_nonpublic_allocator_addresses: int,
    minimum_distinct_policy_families: int,
) -> dict[str, Any]:
    """Evaluate frozen role-identity gates without behavioral or market fields."""
    public = {normalize_address(address) for address in public_allocator_addresses}
    assessed: list[dict[str, Any]] = []
    operators: set[str] = set()
    policy_families: set[str] = set()
    nonpublic_addresses: list[str] = []
    all_documented = True
    all_unambiguous = True

    for candidate in candidates:
        operator = candidate.get("operator")
        policy_family = candidate.get("policy_family")
        records = candidate.get("allocator_records")
        documented = candidate.get("operator_authored_automation_binding") is True
        if not isinstance(operator, str) or not operator:
            raise ValueError("candidate operator must be a nonempty string")
        if not isinstance(policy_family, str) or not policy_family:
            raise ValueError("candidate policy_family must be a nonempty string")
        if not isinstance(records, list) or any(not isinstance(record, Mapping) for record in records):
            raise ValueError("candidate allocator_records must be a list of objects")

        normalized_records: list[dict[str, str]] = []
        for record in records:
            address_value = record.get("address")
            tx_hash_value = record.get("tx_hash")
            if not isinstance(address_value, str):
                raise ValueError("allocator record address must be a string")
            normalized = {"address": normalize_address(address_value)}
            if tx_hash_value is not None:
                if not isinstance(tx_hash_value, str) or _TX_HASH_RE.fullmatch(tx_hash_value) is None:
                    raise ValueError("allocator role-grant transaction hash is invalid")
                normalized["tx_hash"] = tx_hash_value.lower()
            normalized_records.append(normalized)
        private_records = [record for record in normalized_records if record["address"] not in public]
        unambiguous = len(private_records) == 1
        all_unambiguous = all_unambiguous and unambiguous
        all_documented = all_documented and documented
        operators.add(operator)
        policy_families.add(policy_family)
        nonpublic_addresses.extend(record["address"] for record in private_records)
        assessed.append(
            {
                "operator": operator,
                "policy_family": policy_family,
                "documentary_binding": documented,
                "allocator_count": len(normalized_records),
                "public_allocator_count": len(normalized_records) - len(private_records),
                "nonpublic_allocator_count": len(private_records),
                "nonpublic_allocators": private_records,
                "unambiguous_nonpublic_allocator": unambiguous,
            }
        )

    distinct_private = set(nonpublic_addresses)
    gates = {
        "candidate_count": len(candidates) == required_candidate_count,
        "independent_operator_clusters": len(operators) >= minimum_independent_operator_clusters,
        "operator_authored_automation_bindings": all_documented,
        "one_nonpublic_allocator_per_anchor": all_unambiguous,
        "distinct_nonpublic_allocator_addresses": (
            len(distinct_private) >= minimum_distinct_nonpublic_allocator_addresses
            and len(distinct_private) == len(nonpublic_addresses)
        ),
        "distinct_policy_families": len(policy_families) >= minimum_distinct_policy_families,
    }
    return {
        "candidates": assessed,
        "counts": {
            "candidate_count": len(candidates),
            "operator_cluster_count": len(operators),
            "policy_family_count": len(policy_families),
            "distinct_nonpublic_allocator_count": len(distinct_private),
        },
        "gates": gates,
        "pass": all(gates.values()),
    }
