"""Run the source-bound synthetic T0 checks for coupled allocation and local IRMs."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from ecomd.data.aave_qualification import canonical_sha256
from ecomd.physics.resource_pressure import (
    advance_log_rate_at_target,
    apply_allocation_flows,
    control_pressure,
    equalized_supply,
    pressure_continuity_residual,
    utilization,
    utilization_minimax_lower_bound,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SECONDS_PER_YEAR = 365.0 * 24.0 * 60.0 * 60.0


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"YAML config must be an object: {path}")
    return payload


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_source(root: Path, expected: Mapping[str, Any]) -> dict[str, Any]:
    observed_sha = _git(root, "rev-parse", "HEAD")
    if observed_sha != str(expected["commit"]):
        raise RuntimeError(f"source SHA mismatch: {observed_sha} != {expected['commit']}")
    if _git(root, "status", "--porcelain"):
        raise RuntimeError(f"source worktree is dirty: {root}")
    raw_files = expected.get("files")
    if not isinstance(raw_files, Mapping) or not raw_files:
        raise RuntimeError("source file manifest is missing")
    observed_files: dict[str, str] = {}
    for relative, expected_digest in raw_files.items():
        path = root / str(relative)
        if not path.is_file():
            raise RuntimeError(f"pinned source file is missing: {path}")
        digest = _sha256_file(path)
        if digest != str(expected_digest):
            raise RuntimeError(f"source file digest mismatch for {relative}: {digest}")
        observed_files[str(relative)] = digest
    return {
        "repository": str(expected["repository"]),
        "git_sha": observed_sha,
        "file_sha256": dict(sorted(observed_files.items())),
    }


def _validate_contract(config: Mapping[str, Any]) -> None:
    if config.get("experiment_id") != "morpho_controller_coupling_t0_v1":
        raise RuntimeError("unexpected experiment_id")
    if config.get("allowed_data") != ["synthetic_arrays", "pinned_source_constants"]:
        raise RuntimeError("T0 allowed_data changed")
    forbidden = set(config.get("forbidden_data", []))
    required_forbidden = {
        "historical_reallocation_events",
        "asset_amounts",
        "rates",
        "utilization_history",
        "prices",
        "liquidations",
        "market_outcomes",
    }
    if forbidden != required_forbidden:
        raise RuntimeError("T0 forbidden_data changed")
    resources = config.get("resources")
    if not isinstance(resources, Mapping) or resources.get("gpu_forbidden") is not True:
        raise RuntimeError("T0 must explicitly forbid GPU use")
    source = config.get("source")
    if not isinstance(source, Mapping):
        raise RuntimeError("T0 source contract is missing")
    if float(config["target_utilization"]) != float(source["target_utilization_constant"]):
        raise RuntimeError("configured target utilization differs from pinned source")
    if float(config["adjustment_speed_per_year"]) != float(source["adjustment_speed_constant_per_year"]):
        raise RuntimeError("configured adjustment speed differs from pinned source")


def _random_valid_flows(
    rng: np.random.Generator,
    borrowed: np.ndarray,
    supplied: np.ndarray,
    max_fraction: float,
) -> np.ndarray:
    n_markets = supplied.size
    weights = rng.random((n_markets, n_markets))
    np.fill_diagonal(weights, 0.0)
    row_sums = weights.sum(axis=1)
    available = np.maximum(supplied - borrowed, 0.0)
    requested = rng.uniform(0.0, max_fraction, size=n_markets) * supplied
    outflows = np.minimum(requested, 0.5 * available)
    return weights * np.divide(outflows, row_sums, out=np.zeros_like(outflows), where=row_sums > 0.0)[:, None]


def _run_checks(config: Mapping[str, Any]) -> dict[str, Any]:
    rng = np.random.default_rng(int(config["seed"]))
    trials = int(config["trials"])
    n_min = int(config["n_markets_min"])
    n_max = int(config["n_markets_max"])
    target = float(config["target_utilization"])
    max_flow_fraction = float(config["flow_fraction_max"])
    min_utilization = float(config["min_utilization"])
    max_utilization = float(config["max_utilization"])
    min_gap = float(config["min_aggregate_utilization_gap"])
    adjustment_speed = float(config["adjustment_speed_per_year"]) / SECONDS_PER_YEAR
    elapsed = float(config["elapsed_seconds"])

    max_continuity = 0.0
    max_global_conservation = 0.0
    max_minimax_violation = 0.0
    max_minimax_attainment_residual = 0.0
    max_equalization_spread = 0.0
    max_differential_memory_residual = 0.0
    common_mode_trials = 0
    min_nonzero_common_mode_shift = float("inf")

    for _ in range(trials):
        n_markets = int(rng.integers(n_min, n_max + 1))
        supplied = np.exp(rng.uniform(np.log(10.0), np.log(10_000.0), size=n_markets))
        utilizations = rng.uniform(min_utilization, max_utilization, size=n_markets)
        borrowed = supplied * utilizations
        flows = _random_valid_flows(rng, borrowed, supplied, max_flow_fraction)
        updated_supply = apply_allocation_flows(supplied, flows)
        scale = max(1.0, float(borrowed.sum()), float(supplied.sum()))

        continuity = pressure_continuity_residual(borrowed, supplied, flows, target)
        max_continuity = max(max_continuity, float(np.max(np.abs(continuity))) / scale)
        pressure_before = control_pressure(borrowed, supplied, target)
        pressure_after = control_pressure(borrowed, updated_supply, target)
        max_global_conservation = max(
            max_global_conservation,
            abs(float(pressure_after.sum() - pressure_before.sum())) / scale,
        )

        lower_bound = utilization_minimax_lower_bound(borrowed, supplied, target)
        observed_max_error = float(np.max(np.abs(utilizations - target)))
        max_minimax_violation = max(max_minimax_violation, max(0.0, lower_bound - observed_max_error))

        equal_supply = equalized_supply(borrowed, float(supplied.sum()))
        equal_utilizations = utilization(borrowed, equal_supply)
        max_equalization_spread = max(
            max_equalization_spread,
            float(equal_utilizations.max() - equal_utilizations.min()),
        )
        equal_max_error = float(np.max(np.abs(equal_utilizations - target)))
        max_minimax_attainment_residual = max(
            max_minimax_attainment_residual,
            abs(equal_max_error - lower_bound),
        )

        log_rates = rng.uniform(np.log(0.001), np.log(2.0), size=n_markets)
        advanced = advance_log_rate_at_target(
            log_rates,
            equal_utilizations,
            target_utilization=target,
            adjustment_speed_per_second=adjustment_speed,
            elapsed_seconds=elapsed,
        )
        before_centered = log_rates - log_rates.mean()
        after_centered = advanced - advanced.mean()
        max_differential_memory_residual = max(
            max_differential_memory_residual,
            float(np.max(np.abs(after_centered - before_centered))),
        )
        aggregate_utilization = float(borrowed.sum() / supplied.sum())
        if abs(aggregate_utilization - target) >= min_gap:
            common_mode_trials += 1
            common_shift = abs(float(np.mean(advanced - log_rates)))
            min_nonzero_common_mode_shift = min(min_nonzero_common_mode_shift, common_shift)

    return {
        "trials": trials,
        "market_count_range": [n_min, n_max],
        "max_pressure_continuity_residual": max_continuity,
        "max_global_conservation_residual": max_global_conservation,
        "max_minimax_bound_violation": max_minimax_violation,
        "max_minimax_attainment_residual": max_minimax_attainment_residual,
        "max_equalization_spread": max_equalization_spread,
        "max_differential_rate_memory_residual": max_differential_memory_residual,
        "nonzero_common_mode_trials": common_mode_trials,
        "min_nonzero_common_mode_log_rate_shift": (
            min_nonzero_common_mode_shift if common_mode_trials else None
        ),
    }


def _gate(config: Mapping[str, Any], metrics: Mapping[str, Any]) -> dict[str, bool]:
    gates = config["gates"]
    return {
        "pressure_continuity": float(metrics["max_pressure_continuity_residual"])
        <= float(gates["pressure_continuity_max_residual"]),
        "global_conservation": float(metrics["max_global_conservation_residual"])
        <= float(gates["global_conservation_max_residual"]),
        "minimax_bound": float(metrics["max_minimax_bound_violation"])
        <= float(gates["minimax_bound_max_violation"]),
        "minimax_attainment": float(metrics["max_minimax_attainment_residual"])
        <= float(gates["minimax_bound_max_violation"]),
        "equalization": float(metrics["max_equalization_spread"]) <= float(gates["equalization_spread_max"]),
        "differential_rate_memory": float(metrics["max_differential_rate_memory_residual"])
        <= float(gates["differential_rate_memory_max_residual"]),
        "nonzero_common_mode": (
            int(metrics["nonzero_common_mode_trials"]) > 0
            and float(metrics["min_nonzero_common_mode_log_rate_shift"]) > 0.0
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "configs/empirical_physics/morpho_controller_coupling_t0_v1.yaml",
    )
    parser.add_argument("--bot-root", type=Path, required=True)
    parser.add_argument("--irm-root", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "results/empirical_physics/morpho_controller_coupling_t0_v1.json",
    )
    args = parser.parse_args()

    config_path = args.config.resolve()
    config = _load_yaml(config_path)
    _validate_contract(config)
    if _git(REPO_ROOT, "status", "--porcelain"):
        raise RuntimeError("formal T0 requires a clean repository worktree")
    repository_sha = _git(REPO_ROOT, "rev-parse", "HEAD")

    source = config["source"]
    source_audit = {
        "bot": _verify_source(args.bot_root.resolve(), source["bot"]),
        "irm": _verify_source(args.irm_root.resolve(), source["irm"]),
    }
    metrics = _run_checks(config)
    gate_results = _gate(config, metrics)
    math_checks_pass = all(gate_results.values())
    result: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": str(config["experiment_id"]),
        "created_utc": datetime.now(UTC).isoformat(),
        "repository": {
            "git_sha": repository_sha,
            "worktree_clean": True,
        },
        "config": {
            "path": str(config_path.relative_to(REPO_ROOT)),
            "sha256": _sha256_file(config_path),
            "seed": int(config["seed"]),
        },
        "source_audit": source_audit,
        "data_contract": {
            "used": list(config["allowed_data"]),
            "forbidden_untouched": list(config["forbidden_data"]),
            "gpu_used": False,
        },
        "metrics": metrics,
        "gates": gate_results,
        "math_checks_pass": math_checks_pass,
        "scientific_decision": (
            "math_encoding_pass_novelty_and_field_support_remain_amber"
            if math_checks_pass
            else "stop_math_encoding_failed"
        ),
        "claim_limit": (
            "Passing verifies source-bound algebra only; it does not establish novelty, field prevalence, "
            "causality, NMI fit, or NCS fit."
        ),
    }
    result["canonical_payload_sha256"] = canonical_sha256(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not math_checks_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
