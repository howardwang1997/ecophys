from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = REPO_ROOT / "results/empirical_physics/morpho_public_allocator_pressure_d0_v2.json"
CHAIN_PATHS = {
    "base": REPO_ROOT
    / "results/empirical_physics/morpho_public_allocator_pressure_d0_base_chain_v2.json",
    "ethereum": REPO_ROOT
    / "results/empirical_physics/morpho_public_allocator_pressure_d0_ethereum_chain_v2.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_full_failure_artifact_is_immutable_and_bound_to_formal_run() -> None:
    result = _load_json(RESULT_PATH)
    claimed = str(result.pop("canonical_payload_sha256"))

    assert _canonical_sha256(result) == claimed
    assert claimed == "cf97beb874b855a07245ebf942f4ed8f21ffcf647ff06d677100ccc9378d8dab"
    assert _file_sha256(RESULT_PATH) == (
        "6b261b7878d194aff5046ced2a626d2836c2b009ce69075c0bf8bdf98cc6a5c4"
    )
    assert result["repository"] == {
        "git_sha": "78cfc09e08c7121dbdff998343d3b54576420ee5",
        "worktree_clean_before_run": True,
    }
    assert result["parent_config"]["sha256"] == (
        "bc6fc21cfd6b782280ace89d4d854b603dd19370bdad3c6d4803c72557333c60"
    )
    assert result["transport_amendment"]["sha256"] == (
        "b549efa43be88d9ce9385224f61158767b042df824fef447f959b600c66634a4"
    )
    assert result["qualification_artifact"]["canonical_payload_sha256"] == (
        "d9b28e6549d120fd94acfc378946f1e5deb475abf67b2de3f4870acc18aa65de"
    )


def test_chain_artifacts_are_exact_and_share_one_formal_batch() -> None:
    result = _load_json(RESULT_PATH)
    expected_file_hashes = {
        "base": "b183ef85e49292a5e8b9f027c8a8ab6173aa54e866f9f14ac086c4220ab2e973",
        "ethereum": "8f90f2f35b1a2f6f6b4f8988e0633c06b8c7c0158c0809ddc1aba1288475313d",
    }
    expected_canonical_hashes = {
        "base": "bb330b79a17da2b7716a0bc90cc05c5b0cdab1f219917f56b8ffc046392c16ca",
        "ethereum": "181d11c92689e8e3097f6139e094af11a52d46fe3cf31fc189536e8e6d01b2c1",
    }
    batch_ids: set[str] = set()

    for chain, path in CHAIN_PATHS.items():
        artifact = _load_json(path)
        claimed = str(artifact.pop("canonical_payload_sha256"))
        assert _canonical_sha256(artifact) == claimed
        assert claimed == expected_canonical_hashes[chain]
        assert _file_sha256(path) == expected_file_hashes[chain]
        assert result["chain_artifacts"][chain] == {
            "canonical_payload_sha256": claimed,
            "file_sha256": expected_file_hashes[chain],
        }
        assert artifact["repository"]["git_sha"] == result["repository"]["git_sha"]
        assert artifact["chain_result"] == result["chains"][chain]
        assert artifact["merge_eligibility"] is False
        assert artifact["worker"]["cuda_visible_devices"] == ""
        batch_ids.add(str(artifact["formal_batch_id"]))

    assert batch_ids == {"e35adb819faa8b8fb96885266ff6e87c6e73738e5c48e85645cf9e63ca0d6c59"}


def test_transport_failure_precedes_support_and_outcomes() -> None:
    result = _load_json(RESULT_PATH)

    assert result["d0_pass"] is False
    assert result["scientific_decision"] == "fail_stop_before_protocol_values_or_outcomes"
    assert result["chains"]["base"]["status"] == "transport_fail_before_support_interpretation"
    assert result["chains"]["ethereum"]["status"] == (
        "transport_fail_before_support_interpretation"
    )
    assert result["chains"]["base"]["support"] is None
    assert result["chains"]["ethereum"]["support"] is None
    assert result["gates"]["chains"]["base"]["transport"] is False
    assert result["gates"]["chains"]["ethereum"]["transport"] is False
    assert result["resources"]["gpu_hours"] == 0
    assert result["resources"]["paid_data_usd"] == 0
    assert all(value is False for value in result["data_contract"].values())


def test_legacy_pooled_zero_is_not_an_observed_support_count() -> None:
    result = _load_json(RESULT_PATH)

    assert result["pooled_support"] == {
        "candidate_transaction_count": 0,
        "distinct_chain_qualified_edge_count": 0,
    }
    assert all(chain["support"] is None for chain in result["chains"].values())
    assert result["gates"]["pooled"]["candidate_transactions"] is False
    assert result["gates"]["pooled"]["directed_edges"] is False
