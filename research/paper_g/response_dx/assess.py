"""Frozen exploratory screening rules; never a publication or activation decision."""

from __future__ import annotations

from typing import Any


def assess_regime(records: dict[tuple[int, bool, int], dict[str, Any]], partial: bool) -> dict[str, Any]:
    expected = {(frames, augmented, seed) for frames in (1, 4) for augmented in (False, True) for seed in (201, 202)}
    if set(records) != expected:
        raise ValueError("the complete eight-fit regime is required")
    reference = records[(1, False, 201)]["contrasts"]
    keys = {(1, .02), (1, .04), (4, .02), (4, .04)}
    truth = {(c["mode"], c["amplitude"]): c["reference_response"] for c in reference}
    if set(truth) != keys or len(reference) != 4:
        raise ValueError("all four reference contrasts are required")
    for record in records.values():
        contrasts = record["contrasts"]
        if len(contrasts) != 4 or {(c["mode"], c["amplitude"]) for c in contrasts} != keys:
            raise ValueError("contrast identity or multiplicity changed")
        if any(abs(c["reference_response"] - truth[(c["mode"], c["amplitude"])]) > 1e-12 for c in contrasts):
            raise ValueError("paired reference responses differ between fitted arms")
    if any(abs(truth[(k, .04)] - truth[(k, .02)]) > .05 * max(abs(truth[(k, .02)]), .1) for k in (1, 4)):
        return {"decision": "inconclusive", "reason": "finite_amplitude_only_linear_lead_stops"}
    if all(r["forecast_nrmse"] >= .1 for r in records.values()):
        return {"decision": "inconclusive", "reason": "no_forecast_competent_predictor"}
    null_by_seed = []
    residual_by_seed = []
    for seed in (201, 202):
        history = records[(4, True, seed)]
        unaugmented = records[(4, False, seed)]
        current = records[(1, True, seed)]
        h_errors = {(c["mode"], c["amplitude"]): c["normalized_mean_error"] for c in history["contrasts"]}
        c_errors = {(c["mode"], c["amplitude"]): c["normalized_mean_error"] for c in current["contrasts"]}
        competent = history["forecast_nrmse"] < .1
        null_by_seed.append(competent and all(e < .1 for e in h_errors.values())
                            and history["forecast_nrmse"] <= 1.2 * unaugmented["forecast_nrmse"])
        useful = history["forecast_nrmse"] <= .8 * current["forecast_nrmse"]
        residual_by_seed.append({key for key in keys if partial and competent and useful
                                 and h_errors[key] > .25 and c_errors[key] < .1})
    if all(null_by_seed):
        return {"decision": "stop_this_mean_response_method_lead", "reason": "ordinary_augmented_history_suffices_in_both_initializations"}
    matched = sorted(residual_by_seed[0] & residual_by_seed[1])
    if matched:
        return {"decision": "contribution_audit_only", "matched_contrasts": matched,
                "claim_support": False, "candidate_harvest_authorized": False}
    return {"decision": "inconclusive", "reason": "no_same_contrast_useful_history_residual_in_both_initializations"}
