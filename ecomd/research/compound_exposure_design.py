"""Zero-row design contract and exposure-completeness identity for Compound III."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import yaml

SCHEMA_VERSION = "ecophys-compound-v3-exposure-control-design/v1"
STAGE = "zero_row_protocol_design_only"
TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "design_id",
        "as_of",
        "stage",
        "evidence",
        "access_boundary",
        "unit_contract",
        "treatment_contract",
        "population_contract",
        "action_contract",
        "control_contract",
        "finality_contract",
        "privacy_retention_contract",
        "gates",
        "decision_policy",
        "limitations",
    }
)
EVIDENCE_KEYS = frozenset(
    {
        "source_summary_path",
        "source_summary_sha256",
        "chain_summary_path",
        "chain_summary_sha256",
        "source_commit",
        "chain_collection_commit",
    }
)
ACCESS_KEYS = frozenset(
    {
        "account_state_rows_opened",
        "chain_rpc_used",
        "governance_payload_rows_opened",
        "governance_log_rows_opened",
        "participant_action_rows_opened",
        "call_trace_rows_opened",
        "liquidation_rows_opened",
        "price_or_oracle_rows_opened",
        "realized_response_rows_opened",
        "raw_addresses_retained",
        "paid_data_used",
        "external_workers_used",
        "gpu_used",
        "official_code_blobs_opened",
    }
)
EXPECTED_IDENTITY_LAYERS = (
    "account_state_owner",
    "top_level_transaction_sender",
    "immediate_call_operator",
    "manager_or_bulker",
    "token_funder_or_recipient",
    "liquidation_absorber",
    "collateral_sale_recipient",
)
EXPECTED_ELIGIBLE_EVENTS = (
    "UpdateAssetBorrowCollateralFactor",
    "UpdateAssetLiquidateCollateralFactor",
    "UpdateAssetSupplyCap",
)
EXPECTED_EXCLUDED_EVENTS = frozenset(
    {
        "AddAsset",
        "UpdateAssetPriceFeed",
        "implementation_only_upgrade",
        "PauseAction",
        "rewards_or_reserves_change",
        "bundled_multi_market_change",
    }
)
EXPECTED_TRANSACTION_EVENTS = (
    "eligible_configuration_event",
    "CometDeployed",
    "Upgraded",
)
EXPECTED_STATE_OWNER_EVENTS = (
    ("Supply", ("dst",)),
    ("Withdraw", ("src",)),
    ("SupplyCollateral", ("dst",)),
    ("WithdrawCollateral", ("src",)),
    ("Transfer", ("from", "to")),
    ("TransferCollateral", ("from", "to")),
    ("AbsorbDebt", ("borrower",)),
    ("AbsorbCollateral", ("borrower",)),
)
EXPECTED_RESIDUAL_IDENTITIES = (
    "totalSupplyBase_equals_sum_positive_principal",
    "totalBorrowBase_equals_sum_negative_principal_magnitude",
    "each_totalsCollateral_equals_sum_account_collateral",
)
EXPECTED_VOLUNTARY_CHANNELS = (
    "supply_base",
    "repay_base",
    "withdraw_base",
    "borrow_base",
    "supply_collateral",
    "withdraw_collateral",
    "transfer_base",
    "transfer_collateral",
)
EXPECTED_CONTROL_FAMILIES = (
    "same_market_zero_direct_asset_exposure",
    "same_asset_other_unchanged_comet_market",
    "matched_account_market_in_unchanged_comet_market",
    "pre_event_pseudo_intervention",
)
REQUIRED_GATES = frozenset(
    {
        "evidence_hashes",
        "zero_row_access_boundary",
        "scoped_address_unit",
        "operative_upgrade_clock",
        "single_asset_event_filter",
        "exact_population_certificate",
        "complete_action_semantics",
        "liquidation_separation",
        "outcome_blind_controls",
        "consensus_finality_replication",
        "privacy_and_retention",
        "gpu_lock",
    }
)
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


@dataclass(frozen=True)
class ExposureResiduals:
    """Nonnegative-total residuals at one atomic Comet snapshot."""

    supply_base: int
    borrow_base: int
    collateral: dict[str, int]

    @property
    def complete(self) -> bool:
        """Whether every aggregate-minus-enumerated residual is exactly zero."""

        return self.supply_base == 0 and self.borrow_base == 0 and all(
            value == 0 for value in self.collateral.values()
        )


def load_exposure_control_design(path: str | Path) -> dict[str, object]:
    """Load a zero-row design manifest."""

    value: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("exposure-control design root must be a mapping")
    return cast(dict[str, object], value)


def _mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _strings(value: object) -> tuple[str, ...] | None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        return None
    return tuple(cast(list[str], value))


def _path_is_safe(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and not Path(value).is_absolute()
        and ".." not in Path(value).parts
    )


def _require_exact_keys(
    value: object,
    *,
    expected: frozenset[str],
    path: str,
    errors: list[str],
) -> Mapping[str, object]:
    mapped = _mapping(value)
    if mapped is None or set(mapped) != expected:
        errors.append(f"{path} must contain exactly {sorted(expected)}")
        return {}
    return mapped


def _require_true(mapping: Mapping[str, object], keys: Sequence[str], *, path: str, errors: list[str]) -> None:
    for key in keys:
        if mapping.get(key) is not True:
            errors.append(f"{path}.{key} must be true")


def _require_false(mapping: Mapping[str, object], keys: Sequence[str], *, path: str, errors: list[str]) -> None:
    for key in keys:
        if mapping.get(key) is not False:
            errors.append(f"{path}.{key} must be false")


def validate_exposure_control_design(manifest: Mapping[str, object]) -> list[str]:
    """Return deterministic design and forbidden-access violations."""

    errors: list[str] = []
    if set(manifest) != TOP_LEVEL_KEYS:
        errors.append(f"top level must contain exactly {sorted(TOP_LEVEL_KEYS)}")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION}")
    if manifest.get("stage") != STAGE:
        errors.append(f"stage must equal {STAGE}")
    design_id = manifest.get("design_id")
    if not isinstance(design_id, str) or ID_PATTERN.fullmatch(design_id) is None:
        errors.append("design_id must be a stable lowercase identifier")
    as_of = manifest.get("as_of")
    if not isinstance(as_of, str) or DATE_PATTERN.fullmatch(as_of) is None:
        errors.append("as_of must be an ISO date")

    evidence = _require_exact_keys(
        manifest.get("evidence"), expected=EVIDENCE_KEYS, path="evidence", errors=errors
    )
    for key in ("source_summary_path", "chain_summary_path"):
        if not _path_is_safe(evidence.get(key)):
            errors.append(f"evidence.{key} must be a safe relative path")
    for key in ("source_summary_sha256", "chain_summary_sha256"):
        value = evidence.get(key)
        if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
            errors.append(f"evidence.{key} must be a lowercase SHA-256")
    for key in ("source_commit", "chain_collection_commit"):
        value = evidence.get(key)
        if not isinstance(value, str) or GIT_SHA_PATTERN.fullmatch(value) is None:
            errors.append(f"evidence.{key} must be a full lowercase Git SHA")

    access = _require_exact_keys(
        manifest.get("access_boundary"), expected=ACCESS_KEYS, path="access_boundary", errors=errors
    )
    _require_true(access, ("official_code_blobs_opened",), path="access_boundary", errors=errors)
    _require_false(
        access,
        tuple(sorted(ACCESS_KEYS - {"official_code_blobs_opened"})),
        path="access_boundary",
        errors=errors,
    )

    unit_keys = frozenset(
        {
            "primary_unit",
            "beneficial_person_claimed",
            "cross_market_address_clustered_for_inference",
            "smart_contract_wallet_is_distinct_address_unit",
            "entity_clustering_forbidden",
            "identity_layers",
        }
    )
    unit = _require_exact_keys(
        manifest.get("unit_contract"), expected=unit_keys, path="unit_contract", errors=errors
    )
    if unit.get("primary_unit") != "chain_comet_market_account_address":
        errors.append("unit_contract.primary_unit must preserve the scoped account-address unit")
    _require_true(
        unit,
        (
            "cross_market_address_clustered_for_inference",
            "smart_contract_wallet_is_distinct_address_unit",
            "entity_clustering_forbidden",
        ),
        path="unit_contract",
        errors=errors,
    )
    _require_false(unit, ("beneficial_person_claimed",), path="unit_contract", errors=errors)
    if _strings(unit.get("identity_layers")) != EXPECTED_IDENTITY_LAYERS:
        errors.append("unit_contract.identity_layers must preserve all frozen identity layers")

    treatment_keys = frozenset(
        {
            "eligible_configuration_events",
            "priority_order",
            "excluded_event_classes",
            "required_same_transaction_events",
            "operative_clock",
            "require_single_market",
            "require_single_existing_collateral_asset",
            "require_pre_post_getter_conformance",
            "require_no_other_market_upgrade_in_transaction",
            "contamination_window_seconds",
            "selection_uses_post_event_participant_data",
        }
    )
    treatment = _require_exact_keys(
        manifest.get("treatment_contract"),
        expected=treatment_keys,
        path="treatment_contract",
        errors=errors,
    )
    if _strings(treatment.get("eligible_configuration_events")) != EXPECTED_ELIGIBLE_EVENTS:
        errors.append("treatment_contract.eligible_configuration_events must equal the frozen event set")
    if _strings(treatment.get("priority_order")) != EXPECTED_ELIGIBLE_EVENTS:
        errors.append("treatment_contract.priority_order must equal the frozen ordering")
    excluded = _strings(treatment.get("excluded_event_classes"))
    if excluded is None or frozenset(excluded) != EXPECTED_EXCLUDED_EVENTS:
        errors.append("treatment_contract.excluded_event_classes must equal the frozen exclusions")
    if _strings(treatment.get("required_same_transaction_events")) != EXPECTED_TRANSACTION_EVENTS:
        errors.append("treatment_contract.required_same_transaction_events must preserve atomic linkage")
    if treatment.get("operative_clock") != "comet_proxy_upgraded_log":
        errors.append("treatment_contract.operative_clock must equal comet_proxy_upgraded_log")
    _require_true(
        treatment,
        (
            "require_single_market",
            "require_single_existing_collateral_asset",
            "require_pre_post_getter_conformance",
            "require_no_other_market_upgrade_in_transaction",
        ),
        path="treatment_contract",
        errors=errors,
    )
    _require_false(
        treatment,
        ("selection_uses_post_event_participant_data",),
        path="treatment_contract",
        errors=errors,
    )
    if treatment.get("contamination_window_seconds") != 86_400:
        errors.append("treatment_contract.contamination_window_seconds must equal 86400")

    population_keys = frozenset(
        {
            "enumeration_start",
            "snapshot_block",
            "at_risk_rule",
            "state_owner_events",
            "exclude_zero_address",
            "exact_residual_tolerance",
            "residual_identities",
            "all_residuals_must_equal_zero",
            "require_historical_implementation_source_conformance",
        }
    )
    population = _require_exact_keys(
        manifest.get("population_contract"),
        expected=population_keys,
        path="population_contract",
        errors=errors,
    )
    if population.get("enumeration_start") != "comet_proxy_deployment_block":
        errors.append("population_contract.enumeration_start must equal comet_proxy_deployment_block")
    if population.get("snapshot_block") != "execution_block_minus_one":
        errors.append("population_contract.snapshot_block must equal execution_block_minus_one")
    if population.get("at_risk_rule") != "nonzero_signed_principal_or_any_positive_collateral_balance":
        errors.append("population_contract.at_risk_rule must preserve the frozen nonzero-state rule")
    state_owner_events = population.get("state_owner_events")
    normalized_events: list[tuple[str, tuple[str, ...]]] = []
    if isinstance(state_owner_events, list):
        for index, item in enumerate(state_owner_events):
            mapped = _mapping(item)
            if mapped is None or set(mapped) != {"event", "owner_fields"}:
                errors.append(f"population_contract.state_owner_events[{index}] is malformed")
                continue
            event = mapped.get("event")
            fields = _strings(mapped.get("owner_fields"))
            if isinstance(event, str) and fields is not None:
                normalized_events.append((event, fields))
    else:
        errors.append("population_contract.state_owner_events must be a list")
    if tuple(normalized_events) != EXPECTED_STATE_OWNER_EVENTS:
        errors.append("population_contract.state_owner_events must equal the frozen owner-role map")
    _require_true(
        population,
        (
            "exclude_zero_address",
            "all_residuals_must_equal_zero",
            "require_historical_implementation_source_conformance",
        ),
        path="population_contract",
        errors=errors,
    )
    if population.get("exact_residual_tolerance") != 0:
        errors.append("population_contract.exact_residual_tolerance must equal zero")
    if _strings(population.get("residual_identities")) != EXPECTED_RESIDUAL_IDENTITIES:
        errors.append("population_contract.residual_identities must equal the frozen exact identities")

    action_keys = frozenset(
        {
            "voluntary_channels",
            "liquidation_channel",
            "no_action_label",
            "no_action_does_not_mean_no_intent_or_revert",
            "require_complete_successful_call_traces",
            "logged_event_only_panel_is_complete_claim",
            "require_pre_post_state_reconciliation",
            "response_horizons_seconds",
        }
    )
    action = _require_exact_keys(
        manifest.get("action_contract"), expected=action_keys, path="action_contract", errors=errors
    )
    if _strings(action.get("voluntary_channels")) != EXPECTED_VOLUNTARY_CHANNELS:
        errors.append("action_contract.voluntary_channels must equal the frozen channel list")
    if action.get("liquidation_channel") != "separate_competing_risk":
        errors.append("action_contract.liquidation_channel must remain a separate competing risk")
    if action.get("no_action_label") != "no_successful_state_changing_account_adjustment_in_frozen_window":
        errors.append("action_contract.no_action_label must preserve the scoped successful-action null")
    _require_true(
        action,
        (
            "no_action_does_not_mean_no_intent_or_revert",
            "require_complete_successful_call_traces",
            "require_pre_post_state_reconciliation",
        ),
        path="action_contract",
        errors=errors,
    )
    _require_false(
        action,
        ("logged_event_only_panel_is_complete_claim",),
        path="action_contract",
        errors=errors,
    )
    if action.get("response_horizons_seconds") != [3_600, 86_400, 604_800, 2_419_200]:
        errors.append("action_contract.response_horizons_seconds must equal the frozen four horizons")

    control_keys = frozenset(
        {
            "candidate_families",
            "single_control_family_sufficient",
            "shared_admin_is_independence_evidence",
            "require_payload_level_spillover_audit",
            "require_common_support_before_response_access",
            "maximum_weighted_standardized_mean_difference",
            "minimum_effective_sample_size_per_arm",
            "maximum_top_one_weight_share",
            "maximum_top_ten_weight_share",
            "cluster_by_account_address",
        }
    )
    control = _require_exact_keys(
        manifest.get("control_contract"), expected=control_keys, path="control_contract", errors=errors
    )
    if _strings(control.get("candidate_families")) != EXPECTED_CONTROL_FAMILIES:
        errors.append("control_contract.candidate_families must equal the frozen control set")
    _require_true(
        control,
        (
            "require_payload_level_spillover_audit",
            "require_common_support_before_response_access",
            "cluster_by_account_address",
        ),
        path="control_contract",
        errors=errors,
    )
    _require_false(
        control,
        ("single_control_family_sufficient", "shared_admin_is_independence_evidence"),
        path="control_contract",
        errors=errors,
    )
    expected_control_values = {
        "maximum_weighted_standardized_mean_difference": 0.10,
        "minimum_effective_sample_size_per_arm": 100,
        "maximum_top_one_weight_share": 0.20,
        "maximum_top_ten_weight_share": 0.60,
    }
    for key, expected in expected_control_values.items():
        if control.get(key) != expected:
            errors.append(f"control_contract.{key} must equal {expected}")

    finality_keys = frozenset(
        {
            "confirmation_depth_is_consensus_finality",
            "require_consensus_finalized_execution_block",
            "require_second_execution_provider_block_hash_match",
            "require_beacon_execution_payload_hash_match",
            "provider_substitution_after_freeze",
        }
    )
    finality = _require_exact_keys(
        manifest.get("finality_contract"), expected=finality_keys, path="finality_contract", errors=errors
    )
    _require_true(
        finality,
        (
            "require_consensus_finalized_execution_block",
            "require_second_execution_provider_block_hash_match",
            "require_beacon_execution_payload_hash_match",
        ),
        path="finality_contract",
        errors=errors,
    )
    _require_false(
        finality,
        ("confirmation_depth_is_consensus_finality", "provider_substitution_after_freeze"),
        path="finality_contract",
        errors=errors,
    )

    privacy_keys = frozenset(
        {
            "public_artifacts_contain_raw_account_addresses",
            "internal_longitudinal_id",
            "encrypted_address_crosswalk_required",
            "raw_rpc_payload_publication_forbidden",
            "provider_terms_review_required",
            "human_reidentification_forbidden",
            "code_license_and_chain_data_terms_separate",
        }
    )
    privacy = _require_exact_keys(
        manifest.get("privacy_retention_contract"),
        expected=privacy_keys,
        path="privacy_retention_contract",
        errors=errors,
    )
    if privacy.get("internal_longitudinal_id") != "keyed_hmac_sha256":
        errors.append("privacy_retention_contract.internal_longitudinal_id must equal keyed_hmac_sha256")
    _require_true(
        privacy,
        (
            "encrypted_address_crosswalk_required",
            "raw_rpc_payload_publication_forbidden",
            "provider_terms_review_required",
            "human_reidentification_forbidden",
            "code_license_and_chain_data_terms_separate",
        ),
        path="privacy_retention_contract",
        errors=errors,
    )
    _require_false(
        privacy,
        ("public_artifacts_contain_raw_account_addresses",),
        path="privacy_retention_contract",
        errors=errors,
    )

    gates = _strings(manifest.get("gates"))
    if gates is None or frozenset(gates) != REQUIRED_GATES or len(gates) != len(REQUIRED_GATES):
        errors.append(f"gates must contain exactly {sorted(REQUIRED_GATES)}")
    decision_keys = frozenset({"all_gates_required", "pass", "fail", "authorized_next_stage"})
    decision = _require_exact_keys(
        manifest.get("decision_policy"), expected=decision_keys, path="decision_policy", errors=errors
    )
    if decision.get("all_gates_required") is not True:
        errors.append("decision_policy.all_gates_required must be true")
    for key in ("pass", "fail", "authorized_next_stage"):
        if not isinstance(decision.get(key), str) or not decision[key]:
            errors.append(f"decision_policy.{key} must be non-empty")
    limitations = _strings(manifest.get("limitations"))
    if limitations is None or len(limitations) < 6:
        errors.append("limitations must contain at least six strings")
    return sorted(errors)


def validate_design_evidence(manifest: Mapping[str, object], root: str | Path) -> list[str]:
    """Verify committed prerequisite artifacts without opening any chain row."""

    errors: list[str] = []
    evidence = cast(Mapping[str, object], manifest["evidence"])
    root_path = Path(root)
    contracts = (
        ("source", "source_summary_path", "source_summary_sha256"),
        ("chain", "chain_summary_path", "chain_summary_sha256"),
    )
    summaries: dict[str, Mapping[str, object]] = {}
    for label, path_key, hash_key in contracts:
        path = root_path / cast(str, evidence[path_key])
        if not path.is_file():
            errors.append(f"{label} summary is missing")
            continue
        observed_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed_hash != evidence[hash_key]:
            errors.append(f"{label} summary hash differs from the frozen value")
            continue
        value: object = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, Mapping):
            errors.append(f"{label} summary must be a mapping")
            continue
        summaries[label] = cast(Mapping[str, object], value)
    source = summaries.get("source")
    if source is not None:
        source_record = _mapping(source.get("source"))
        if source.get("decision") != "PASS_SOURCE_METADATA_AUTHORIZE_CHAIN_METADATA_ONLY":
            errors.append("source summary decision is not the frozen pass")
        if source_record is None or source_record.get("commit") != evidence["source_commit"]:
            errors.append("source summary commit differs from the frozen source commit")
    chain = summaries.get("chain")
    if chain is not None:
        if chain.get("decision") != "PASS_CHAIN_METADATA_AUTHORIZE_EXPOSURE_PROTOCOL_DESIGN_ONLY":
            errors.append("chain summary decision is not the frozen pass")
        if chain.get("collection_commit") != evidence["chain_collection_commit"]:
            errors.append("chain summary collection commit differs from the frozen commit")
    return sorted(errors)


def compute_exposure_residuals(
    principals: Mapping[str, int],
    collateral_balances: Mapping[str, Mapping[str, int]],
    *,
    total_supply_base: int,
    total_borrow_base: int,
    totals_collateral: Mapping[str, int],
) -> ExposureResiduals:
    """Compute aggregate-minus-enumerated residuals for one atomic snapshot."""

    if isinstance(total_supply_base, bool) or total_supply_base < 0:
        raise ValueError("total_supply_base must be a nonnegative integer")
    if isinstance(total_borrow_base, bool) or total_borrow_base < 0:
        raise ValueError("total_borrow_base must be a nonnegative integer")
    if any(isinstance(value, bool) or value < 0 for value in totals_collateral.values()):
        raise ValueError("totals_collateral must contain nonnegative integers")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in principals.values()):
        raise ValueError("principals must contain signed integers")
    known_assets = set(totals_collateral)
    observed_collateral = {asset: 0 for asset in known_assets}
    for account, balances in collateral_balances.items():
        if account not in principals:
            raise ValueError("every collateral account must have a principal record")
        unknown_assets = set(balances) - known_assets
        if unknown_assets:
            raise ValueError(f"unknown collateral assets: {sorted(unknown_assets)}")
        for asset, balance in balances.items():
            if isinstance(balance, bool) or not isinstance(balance, int) or balance < 0:
                raise ValueError("collateral balances must be nonnegative integers")
            observed_collateral[asset] += balance
    observed_supply = sum(max(principal, 0) for principal in principals.values())
    observed_borrow = sum(max(-principal, 0) for principal in principals.values())
    return ExposureResiduals(
        supply_base=total_supply_base - observed_supply,
        borrow_base=total_borrow_base - observed_borrow,
        collateral={
            asset: total - observed_collateral[asset]
            for asset, total in sorted(totals_collateral.items())
        },
    )
