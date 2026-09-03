"""Adjudicate the frozen PDEBench external block after complete integrity gates."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from constraint_iclr_common import bootstrap_mean_ci, holm_adjust, sha256_file, stable_seed
from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf

MECHANISMS = {"free", "free_res", "hard", "soft30", "projection"}


def load_config(path: Path) -> dict[str, Any]:
    with initialize_config_dir(version_base=None, config_dir=str(path.parent.resolve())):
        config = OmegaConf.to_container(compose(config_name=path.stem), resolve=True)
    if not isinstance(config, dict):
        raise TypeError("PDEBench analysis config must resolve to a mapping")
    return config


def read_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"invalid JSONL at line {line_number}: {error}") from error
        if not isinstance(record, dict):
            raise RuntimeError(f"record at line {line_number} is not an object")
        records.append(record)
    return records


def _all_finite(value: Any) -> bool:
    if isinstance(value, dict):
        return all(_all_finite(item) for item in value.values())
    if isinstance(value, list):
        return all(_all_finite(item) for item in value)
    if isinstance(value, float):
        return math.isfinite(value)
    return True


def validate_records(
    records: list[dict[str, Any]], config: dict[str, Any]
) -> dict[tuple[int, str], dict[str, Any]]:
    expected_seeds = {int(value) for value in config["seeds"]}
    expected_protocol = str(config["protocol_sha256"])
    expected_schema_amendment = str(config["schema_amendment_sha256"])
    expected_data_lock = str(config["dataset"]["lock_sha256"])
    if any(
        value in {"", "None"}
        for value in (expected_protocol, expected_schema_amendment, expected_data_lock)
    ):
        raise RuntimeError("analysis requires frozen protocol, amendment, and data-lock hashes")
    expected_pairs = {(seed, mechanism) for seed in expected_seeds for mechanism in MECHANISMS}
    indexed: dict[tuple[int, str], dict[str, Any]] = {}
    run_ids: set[str] = set()
    failures: list[str] = []
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
        if record.get("stage") != "external_confirmation":
            failures.append(f"wrong stage for {key}")
        if record.get("benchmark_id") != config["benchmark_id"]:
            failures.append(f"wrong benchmark for {key}")
        if record.get("protocol_sha256") != expected_protocol:
            failures.append(f"wrong protocol binding for {key}")
        if record.get("schema_amendment_sha256") != expected_schema_amendment:
            failures.append(f"wrong schema-amendment binding for {key}")
        if record.get("data_lock_sha256") != expected_data_lock:
            failures.append(f"wrong data-lock binding for {key}")
        if not _all_finite(record):
            failures.append(f"non-finite numeric field for {key}")
    missing = expected_pairs.difference(indexed)
    extra = set(indexed).difference(expected_pairs)
    if missing:
        failures.append(f"missing seed/mechanism pairs: {sorted(missing)}")
    if extra:
        failures.append(f"unexpected seed/mechanism pairs: {sorted(extra)}")
    for seed in expected_seeds:
        seed_records = [indexed[(seed, mechanism)] for mechanism in MECHANISMS]
        subset_hashes = {record["training_subset"]["index_sha256"] for record in seed_records}
        if len(subset_hashes) != 1:
            failures.append(f"unpaired training subset for seed {seed}")
        trained = [indexed[(seed, mechanism)] for mechanism in MECHANISMS - {"projection"}]
        parameter_counts = {
            int(record["compute"]["trainable_parameters"]) for record in trained
        }
        if len(parameter_counts) != 1:
            failures.append(f"unequal trained parameter counts for seed {seed}")
        free = indexed[(seed, "free")]
        projection = indexed[(seed, "projection")]
        if projection.get("derived_from") != free.get("run_id"):
            failures.append(f"projection parent mismatch for seed {seed}")
        for case in config["evaluation"]["case_names"]:
            free_value = float(free["cases"][case]["1"]["conserving_rmse"])
            projection_value = float(projection["cases"][case]["1"]["conserving_rmse"])
            if not math.isclose(free_value, projection_value, rel_tol=1e-5, abs_tol=1e-8):
                failures.append(f"projection horizon-one identity failure for seed {seed}, {case}")
    if failures:
        raise RuntimeError("; ".join(failures))
    return indexed


def _values(
    indexed: dict[tuple[int, str], dict[str, Any]],
    seeds: list[int],
    mechanism: str,
    case: str,
    horizon: int,
) -> np.ndarray:
    return np.asarray(
        [
            indexed[(seed, mechanism)]["cases"][case][str(horizon)]["conserving_rmse"]
            for seed in seeds
        ],
        dtype=np.float64,
    )


def paired_sign_flip_pvalue(values: np.ndarray, *, seed: int, draws: int = 100_000) -> float:
    differences = np.asarray(values, dtype=np.float64)
    observed = abs(float(np.mean(differences)))
    rng = np.random.default_rng(seed)
    exceedances = 0
    generated = 0
    while generated < draws:
        count = min(10_000, draws - generated)
        signs = rng.integers(0, 2, size=(count, differences.size), dtype=np.int8) * 2 - 1
        permuted = np.abs(np.mean(signs * differences[None, :], axis=1))
        exceedances += int(np.count_nonzero(permuted >= observed))
        generated += count
    return (exceedances + 1.0) / (draws + 1.0)


def analyze_comparison(
    indexed: dict[tuple[int, str], dict[str, Any]],
    seeds: list[int],
    case: str,
    horizon: int,
) -> dict[str, Any]:
    free = _values(indexed, seeds, "free", case, horizon)
    residual = _values(indexed, seeds, "free_res", case, horizon)
    hard = _values(indexed, seeds, "hard", case, horizon)
    parameterization = free - residual
    enforcement = hard - residual
    parameterization_ci = bootstrap_mean_ci(
        parameterization, confidence=0.95, draws=50_000, seed=20260901
    )
    enforcement_ci = bootstrap_mean_ci(
        enforcement, confidence=0.90, draws=50_000, seed=20260902
    )
    sesoi = 0.10 * float(np.mean(residual))
    equivalence = enforcement_ci[0] > -sesoi and enforcement_ci[1] < sesoi
    parameterization_nonzero = parameterization_ci[0] > 0.0 or parameterization_ci[1] < 0.0
    mean_parameterization = float(np.mean(parameterization))
    mean_enforcement = float(np.mean(enforcement))
    attribution = (
        equivalence
        and abs(mean_parameterization) >= 2.0 * abs(mean_enforcement)
        and parameterization_nonzero
    )
    return {
        "case": case,
        "horizon": horizon,
        "mean_free": float(np.mean(free)),
        "mean_free_res": float(np.mean(residual)),
        "mean_hard": float(np.mean(hard)),
        "parameterization_effect_free_minus_free_res": mean_parameterization,
        "parameterization_effect_ci95": list(parameterization_ci),
        "parameterization_effect_nonzero": parameterization_nonzero,
        "hard_enforcement_effect_hard_minus_free_res": mean_enforcement,
        "hard_enforcement_effect_ci90": list(enforcement_ci),
        "equivalence_sesoi": sesoi,
        "hard_free_res_equivalent": equivalence,
        "attribution_rule_passed": attribution,
        "parameterization_sign_flip_p": paired_sign_flip_pvalue(
            parameterization,
            seed=stable_seed(20260831, f"pdebench-sign:{case}:{horizon}"),
        ),
    }


def analyze_records(
    records: list[dict[str, Any]], config: dict[str, Any]
) -> dict[str, Any]:
    indexed = validate_records(records, config)
    seeds = [int(value) for value in config["seeds"]]
    comparisons = [
        analyze_comparison(indexed, seeds, str(case), int(horizon))
        for case in config["evaluation"]["case_names"]
        for horizon in config["evaluation"]["horizons"]
    ]
    adjusted = holm_adjust(
        [float(comparison["parameterization_sign_flip_p"]) for comparison in comparisons]
    )
    for comparison, adjusted_p in zip(comparisons, adjusted, strict=True):
        comparison["parameterization_sign_flip_p_holm"] = adjusted_p
    primary = next(
        comparison
        for comparison in comparisons
        if comparison["case"] == config["evaluation"]["primary_case"]
        and comparison["horizon"] == int(config["evaluation"]["primary_horizon"])
    )
    return {
        "schema_version": "constraint-iclr-pdebench-analysis-v1",
        "benchmark_id": config["benchmark_id"],
        "record_count": len(records),
        "seeds": seeds,
        "integrity_gates_passed": True,
        "primary": primary,
        "all_cases": comparisons,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/constraint_iclr/pdebench_advection_fno_v2_confirmation.yaml"),
    )
    parser.add_argument("--input", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/constraint_attribution_iclr/pdebench/analysis.json"),
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    config_path = args.config if args.config.is_absolute() else root / args.config
    config = load_config(config_path)
    input_path = args.input or Path(str(config["output"]))
    if not input_path.is_absolute():
        input_path = root / input_path
    output_path = args.output if args.output.is_absolute() else root / args.output
    result = analyze_records(read_records(input_path), config)
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
