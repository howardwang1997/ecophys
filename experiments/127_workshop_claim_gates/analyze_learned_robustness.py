"""Secondary dependence-aware robustness checks for experiment 127."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, TypeAlias, cast

import numpy as np
import numpy.typing as npt

from ecomd.eval.stylized_facts import hill_tail_index

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = EXPERIMENT_DIR / "LEARNED_RESULTS.json"
DEFAULT_OUTPUT = EXPERIMENT_DIR / "LEARNED_ROBUSTNESS.json"
DEFAULT_ARTIFACT_ROOT = REPO_ROOT / "outputs/exp127_remote_artifacts"
AMENDMENT_PATH = EXPERIMENT_DIR / "PREHELDOUT_ROBUSTNESS_AMENDMENT_2026-08-07.md"
HILL_AMENDMENT_PATH = EXPERIMENT_DIR / "PREHELDOUT_HILL_FRACTION_AMENDMENT_2026-08-07.md"
BOOTSTRAP_SEED = 127902
BOOTSTRAP_REPLICATES = 2000
HILL_K_FRACTIONS = (0.025, 0.05, 0.10)
HILL_BOOTSTRAP_SEEDS = (127903, 127904, 127905)
FIXED_LENGTH = 4000
MARKET_ORDER = ("spx", "ndx", "gold", "eurusd", "btc")
MARKET_BY_JOB = {
    "e1_spx_concave": "spx",
    "e1_spx_base": "spx",
    "e1_ndx_concave": "ndx",
    "e1_gold_concave": "gold",
    "e1_eurusd_concave": "eurusd",
    "e1_btc_concave": "btc",
    "e1_btc_base": "btc",
}

ArrayF: TypeAlias = npt.NDArray[np.float64]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_scorable_matrix(payload: Mapping[str, Any]) -> tuple[list[str], tuple[int, ...], ArrayF]:
    checkpoints = cast(list[Mapping[str, Any]], payload["checkpoints"])
    e1 = [row for row in checkpoints if str(row["job_id"]).startswith("e1_")]
    job_ids = {str(row["job_id"]) for row in e1}
    if job_ids != set(MARKET_BY_JOB):
        raise ValueError("learned result does not contain the seven frozen E1 checkpoints")

    scorable_ids: list[str] = []
    rows: list[ArrayF] = []
    common_seeds: tuple[int, ...] | None = None
    for checkpoint in e1:
        differences = np.asarray(checkpoint["paired_hill_differences"], dtype=np.float64)
        if differences.size == 0:
            continue
        if differences.ndim != 1 or not np.all(np.isfinite(differences)):
            raise ValueError(f"invalid paired differences for {checkpoint['job_id']}")
        provenance = cast(list[Mapping[str, Any]], checkpoint["heldout_provenance"])
        seeds = tuple(int(record["seed"]) for record in provenance)
        if len(seeds) != 16 or len(seeds) != differences.size or len(set(seeds)) != len(seeds):
            raise ValueError(f"held-out seed provenance mismatch for {checkpoint['job_id']}")
        if common_seeds is None:
            common_seeds = seeds
        elif seeds != common_seeds:
            raise ValueError("scorable checkpoints do not share an identical held-out seed order")
        scorable_ids.append(str(checkpoint["job_id"]))
        rows.append(differences)

    if not rows or common_seeds is None:
        return [], (), np.empty((0, 0), dtype=np.float64)
    return scorable_ids, common_seeds, np.stack(rows)


def crossed_bootstrap(matrix: ArrayF, *, seed: int, replicates: int) -> dict[str, Any]:
    values = np.asarray(matrix, dtype=np.float64)
    if values.ndim != 2 or min(values.shape) < 1 or not np.all(np.isfinite(values)):
        raise ValueError("matrix must be a finite nonempty checkpoint-by-seed array")
    if replicates < 1:
        raise ValueError("replicates must be positive")
    point = float(np.mean(np.median(values, axis=1)))
    rng = np.random.default_rng(seed)
    draws: ArrayF = np.empty(replicates, dtype=np.float64)
    for replicate in range(replicates):
        checkpoint_indices = rng.integers(0, values.shape[0], size=values.shape[0])
        common_seed_indices = rng.integers(0, values.shape[1], size=values.shape[1])
        sampled = values[checkpoint_indices][:, common_seed_indices]
        draws[replicate] = float(np.mean(np.median(sampled, axis=1)))
    interval = np.quantile(draws, (0.025, 0.975))
    return {
        "estimand": "equal-weight mean of checkpoint median paired Hill differences",
        "effect": point,
        "ci_95": [float(interval[0]), float(interval[1])],
        "positive_direction_passes": bool(interval[0] > 0.0),
        "bootstrap_seed": seed,
        "bootstrap_replicates": replicates,
        "dependence_rule": "one common held-out seed resample is applied to all selected checkpoints",
    }


def market_leave_one_out(job_ids: Sequence[str], matrix: ArrayF) -> dict[str, Any]:
    values = np.asarray(matrix, dtype=np.float64)
    if values.ndim != 2 or values.shape[0] != len(job_ids):
        raise ValueError("job_ids and checkpoint matrix do not align")
    checkpoint_effects = np.median(values, axis=1)
    by_market: dict[str, list[float]] = {market: [] for market in MARKET_ORDER}
    for job_id, effect in zip(job_ids, checkpoint_effects, strict=True):
        if job_id not in MARKET_BY_JOB:
            raise ValueError(f"unknown E1 checkpoint {job_id}")
        by_market[MARKET_BY_JOB[job_id]].append(float(effect))
    market_effects = {
        market: float(np.mean(by_market[market]))
        for market in MARKET_ORDER
        if by_market[market]
    }
    if not market_effects:
        raise ValueError("no represented markets")
    balanced = float(np.mean(list(market_effects.values())))
    leave_one_out: dict[str, float] = {}
    if len(market_effects) > 1:
        for omitted in market_effects:
            retained = [value for market, value in market_effects.items() if market != omitted]
            leave_one_out[omitted] = float(np.mean(retained))
    loo_values = list(leave_one_out.values())
    return {
        "estimand": "equal-weight mean of represented market effects",
        "market_effects": market_effects,
        "effect": balanced,
        "leave_one_market_out": leave_one_out,
        "leave_one_out_range": (
            [float(min(loo_values)), float(max(loo_values))] if loo_values else None
        ),
        "all_leave_one_out_positive": bool(loo_values) and all(value > 0.0 for value in loo_values),
    }


def _fraction_key(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def compute_hill_fraction_matrices(
    payload: Mapping[str, Any],
    artifact_root: Path,
) -> tuple[list[str], dict[str, ArrayF]]:
    scorable_ids, common_seeds, primary_matrix = extract_scorable_matrix(payload)
    if not scorable_ids:
        return [], {}
    checkpoints = {
        str(row["job_id"]): row
        for row in cast(list[Mapping[str, Any]], payload["checkpoints"])
        if str(row["job_id"]) in scorable_ids
    }
    matrices: dict[str, ArrayF] = {
        _fraction_key(fraction): np.empty(
            (len(scorable_ids), len(common_seeds)), dtype=np.float64
        )
        for fraction in HILL_K_FRACTIONS
    }
    for checkpoint_index, job_id in enumerate(scorable_ids):
        checkpoint = checkpoints[job_id]
        w_star = checkpoint["calibration_w_star"]
        if w_star is None:
            raise ValueError(f"scorable checkpoint {job_id} lacks calibration_w_star")
        start = int(w_star)
        provenance = cast(list[Mapping[str, Any]], checkpoint["heldout_provenance"])
        for seed_index, record in enumerate(provenance):
            seed = int(record["seed"])
            node = str(record["node"])
            path = (
                artifact_root
                / "rollouts/heldout"
                / job_id
                / node
                / f"trajectory_seed{seed}.npz"
            )
            with np.load(path, allow_pickle=False) as stored:
                recorded_seed = int(stored["seed"])
                returns = np.asarray(stored["log_returns"], dtype=np.float64)
            if recorded_seed != seed or returns.shape != (8000,) or not np.all(np.isfinite(returns)):
                raise ValueError(f"invalid held-out trajectory {path}")
            for fraction in HILL_K_FRACTIONS:
                early = hill_tail_index(
                    returns[:FIXED_LENGTH], k_frac=fraction, n_bootstrap=0
                ).estimate
                post = hill_tail_index(
                    returns[start:start + FIXED_LENGTH],
                    k_frac=fraction,
                    n_bootstrap=0,
                ).estimate
                matrices[_fraction_key(fraction)][checkpoint_index, seed_index] = post - early
    primary_key = _fraction_key(0.05)
    if not np.allclose(matrices[primary_key], primary_matrix, rtol=0.0, atol=1e-12):
        raise ValueError("recomputed 5% Hill differences disagree with frozen learned results")
    return scorable_ids, matrices


def summarize_hill_fraction_sensitivity(
    job_ids: Sequence[str],
    matrices: Mapping[str, ArrayF],
) -> dict[str, Any]:
    expected_keys = {_fraction_key(value) for value in HILL_K_FRACTIONS}
    if set(matrices) != expected_keys:
        raise ValueError("Hill-fraction matrix grid is incomplete")
    by_fraction: dict[str, Any] = {}
    for fraction, seed in zip(HILL_K_FRACTIONS, HILL_BOOTSTRAP_SEEDS, strict=True):
        key = _fraction_key(fraction)
        by_fraction[key] = {
            "crossed_checkpoint_seed_bootstrap": crossed_bootstrap(
                matrices[key], seed=seed, replicates=BOOTSTRAP_REPLICATES
            ),
            "market_balanced_sensitivity": market_leave_one_out(job_ids, matrices[key]),
        }
    point_positive = sum(
        float(row["crossed_checkpoint_seed_bootstrap"]["effect"]) > 0.0
        for row in by_fraction.values()
    )
    interval_positive = sum(
        bool(row["crossed_checkpoint_seed_bootstrap"]["positive_direction_passes"])
        for row in by_fraction.values()
    )
    return {
        "primary_fraction": 0.05,
        "fractions": list(HILL_K_FRACTIONS),
        "by_fraction": by_fraction,
        "positive_point_effect_count": point_positive,
        "positive_common_seed_interval_count": interval_positive,
        "all_point_effects_positive": point_positive == len(HILL_K_FRACTIONS),
        "all_common_seed_intervals_positive": interval_positive == len(HILL_K_FRACTIONS),
    }


def analyze(
    payload: Mapping[str, Any],
    source_sha256: str,
    hill_fraction_sensitivity: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    job_ids, heldout_seeds, matrix = extract_scorable_matrix(payload)
    primary = cast(Mapping[str, Any], payload["primary"])
    if int(primary["e1_scorable"]) != len(job_ids):
        raise ValueError("primary scorable count disagrees with checkpoint rows")
    if not job_ids:
        return {
            "schema_version": 1,
            "source_result_sha256": source_sha256,
            "amendment_sha256": sha256_file(AMENDMENT_PATH),
            "hill_fraction_amendment_sha256": sha256_file(HILL_AMENDMENT_PATH),
            "scorable_job_ids": [],
            "common_heldout_seeds": [],
            "crossed_checkpoint_seed_bootstrap": None,
            "market_balanced_sensitivity": None,
            "hill_fraction_sensitivity": hill_fraction_sensitivity,
        }
    crossed = crossed_bootstrap(
        matrix,
        seed=BOOTSTRAP_SEED,
        replicates=BOOTSTRAP_REPLICATES,
    )
    primary_effect = primary["effect"]
    if primary_effect is None or not np.isclose(float(primary_effect), float(crossed["effect"])):
        raise ValueError("secondary point estimate disagrees with the frozen primary estimand")
    return {
        "schema_version": 1,
        "source_result_sha256": source_sha256,
        "amendment_sha256": sha256_file(AMENDMENT_PATH),
        "hill_fraction_amendment_sha256": sha256_file(HILL_AMENDMENT_PATH),
        "scorable_job_ids": job_ids,
        "common_heldout_seeds": list(heldout_seeds),
        "crossed_checkpoint_seed_bootstrap": crossed,
        "market_balanced_sensitivity": market_leave_one_out(job_ids, matrix),
        "hill_fraction_sensitivity": hill_fraction_sensitivity,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    payload = cast(dict[str, Any], json.loads(args.input.read_text()))
    job_ids, matrices = compute_hill_fraction_matrices(payload, args.artifact_root)
    hill_sensitivity = (
        summarize_hill_fraction_sensitivity(job_ids, matrices) if job_ids else None
    )
    result = analyze(payload, sha256_file(args.input), hill_sensitivity)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2) + "\n")
    temporary.replace(args.output)
    print(json.dumps({"output": str(args.output), "sha256": sha256_file(args.output)}, indent=2))


if __name__ == "__main__":
    main()
