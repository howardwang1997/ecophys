"""Validate and analyze the frozen SWE training-by-inference enforcement cube."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from analyze_constraint_iclr_pdebench import (
    load_config,
    paired_sign_flip_pvalue,
    read_records,
)
from analyze_constraint_iclr_pdebench_swe import validate_swe_records
from constraint_iclr_common import bootstrap_mean_ci, holm_adjust, sha256_file, stable_seed

DERIVED_SPEC: dict[str, dict[str, Any]] = {
    "projection_res": {
        "parent": "free_res",
        "forward_map": "free_res",
        "inference_projected": True,
        "cell": "R01",
    },
    "hard_abs_unprojected": {
        "parent": "hard_abs",
        "forward_map": "free",
        "inference_projected": False,
        "cell": "A10",
    },
    "hard_res_unprojected": {
        "parent": "hard",
        "forward_map": "free_res",
        "inference_projected": False,
        "cell": "R10",
    },
}

CORE_CELL_MECHANISMS = {
    "A00": "free",
    "R00": "free_res",
    "A01": "projection",
    "A11": "hard_abs",
    "R11": "hard",
}


def canonical_object_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _all_finite(value: Any) -> bool:
    if isinstance(value, dict):
        return all(_all_finite(item) for item in value.values())
    if isinstance(value, list):
        return all(_all_finite(item) for item in value)
    if isinstance(value, float):
        return math.isfinite(value)
    return True


def validate_swe_checkpoint_lock(
    lock: dict[str, Any],
    core: dict[tuple[int, str], dict[str, Any]],
    config: dict[str, Any],
    *,
    core_records_sha256: str,
    core_analysis_sha256: str,
) -> dict[tuple[int, str], dict[str, Any]]:
    cube = config["cube"]
    seeds = [int(value) for value in config["seeds"]]
    mechanisms = [str(value) for value in cube["trained_parent_mechanisms"]]
    expected = {(seed, mechanism) for seed in seeds for mechanism in mechanisms}
    failures: list[str] = []
    if lock.get("schema_version") != cube["checkpoint_lock_schema_version"]:
        failures.append("wrong SWE checkpoint-lock schema")
    if lock.get("benchmark_id") != config["benchmark_id"]:
        failures.append("wrong SWE checkpoint-lock benchmark")
    if lock.get("core_records", {}).get("sha256") != core_records_sha256:
        failures.append("SWE checkpoint lock is not bound to the complete core JSONL")
    if int(lock.get("core_records", {}).get("record_count", -1)) != int(cube["expected_core_records"]):
        failures.append("wrong SWE core record count in checkpoint lock")
    if lock.get("core_analysis", {}).get("sha256") != core_analysis_sha256:
        failures.append("SWE checkpoint lock is not bound to the core analysis")
    if lock.get("factorial_protocol_sha256") != config["protocol_sha256"]:
        failures.append("SWE checkpoint lock has the wrong factorial protocol")
    if lock.get("cube_protocol_sha256") != cube["protocol_sha256"]:
        failures.append("SWE checkpoint lock has the wrong cube protocol")
    if lock.get("cube_decision_sha256") != cube["decision_sha256"]:
        failures.append("SWE checkpoint lock has the wrong cube decision")

    entries = lock.get("checkpoints", [])
    if not isinstance(entries, list):
        failures.append("SWE checkpoint-lock entries are not a list")
        entries = []
    indexed: dict[tuple[int, str], dict[str, Any]] = {}
    for entry in entries:
        key = (int(entry.get("seed", -1)), str(entry.get("mechanism")))
        if key in indexed:
            failures.append(f"duplicate SWE checkpoint-lock entry {key}")
        indexed[key] = entry
        if key not in core:
            failures.append(f"SWE checkpoint lock has no core parent for {key}")
            continue
        parent = core[key]
        parent_checkpoint = parent.get("checkpoint", {})
        expected_fields = {
            "run_id": parent.get("run_id"),
            "path": parent_checkpoint.get("path"),
            "bytes": parent_checkpoint.get("bytes"),
            "sha256": parent_checkpoint.get("sha256"),
            "payload_schema_version": cube["checkpoint_schema_version"],
            "completed_epochs": cube["checkpoint_completed_epochs"],
        }
        for field, expected_value in expected_fields.items():
            if entry.get(field) != expected_value:
                failures.append(f"wrong SWE checkpoint {field} for {key}")
    if set(indexed) != expected:
        failures.append(
            "SWE checkpoint coverage mismatch: "
            f"missing={sorted(expected.difference(indexed))}, "
            f"extra={sorted(set(indexed).difference(expected))}"
        )
    if len(entries) != int(cube["expected_trained_checkpoints"]):
        failures.append("wrong number of SWE checkpoint-lock entries")
    if failures:
        raise RuntimeError("; ".join(failures))
    return indexed


def validate_swe_cube_records(
    derived_records: list[dict[str, Any]],
    core_records: list[dict[str, Any]],
    checkpoint_lock: dict[str, Any],
    config: dict[str, Any],
    *,
    core_records_sha256: str,
    core_analysis_sha256: str,
    checkpoint_lock_sha256: str,
) -> tuple[
    dict[tuple[int, str], dict[str, Any]],
    dict[tuple[int, str], dict[str, Any]],
]:
    core = validate_swe_records(core_records, config)
    checkpoints = validate_swe_checkpoint_lock(
        checkpoint_lock,
        core,
        config,
        core_records_sha256=core_records_sha256,
        core_analysis_sha256=core_analysis_sha256,
    )
    cube = config["cube"]
    seeds = [int(value) for value in config["seeds"]]
    mechanisms = [str(value) for value in cube["derived_mechanisms"]]
    expected = {(seed, mechanism) for seed in seeds for mechanism in mechanisms}
    expected_cases = {str(value) for value in config["evaluation"]["case_names"]}
    expected_horizons = {str(int(value)) for value in config["evaluation"]["horizons"]}
    primary_metric = str(cube["primary_metric"])
    required_metrics = {
        primary_metric,
        "total_rmse",
        "max_abs_invariant_drift",
        "negative_depth_fraction",
        "mean_negative_depth_deficit",
        "minimum_predicted_depth",
    }
    required_sources = (
        str(cube["protocol_path"]),
        str(cube["decision_path"]),
        str(cube["checkpoint_lock"]),
        str(config["dataset"]["lock_path"]),
    )
    failures: list[str] = []
    indexed: dict[tuple[int, str], dict[str, Any]] = {}
    run_ids: set[str] = set()
    source_manifests: set[str] = set()
    drift_atol = float(config["factorial_analysis"]["invariant_drift_atol"])
    for record in derived_records:
        key = (int(record.get("seed", -1)), str(record.get("mechanism")))
        run_id = str(record.get("run_id"))
        if key in indexed:
            failures.append(f"duplicate SWE cube seed/mechanism {key}")
        if run_id in run_ids:
            failures.append(f"duplicate SWE cube run ID {run_id}")
        indexed[key] = record
        run_ids.add(run_id)
        expected_record_fields = {
            "schema_version": cube["schema_version"],
            "stage": cube["stage"],
            "benchmark_id": config["benchmark_id"],
            "data_lock_sha256": config["dataset"]["lock_sha256"],
            "factorial_protocol_sha256": config["protocol_sha256"],
            "cube_protocol_sha256": cube["protocol_sha256"],
            "cube_decision_sha256": cube["decision_sha256"],
            "core_records_sha256": core_records_sha256,
            "core_analysis_sha256": core_analysis_sha256,
            "checkpoint_lock_sha256": checkpoint_lock_sha256,
        }
        for field, expected_value in expected_record_fields.items():
            if record.get(field) != expected_value:
                failures.append(f"wrong SWE cube {field} for {key}")
        if not _all_finite(record):
            failures.append(f"non-finite SWE cube record for {key}")
        if key[1] not in DERIVED_SPEC:
            continue
        spec = DERIVED_SPEC[key[1]]
        if record.get("forward_map") != spec["forward_map"]:
            failures.append(f"wrong SWE cube forward map for {key}")
        if bool(record.get("inference_projected")) is not bool(spec["inference_projected"]):
            failures.append(f"wrong SWE cube inference projector for {key}")
        parent_key = (key[0], str(spec["parent"]))
        if parent_key not in core or parent_key not in checkpoints:
            failures.append(f"missing SWE cube parent for {key}")
            continue
        parent = core[parent_key]
        checkpoint = checkpoints[parent_key]
        parent_binding = record.get("parent", {})
        expected_parent = {
            "run_id": parent["run_id"],
            "mechanism": spec["parent"],
            "checkpoint_path": checkpoint["path"],
            "checkpoint_sha256": checkpoint["sha256"],
            "checkpoint_bytes": checkpoint["bytes"],
            "training_index_sha256": parent["training_index_sha256"],
            "initialization_sha256": parent["initialization_sha256"],
            "provenance_sha256": canonical_object_sha256(parent["provenance"]),
        }
        for field, expected_value in expected_parent.items():
            if parent_binding.get(field) != expected_value:
                failures.append(f"wrong SWE cube parent {field} for {key}")
        if record.get("derived_from") != parent["run_id"]:
            failures.append(f"wrong SWE cube derived_from for {key}")
        if record.get("training_index_sha256") != parent["training_index_sha256"]:
            failures.append(f"wrong SWE cube training-index binding for {key}")
        if record.get("initialization_sha256") != parent["initialization_sha256"]:
            failures.append(f"wrong SWE cube initialization binding for {key}")
        compute = record.get("compute", {})
        for field in ("optimization_runs", "examples_seen", "proxy"):
            if int(compute.get(field, -1)) != 0:
                failures.append(f"SWE cube has nonzero {field} for {key}")
        if float(compute.get("training_runtime_seconds", math.nan)) != 0.0:
            failures.append(f"SWE cube has nonzero training runtime for {key}")
        cases = record.get("cases", {})
        if set(cases) != expected_cases:
            failures.append(f"wrong SWE cube cases for {key}")
        else:
            for case, horizons in cases.items():
                if set(horizons) != expected_horizons:
                    failures.append(f"wrong SWE cube horizons for {key}, {case}")
                    continue
                for horizon, metrics in horizons.items():
                    missing = required_metrics.difference(metrics)
                    if missing:
                        failures.append(
                            f"missing SWE cube metrics for {key}, {case}, {horizon}: {sorted(missing)}"
                        )
        provenance = record.get("provenance", {})
        if provenance.get("git_head") != config["expected_git_head"]:
            failures.append(f"wrong SWE cube Git head for {key}")
        if bool(provenance.get("git_dirty")) is not bool(config["expected_git_dirty"]):
            failures.append(f"wrong SWE cube dirty flag for {key}")
        sources = provenance.get("source_sha256", {})
        if not isinstance(sources, dict):
            failures.append(f"missing SWE cube source manifest for {key}")
        else:
            source_manifests.add(json.dumps(sources, sort_keys=True))
            for required in required_sources:
                if required not in sources:
                    failures.append(f"SWE cube source manifest omits {required} for {key}")
            if sources.get(str(cube["checkpoint_lock"])) != checkpoint_lock_sha256:
                failures.append(f"SWE cube source manifest has wrong lock for {key}")

    if set(indexed) != expected:
        failures.append(
            "SWE cube coverage mismatch: "
            f"missing={sorted(expected.difference(indexed))}, "
            f"extra={sorted(set(indexed).difference(expected))}"
        )
    if len(derived_records) != int(cube["expected_derived_records"]):
        failures.append("wrong SWE cube derived record count")
    if len(source_manifests) != 1:
        failures.append("SWE cube records do not share one source manifest")
    if not expected.difference(indexed):
        for seed in seeds:
            for mechanism, spec in DERIVED_SPEC.items():
                derived = indexed[(seed, mechanism)]
                parent = core[(seed, str(spec["parent"]))]
                for case in expected_cases:
                    derived_h1 = float(derived["cases"][case]["1"][primary_metric])
                    parent_h1 = float(parent["cases"][case]["1"][primary_metric])
                    if not math.isclose(derived_h1, parent_h1, rel_tol=1e-5, abs_tol=1e-8):
                        failures.append(
                            f"SWE cube horizon-one identity failure for {seed}, {mechanism}, {case}"
                        )
                    if bool(spec["inference_projected"]):
                        for horizon in expected_horizons:
                            drift = float(derived["cases"][case][horizon]["max_abs_invariant_drift"])
                            if drift > drift_atol:
                                failures.append(
                                    f"SWE cube invariant gate failure for "
                                    f"{seed}, {mechanism}, {case}, h={horizon}"
                                )
    if failures:
        raise RuntimeError("; ".join(failures))
    return core, indexed


def _metric(
    core: dict[tuple[int, str], dict[str, Any]],
    derived: dict[tuple[int, str], dict[str, Any]],
    seed: int,
    cell: str,
    case: str,
    horizon: int,
    metric: str,
) -> float:
    if cell in CORE_CELL_MECHANISMS:
        record = core[(seed, CORE_CELL_MECHANISMS[cell])]
    else:
        mechanism = next(name for name, spec in DERIVED_SPEC.items() if spec["cell"] == cell)
        record = derived[(seed, mechanism)]
    return float(record["cases"][case][str(horizon)][metric])


def swe_cube_seed_effects(
    core: dict[tuple[int, str], dict[str, Any]],
    derived: dict[tuple[int, str], dict[str, Any]],
    seeds: list[int],
    case: str,
    horizon: int,
    metric: str,
) -> dict[str, np.ndarray]:
    cells = {
        cell: np.asarray(
            [_metric(core, derived, seed, cell, case, horizon, metric) for seed in seeds],
            dtype=np.float64,
        )
        for cell in ("A00", "R00", "A01", "R01", "A10", "R10", "A11", "R11")
    }
    d00 = cells["A00"] - cells["R00"]
    d01 = cells["A01"] - cells["R01"]
    d10 = cells["A10"] - cells["R10"]
    d11 = cells["A11"] - cells["R11"]
    effects = {
        "D00": d00,
        "D01": d01,
        "D10": d10,
        "D11": d11,
        "I_bundle": d00 - d11,
        "T0": d00 - d10,
        "T1": d01 - d11,
        "E0": d00 - d01,
        "E1": d10 - d11,
        # Simple effects use the sign convention ``unconstrained minus
        # constrained``.  For losses and violation metrics, positive values
        # therefore favor the corresponding enforcement intervention.
        "train_A_e0": cells["A00"] - cells["A10"],
        "train_R_e0": cells["R00"] - cells["R10"],
        "train_A_e1": cells["A01"] - cells["A11"],
        "train_R_e1": cells["R01"] - cells["R11"],
        "infer_A_t0": cells["A00"] - cells["A01"],
        "infer_R_t0": cells["R00"] - cells["R01"],
        "infer_A_t1": cells["A10"] - cells["A11"],
        "infer_R_t1": cells["R10"] - cells["R11"],
    }
    effects["J"] = effects["T0"] - effects["T1"]
    effects["J_inference_path"] = effects["E0"] - effects["E1"]
    effects["phi_train"] = 0.5 * (effects["T0"] + effects["T1"])
    effects["phi_infer"] = 0.5 * (effects["E0"] + effects["E1"])
    effects["train_unprojected"] = 0.5 * (effects["train_A_e0"] + effects["train_R_e0"])
    effects["train_projected"] = 0.5 * (effects["train_A_e1"] + effects["train_R_e1"])
    effects["infer_free_train"] = 0.5 * (effects["infer_A_t0"] + effects["infer_R_t0"])
    effects["infer_hard_train"] = 0.5 * (effects["infer_A_t1"] + effects["infer_R_t1"])
    effects["main_train"] = 0.5 * (effects["train_unprojected"] + effects["train_projected"])
    effects["main_infer"] = 0.5 * (effects["infer_free_train"] + effects["infer_hard_train"])
    effects["main_coordinate"] = 0.25 * (d00 + d01 + d10 + d11)
    return {**cells, **effects}


def _summary(
    values: np.ndarray,
    *,
    name: str,
    case: str,
    horizon: int,
    confidence: float,
    draws: int,
    metric: str = "conserving_rmse",
) -> dict[str, Any]:
    interval = bootstrap_mean_ci(
        values,
        confidence=confidence,
        draws=draws,
        seed=stable_seed(20260902, f"swe-cube:{metric}:{name}:{case}:{horizon}:{confidence}"),
    )
    return {"mean": float(np.mean(values)), "ci": list(interval)}


def _roundoff_tolerance(absolute_floor: float, *operands: np.ndarray) -> float:
    """Bound rearrangement error without weakening the frozen absolute floor.

    The cube identities compare algebraically equivalent expressions evaluated
    in different orders.  Their roundoff scales with the operands that cancel,
    not with the (potentially near-zero) identity residual.  Sixty-four eps is
    a conservative, data-independent operation-count allowance for the nested
    additions, subtractions, and averages used below.
    """

    if absolute_floor < 0.0 or not math.isfinite(absolute_floor):
        raise ValueError("algebra absolute tolerance must be finite and nonnegative")
    if not operands:
        return absolute_floor
    stacked_scale = np.zeros_like(np.asarray(operands[0], dtype=np.float64))
    for operand in operands:
        stacked_scale = stacked_scale + np.abs(np.asarray(operand, dtype=np.float64))
    scale = max(1.0, float(np.max(stacked_scale)))
    return absolute_floor + 64.0 * float(np.finfo(np.float64).eps) * scale


def analyze_swe_cube_cell(
    core: dict[tuple[int, str], dict[str, Any]],
    derived: dict[tuple[int, str], dict[str, Any]],
    seeds: list[int],
    config: dict[str, Any],
    case: str,
    horizon: int,
) -> dict[str, Any]:
    settings = config["factorial_analysis"]
    metric = str(config["cube"]["primary_metric"])
    effects = swe_cube_seed_effects(core, derived, seeds, case, horizon, metric)
    atol = float(config["cube"]["algebra_atol"])
    path_error = float(np.max(np.abs(effects["J"] - effects["J_inference_path"])))
    efficiency_error = float(
        np.max(np.abs(effects["phi_train"] + effects["phi_infer"] - effects["I_bundle"]))
    )
    path_tolerance = _roundoff_tolerance(
        atol,
        effects["D00"],
        effects["D01"],
        effects["D10"],
        effects["D11"],
    )
    efficiency_tolerance = _roundoff_tolerance(
        atol,
        effects["T0"],
        effects["T1"],
        effects["E0"],
        effects["E1"],
        effects["I_bundle"],
    )
    if path_error > path_tolerance:
        raise RuntimeError(f"SWE cube path identity failed for {case}, h={horizon}")
    if efficiency_error > efficiency_tolerance:
        raise RuntimeError(f"SWE cube efficiency failed for {case}, h={horizon}")
    draws = int(settings["bootstrap_draws"])
    confidence95 = float(settings["confidence_nonzero"])
    confidence90 = float(settings["confidence_equivalence"])
    names = (
        "D00",
        "D01",
        "D10",
        "D11",
        "I_bundle",
        "T0",
        "T1",
        "E0",
        "E1",
        "J",
        "phi_train",
        "phi_infer",
        "train_A_e0",
        "train_R_e0",
        "train_A_e1",
        "train_R_e1",
        "infer_A_t0",
        "infer_R_t0",
        "infer_A_t1",
        "infer_R_t1",
        "train_unprojected",
        "train_projected",
        "infer_free_train",
        "infer_hard_train",
        "main_train",
        "main_infer",
        "main_coordinate",
    )
    summaries = {
        name: _summary(
            effects[name],
            name=name,
            case=case,
            horizon=horizon,
            confidence=confidence95,
            draws=draws,
            metric=metric,
        )
        for name in names
    }
    j90 = _summary(
        effects["J"],
        name="J90",
        case=case,
        horizon=horizon,
        confidence=confidence90,
        draws=draws,
        metric=metric,
    )
    sesoi = float(settings["sesoi_fraction_of_free_res"]) * float(np.mean(effects["R00"]))
    low95, high95 = (float(value) for value in summaries["J"]["ci"])
    low90, high90 = (float(value) for value in j90["ci"])
    if low95 > sesoi or high95 < -sesoi:
        classification = "material_nonadditivity"
    elif low95 > 0.0 or high95 < 0.0:
        classification = "statistical_nonadditivity_below_or_crossing_sesoi"
    elif low90 > -sesoi and high90 < sesoi:
        classification = "practical_additivity"
    else:
        classification = "unresolved"
    return {
        "case": case,
        "horizon": horizon,
        "primary_metric": metric,
        "cell_mean_primary_metric": {
            name: float(np.mean(effects[name]))
            for name in ("A00", "R00", "A01", "R01", "A10", "R10", "A11", "R11")
        },
        "effects": summaries,
        "three_way_interaction": {
            "mean": summaries["J"]["mean"],
            "ci95": summaries["J"]["ci"],
            "ci90": j90["ci"],
            "sesoi": sesoi,
            "classification": classification,
            "sign_flip_p": paired_sign_flip_pvalue(
                effects["J"],
                seed=stable_seed(20260902, f"swe-cube-sign:{case}:{horizon}"),
                draws=int(settings["sign_flip_draws"]),
            ),
        },
        "max_abs_three_way_path_identity_error": path_error,
        "three_way_path_identity_tolerance": path_tolerance,
        "max_abs_shapley_efficiency_error": efficiency_error,
        "shapley_efficiency_tolerance": efficiency_tolerance,
    }


def _secondary_primary_summaries(
    core: dict[tuple[int, str], dict[str, Any]],
    derived: dict[tuple[int, str], dict[str, Any]],
    seeds: list[int],
    config: dict[str, Any],
) -> dict[str, Any]:
    case = str(config["evaluation"]["primary_case"])
    horizon = int(config["evaluation"]["primary_horizon"])
    draws = int(config["factorial_analysis"]["bootstrap_draws"])
    confidence = float(config["factorial_analysis"]["confidence_nonzero"])
    result: dict[str, Any] = {}
    for metric in (
        "total_rmse",
        "max_abs_invariant_drift",
        "negative_depth_fraction",
        "mean_negative_depth_deficit",
    ):
        effects = swe_cube_seed_effects(core, derived, seeds, case, horizon, metric)
        result[metric] = {
            "cell_means": {
                name: float(np.mean(effects[name]))
                for name in (
                    "A00",
                    "R00",
                    "A01",
                    "R01",
                    "A10",
                    "R10",
                    "A11",
                    "R11",
                )
            },
            "effects": {
                name: _summary(
                    effects[name],
                    name=name,
                    case=case,
                    horizon=horizon,
                    confidence=confidence,
                    draws=draws,
                    metric=metric,
                )
                for name in (
                    "I_bundle",
                    "T0",
                    "T1",
                    "E0",
                    "E1",
                    "J",
                    "phi_train",
                    "phi_infer",
                    "train_A_e0",
                    "train_R_e0",
                    "train_A_e1",
                    "train_R_e1",
                    "infer_A_t0",
                    "infer_R_t0",
                    "infer_A_t1",
                    "infer_R_t1",
                    "train_unprojected",
                    "train_projected",
                    "infer_free_train",
                    "infer_hard_train",
                    "main_train",
                    "main_infer",
                    "main_coordinate",
                )
            },
        }
    return result


def analyze_conservation_positivity_tradeoff(
    core: dict[tuple[int, str], dict[str, Any]],
    derived: dict[tuple[int, str], dict[str, Any]],
    seeds: list[int],
    config: dict[str, Any],
) -> dict[str, Any]:
    """Adjudicate the prespecified free-checkpoint projection trade-off.

    The contrast averages the absolute and residual output coordinates while
    holding training enforcement off.  This keeps the projection intervention
    paired within a checkpoint and avoids treating an unprojected hard-trained
    network as the primary positivity control.
    """
    tradeoff = config["cube"]["tradeoff"]
    case = str(tradeoff["case"])
    horizon = int(tradeoff["horizon"])
    if case not in {str(value) for value in config["evaluation"]["case_names"]}:
        raise RuntimeError("SWE trade-off case is outside the frozen evaluation grid")
    if horizon not in {int(value) for value in config["evaluation"]["horizons"]}:
        raise RuntimeError("SWE trade-off horizon is outside the frozen evaluation grid")
    confidence = float(tradeoff["confidence"])
    draws = int(config["factorial_analysis"]["bootstrap_draws"])
    metric_names = {
        "conservation": str(tradeoff["conservation_metric"]),
        "positivity": str(tradeoff["positivity_metric"]),
        "positivity_secondary": str(tradeoff["secondary_positivity_metric"]),
        "dynamics": str(config["cube"]["primary_metric"]),
    }
    summaries: dict[str, Any] = {}
    for label, metric in metric_names.items():
        effects = swe_cube_seed_effects(core, derived, seeds, case, horizon, metric)
        summaries[label] = {
            "metric": metric,
            "infer_free_train": _summary(
                effects["infer_free_train"],
                name=f"tradeoff_{label}_infer_free_train",
                case=case,
                horizon=horizon,
                confidence=confidence,
                draws=draws,
                metric=metric,
            ),
            "absolute": _summary(
                effects["infer_A_t0"],
                name=f"tradeoff_{label}_absolute",
                case=case,
                horizon=horizon,
                confidence=confidence,
                draws=draws,
                metric=metric,
            ),
            "residual": _summary(
                effects["infer_R_t0"],
                name=f"tradeoff_{label}_residual",
                case=case,
                horizon=horizon,
                confidence=confidence,
                draws=draws,
                metric=metric,
            ),
            "coordinate_interaction": _summary(
                effects["E0"],
                name=f"tradeoff_{label}_coordinate_interaction",
                case=case,
                horizon=horizon,
                confidence=confidence,
                draws=draws,
                metric=metric,
            ),
        }

    conservation_ci = summaries["conservation"]["infer_free_train"]["ci"]
    positivity_ci = summaries["positivity"]["infer_free_train"]["ci"]
    conservation_gain = float(conservation_ci[0]) > 0.0
    positivity_harm = float(positivity_ci[1]) < 0.0
    positivity_gain = float(positivity_ci[0]) > 0.0
    if not conservation_gain:
        classification = "conservation_gain_not_resolved"
    elif positivity_harm:
        classification = "resolved_conservation_positivity_tradeoff"
    elif positivity_gain:
        classification = "resolved_conservation_positivity_synergy"
    else:
        classification = "conservation_gain_with_unresolved_positivity_effect"
    return {
        "case": case,
        "horizon": horizon,
        "sign_convention": (
            "unprojected minus projected; positive favors inference projection "
            "for every listed lower-is-better metric"
        ),
        "classification": classification,
        "metrics": summaries,
    }


def analyze_swe_enforcement_cube(
    derived_records: list[dict[str, Any]],
    core_records: list[dict[str, Any]],
    checkpoint_lock: dict[str, Any],
    config: dict[str, Any],
    *,
    core_records_sha256: str,
    core_analysis_sha256: str,
    checkpoint_lock_sha256: str,
) -> dict[str, Any]:
    core, derived = validate_swe_cube_records(
        derived_records,
        core_records,
        checkpoint_lock,
        config,
        core_records_sha256=core_records_sha256,
        core_analysis_sha256=core_analysis_sha256,
        checkpoint_lock_sha256=checkpoint_lock_sha256,
    )
    seeds = [int(value) for value in config["seeds"]]
    cells = [
        analyze_swe_cube_cell(core, derived, seeds, config, str(case), int(horizon))
        for case in config["evaluation"]["case_names"]
        for horizon in config["evaluation"]["horizons"]
    ]
    if config["cube"]["stage"] == "swe_enforcement_cube_confirmation" and len(cells) != 8:
        raise RuntimeError("formal SWE cube analysis requires exactly eight cells")
    adjusted = holm_adjust([float(cell["three_way_interaction"]["sign_flip_p"]) for cell in cells])
    for cell, adjusted_p in zip(cells, adjusted, strict=True):
        cell["three_way_interaction"]["sign_flip_p_holm"] = adjusted_p
    primary = next(
        cell
        for cell in cells
        if cell["case"] == config["evaluation"]["primary_case"]
        and cell["horizon"] == int(config["evaluation"]["primary_horizon"])
    )
    return {
        "schema_version": "constraint-iclr-pdebench-swe-enforcement-cube-analysis-v1",
        "benchmark_id": config["benchmark_id"],
        "core_record_count": len(core_records),
        "derived_record_count": len(derived_records),
        "checkpoint_count": len(checkpoint_lock["checkpoints"]),
        "seeds": seeds,
        "integrity_gates_passed": True,
        "primary": primary,
        "secondary_primary_case": _secondary_primary_summaries(core, derived, seeds, config),
        "conservation_positivity_tradeoff": analyze_conservation_positivity_tradeoff(
            core, derived, seeds, config
        ),
        "all_cases": cells,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/constraint_iclr/pdebench_swe_rdb_enforcement_cube_20260902.yaml"),
    )
    parser.add_argument("--derived-input", type=Path)
    parser.add_argument("--core-input", type=Path)
    parser.add_argument("--core-analysis", type=Path)
    parser.add_argument("--checkpoint-lock", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "experiments/constraint_attribution_iclr/pdebench/swe_enforcement_cube_analysis_20260902.json"
        ),
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    config_path = args.config if args.config.is_absolute() else root / args.config
    config = load_config(config_path)
    cube = config["cube"]

    def resolved_path(value: Path | str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else root / path

    derived_path = resolved_path(args.derived_input or cube["output"])
    core_path = resolved_path(args.core_input or config["output"])
    core_analysis_path = resolved_path(args.core_analysis or cube["core_analysis"])
    checkpoint_lock_path = resolved_path(args.checkpoint_lock or cube["checkpoint_lock"])
    output_path = resolved_path(args.output)
    core_analysis = json.loads(core_analysis_path.read_text(encoding="utf-8"))
    core_sha256 = sha256_file(core_path)
    if core_analysis.get("input_sha256") != core_sha256:
        raise RuntimeError("SWE core analysis is not bound to the complete JSONL")
    if not core_analysis.get("integrity_gates_passed", False):
        raise RuntimeError("SWE core analysis did not pass integrity gates")
    checkpoint_lock = json.loads(checkpoint_lock_path.read_text(encoding="utf-8"))
    result = analyze_swe_enforcement_cube(
        read_records(derived_path),
        read_records(core_path),
        checkpoint_lock,
        config,
        core_records_sha256=core_sha256,
        core_analysis_sha256=sha256_file(core_analysis_path),
        checkpoint_lock_sha256=sha256_file(checkpoint_lock_path),
    )
    result.update(
        {
            "derived_input_sha256": sha256_file(derived_path),
            "core_input_sha256": core_sha256,
            "core_analysis_sha256": sha256_file(core_analysis_path),
            "checkpoint_lock_sha256": sha256_file(checkpoint_lock_path),
            "config_sha256": sha256_file(config_path),
        }
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"analysis={output_path}")
    print(f"analysis_sha256={sha256_file(output_path)}")


if __name__ == "__main__":
    main()
