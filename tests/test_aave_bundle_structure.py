from copy import deepcopy
from pathlib import Path

from ecomd.research.aave_bundle_structure import (
    build_transaction_bundles,
    load_bundle_manifest,
    run_bundle_feasibility,
    validate_bundle_manifest,
    validate_parent_artifacts,
)

MANIFEST_PATH = Path("data/manifests/aave_v3_bundle_structure_feasibility_v1.yaml")
CONFIGURATOR = "0x64b761d848206f447fe2dd461b0c635ec39ebb27"
ASSET_A = "0x1111111111111111111111111111111111111111"
ASSET_B = "0x2222222222222222222222222222222222222222"


def _row(
    *,
    block: int,
    transaction: int,
    log_index: int,
    asset: str = ASSET_A,
    ltv: int = 7_500,
    threshold: int = 8_000,
    bonus: int = 10_500,
) -> dict[str, object]:
    return {
        "address": CONFIGURATOR,
        "asset": asset,
        "block_hash": "0x" + f"{block:064x}",
        "block_number": block,
        "event_type": "collateral_configuration_changed",
        "liquidation_bonus": bonus,
        "liquidation_threshold": threshold,
        "log_index": log_index,
        "ltv": ltv,
        "role": "configurator",
        "topic0": "0x" + "63" * 32,
        "transaction_hash": "0x" + f"{transaction:064x}",
        "transaction_index": transaction,
    }


def _other(*, block: int, transaction: int, log_index: int) -> dict[str, object]:
    return {
        "address": CONFIGURATOR,
        "block_hash": "0x" + f"{block:064x}",
        "block_number": block,
        "event_type": "other_configurator",
        "log_index": log_index,
        "role": "configurator",
        "topic0": "0x" + "99" * 32,
        "transaction_hash": "0x" + f"{transaction:064x}",
        "transaction_index": transaction,
    }


def test_manifest_and_parent_artifacts_are_valid() -> None:
    manifest = load_bundle_manifest(MANIFEST_PATH)

    assert validate_bundle_manifest(manifest) == []
    assert validate_parent_artifacts(manifest, Path.cwd()) == []


def test_first_observation_is_unknown_and_never_imputed_as_zero() -> None:
    bundles = build_transaction_bundles([_row(block=1, transaction=1, log_index=0)])

    assert len(bundles) == 1
    bundle = bundles[0]
    assert bundle["predecessor_unknown_asset_count"] == 1
    assert bundle["net_changed_dimension_count"] == 0
    asset = bundle["asset_records"][0]
    assert asset["predecessor_known"] is False
    assert asset["predecessor_configuration"] is None


def test_round_trip_uses_final_transaction_state_not_intermediate_legs() -> None:
    records = [
        _row(block=1, transaction=1, log_index=0, threshold=8_000),
        _row(block=2, transaction=2, log_index=0, threshold=1),
        _row(block=2, transaction=2, log_index=1, threshold=8_000),
    ]

    bundles = build_transaction_bundles(records)
    round_trip = bundles[1]

    assert round_trip["contains_round_trip"] is True
    assert round_trip["net_changed_dimension_count"] == 0
    assert round_trip["net_liquidation_threshold_decrease_count"] == 0
    assert round_trip["asset_records"][0]["returns_to_predecessor_after_intermediate_change"] is True


def test_pure_lt_vector_requires_a_nonempty_net_vector() -> None:
    records = [
        _row(block=1, transaction=1, log_index=0, threshold=8_000),
        _row(block=2, transaction=2, log_index=0, threshold=7_800),
    ]

    bundles = build_transaction_bundles(records)

    assert bundles[0]["pure_liquidation_threshold_vector"] is False
    assert bundles[1]["pure_liquidation_threshold_vector"] is True
    assert bundles[1]["net_changes"] == [
        {
            "asset": ASSET_A,
            "field": "liquidation_threshold",
            "old_value": 8_000,
            "new_value": 7_800,
            "delta": -200,
        }
    ]


def test_vector_dimensions_cover_assets_and_all_three_configuration_fields() -> None:
    records = [
        _row(block=1, transaction=1, log_index=0, asset=ASSET_A),
        _row(block=1, transaction=1, log_index=1, asset=ASSET_B, threshold=7_000),
        _row(block=2, transaction=2, log_index=0, asset=ASSET_A, ltv=7_400, threshold=7_900),
        _row(block=2, transaction=2, log_index=1, asset=ASSET_B, threshold=6_900, bonus=10_600),
    ]

    bundle = build_transaction_bundles(records)[1]

    assert bundle["net_changed_asset_count"] == 2
    assert bundle["net_changed_dimension_count"] == 4
    assert bundle["net_change_field_counts"] == {
        "liquidation_bonus": 1,
        "liquidation_threshold": 2,
        "ltv": 1,
    }
    assert bundle["pure_liquidation_threshold_vector"] is False


def test_other_configurator_events_are_counted_but_not_semantically_invented() -> None:
    records = [
        _row(block=1, transaction=1, log_index=0),
        _other(block=1, transaction=1, log_index=1),
    ]

    bundle = build_transaction_bundles(records)[0]

    assert bundle["configurator_log_count"] == 2
    assert bundle["other_configurator_event_count"] == 1
    assert bundle["other_configurator_topic0_counts"] == {"0x" + "99" * 32: 1}
    assert bundle["only_semantically_decoded_configurator_events"] is False


def test_actual_parent_is_reproduced_as_development_only_structure() -> None:
    manifest = load_bundle_manifest(MANIFEST_PATH)

    summary = run_bundle_feasibility(manifest, root=Path.cwd())
    bundle = summary["bundle_summary"]

    assert summary["decision"] == (
        "COMPLETE_DEVELOPMENT_BUNDLE_STRUCTURE_AUTHORIZE_VECTOR_COMPILER_PROTOCOL_DESIGN_ONLY"
    )
    assert summary["gate_counts"] == {"pass": 7, "fail": 0}
    assert summary["parent_inventory"]["normalized_log_count"] == 3_119
    assert summary["parent_inventory"]["unique_configurator_topic0_count"] == 28
    assert bundle["transaction_count"] == 77
    assert bundle["transaction_with_net_lt_decrease_count"] == 5
    assert bundle["pure_emitted_lt_vector_transaction_count"] == 0
    assert bundle["round_trip_transaction_count"] == 1
    assert summary["development_disclosure"]["confirmatory_or_blind_claim_permitted"] is False


def test_validator_rejects_outcome_access_and_false_blindness() -> None:
    manifest = load_bundle_manifest(MANIFEST_PATH)
    broken = deepcopy(manifest)
    access = broken["access_boundary"]
    disclosure = broken["development_disclosure"]
    assert isinstance(access, dict)
    assert isinstance(disclosure, dict)
    access["realized_response_rows_opened"] = True
    disclosure["bundle_count_and_shape_explored_before_freeze"] = False
    disclosure["confirmatory_or_blind_claim_permitted"] = True

    errors = validate_bundle_manifest(broken)

    assert "realized_response_rows_opened must be false" in errors
    assert "development disclosure must remain explicit" in errors
