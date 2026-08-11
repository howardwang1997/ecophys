"""Held-out shard generation and blinded merge for Experiment 141."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Literal, cast

import numpy as np
from numpy.typing import NDArray

from .feasibility import (
    PRIMARY_COMPONENTS,
    ResponseParameters,
    TruthFamily,
    anchor_signature,
    candidate_response,
    simulate_path,
    truth_response,
)
from .fitting import detector_z_score
from .protocol import Protocol

CandidateName = Literal["frozen", "instant", "multiclock"]
CANDIDATES: tuple[CandidateName, ...] = ("frozen", "instant", "multiclock")


def _as_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"expected a number, received {type(value).__name__}")
    return float(value)


def _as_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"expected an integer, received {type(value).__name__}")
    return value


def _fit_for_family(fit_bundle: dict[str, object], family: TruthFamily) -> dict[str, float]:
    fit_data = cast(dict[str, object], fit_bundle["development_fit"])
    families = cast(dict[str, object], fit_data["families"])
    key = "single_rate" if family == "confounded" else family
    values = cast(dict[str, object], families[key])
    return {
        "target_slope": _as_float(values["target_slope"]),
        "rate": _as_float(values["rate"]),
    }


def _detector_parameters(fit_bundle: dict[str, object]) -> tuple[float, float]:
    fit_data = cast(dict[str, object], fit_bundle["development_fit"])
    detector = cast(dict[str, object], fit_data["detector"])
    return _as_float(detector["target_slope"]), _as_float(detector["rate"])


def run_evaluation_shard(
    protocol: Protocol,
    fit_bundle: dict[str, object],
    shard: int,
) -> dict[str, object]:
    if shard < 0 or shard >= protocol.evaluation.n_shards:
        raise ValueError("invalid shard index")
    rows: list[dict[str, object]] = []
    seeds = [
        protocol.evaluation.seed_start + index
        for index in range(protocol.evaluation.n_seeds)
        if index % protocol.evaluation.n_shards == shard
    ]
    counterfactuals = {
        seed: simulate_path(
            protocol.world,
            seed,
            0.0,
            ResponseParameters(kind="frozen"),
            intervention=False,
        )
        for seed in seeds
    }
    detector_slope, detector_rate = _detector_parameters(fit_bundle)

    for family in protocol.evaluation.truth_families:
        fit = _fit_for_family(fit_bundle, family)
        for magnitude in protocol.evaluation.intervention_magnitudes:
            for seed in seeds:
                counterfactual = counterfactuals[seed]
                truth = simulate_path(
                    protocol.world,
                    seed,
                    magnitude,
                    truth_response(protocol.world, family),
                    intervention=True,
                    confounded=family == "confounded",
                )
                predictions: dict[str, object] = {}
                path_violations: dict[str, list[str]] = {
                    "counterfactual": list(counterfactual.mechanics_violations),
                    "truth": list(truth.mechanics_violations),
                }
                path_digests: dict[str, str] = {
                    "counterfactual": counterfactual.event_digest,
                    "truth": truth.event_digest,
                }
                for candidate in CANDIDATES:
                    prediction = simulate_path(
                        protocol.world,
                        seed,
                        magnitude,
                        candidate_response(
                            candidate,
                            fit["target_slope"],
                            fit["rate"],
                        ),
                        intervention=True,
                    )
                    predictions[candidate] = list(prediction.primary_effect(counterfactual))
                    path_violations[candidate] = list(prediction.mechanics_violations)
                    path_digests[candidate] = prediction.event_digest
                rows.append(
                    {
                        "family": family,
                        "magnitude": magnitude,
                        "seed": seed,
                        "truth_effect": list(truth.primary_effect(counterfactual)),
                        "predictions": predictions,
                        "detector_z": detector_z_score(
                            protocol,
                            truth,
                            detector_slope,
                            detector_rate,
                        ),
                        "mechanics_violations": path_violations,
                        "event_digests": path_digests,
                    }
                )

    anchor = simulate_path(
        protocol.world,
        protocol.evaluation.shared_anchor_seed,
        1.0,
        truth_response(protocol.world, "single_rate"),
        intervention=True,
    )
    return {
        "schema": "exp141-shard-v1",
        "experiment": protocol.experiment,
        "protocol_version": protocol.protocol_version,
        "config_sha256": protocol.config_sha256,
        "shard": shard,
        "n_shards": protocol.evaluation.n_shards,
        "seed_indices_modulo": shard,
        "seeds": seeds,
        "primary_components": list(PRIMARY_COMPONENTS),
        "anchor_sha256": anchor_signature(anchor),
        "anchor_mechanics_violations": list(anchor.mechanics_violations),
        "rows": rows,
    }


def _standardized_rmse(
    rows: list[dict[str, object]],
    candidate: CandidateName,
    scale: NDArray[np.float64],
) -> float:
    errors: list[NDArray[np.float64]] = []
    for row in rows:
        truth = np.asarray(cast(list[float], row["truth_effect"]), dtype=np.float64)
        predictions = cast(dict[str, object], row["predictions"])
        predicted = np.asarray(cast(list[float], predictions[candidate]), dtype=np.float64)
        errors.append((predicted - truth) / scale)
    if not errors:
        raise ValueError("cannot calculate RMSE without rows")
    stacked = np.stack(errors)
    return float(np.sqrt(np.mean(stacked**2)))


def _improvement(multiclock_rmse: float, baseline_rmse: float) -> float:
    if baseline_rmse <= 1e-15:
        return 0.0 if multiclock_rmse <= 1e-15 else -math.inf
    return 1.0 - multiclock_rmse / baseline_rmse


def _bootstrap_improvement(
    rows: list[dict[str, object]],
    scale: NDArray[np.float64],
    baseline: Literal["frozen", "instant"],
    replicates: int,
    seed: int,
) -> tuple[float, float, float]:
    seed_values = sorted({_as_int(row["seed"]) for row in rows})
    by_seed = {
        seed_value: [row for row in rows if _as_int(row["seed"]) == seed_value]
        for seed_value in seed_values
    }
    rng = np.random.default_rng(seed)
    values = np.empty(replicates, dtype=np.float64)
    for index in range(replicates):
        sampled = rng.choice(seed_values, size=len(seed_values), replace=True)
        sample_rows = [row for seed_value in sampled for row in by_seed[int(seed_value)]]
        values[index] = _improvement(
            _standardized_rmse(sample_rows, "multiclock", scale),
            _standardized_rmse(sample_rows, baseline, scale),
        )
    lower, median, upper = np.quantile(values, [0.025, 0.5, 0.975])
    return float(lower), float(median), float(upper)


def merge_scientific_shards(
    protocol: Protocol,
    fit_bundle: dict[str, object],
    shards: list[dict[str, object]],
) -> dict[str, object]:
    expected_indices = set(range(protocol.evaluation.n_shards))
    actual_indices = {_as_int(shard["shard"]) for shard in shards}
    if actual_indices != expected_indices:
        raise ValueError(f"expected shards {expected_indices}, received {actual_indices}")
    anchors = {str(shard["anchor_sha256"]) for shard in shards}
    if len(anchors) != 1:
        raise ValueError("shared anchor hashes disagree")
    for shard in shards:
        if shard["config_sha256"] != protocol.config_sha256:
            raise ValueError("shard config hash mismatch")
        if shard["protocol_version"] != protocol.protocol_version:
            raise ValueError("shard protocol mismatch")

    rows = [
        cast(dict[str, object], row)
        for shard in shards
        for row in cast(list[object], shard["rows"])
    ]
    expected_rows = (
        len(protocol.evaluation.truth_families)
        * len(protocol.evaluation.intervention_magnitudes)
        * protocol.evaluation.n_seeds
    )
    if len(rows) != expected_rows:
        raise ValueError(f"expected {expected_rows} rows, received {len(rows)}")
    identities = {
        (str(row["family"]), _as_float(row["magnitude"]), _as_int(row["seed"])) for row in rows
    }
    if len(identities) != expected_rows:
        raise ValueError("duplicate or missing evaluation identities")

    fit_data = cast(dict[str, object], fit_bundle["development_fit"])
    standardizer = cast(dict[str, object], fit_data["standardizer"])
    if tuple(cast(list[str], standardizer["components"])) != PRIMARY_COMPONENTS:
        raise ValueError("standardizer component mismatch")
    scale = np.asarray(cast(list[float], standardizer["scale"]), dtype=np.float64)
    family_metrics: dict[str, object] = {}
    for family in ("none", "single_rate", "two_rate"):
        selected = [row for row in rows if row["family"] == family]
        rmses = {
            candidate: _standardized_rmse(selected, candidate, scale) for candidate in CANDIDATES
        }
        frozen_improvement = _improvement(rmses["multiclock"], rmses["frozen"])
        instant_improvement = _improvement(rmses["multiclock"], rmses["instant"])
        family_metrics[family] = {
            "n_rows": len(selected),
            "rmse": rmses,
            "improvement_vs_frozen": frozen_improvement,
            "improvement_vs_instant": instant_improvement,
            "bootstrap_vs_frozen_95": list(
                _bootstrap_improvement(
                    selected,
                    scale,
                    "frozen",
                    protocol.gates.bootstrap_replicates,
                    protocol.gates.bootstrap_seed,
                )
            ),
        }

    mechanics_violations = sum(
        len(cast(list[str], violations))
        for row in rows
        for violations in cast(dict[str, object], row["mechanics_violations"]).values()
    ) + sum(len(cast(list[str], shard["anchor_mechanics_violations"])) for shard in shards)
    single_rows = [row for row in rows if row["family"] == "single_rate"]
    confounded_rows = [row for row in rows if row["family"] == "confounded"]
    threshold = protocol.gates.confound_residual_z_threshold
    false_positive_rate = float(
        np.mean([abs(_as_float(row["detector_z"])) > threshold for row in single_rows])
    )
    detection_rate = float(
        np.mean([abs(_as_float(row["detector_z"])) > threshold for row in confounded_rows])
    )

    single = cast(dict[str, object], family_metrics["single_rate"])
    two_rate = cast(dict[str, object], family_metrics["two_rate"])
    no_adaptation = cast(dict[str, object], family_metrics["none"])
    no_improvement = _as_float(no_adaptation["improvement_vs_frozen"])
    no_degradation = -no_improvement
    single_bootstrap = cast(list[float], single["bootstrap_vs_frozen_95"])
    two_bootstrap = cast(list[float], two_rate["bootstrap_vs_frozen_95"])
    gates = {
        "mechanics": mechanics_violations <= protocol.gates.maximum_mechanics_violations,
        "single_rate_vs_frozen": (
            _as_float(single["improvement_vs_frozen"])
            >= protocol.gates.single_rate_minimum_rmse_reduction
            and single_bootstrap[0] >= protocol.gates.single_rate_minimum_bootstrap_lower
        ),
        "single_rate_vs_instant": (
            _as_float(single["improvement_vs_instant"]) >= 0.10
        ),
        "two_rate_vs_frozen": (
            _as_float(two_rate["improvement_vs_frozen"])
            >= protocol.gates.two_rate_minimum_rmse_reduction
            and two_bootstrap[0] >= protocol.gates.two_rate_minimum_bootstrap_lower
        ),
        "no_adaptation": (
            no_degradation <= protocol.gates.no_adaptation_maximum_rmse_degradation
        ),
        "confound_detector": (
            detection_rate >= protocol.gates.confound_minimum_detection_rate
            and false_positive_rate <= protocol.gates.confound_maximum_false_positive_rate
        ),
        "anchor": len(anchors) == 1,
    }
    canonical_rows = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return {
        "schema": "exp141-scientific-merge-v1",
        "protocol_version": protocol.protocol_version,
        "config_sha256": protocol.config_sha256,
        "raw_rows_sha256": hashlib.sha256(canonical_rows).hexdigest(),
        "n_rows": len(rows),
        "anchor_sha256": next(iter(anchors)),
        "mechanics_violation_count": mechanics_violations,
        "family_metrics": family_metrics,
        "detector": {
            "threshold": threshold,
            "detection_rate": detection_rate,
            "false_positive_rate": false_positive_rate,
        },
        "gates": gates,
        "scientific_pass": all(gates.values()),
    }


def read_json(path: str | Path) -> dict[str, object]:
    value = json.loads(Path(path).read_text())
    if not isinstance(value, dict):
        raise TypeError(f"{path} does not contain a JSON object")
    return cast(dict[str, object], value)
