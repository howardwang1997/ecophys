"""Run the frozen source-bound Morpho Public Allocator pressure T0."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from ecomd.physics.public_allocator_pressure import (
    apply_flow_cap_reallocation,
    displaced_pressure_fraction,
    independent_vault_target_capacity,
    pure_routing_pressure_changes,
    routed_borrow_pressure_changes,
    target_inflow_capacity,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def _load_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("T0 config must be an object")
    return payload


def _verify_sources(
    config: Mapping[str, Any],
    *,
    public_allocator_root: Path,
    irm_root: Path,
) -> dict[str, Any]:
    audit = config["source_audit"]
    allocator = audit["public_allocator"]
    irm = audit["adaptive_curve_irm"]
    if _git(public_allocator_root, "status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("Public Allocator source worktree is dirty")
    if _git(irm_root, "status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("AdaptiveCurveIRM source worktree is dirty")
    if _git(public_allocator_root, "rev-parse", "HEAD") != allocator["expected_git_sha"]:
        raise RuntimeError("Public Allocator source commit mismatch")
    if _git(irm_root, "rev-parse", "HEAD") != irm["expected_git_sha"]:
        raise RuntimeError("AdaptiveCurveIRM source commit mismatch")
    observed_hashes: dict[str, str] = {}
    for relative, expected in allocator["file_sha256"].items():
        observed = _hash(public_allocator_root / relative)
        if observed != expected:
            raise RuntimeError(f"Public Allocator source hash mismatch: {relative}")
        observed_hashes[str(relative)] = observed

    constants_path = irm_root / "src/adaptive-curve-irm/libraries/ConstantsLib.sol"
    constants_source = constants_path.read_text(encoding="utf-8")
    if "TARGET_UTILIZATION = 0.9 ether" not in constants_source:
        raise RuntimeError("frozen 90% target is absent from AdaptiveCurveIRM source")
    contract_source = (public_allocator_root / "src/PublicAllocator.sol").read_text(encoding="utf-8")
    required_fragments = (
        "flowCaps[vault][id].maxIn += withdrawnAssets",
        "flowCaps[vault][id].maxOut -= withdrawnAssets",
        "flowCaps[vault][supplyMarketId].maxIn -= totalWithdrawn",
        "flowCaps[vault][supplyMarketId].maxOut += totalWithdrawn",
    )
    if any(fragment not in contract_source for fragment in required_fragments):
        raise RuntimeError("Public Allocator cap transitions differ from the frozen identity")
    return {
        "public_allocator": {
            "git_sha": allocator["expected_git_sha"],
            "file_sha256": observed_hashes,
        },
        "adaptive_curve_irm": {
            "git_sha": irm["expected_git_sha"],
            "constants_sha256": _hash(constants_path),
            "target_utilization": float(irm["target_utilization"]),
        },
    }


def _greedy_flows(capacities: np.ndarray, target: float) -> np.ndarray:
    remaining = target
    flows = np.zeros_like(capacities)
    for index, capacity in enumerate(capacities):
        amount = min(float(capacity), remaining)
        flows[index] = amount
        remaining -= amount
    if remaining > 1e-9 * max(1.0, target):
        raise RuntimeError("greedy construction failed to attain feasible target")
    return flows


def run_probe(
    config_path: Path,
    output_path: Path,
    *,
    public_allocator_root: Path,
    irm_root: Path,
) -> dict[str, Any]:
    """Execute the frozen T0 and write an immutable result artifact."""
    config = _load_config(config_path)
    contract = config["contract"]
    if contract["status"] != "frozen_before_synthetic_trials_or_market_history":
        raise ValueError("T0 contract is not frozen")
    if _git(REPO_ROOT, "status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("formal T0 requires a clean worktree")
    source_audit = _verify_sources(
        config,
        public_allocator_root=public_allocator_root,
        irm_root=irm_root,
    )

    simulation = config["simulation"]
    rng = np.random.default_rng(int(simulation["seed"]))
    trials = int(simulation["trials"])
    target_utilization = float(config["source_audit"]["adaptive_curve_irm"]["target_utilization"])
    tolerance = float(simulation["tolerance"])
    metrics = {
        "max_pressure_continuity_residual": 0.0,
        "max_network_source_residual": 0.0,
        "max_partition_residual": 0.0,
        "max_full_jit_fraction_residual": 0.0,
        "max_flow_cap_invariant_residual": 0.0,
        "max_capacity_bound_residual": 0.0,
        "minimum_touched_jit_pressure": float("inf"),
    }

    for _ in range(trials):
        donor_count = int(
            rng.integers(int(simulation["minimum_donors"]), int(simulation["maximum_donors"]) + 1)
        )
        flows = rng.uniform(1e-3, 1e6, size=donor_count)
        routed = float(np.sum(flows, dtype=np.float64))
        borrow = routed + float(rng.uniform(0.0, 1e6))

        pure = pure_routing_pressure_changes(flows, target_utilization=target_utilization)
        jit = routed_borrow_pressure_changes(
            flows,
            borrow,
            target_utilization=target_utilization,
        )
        metrics["max_pressure_continuity_residual"] = max(
            metrics["max_pressure_continuity_residual"], abs(float(np.sum(pure))) / max(1.0, routed)
        )
        metrics["max_network_source_residual"] = max(
            metrics["max_network_source_residual"],
            abs(float(np.sum(jit)) - borrow) / max(1.0, borrow),
        )
        expected_donor = target_utilization * routed
        partition_residual = max(
            abs(float(np.sum(jit[:-1])) - expected_donor),
            abs(float(jit[-1]) - (borrow - expected_donor)),
        ) / max(1.0, borrow)
        metrics["max_partition_residual"] = max(metrics["max_partition_residual"], partition_residual)
        metrics["minimum_touched_jit_pressure"] = min(
            metrics["minimum_touched_jit_pressure"], float(np.min(jit))
        )
        full_fraction = displaced_pressure_fraction(
            routed,
            routed,
            target_utilization=target_utilization,
        )
        metrics["max_full_jit_fraction_residual"] = max(
            metrics["max_full_jit_fraction_residual"], abs(full_fraction - target_utilization)
        )

        market_count = donor_count + 1
        target_index = donor_count
        max_out = np.concatenate((flows + rng.uniform(0.0, 1e6, donor_count), np.array([0.0])))
        max_in = rng.uniform(0.0, 1e6, market_count)
        max_in[target_index] = routed + float(rng.uniform(0.0, 1e6))
        cap_flows = np.concatenate((flows, np.array([0.0])))
        before_budget = max_in + max_out
        new_in, new_out = apply_flow_cap_reallocation(
            max_in,
            max_out,
            cap_flows,
            target_index=target_index,
        )
        cap_scale = max(1.0, float(np.max(before_budget)))
        metrics["max_flow_cap_invariant_residual"] = max(
            metrics["max_flow_cap_invariant_residual"],
            float(np.max(np.abs(new_in + new_out - before_budget))) / cap_scale,
        )

        donor_max_out = rng.uniform(0.0, 1e6, donor_count)
        donor_supply = rng.uniform(0.0, 1e6, donor_count)
        target_max_in = float(rng.uniform(0.0, 1e6))
        capacity = target_inflow_capacity(target_max_in, donor_max_out, donor_supply)
        attainable = _greedy_flows(np.minimum(donor_max_out, donor_supply), capacity)
        capacity_residual = abs(float(np.sum(attainable)) - capacity) / max(1.0, capacity)

        vault_count = int(
            rng.integers(int(simulation["minimum_vaults"]), int(simulation["maximum_vaults"]) + 1)
        )
        vault_target_caps = rng.uniform(0.0, 1e6, vault_count)
        vault_donor_out = rng.uniform(0.0, 1e6, size=(vault_count, donor_count))
        vault_donor_supply = rng.uniform(0.0, 1e6, size=(vault_count, donor_count))
        aggregate = independent_vault_target_capacity(
            vault_target_caps,
            vault_donor_out,
            vault_donor_supply,
        )
        explicit = float(
            np.sum(
                np.minimum(
                    vault_target_caps,
                    np.sum(np.minimum(vault_donor_out, vault_donor_supply), axis=1),
                )
            )
        )
        capacity_residual = max(
            capacity_residual,
            abs(aggregate - explicit) / max(1.0, explicit),
        )
        metrics["max_capacity_bound_residual"] = max(
            metrics["max_capacity_bound_residual"], capacity_residual
        )

    frozen_gates = config["gates"]
    gates = {
        "pressure_continuity": metrics["max_pressure_continuity_residual"]
        <= float(frozen_gates["maximum_pressure_continuity_residual"]),
        "network_source": metrics["max_network_source_residual"]
        <= float(frozen_gates["maximum_network_source_residual"]),
        "pressure_partition": metrics["max_partition_residual"]
        <= float(frozen_gates["maximum_partition_residual"]),
        "full_jit_fraction": metrics["max_full_jit_fraction_residual"]
        <= float(frozen_gates["maximum_full_jit_fraction_residual"]),
        "flow_cap_invariant": metrics["max_flow_cap_invariant_residual"]
        <= float(frozen_gates["maximum_flow_cap_invariant_residual"]),
        "capacity_bound": metrics["max_capacity_bound_residual"]
        <= float(frozen_gates["maximum_capacity_bound_residual"]),
        "nonnegative_jit_pressure": metrics["minimum_touched_jit_pressure"] >= -tolerance,
    }
    body: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": "morpho_public_allocator_pressure_t0_v1",
        "created_utc": datetime.now(UTC).isoformat(),
        "repository": {
            "git_sha": _git(REPO_ROOT, "rev-parse", "HEAD"),
            "worktree_clean": True,
        },
        "config": {
            "path": str(config_path.relative_to(REPO_ROOT)),
            "sha256": _hash(config_path),
            "seed": int(simulation["seed"]),
        },
        "source_audit": source_audit,
        "metrics": {**metrics, "trials": trials},
        "gates": gates,
        "math_checks_pass": all(gates.values()),
        "scientific_decision": (
            "math_encoding_pass_novelty_and_field_support_remain_amber"
            if all(gates.values())
            else "math_encoding_fail_stop_route"
        ),
        "data_contract": {
            "used": list(config["allowed_data"]),
            "forbidden_untouched": list(config["forbidden_data"]),
            "gpu_used": False,
        },
        "claim_limit": (
            "Passing verifies source-bound algebra only; it does not establish novelty, field prevalence, "
            "causality, incident prediction, NMI fit, or NCS fit."
        ),
    }
    body["canonical_payload_sha256"] = _canonical_sha256(body)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return body


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "configs/empirical_physics/morpho_public_allocator_pressure_t0_v1.yaml",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "results/empirical_physics/morpho_public_allocator_pressure_t0_v1.json",
    )
    parser.add_argument("--public-allocator-root", type=Path, required=True)
    parser.add_argument("--irm-root", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = run_probe(
        args.config.resolve(),
        args.output.resolve(),
        public_allocator_root=args.public_allocator_root.resolve(),
        irm_root=args.irm_root.resolve(),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
