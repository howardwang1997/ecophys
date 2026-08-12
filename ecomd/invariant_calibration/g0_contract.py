"""Machine-checkable admission contract for Plan v4 G0 re-entry."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TypeVar, cast

import yaml

SCHEMA_VERSION = "ecomd-ncs-g0-candidate/v1"


class AdmissionStatus(StrEnum):
    INCOMPLETE = "INCOMPLETE"
    REJECTED_EQUIVALENT = "REJECTED_EQUIVALENT"
    NOT_FALSIFIABLE = "NOT_FALSIFIABLE"
    ECO_MD_ONLY = "ECO_MD_ONLY"
    BASELINES_MISSING = "BASELINES_MISSING"
    READY_FOR_HUMAN_AUDIT = "READY_FOR_HUMAN_AUDIT"


class ReasonCode(StrEnum):
    NOT_FROZEN_BEFORE_IMPLEMENTATION = "NOT_FROZEN_BEFORE_IMPLEMENTATION"
    MATHEMATICAL_OBJECT_INCOMPLETE = "MATHEMATICAL_OBJECT_INCOMPLETE"
    ASSUMPTIONS_MISSING = "ASSUMPTIONS_MISSING"
    FORMAL_PRIMITIVE_MISSING = "FORMAL_PRIMITIVE_MISSING"
    THEOREM_OBLIGATION_MISSING = "THEOREM_OBLIGATION_MISSING"
    PROOF_SKETCH_MISSING = "PROOF_SKETCH_MISSING"
    PRIOR_ART_FAMILY_MISSING = "PRIOR_ART_FAMILY_MISSING"
    PRIOR_ART_SCOPE_INCOMPLETE = "PRIOR_ART_SCOPE_INCOMPLETE"
    CLAIM_BOUNDARY_INCOMPLETE = "CLAIM_BOUNDARY_INCOMPLETE"
    DATA_SCOPE_BEFORE_G0_INVALID = "DATA_SCOPE_BEFORE_G0_INVALID"
    MARKET_DATA_BEFORE_G0 = "MARKET_DATA_BEFORE_G0"
    SEALED_DATA_BEFORE_G0 = "SEALED_DATA_BEFORE_G0"
    GPU_BEFORE_G0 = "GPU_BEFORE_G0"
    DECLARED_COMPOSITION_ONLY = "DECLARED_COMPOSITION_ONLY"
    NOVELTY_BASIS_NOT_FORMAL = "NOVELTY_BASIS_NOT_FORMAL"
    NON_EQUIVALENCE_WITNESS_INCOMPLETE = "NON_EQUIVALENCE_WITNESS_INCOMPLETE"
    COUNTEREXAMPLES_INSUFFICIENT = "COUNTEREXAMPLES_INSUFFICIENT"
    SLOW_MIXING_OR_METASTABLE_CASE_MISSING = (
        "SLOW_MIXING_OR_METASTABLE_CASE_MISSING"
    )
    INDEPENDENT_SYSTEMS_INSUFFICIENT = "INDEPENDENT_SYSTEMS_INSUFFICIENT"
    ECO_MD_ONLY_BENCHMARK = "ECO_MD_ONLY_BENCHMARK"
    BASELINE_FAMILY_MISSING = "BASELINE_FAMILY_MISSING"
    BASELINE_SPEC_INCOMPLETE = "BASELINE_SPEC_INCOMPLETE"
    COMPUTE_MATCHING_MISSING = "COMPUTE_MATCHING_MISSING"
    REQUIRED_METRIC_MISSING = "REQUIRED_METRIC_MISSING"
    HUMAN_AUDIT_REQUIRED = "HUMAN_AUDIT_REQUIRED"


class PrimitiveCategory(StrEnum):
    CROSS_PARAMETER_COUPLING = "cross_parameter_coupling"
    FINITE_BUDGET_RESIDUAL = "finite_budget_residual"
    VARIANCE_COST = "variance_cost"
    OTHER_FORMAL_IDENTITY = "other_formal_identity"


class NoveltyBasis(StrEnum):
    FORMAL_IDENTITY_OR_THEOREM = "formal_identity_or_theorem"
    PERFORMANCE = "performance"
    APPLICATION = "application"
    COMPOSITION = "composition"


class MethodFamily(StrEnum):
    PERSISTENT_MARKOV = "persistent_markov_pcd_soul"
    SEQUENTIAL_REWEIGHTING = "sequential_reweighting_smc_jarzynski"
    STEADY_STATE_SENSITIVITY = "steady_state_lr_pathwise"
    STOCHASTIC_EVENT_GRADIENT = "stochastic_adjoint_stochasticad_gge"
    COUPLED_DEBIASING = "coupled_debiasing_rhee_glynn"
    LONG_HORIZON_BPTT = "long_full_truncated_bptt"


class CoverageDisposition(StrEnum):
    COVERED = "covered"
    NOT_APPLICABLE = "not_applicable"


class BaselineDisposition(StrEnum):
    INCLUDED = "included"
    NOT_APPLICABLE = "not_applicable"


class CounterexampleFamily(StrEnum):
    SLOW_MIXING = "slow_mixing"
    METASTABLE = "metastable"
    DISCONTINUOUS_EVENT = "discontinuous_event"
    MISSPECIFIED_INVARIANT = "misspecified_invariant"
    OTHER = "other"


@dataclass(frozen=True)
class MathematicalObject:
    state_space: str
    transition_law: str
    invariant_or_path_measure: str
    target_derivative: str
    estimator_or_identity: str
    assumptions: tuple[str, ...]
    formal_difference_statement: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "assumptions", _sorted_unique(self.assumptions))


@dataclass(frozen=True)
class PrimitiveClaim:
    category: PrimitiveCategory
    novelty_basis: NoveltyBasis
    statement: str
    theorem_obligation: str
    proof_sketch: str
    composition_only: bool


@dataclass(frozen=True)
class PriorArtEntry:
    family: MethodFamily
    source_id: str
    primary_url: str
    equation_or_theorem: str
    disposition: CoverageDisposition
    candidate_difference: str


@dataclass(frozen=True)
class NonEquivalenceWitness:
    symbolic_difference: str
    controlled_problem: str
    candidate_prediction: str
    nearest_composition_prediction: str
    rejection_rule: str


@dataclass(frozen=True)
class Counterexample:
    counterexample_id: str
    family: CounterexampleFamily
    construction: str
    expected_failure: str
    rejection_rule: str


@dataclass(frozen=True)
class BaselineEntry:
    family: MethodFamily
    disposition: BaselineDisposition
    implementation: str
    justification: str
    compute_match_rule: str


@dataclass(frozen=True)
class BenchmarkBlueprint:
    independent_systems: tuple[str, ...]
    baselines: tuple[BaselineEntry, ...]
    metrics: tuple[str, ...]
    compute_matched: bool

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "independent_systems", _sorted_unique(self.independent_systems)
        )
        object.__setattr__(
            self, "baselines", tuple(sorted(self.baselines, key=lambda item: item.family.value))
        )
        object.__setattr__(self, "metrics", _sorted_unique(self.metrics))


@dataclass(frozen=True)
class ClaimBoundary:
    not_proved: tuple[str, ...]
    diagnostic_only: tuple[str, ...]
    stop_rule: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "not_proved", _sorted_unique(self.not_proved))
        object.__setattr__(self, "diagnostic_only", _sorted_unique(self.diagnostic_only))


@dataclass(frozen=True)
class ResourceRequest:
    data_scope: str
    uses_market_data: bool
    opens_sealed_data: bool
    gpu_hours: float


@dataclass(frozen=True)
class CandidateContract:
    schema_version: str
    candidate_id: str
    version: str
    frozen_before_implementation: bool
    mathematical_object: MathematicalObject
    primitive: PrimitiveClaim
    prior_art: tuple[PriorArtEntry, ...]
    witness: NonEquivalenceWitness
    counterexamples: tuple[Counterexample, ...]
    benchmark: BenchmarkBlueprint
    claim_boundary: ClaimBoundary
    resources: ResourceRequest

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "prior_art", tuple(sorted(self.prior_art, key=lambda item: item.family.value))
        )
        object.__setattr__(
            self,
            "counterexamples",
            tuple(sorted(self.counterexamples, key=lambda item: item.counterexample_id)),
        )


@dataclass(frozen=True)
class AdmissionReport:
    status: AdmissionStatus
    reason_codes: tuple[str, ...]
    candidate_sha256: str
    automated_novelty_pass: bool = False

    @property
    def human_review_required(self) -> bool:
        return self.status is AdmissionStatus.READY_FOR_HUMAN_AUDIT

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status.value,
            "reason_codes": list(self.reason_codes),
            "candidate_sha256": self.candidate_sha256,
            "automated_novelty_pass": self.automated_novelty_pass,
            "human_review_required": self.human_review_required,
        }


REQUIRED_METHOD_FAMILIES = frozenset(MethodFamily)
REQUIRED_METRICS = frozenset(
    {"accuracy", "bias", "variance", "simulator_steps", "wall_time", "peak_memory", "failure_rate"}
)
ALLOWED_PRE_G0_DATA_SCOPES = frozenset(
    {"generated_metadata_only", "literature_only", "generated_metadata_and_literature"}
)


def assess_candidate(candidate: CandidateContract) -> AdmissionReport:
    """Apply deterministic process gates without making a novelty judgment."""
    if candidate.schema_version != SCHEMA_VERSION:
        raise ValueError(
            f"unsupported schema_version {candidate.schema_version!r}; expected {SCHEMA_VERSION!r}"
        )

    equivalence = _equivalence_reasons(candidate)
    completeness = _completeness_reasons(candidate)
    falsifiability = _falsifiability_reasons(candidate)
    independence = _independence_reasons(candidate)
    baseline = _baseline_reasons(candidate)

    if equivalence:
        status = AdmissionStatus.REJECTED_EQUIVALENT
        reasons = equivalence
    elif completeness:
        status = AdmissionStatus.INCOMPLETE
        reasons = completeness
    elif falsifiability:
        status = AdmissionStatus.NOT_FALSIFIABLE
        reasons = falsifiability
    elif independence:
        status = AdmissionStatus.ECO_MD_ONLY
        reasons = independence
    elif baseline:
        status = AdmissionStatus.BASELINES_MISSING
        reasons = baseline
    else:
        status = AdmissionStatus.READY_FOR_HUMAN_AUDIT
        reasons = {ReasonCode.HUMAN_AUDIT_REQUIRED.value}

    return AdmissionReport(
        status=status,
        reason_codes=tuple(sorted(reasons)),
        candidate_sha256=candidate_sha256(candidate),
    )


def _equivalence_reasons(candidate: CandidateContract) -> set[str]:
    reasons: set[str] = set()
    if candidate.primitive.composition_only:
        reasons.add(ReasonCode.DECLARED_COMPOSITION_ONLY.value)
    if candidate.primitive.novelty_basis is not NoveltyBasis.FORMAL_IDENTITY_OR_THEOREM:
        reasons.add(ReasonCode.NOVELTY_BASIS_NOT_FORMAL.value)
    return reasons


def _completeness_reasons(candidate: CandidateContract) -> set[str]:
    reasons: set[str] = set()
    if not candidate.frozen_before_implementation:
        reasons.add(ReasonCode.NOT_FROZEN_BEFORE_IMPLEMENTATION.value)
    mathematical_fields = (
        candidate.candidate_id,
        candidate.version,
        candidate.mathematical_object.state_space,
        candidate.mathematical_object.transition_law,
        candidate.mathematical_object.invariant_or_path_measure,
        candidate.mathematical_object.target_derivative,
        candidate.mathematical_object.estimator_or_identity,
        candidate.mathematical_object.formal_difference_statement,
    )
    if not all(_has_text(value) for value in mathematical_fields):
        reasons.add(ReasonCode.MATHEMATICAL_OBJECT_INCOMPLETE.value)
    if not candidate.mathematical_object.assumptions or not all(
        _has_text(value) for value in candidate.mathematical_object.assumptions
    ):
        reasons.add(ReasonCode.ASSUMPTIONS_MISSING.value)
    if not _has_text(candidate.primitive.statement):
        reasons.add(ReasonCode.FORMAL_PRIMITIVE_MISSING.value)
    if not _has_text(candidate.primitive.theorem_obligation):
        reasons.add(ReasonCode.THEOREM_OBLIGATION_MISSING.value)
    if not _has_text(candidate.primitive.proof_sketch):
        reasons.add(ReasonCode.PROOF_SKETCH_MISSING.value)

    prior_families = [entry.family for entry in candidate.prior_art]
    if set(prior_families) != REQUIRED_METHOD_FAMILIES or len(prior_families) != len(
        REQUIRED_METHOD_FAMILIES
    ):
        reasons.add(ReasonCode.PRIOR_ART_FAMILY_MISSING.value)
    for entry in candidate.prior_art:
        if not all(
            (
                _has_text(entry.source_id),
                _is_primary_url(entry.primary_url),
                _has_text(entry.equation_or_theorem),
                _has_text(entry.candidate_difference),
            )
        ):
            reasons.add(ReasonCode.PRIOR_ART_SCOPE_INCOMPLETE.value)

    if (
        not candidate.claim_boundary.not_proved
        or not candidate.claim_boundary.diagnostic_only
        or not _has_text(candidate.claim_boundary.stop_rule)
    ):
        reasons.add(ReasonCode.CLAIM_BOUNDARY_INCOMPLETE.value)
    if candidate.resources.data_scope not in ALLOWED_PRE_G0_DATA_SCOPES:
        reasons.add(ReasonCode.DATA_SCOPE_BEFORE_G0_INVALID.value)
    if candidate.resources.uses_market_data:
        reasons.add(ReasonCode.MARKET_DATA_BEFORE_G0.value)
    if candidate.resources.opens_sealed_data:
        reasons.add(ReasonCode.SEALED_DATA_BEFORE_G0.value)
    if not math.isfinite(candidate.resources.gpu_hours) or candidate.resources.gpu_hours != 0.0:
        reasons.add(ReasonCode.GPU_BEFORE_G0.value)
    return reasons


def _falsifiability_reasons(candidate: CandidateContract) -> set[str]:
    reasons: set[str] = set()
    witness_fields = (
        candidate.witness.symbolic_difference,
        candidate.witness.controlled_problem,
        candidate.witness.candidate_prediction,
        candidate.witness.nearest_composition_prediction,
        candidate.witness.rejection_rule,
    )
    if not all(_has_text(value) for value in witness_fields):
        reasons.add(ReasonCode.NON_EQUIVALENCE_WITNESS_INCOMPLETE.value)
    if len({item.counterexample_id for item in candidate.counterexamples}) < 2 or any(
        not all(
            (
                _has_text(item.counterexample_id),
                _has_text(item.construction),
                _has_text(item.expected_failure),
                _has_text(item.rejection_rule),
            )
        )
        for item in candidate.counterexamples
    ):
        reasons.add(ReasonCode.COUNTEREXAMPLES_INSUFFICIENT.value)
    if not any(
        item.family in (CounterexampleFamily.SLOW_MIXING, CounterexampleFamily.METASTABLE)
        for item in candidate.counterexamples
    ):
        reasons.add(ReasonCode.SLOW_MIXING_OR_METASTABLE_CASE_MISSING.value)
    return reasons


def _independence_reasons(candidate: CandidateContract) -> set[str]:
    systems = [item for item in candidate.benchmark.independent_systems if _has_text(item)]
    non_ecomd = [item for item in systems if "ecomd" not in item.casefold()]
    reasons: set[str] = set()
    if systems and not non_ecomd:
        reasons.add(ReasonCode.ECO_MD_ONLY_BENCHMARK.value)
    if len(set(non_ecomd)) < 2:
        reasons.add(ReasonCode.INDEPENDENT_SYSTEMS_INSUFFICIENT.value)
    return reasons


def _baseline_reasons(candidate: CandidateContract) -> set[str]:
    reasons: set[str] = set()
    families = [entry.family for entry in candidate.benchmark.baselines]
    if set(families) != REQUIRED_METHOD_FAMILIES or len(families) != len(
        REQUIRED_METHOD_FAMILIES
    ):
        reasons.add(ReasonCode.BASELINE_FAMILY_MISSING.value)
    for entry in candidate.benchmark.baselines:
        if entry.disposition is BaselineDisposition.INCLUDED:
            complete = all(
                (
                    _has_text(entry.implementation),
                    _has_text(entry.justification),
                    _has_text(entry.compute_match_rule),
                )
            )
        else:
            complete = _has_text(entry.justification)
        if not complete:
            reasons.add(ReasonCode.BASELINE_SPEC_INCOMPLETE.value)
    if not candidate.benchmark.compute_matched:
        reasons.add(ReasonCode.COMPUTE_MATCHING_MISSING.value)
    if not REQUIRED_METRICS.issubset(candidate.benchmark.metrics):
        reasons.add(ReasonCode.REQUIRED_METRIC_MISSING.value)
    return reasons


def candidate_to_dict(candidate: CandidateContract) -> dict[str, object]:
    """Serialize a candidate to its canonical JSON-safe mapping."""
    return {
        "schema_version": candidate.schema_version,
        "candidate_id": candidate.candidate_id,
        "version": candidate.version,
        "frozen_before_implementation": candidate.frozen_before_implementation,
        "mathematical_object": {
            "state_space": candidate.mathematical_object.state_space,
            "transition_law": candidate.mathematical_object.transition_law,
            "invariant_or_path_measure": candidate.mathematical_object.invariant_or_path_measure,
            "target_derivative": candidate.mathematical_object.target_derivative,
            "estimator_or_identity": candidate.mathematical_object.estimator_or_identity,
            "assumptions": list(candidate.mathematical_object.assumptions),
            "formal_difference_statement": candidate.mathematical_object.formal_difference_statement,
        },
        "primitive": {
            "category": candidate.primitive.category.value,
            "novelty_basis": candidate.primitive.novelty_basis.value,
            "statement": candidate.primitive.statement,
            "theorem_obligation": candidate.primitive.theorem_obligation,
            "proof_sketch": candidate.primitive.proof_sketch,
            "composition_only": candidate.primitive.composition_only,
        },
        "prior_art": [
            {
                "family": entry.family.value,
                "source_id": entry.source_id,
                "primary_url": entry.primary_url,
                "equation_or_theorem": entry.equation_or_theorem,
                "disposition": entry.disposition.value,
                "candidate_difference": entry.candidate_difference,
            }
            for entry in candidate.prior_art
        ],
        "witness": {
            "symbolic_difference": candidate.witness.symbolic_difference,
            "controlled_problem": candidate.witness.controlled_problem,
            "candidate_prediction": candidate.witness.candidate_prediction,
            "nearest_composition_prediction": candidate.witness.nearest_composition_prediction,
            "rejection_rule": candidate.witness.rejection_rule,
        },
        "counterexamples": [
            {
                "counterexample_id": item.counterexample_id,
                "family": item.family.value,
                "construction": item.construction,
                "expected_failure": item.expected_failure,
                "rejection_rule": item.rejection_rule,
            }
            for item in candidate.counterexamples
        ],
        "benchmark": {
            "independent_systems": list(candidate.benchmark.independent_systems),
            "baselines": [
                {
                    "family": entry.family.value,
                    "disposition": entry.disposition.value,
                    "implementation": entry.implementation,
                    "justification": entry.justification,
                    "compute_match_rule": entry.compute_match_rule,
                }
                for entry in candidate.benchmark.baselines
            ],
            "metrics": list(candidate.benchmark.metrics),
            "compute_matched": candidate.benchmark.compute_matched,
        },
        "claim_boundary": {
            "not_proved": list(candidate.claim_boundary.not_proved),
            "diagnostic_only": list(candidate.claim_boundary.diagnostic_only),
            "stop_rule": candidate.claim_boundary.stop_rule,
        },
        "resources": {
            "data_scope": candidate.resources.data_scope,
            "uses_market_data": candidate.resources.uses_market_data,
            "opens_sealed_data": candidate.resources.opens_sealed_data,
            "gpu_hours": candidate.resources.gpu_hours,
        },
    }


def candidate_to_json(candidate: CandidateContract) -> str:
    """Return deterministic compact JSON for hashing and comparison."""
    return json.dumps(
        candidate_to_dict(candidate), sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def candidate_sha256(candidate: CandidateContract) -> str:
    """Hash the semantic candidate contract, independent of YAML key order."""
    return hashlib.sha256(candidate_to_json(candidate).encode()).hexdigest()


def load_candidate(path: Path) -> CandidateContract:
    """Load a strict YAML candidate contract."""
    return candidate_from_dict(yaml.safe_load(path.read_text()))


def candidate_from_dict(payload: object) -> CandidateContract:
    """Parse a strict mapping and reject unknown or missing fields."""
    root = _strict_mapping(
        payload,
        {
            "schema_version",
            "candidate_id",
            "version",
            "frozen_before_implementation",
            "mathematical_object",
            "primitive",
            "prior_art",
            "witness",
            "counterexamples",
            "benchmark",
            "claim_boundary",
            "resources",
        },
        "candidate",
    )
    mathematical = _strict_mapping(
        root["mathematical_object"],
        {
            "state_space",
            "transition_law",
            "invariant_or_path_measure",
            "target_derivative",
            "estimator_or_identity",
            "assumptions",
            "formal_difference_statement",
        },
        "candidate.mathematical_object",
    )
    primitive = _strict_mapping(
        root["primitive"],
        {
            "category",
            "novelty_basis",
            "statement",
            "theorem_obligation",
            "proof_sketch",
            "composition_only",
        },
        "candidate.primitive",
    )
    witness = _strict_mapping(
        root["witness"],
        {
            "symbolic_difference",
            "controlled_problem",
            "candidate_prediction",
            "nearest_composition_prediction",
            "rejection_rule",
        },
        "candidate.witness",
    )
    benchmark = _strict_mapping(
        root["benchmark"],
        {"independent_systems", "baselines", "metrics", "compute_matched"},
        "candidate.benchmark",
    )
    boundary = _strict_mapping(
        root["claim_boundary"],
        {"not_proved", "diagnostic_only", "stop_rule"},
        "candidate.claim_boundary",
    )
    resources = _strict_mapping(
        root["resources"],
        {"data_scope", "uses_market_data", "opens_sealed_data", "gpu_hours"},
        "candidate.resources",
    )
    return CandidateContract(
        schema_version=_string(root, "schema_version", "candidate"),
        candidate_id=_string(root, "candidate_id", "candidate"),
        version=_string(root, "version", "candidate"),
        frozen_before_implementation=_boolean(
            root, "frozen_before_implementation", "candidate"
        ),
        mathematical_object=MathematicalObject(
            state_space=_string(mathematical, "state_space", "candidate.mathematical_object"),
            transition_law=_string(
                mathematical, "transition_law", "candidate.mathematical_object"
            ),
            invariant_or_path_measure=_string(
                mathematical,
                "invariant_or_path_measure",
                "candidate.mathematical_object",
            ),
            target_derivative=_string(
                mathematical, "target_derivative", "candidate.mathematical_object"
            ),
            estimator_or_identity=_string(
                mathematical, "estimator_or_identity", "candidate.mathematical_object"
            ),
            assumptions=_string_tuple(
                mathematical, "assumptions", "candidate.mathematical_object"
            ),
            formal_difference_statement=_string(
                mathematical,
                "formal_difference_statement",
                "candidate.mathematical_object",
            ),
        ),
        primitive=PrimitiveClaim(
            category=_enum_value(
                PrimitiveCategory, primitive, "category", "candidate.primitive"
            ),
            novelty_basis=_enum_value(
                NoveltyBasis, primitive, "novelty_basis", "candidate.primitive"
            ),
            statement=_string(primitive, "statement", "candidate.primitive"),
            theorem_obligation=_string(
                primitive, "theorem_obligation", "candidate.primitive"
            ),
            proof_sketch=_string(primitive, "proof_sketch", "candidate.primitive"),
            composition_only=_boolean(
                primitive, "composition_only", "candidate.primitive"
            ),
        ),
        prior_art=_prior_art_entries(root["prior_art"]),
        witness=NonEquivalenceWitness(
            symbolic_difference=_string(
                witness, "symbolic_difference", "candidate.witness"
            ),
            controlled_problem=_string(
                witness, "controlled_problem", "candidate.witness"
            ),
            candidate_prediction=_string(
                witness, "candidate_prediction", "candidate.witness"
            ),
            nearest_composition_prediction=_string(
                witness, "nearest_composition_prediction", "candidate.witness"
            ),
            rejection_rule=_string(witness, "rejection_rule", "candidate.witness"),
        ),
        counterexamples=_counterexample_entries(root["counterexamples"]),
        benchmark=BenchmarkBlueprint(
            independent_systems=_string_tuple(
                benchmark, "independent_systems", "candidate.benchmark"
            ),
            baselines=_baseline_entries(benchmark["baselines"]),
            metrics=_string_tuple(benchmark, "metrics", "candidate.benchmark"),
            compute_matched=_boolean(
                benchmark, "compute_matched", "candidate.benchmark"
            ),
        ),
        claim_boundary=ClaimBoundary(
            not_proved=_string_tuple(boundary, "not_proved", "candidate.claim_boundary"),
            diagnostic_only=_string_tuple(
                boundary, "diagnostic_only", "candidate.claim_boundary"
            ),
            stop_rule=_string(boundary, "stop_rule", "candidate.claim_boundary"),
        ),
        resources=ResourceRequest(
            data_scope=_string(resources, "data_scope", "candidate.resources"),
            uses_market_data=_boolean(
                resources, "uses_market_data", "candidate.resources"
            ),
            opens_sealed_data=_boolean(
                resources, "opens_sealed_data", "candidate.resources"
            ),
            gpu_hours=_float(resources, "gpu_hours", "candidate.resources"),
        ),
    )


def _prior_art_entries(value: object) -> tuple[PriorArtEntry, ...]:
    entries = _mapping_array(value, "candidate.prior_art")
    parsed: list[PriorArtEntry] = []
    for index, item in enumerate(entries):
        path = f"candidate.prior_art[{index}]"
        row = _strict_mapping(
            item,
            {
                "family",
                "source_id",
                "primary_url",
                "equation_or_theorem",
                "disposition",
                "candidate_difference",
            },
            path,
        )
        parsed.append(
            PriorArtEntry(
                family=_enum_value(MethodFamily, row, "family", path),
                source_id=_string(row, "source_id", path),
                primary_url=_string(row, "primary_url", path),
                equation_or_theorem=_string(row, "equation_or_theorem", path),
                disposition=_enum_value(
                    CoverageDisposition, row, "disposition", path
                ),
                candidate_difference=_string(row, "candidate_difference", path),
            )
        )
    return tuple(parsed)


def _counterexample_entries(value: object) -> tuple[Counterexample, ...]:
    entries = _mapping_array(value, "candidate.counterexamples")
    parsed: list[Counterexample] = []
    for index, item in enumerate(entries):
        path = f"candidate.counterexamples[{index}]"
        row = _strict_mapping(
            item,
            {"counterexample_id", "family", "construction", "expected_failure", "rejection_rule"},
            path,
        )
        parsed.append(
            Counterexample(
                counterexample_id=_string(row, "counterexample_id", path),
                family=_enum_value(CounterexampleFamily, row, "family", path),
                construction=_string(row, "construction", path),
                expected_failure=_string(row, "expected_failure", path),
                rejection_rule=_string(row, "rejection_rule", path),
            )
        )
    return tuple(parsed)


def _baseline_entries(value: object) -> tuple[BaselineEntry, ...]:
    entries = _mapping_array(value, "candidate.benchmark.baselines")
    parsed: list[BaselineEntry] = []
    for index, item in enumerate(entries):
        path = f"candidate.benchmark.baselines[{index}]"
        row = _strict_mapping(
            item,
            {"family", "disposition", "implementation", "justification", "compute_match_rule"},
            path,
        )
        parsed.append(
            BaselineEntry(
                family=_enum_value(MethodFamily, row, "family", path),
                disposition=_enum_value(
                    BaselineDisposition, row, "disposition", path
                ),
                implementation=_string(row, "implementation", path),
                justification=_string(row, "justification", path),
                compute_match_rule=_string(row, "compute_match_rule", path),
            )
        )
    return tuple(parsed)


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


def _mapping_array(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"{path} must be an array")
    return cast(list[object], value)


def _string(mapping: Mapping[str, object], key: str, path: str) -> str:
    value = mapping[key]
    if not isinstance(value, str):
        raise ValueError(f"{path}.{key} must be a string")
    return value


def _string_tuple(mapping: Mapping[str, object], key: str, path: str) -> tuple[str, ...]:
    value = mapping[key]
    if not isinstance(value, list):
        raise ValueError(f"{path}.{key} must be an array")
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise ValueError(f"{path}.{key}[{index}] must be a string")
        result.append(item)
    return tuple(result)


def _boolean(mapping: Mapping[str, object], key: str, path: str) -> bool:
    value = mapping[key]
    if not isinstance(value, bool):
        raise ValueError(f"{path}.{key} must be a boolean")
    return value


def _float(mapping: Mapping[str, object], key: str, path: str) -> float:
    value = mapping[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{path}.{key} must be numeric")
    return float(value)


def _enum_value(
    enum_type: type[EnumT], mapping: Mapping[str, object], key: str, path: str
) -> EnumT:
    value = _string(mapping, key, path)
    try:
        return enum_type(value)
    except ValueError as error:
        raise ValueError(f"{path}.{key} has unknown value {value!r}") from error


def _sorted_unique(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


def _has_text(value: str) -> bool:
    return bool(value.strip())


def _is_primary_url(value: str) -> bool:
    lowered = value.strip().casefold()
    return lowered.startswith(("https://", "http://", "doi:"))


__all__ = [
    "SCHEMA_VERSION",
    "AdmissionReport",
    "AdmissionStatus",
    "CandidateContract",
    "ReasonCode",
    "assess_candidate",
    "candidate_from_dict",
    "candidate_sha256",
    "candidate_to_dict",
    "candidate_to_json",
    "load_candidate",
]
