"""Typed loading and hashing for the Experiment 141 protocol."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from omegaconf import OmegaConf

from .feasibility import TruthFamily, WorldSettings


@dataclass(frozen=True)
class SeedSplit:
    intervention_magnitudes: tuple[float, ...]
    seed_start: int
    n_seeds: int


@dataclass(frozen=True)
class EvaluationSplit(SeedSplit):
    truth_families: tuple[TruthFamily, ...]
    shared_anchor_seed: int
    n_shards: int


@dataclass(frozen=True)
class FitSettings:
    lower_rate: float
    upper_rate: float
    rho_bounds: tuple[float, float]
    target_slope_bounds: tuple[float, float]


@dataclass(frozen=True)
class GateSettings:
    maximum_mechanics_violations: int
    single_rate_minimum_rmse_reduction: float
    single_rate_minimum_bootstrap_lower: float
    two_rate_minimum_rmse_reduction: float
    two_rate_minimum_bootstrap_lower: float
    no_adaptation_maximum_rmse_degradation: float
    confound_residual_z_threshold: float
    confound_minimum_detection_rate: float
    confound_maximum_false_positive_rate: float
    bootstrap_replicates: int
    bootstrap_seed: int


@dataclass(frozen=True)
class HardwareProbeSettings:
    seed: int
    batch_size: int
    sequence_length: int
    feature_dim: int
    hidden_dim: int
    steps: int
    split_step: int
    learning_rate: float
    maximum_memory_fraction: float
    cross_device_relative_loss_tolerance: float


@dataclass(frozen=True)
class Protocol:
    experiment: int
    protocol_version: str
    root_seed: int
    base_commit: str
    world: WorldSettings
    development: SeedSplit
    evaluation: EvaluationSplit
    fit: FitSettings
    gates: GateSettings
    hardware_probe: HardwareProbeSettings
    config_path: Path
    config_sha256: str


def _mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a mapping")
    return cast(dict[str, Any], value)


def _tuple_float(value: object, name: str) -> tuple[float, ...]:
    if not isinstance(value, list):
        raise TypeError(f"{name} must be a list")
    return tuple(float(item) for item in value)


def load_protocol(path: str | Path) -> Protocol:
    config_path = Path(path).resolve()
    raw_bytes = config_path.read_bytes()
    container = OmegaConf.to_container(OmegaConf.load(config_path), resolve=True)
    root = _mapping(container, "protocol")
    world = _mapping(root["world"], "world")
    development = _mapping(root["development"], "development")
    evaluation = _mapping(root["evaluation"], "evaluation")
    fit = _mapping(root["fit"], "fit")
    gates = _mapping(root["gates"], "gates")
    hardware = _mapping(root["hardware_probe"], "hardware_probe")
    truth_families = tuple(str(item) for item in cast(list[object], evaluation["truth_families"]))
    valid_families = {"none", "single_rate", "two_rate", "confounded"}
    if any(family not in valid_families for family in truth_families):
        raise ValueError("unsupported evaluation truth family")
    return Protocol(
        experiment=int(root["experiment"]),
        protocol_version=str(root["protocol_version"]),
        root_seed=int(root["root_seed"]),
        base_commit=str(root["base_commit"]),
        world=WorldSettings(**world),
        development=SeedSplit(
            intervention_magnitudes=_tuple_float(
                development["intervention_magnitudes"], "development magnitudes"
            ),
            seed_start=int(development["seed_start"]),
            n_seeds=int(development["n_seeds"]),
        ),
        evaluation=EvaluationSplit(
            intervention_magnitudes=_tuple_float(
                evaluation["intervention_magnitudes"], "evaluation magnitudes"
            ),
            seed_start=int(evaluation["seed_start"]),
            n_seeds=int(evaluation["n_seeds"]),
            truth_families=cast(tuple[TruthFamily, ...], truth_families),
            shared_anchor_seed=int(evaluation["shared_anchor_seed"]),
            n_shards=int(evaluation["n_shards"]),
        ),
        fit=FitSettings(
            lower_rate=float(fit["lower_rate"]),
            upper_rate=float(fit["upper_rate"]),
            rho_bounds=cast(tuple[float, float], _tuple_float(fit["rho_bounds"], "rho_bounds")),
            target_slope_bounds=cast(
                tuple[float, float],
                _tuple_float(fit["target_slope_bounds"], "target_slope_bounds"),
            ),
        ),
        gates=GateSettings(**gates),
        hardware_probe=HardwareProbeSettings(**hardware),
        config_path=config_path,
        config_sha256=hashlib.sha256(raw_bytes).hexdigest(),
    )
