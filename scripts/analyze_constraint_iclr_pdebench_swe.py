"""Adjudicate the frozen PDEBench 2D shallow-water factorial."""

from __future__ import annotations

import argparse
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
from constraint_iclr_common import bootstrap_mean_ci, holm_adjust, sha256_file, stable_seed

TRAINED_MECHANISMS = ("free", "free_res", "hard_abs", "hard")
MECHANISMS = (*TRAINED_MECHANISMS, "projection")


def _all_finite(value: Any) -> bool:
    if isinstance(value, dict):
        return all(_all_finite(item) for item in value.values())
    if isinstance(value, list):
        return all(_all_finite(item) for item in value)
    if isinstance(value, float):
        return math.isfinite(value)
    return True


def validate_swe_records(
    records: list[dict[str, Any]], config: dict[str, Any]
) -> dict[tuple[int, str], dict[str, Any]]:
    seeds = [int(value) for value in config["seeds"]]
    expected = {(seed, mechanism) for seed in seeds for mechanism in MECHANISMS}
    expected_cases = {str(value) for value in config["evaluation"]["case_names"]}
    expected_horizons = {
        str(int(value)) for value in config["evaluation"]["horizons"]
    }
    required_sources = [
        str(config["active_config_path"]),
        str(config["protocol_path"]),
        str(config["source_metadata_path"]),
        str(config["data_decision_path"]),
        str(config["transport_decision_path"]),
        str(config["dataset"]["lock_path"]),
    ]
    if config.get("model_decision_path"):
        required_sources.append(str(config["model_decision_path"]))
    if config.get("distributed_runtime_path"):
        required_sources.append(str(config["distributed_runtime_path"]))
    failures: list[str] = []
    indexed: dict[tuple[int, str], dict[str, Any]] = {}
    run_ids: set[str] = set()
    source_manifests: set[str] = set()
    drift_atol = float(config["factorial_analysis"]["invariant_drift_atol"])
    primary_metric = str(config["evaluation"]["primary_metric"])
    required_metrics = {
        primary_metric,
        "total_rmse",
        "mean_abs_invariant_drift",
        "max_abs_invariant_drift",
        "mean_abs_target_invariant_drift",
        "max_abs_target_invariant_drift",
        "negative_depth_fraction",
        "mean_negative_depth_deficit",
        "minimum_predicted_depth",
    }
    for record in records:
        key = (int(record.get("seed", -1)), str(record.get("mechanism")))
        run_id = str(record.get("run_id"))
        if key in indexed:
            failures.append(f"duplicate SWE seed/mechanism {key}")
        if run_id in run_ids:
            failures.append(f"duplicate SWE run ID {run_id}")
        indexed[key] = record
        run_ids.add(run_id)
        if record.get("schema_version") != "constraint-iclr-pdebench-swe-v1":
            failures.append(f"wrong SWE schema for {key}")
        if record.get("stage") != config["stage"]:
            failures.append(f"wrong SWE stage for {key}")
        if record.get("benchmark_id") != config["benchmark_id"]:
            failures.append(f"wrong SWE benchmark for {key}")
        if record.get("protocol_sha256") != config["protocol_sha256"]:
            failures.append(f"wrong SWE protocol for {key}")
        if record.get("data_lock_sha256") != config["dataset"]["lock_sha256"]:
            failures.append(f"wrong SWE data lock for {key}")
        if not _all_finite(record):
            failures.append(f"non-finite SWE record for {key}")
        provenance = record.get("provenance", {})
        if provenance.get("git_head") != config["expected_git_head"]:
            failures.append(f"wrong SWE Git head for {key}")
        if bool(provenance.get("git_dirty")) is not bool(config["expected_git_dirty"]):
            failures.append(f"wrong SWE dirty flag for {key}")
        sources = provenance.get("source_sha256", {})
        if not isinstance(sources, dict):
            failures.append(f"missing SWE source manifest for {key}")
        else:
            source_manifests.add(json.dumps(sources, sort_keys=True))
            for required in required_sources:
                if required not in sources:
                    failures.append(f"source manifest for {key} omits {required}")
        cases = record.get("cases", {})
        if set(cases) != expected_cases:
            failures.append(f"wrong SWE cases for {key}")
        else:
            for case, horizons in cases.items():
                if set(horizons) != expected_horizons:
                    failures.append(f"wrong SWE horizons for {key}, {case}")
                    continue
                for horizon, metrics in horizons.items():
                    missing_metrics = required_metrics.difference(metrics)
                    if missing_metrics:
                        failures.append(
                            f"missing SWE metrics for {key}, {case}, {horizon}: "
                            f"{sorted(missing_metrics)}"
                        )
                        continue
                    if not 0.0 <= float(metrics["negative_depth_fraction"]) <= 1.0:
                        failures.append(
                            f"invalid SWE negative-depth fraction for {key}, {case}, {horizon}"
                        )
                    if float(metrics["mean_negative_depth_deficit"]) < 0.0:
                        failures.append(
                            f"invalid SWE negative-depth deficit for {key}, {case}, {horizon}"
                        )
        if record.get("training_index_sha256") != record.get(
            "training_subset", {}
        ).get("index_sha256"):
            failures.append(f"SWE training-index mismatch for {key}")
        checkpoint = record.get("checkpoint", {})
        if not isinstance(checkpoint.get("sha256"), str) or len(
            checkpoint["sha256"]
        ) != 64:
            failures.append(f"missing SWE checkpoint SHA-256 for {key}")
        if int(checkpoint.get("bytes", 0)) <= 0:
            failures.append(f"invalid SWE checkpoint byte count for {key}")

    if set(indexed) != expected:
        failures.append(
            f"SWE coverage mismatch: missing={sorted(expected.difference(indexed))}, "
            f"extra={sorted(set(indexed).difference(expected))}"
        )
    if len(source_manifests) != 1:
        failures.append("SWE records do not share one exact source SHA-256 manifest")
    if not expected.difference(indexed):
        for seed in seeds:
            seed_records = [indexed[(seed, mechanism)] for mechanism in MECHANISMS]
            subset_hashes = {
                str(record["training_subset"]["index_sha256"])
                for record in seed_records
            }
            if len(subset_hashes) != 1:
                failures.append(f"unpaired SWE training subset for seed {seed}")
            trained = [indexed[(seed, mechanism)] for mechanism in TRAINED_MECHANISMS]
            parameter_counts = {
                int(record["compute"]["trainable_parameters"]) for record in trained
            }
            if len(parameter_counts) != 1:
                failures.append(f"unequal SWE parameter counts for seed {seed}")
            initialization_hashes = {
                str(record["initialization_sha256"]) for record in trained
            }
            if len(initialization_hashes) != 1:
                failures.append(f"unpaired SWE initialization for seed {seed}")
            for mechanism in TRAINED_MECHANISMS:
                if int(indexed[(seed, mechanism)]["compute"]["optimization_runs"]) != 1:
                    failures.append(
                        f"wrong SWE optimization count for {seed}, {mechanism}"
                    )
            free = indexed[(seed, "free")]
            projection = indexed[(seed, "projection")]
            if projection.get("derived_from") != free.get("run_id"):
                failures.append(f"SWE projection parent mismatch for seed {seed}")
            if int(projection["compute"]["optimization_runs"]) != 0:
                failures.append(f"SWE projection was optimized for seed {seed}")
            if projection.get("checkpoint") != free.get("checkpoint"):
                failures.append(f"SWE projection checkpoint mismatch for seed {seed}")
            for case in expected_cases:
                free_h1 = float(free["cases"][case]["1"][primary_metric])
                projection_h1 = float(projection["cases"][case]["1"][primary_metric])
                if not math.isclose(free_h1, projection_h1, rel_tol=1e-5, abs_tol=1e-8):
                    failures.append(
                        f"SWE horizon-one projection identity failure for {seed}, {case}"
                    )
                for mechanism in ("hard_abs", "hard", "projection"):
                    for horizon in expected_horizons:
                        drift = float(
                            indexed[(seed, mechanism)]["cases"][case][horizon][
                                "max_abs_invariant_drift"
                            ]
                        )
                        if drift > drift_atol:
                            failures.append(
                                f"SWE invariant gate failure for {seed}, {mechanism}, "
                                f"{case}, h={horizon}: {drift}"
                            )
    if failures:
        raise RuntimeError("; ".join(failures))
    return indexed


def _metric_values(
    indexed: dict[tuple[int, str], dict[str, Any]],
    seeds: list[int],
    mechanism: str,
    case: str,
    horizon: int,
    metric: str,
) -> np.ndarray:
    return np.asarray(
        [
            indexed[(seed, mechanism)]["cases"][case][str(horizon)][metric]
            for seed in seeds
        ],
        dtype=np.float64,
    )


def _summary(
    values: np.ndarray,
    *,
    name: str,
    case: str,
    horizon: int,
    confidence: float,
    draws: int,
) -> dict[str, Any]:
    interval = bootstrap_mean_ci(
        values,
        confidence=confidence,
        draws=draws,
        seed=stable_seed(20260902, f"swe:{name}:{case}:{horizon}:{confidence}"),
    )
    return {"mean": float(np.mean(values)), "ci": list(interval)}


def analyze_swe_cell(
    indexed: dict[tuple[int, str], dict[str, Any]],
    seeds: list[int],
    config: dict[str, Any],
    case: str,
    horizon: int,
) -> dict[str, Any]:
    settings = config["factorial_analysis"]
    metric = str(config["evaluation"]["primary_metric"])
    values = {
        mechanism: _metric_values(indexed, seeds, mechanism, case, horizon, metric)
        for mechanism in MECHANISMS
    }
    a0 = values["free"]
    r0 = values["free_res"]
    a1 = values["hard_abs"]
    r1 = values["hard"]
    p0 = a0 - r0
    p1 = a1 - r1
    e_abs = a0 - a1
    e_res = r0 - r1
    interaction = p0 - p1
    phi_parameterization = 0.5 * (p0 + p1)
    phi_enforcement = 0.5 * (e_abs + e_res)
    efficiency_error = phi_parameterization + phi_enforcement - (a0 - r1)
    maximum_efficiency_error = float(np.max(np.abs(efficiency_error)))
    if maximum_efficiency_error > float(settings["shapley_efficiency_atol"]):
        raise RuntimeError(f"SWE Shapley efficiency failed for {case}, h={horizon}")
    draws = int(settings["bootstrap_draws"])
    confidence95 = float(settings["confidence_nonzero"])
    confidence90 = float(settings["confidence_equivalence"])
    interaction95 = _summary(
        interaction,
        name="interaction95",
        case=case,
        horizon=horizon,
        confidence=confidence95,
        draws=draws,
    )
    interaction90 = _summary(
        interaction,
        name="interaction90",
        case=case,
        horizon=horizon,
        confidence=confidence90,
        draws=draws,
    )
    sesoi = float(settings["sesoi_fraction_of_free_res"]) * float(np.mean(r0))
    low95, high95 = (float(value) for value in interaction95["ci"])
    low90, high90 = (float(value) for value in interaction90["ci"])
    if low95 > sesoi or high95 < -sesoi:
        classification = "material_nonadditivity"
    elif low95 > 0.0 or high95 < 0.0:
        classification = "statistical_nonadditivity_below_or_crossing_sesoi"
    elif low90 > -sesoi and high90 < sesoi:
        classification = "practical_additivity"
    else:
        classification = "unresolved"
    credits = {
        "parameterization_when_free": p0,
        "parameterization_when_hard": p1,
        "enforcement_in_absolute_coordinates": e_abs,
        "enforcement_in_residual_coordinates": e_res,
        "shapley_parameterization": phi_parameterization,
        "shapley_enforcement": phi_enforcement,
        "projection_minus_hard_abs": values["projection"] - a1,
    }
    return {
        "case": case,
        "horizon": horizon,
        "primary_metric": metric,
        "cell_mean_primary_metric": {
            mechanism: float(np.mean(mechanism_values))
            for mechanism, mechanism_values in values.items()
        },
        "credits": {
            name: _summary(
                credit,
                name=name,
                case=case,
                horizon=horizon,
                confidence=confidence95,
                draws=draws,
            )
            for name, credit in credits.items()
        },
        "interaction": {
            "mean": float(np.mean(interaction)),
            "ci95": interaction95["ci"],
            "ci90": interaction90["ci"],
            "sesoi": sesoi,
            "classification": classification,
            "sign_flip_p": paired_sign_flip_pvalue(
                interaction,
                seed=stable_seed(20260902, f"swe-sign:{case}:{horizon}"),
                draws=int(settings["sign_flip_draws"]),
            ),
        },
        "max_abs_shapley_efficiency_error": maximum_efficiency_error,
    }


def analyze_swe_records(
    records: list[dict[str, Any]], config: dict[str, Any]
) -> dict[str, Any]:
    indexed = validate_swe_records(records, config)
    seeds = [int(value) for value in config["seeds"]]
    cells = [
        analyze_swe_cell(indexed, seeds, config, str(case), int(horizon))
        for case in config["evaluation"]["case_names"]
        for horizon in config["evaluation"]["horizons"]
    ]
    if config["stage"] == "swe_factorial_confirmation" and len(cells) != 8:
        raise RuntimeError("formal SWE analysis requires exactly eight cells")
    adjusted = holm_adjust([float(cell["interaction"]["sign_flip_p"]) for cell in cells])
    for cell, adjusted_p in zip(cells, adjusted, strict=True):
        cell["interaction"]["sign_flip_p_holm"] = adjusted_p
    primary = next(
        cell
        for cell in cells
        if cell["case"] == config["evaluation"]["primary_case"]
        and cell["horizon"] == int(config["evaluation"]["primary_horizon"])
    )
    descriptive_metrics = [
        str(config["evaluation"]["primary_metric"]),
        "total_rmse",
        "mean_abs_invariant_drift",
        "max_abs_invariant_drift",
        "negative_depth_fraction",
        "mean_negative_depth_deficit",
        "minimum_predicted_depth",
    ]
    primary_case = str(config["evaluation"]["primary_case"])
    primary_horizon = int(config["evaluation"]["primary_horizon"])
    return {
        "schema_version": "constraint-iclr-pdebench-swe-factorial-analysis-v1",
        "benchmark_id": config["benchmark_id"],
        "record_count": len(records),
        "seeds": seeds,
        "integrity_gates_passed": True,
        "primary": primary,
        "primary_descriptive_table": {
            mechanism: {
                metric: float(
                    np.mean(
                        _metric_values(
                            indexed,
                            seeds,
                            mechanism,
                            primary_case,
                            primary_horizon,
                            metric,
                        )
                    )
                )
                for metric in descriptive_metrics
            }
            for mechanism in MECHANISMS
        },
        "all_cases": cells,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(
            "configs/constraint_iclr/pdebench_swe_rdb_factorial_20260902.yaml"
        ),
    )
    parser.add_argument("--input", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "experiments/constraint_attribution_iclr/pdebench/"
            "swe_factorial_analysis_20260902.json"
        ),
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    config_path = args.config if args.config.is_absolute() else root / args.config
    config = load_config(config_path)
    input_path = args.input or Path(str(config["output"]))
    if not input_path.is_absolute():
        input_path = root / input_path
    output_path = args.output if args.output.is_absolute() else root / args.output
    result = analyze_swe_records(read_records(input_path), config)
    result["input_sha256"] = sha256_file(input_path)
    result["config_sha256"] = sha256_file(config_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"analysis={output_path}")
    print(f"analysis_sha256={sha256_file(output_path)}")


if __name__ == "__main__":
    main()
