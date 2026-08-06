"""Generate and analyze the pre-registered experiment-127 analytic controls."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, TypeAlias, cast

import numpy as np
import numpy.typing as npt

from ecomd.baselines.ar1_sv import AR1SV
from ecomd.baselines.garch import GARCH11
from ecomd.eval.stationarity_baselines import ADFKPSSConfig, fit_adf_kpss_gate
from ecomd.eval.stationarity_gate import GateConfig, evaluate_stationarity_gate, fit_stationarity_gate
from ecomd.eval.stylized_facts import hill_tail_index

ArrayF: TypeAlias = npt.NDArray[np.float64]

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = Path(__file__).resolve().parent
PARAMS_PATH = EXPERIMENT_DIR / "ANALYTIC_PARAMS.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "exp127_analytic_controls"
DEFAULT_RESULTS_PATH = EXPERIMENT_DIR / "ANALYTIC_RESULTS.json"
METHODS = ("no_discard", "fixed_500", "fixed_1000", "adf_kpss", "energy")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repository_state() -> dict[str, Any]:
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    return {"git_sha": sha, "clean": not status, "status_entries": status}


def load_frozen_parameters() -> dict[str, Any]:
    payload = cast(dict[str, Any], json.loads(PARAMS_PATH.read_text()))
    for model_name in ("garch_t", "ar1_sv"):
        record = payload[model_name]
        source = REPO_ROOT / record["source"]
        actual = sha256_file(source)
        if actual != record["source_sha256"]:
            raise RuntimeError(
                f"frozen source hash mismatch for {model_name}: {actual} != {record['source_sha256']}"
            )
    return payload


def generate_controls(
    output_dir: Path,
    allow_dirty: bool = False,
    smoke: bool = False,
) -> dict[str, Any]:
    frozen = load_frozen_parameters()
    state = repository_state()
    if not state["clean"] and not allow_dirty:
        raise RuntimeError("formal analytic generation requires a clean git worktree")

    n_trajectories = 4 if smoke else int(frozen["trajectories_per_condition"])
    trajectory_length = 80 if smoke else int(frozen["trajectory_length"])
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    started = time.time()
    for model_name in ("garch_t", "ar1_sv"):
        model_record = frozen[model_name]
        for condition_name, condition in model_record["conditions"].items():
            artifact_name = f"{model_name}__{condition_name}.npy"
            artifact_path = output_dir / artifact_name
            matrix: ArrayF = np.empty((n_trajectories, trajectory_length), dtype=np.float64)
            condition_started = time.time()
            for row_index in range(n_trajectories):
                seed = int(condition["seed_start"]) + row_index
                matrix[row_index] = _simulate(
                    model_name=model_name,
                    params=model_record["params"],
                    n_steps=trajectory_length,
                    seed=seed,
                    burn_in=int(condition["burn_in"]),
                    initial_variance_multiplier=float(condition["initial_variance_multiplier"]),
                )
            np.save(artifact_path, matrix, allow_pickle=False)
            records.append({
                "model": model_name,
                "condition": condition_name,
                "artifact": artifact_name,
                "artifact_sha256": sha256_file(artifact_path),
                "shape": list(matrix.shape),
                "dtype": str(matrix.dtype),
                "seed_start": int(condition["seed_start"]),
                "seed_stop_exclusive": int(condition["seed_start"]) + n_trajectories,
                "burn_in": int(condition["burn_in"]),
                "initial_variance_multiplier": float(condition["initial_variance_multiplier"]),
                "elapsed_seconds": time.time() - condition_started,
            })

    manifest = {
        "schema_version": 1,
        "formal": not smoke,
        "repository": state,
        "parameters_sha256": sha256_file(PARAMS_PATH),
        "n_trajectories": n_trajectories,
        "trajectory_length": trajectory_length,
        "elapsed_seconds": time.time() - started,
        "artifacts": records,
    }
    manifest_path = output_dir / "generation_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def analyze_controls(output_dir: Path, results_path: Path, allow_dirty: bool = False) -> dict[str, Any]:
    frozen = load_frozen_parameters()
    state = repository_state()
    if not state["clean"] and not allow_dirty:
        raise RuntimeError("formal analytic analysis requires a clean git worktree")
    generation_path = output_dir / "generation_manifest.json"
    generation = json.loads(generation_path.read_text())
    if not generation.get("formal", False):
        raise RuntimeError("refusing to analyze a smoke generation as formal data")
    if generation["n_trajectories"] != frozen["trajectories_per_condition"]:
        raise RuntimeError("trajectory count differs from frozen parameters")
    if generation["trajectory_length"] != frozen["trajectory_length"]:
        raise RuntimeError("trajectory length differs from frozen parameters")
    _verify_generation_artifacts(output_dir, generation)

    gate_base_seed = 127900
    rows: list[dict[str, Any]] = []
    condition_order: list[tuple[str, str]] = []
    condition_index = 0
    started = time.time()
    for model_name in ("garch_t", "ar1_sv"):
        for condition_name in frozen[model_name]["conditions"]:
            condition_key = f"{model_name}__{condition_name}"
            condition_order.append((model_name, condition_name))
            matrix = np.load(output_dir / f"{condition_key}.npy", mmap_mode="r", allow_pickle=False)
            for pseudo_index in range(int(frozen["pseudo_checkpoints_per_condition"])):
                start = pseudo_index * int(frozen["pseudo_checkpoint_size"])
                stop = start + int(frozen["pseudo_checkpoint_size"])
                checkpoint = np.asarray(matrix[start:stop], dtype=np.float64)
                n_calibration = int(frozen["calibration_per_pseudo_checkpoint"])
                calibration = checkpoint[:n_calibration]
                heldout = checkpoint[n_calibration:]

                energy_config = GateConfig(bootstrap_seed=gate_base_seed + condition_index * 100 + pseudo_index)
                energy_fit = fit_stationarity_gate(calibration, energy_config)
                energy_evaluation = evaluate_stationarity_gate(heldout, energy_fit)
                classical_fit = fit_adf_kpss_gate(calibration, ADFKPSSConfig())
                selected = {
                    "no_discard": 0,
                    "fixed_500": 500,
                    "fixed_1000": 1000,
                    "adf_kpss": classical_fit.w_star,
                    "energy": energy_fit.w_star,
                }
                for method in METHODS:
                    w_star = selected[method]
                    hill_values = (
                        [_hill(row, w_star) for row in heldout] if w_star is not None else []
                    )
                    rows.append({
                        "model": model_name,
                        "condition": condition_name,
                        "condition_index": condition_index,
                        "pseudo_checkpoint": pseudo_index,
                        "method": method,
                        "selected_w": w_star,
                        "detected_transient": w_star is None or w_star > 0,
                        "unresolved": w_star is None,
                        "heldout_hill_median": float(np.median(hill_values)) if hill_values else None,
                        "heldout_hill_values": hill_values,
                        "energy_tolerance": energy_fit.tolerance if method == "energy" else None,
                        "energy_heldout_frozen_w_passes": (
                            energy_evaluation.frozen_w_star_passes if method == "energy" else None
                        ),
                        "adf_kpss_block_pass_fractions": (
                            list(classical_fit.block_pass_fractions) if method == "adf_kpss" else None
                        ),
                        "bootstrap_seed": (
                            energy_config.bootstrap_seed if method == "energy" else None
                        ),
                    })
            condition_index += 1

    _attach_reference_errors(rows)
    summary = _summarize(rows)
    result = {
        "schema_version": 1,
        "repository": state,
        "parameters_sha256": sha256_file(PARAMS_PATH),
        "generation_manifest_sha256": sha256_file(generation_path),
        "gate_config": asdict(GateConfig()),
        "adf_kpss_config": asdict(ADFKPSSConfig()),
        "fixed_length": 4000,
        "hill_k_frac": 0.05,
        "condition_order": condition_order,
        "elapsed_seconds": time.time() - started,
        "summary": summary,
        "pseudo_checkpoint_rows": rows,
    }
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(result, indent=2) + "\n")
    return result


def _simulate(
    model_name: str,
    params: dict[str, Any],
    n_steps: int,
    seed: int,
    burn_in: int,
    initial_variance_multiplier: float,
) -> ArrayF:
    simulator: GARCH11 | AR1SV
    if model_name == "garch_t":
        simulator = GARCH11(**params)
    elif model_name == "ar1_sv":
        simulator = AR1SV(**params)
    else:
        raise ValueError(f"unknown analytic model {model_name!r}")
    return simulator.simulate(
        n_steps=n_steps,
        seed=seed,
        burn_in=burn_in,
        initial_variance_multiplier=initial_variance_multiplier,
    )


def _hill(returns: ArrayF, start: int, length: int = 4000) -> float:
    selected = returns[start:start + length]
    if selected.size != length:
        raise ValueError(f"fixed-length Hill slice requires {length} returns, got {selected.size}")
    return float(hill_tail_index(selected, k_frac=0.05).estimate)


def _verify_generation_artifacts(output_dir: Path, generation: dict[str, Any]) -> None:
    for record in generation["artifacts"]:
        path = output_dir / Path(record["artifact"]).name
        if sha256_file(path) != record["artifact_sha256"]:
            raise RuntimeError(f"artifact hash mismatch: {path}")
        matrix = np.load(path, mmap_mode="r", allow_pickle=False)
        if list(matrix.shape) != record["shape"] or str(matrix.dtype) != record["dtype"]:
            raise RuntimeError(f"artifact schema mismatch: {path}")


def _attach_reference_errors(rows: list[dict[str, Any]]) -> None:
    reference_condition = {"garch_t": "long_burn", "ar1_sv": "stationary"}
    references = {
        (row["model"], row["pseudo_checkpoint"]): row["heldout_hill_median"]
        for row in rows
        if row["condition"] == reference_condition[row["model"]] and row["method"] == "no_discard"
    }
    for row in rows:
        value = row["heldout_hill_median"]
        reference = references[(row["model"], row["pseudo_checkpoint"])]
        row["hill_reference"] = reference
        row["hill_abs_error_to_reference"] = (
            abs(float(value) - float(reference)) if value is not None and reference is not None else None
        )


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (row["model"], row["condition"], row["method"])
        groups.setdefault(key, []).append(row)
    by_condition_method: list[dict[str, Any]] = []
    for (model, condition, method), group in groups.items():
        selected = [int(row["selected_w"]) for row in group if row["selected_w"] is not None]
        errors = [float(row["hill_abs_error_to_reference"]) for row in group
                  if row["hill_abs_error_to_reference"] is not None]
        detected = sum(bool(row["detected_transient"]) for row in group)
        unresolved = sum(bool(row["unresolved"]) for row in group)
        by_condition_method.append({
            "model": model,
            "condition": condition,
            "method": method,
            "n": len(group),
            "detection_rate": detected / len(group),
            "detection_wilson_95": list(_wilson_interval(detected, len(group))),
            "unresolved_rate": unresolved / len(group),
            "median_selected_w_resolved": float(np.median(selected)) if selected else None,
            "median_hill_abs_error_to_reference": float(np.median(errors)) if errors else None,
        })

    stationary = {("garch_t", "long_burn"), ("ar1_sv", "stationary")}
    cold = {
        ("garch_t", "cold_low"),
        ("garch_t", "cold_high"),
        ("ar1_sv", "cold_low"),
        ("ar1_sv", "cold_high"),
    }
    stationary_fp: dict[str, Any] = {}
    cold_detection: dict[str, Any] = {}
    for method in METHODS:
        stationary_rows = [row for row in rows
                           if row["method"] == method and (row["model"], row["condition"]) in stationary]
        cold_rows = [row for row in rows
                     if row["method"] == method and (row["model"], row["condition"]) in cold]
        fp_count = sum(bool(row["detected_transient"]) for row in stationary_rows)
        detect_count = sum(bool(row["detected_transient"]) for row in cold_rows)
        stationary_fp[method] = {
            "count": fp_count,
            "n": len(stationary_rows),
            "rate": fp_count / len(stationary_rows),
            "wilson_95": list(_wilson_interval(fp_count, len(stationary_rows))),
        }
        cold_detection[method] = {
            "count": detect_count,
            "n": len(cold_rows),
            "rate": detect_count / len(cold_rows),
            "wilson_95": list(_wilson_interval(detect_count, len(cold_rows))),
        }
    energy_upper = float(stationary_fp["energy"]["wilson_95"][1])
    return {
        "by_condition_method": by_condition_method,
        "pooled_stationary_false_positive": stationary_fp,
        "pooled_cold_detection": cold_detection,
        "energy_specificity_gate_upper_le_0_15": energy_upper <= 0.15,
    }


def _wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total < 1 or not 0 <= successes <= total:
        raise ValueError("Wilson interval requires 0 <= successes <= total and total > 0")
    proportion = successes / total
    denominator = 1.0 + z ** 2 / total
    center = (proportion + z ** 2 / (2.0 * total)) / denominator
    half_width = z * np.sqrt(
        proportion * (1.0 - proportion) / total + z ** 2 / (4.0 * total ** 2)
    ) / denominator
    return float(max(0.0, center - half_width)), float(min(1.0, center + half_width))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("generate", "analyze", "all"))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--results-path", type=Path, default=DEFAULT_RESULTS_PATH)
    parser.add_argument("--allow-dirty", action="store_true", help="smoke/debug only; recorded as a deviation")
    parser.add_argument("--smoke", action="store_true", help="generate four short trajectories per condition")
    args = parser.parse_args()
    if args.smoke and args.command != "generate":
        parser.error("--smoke is supported only for generate")
    if args.command in ("generate", "all"):
        manifest = generate_controls(args.output_dir, allow_dirty=args.allow_dirty, smoke=args.smoke)
        print(json.dumps({"generation": manifest}, indent=2))
    if args.command in ("analyze", "all"):
        result = analyze_controls(args.output_dir, args.results_path, allow_dirty=args.allow_dirty)
        print(json.dumps({"summary": result["summary"]}, indent=2))


if __name__ == "__main__":
    main()
