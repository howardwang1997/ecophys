"""Executable contract for the frozen EcoMD v1 M0 configuration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from typing import Any

from ..models.ecomd import EcoMDConfig
from ..models.price_formation import ExcessDemandParams
from .losses import LossWeights
from .train_distributed import validate_release_training_contract

M0_MODEL_CONTRACT_VERSION = 1


def _expect(mapping: Mapping[str, Any], key: str, expected: object) -> None:
    actual = mapping.get(key)
    if type(actual) is not type(expected) or actual != expected:
        raise ValueError(f"{key} must equal {expected!r}, got {actual!r}")


def validate_m0_config(config: Mapping[str, Any]) -> None:
    """Validate the unique pre-registered EcoMD v1 M0 model configuration."""
    contract = config.get("contract")
    simulator = config.get("simulator")
    training = config.get("training")
    data_protocol = config.get("data_protocol")
    compute_protocol = config.get("compute_protocol")
    unknown_sections = sorted(
        set(config)
        - {"contract", "simulator", "training", "data_protocol", "compute_protocol"}
    )
    if unknown_sections:
        raise ValueError(f"unknown top-level sections: {unknown_sections}")
    if not isinstance(contract, Mapping):
        raise ValueError("missing mapping: contract")
    if not isinstance(simulator, Mapping):
        raise ValueError("missing mapping: simulator")
    if not isinstance(training, Mapping):
        raise ValueError("missing mapping: training")
    if not isinstance(data_protocol, Mapping):
        raise ValueError("missing mapping: data_protocol")
    if not isinstance(compute_protocol, Mapping):
        raise ValueError("missing mapping: compute_protocol")

    _expect(contract, "name", "ecomd_v1_m0")
    _expect(contract, "model_contract_version", M0_MODEL_CONTRACT_VERSION)
    _expect(contract, "status", "frozen")
    _expect(
        contract,
        "preregistration_commit",
        "2701833bcf7ba42803995745cd0fd338762b9ce0",
    )
    _expect(
        contract,
        "allowed_cpu_overrides",
        {"simulator.n_agents": [64], "training.n_iters": [2]},
    )
    _expect(training, "model_contract_version", M0_MODEL_CONTRACT_VERSION)
    validate_release_training_contract(dict(simulator), dict(training))

    valid_simulator_keys = {item.name for item in fields(EcoMDConfig)}
    unknown = sorted(set(simulator) - valid_simulator_keys)
    if unknown:
        raise ValueError(f"unknown EcoMDConfig fields: {unknown}")

    required_simulator_values: dict[str, Any] = {
        "n_agents": 256,
        "d_state": 32,
        "hidden": 96,
        "dt": 0.01,
        "pairwise_kind": "stochastic_mlp",
        "pairwise_kac_normalize": True,
        "sps_k_random": 50,
        "sps_resample_per_step": True,
        "pair_input_layernorm": True,
        "global_state_enabled": True,
        "global_state_d": 16,
        "global_state_update_every": 1,
        "global_state_into_pair": True,
        "twopop_enabled": True,
        "noise_dist": "normal",
        "jump_lambda": 0.0,
        "jump_scale": 0.0,
        "learn_gamma": False,
        "learn_temperature": False,
        "gamma_init": 10.0,
        "temperature_init": 0.05,
        "init_state_scale": 0.1,
        "lam_dissipation": 0.01,
        "twopop_gamma_scale": [0.7, 1.5, 1.0, 0.5],
        "twopop_temp_scale": [0.5, 2.0, 1.0, 0.3],
        "v2_type_seed": 42,
        "pair_features_extra": "none",
        "inner_steps_per_price": 1,
        "edge_gating_enabled": False,
        "pair_heterogeneous_heads": False,
        "agent_memory_enabled": False,
        "regime_enabled": False,
        "moe_enabled": False,
        "multi_timescale_enabled": False,
        "info_asym_enabled": False,
        "power_law_external": False,
        "sv_integrator_enabled": False,
        "scheduled_sampling_enabled": False,
        "legacy_total_derivative_force": False,
        "jump_legacy_train_proxy": False,
        "bptt_checkpoint_every": 0,
        "bptt_custom_function": False,
    }
    for key, expected in required_simulator_values.items():
        _expect(simulator, key, expected)

    price = simulator.get("price_formation_kwargs")
    if not isinstance(price, Mapping):
        raise ValueError("simulator.price_formation_kwargs must be a mapping")
    _expect(simulator, "price_formation", "excess_demand")
    required_price_values: dict[str, Any] = {
        "beta": 0.02,
        "kappa": 0.5,
        "sigma_price": 0.005,
        "ewma_alpha": 0.05,
        "initial_log_price": 0.0,
        "learnable_beta": False,
        "beta_hidden": 16,
        "hawkes_alpha": 0.1,
        "hawkes_kappa": 0.3,
        "hawkes_alpha_long": 0.0,
        "hawkes_kappa_long": 0.0,
        "hawkes_sign_mode": "coherent",
        "volume_mode": "delta_pos",
        "sigma_ed": 0.0,
        "ed_normalize": True,
        "sv_price_enabled": False,
        "tail_clamp_c": 0.0,
        "impact_concave_enabled": True,
        "impact_delta_init": 0.5,
        "impact_delta_learnable": False,
        "impact_scale": 0.5,
        "het_mass_enabled": False,
        "log_raw_excess_demand": True,
    }
    for key, expected in required_price_values.items():
        _expect(price, key, expected)
    valid_price_keys = {item.name for item in fields(ExcessDemandParams)}
    unknown_price = sorted(set(price) - valid_price_keys)
    if unknown_price:
        raise ValueError(f"unknown ExcessDemandParams fields: {unknown_price}")
    canonical_price = ExcessDemandParams(**required_price_values)
    if ExcessDemandParams(**dict(price)) != canonical_price:
        raise ValueError("price_formation_kwargs deviates from the M0 contract")

    canonical_simulator = EcoMDConfig(
        **required_simulator_values,
        price_formation="excess_demand",
        price_formation_kwargs=dict(price),
        v2_kyle_enabled=False,
        v2_kyle_lambda_learnable=False,
        regime_kind="gru",
        regime_modulate_gamma=False,
        regime_modulate_temp=False,
        regime_modulate_kappa=False,
        edge_gating_input_u=False,
    )
    if EcoMDConfig(**dict(simulator)) != canonical_simulator:
        raise ValueError("simulator configuration deviates from the M0 contract")

    required_training_values: dict[str, Any] = {
        "mixed_precision": "fp32",
        "chunk_steps": 64,
        "warmup_steps": 16,
        "n_iters": 600,
        "rollout_reg_enabled": False,
        "target_dataset": "spx",
        "target_period": "2015-2018_daily",
        "state_complete": True,
        "persistent_state": True,
        "release_contract_version": 1,
        "lr": 0.001,
        "lr_warmup_iters": 10,
        "grad_clip_max_norm": 100.0,
        "checkpoint_every_s": 600.0,
        "seed": 0,
    }
    for key, expected in required_training_values.items():
        _expect(training, key, expected)
    allowed_training_keys = (
        set(required_training_values)
        | {"model_contract_version", "loss_weights"}
    )
    if set(training) != allowed_training_keys:
        raise ValueError(
            "training keys deviate from the M0 contract: "
            f"expected {sorted(allowed_training_keys)}, got {sorted(training)}"
        )
    loss_weights = training.get("loss_weights")
    if not isinstance(loss_weights, Mapping):
        raise ValueError("training.loss_weights must be a mapping")
    _expect(loss_weights, "loss_family", "moments")
    _expect(loss_weights, "distance_mode", "l1")
    _expect(loss_weights, "tail_estimator", "soft_hill")
    _expect(loss_weights, "max_lag", 8)
    canonical_weights = LossWeights(
        w_acf_sq=1.0,
        w_leverage=0.2,
        w_hill=0.1,
        max_lag=8,
        hill_k_frac=0.05,
        w_autocorr_r=0.5,
        w_hill_max=0.3,
        hill_max_target=10.0,
        loss_family="moments",
        distance_mode="l1",
        tail_estimator="soft_hill",
        balance_mode="fixed",
    )
    try:
        actual_weights = LossWeights(**dict(loss_weights))
    except TypeError as exc:
        raise ValueError(f"invalid M0 loss_weights: {exc}") from exc
    if actual_weights != canonical_weights:
        raise ValueError("training.loss_weights deviates from the M0 contract")
    usable_returns = int(training["chunk_steps"]) - 1 - int(training["warmup_steps"])
    if usable_returns < 4 * int(loss_weights["max_lag"]):
        raise ValueError(
            "training horizon is too short: "
            f"usable_returns={usable_returns} < 4*max_lag"
        )

    _expect(data_protocol, "train", "2015-2018_daily")
    _expect(data_protocol, "validation", "2019_daily")
    _expect(data_protocol, "sealed_crash_test", "2020_daily")
    _expect(data_protocol, "temporal_test", "2021-2024_daily")
    _expect(data_protocol, "supplemental_holdout", "2025-2026_daily")

    _expect(compute_protocol, "reference_device", "v100_32gb")
    _expect(compute_protocol, "cpu_gate_n_agents", 64)
    _expect(compute_protocol, "v100_pilot_n_iters", 10)
    _expect(compute_protocol, "peak_reserved_gib_max", 26.0)
    _expect(compute_protocol, "projected_reference_hours_max", 12.0)


__all__ = ["M0_MODEL_CONTRACT_VERSION", "validate_m0_config"]
