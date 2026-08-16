from copy import deepcopy
from pathlib import Path

import pytest

from ecomd.research.aave_liquidation_threshold_source import (
    EFFECT_CONTRACT,
    REQUIRED_GATES,
    SOURCE_COMMIT,
    SOURCE_REPO,
    UINT256_MAX,
    WAD,
    LiquidationThresholdShockInput,
    audit_source_tree,
    evaluate_liquidation_threshold_shock,
    health_factor_from_weighted_sum,
    load_source_preflight,
    validate_source_preflight,
    wad_div_half_up,
)

MANIFEST_PATH = Path("data/manifests/aave_v3_liquidation_threshold_source_preflight_v1.yaml")


def _direct_input(**updates: object) -> LiquidationThresholdShockInput:
    values: dict[str, object] = {
        "old_weighted_liquidation_threshold_sum": 20_000_000_000 * 8_000,
        "changed_collateral_base_value": 20_000_000_000,
        "total_debt_base": 15_000_000_000,
        "old_liquidation_threshold_bps": 8_000,
        "new_liquidation_threshold_bps": 7_000,
        "old_ltv_bps": 6_500,
        "new_ltv_bps": 6_500,
        "old_liquidation_bonus_bps": 10_500,
        "new_liquidation_bonus_bps": 10_500,
        "using_changed_reserve_as_collateral": True,
        "borrowing_any": True,
        "e_mode_overrides_changed_reserve": False,
    }
    values.update(updates)
    return LiquidationThresholdShockInput(**values)  # type: ignore[arg-type]


def _write_synthetic_source(root: Path, manifest: dict[str, object]) -> None:
    files = manifest["files"]
    assert isinstance(files, dict)
    for role, raw_record in files.items():
        assert isinstance(role, str)
        assert isinstance(raw_record, dict)
        path = root / str(raw_record["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        markers = raw_record["required_normalized_markers"]
        assert isinstance(markers, list)
        if role == "pool_configurator":
            text = """
            function configureReserveAsCollateral(
              address asset,
              uint256 ltv,
              uint256 liquidationThreshold,
              uint256 liquidationBonus
            ) external override onlyRiskOrPoolAdmins {
              if (currentConfig.getFrozen()) {
                _pendingLtv[asset] = ltv;
              }
              currentConfig.setLiquidationThreshold(liquidationThreshold);
              currentConfig.setLiquidationBonus(liquidationBonus);
              _pool.setConfiguration(asset, currentConfig);
              emit CollateralConfigurationChanged(
                asset, newLtv, liquidationThreshold, liquidationBonus
              );
            }
            """
        else:
            text = "\n".join(str(marker) for marker in markers)
        path.write_text(text, encoding="utf-8")


def test_manifest_freezes_source_zero_row_boundary_and_effect_contract() -> None:
    manifest = load_source_preflight(MANIFEST_PATH)

    assert validate_source_preflight(manifest) == []
    assert manifest["effect_contract"] == EFFECT_CONTRACT
    assert set(manifest["gates"]) == REQUIRED_GATES  # type: ignore[arg-type]
    assert manifest["source"] == {
        "repo_url": SOURCE_REPO,
        "commit": SOURCE_COMMIT,
        "reconnaissance_disclosure": manifest["source"][  # type: ignore[index]
            "reconnaissance_disclosure"
        ],
    }
    access = manifest["access_boundary"]
    assert isinstance(access, dict)
    assert access["official_code_blobs_opened"] is True
    assert access["official_documentation_opened"] is True
    assert all(
        value is False
        for key, value in access.items()
        if key not in {"official_code_blobs_opened", "official_documentation_opened"}
    )


def test_exact_direct_identity_crosses_only_the_health_factor_boundary() -> None:
    result = evaluate_liquidation_threshold_shock(_direct_input())

    assert result.mechanically_exposed is True
    assert result.direct_weighted_sum_decrease == 20_000_000_000 * 1_000
    assert result.new_weighted_liquidation_threshold_sum == 20_000_000_000 * 7_000
    assert result.weighted_identity_holds is True
    assert result.old_health_factor >= WAD
    assert result.new_health_factor < WAD
    assert result.crosses_health_factor_boundary is True
    assert result.health_factor_monotone_nonincreasing is True


def test_e_mode_override_and_disabled_collateral_have_zero_direct_base_lt_effect() -> None:
    e_mode = evaluate_liquidation_threshold_shock(_direct_input(e_mode_overrides_changed_reserve=True))
    disabled = evaluate_liquidation_threshold_shock(_direct_input(using_changed_reserve_as_collateral=False))

    assert e_mode.route_reason == "e_mode_liquidation_threshold_override"
    assert disabled.route_reason == "changed_reserve_not_enabled_as_collateral"
    for result in (e_mode, disabled):
        assert result.mechanically_exposed is False
        assert result.direct_weighted_sum_decrease == 0
        assert result.old_health_factor == result.new_health_factor
        assert result.crosses_health_factor_boundary is False


def test_strict_effect_rejects_bundles_invalid_states_and_uint256_overflow() -> None:
    with pytest.raises(ValueError, match="ltv must remain unchanged"):
        evaluate_liquidation_threshold_shock(_direct_input(new_ltv_bps=6_400))
    with pytest.raises(ValueError, match="liquidation bonus must remain unchanged"):
        evaluate_liquidation_threshold_shock(_direct_input(new_liquidation_bonus_bps=10_600))
    with pytest.raises(ValueError, match="contribution exceeds"):
        evaluate_liquidation_threshold_shock(_direct_input(old_weighted_liquidation_threshold_sum=1))
    with pytest.raises(OverflowError, match="wadDiv would overflow"):
        wad_div_half_up(UINT256_MAX, 1)


def test_exact_arithmetic_is_monotone_over_frozen_threshold_grid() -> None:
    prior_health_factor: int | None = None
    for new_threshold in range(7_999, 6_499, -37):
        result = evaluate_liquidation_threshold_shock(
            _direct_input(new_liquidation_threshold_bps=new_threshold)
        )
        assert result.health_factor_monotone_nonincreasing is True
        assert result.direct_health_factor_decrease >= 0
        if prior_health_factor is not None:
            assert result.new_health_factor <= prior_health_factor
        prior_health_factor = result.new_health_factor

    assert wad_div_half_up(1, 6) == (WAD + 3) // 6
    assert health_factor_from_weighted_sum(0, 0) == UINT256_MAX


def test_synthetic_pinned_source_tree_passes_all_twelve_gates(tmp_path: Path) -> None:
    manifest = load_source_preflight(MANIFEST_PATH)
    _write_synthetic_source(tmp_path, manifest)

    artifact = audit_source_tree(
        tmp_path,
        manifest,
        source_commit=SOURCE_COMMIT,
        source_remote=SOURCE_REPO,
        source_clean=True,
        collection_commit="a" * 40,
        manifest_sha256="b" * 64,
    )

    assert artifact["gate_counts"] == {"pass": 12, "fail": 0}
    assert artifact["decision"] == (
        "PASS_SOURCE_EFFECT_IDENTITY_AUTHORIZE_AAVE_CHAIN_EVENT_INVENTORY_DESIGN_ONLY"
    )
    assert artifact["authorized_next_stage"] == (
        "separately_frozen_aave_ethereum_deployment_and_liquidation_threshold_event_inventory_design_only"
    )
    assert artifact["source"]["raw_source_retained_in_artifact"] is False  # type: ignore[index]


def test_source_marker_and_account_write_mutations_fail_closed(tmp_path: Path) -> None:
    manifest = load_source_preflight(MANIFEST_PATH)
    _write_synthetic_source(tmp_path, manifest)
    files = manifest["files"]
    assert isinstance(files, dict)
    generic = files["generic_logic"]
    assert isinstance(generic, dict)
    generic_path = tmp_path / str(generic["path"])
    generic_path.write_text("missing semantic markers", encoding="utf-8")
    configurator = files["pool_configurator"]
    assert isinstance(configurator, dict)
    configurator_path = tmp_path / str(configurator["path"])
    configurator_path.write_text(
        configurator_path.read_text(encoding="utf-8").replace(
            "currentConfig.setLiquidationThreshold(liquidationThreshold);",
            "_usersConfig[user] = config;\ncurrentConfig.setLiquidationThreshold(liquidationThreshold);",
        ),
        encoding="utf-8",
    )

    artifact = audit_source_tree(
        tmp_path,
        manifest,
        source_commit=SOURCE_COMMIT,
        source_remote=SOURCE_REPO,
        source_clean=True,
        collection_commit="a" * 40,
        manifest_sha256="b" * 64,
    )

    assert artifact["gates"]["required_markers"] is False  # type: ignore[index]
    assert (
        artifact["gates"][  # type: ignore[index]
            "configuration_transition_has_no_account_write_or_iteration"
        ]
        is False
    )
    assert artifact["decision"] == "FAIL_SOURCE_EFFECT_IDENTITY_KEEP_AAVE_UNADMITTED"
    assert artifact["authorized_next_stage"] is None


def test_manifest_mutations_cannot_open_rows_or_drift_source_and_markers() -> None:
    manifest = load_source_preflight(MANIFEST_PATH)
    broken = deepcopy(manifest)
    broken["access_boundary"]["chain_event_rows_opened"] = True  # type: ignore[index]
    broken["source"]["commit"] = "0" * 40  # type: ignore[index]
    broken["files"]["pool"]["required_normalized_markers"].append(  # type: ignore[index,union-attr]
        "marker with whitespace"
    )

    errors = validate_source_preflight(broken)

    assert "access_boundary.chain_event_rows_opened must be false" in errors
    assert "source.commit differs from the frozen Aave source commit" in errors
    assert "files.pool.required_normalized_markers must contain no whitespace" in errors
