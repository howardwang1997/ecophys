"""Machine-enforced support boundaries for EcoMD observation claims."""

from __future__ import annotations

import json
import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import NoReturn, TypeVar, cast

SCHEMA_VERSION = "ecomd-observation-contract/v1"


class SupportLevel(StrEnum):
    SYNTHETIC_FIXTURE = "synthetic_fixture"
    AGGREGATE_BIN = "aggregate_bin"
    AGGREGATE_EVENT = "aggregate_event"
    INDIVIDUAL_ORDER = "individual_order"


class DataScope(StrEnum):
    GENERATED = "generated"
    EXTERNAL = "external"


class ClockKind(StrEnum):
    SIMULATOR_STEP = "simulator_step"
    FIXED_PHYSICAL_BIN = "fixed_physical_bin"
    CONDITIONAL_EVENT = "conditional_event"
    VENDOR_EVENT = "vendor_event"


class CountLaw(StrEnum):
    ONE_PER_TRANSITION = "one_per_transition"
    AGGREGATED_COUNTS = "aggregated_counts"
    CONDITIONAL_INTENSITY = "conditional_intensity"
    OBSERVED = "observed"


class PriceChoice(StrEnum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class PriceProcess(StrEnum):
    ECOMD_INTERNAL = "ecomd_internal"
    EMITTED_BOOK = "emitted_book"
    EXTERNAL_MID = "external_mid"


class SizeUnit(StrEnum):
    NONE = "none"
    MODEL_COORDINATE = "model_coordinate"
    SHARES = "shares"
    CONTRACTS = "contracts"


class IdentitySemantics(StrEnum):
    NONE = "none"
    EVENT_COUNTER = "event_counter"
    ORDER = "order"


class LatentQuantity(StrEnum):
    NONE = "none"
    LATENT_FLOW_ALIGNMENT = "latent_flow_alignment"


class ObservableLabel(StrEnum):
    NONE = "none"
    LATENT_FLOW_ALIGNMENT = "latent_flow_alignment"
    OFI = "ofi"


class LatentAccess(StrEnum):
    GENERATED = "generated"
    UNCONDITIONAL_TRAIN_CALIBRATED = "unconditional_train_calibrated"
    CAUSAL_FILTER = "causal_filter"
    TEST_CONDITIONED = "test_conditioned"


class SignAnchor(StrEnum):
    NONE = "none"
    FIXED_STRUCTURAL = "fixed_structural"
    SIGN_FLIPPED = "sign_flipped"


class ModelInputs(StrEnum):
    NONE = "none"
    OBSERVATION_ONLY = "observation_only"
    LATENT_ONLY = "latent_only"
    COMBINED = "combined"


class ClaimKind(StrEnum):
    NONE = "none"
    DIRECTIONAL_LATENT = "directional_latent"
    LATENT_INCREMENTAL = "latent_incremental"


class NegativeControl(StrEnum):
    OBSERVATION_ONLY = "observation_only"
    SIGN_FLIP = "sign_flip"


class ErrorCode(StrEnum):
    EXTERNAL_EVENT_CLOCK_REQUIRES_CONDITIONAL_LAW = (
        "EXTERNAL_EVENT_CLOCK_REQUIRES_CONDITIONAL_LAW"
    )
    DUAL_PRICE_PROCESS_WITHOUT_LINK = "DUAL_PRICE_PROCESS_WITHOUT_LINK"
    AGGREGATE_BIN_REQUIRES_PHYSICAL_SECONDS = (
        "AGGREGATE_BIN_REQUIRES_PHYSICAL_SECONDS"
    )
    EVENT_COUNTER_MUST_NOT_BE_ORDER_ID = "EVENT_COUNTER_MUST_NOT_BE_ORDER_ID"
    INDIVIDUAL_ORDER_CAPABILITIES_MISSING = "INDIVIDUAL_ORDER_CAPABILITIES_MISSING"
    MARKET_SIZE_REQUIRES_TRAIN_ONLY_LINK = "MARKET_SIZE_REQUIRES_TRAIN_ONLY_LINK"
    LATENT_PROXY_MUST_NOT_BE_LABELED_OFI = "LATENT_PROXY_MUST_NOT_BE_LABELED_OFI"
    DIRECTIONAL_SIGN_CONTRADICTS_ANCHOR = "DIRECTIONAL_SIGN_CONTRADICTS_ANCHOR"
    TEST_CONDITIONED_LATENT_FORBIDDEN = "TEST_CONDITIONED_LATENT_FORBIDDEN"
    LATENT_CLAIM_REQUIRES_LATENT_INPUT = "LATENT_CLAIM_REQUIRES_LATENT_INPUT"
    SIGN_FLIP_CONTROL_REQUIRED = "SIGN_FLIP_CONTROL_REQUIRED"
    OBSERVATION_ONLY_CONTROL_REQUIRED = "OBSERVATION_ONLY_CONTROL_REQUIRED"
    AGGREGATE_BIN_REQUIRES_FIXED_CLOCK = "AGGREGATE_BIN_REQUIRES_FIXED_CLOCK"
    EXTERNAL_SIZE_UNIT_REQUIRED = "EXTERNAL_SIZE_UNIT_REQUIRED"
    SYNTHETIC_FIXTURE_REQUIRES_GENERATED_SCOPE = (
        "SYNTHETIC_FIXTURE_REQUIRES_GENERATED_SCOPE"
    )
    UNKNOWN_SCHEMA_VERSION = "UNKNOWN_SCHEMA_VERSION"


class WarningCode(StrEnum):
    SYNTHETIC_ORDER_ID_IS_EVENT_COUNTER = "SYNTHETIC_ORDER_ID_IS_EVENT_COUNTER"


@dataclass(frozen=True)
class ClockSpec:
    kind: ClockKind
    count_law: CountLaw
    physical_seconds: float | None


@dataclass(frozen=True)
class PriceSpec:
    choice: PriceChoice
    scored_processes: tuple[PriceProcess, ...]
    train_only_measurement_link: bool

    def __post_init__(self) -> None:
        ordered = tuple(sorted(set(self.scored_processes), key=lambda item: item.value))
        object.__setattr__(self, "scored_processes", ordered)


@dataclass(frozen=True)
class SizeSpec:
    latent_unit: SizeUnit
    observed_unit: SizeUnit
    train_only_measurement_link: bool


@dataclass(frozen=True)
class IdentitySpec:
    field_name: str | None
    semantics: IdentitySemantics
    persistent_lifecycle: bool
    matching_engine: bool
    price_time_priority: bool


@dataclass(frozen=True)
class LatentSpec:
    source_quantity: LatentQuantity
    observable_label: ObservableLabel
    access: LatentAccess
    sign_anchor: SignAnchor
    model_inputs: ModelInputs
    claim: ClaimKind
    controls: tuple[NegativeControl, ...]

    def __post_init__(self) -> None:
        ordered = tuple(sorted(set(self.controls), key=lambda item: item.value))
        object.__setattr__(self, "controls", ordered)


@dataclass(frozen=True)
class ObservationContract:
    schema_version: str
    name: str
    support_level: SupportLevel
    data_scope: DataScope
    clock: ClockSpec
    price: PriceSpec
    size: SizeSpec
    identity: IdentitySpec
    latent: LatentSpec


@dataclass(frozen=True)
class ValidationReport:
    requested_support: SupportLevel
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, object]:
        return {
            "requested_support": self.requested_support.value,
            "valid": self.valid,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }


class ContractValidationError(ValueError):
    """Raised before work starts when an observation contract is invalid."""

    def __init__(self, report: ValidationReport) -> None:
        self.report = report
        super().__init__("invalid observation contract: " + ", ".join(report.errors))


def current_adapter_synthetic_contract() -> ObservationContract:
    """Declare the current EcoMD adapter at its supported synthetic-fixture level."""
    return ObservationContract(
        schema_version=SCHEMA_VERSION,
        name="current_ecomd_l2_adapter_synthetic_only",
        support_level=SupportLevel.SYNTHETIC_FIXTURE,
        data_scope=DataScope.GENERATED,
        clock=ClockSpec(
            kind=ClockKind.SIMULATOR_STEP,
            count_law=CountLaw.ONE_PER_TRANSITION,
            physical_seconds=0.005,
        ),
        price=PriceSpec(
            choice=PriceChoice.P2,
            scored_processes=(PriceProcess.EMITTED_BOOK,),
            train_only_measurement_link=False,
        ),
        size=SizeSpec(
            latent_unit=SizeUnit.MODEL_COORDINATE,
            observed_unit=SizeUnit.MODEL_COORDINATE,
            train_only_measurement_link=False,
        ),
        identity=IdentitySpec(
            field_name="order_id",
            semantics=IdentitySemantics.EVENT_COUNTER,
            persistent_lifecycle=False,
            matching_engine=False,
            price_time_priority=False,
        ),
        latent=LatentSpec(
            source_quantity=LatentQuantity.LATENT_FLOW_ALIGNMENT,
            observable_label=ObservableLabel.LATENT_FLOW_ALIGNMENT,
            access=LatentAccess.GENERATED,
            sign_anchor=SignAnchor.FIXED_STRUCTURAL,
            model_inputs=ModelInputs.COMBINED,
            claim=ClaimKind.LATENT_INCREMENTAL,
            controls=(NegativeControl.SIGN_FLIP, NegativeControl.OBSERVATION_ONLY),
        ),
    )


def aggregate_bin_p3_contract() -> ObservationContract:
    """Declare the narrow external aggregate-bin P3 observation design."""
    return ObservationContract(
        schema_version=SCHEMA_VERSION,
        name="aggregate_bin_p3_external",
        support_level=SupportLevel.AGGREGATE_BIN,
        data_scope=DataScope.EXTERNAL,
        clock=ClockSpec(
            kind=ClockKind.FIXED_PHYSICAL_BIN,
            count_law=CountLaw.AGGREGATED_COUNTS,
            physical_seconds=60.0,
        ),
        price=PriceSpec(
            choice=PriceChoice.P3,
            scored_processes=(PriceProcess.ECOMD_INTERNAL, PriceProcess.EXTERNAL_MID),
            train_only_measurement_link=True,
        ),
        size=SizeSpec(
            latent_unit=SizeUnit.MODEL_COORDINATE,
            observed_unit=SizeUnit.SHARES,
            train_only_measurement_link=True,
        ),
        identity=IdentitySpec(
            field_name=None,
            semantics=IdentitySemantics.NONE,
            persistent_lifecycle=False,
            matching_engine=False,
            price_time_priority=False,
        ),
        latent=LatentSpec(
            source_quantity=LatentQuantity.LATENT_FLOW_ALIGNMENT,
            observable_label=ObservableLabel.LATENT_FLOW_ALIGNMENT,
            access=LatentAccess.UNCONDITIONAL_TRAIN_CALIBRATED,
            sign_anchor=SignAnchor.FIXED_STRUCTURAL,
            model_inputs=ModelInputs.COMBINED,
            claim=ClaimKind.LATENT_INCREMENTAL,
            controls=(NegativeControl.SIGN_FLIP, NegativeControl.OBSERVATION_ONLY),
        ),
    )


def aggregate_event_p2_contract() -> ObservationContract:
    """Declare a structurally admissible, not implementation-attested, event design."""
    return ObservationContract(
        schema_version=SCHEMA_VERSION,
        name="aggregate_event_p2_schema_fixture",
        support_level=SupportLevel.AGGREGATE_EVENT,
        data_scope=DataScope.EXTERNAL,
        clock=ClockSpec(
            kind=ClockKind.CONDITIONAL_EVENT,
            count_law=CountLaw.CONDITIONAL_INTENSITY,
            physical_seconds=1.0,
        ),
        price=PriceSpec(
            choice=PriceChoice.P2,
            scored_processes=(PriceProcess.EMITTED_BOOK,),
            train_only_measurement_link=False,
        ),
        size=SizeSpec(
            latent_unit=SizeUnit.MODEL_COORDINATE,
            observed_unit=SizeUnit.SHARES,
            train_only_measurement_link=True,
        ),
        identity=IdentitySpec(
            field_name="event_id",
            semantics=IdentitySemantics.EVENT_COUNTER,
            persistent_lifecycle=False,
            matching_engine=False,
            price_time_priority=False,
        ),
        latent=LatentSpec(
            source_quantity=LatentQuantity.LATENT_FLOW_ALIGNMENT,
            observable_label=ObservableLabel.LATENT_FLOW_ALIGNMENT,
            access=LatentAccess.CAUSAL_FILTER,
            sign_anchor=SignAnchor.FIXED_STRUCTURAL,
            model_inputs=ModelInputs.COMBINED,
            claim=ClaimKind.LATENT_INCREMENTAL,
            controls=(NegativeControl.SIGN_FLIP, NegativeControl.OBSERVATION_ONLY),
        ),
    )


def validate_contract(contract: ObservationContract) -> ValidationReport:
    """Return deterministic errors without weakening the requested support level."""
    errors: set[str] = set()
    warnings: set[str] = set()

    if contract.schema_version != SCHEMA_VERSION:
        errors.add(ErrorCode.UNKNOWN_SCHEMA_VERSION.value)
    if (
        contract.support_level is SupportLevel.SYNTHETIC_FIXTURE
        and contract.data_scope is not DataScope.GENERATED
    ):
        errors.add(ErrorCode.SYNTHETIC_FIXTURE_REQUIRES_GENERATED_SCOPE.value)
    if contract.support_level is SupportLevel.AGGREGATE_BIN:
        if contract.clock.kind is not ClockKind.FIXED_PHYSICAL_BIN:
            errors.add(ErrorCode.AGGREGATE_BIN_REQUIRES_FIXED_CLOCK.value)
        elif (
            contract.clock.physical_seconds is None
            or not math.isfinite(contract.clock.physical_seconds)
            or contract.clock.physical_seconds <= 0.0
        ):
            errors.add(ErrorCode.AGGREGATE_BIN_REQUIRES_PHYSICAL_SECONDS.value)
    if (
        contract.data_scope is DataScope.EXTERNAL
        and contract.support_level
        in (SupportLevel.AGGREGATE_EVENT, SupportLevel.INDIVIDUAL_ORDER)
        and (
            contract.clock.kind
            not in (ClockKind.CONDITIONAL_EVENT, ClockKind.VENDOR_EVENT)
            or contract.clock.count_law
            not in (CountLaw.CONDITIONAL_INTENSITY, CountLaw.OBSERVED)
        )
    ):
        errors.add(ErrorCode.EXTERNAL_EVENT_CLOCK_REQUIRES_CONDITIONAL_LAW.value)

    price_processes = set(contract.price.scored_processes)
    if (
        PriceProcess.ECOMD_INTERNAL in price_processes
        and PriceProcess.EMITTED_BOOK in price_processes
        and not contract.price.train_only_measurement_link
    ):
        errors.add(ErrorCode.DUAL_PRICE_PROCESS_WITHOUT_LINK.value)

    if contract.data_scope is DataScope.EXTERNAL:
        if contract.size.observed_unit not in (SizeUnit.SHARES, SizeUnit.CONTRACTS):
            errors.add(ErrorCode.EXTERNAL_SIZE_UNIT_REQUIRED.value)
        elif (
            contract.size.latent_unit is SizeUnit.MODEL_COORDINATE
            and not contract.size.train_only_measurement_link
        ):
            errors.add(ErrorCode.MARKET_SIZE_REQUIRES_TRAIN_ONLY_LINK.value)

    if (
        contract.data_scope is DataScope.EXTERNAL
        and contract.identity.field_name == "order_id"
        and contract.identity.semantics is not IdentitySemantics.ORDER
    ):
        errors.add(ErrorCode.EVENT_COUNTER_MUST_NOT_BE_ORDER_ID.value)
    if contract.support_level is SupportLevel.INDIVIDUAL_ORDER and not (
        contract.identity.semantics is IdentitySemantics.ORDER
        and contract.identity.persistent_lifecycle
        and contract.identity.matching_engine
        and contract.identity.price_time_priority
    ):
        errors.add(ErrorCode.INDIVIDUAL_ORDER_CAPABILITIES_MISSING.value)
    if (
        contract.support_level is SupportLevel.SYNTHETIC_FIXTURE
        and contract.identity.field_name == "order_id"
        and contract.identity.semantics is IdentitySemantics.EVENT_COUNTER
    ):
        warnings.add(WarningCode.SYNTHETIC_ORDER_ID_IS_EVENT_COUNTER.value)

    if (
        contract.latent.source_quantity is LatentQuantity.LATENT_FLOW_ALIGNMENT
        and contract.latent.observable_label is ObservableLabel.OFI
    ):
        errors.add(ErrorCode.LATENT_PROXY_MUST_NOT_BE_LABELED_OFI.value)
    if contract.latent.access is LatentAccess.TEST_CONDITIONED:
        errors.add(ErrorCode.TEST_CONDITIONED_LATENT_FORBIDDEN.value)
    latent_claim = contract.latent.claim in (
        ClaimKind.DIRECTIONAL_LATENT,
        ClaimKind.LATENT_INCREMENTAL,
    )
    if latent_claim and contract.latent.sign_anchor is SignAnchor.SIGN_FLIPPED:
        errors.add(ErrorCode.DIRECTIONAL_SIGN_CONTRADICTS_ANCHOR.value)
    if latent_claim and contract.latent.model_inputs in (
        ModelInputs.NONE,
        ModelInputs.OBSERVATION_ONLY,
    ):
        errors.add(ErrorCode.LATENT_CLAIM_REQUIRES_LATENT_INPUT.value)
    controls = set(contract.latent.controls)
    if latent_claim and NegativeControl.SIGN_FLIP not in controls:
        errors.add(ErrorCode.SIGN_FLIP_CONTROL_REQUIRED.value)
    if (
        contract.latent.claim is ClaimKind.LATENT_INCREMENTAL
        and NegativeControl.OBSERVATION_ONLY not in controls
    ):
        errors.add(ErrorCode.OBSERVATION_ONLY_CONTROL_REQUIRED.value)

    return ValidationReport(
        requested_support=contract.support_level,
        errors=tuple(sorted(errors)),
        warnings=tuple(sorted(warnings)),
    )


ResultT = TypeVar("ResultT")


def run_validated(contract: ObservationContract, callback: Callable[[], ResultT]) -> ResultT:
    """Invoke ``callback`` only after the support declaration passes validation."""
    report = validate_contract(contract)
    if not report.valid:
        raise ContractValidationError(report)
    return callback()


def contract_to_dict(contract: ObservationContract) -> dict[str, object]:
    """Serialize a contract to its canonical JSON-safe mapping."""
    return {
        "schema_version": contract.schema_version,
        "name": contract.name,
        "support_level": contract.support_level.value,
        "data_scope": contract.data_scope.value,
        "clock": {
            "kind": contract.clock.kind.value,
            "count_law": contract.clock.count_law.value,
            "physical_seconds": contract.clock.physical_seconds,
        },
        "price": {
            "choice": contract.price.choice.value,
            "scored_processes": [item.value for item in contract.price.scored_processes],
            "train_only_measurement_link": contract.price.train_only_measurement_link,
        },
        "size": {
            "latent_unit": contract.size.latent_unit.value,
            "observed_unit": contract.size.observed_unit.value,
            "train_only_measurement_link": contract.size.train_only_measurement_link,
        },
        "identity": {
            "field_name": contract.identity.field_name,
            "semantics": contract.identity.semantics.value,
            "persistent_lifecycle": contract.identity.persistent_lifecycle,
            "matching_engine": contract.identity.matching_engine,
            "price_time_priority": contract.identity.price_time_priority,
        },
        "latent": {
            "source_quantity": contract.latent.source_quantity.value,
            "observable_label": contract.latent.observable_label.value,
            "access": contract.latent.access.value,
            "sign_anchor": contract.latent.sign_anchor.value,
            "model_inputs": contract.latent.model_inputs.value,
            "claim": contract.latent.claim.value,
            "controls": [item.value for item in contract.latent.controls],
        },
    }


def contract_to_json(contract: ObservationContract) -> str:
    """Return deterministic compact JSON for hashing and comparison."""
    return json.dumps(
        contract_to_dict(contract),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


EnumT = TypeVar("EnumT", bound=StrEnum)


def _strict_mapping(value: object, expected: set[str], path: str) -> Mapping[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{path} must be an object with string keys")
    mapping = cast(dict[str, object], value)
    actual = set(mapping)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        raise ValueError(f"{path} keys differ: missing={missing}, unknown={unknown}")
    return mapping


def _string(mapping: Mapping[str, object], key: str, path: str) -> str:
    value = mapping[key]
    if not isinstance(value, str):
        raise ValueError(f"{path}.{key} must be a string")
    return value


def _optional_string(mapping: Mapping[str, object], key: str, path: str) -> str | None:
    value = mapping[key]
    if value is not None and not isinstance(value, str):
        raise ValueError(f"{path}.{key} must be a string or null")
    return value


def _boolean(mapping: Mapping[str, object], key: str, path: str) -> bool:
    value = mapping[key]
    if not isinstance(value, bool):
        raise ValueError(f"{path}.{key} must be a boolean")
    return value


def _optional_float(mapping: Mapping[str, object], key: str, path: str) -> float | None:
    value = mapping[key]
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{path}.{key} must be numeric or null")
    return float(value)


def _enum_value(
    enum_type: type[EnumT], mapping: Mapping[str, object], key: str, path: str
) -> EnumT:
    value = _string(mapping, key, path)
    try:
        return enum_type(value)
    except ValueError as error:
        raise ValueError(f"{path}.{key} has unknown value {value!r}") from error


def _enum_tuple(
    enum_type: type[EnumT], mapping: Mapping[str, object], key: str, path: str
) -> tuple[EnumT, ...]:
    value = mapping[key]
    if not isinstance(value, list):
        raise ValueError(f"{path}.{key} must be an array")
    result: list[EnumT] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise ValueError(f"{path}.{key}[{index}] must be a string")
        try:
            result.append(enum_type(item))
        except ValueError as error:
            raise ValueError(f"{path}.{key}[{index}] has unknown value {item!r}") from error
    return tuple(result)


def contract_from_dict(payload: object) -> ObservationContract:
    """Parse a strict contract mapping, rejecting unknown and missing fields."""
    root = _strict_mapping(
        payload,
        {"schema_version", "name", "support_level", "data_scope", "clock", "price", "size", "identity", "latent"},
        "contract",
    )
    clock = _strict_mapping(
        root["clock"], {"kind", "count_law", "physical_seconds"}, "contract.clock"
    )
    price = _strict_mapping(
        root["price"],
        {"choice", "scored_processes", "train_only_measurement_link"},
        "contract.price",
    )
    size = _strict_mapping(
        root["size"],
        {"latent_unit", "observed_unit", "train_only_measurement_link"},
        "contract.size",
    )
    identity = _strict_mapping(
        root["identity"],
        {"field_name", "semantics", "persistent_lifecycle", "matching_engine", "price_time_priority"},
        "contract.identity",
    )
    latent = _strict_mapping(
        root["latent"],
        {"source_quantity", "observable_label", "access", "sign_anchor", "model_inputs", "claim", "controls"},
        "contract.latent",
    )
    return ObservationContract(
        schema_version=_string(root, "schema_version", "contract"),
        name=_string(root, "name", "contract"),
        support_level=_enum_value(SupportLevel, root, "support_level", "contract"),
        data_scope=_enum_value(DataScope, root, "data_scope", "contract"),
        clock=ClockSpec(
            kind=_enum_value(ClockKind, clock, "kind", "contract.clock"),
            count_law=_enum_value(CountLaw, clock, "count_law", "contract.clock"),
            physical_seconds=_optional_float(clock, "physical_seconds", "contract.clock"),
        ),
        price=PriceSpec(
            choice=_enum_value(PriceChoice, price, "choice", "contract.price"),
            scored_processes=_enum_tuple(
                PriceProcess, price, "scored_processes", "contract.price"
            ),
            train_only_measurement_link=_boolean(
                price, "train_only_measurement_link", "contract.price"
            ),
        ),
        size=SizeSpec(
            latent_unit=_enum_value(SizeUnit, size, "latent_unit", "contract.size"),
            observed_unit=_enum_value(SizeUnit, size, "observed_unit", "contract.size"),
            train_only_measurement_link=_boolean(
                size, "train_only_measurement_link", "contract.size"
            ),
        ),
        identity=IdentitySpec(
            field_name=_optional_string(identity, "field_name", "contract.identity"),
            semantics=_enum_value(
                IdentitySemantics, identity, "semantics", "contract.identity"
            ),
            persistent_lifecycle=_boolean(
                identity, "persistent_lifecycle", "contract.identity"
            ),
            matching_engine=_boolean(identity, "matching_engine", "contract.identity"),
            price_time_priority=_boolean(
                identity, "price_time_priority", "contract.identity"
            ),
        ),
        latent=LatentSpec(
            source_quantity=_enum_value(
                LatentQuantity, latent, "source_quantity", "contract.latent"
            ),
            observable_label=_enum_value(
                ObservableLabel, latent, "observable_label", "contract.latent"
            ),
            access=_enum_value(LatentAccess, latent, "access", "contract.latent"),
            sign_anchor=_enum_value(
                SignAnchor, latent, "sign_anchor", "contract.latent"
            ),
            model_inputs=_enum_value(
                ModelInputs, latent, "model_inputs", "contract.latent"
            ),
            claim=_enum_value(ClaimKind, latent, "claim", "contract.latent"),
            controls=_enum_tuple(
                NegativeControl, latent, "controls", "contract.latent"
            ),
        ),
    )


def _reject_json_constant(value: str) -> NoReturn:
    raise ValueError(f"non-finite JSON constant {value!r} is forbidden")


def contract_from_json(payload: str) -> ObservationContract:
    """Parse canonical or pretty JSON using the strict schema parser."""
    parsed = cast(object, json.loads(payload, parse_constant=_reject_json_constant))
    return contract_from_dict(parsed)
