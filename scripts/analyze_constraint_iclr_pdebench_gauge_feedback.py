"""Validate and analyze the frozen Advection input-gauge feedback intervention."""

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
from analyze_constraint_iclr_pdebench_enforcement_cube import (
    canonical_object_sha256,
    validate_cube_records,
)
from analyze_constraint_iclr_pdebench_gradient_coupling import spearman_bootstrap
from constraint_iclr_common import (
    bootstrap_mean_ci,
    canonical_run_id,
    holm_adjust,
    sha256_file,
    stable_seed,
)
from constraint_iclr_gauge_identity import gauge_identity_gate

REQUIRED_METRICS = {
    "feedback_rmse",
    "projected_history_conserving_rmse",
    "raw_history_conserving_rmse",
    "feedback_ratio",
    "first_step_gauge_rmse",
    "step_one_q_identity_max_abs",
    "step_one_gauge_nonconstant_max_abs",
    "step_one_identity_scale_max_abs",
}


def _all_finite(value: Any) -> bool:
    if isinstance(value, dict):
        return all(_all_finite(item) for item in value.values())
    if isinstance(value, list):
        return all(_all_finite(item) for item in value)
    if isinstance(value, float):
        return math.isfinite(value)
    return True


def validate_gauge_feedback_records(
    records: list[dict[str, Any]],
    core: dict[tuple[int, str], dict[str, Any]],
    checkpoint_lock: dict[str, Any],
    config: dict[str, Any],
) -> dict[tuple[int, str], dict[str, Any]]:
    gauge = config["gauge_feedback"]
    seeds = [int(value) for value in config["seeds"]]
    mechanisms = [str(value) for value in gauge["parent_mechanisms"]]
    maps = {str(key): str(value) for key, value in gauge["compatible_forward_maps"].items()}
    expected = {(seed, mechanism) for seed in seeds for mechanism in mechanisms}
    cases = {str(value) for value in config["evaluation"]["case_names"]}
    checkpoints = {
        (int(entry["seed"]), str(entry["mechanism"])): entry for entry in checkpoint_lock["checkpoints"]
    }
    required_sources = {
        str(config["active_config_path"]),
        str(gauge["protocol_path"]),
        str(gauge["decision_path"]),
        str(gauge["identity_runtime_amendment_path"]),
        str(gauge["identity_runtime_decision_path"]),
        str(config["dataset"]["lock_path"]),
        str(config["cube"]["checkpoint_lock"]),
    }
    exact_source_hashes = {
        str(gauge["protocol_path"]): str(gauge["protocol_sha256"]),
        str(gauge["decision_path"]): str(gauge["decision_sha256"]),
        str(gauge["identity_runtime_amendment_path"]): str(gauge["identity_runtime_amendment_sha256"]),
        str(gauge["identity_runtime_decision_path"]): str(gauge["identity_runtime_decision_sha256"]),
        str(config["dataset"]["lock_path"]): str(config["dataset"]["lock_sha256"]),
        str(config["cube"]["checkpoint_lock"]): str(gauge["checkpoint_lock_sha256"]),
    }
    failures: list[str] = []
    indexed: dict[tuple[int, str], dict[str, Any]] = {}
    run_ids: set[str] = set()
    source_manifests: set[str] = set()

    for record in records:
        key = (int(record.get("seed", -1)), str(record.get("mechanism")))
        run_id = str(record.get("run_id"))
        if key in indexed:
            failures.append(f"duplicate gauge-feedback seed/mechanism {key}")
        if run_id in run_ids:
            failures.append(f"duplicate gauge-feedback run ID {run_id}")
        indexed[key] = record
        run_ids.add(run_id)
        expected_fields = {
            "schema_version": gauge["schema_version"],
            "stage": gauge["stage"],
            "benchmark_id": config["benchmark_id"],
            "dataset_sha256": config["dataset"]["expected_sha256"],
            "data_lock_sha256": config["dataset"]["lock_sha256"],
            "gauge_protocol_sha256": gauge["protocol_sha256"],
            "gauge_decision_sha256": gauge["decision_sha256"],
            "gauge_identity_amendment_sha256": gauge["identity_runtime_amendment_sha256"],
            "gauge_identity_decision_sha256": gauge["identity_runtime_decision_sha256"],
            "core_records_sha256": gauge["parent_core_records_sha256"],
            "core_analysis_sha256": gauge["parent_core_analysis_sha256"],
            "cube_records_sha256": gauge["parent_cube_records_sha256"],
            "cube_analysis_sha256": gauge["parent_cube_analysis_sha256"],
            "checkpoint_lock_sha256": gauge["checkpoint_lock_sha256"],
        }
        for field, expected_value in expected_fields.items():
            if record.get(field) != expected_value:
                failures.append(f"wrong gauge-feedback {field} for {key}")
        if key not in expected:
            continue
        parent = core[key]
        checkpoint = checkpoints.get(key)
        if checkpoint is None:
            failures.append(f"missing locked checkpoint for {key}")
            continue
        if record.get("forward_map") != maps[key[1]]:
            failures.append(f"wrong compatible forward map for {key}")
        identity = {
            **expected_fields,
            "seed": key[0],
            "mechanism": key[1],
            "forward_map": maps[key[1]],
            "parent_run_id": parent["run_id"],
        }
        if canonical_run_id(identity) != run_id:
            failures.append(f"noncanonical gauge-feedback run ID for {key}")
        if record.get("derived_from") != parent["run_id"]:
            failures.append(f"wrong gauge-feedback parent run ID for {key}")
        if record.get("training_index_sha256") != parent["training_index_sha256"]:
            failures.append(f"wrong training-index binding for {key}")
        if record.get("initialization_sha256") != parent["initialization_sha256"]:
            failures.append(f"wrong initialization binding for {key}")
        parent_binding = record.get("parent", {})
        expected_parent = {
            "run_id": parent["run_id"],
            "mechanism": key[1],
            "checkpoint_path": checkpoint["path"],
            "checkpoint_sha256": checkpoint["sha256"],
            "checkpoint_bytes": checkpoint["bytes"],
            "training_index_sha256": parent["training_index_sha256"],
            "initialization_sha256": parent["initialization_sha256"],
            "provenance_sha256": canonical_object_sha256(parent["provenance"]),
        }
        for field, expected_value in expected_parent.items():
            if parent_binding.get(field) != expected_value:
                failures.append(f"wrong parent {field} for {key}")
        compute = record.get("compute", {})
        for field in ("optimization_runs", "examples_seen", "proxy"):
            if int(compute.get(field, -1)) != 0:
                failures.append(f"nonzero gauge-feedback {field} for {key}")
        if float(compute.get("training_runtime_seconds", math.nan)) != 0.0:
            failures.append(f"nonzero gauge-feedback training runtime for {key}")
        record_cases = record.get("cases", {})
        if set(record_cases) != cases:
            failures.append(f"wrong gauge-feedback case coverage for {key}")
        else:
            for case, metrics in record_cases.items():
                if set(metrics) != REQUIRED_METRICS:
                    failures.append(f"wrong metric coverage for {key}, {case}")
                    continue
                if float(metrics["projected_history_conserving_rmse"]) <= 0.0:
                    failures.append(f"non-positive feedback denominator for {key}, {case}")
                expected_ratio = float(metrics["feedback_rmse"]) / float(
                    metrics["projected_history_conserving_rmse"]
                )
                if not math.isclose(
                    float(metrics["feedback_ratio"]),
                    expected_ratio,
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                ):
                    failures.append(f"feedback ratio identity failed for {key}, {case}")
                try:
                    _, _, identity_passed = gauge_identity_gate(metrics, gauge)
                except (KeyError, TypeError, ValueError) as error:
                    failures.append(f"invalid gauge identity gate for {key}, {case}: {error}")
                else:
                    if not identity_passed:
                        failures.append(f"gauge identity failed for {key}, {case}")
        if not _all_finite(record):
            failures.append(f"non-finite gauge-feedback record for {key}")
        provenance = record.get("provenance", {})
        if provenance.get("git_head") != config["expected_git_head"]:
            failures.append(f"wrong gauge-feedback Git head for {key}")
        if bool(provenance.get("git_dirty")) is not bool(config["expected_git_dirty"]):
            failures.append(f"wrong gauge-feedback dirty flag for {key}")
        sources = provenance.get("source_sha256", {})
        if not isinstance(sources, dict):
            failures.append(f"missing source manifest for {key}")
        else:
            source_manifests.add(json.dumps(sources, sort_keys=True))
            for required in required_sources:
                if required not in sources:
                    failures.append(f"source manifest omits {required} for {key}")
            for path, expected_hash in exact_source_hashes.items():
                if sources.get(path) != expected_hash:
                    failures.append(f"source manifest has wrong hash for {path}, {key}")

    if set(indexed) != expected:
        failures.append(
            "gauge-feedback coverage mismatch: "
            f"missing={sorted(expected.difference(indexed))}, "
            f"extra={sorted(set(indexed).difference(expected))}"
        )
    if len(records) != int(gauge["expected_records"]):
        failures.append("wrong gauge-feedback record count")
    if len(source_manifests) != 1:
        failures.append("gauge-feedback records do not share one source manifest")
    if failures:
        raise RuntimeError("; ".join(failures))
    return indexed


def _summary(
    values: np.ndarray,
    *,
    name: str,
    case: str,
    draws: int,
) -> dict[str, Any]:
    ci95 = bootstrap_mean_ci(
        values,
        confidence=0.95,
        draws=draws,
        seed=stable_seed(20260902, f"gauge-feedback:{name}:{case}:0.95"),
    )
    ci90 = bootstrap_mean_ci(
        values,
        confidence=0.90,
        draws=draws,
        seed=stable_seed(20260902, f"gauge-feedback:{name}:{case}:0.90"),
    )
    return {
        "mean": float(np.mean(values)),
        "ci95": list(ci95),
        "ci90": list(ci90),
    }


def _classify_ratio(summary: dict[str, Any], threshold: float) -> str:
    low95, _ = (float(value) for value in summary["ci95"])
    low90, high90 = (float(value) for value in summary["ci90"])
    if low95 > threshold:
        return "material_gauge_feedback"
    if low90 >= 0.0 and high90 < threshold:
        return "practically_negligible_gauge_feedback"
    return "unresolved"


def analyze_gauge_feedback(
    records: list[dict[str, Any]],
    core_records: list[dict[str, Any]],
    cube_records: list[dict[str, Any]],
    checkpoint_lock: dict[str, Any],
    config: dict[str, Any],
    *,
    core_records_sha256: str,
    core_analysis_sha256: str,
    checkpoint_lock_sha256: str,
) -> dict[str, Any]:
    core, cube = validate_cube_records(
        cube_records,
        core_records,
        checkpoint_lock,
        config,
        core_records_sha256=core_records_sha256,
        core_analysis_sha256=core_analysis_sha256,
        checkpoint_lock_sha256=checkpoint_lock_sha256,
    )
    indexed = validate_gauge_feedback_records(records, core, checkpoint_lock, config)
    gauge = config["gauge_feedback"]
    seeds = [int(value) for value in config["seeds"]]
    mechanisms = [str(value) for value in gauge["parent_mechanisms"]]
    cases = [str(value) for value in config["evaluation"]["case_names"]]
    draws = int(gauge["bootstrap_draws"])
    threshold = float(gauge["practical_ratio_threshold"])

    identity_audits = [
        gauge_identity_gate(indexed[(seed, mechanism)]["cases"][case], gauge)
        for seed in seeds
        for mechanism in mechanisms
        for case in cases
    ]

    cells: list[dict[str, Any]] = []
    contrast_p_values: list[float] = []
    for case in cases:
        by_mechanism = {
            mechanism: np.asarray(
                [float(indexed[(seed, mechanism)]["cases"][case]["feedback_ratio"]) for seed in seeds],
                dtype=np.float64,
            )
            for mechanism in mechanisms
        }
        coordinate_average = 0.5 * (by_mechanism["hard_abs"] + by_mechanism["hard"])
        coordinate_contrast = by_mechanism["hard_abs"] - by_mechanism["hard"]
        ratio_summary = _summary(
            coordinate_average,
            name="coordinate-average-ratio",
            case=case,
            draws=draws,
        )
        contrast_p_values.append(
            paired_sign_flip_pvalue(
                coordinate_contrast,
                draws=int(config["factorial_analysis"]["sign_flip_draws"]),
                seed=stable_seed(20260902, f"gauge-feedback:coordinate:{case}"),
            )
        )
        cells.append(
            {
                "case": case,
                "coordinate_average_feedback_ratio": ratio_summary,
                "classification": _classify_ratio(ratio_summary, threshold),
                "by_coordinate_feedback_ratio": {
                    mechanism: _summary(
                        values,
                        name=f"ratio:{mechanism}",
                        case=case,
                        draws=draws,
                    )
                    for mechanism, values in by_mechanism.items()
                },
                "coordinate_contrast": _summary(
                    coordinate_contrast,
                    name="coordinate-contrast",
                    case=case,
                    draws=draws,
                ),
                "coordinate_average_feedback_rmse": _summary(
                    0.5
                    * np.asarray(
                        [
                            float(indexed[(seed, "hard_abs")]["cases"][case]["feedback_rmse"])
                            + float(indexed[(seed, "hard")]["cases"][case]["feedback_rmse"])
                            for seed in seeds
                        ],
                        dtype=np.float64,
                    ),
                    name="coordinate-average-feedback-rmse",
                    case=case,
                    draws=draws,
                ),
            }
        )

    adjusted = holm_adjust(contrast_p_values)
    for cell, raw_p, adjusted_p in zip(cells, contrast_p_values, adjusted, strict=True):
        cell["coordinate_contrast_sign_flip_p_raw"] = raw_p
        cell["coordinate_contrast_sign_flip_p_holm"] = adjusted_p

    primary_case = str(gauge["primary_case"])
    primary = next(cell for cell in cells if cell["case"] == primary_case)
    feedback_ratio = np.asarray(
        [
            0.5
            * (
                float(indexed[(seed, "hard_abs")]["cases"][primary_case]["feedback_ratio"])
                + float(indexed[(seed, "hard")]["cases"][primary_case]["feedback_ratio"])
            )
            for seed in seeds
        ],
        dtype=np.float64,
    )
    horizon = int(config["evaluation"]["primary_horizon"])
    removal_harm = np.asarray(
        [
            0.5
            * (
                float(
                    cube[(seed, "hard_abs_unprojected")]["cases"][primary_case][str(horizon)][
                        "conserving_rmse"
                    ]
                )
                - float(core[(seed, "hard_abs")]["cases"][primary_case][str(horizon)]["conserving_rmse"])
                + float(
                    cube[(seed, "hard_res_unprojected")]["cases"][primary_case][str(horizon)][
                        "conserving_rmse"
                    ]
                )
                - float(core[(seed, "hard")]["cases"][primary_case][str(horizon)]["conserving_rmse"])
            )
            for seed in seeds
        ],
        dtype=np.float64,
    )
    association = spearman_bootstrap(
        feedback_ratio,
        removal_harm,
        draws=draws,
        seed=stable_seed(20260902, "gauge-feedback:final-harm-spearman"),
    )
    return {
        "schema_version": gauge["analysis_schema_version"],
        "benchmark_id": config["benchmark_id"],
        "record_count": len(records),
        "checkpoint_count": len(checkpoint_lock["checkpoints"]),
        "seeds": seeds,
        "integrity_gates_passed": True,
        "practical_ratio_threshold": threshold,
        "identity_integrity": {
            "absolute_floor": float(gauge["identity_atol"]),
            "roundoff_ulps": int(gauge["identity_roundoff_ulps"]),
            "relative_to_projected_baseline_max": float(gauge["identity_relative_baseline_atol"]),
            "max_roundoff_tolerance": max(value[0] for value in identity_audits),
            "max_contamination_fraction": max(value[1] for value in identity_audits),
        },
        "primary": primary,
        "all_cases": cells,
        "secondary_final_harm_association": {
            "case": primary_case,
            "horizon": horizon,
            **association,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/constraint_iclr/pdebench_advection_fno_gauge_feedback_20260902.yaml"),
    )
    parser.add_argument("--input", type=Path)
    parser.add_argument("--core-input", type=Path)
    parser.add_argument("--core-analysis", type=Path)
    parser.add_argument("--cube-input", type=Path)
    parser.add_argument("--cube-analysis", type=Path)
    parser.add_argument("--checkpoint-lock", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    config_path = args.config if args.config.is_absolute() else root / args.config
    config = load_config(config_path)
    gauge = config["gauge_feedback"]

    def resolved_path(value: Path | str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else root / path

    input_path = resolved_path(args.input or gauge["output"])
    core_path = resolved_path(args.core_input or config["output"])
    core_analysis_path = resolved_path(args.core_analysis or config["cube"]["core_analysis"])
    cube_path = resolved_path(args.cube_input or gauge["parent_cube_records"])
    cube_analysis_path = resolved_path(args.cube_analysis or gauge["parent_cube_analysis"])
    lock_path = resolved_path(args.checkpoint_lock or config["cube"]["checkpoint_lock"])
    output_path = resolved_path(args.output or gauge["analysis_output"])

    expected_hashes = {
        core_path: gauge["parent_core_records_sha256"],
        core_analysis_path: gauge["parent_core_analysis_sha256"],
        cube_path: gauge["parent_cube_records_sha256"],
        cube_analysis_path: gauge["parent_cube_analysis_sha256"],
        lock_path: gauge["checkpoint_lock_sha256"],
    }
    for path, expected_hash in expected_hashes.items():
        if sha256_file(path) != str(expected_hash):
            raise RuntimeError(f"bound parent artifact changed: {path}")
    core_analysis = json.loads(core_analysis_path.read_text(encoding="utf-8"))
    cube_analysis = json.loads(cube_analysis_path.read_text(encoding="utf-8"))
    if (
        core_analysis.get("input_sha256") != sha256_file(core_path)
        or core_analysis.get("integrity_gates_passed") is not True
    ):
        raise RuntimeError("core analysis is not integrity-bound")
    if (
        cube_analysis.get("core_input_sha256") != sha256_file(core_path)
        or cube_analysis.get("derived_input_sha256") != sha256_file(cube_path)
        or cube_analysis.get("integrity_gates_passed") is not True
    ):
        raise RuntimeError("cube analysis is not integrity-bound")
    checkpoint_lock = json.loads(lock_path.read_text(encoding="utf-8"))
    result = analyze_gauge_feedback(
        read_records(input_path),
        read_records(core_path),
        read_records(cube_path),
        checkpoint_lock,
        config,
        core_records_sha256=sha256_file(core_path),
        core_analysis_sha256=sha256_file(core_analysis_path),
        checkpoint_lock_sha256=sha256_file(lock_path),
    )
    result.update(
        {
            "input_sha256": sha256_file(input_path),
            "core_records_sha256": sha256_file(core_path),
            "core_analysis_sha256": sha256_file(core_analysis_path),
            "cube_records_sha256": sha256_file(cube_path),
            "cube_analysis_sha256": sha256_file(cube_analysis_path),
            "checkpoint_lock_sha256": sha256_file(lock_path),
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
