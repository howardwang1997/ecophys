"""Prospectively bounded model audit, learning extension and feasible probing."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import time
from typing import Any

from hydra import compose, initialize_config_dir
import numpy as np
from omegaconf import OmegaConf

from .model import ACTIONS, Action, Law, Market, State, TabularModel
from .run import run_job


def probe_action(inventory: int) -> Action:
    if inventory == 1:
        return Action(0, 98, 102)
    if inventory == 0:
        return Action(0, 99, 0)
    if inventory == 2:
        return Action(0, 0, 101)
    raise ValueError("probe policy is restricted to inventory 0,1,2")


def expected_probe_cycle(law: Law) -> float:
    p, b, s = law.values()
    if not 0 < p < 1:
        raise ValueError("two-sided arrivals required")
    return 1+p*b/(1-p)+(1-p)*s/p


def audit(config: dict[str, Any], output: Path) -> dict[str, Any]:
    start = time.perf_counter()
    rows = []
    for name, parameters in config["laws"].items():
        law = Law(**parameters)
        for capacity in config["capacities"]:
            for rho in config["refill_probabilities"]:
                model = TabularModel(capacity, rho)
                values, policy = model.solve(law, config["audit_horizon"])
                idx = model.index[State(config["initial_inventory"], 1, 1)]
                transitions, _ = model.kernel(law)
                distribution = np.zeros(len(model.states))
                distribution[idx] = 1
                hedges = 0.0
                for remaining in range(config["audit_horizon"], 0, -1):
                    chosen = policy[remaining]
                    hedges += float(distribution @ np.array([abs(ACTIONS[int(j)].hedge) for j in chosen]))
                    distribution = distribution @ transitions[np.arange(len(model.states)), chosen]
                model.legal[:, [j for j, a in enumerate(ACTIONS) if a.hedge != 0]] = False
                restricted, _ = model.solve(law, config["audit_horizon"])
                rows.append({"law": name, "capacity": capacity, "rho": rho,
                             "value": float(values[-1, idx]), "no_hedge_value": float(restricted[-1, idx]),
                             "hedge_value_per_round": float((values[-1, idx]-restricted[-1, idx])/config["audit_horizon"]),
                             "expected_oracle_hedges": hedges,
                             "values_by_horizon": {str(h): float(values[h, idx]) for h in config["learning_horizons"]}})
    binding = []
    for capacity in config["capacities"]:
        selected = {r["rho"]: r for r in rows if r["law"] == config["learning_law"] and r["capacity"] == capacity}
        gain = (selected[1.0]["value"]-selected[0.1]["value"])/config["audit_horizon"]
        binding.append({"capacity": capacity, "availability_value_per_round": gain})
    result = {"evidence_label": "development_not_confirmation", "rows": rows, "binding": binding,
              "learning_gate_pass": any(r["availability_value_per_round"] > config["binding_value_per_round_threshold"] for r in binding),
              "wall_seconds": time.perf_counter()-start}
    (output / "audit.json").write_text(json.dumps(result, indent=2)+"\n")
    return result


def probe(config: dict[str, Any], output: Path) -> dict[str, Any]:
    start = time.perf_counter()
    rows = []
    for name, parameters in config["laws"].items():
        law = Law(**parameters)
        for seed in range(config["probe_seed_start"], config["probe_seed_start"]+config["probe_seed_count"]):
            innovations = np.random.default_rng(np.random.SeedSequence([seed, 23])).random((config["probe_horizon"], 5))
            paired_signatures = []
            for rho in config["probe_refill_probabilities"]:
                market = Market(2, config["probe_horizon"])
                market.state = State(1, *config["probe_initial_depths"])
                samples, cycles, elapsed, buy_samples, high_buy_samples, low_sell_samples = 0, [], 0, 0, 0, 0
                signature = hashlib.sha256()
                for u in innovations:
                    state = market.state
                    action = probe_action(state.inventory)
                    buy = bool(u[0] < law.buy_probability)
                    value = (102 if u[1] < law.buyer_high_probability else 101) if buy else (98 if u[2] < law.seller_low_probability else 99)
                    event = market.step(action, buy, value, bool(u[3] < rho), bool(u[4] < rho), False)
                    if state.inventory == 1:
                        decoded = (102 if event.feedback.filled else 101) if buy else (98 if event.feedback.filled else 99)
                        if decoded != value:
                            raise AssertionError("actual feedback did not identify probe type")
                        samples += 1
                        buy_samples += int(buy)
                        high_buy_samples += int(buy and decoded == 102)
                        low_sell_samples += int(not buy and decoded == 98)
                    elapsed += 1
                    if event.state.inventory == 1:
                        cycles.append(elapsed)
                        elapsed = 0
                    signature.update(bytes([state.inventory, action.bid, action.ask, int(buy), int(event.feedback.filled), event.state.inventory]))
                paired_signatures.append(signature.hexdigest())
                rows.append({"law": name, "rho": rho, "seed": seed, "horizon": config["probe_horizon"],
                             "samples": samples, "completed_cycles": len(cycles), "censored_cycle_elapsed": elapsed,
                             "cycle_sum": sum(cycles), "probe_rate": samples/config["probe_horizon"],
                             "predicted_cycle_length": expected_probe_cycle(law),
                             "predicted_probe_rate": 1/expected_probe_cycle(law),
                             "buy_samples": buy_samples, "high_buy_samples": high_buy_samples, "low_sell_samples": low_sell_samples,
                             "hedges": 0, "inventory_signature": signature.hexdigest(), "violations": 0})
            if len(set(paired_signatures)) != 1:
                raise AssertionError("rho changed a policy that never hedges")
    result = {"evidence_label": "development_not_confirmation", "rows": rows, "wall_seconds": time.perf_counter()-start}
    (output / "probe.json").write_text(json.dumps(result, indent=2)+"\n")
    return result


def learn(config: dict[str, Any], output: Path, audit_path: Path) -> dict[str, Any]:
    audit_result = json.loads(audit_path.read_text())
    if not audit_result["learning_gate_pass"]:
        raise ValueError("prospective binding-value gate failed")
    start = time.perf_counter()
    jobs = []
    for capacity in config["capacities"]:
        for horizon in config["learning_horizons"]:
            directory = output / f"Q{capacity}_T{horizon}"
            directory.mkdir()
            cfg = {**config, "capacity": capacity, "horizon": horizon, "law": config["laws"][config["learning_law"]]}
            for rho in config["refill_probabilities"]:
                oracle = next(r for r in audit_result["rows"] if r["law"] == config["learning_law"] and r["capacity"] == capacity and r["rho"] == rho)
                for seed in config["learning_seeds"]:
                    for method in config["methods"]:
                        for feedback in config["feedback"]:
                            jobs.append(dict(config=cfg, output=str(directory), seed=seed, method=method, feedback=feedback,
                                             rho=rho, oracle_value=oracle["values_by_horizon"][str(horizon)]))
    rows = []
    with ProcessPoolExecutor(max_workers=config["max_workers"]) as pool:
        futures = {pool.submit(run_job, job): job for job in jobs}
        for future in as_completed(futures, timeout=config["max_wall_seconds"]):
            row = future.result()
            row["capacity"] = futures[future]["config"]["capacity"]
            row["law"] = config["learning_law"]
            rows.append(row)
            if len(rows) % 16 == 0 or len(rows) == len(jobs):
                print(json.dumps({"complete": len(rows), "total": len(jobs), "elapsed_s": round(time.perf_counter()-start, 2)}), flush=True)
    result = {"evidence_label": "development_not_confirmation", "rows": rows,
              "audit_input_sha256": hashlib.sha256(audit_path.read_bytes()).hexdigest(),
              "wall_seconds": time.perf_counter()-start, "job_cpu_seconds": sum(r["cpu_seconds"] for r in rows)}
    (output / "learning.json").write_text(json.dumps(result, indent=2)+"\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["audit", "probe", "learn"])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    for name, digest in manifest["files"].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"immutable source mismatch: {name}")
    with initialize_config_dir(config_dir=str(args.config.resolve().parent), version_base=None):
        obj = OmegaConf.to_container(compose(config_name=args.config.stem), resolve=True)
    if not isinstance(obj, dict):
        raise ValueError("mapping required")
    config: dict[str, Any] = {str(k): v for k, v in obj.items()}
    if config["evidence_label"] != "development_not_confirmation" or any(not 750000 <= s <= 750015 for s in config["learning_seeds"]):
        raise ValueError("invalid development partition")
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "input_manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    (args.output / "config.yaml").write_bytes(args.config.read_bytes())
    if args.phase == "audit":
        result = audit(config, args.output)
        print(json.dumps(result, indent=2), flush=True)
    elif args.phase == "probe":
        result = probe(config, args.output)
        print(json.dumps({"rows": len(result["rows"]), "wall_seconds": result["wall_seconds"]}), flush=True)
    else:
        if args.audit is None:
            raise ValueError("audit required")
        result = learn(config, args.output, args.audit)
    paths = [p for p in args.output.rglob("*") if p.is_file()]
    if sum(p.stat().st_size for p in paths) > config["max_output_bytes"]:
        raise RuntimeError("output budget exceeded")
    receipts = {str(p.relative_to(args.output)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (args.output / "receipt_sha256.json").write_text(json.dumps(receipts, indent=2)+"\n")
    (args.output / "COMPLETE").write_text(f"{args.phase} complete\n")


if __name__ == "__main__":
    main()
