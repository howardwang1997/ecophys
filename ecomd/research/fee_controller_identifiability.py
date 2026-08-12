"""Generated closed-loop identifiability witnesses for fee-controller interventions."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import subprocess
import sys
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

for _accelerator_variable in ("CUDA_VISIBLE_DEVICES", "ROCR_VISIBLE_DEVICES"):
    os.environ[_accelerator_variable] = "-1"
for _thread_variable in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[_thread_variable] = "1"

import numpy as np  # noqa: E402
import yaml  # noqa: E402
from numpy.typing import NDArray  # noqa: E402

CONFIG_SCHEMA = "ecophys-fee-controller-identifiability-witness/v1"
FREEZE_SCHEMA = "ecophys-fee-controller-identifiability-witness-freeze/v1"
RESULT_SCHEMA = "ecophys-fee-controller-identifiability-witness-result/v1"
FORMAL_EXPERIMENT_ID = "151_fee_controller_identifiability_witness"
FloatArray = NDArray[np.float64]

_NETWORK_AUDIT_EVENTS = frozenset(
    {
        "socket.bind",
        "socket.connect",
        "socket.getaddrinfo",
        "socket.gethostbyaddr",
        "socket.gethostbyname",
        "socket.sendto",
    }
)


@dataclass(frozen=True)
class LinearSystem:
    """Response and latent-state matrices for one generated system."""

    response: FloatArray
    latent_transition: FloatArray
    fee_to_latent: FloatArray

    def __post_init__(self) -> None:
        arrays = (self.response, self.latent_transition, self.fee_to_latent)
        if any(array.shape != (2, 2) for array in arrays):
            raise ValueError("linear-system matrices must all be 2 by 2")
        if any(not np.isfinite(array).all() for array in arrays):
            raise ValueError("linear-system matrices must be finite")


@dataclass(frozen=True)
class CellResult:
    """Aggregate diagnostics for one topology, perturbation and seed."""

    response_distance: float
    development_maximum_difference: float
    phi_residual: float
    gamma_residual: float
    reference_spectral_radius: float
    transformed_spectral_radius: float
    development_finite: bool
    intervention_maximum_divergence: float
    intervention_rms_divergence: float
    intervention_finite: bool


def _mapping(value: object, *, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be a mapping")
    return cast(Mapping[str, object], value)


def _sequence(value: object, *, name: str) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{name} must be a sequence")
    return cast(Sequence[object], value)


def _string(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a nonempty string")
    return value


def _integer(payload: Mapping[str, object], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _number(payload: Mapping[str, object], key: str) -> float:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key} must be numeric")
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(f"{key} must be finite")
    return result


def _numeric_value(value: object, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _array(value: object, *, name: str, shape: tuple[int, ...]) -> FloatArray:
    result = np.asarray(value, dtype=np.float64)
    if result.shape != shape or not np.isfinite(result).all():
        raise ValueError(f"{name} must be a finite array with shape {shape}")
    return result


def load_config(path: Path) -> dict[str, object]:
    """Load and minimally validate one witness configuration."""

    raw: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("witness config must contain a mapping")
    config = cast(dict[str, object], raw)
    if config.get("schema_version") != CONFIG_SCHEMA:
        raise ValueError(f"config schema must equal {CONFIG_SCHEMA}")
    return config


def reference_system(config: Mapping[str, object]) -> LinearSystem:
    """Construct the frozen reference system from configuration."""

    reference = _mapping(config.get("reference"), name="reference")
    return LinearSystem(
        response=_array(reference.get("response_matrix"), name="response_matrix", shape=(2, 2)),
        latent_transition=_array(
            reference.get("latent_transition"), name="latent_transition", shape=(2, 2)
        ),
        fee_to_latent=_array(
            reference.get("fee_to_latent"), name="fee_to_latent", shape=(2, 2)
        ),
    )


def construct_alias(
    system: LinearSystem,
    perturbation: FloatArray,
    development_gain: FloatArray,
) -> LinearSystem:
    """Construct the frozen observationally aliased system at one controller gain."""

    delta = _array(perturbation, name="perturbation", shape=(2, 2))
    gain = _array(development_gain, name="development_gain", shape=(2, 2))
    transformed_response = system.response - delta
    transformed_transition = system.latent_transition + delta @ gain
    transformed_fee_to_latent = (
        system.fee_to_latent
        - system.latent_transition @ delta
        + delta @ (np.eye(2, dtype=np.float64) + gain @ transformed_response)
    )
    return LinearSystem(
        response=transformed_response,
        latent_transition=transformed_transition,
        fee_to_latent=transformed_fee_to_latent,
    )


def seed_from_label(
    seed_root: int,
    topology: str,
    perturbation_id: str,
    seed_index: int,
) -> int:
    """Derive the frozen NumPy seed from the declared SHA256 label."""

    if seed_root < 0 or seed_index < 0 or not topology or not perturbation_id:
        raise ValueError("seed label fields must be nonnegative and nonempty")
    label = f"{seed_root}|{topology}|{perturbation_id}|{seed_index}"
    return int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest()[:8], "big")


def intervention_stack(
    development_gain: FloatArray,
    intervention_gains: Sequence[FloatArray],
) -> FloatArray:
    """Stack the controller-difference maps acting on a two-by-two perturbation."""

    development = _array(development_gain, name="development_gain", shape=(2, 2))
    if not intervention_gains:
        raise ValueError("at least one intervention gain is required")
    identity = np.eye(2, dtype=np.float64)
    blocks = [
        np.kron(
            (_array(gain, name=f"intervention_gain[{index}]", shape=(2, 2)) - development).T,
            identity,
        )
        for index, gain in enumerate(intervention_gains)
    ]
    return np.vstack(blocks)


def stack_diagnostics(stack: FloatArray) -> dict[str, object]:
    """Return rank and all singular values for one intervention stack."""

    if stack.ndim != 2 or not np.isfinite(stack).all():
        raise ValueError("intervention stack must be a finite matrix")
    singular_values = np.linalg.svd(stack, compute_uv=False)
    return {
        "rank": int(np.linalg.matrix_rank(stack)),
        "singular_values": [float(value) for value in singular_values],
        "minimum_singular_value": float(np.min(singular_values)),
    }


def _spectral_radius(matrix: FloatArray) -> float:
    return float(np.max(np.abs(np.linalg.eigvals(matrix))))


def _step(system: LinearSystem, q: FloatArray, h: FloatArray, gain: FloatArray) -> tuple[FloatArray, FloatArray, FloatArray]:
    y = system.response @ q + h
    return y, q + gain @ y, system.latent_transition @ h + system.fee_to_latent @ q


def run_cell(
    reference: LinearSystem,
    perturbation: FloatArray,
    development_gain: FloatArray,
    intervention_gain: FloatArray,
    q0: FloatArray,
    h0: FloatArray,
    innovations: FloatArray,
    intervention_steps: int,
) -> CellResult:
    """Run one already-generated development/intervention witness cell."""

    delta = _array(perturbation, name="perturbation", shape=(2, 2))
    development = _array(development_gain, name="development_gain", shape=(2, 2))
    intervention = _array(intervention_gain, name="intervention_gain", shape=(2, 2))
    initial_q = _array(q0, name="q0", shape=(2,))
    initial_h = _array(h0, name="h0", shape=(2,))
    noise = np.asarray(innovations, dtype=np.float64)
    if noise.ndim != 2 or noise.shape[1] != 2 or not np.isfinite(noise).all():
        raise ValueError("innovations must be a finite n by 2 array")
    if intervention_steps <= 0:
        raise ValueError("intervention_steps must be positive")

    transformed = construct_alias(reference, delta, development)
    phi_residual = float(
        np.max(
            np.abs(
                transformed.latent_transition
                - reference.latent_transition
                - delta @ development
            )
        )
    )
    expected_gamma = (
        reference.fee_to_latent
        - reference.latent_transition @ delta
        + delta @ (np.eye(2, dtype=np.float64) + development @ transformed.response)
    )
    gamma_residual = float(np.max(np.abs(transformed.fee_to_latent - expected_gamma)))

    q = initial_q.copy()
    h = initial_h.copy()
    transformed_q = initial_q.copy()
    transformed_h = initial_h + delta @ initial_q
    development_maximum = 0.0
    development_finite = True
    for innovation in noise:
        y, next_q, next_h = _step(reference, q, h, development)
        transformed_y, next_transformed_q, next_transformed_h = _step(
            transformed, transformed_q, transformed_h, development
        )
        development_maximum = max(
            development_maximum,
            float(np.max(np.abs(np.concatenate((q - transformed_q, y - transformed_y))))),
        )
        next_h = next_h + innovation
        next_transformed_h = next_transformed_h + innovation
        development_finite = development_finite and bool(
            np.isfinite(
                np.concatenate(
                    (y, next_q, next_h, transformed_y, next_transformed_q, next_transformed_h)
                )
            ).all()
        )
        q, h = next_q, next_h
        transformed_q, transformed_h = next_transformed_q, next_transformed_h

    squared_divergence = 0.0
    maximum_divergence = 0.0
    intervention_finite = True
    for _ in range(intervention_steps):
        y, next_q, next_h = _step(reference, q, h, intervention)
        transformed_y, next_transformed_q, next_transformed_h = _step(
            transformed, transformed_q, transformed_h, intervention
        )
        observed_difference = np.concatenate((q - transformed_q, y - transformed_y))
        maximum_divergence = max(maximum_divergence, float(np.max(np.abs(observed_difference))))
        squared_divergence += float(observed_difference @ observed_difference)
        intervention_finite = intervention_finite and bool(
            np.isfinite(
                np.concatenate(
                    (y, next_q, next_h, transformed_y, next_transformed_q, next_transformed_h)
                )
            ).all()
        )
        q, h = next_q, next_h
        transformed_q, transformed_h = next_transformed_q, next_transformed_h

    return CellResult(
        response_distance=float(np.linalg.norm(reference.response - transformed.response)),
        development_maximum_difference=development_maximum,
        phi_residual=phi_residual,
        gamma_residual=gamma_residual,
        reference_spectral_radius=_spectral_radius(reference.latent_transition),
        transformed_spectral_radius=_spectral_radius(transformed.latent_transition),
        development_finite=development_finite,
        intervention_maximum_divergence=maximum_divergence,
        intervention_rms_divergence=float(
            np.sqrt(squared_divergence / (intervention_steps * 4))
        ),
        intervention_finite=intervention_finite,
    )


def _diagonal(values: object, *, name: str) -> FloatArray:
    sequence = _sequence(values, name=name)
    if len(sequence) != 2:
        raise ValueError(f"{name} must contain two values")
    diagonal = np.asarray(sequence, dtype=np.float64)
    if not np.isfinite(diagonal).all():
        raise ValueError(f"{name} must be finite")
    return np.diag(diagonal)


def controller_gains(config: Mapping[str, object]) -> dict[str, FloatArray]:
    """Construct all frozen generated and BPO controller gains."""

    controllers = _mapping(config.get("controllers"), name="controllers")
    generated_development = _mapping(
        controllers.get("generated_development"), name="generated_development"
    )
    generated_nonproportional = _mapping(
        controllers.get("generated_nonproportional"), name="generated_nonproportional"
    )
    bpo = _mapping(controllers.get("bpo"), name="bpo")
    gas_per_blob = _integer(bpo, "gas_per_blob")
    execution_gain = _number(bpo, "execution_gain")
    gains: dict[str, FloatArray] = {
        "generated_development": _diagonal(
            generated_development.get("diagonal"), name="generated_development.diagonal"
        ),
        "generated_nonproportional": _diagonal(
            generated_nonproportional.get("diagonal"), name="generated_nonproportional.diagonal"
        ),
    }
    schedules = _sequence(bpo.get("schedules"), name="bpo.schedules")
    for raw_schedule in schedules:
        schedule = _mapping(raw_schedule, name="bpo schedule")
        name = _string(schedule, "name")
        target = _integer(schedule, "target")
        maximum = _integer(schedule, "maximum")
        update_fraction = _integer(schedule, "update_fraction")
        if not 0 < target < maximum or update_fraction <= 0:
            raise ValueError(f"invalid BPO schedule: {name}")
        gains[name] = np.diag(
            np.asarray(
                [execution_gain, gas_per_blob * target / update_fraction], dtype=np.float64
            )
        )
    required = {"Prague_Osaka", "BPO1", "BPO2"}
    if not required.issubset(gains):
        raise ValueError("BPO schedules must include Prague_Osaka, BPO1 and BPO2")
    return gains


def _perturbations(config: Mapping[str, object]) -> list[tuple[str, FloatArray]]:
    result: list[tuple[str, FloatArray]] = []
    for raw in _sequence(config.get("alias_perturbations"), name="alias_perturbations"):
        entry = _mapping(raw, name="alias perturbation")
        result.append(
            (
                _string(entry, "id"),
                _array(entry.get("matrix"), name="perturbation.matrix", shape=(2, 2)),
            )
        )
    if not result or len({name for name, _ in result}) != len(result):
        raise ValueError("alias perturbations must have unique nonempty ids")
    return result


def _state(config: Mapping[str, object]) -> tuple[FloatArray, FloatArray, float]:
    state = _mapping(config.get("state"), name="state")
    return (
        _array(state.get("q0"), name="q0", shape=(2,)),
        _array(state.get("h0"), name="h0", shape=(2,)),
        _number(state, "innovation_sigma"),
    )


def _cell_passes_w1(cell: CellResult, gates: Mapping[str, object]) -> bool:
    return bool(
        cell.response_distance >= _number(gates, "minimum_response_matrix_distance")
        and cell.development_maximum_difference
        <= _number(gates, "maximum_development_observation_difference")
        and cell.phi_residual <= _number(gates, "maximum_algebra_residual")
        and cell.gamma_residual <= _number(gates, "maximum_algebra_residual")
        and cell.reference_spectral_radius
        < _number(gates, "maximum_latent_spectral_radius")
        and cell.transformed_spectral_radius
        < _number(gates, "maximum_latent_spectral_radius")
        and cell.development_finite
        and cell.intervention_finite
    )


def _summarize_cells(cells: Sequence[CellResult], threshold: float) -> dict[str, object]:
    divergences = np.asarray(
        [cell.intervention_maximum_divergence for cell in cells], dtype=np.float64
    )
    rms_values = np.asarray(
        [cell.intervention_rms_divergence for cell in cells], dtype=np.float64
    )
    return {
        "seed_count": len(cells),
        "maximum_development_difference": max(
            cell.development_maximum_difference for cell in cells
        ),
        "maximum_intervention_divergence": float(np.max(divergences)),
        "minimum_intervention_divergence": float(np.min(divergences)),
        "median_intervention_divergence": float(np.median(divergences)),
        "maximum_intervention_rms_divergence": float(np.max(rms_values)),
        "fraction_meeting_divergence_threshold": float(np.mean(divergences >= threshold)),
    }


def evaluate_formal_cells(config: Mapping[str, object], *, formal_authorized: bool) -> dict[str, object]:
    """Evaluate all frozen Experiment 151 cells after an explicit freeze authorization."""

    if not formal_authorized or config.get("experiment_id") != FORMAL_EXPERIMENT_ID:
        raise RuntimeError("formal Experiment 151 cells require verified freeze authorization")
    reference = reference_system(config)
    gains = controller_gains(config)
    perturbations = _perturbations(config)
    q0, h0, innovation_sigma = _state(config)
    gates = _mapping(config.get("gates"), name="gates")
    formal_range = _mapping(config.get("formal_seed_indices"), name="formal_seed_indices")
    seed_start = _integer(formal_range, "start")
    seed_stop = _integer(formal_range, "stop_exclusive")
    seed_root = _integer(config, "seed_root")
    development_steps = _integer(config, "development_steps")
    intervention_steps = _integer(config, "intervention_steps")
    if seed_start != 0 or seed_stop != 128:
        raise ValueError("Experiment 151 formal seeds must be exactly 0 through 127")

    topologies: tuple[tuple[str, FloatArray, tuple[tuple[str, FloatArray], ...]], ...] = (
        (
            "bpo",
            gains["Prague_Osaka"],
            (("BPO1", gains["BPO1"]), ("BPO2", gains["BPO2"])),
        ),
        (
            "nonproportional",
            gains["generated_development"],
            (("generated_nonproportional", gains["generated_nonproportional"]),),
        ),
    )
    w1_all_pass = True
    counts = {
        "perturbations": len(perturbations),
        "seeds": seed_stop - seed_start,
        "development_topologies": len(topologies),
        "development_cells": 0,
        "bpo_intervention_cells": 0,
        "nonproportional_intervention_cells": 0,
    }
    summaries: dict[str, object] = {}
    geometry: dict[str, object] = {}
    for topology, development_gain, interventions in topologies:
        topology_summaries: dict[str, object] = {}
        stack = intervention_stack(
            development_gain, [gain for _, gain in interventions]
        )
        geometry[topology] = stack_diagnostics(stack)
        for perturbation_id, perturbation in perturbations:
            intervention_cells: dict[str, list[CellResult]] = {
                name: [] for name, _ in interventions
            }
            for seed_index in range(seed_start, seed_stop):
                rng = np.random.default_rng(
                    seed_from_label(seed_root, topology, perturbation_id, seed_index)
                )
                innovations = rng.normal(
                    0.0, innovation_sigma, size=(development_steps, 2)
                )
                for intervention_name, intervention_gain in interventions:
                    cell = run_cell(
                        reference,
                        perturbation,
                        development_gain,
                        intervention_gain,
                        q0,
                        h0,
                        innovations,
                        intervention_steps,
                    )
                    intervention_cells[intervention_name].append(cell)
                    w1_all_pass = w1_all_pass and _cell_passes_w1(cell, gates)
                    if topology == "bpo":
                        counts["bpo_intervention_cells"] += 1
                    else:
                        counts["nonproportional_intervention_cells"] += 1
                counts["development_cells"] += 1
            topology_summaries[perturbation_id] = {
                name: _summarize_cells(
                    cells,
                    _number(gates, "minimum_nonproportional_divergence"),
                )
                for name, cells in intervention_cells.items()
            }
        summaries[topology] = topology_summaries

    expected_counts = _mapping(config.get("expected_counts"), name="expected_counts")
    count_pass = all(counts[key] == _integer(expected_counts, key) for key in counts)
    bpo_displacements = {
        name: float(np.linalg.norm(gains[name] - gains["Prague_Osaka"]))
        for name in ("BPO1", "BPO2")
    }
    bpo_summaries = cast(Mapping[str, object], summaries["bpo"])
    bpo_maximum_divergence = max(
        _numeric_value(
            cast(Mapping[str, object], cast(Mapping[str, object], raw)[intervention]).get(
                "maximum_intervention_divergence"
            ),
            name="maximum_intervention_divergence",
        )
        for raw in bpo_summaries.values()
        for intervention in ("BPO1", "BPO2")
    )
    bpo_geometry = cast(Mapping[str, object], geometry["bpo"])
    w2_pass = bool(
        max(bpo_displacements.values())
        < _number(gates, "maximum_bpo_gain_displacement")
        and bpo_maximum_divergence
        < _number(gates, "maximum_bpo_observation_divergence")
        and int(cast(int, bpo_geometry["rank"]))
        <= _integer(gates, "maximum_bpo_stack_rank")
        and float(cast(float, bpo_geometry["minimum_singular_value"]))
        < _number(gates, "maximum_bpo_stack_minimum_singular_value")
    )
    nonproportional_summaries = cast(
        Mapping[str, object], summaries["nonproportional"]
    )
    nonproportional_geometry = cast(
        Mapping[str, object], geometry["nonproportional"]
    )
    w3_pass = bool(
        all(
            _numeric_value(
                cast(
                    Mapping[str, object],
                    cast(Mapping[str, object], raw)["generated_nonproportional"],
                ).get("fraction_meeting_divergence_threshold"),
                name="fraction_meeting_divergence_threshold",
            )
            >= _number(gates, "minimum_nonproportional_seed_fraction")
            for raw in nonproportional_summaries.values()
        )
        and int(cast(int, nonproportional_geometry["rank"]))
        == _integer(gates, "required_nonproportional_stack_rank")
        and float(cast(float, nonproportional_geometry["minimum_singular_value"]))
        >= _number(gates, "minimum_nonproportional_stack_singular_value")
    )
    decisions = _mapping(config.get("decisions"), name="decisions")
    if not w1_all_pass or not count_pass:
        decision = _string(decisions, "implementation_fail")
    elif w2_pass and w3_pass:
        decision = _string(decisions, "pass")
    else:
        decision = _string(decisions, "intervention_fail")
    return {
        "decision": decision,
        "gates": {
            "W1_exact_alias_and_stability": w1_all_pass,
            "W2_bpo_impotence": w2_pass,
            "W3_nonproportional_separation": w3_pass,
            "W4_assumption_audit": True,
            "count_contract": count_pass,
        },
        "counts": counts,
        "bpo_gain_displacements": bpo_displacements,
        "bpo_maximum_observation_divergence": bpo_maximum_divergence,
        "geometry": geometry,
        "summaries": summaries,
        "assumption_audit": {
            "latent_dynamics_invariance_required": True,
            "free_regime_specific_latent_dynamics_restore_alias": True,
            "real_adaptation_identified": False,
            "base_is_independent_replication": False,
            "bpo_is_independent_replication": False,
            "real_data_gate_changed": False,
        },
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    )
    return completed.stdout.strip()


def _verify_freeze(root: Path, config_path: Path, freeze_path: Path) -> dict[str, object]:
    raw: object = yaml.safe_load(freeze_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RuntimeError("Experiment 151 freeze must contain a mapping")
    freeze = cast(dict[str, object], raw)
    if freeze.get("schema_version") != FREEZE_SCHEMA:
        raise RuntimeError("Experiment 151 freeze schema mismatch")
    if freeze.get("formal_run_authorized") is not True:
        raise RuntimeError("Experiment 151 formal run is not authorized")
    if _git(root, "status", "--porcelain"):
        raise RuntimeError("Experiment 151 requires a clean committed checkout")
    for key in ("preregistration_commit", "void_commit", "implementation_commit"):
        commit = _string(freeze, key)
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
        )
    expected_paths: Mapping[str, Path] = {
        "config": config_path,
        "preregistration": config_path.parent / "PREREGISTRATION.md",
        "readme": config_path.parent / "README.md",
        "void_record": root
        / "experiments/150_fee_controller_identifiability_witness/PROTOCOL_DEVIATION_VOID.md",
        "module": Path(__file__).resolve(),
        "test": root / "tests/test_fee_controller_identifiability.py",
    }
    files = _mapping(freeze.get("files"), name="files")
    for key, expected_path in expected_paths.items():
        entry = _mapping(files.get(key), name=f"files.{key}")
        recorded_path = (root / _string(entry, "path")).resolve()
        if recorded_path != expected_path.resolve():
            raise RuntimeError(f"Experiment 151 frozen path mismatch: {key}")
        if _sha256_file(recorded_path) != _string(entry, "sha256"):
            raise RuntimeError(f"Experiment 151 frozen hash mismatch: {key}")
    dependencies = _mapping(freeze.get("dependencies"), name="dependencies")
    if platform.python_version() != _string(dependencies, "python"):
        raise RuntimeError("Experiment 151 Python version mismatch")
    if importlib.metadata.version("numpy") != _string(dependencies, "numpy"):
        raise RuntimeError("Experiment 151 NumPy version mismatch")
    if importlib.metadata.version("PyYAML") != _string(dependencies, "pyyaml"):
        raise RuntimeError("Experiment 151 PyYAML version mismatch")
    return freeze


def _network_audit_hook(event: str, _arguments: tuple[object, ...]) -> None:
    if event in _NETWORK_AUDIT_EVENTS:
        raise PermissionError(f"network disabled during Experiment 151: {event}")


def _peak_rss_gb() -> float:
    peak = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    if sys.platform != "darwin":
        peak *= 1024.0
    return peak / (1024.0**3)


def _atomic_write_json(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def run_formal(config_path: Path, output_path: Path) -> dict[str, object]:
    """Run the sole frozen Experiment 151 formal attempt."""

    root = Path(__file__).resolve().parents[2]
    resolved_config = config_path.resolve()
    if not resolved_config.is_relative_to(root):
        raise RuntimeError("Experiment 151 config must be inside the repository")
    expected_output = resolved_config.parent / "artifacts/raw/witness.json"
    if output_path.resolve() != expected_output.resolve():
        raise RuntimeError("Experiment 151 output path differs from preregistration")
    if output_path.exists():
        raise RuntimeError("Experiment 151 formal output already exists")
    config = load_config(resolved_config)
    freeze = _verify_freeze(root, resolved_config, resolved_config.parent / "FREEZE.yaml")
    sys.addaudithook(_network_audit_hook)
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    result = evaluate_formal_cells(config, formal_authorized=True)
    resources = _mapping(config.get("resources"), name="resources")
    wall_seconds = time.perf_counter() - started_wall
    cpu_seconds = time.process_time() - started_cpu
    peak_rss_gb = _peak_rss_gb()
    resource_pass = bool(
        wall_seconds <= 60.0 * _number(resources, "max_wall_minutes")
        and cpu_seconds <= 3600.0 * _number(resources, "max_cpu_core_hours")
        and peak_rss_gb <= _number(resources, "max_ram_gb")
    )
    if not resource_pass:
        decisions = _mapping(config.get("decisions"), name="decisions")
        result["decision"] = _string(decisions, "implementation_fail")
    result_gates = cast(dict[str, object], result["gates"])
    result_gates["resource_contract"] = resource_pass
    formal: dict[str, object] = {
        "schema_version": RESULT_SCHEMA,
        "experiment_id": config.get("experiment_id"),
        "decision": result["decision"],
        "git_sha": _git(root, "rev-parse", "HEAD"),
        "preregistration_commit": freeze["preregistration_commit"],
        "implementation_commit": freeze["implementation_commit"],
        "config_sha256": _sha256_file(resolved_config),
        "module_sha256": _sha256_file(Path(__file__).resolve()),
        "witness_result": result,
        "resources": {
            "wall_seconds": wall_seconds,
            "cpu_seconds": cpu_seconds,
            "peak_rss_gb": peak_rss_gb,
            "controller_processes": 1,
            "numerical_threads": 1,
            "network_calls": 0,
            "chain_outcome_files": 0,
            "remote_hosts": 0,
            "gpu_hours": 0.0,
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": importlib.metadata.version("numpy"),
            "pyyaml": importlib.metadata.version("PyYAML"),
            "platform": platform.platform(),
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "rocr_visible_devices": os.environ.get("ROCR_VISIBLE_DEVICES"),
        },
    }
    _atomic_write_json(output_path, formal)
    return formal


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line Experiment 151 witness."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    formal = run_formal(arguments.config, arguments.output)
    print(json.dumps(formal, indent=2, sort_keys=True))
    config = load_config(arguments.config)
    decisions = _mapping(config.get("decisions"), name="decisions")
    return 0 if formal["decision"] == _string(decisions, "pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
