"""Join the frozen gradient-coupling audit to a completed factorial result."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from analyze_constraint_iclr_pdebench import load_config, read_records
from analyze_constraint_iclr_pdebench_factorial import validate_factorial_records
from constraint_iclr_common import bootstrap_mean_ci, sha256_file, stable_seed

COORDINATES = ("absolute", "residual")


def _all_finite(value: Any) -> bool:
    if isinstance(value, dict):
        return all(_all_finite(item) for item in value.values())
    if isinstance(value, list):
        return all(_all_finite(item) for item in value)
    if isinstance(value, float):
        return math.isfinite(value)
    return True


def validate_diagnostic_records(
    records: list[dict[str, Any]], config: dict[str, Any]
) -> dict[tuple[int, str], dict[str, Any]]:
    seeds = [int(value) for value in config["seeds"]]
    expected = {(seed, coordinate) for seed in seeds for coordinate in COORDINATES}
    expected_lock = str(config["dataset"]["lock_sha256"])
    expected_factorial_protocol = str(config["protocol_sha256"])
    expected_gradient_protocol = str(config["gradient_protocol_sha256"])
    expected_benchmark = str(config["benchmark_id"])
    expected_head = str(config["expected_git_head"])
    expected_dirty = bool(config["expected_git_dirty"])
    protocol_path = str(config["gradient_protocol_path"])
    decision_path = str(config["gradient_decision_path"])
    lock_path = str(config["dataset"]["lock_path"])

    indexed: dict[tuple[int, str], dict[str, Any]] = {}
    run_ids: set[str] = set()
    source_manifests: set[str] = set()
    failures: list[str] = []
    for record in records:
        key = (int(record.get("seed", -1)), str(record.get("coordinate")))
        run_id = str(record.get("run_id"))
        if key in indexed:
            failures.append(f"duplicate seed/coordinate {key}")
        if run_id in run_ids:
            failures.append(f"duplicate run_id {run_id}")
        indexed[key] = record
        run_ids.add(run_id)
        if record.get("schema_version") != "constraint-iclr-gradient-coupling-v1":
            failures.append(f"wrong schema for {key}")
        if record.get("benchmark_id") != expected_benchmark:
            failures.append(f"wrong benchmark for {key}")
        if record.get("data_lock_sha256") != expected_lock:
            failures.append(f"wrong data lock for {key}")
        if record.get("factorial_protocol_sha256") != expected_factorial_protocol:
            failures.append(f"wrong factorial protocol for {key}")
        if record.get("gradient_protocol_sha256") != expected_gradient_protocol:
            failures.append(f"wrong gradient protocol for {key}")
        if not _all_finite(record):
            failures.append(f"non-finite diagnostic for {key}")
        losses = record.get("losses_before", {})
        discrepancy = abs(
            float(losses.get("total", math.nan))
            - float(losses.get("conserving", math.nan))
            - float(losses.get("violating", math.nan))
        )
        tolerance = 1e-9 + 1e-6 * abs(float(losses.get("total", math.nan)))
        if not math.isfinite(discrepancy) or discrepancy > tolerance:
            failures.append(f"loss decomposition mismatch for {key}")
        gradients = record.get("gradients", {})
        cosine = float(gradients.get("cosine", math.nan))
        if not math.isfinite(cosine) or abs(cosine) > 1.000001:
            failures.append(f"invalid gradient cosine for {key}")
        if float(gradients.get("q_norm", 0.0)) <= 0.0 or float(
            gradients.get("p_norm", 0.0)
        ) <= 0.0:
            failures.append(f"zero gradient norm for {key}")
        one_step = record.get("one_step", {})
        expected_credit = float(
            one_step.get("free_conserving_loss_after", math.nan)
        ) - float(one_step.get("hard_conserving_loss_after", math.nan))
        if not math.isclose(
            float(one_step.get("one_step_enforcement_credit", math.nan)),
            expected_credit,
            rel_tol=1e-12,
            abs_tol=1e-15,
        ):
            failures.append(f"one-step credit identity mismatch for {key}")
        provenance = record.get("provenance", {})
        if provenance.get("git_head") != expected_head:
            failures.append(f"wrong Git head for {key}")
        if bool(provenance.get("git_dirty")) is not expected_dirty:
            failures.append(f"wrong dirty flag for {key}")
        sources = provenance.get("source_sha256", {})
        if not isinstance(sources, dict):
            failures.append(f"missing source manifest for {key}")
        else:
            source_manifests.add(json.dumps(sources, sort_keys=True))
            for required in (protocol_path, decision_path, lock_path):
                if required not in sources:
                    failures.append(f"source manifest for {key} omits {required}")

    missing = expected.difference(indexed)
    extra = set(indexed).difference(expected)
    if missing:
        failures.append(f"missing seed/coordinate pairs: {sorted(missing)}")
    if extra:
        failures.append(f"unexpected seed/coordinate pairs: {sorted(extra)}")
    if len(source_manifests) != 1:
        failures.append("diagnostic records do not share one exact source SHA-256 manifest")
    if not missing:
        for seed in seeds:
            absolute = indexed[(seed, "absolute")]
            residual = indexed[(seed, "residual")]
            if absolute.get("initialization_sha256") != residual.get(
                "initialization_sha256"
            ):
                failures.append(f"unpaired initialization for seed {seed}")
            if absolute.get("batch") != residual.get("batch"):
                failures.append(f"unpaired first minibatch for seed {seed}")
    if failures:
        raise RuntimeError("; ".join(failures))
    return indexed


def validate_factorial_join_pairing(
    diagnostic: dict[tuple[int, str], dict[str, Any]],
    factorial: dict[tuple[int, str], dict[str, Any]],
    seeds: list[int],
) -> None:
    failures: list[str] = []
    for seed in seeds:
        factorial_reference = factorial[(seed, "free")]
        expected_initialization = str(factorial_reference.get("initialization_sha256"))
        expected_training_index = str(factorial_reference.get("training_index_sha256"))
        for coordinate in COORDINATES:
            record = diagnostic[(seed, coordinate)]
            if str(record.get("initialization_sha256")) != expected_initialization:
                failures.append(
                    f"diagnostic/factorial initialization mismatch for seed {seed}, {coordinate}"
                )
            batch = record.get("batch", {})
            observed_training_index = (
                str(batch.get("training_index_sha256"))
                if isinstance(batch, dict)
                else "None"
            )
            if observed_training_index != expected_training_index:
                failures.append(
                    f"diagnostic/factorial training-index mismatch for seed {seed}, {coordinate}"
                )
    if failures:
        raise RuntimeError("; ".join(failures))


def _rankdata(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(values.size, dtype=np.float64)
    start = 0
    while start < values.size:
        stop = start + 1
        while stop < values.size and values[order[stop]] == values[order[start]]:
            stop += 1
        ranks[order[start:stop]] = 0.5 * (start + stop - 1) + 1.0
        start = stop
    return ranks


def _correlation(x: np.ndarray, y: np.ndarray) -> float | None:
    centered_x = x - np.mean(x)
    centered_y = y - np.mean(y)
    denominator = math.sqrt(
        float(np.sum(np.square(centered_x)) * np.sum(np.square(centered_y)))
    )
    if denominator == 0.0:
        return None
    return float(np.sum(centered_x * centered_y) / denominator)


def _spearman_correlation(x: np.ndarray, y: np.ndarray) -> float | None:
    return _correlation(_rankdata(x), _rankdata(y))


def spearman_bootstrap(
    x: np.ndarray, y: np.ndarray, *, draws: int, seed: int
) -> dict[str, Any]:
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if x.ndim != 1 or y.ndim != 1 or x.size != y.size or x.size < 2:
        raise ValueError("Spearman bootstrap requires paired one-dimensional samples")
    estimate = _spearman_correlation(x, y)
    if estimate is None:
        return {
            "estimable": False,
            "rho": None,
            "ci95": None,
            "valid_bootstrap_draws": 0,
            "classification": "unresolved_constant_rank",
        }
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, x.size, size=(draws, x.size))
    correlations = np.asarray(
        [
            correlation
            for row in indices
            if (correlation := _spearman_correlation(x[row], y[row])) is not None
        ],
        dtype=np.float64,
    )
    if correlations.size < int(0.99 * draws):
        return {
            "estimable": False,
            "rho": estimate,
            "ci95": None,
            "valid_bootstrap_draws": int(correlations.size),
            "classification": "unresolved_bootstrap_degeneracy",
        }
    interval = [float(value) for value in np.quantile(correlations, [0.025, 0.975])]
    return {
        "estimable": True,
        "rho": estimate,
        "ci95": interval,
        "valid_bootstrap_draws": int(correlations.size),
        "classification": (
            "positive_mechanism_support" if interval[0] > 0.0 else "not_supported"
        ),
    }


def _mean_summary(values: np.ndarray, *, name: str, draws: int) -> dict[str, Any]:
    interval = bootstrap_mean_ci(
        values,
        confidence=0.95,
        draws=draws,
        seed=stable_seed(20260901, f"gradient-coupling:{name}"),
    )
    return {"mean": float(np.mean(values)), "ci95": list(interval)}


def analyze_gradient_coupling(
    diagnostic_records: list[dict[str, Any]],
    factorial_records: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    diagnostic = validate_diagnostic_records(diagnostic_records, config)
    factorial = validate_factorial_records(factorial_records, config)
    seeds = [int(value) for value in config["seeds"]]
    validate_factorial_join_pairing(diagnostic, factorial, seeds)
    case = str(config["evaluation"]["primary_case"])
    horizon = str(int(config["evaluation"]["primary_horizon"]))
    draws = 50_000

    d_absolute = np.asarray(
        [
            diagnostic[(seed, "absolute")]["one_step"][
                "one_step_enforcement_credit"
            ]
            for seed in seeds
        ],
        dtype=np.float64,
    )
    d_residual = np.asarray(
        [
            diagnostic[(seed, "residual")]["one_step"][
                "one_step_enforcement_credit"
            ]
            for seed in seeds
        ],
        dtype=np.float64,
    )
    d_interaction = d_absolute - d_residual

    def metric(seed: int, mechanism: str) -> float:
        return float(
            factorial[(seed, mechanism)]["cases"][case][horizon]["conserving_rmse"]
        )

    final_interaction = np.asarray(
        [
            (metric(seed, "free") - metric(seed, "hard_abs"))
            - (metric(seed, "free_res") - metric(seed, "hard"))
            for seed in seeds
        ],
        dtype=np.float64,
    )
    cos_absolute = np.asarray(
        [diagnostic[(seed, "absolute")]["gradients"]["cosine"] for seed in seeds],
        dtype=np.float64,
    )
    cos_residual = np.asarray(
        [diagnostic[(seed, "residual")]["gradients"]["cosine"] for seed in seeds],
        dtype=np.float64,
    )
    result = {
        "schema_version": "constraint-iclr-gradient-coupling-analysis-v1",
        "benchmark_id": config["benchmark_id"],
        "record_count": len(diagnostic_records),
        "factorial_record_count": len(factorial_records),
        "seeds": seeds,
        "primary_case": case,
        "primary_horizon": int(horizon),
        "integrity_gates_passed": True,
        "one_step": {
            "absolute": _mean_summary(d_absolute, name="D_A", draws=draws),
            "residual": _mean_summary(d_residual, name="D_R", draws=draws),
            "interaction": _mean_summary(d_interaction, name="D_I", draws=draws),
        },
        "gradient_cosine": {
            "absolute": _mean_summary(cos_absolute, name="cos_A", draws=draws),
            "residual": _mean_summary(cos_residual, name="cos_R", draws=draws),
        },
        "final_interaction": _mean_summary(
            final_interaction, name="I_final", draws=draws
        ),
        "primary_mechanistic_association": spearman_bootstrap(
            d_interaction,
            final_interaction,
            draws=draws,
            seed=stable_seed(20260901, "gradient-coupling:spearman"),
        ),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(
            "configs/constraint_iclr/"
            "pdebench_advection_fno_gradient_coupling_20260901.yaml"
        ),
    )
    parser.add_argument("--diagnostic-input", type=Path)
    parser.add_argument("--factorial-input", type=Path)
    parser.add_argument("--factorial-analysis", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    config_path = args.config if args.config.is_absolute() else root / args.config
    config = load_config(config_path)
    diagnostic_path = args.diagnostic_input or Path(str(config["gradient_output"]))
    factorial_path = args.factorial_input or Path(str(config["output"]))
    if not diagnostic_path.is_absolute():
        diagnostic_path = root / diagnostic_path
    if not factorial_path.is_absolute():
        factorial_path = root / factorial_path
    factorial_analysis_path = (
        args.factorial_analysis
        if args.factorial_analysis.is_absolute()
        else root / args.factorial_analysis
    )
    output_path = args.output if args.output.is_absolute() else root / args.output
    completed_factorial_analysis = json.loads(
        factorial_analysis_path.read_text(encoding="utf-8")
    )
    if completed_factorial_analysis.get("input_sha256") != sha256_file(factorial_path):
        raise RuntimeError("factorial analysis is not bound to the supplied complete JSONL")
    result = analyze_gradient_coupling(
        read_records(diagnostic_path), read_records(factorial_path), config
    )
    result.update(
        {
            "diagnostic_input_sha256": sha256_file(diagnostic_path),
            "factorial_input_sha256": sha256_file(factorial_path),
            "factorial_analysis_sha256": sha256_file(factorial_analysis_path),
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
