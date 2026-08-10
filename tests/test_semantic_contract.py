from __future__ import annotations

import json
from dataclasses import replace

import pytest

from ecomd.observation.semantic_contract import (
    ClockKind,
    ClockSpec,
    ContractValidationError,
    CountLaw,
    DataScope,
    IdentitySemantics,
    LatentAccess,
    ModelInputs,
    NegativeControl,
    ObservableLabel,
    PriceProcess,
    SignAnchor,
    SupportLevel,
    aggregate_bin_p3_contract,
    aggregate_event_p2_contract,
    contract_from_json,
    contract_to_json,
    current_adapter_synthetic_contract,
    run_validated,
    validate_contract,
)


def _mutations():
    bin_contract = aggregate_bin_p3_contract()
    event_contract = aggregate_event_p2_contract()
    return {
        "N1": replace(
            event_contract,
            clock=ClockSpec(
                kind=ClockKind.SIMULATOR_STEP,
                count_law=CountLaw.ONE_PER_TRANSITION,
                physical_seconds=0.005,
            ),
        ),
        "N2": replace(
            event_contract,
            price=replace(
                event_contract.price,
                scored_processes=(PriceProcess.ECOMD_INTERNAL, PriceProcess.EMITTED_BOOK),
                train_only_measurement_link=False,
            ),
        ),
        "N3": replace(
            bin_contract,
            clock=replace(bin_contract.clock, physical_seconds=None),
        ),
        "N4": replace(
            event_contract,
            identity=replace(event_contract.identity, field_name="order_id"),
        ),
        "N5": replace(event_contract, support_level=SupportLevel.INDIVIDUAL_ORDER),
        "N6": replace(
            bin_contract,
            size=replace(bin_contract.size, train_only_measurement_link=False),
        ),
        "N7": replace(
            bin_contract,
            latent=replace(bin_contract.latent, observable_label=ObservableLabel.OFI),
        ),
        "N8": replace(
            bin_contract,
            latent=replace(bin_contract.latent, sign_anchor=SignAnchor.SIGN_FLIPPED),
        ),
        "N9": replace(
            bin_contract,
            latent=replace(bin_contract.latent, access=LatentAccess.TEST_CONDITIONED),
        ),
        "N10": replace(
            bin_contract,
            latent=replace(bin_contract.latent, model_inputs=ModelInputs.OBSERVATION_ONLY),
        ),
        "N11": replace(
            bin_contract,
            latent=replace(
                bin_contract.latent,
                controls=(NegativeControl.OBSERVATION_ONLY,),
            ),
        ),
        "N12": replace(
            bin_contract,
            latent=replace(bin_contract.latent, controls=(NegativeControl.SIGN_FLIP,)),
        ),
    }


EXPECTED_ERRORS = {
    "N1": "EXTERNAL_EVENT_CLOCK_REQUIRES_CONDITIONAL_LAW",
    "N2": "DUAL_PRICE_PROCESS_WITHOUT_LINK",
    "N3": "AGGREGATE_BIN_REQUIRES_PHYSICAL_SECONDS",
    "N4": "EVENT_COUNTER_MUST_NOT_BE_ORDER_ID",
    "N5": "INDIVIDUAL_ORDER_CAPABILITIES_MISSING",
    "N6": "MARKET_SIZE_REQUIRES_TRAIN_ONLY_LINK",
    "N7": "LATENT_PROXY_MUST_NOT_BE_LABELED_OFI",
    "N8": "DIRECTIONAL_SIGN_CONTRADICTS_ANCHOR",
    "N9": "TEST_CONDITIONED_LATENT_FORBIDDEN",
    "N10": "LATENT_CLAIM_REQUIRES_LATENT_INPUT",
    "N11": "SIGN_FLIP_CONTROL_REQUIRED",
    "N12": "OBSERVATION_ONLY_CONTROL_REQUIRED",
}


def test_positive_contracts_have_frozen_reports() -> None:
    synthetic = validate_contract(current_adapter_synthetic_contract())
    aggregate_bin = validate_contract(aggregate_bin_p3_contract())
    aggregate_event = validate_contract(aggregate_event_p2_contract())

    assert synthetic.valid
    assert synthetic.warnings == ("SYNTHETIC_ORDER_ID_IS_EVENT_COUNTER",)
    assert aggregate_bin.valid and aggregate_bin.warnings == ()
    assert aggregate_event.valid and aggregate_event.warnings == ()


@pytest.mark.parametrize(("case", "expected"), EXPECTED_ERRORS.items())
def test_single_defect_mutations_have_exact_error(case: str, expected: str) -> None:
    report = validate_contract(_mutations()[case])
    assert report.errors == (expected,)


def test_canonical_json_round_trip_and_strict_rejection() -> None:
    contract = aggregate_bin_p3_contract()
    encoded = contract_to_json(contract)
    assert contract_from_json(encoded) == contract
    assert contract_to_json(contract_from_json(encoded)) == encoded

    with_unknown = json.loads(encoded)
    with_unknown["unknown"] = True
    with pytest.raises(ValueError, match="unknown"):
        contract_from_json(json.dumps(with_unknown))

    bad_enum = json.loads(encoded)
    bad_enum["support_level"] = "orderish"
    with pytest.raises(ValueError, match="unknown value"):
        contract_from_json(json.dumps(bad_enum))


def test_invalid_contract_never_invokes_callback() -> None:
    calls = 0

    def callback() -> str:
        nonlocal calls
        calls += 1
        return "sentinel"

    with pytest.raises(ContractValidationError) as captured:
        run_validated(_mutations()["N9"], callback)
    assert captured.value.report.errors == ("TEST_CONDITIONED_LATENT_FORBIDDEN",)
    assert calls == 0
    assert run_validated(aggregate_bin_p3_contract(), callback) == "sentinel"
    assert calls == 1


def test_current_adapter_cannot_be_redeclared_external_by_support_only() -> None:
    current = current_adapter_synthetic_contract()
    for support in (
        SupportLevel.AGGREGATE_BIN,
        SupportLevel.AGGREGATE_EVENT,
        SupportLevel.INDIVIDUAL_ORDER,
    ):
        escalated = replace(current, support_level=support, data_scope=DataScope.EXTERNAL)
        report = validate_contract(escalated)
        assert not report.valid
        assert report.requested_support is support
        assert "EVENT_COUNTER_MUST_NOT_BE_ORDER_ID" in report.errors


def test_enum_sequences_are_canonicalized() -> None:
    contract = aggregate_bin_p3_contract()
    reversed_latent = replace(
        contract.latent,
        controls=(NegativeControl.SIGN_FLIP, NegativeControl.OBSERVATION_ONLY),
    )
    duplicated_price = replace(
        contract.price,
        scored_processes=(
            PriceProcess.EXTERNAL_MID,
            PriceProcess.ECOMD_INTERNAL,
            PriceProcess.EXTERNAL_MID,
        ),
    )
    normalized = replace(contract, latent=reversed_latent, price=duplicated_price)
    assert contract_to_json(contract_from_json(contract_to_json(normalized))) == contract_to_json(
        normalized
    )


def test_identity_semantics_remains_explicit() -> None:
    contract = aggregate_event_p2_contract()
    order_named = replace(
        contract,
        identity=replace(
            contract.identity,
            field_name="order_id",
            semantics=IdentitySemantics.EVENT_COUNTER,
        ),
    )
    assert validate_contract(order_named).errors == ("EVENT_COUNTER_MUST_NOT_BE_ORDER_ID",)
