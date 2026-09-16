"""Private DX image entry point. Do not invoke outside an authorized OCI branch."""

from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import tarfile
import time
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from .model import (
    Dynamics,
    Network,
    build_examples,
    forecast_nrmse,
    observation_indices,
    pulse,
    reference_check,
    rollout,
    unit_state,
)


def digest_array(value: np.ndarray[Any, Any]) -> str:
    return hashlib.sha256(np.asarray(value, dtype="<f8").tobytes()).hexdigest()


def execute(config: dict[str, Any]) -> dict[str, Any]:
    if config.get("epistemic_class") != "sandbox_exploratory_tainted":
        raise ValueError("missing exploratory label")
    groups = config["groups"]
    units = sorted(u for group in groups.values() for u in group)
    if units != sorted(config["unit_ids"]) or len(set(units)) != 192:
        raise ValueError("exploration membership mismatch")
    if [len(groups[k]) for k in ("train", "diagnostic", "response")] != [128, 32, 32]:
        raise ValueError("incorrect split size")
    dynamics = Dynamics(**config["dynamics"])
    report: dict[str, Any] = {"branch_id": config["branch_id"], "epistemic_class": config["epistemic_class"]}
    cpu_start = time.process_time()
    if config["qualify_reference"]:
        report["reference_check"] = reference_check(groups, dynamics)
    report["reference_check_cpu_seconds"] = time.process_time() - cpu_start if config["qualify_reference"] else 0.0
    if report["reference_check_cpu_seconds"] > config["reference_cpu_reservation"]:
        raise RuntimeError("reference-check reservation exceeded")
    fit_start = time.process_time()
    trajectories = {name: np.stack([dynamics.trajectory(unit_state(u, dynamics), 40) for u in ids])
                    for name, ids in groups.items()}
    observed = config["observed_modes"]
    idx = observation_indices(dynamics.modes, observed)
    train = trajectories["train"]
    mean = train[:, :, idx].mean(axis=(0, 1))
    scale = np.maximum(train[:, :, idx].std(axis=(0, 1)), 1e-8)
    histories, targets = build_examples(train, config["augmented"], dynamics)
    histories, targets = histories[:, :, idx], targets[:, idx]
    frames = config["frames"]
    inputs = ((histories[:, -frames:] - mean) / scale).reshape(4000, -1)
    increments = (targets - histories[:, -1]) / scale
    report["generation_cpu_seconds"] = time.process_time() - fit_start
    report["data_hashes"] = {k: digest_array(v) for k, v in trajectories.items()}
    report["data_hashes"].update({"train_inputs": digest_array(inputs), "train_targets": digest_array(increments)})
    network = Network(inputs.shape[1], len(idx), config["width"], config["initialization_seed"])
    report["parameter_count"] = sum(p.size for p in network.parameters)
    train_start = time.process_time()
    report["training"] = network.fit(inputs, increments, **config["optimizer"])
    report["training_cpu_seconds"] = time.process_time() - train_start
    diagnostics = trajectories["diagnostic"][:, :, idx]
    forecast = rollout(network, diagnostics[:, 12:16], mean, scale, frames)
    report["forecast_nrmse"] = forecast_nrmse(forecast, diagnostics[:, 16:21])
    response = trajectories["response"]
    history = response[:, 12:16, :][:, :, idx]
    sham = rollout(network, history, mean, scale, frames)
    report["sham_forecast_nrmse"] = forecast_nrmse(sham, response[:, 16:21, :][:, :, idx])
    report["contrasts"] = []
    for k in (1, 4):
        for a in (.02, .04):
            truth_pair, model_pair = [], []
            for sign in (-1, 1):
                future = np.stack([dynamics.trajectory(pulse(t[15], k, sign * a), 5) for t in response])
                changed_history = history.copy()
                changed_history[:, -1, k - 1] += sign * a
                predicted = rollout(network, changed_history, mean, scale, frames)
                truth_pair.append(future[:, -1, k - 1])
                model_pair.append(predicted[:, -1, k - 1])
            truth_units = (truth_pair[1] - truth_pair[0]) / (2 * a)
            model_units = (model_pair[1] - model_pair[0]) / (2 * a)
            truth_mean, model_mean = float(truth_units.mean()), float(model_units.mean())
            report["contrasts"].append({
                "mode": k, "amplitude": a, "reference_response": truth_mean,
                "model_response": model_mean,
                "normalized_mean_error": abs(model_mean - truth_mean) / max(abs(truth_mean), .1),
                "per_unit_response_rmse": float(np.sqrt(np.mean((model_units - truth_units) ** 2))),
                "reference_units": truth_units.tolist(), "model_units": model_units.tolist(),
            })
    report["fit_and_evaluation_cpu_seconds"] = time.process_time() - fit_start
    if report["fit_and_evaluation_cpu_seconds"] > config["fit_cpu_reservation"]:
        raise RuntimeError("fit/evaluation reservation exceeded")
    report["cpu_seconds"] = time.process_time() - cpu_start
    # JSON forbids non-finite values so no unusable scientific report can be accepted.
    json.dumps(report, allow_nan=False)
    return report


def load_config(path: Path) -> dict[str, Any]:
    raw = path.read_text()
    try:
        config = json.loads(raw)
    except json.JSONDecodeError:
        config = yaml.safe_load(raw)
    if not isinstance(config, dict):
        raise ValueError("configuration must be a mapping")
    return config


def main() -> None:
    if not os.environ.get("ECOMD_DX_SANDBOX_ID") or not os.environ.get("ECOMD_DX_BRANCH_ID"):
        raise RuntimeError("use the governed OCI launcher")
    config_path = Path(os.environ["ECOMD_DX_CONFIG"])
    config = load_config(config_path)
    if config.get("mode") in {"normal", "sleep", "invalid_tar"} and "unit_ids" not in config:
        from .oci_probe import main as probe_main

        raise SystemExit(probe_main())
    if config["branch_id"] != os.environ["ECOMD_DX_BRANCH_ID"]:
        raise ValueError("runtime branch identity mismatch")
    report = execute(config)
    data = json.dumps(report, sort_keys=True, allow_nan=False).encode()
    with tarfile.open(fileobj=sys.stdout.buffer, mode="w|") as archive:
        member = tarfile.TarInfo("exploratory_response.json")
        member.size = len(data)
        member.mode = 0o444
        member.mtime = 0
        archive.addfile(member, io.BytesIO(data))


if __name__ == "__main__":
    main()
