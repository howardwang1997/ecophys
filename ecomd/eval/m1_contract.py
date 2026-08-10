"""Executable checks for the pre-output EcoMD v1 M1 screen."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from ..data.yfinance_provenance import sha256_file
from .stationarity_baselines import ADFKPSSConfig
from .stationarity_gate import GateConfig


def _mapping(parent: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = parent.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"missing mapping: {key}")
    return value


def validate_m1_protocol(config: Mapping[str, Any], repo_root: Path) -> None:
    """Reject changes to the frozen data, training, rollout and decision contract."""
    expected_sections = {
        "contract",
        "data",
        "training",
        "rollout",
        "energy_gate",
        "adf_kpss_comparator",
        "scoring",
        "decision",
        "compute",
    }
    if set(config) != expected_sections:
        raise ValueError(f"M1 sections must equal {sorted(expected_sections)}")

    contract = _mapping(config, "contract")
    if contract.get("name") != "ecomd_v1_m1_stationarity_screen":
        raise ValueError("unexpected M1 contract name")
    if contract.get("version") != 1 or contract.get("status") != "frozen_before_checkpoint_or_rollout":
        raise ValueError("M1 contract version/status is not frozen v1")
    m0_path = repo_root / str(contract["m0_config_path"])
    if sha256_file(m0_path) != contract.get("m0_config_sha256"):
        raise ValueError("M0 config hash does not match the M1 protocol")
    if contract.get("expected_parameter_count") != 36_541:
        raise ValueError("M1 expected parameter count must be 36541")

    data = _mapping(config, "data")
    expected_data = {
        "dataset_id": "ecomd_v1_m1_spx_yahoo_daily_2015_2024",
        "manifest_path": "data/manifests/ecomd_v1_m1_spx_4a2332d62.json",
        "manifest_sha256": "0836ddd279a16db5010907120e65da87db58a2f2634c25f0e732334a98ffff7c",
        "target_symbol": "^GSPC",
        "target_period": "2015-2018_daily",
        "price_column": "adjusted_close",
        "preprocessing": "numpy.diff(numpy.log(adjusted_close_float64))",
        "validation": "2019_daily_report_only",
        "sealed_crash_test": "2020_daily_no_training_selection_or_protocol_change",
        "temporal_test": "2021-2024_daily",
    }
    if dict(data) != expected_data:
        raise ValueError("M1 data protocol changed")

    training = _mapping(config, "training")
    expected_training = {
        "seed": 0,
        "precision": "fp32",
        "first_segment_stop_after_iter": 300,
        "final_iter": 600,
        "resume_required": True,
        "early_stopping": False,
        "reference_host": "v100_a",
    }
    if dict(training) != expected_training:
        raise ValueError("M1 training protocol changed")

    rollout = _mapping(config, "rollout")
    calibration = tuple(int(seed) for seed in rollout["calibration_seeds"])
    heldout = tuple(int(seed) for seed in rollout["heldout_seeds"])
    if calibration != tuple(range(811000, 811016)):
        raise ValueError("M1 calibration seeds changed")
    if heldout != tuple(range(811100, 811116)):
        raise ValueError("M1 held-out seeds changed")
    if set(calibration) & set(heldout):
        raise ValueError("M1 calibration and held-out seeds overlap")
    if rollout.get("usable_returns") != 8000 or rollout.get("simulator_steps") != 8001:
        raise ValueError("M1 rollout horizon changed")
    if rollout.get("ordering_rule") != "calibration_only_then_frozen_gate_commit_then_heldout":
        raise ValueError("M1 held-out ordering rule changed")
    if rollout.get("shocks_or_inference_overrides") != "forbidden":
        raise ValueError("M1 inference overrides must be forbidden")
    _validate_node_shards(_mapping(rollout, "node_shards"), calibration, heldout)

    energy_payload = dict(_mapping(config, "energy_gate"))
    energy_hash = str(energy_payload.pop("implementation_sha256"))
    energy = GateConfig(
        block_length=int(energy_payload["block_length"]),
        gate_starts=tuple(int(value) for value in energy_payload["gate_starts"]),
        late_starts=tuple(int(value) for value in energy_payload["late_starts"]),
        max_w_star=int(energy_payload["max_w_star"]),
        persistence_blocks=int(energy_payload["persistence_blocks"]),
        tolerance_quantile=float(energy_payload["tolerance_quantile"]),
        bootstrap_replicates=int(energy_payload["bootstrap_replicates"]),
        bootstrap_seed=int(energy_payload["bootstrap_seed"]),
        mad_floor=float(energy_payload["mad_floor"]),
    )
    expected_energy = GateConfig(bootstrap_seed=811900)
    if energy != expected_energy:
        raise ValueError("M1 energy gate changed")
    if sha256_file(repo_root / "ecomd/eval/stationarity_gate.py") != energy_hash:
        raise ValueError("M1 energy-gate implementation hash changed")

    adf_payload = dict(_mapping(config, "adf_kpss_comparator"))
    adf_hash = str(adf_payload.pop("implementation_sha256"))
    adf = ADFKPSSConfig(
        block_length=int(adf_payload["block_length"]),
        gate_starts=tuple(int(value) for value in adf_payload["gate_starts"]),
        max_w_star=int(adf_payload["max_w_star"]),
        persistence_blocks=int(adf_payload["persistence_blocks"]),
        trajectory_pass_fraction=float(adf_payload["trajectory_pass_fraction"]),
        adf_alpha=float(adf_payload["adf_alpha"]),
        kpss_alpha=float(adf_payload["kpss_alpha"]),
        adf_maxlag=int(adf_payload["adf_maxlag"]),
    )
    if adf != ADFKPSSConfig():
        raise ValueError("M1 ADF/KPSS comparator changed")
    if sha256_file(repo_root / "ecomd/eval/stationarity_baselines.py") != adf_hash:
        raise ValueError("M1 ADF/KPSS implementation hash changed")

    scoring = _mapping(config, "scoring")
    expected_starts = (0, 50, 100, 200, 500, 1000, 1500, 2000, 3000, 4000)
    if tuple(int(value) for value in scoring["starts"]) != expected_starts:
        raise ValueError("M1 scoring grid changed")
    if scoring.get("fixed_length") != 4000 or scoring.get("fact_count") != 11:
        raise ValueError("M1 fixed scoring dimensions changed")
    bands_hash = str(scoring["canonical_bands_sha256"])
    if sha256_file(repo_root / "ecomd/eval/canonical_bands.py") != bands_hash:
        raise ValueError("M1 canonical-band implementation hash changed")
    if scoring.get("aggregate_across_heldout") != "per_fact_median_then_band_score":
        raise ValueError("M1 held-out aggregation changed")
    if scoring.get("all_starts_reported") is not True:
        raise ValueError("M1 must report every scoring start")

    decision = _mapping(config, "decision")
    authorization = _mapping(decision, "authorize_multiseed_baselines_and_cross_market_if")
    if decision.get("stop_positive_model_paper_if_post_or_late_pass_count_at_most") != 2:
        raise ValueError("M1 hard scientific stop changed")
    if decision.get("diagnostic_only_if_post_or_late_pass_count_in") != [3, 4]:
        raise ValueError("M1 diagnostic-only tier changed")
    if dict(authorization) != {
        "minimum_post_w_star_pass_count": 5,
        "minimum_late_w4000_pass_count": 5,
        "maximum_late_to_post_mean_normalized_distance_ratio": 1.10,
    }:
        raise ValueError("M1 continuation gate changed")
    if decision.get("authorization_is_not_a_paper_claim") is not True:
        raise ValueError("M1 authorization must not be treated as a paper claim")

    compute = _mapping(config, "compute")
    if compute.get("allowed_gpu_family") != "v100_32gb" or compute.get("h20_forbidden") is not True:
        raise ValueError("M1 hardware contract changed")


def load_and_validate_m1_protocol(path: Path, repo_root: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError("M1 protocol must be a YAML mapping")
    validate_m1_protocol(payload, repo_root)
    return payload


def _validate_node_shards(
    shards: Mapping[str, Any],
    calibration: tuple[int, ...],
    heldout: tuple[int, ...],
) -> None:
    if set(shards) != {"v100_a", "v100_b"}:
        raise ValueError("M1 node shard names changed")
    for split, expected in (("calibration", calibration), ("heldout", heldout)):
        assigned: list[int] = []
        for node in ("v100_a", "v100_b"):
            node_payload = _mapping(shards, node)
            assigned.extend(int(seed) for seed in node_payload[split])
        if sorted(assigned) != list(expected) or len(set(assigned)) != len(expected):
            raise ValueError(f"M1 {split} node shards do not partition the frozen seeds")


__all__ = ["load_and_validate_m1_protocol", "validate_m1_protocol"]
