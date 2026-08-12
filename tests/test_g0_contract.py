from __future__ import annotations

from copy import deepcopy

import pytest

from ecomd.invariant_calibration.g0_contract import (
    AdmissionStatus,
    ReasonCode,
    assess_candidate,
    candidate_from_dict,
    candidate_sha256,
    candidate_to_dict,
)

METHOD_FAMILIES = (
    "persistent_markov_pcd_soul",
    "sequential_reweighting_smc_jarzynski",
    "steady_state_lr_pathwise",
    "stochastic_adjoint_stochasticad_gge",
    "coupled_debiasing_rhee_glynn",
    "long_full_truncated_bptt",
)


def complete_payload() -> dict[str, object]:
    prior_art = [
        {
            "family": family,
            "source_id": f"primary-{index}",
            "primary_url": f"https://example.org/primary-{index}",
            "equation_or_theorem": f"Theorem {index}",
            "disposition": "covered",
            "candidate_difference": f"Witnessed difference {index}",
        }
        for index, family in enumerate(METHOD_FAMILIES, start=1)
    ]
    baselines = [
        {
            "family": family,
            "disposition": "included",
            "implementation": f"reference-{index}",
            "justification": "nearest comparator",
            "compute_match_rule": "same simulator-step and wall-time budgets",
        }
        for index, family in enumerate(METHOD_FAMILIES, start=1)
    ]
    return {
        "schema_version": "ecomd-ncs-g0-candidate/v1",
        "candidate_id": "hypothetical-formal-object",
        "version": "v1",
        "frozen_before_implementation": True,
        "mathematical_object": {
            "state_space": "Polish state space X",
            "transition_law": "parameterized kernel P_theta",
            "invariant_or_path_measure": "unique invariant measure pi_theta",
            "target_derivative": "d_theta E_pi_theta[f]",
            "estimator_or_identity": "hypothetical identity H(theta)",
            "assumptions": ["geometric drift", "finite second moment"],
            "formal_difference_statement": "H contains a term absent from every mapped family",
        },
        "primitive": {
            "category": "cross_parameter_coupling",
            "novelty_basis": "formal_identity_or_theorem",
            "statement": "A hypothetical cross-parameter identity with an observable correction",
            "theorem_obligation": "prove unbiasedness and finite variance under assumptions A1-A2",
            "proof_sketch": "martingale decomposition followed by a dominated convergence argument",
            "composition_only": False,
        },
        "prior_art": prior_art,
        "witness": {
            "symbolic_difference": "H(theta) - H_composed(theta) = R(theta)",
            "controlled_problem": "two-state parameter-switching chain with analytic invariant law",
            "candidate_prediction": "non-zero signed R(theta)",
            "nearest_composition_prediction": "R(theta) equals zero",
            "rejection_rule": "reject if the signed difference misses the analytic value",
        },
        "counterexamples": [
            {
                "counterexample_id": "slow-chain",
                "family": "slow_mixing",
                "construction": "spectral gap tends to zero",
                "expected_failure": "variance diverges outside the stated assumption",
                "rejection_rule": "reject if the diagnostic reports resolved",
            },
            {
                "counterexample_id": "jump-chain",
                "family": "discontinuous_event",
                "construction": "parameter-dependent jump with an analytic derivative",
                "expected_failure": "wrong event term changes the derivative sign",
                "rejection_rule": "reject on sign mismatch",
            },
        ],
        "benchmark": {
            "independent_systems": ["multivariate OU", "reaction network CTMC"],
            "baselines": baselines,
            "metrics": [
                "accuracy",
                "bias",
                "variance",
                "simulator_steps",
                "wall_time",
                "peak_memory",
                "failure_rate",
            ],
            "compute_matched": True,
        },
        "claim_boundary": {
            "not_proved": ["market fidelity", "universal mixing certificate"],
            "diagnostic_only": ["empirical ESS", "fixture admission result"],
            "stop_rule": "stop if the identity reduces to a mapped prior-art composition",
        },
        "resources": {
            "data_scope": "generated_metadata_only",
            "uses_market_data": False,
            "opens_sealed_data": False,
            "gpu_hours": 0.0,
        },
    }


def test_complete_hypothetical_can_only_reach_human_audit() -> None:
    report = assess_candidate(candidate_from_dict(complete_payload()))

    assert report.status is AdmissionStatus.READY_FOR_HUMAN_AUDIT
    assert report.reason_codes == (ReasonCode.HUMAN_AUDIT_REQUIRED.value,)
    assert report.human_review_required
    assert not report.automated_novelty_pass
    assert "PASS" not in {status.value for status in AdmissionStatus}


def test_rejected_v0_composition_cannot_be_laundered() -> None:
    payload = complete_payload()
    primitive = payload["primitive"]
    assert isinstance(primitive, dict)
    primitive["novelty_basis"] = "composition"
    primitive["composition_only"] = True

    report = assess_candidate(candidate_from_dict(payload))

    assert report.status is AdmissionStatus.REJECTED_EQUIVALENT
    assert report.reason_codes == (
        ReasonCode.DECLARED_COMPOSITION_ONLY.value,
        ReasonCode.NOVELTY_BASIS_NOT_FORMAL.value,
    )
    assert not report.automated_novelty_pass


@pytest.mark.parametrize("basis", ["performance", "application"])
def test_performance_or_application_is_not_method_novelty(basis: str) -> None:
    payload = complete_payload()
    primitive = payload["primitive"]
    assert isinstance(primitive, dict)
    primitive["novelty_basis"] = basis

    report = assess_candidate(candidate_from_dict(payload))

    assert report.status is AdmissionStatus.REJECTED_EQUIVALENT
    assert report.reason_codes == (ReasonCode.NOVELTY_BASIS_NOT_FORMAL.value,)


def test_missing_formal_obligations_is_incomplete() -> None:
    payload = complete_payload()
    primitive = payload["primitive"]
    assert isinstance(primitive, dict)
    primitive["theorem_obligation"] = ""
    primitive["proof_sketch"] = ""

    report = assess_candidate(candidate_from_dict(payload))

    assert report.status is AdmissionStatus.INCOMPLETE
    assert report.reason_codes == (
        ReasonCode.PROOF_SKETCH_MISSING.value,
        ReasonCode.THEOREM_OBLIGATION_MISSING.value,
    )


def test_missing_witness_and_slow_case_is_not_falsifiable() -> None:
    payload = complete_payload()
    witness = payload["witness"]
    assert isinstance(witness, dict)
    witness["symbolic_difference"] = ""
    payload["counterexamples"] = [
        {
            "counterexample_id": "jump-chain",
            "family": "discontinuous_event",
            "construction": "jump fixture",
            "expected_failure": "wrong sign",
            "rejection_rule": "reject on sign mismatch",
        }
    ]

    report = assess_candidate(candidate_from_dict(payload))

    assert report.status is AdmissionStatus.NOT_FALSIFIABLE
    assert set(report.reason_codes) == {
        ReasonCode.NON_EQUIVALENCE_WITNESS_INCOMPLETE.value,
        ReasonCode.COUNTEREXAMPLES_INSUFFICIENT.value,
        ReasonCode.SLOW_MIXING_OR_METASTABLE_CASE_MISSING.value,
    }


def test_ecomd_only_benchmark_is_rejected() -> None:
    payload = complete_payload()
    benchmark = payload["benchmark"]
    assert isinstance(benchmark, dict)
    benchmark["independent_systems"] = ["EcoMD", "EcoMD large"]

    report = assess_candidate(candidate_from_dict(payload))

    assert report.status is AdmissionStatus.ECO_MD_ONLY
    assert set(report.reason_codes) == {
        ReasonCode.ECO_MD_ONLY_BENCHMARK.value,
        ReasonCode.INDEPENDENT_SYSTEMS_INSUFFICIENT.value,
    }


def test_missing_baseline_and_metric_is_rejected() -> None:
    payload = complete_payload()
    benchmark = payload["benchmark"]
    assert isinstance(benchmark, dict)
    baselines = benchmark["baselines"]
    metrics = benchmark["metrics"]
    assert isinstance(baselines, list)
    assert isinstance(metrics, list)
    benchmark["baselines"] = baselines[:-1]
    benchmark["metrics"] = [item for item in metrics if item != "variance"]
    benchmark["compute_matched"] = False

    report = assess_candidate(candidate_from_dict(payload))

    assert report.status is AdmissionStatus.BASELINES_MISSING
    assert set(report.reason_codes) == {
        ReasonCode.BASELINE_FAMILY_MISSING.value,
        ReasonCode.COMPUTE_MATCHING_MISSING.value,
        ReasonCode.REQUIRED_METRIC_MISSING.value,
    }


def test_market_data_or_gpu_request_is_incomplete() -> None:
    payload = complete_payload()
    resources = payload["resources"]
    assert isinstance(resources, dict)
    resources["uses_market_data"] = True
    resources["opens_sealed_data"] = True
    resources["gpu_hours"] = 0.5
    resources["data_scope"] = "real_l2"

    report = assess_candidate(candidate_from_dict(payload))

    assert report.status is AdmissionStatus.INCOMPLETE
    assert set(report.reason_codes) == {
        ReasonCode.MARKET_DATA_BEFORE_G0.value,
        ReasonCode.SEALED_DATA_BEFORE_G0.value,
        ReasonCode.GPU_BEFORE_G0.value,
        ReasonCode.DATA_SCOPE_BEFORE_G0_INVALID.value,
    }


def test_duplicate_counterexample_id_does_not_count_twice() -> None:
    payload = complete_payload()
    counterexamples = payload["counterexamples"]
    assert isinstance(counterexamples, list)
    first = counterexamples[0]
    second = counterexamples[1]
    assert isinstance(first, dict)
    assert isinstance(second, dict)
    second["counterexample_id"] = first["counterexample_id"]

    report = assess_candidate(candidate_from_dict(payload))

    assert report.status is AdmissionStatus.NOT_FALSIFIABLE
    assert report.reason_codes == (ReasonCode.COUNTEREXAMPLES_INSUFFICIENT.value,)


def test_semantic_hash_is_invariant_to_mapping_and_set_order() -> None:
    payload = complete_payload()
    reordered = dict(reversed(list(deepcopy(payload).items())))
    mathematical = reordered["mathematical_object"]
    prior_art = reordered["prior_art"]
    counterexamples = reordered["counterexamples"]
    benchmark = reordered["benchmark"]
    assert isinstance(mathematical, dict)
    assert isinstance(prior_art, list)
    assert isinstance(counterexamples, list)
    assert isinstance(benchmark, dict)
    mathematical["assumptions"] = list(reversed(mathematical["assumptions"]))
    reordered["prior_art"] = list(reversed(prior_art))
    reordered["counterexamples"] = list(reversed(counterexamples))
    benchmark["independent_systems"] = list(reversed(benchmark["independent_systems"]))
    benchmark["baselines"] = list(reversed(benchmark["baselines"]))
    benchmark["metrics"] = list(reversed(benchmark["metrics"]))

    first = candidate_from_dict(payload)
    second = candidate_from_dict(reordered)

    assert candidate_to_dict(first) == candidate_to_dict(second)
    assert candidate_sha256(first) == candidate_sha256(second)


def test_parser_rejects_unknown_or_missing_keys() -> None:
    unknown = complete_payload()
    unknown["paper_claim"] = True
    with pytest.raises(ValueError, match=r"unknown=.*paper_claim"):
        candidate_from_dict(unknown)

    missing = complete_payload()
    del missing["witness"]
    with pytest.raises(ValueError, match=r"missing=.*witness"):
        candidate_from_dict(missing)
