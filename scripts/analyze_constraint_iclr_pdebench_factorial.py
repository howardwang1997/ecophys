"""Adjudicate the prospectively frozen PDEBench 2x2 attribution experiment."""

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


def validate_factorial_records(
    records: list[dict[str, Any]], config: dict[str, Any]
) -> dict[tuple[int, str], dict[str, Any]]:
    seeds = [int(value) for value in config["seeds"]]
    expected_pairs = {(seed, mechanism) for seed in seeds for mechanism in MECHANISMS}
    expected_protocol = str(config["protocol_sha256"])
    expected_schema = str(config["schema_amendment_sha256"])
    expected_lock = str(config["dataset"]["lock_sha256"])
    expected_stage = str(config["stage"])
    expected_benchmark = str(config["benchmark_id"])
    expected_git_head = str(config["expected_git_head"])
    expected_git_dirty = bool(config["expected_git_dirty"])
    expected_cases = {str(value) for value in config["evaluation"]["case_names"]}
    expected_horizons = {
        str(int(value)) for value in config["evaluation"]["horizons"]
    }
    drift_atol = float(config["factorial_analysis"]["invariant_drift_atol"])
    failures: list[str] = []
    indexed: dict[tuple[int, str], dict[str, Any]] = {}
    run_ids: set[str] = set()
    source_manifests: set[str] = set()

    for record in records:
        seed = int(record.get("seed", -1))
        mechanism = str(record.get("mechanism"))
        key = (seed, mechanism)
        run_id = str(record.get("run_id"))
        if key in indexed:
            failures.append(f"duplicate seed/mechanism {key}")
        if run_id in run_ids:
            failures.append(f"duplicate run_id {run_id}")
        indexed[key] = record
        run_ids.add(run_id)
        if record.get("stage") != expected_stage:
            failures.append(f"wrong stage for {key}")
        if record.get("benchmark_id") != expected_benchmark:
            failures.append(f"wrong benchmark for {key}")
        if record.get("protocol_sha256") != expected_protocol:
            failures.append(f"wrong protocol binding for {key}")
        if record.get("schema_amendment_sha256") != expected_schema:
            failures.append(f"wrong schema-amendment binding for {key}")
        if record.get("data_lock_sha256") != expected_lock:
            failures.append(f"wrong data-lock binding for {key}")
        if not _all_finite(record):
            failures.append(f"non-finite numeric field for {key}")
        provenance = record.get("provenance", {})
        if provenance.get("git_head") != expected_git_head:
            failures.append(f"wrong Git head for {key}")
        if bool(provenance.get("git_dirty")) is not expected_git_dirty:
            failures.append(f"wrong dirty-worktree flag for {key}")
        source_sha256 = provenance.get("source_sha256", {})
        if not isinstance(source_sha256, dict):
            failures.append(f"missing source manifest for {key}")
        else:
            source_manifests.add(json.dumps(source_sha256, sort_keys=True))
            for required_path in (
                str(config["protocol_path"]),
                str(config["decision_path"]),
                str(config["dataset"]["lock_path"]),
            ):
                if required_path not in source_sha256:
                    failures.append(f"source manifest for {key} omits {required_path}")
        cases = record.get("cases", {})
        if set(cases) != expected_cases:
            failures.append(f"wrong evaluation cases for {key}")
        else:
            for case, horizons in cases.items():
                if set(horizons) != expected_horizons:
                    failures.append(f"wrong horizons for {key}, {case}")
        if record.get("training_index_sha256") != record.get("training_subset", {}).get(
            "index_sha256"
        ):
            failures.append(f"training-index hash mismatch for {key}")

    missing = expected_pairs.difference(indexed)
    extra = set(indexed).difference(expected_pairs)
    if missing:
        failures.append(f"missing seed/mechanism pairs: {sorted(missing)}")
    if extra:
        failures.append(f"unexpected seed/mechanism pairs: {sorted(extra)}")
    if len(source_manifests) != 1:
        failures.append("records do not share one exact source SHA-256 manifest")

    if not missing:
        for seed in seeds:
            seed_records = [indexed[(seed, mechanism)] for mechanism in MECHANISMS]
            subset_hashes = {
                str(record["training_subset"]["index_sha256"])
                for record in seed_records
            }
            if len(subset_hashes) != 1:
                failures.append(f"unpaired training subset for seed {seed}")
            trained = [indexed[(seed, mechanism)] for mechanism in TRAINED_MECHANISMS]
            parameter_counts = {
                int(record["compute"]["trainable_parameters"]) for record in trained
            }
            if len(parameter_counts) != 1:
                failures.append(f"unequal trained parameter counts for seed {seed}")
            initialization_hashes = {
                str(record.get("initialization_sha256")) for record in trained
            }
            if len(initialization_hashes) != 1 or "None" in initialization_hashes:
                failures.append(f"unequal or missing initialization digest for seed {seed}")
            free = indexed[(seed, "free")]
            projection = indexed[(seed, "projection")]
            if projection.get("derived_from") != free.get("run_id"):
                failures.append(f"projection parent mismatch for seed {seed}")
            if projection.get("initialization_sha256") != free.get(
                "initialization_sha256"
            ):
                failures.append(f"projection initialization mismatch for seed {seed}")
            if int(projection["compute"]["optimization_runs"]) != 0:
                failures.append(f"projection was unexpectedly optimized for seed {seed}")
            for mechanism in TRAINED_MECHANISMS:
                if int(indexed[(seed, mechanism)]["compute"]["optimization_runs"]) != 1:
                    failures.append(f"wrong optimization count for seed {seed}, {mechanism}")
            for case in expected_cases:
                free_value = float(free["cases"][case]["1"]["conserving_rmse"])
                projected_value = float(
                    projection["cases"][case]["1"]["conserving_rmse"]
                )
                if not math.isclose(
                    free_value, projected_value, rel_tol=1e-5, abs_tol=1e-8
                ):
                    failures.append(
                        f"projection horizon-one identity failure for seed {seed}, {case}"
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
                                "hard invariant gate failure for "
                                f"seed {seed}, {mechanism}, {case}, h={horizon}: {drift}"
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
        seed=stable_seed(20260901, f"factorial:{name}:{case}:{horizon}:{confidence}"),
    )
    return {"mean": float(np.mean(values)), "ci": list(interval)}


def analyze_factorial_cell(
    indexed: dict[tuple[int, str], dict[str, Any]],
    seeds: list[int],
    config: dict[str, Any],
    case: str,
    horizon: int,
) -> dict[str, Any]:
    settings = config["factorial_analysis"]
    draws = int(settings["bootstrap_draws"])
    confidence95 = float(settings["confidence_nonzero"])
    confidence90 = float(settings["confidence_equivalence"])
    a0 = _metric_values(indexed, seeds, "free", case, horizon, "conserving_rmse")
    r0 = _metric_values(indexed, seeds, "free_res", case, horizon, "conserving_rmse")
    a1 = _metric_values(indexed, seeds, "hard_abs", case, horizon, "conserving_rmse")
    r1 = _metric_values(indexed, seeds, "hard", case, horizon, "conserving_rmse")
    projected = _metric_values(
        indexed, seeds, "projection", case, horizon, "conserving_rmse"
    )

    p0 = a0 - r0
    p1 = a1 - r1
    e_abs = a0 - a1
    e_res = r0 - r1
    interaction = p0 - p1
    phi_parameterization = 0.5 * (p0 + p1)
    phi_enforcement = 0.5 * (e_abs + e_res)
    efficiency_error = phi_parameterization + phi_enforcement - (a0 - r1)
    efficiency_atol = float(settings["shapley_efficiency_atol"])
    maximum_efficiency_error = float(np.max(np.abs(efficiency_error)))
    if maximum_efficiency_error > efficiency_atol:
        raise RuntimeError(
            "Shapley efficiency identity failed for "
            f"{case}, horizon {horizon}: {maximum_efficiency_error}"
        )

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
        "projection_minus_hard_abs": projected - a1,
    }
    credit_summaries = {
        name: _summary(
            values,
            name=name,
            case=case,
            horizon=horizon,
            confidence=confidence95,
            draws=draws,
        )
        for name, values in credits.items()
    }
    return {
        "case": case,
        "horizon": horizon,
        "cell_mean_conserving_rmse": {
            "absolute_free": float(np.mean(a0)),
            "residual_free": float(np.mean(r0)),
            "absolute_hard": float(np.mean(a1)),
            "residual_hard": float(np.mean(r1)),
            "absolute_free_projected": float(np.mean(projected)),
        },
        "credits": credit_summaries,
        "interaction": {
            "mean": float(np.mean(interaction)),
            "ci95": interaction95["ci"],
            "ci90": interaction90["ci"],
            "sesoi": sesoi,
            "classification": classification,
            "sign_flip_p": paired_sign_flip_pvalue(
                interaction,
                seed=stable_seed(20260901, f"factorial-sign:{case}:{horizon}"),
                draws=int(settings["sign_flip_draws"]),
            ),
        },
        "max_abs_shapley_efficiency_error": maximum_efficiency_error,
    }


def _primary_descriptive_table(
    indexed: dict[tuple[int, str], dict[str, Any]],
    seeds: list[int],
    case: str,
    horizon: int,
) -> dict[str, dict[str, float]]:
    metrics = (
        "conserving_rmse",
        "total_rmse",
        "mean_abs_invariant_drift",
        "max_abs_invariant_drift",
    )
    return {
        mechanism: {
            metric: float(
                np.mean(
                    _metric_values(
                        indexed, seeds, mechanism, case, horizon, metric
                    )
                )
            )
            for metric in metrics
        }
        for mechanism in MECHANISMS
    }


def analyze_factorial_records(
    records: list[dict[str, Any]], config: dict[str, Any]
) -> dict[str, Any]:
    indexed = validate_factorial_records(records, config)
    seeds = [int(value) for value in config["seeds"]]
    cells = [
        analyze_factorial_cell(indexed, seeds, config, str(case), int(horizon))
        for case in config["evaluation"]["case_names"]
        for horizon in config["evaluation"]["horizons"]
    ]
    adjusted = holm_adjust(
        [float(cell["interaction"]["sign_flip_p"]) for cell in cells]
    )
    for cell, adjusted_p in zip(cells, adjusted, strict=True):
        cell["interaction"]["sign_flip_p_holm"] = adjusted_p
    primary = next(
        cell
        for cell in cells
        if cell["case"] == config["evaluation"]["primary_case"]
        and cell["horizon"] == int(config["evaluation"]["primary_horizon"])
    )
    primary_case = str(config["evaluation"]["primary_case"])
    primary_horizon = int(config["evaluation"]["primary_horizon"])
    return {
        "schema_version": "constraint-iclr-pdebench-factorial-analysis-v1",
        "benchmark_id": config["benchmark_id"],
        "record_count": len(records),
        "seeds": seeds,
        "integrity_gates_passed": True,
        "primary": primary,
        "primary_descriptive_table": _primary_descriptive_table(
            indexed, seeds, primary_case, primary_horizon
        ),
        "all_cases": cells,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(
            "configs/constraint_iclr/pdebench_advection_fno_factorial_20260901.yaml"
        ),
    )
    parser.add_argument("--input", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "experiments/constraint_attribution_iclr/pdebench/"
            "factorial_analysis_20260901.json"
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
    result = analyze_factorial_records(read_records(input_path), config)
    result["input_sha256"] = sha256_file(input_path)
    result["config_sha256"] = sha256_file(config_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"analysis={output_path}")


if __name__ == "__main__":
    main()
