"""Bounded development run with immutable inputs and per-replicate receipts."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import time
from typing import Any

import numpy as np
from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf

from .learning import Belief
from .model import ACTIONS, Law, Market, State, TabularModel


def run_job(job: dict[str, Any]) -> dict[str, Any]:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    consumed = usage.ru_utime + usage.ru_stime
    resource.setrlimit(resource.RLIMIT_CPU, (math.ceil(consumed)+120, 7200))
    resource.setrlimit(resource.RLIMIT_AS, (6*1024**3, 6*1024**3))
    start, cpu_start = time.perf_counter(), time.process_time()
    cfg = job["config"]
    horizon, seed, rho = int(cfg["horizon"]), int(job["seed"]), float(job["rho"])
    method, reveal = str(job["method"]), job["feedback"] == "reveal"
    identifier = f'{method}_{job["feedback"]}_rho{rho}_seed{seed}'
    path = Path(job["output"])
    law = Law(**cfg["law"])
    model = TabularModel(int(cfg["capacity"]), rho)
    market = Market(int(cfg["capacity"]), horizon, int(cfg["initial_inventory"]))
    innovations = np.random.default_rng(np.random.SeedSequence([seed, 0])).random((horizon, 5))
    rng = np.random.default_rng(np.random.SeedSequence([seed, 1, 0 if method == "certainty_equivalent" else 1]))
    belief = Belief(float(cfg["prior_success"]), float(cfg["prior_failure"]))
    planning_seconds = 0.0
    policy = np.zeros((1, 1), dtype=np.uint8)
    rows: list[list[Any]] = []
    boundaries, hedge_count, fills, informative_buy, informative_sell = 0, 0, 0, 0, 0
    for t in range(horizon):
        if t == 0 or (t & (t-1)) == 0:
            plan_start = time.perf_counter()
            estimate = belief.mean() if method == "certainty_equivalent" else belief.sample(rng)
            _, policy = model.solve(estimate, horizon-t)
            planning_seconds += time.perf_counter()-plan_start
        state = market.state
        idx = model.index[state]
        action_index = int(policy[horizon-t, idx])
        if method == "certainty_equivalent" and rng.random() < min(1, float(cfg["exploration_scale"])/math.sqrt(t+1)):
            action_index = int(rng.choice(np.flatnonzero(model.legal[idx])))
        action = ACTIONS[action_index]
        u = innovations[t]
        buy = bool(u[0] < law.buy_probability)
        value = (102 if u[1] < law.buyer_high_probability else 101) if buy else (98 if u[2] < law.seller_low_probability else 99)
        result = market.step(action, buy, value, bool(u[3] < rho), bool(u[4] < rho), reveal)
        old_counts = belief.counts.copy()
        belief.update(action, result.feedback)
        informative_buy += int(belief.counts[1].sum() > old_counts[1].sum())
        informative_sell += int(belief.counts[2].sum() > old_counts[2].sum())
        boundaries += int(state.inventory in (0, cfg["capacity"]))
        hedge_count += abs(action.hedge)
        fills += int(result.feedback.filled)
        rows.append([t, state.inventory, state.bid_depth, state.ask_depth, action.hedge,
                     action.bid, action.ask, int(buy), value, int(result.feedback.filled),
                     result.state.inventory, result.state.bid_depth, result.state.ask_depth,
                     result.reward, market.cash[0]])
    with gzip.open(path / (identifier+".csv.gz"), "wt", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["t", "q", "bid_depth", "ask_depth", "hedge", "bid", "ask", "customer_buy",
                         "audit_willingness", "filled", "next_q", "next_bid_depth", "next_ask_depth", "reward", "cash"])
        writer.writerows(rows)
    result_row = {
        "id": identifier, "seed": seed, "rho": rho, "feedback": job["feedback"], "method": method,
        "horizon": horizon, "wealth": market.wealth(), "oracle_value": job["oracle_value"],
        "regret": job["oracle_value"]-market.wealth(), "regret_per_round": (job["oracle_value"]-market.wealth())/horizon,
        "boundary_fraction": boundaries/horizon, "hedges": hedge_count, "fills": fills,
        "informative_buy_observations": informative_buy, "informative_sell_observations": informative_sell,
        "posterior_mean": belief.mean().values(), "posterior_counts": belief.counts.tolist(),
        "wall_seconds": time.perf_counter()-start, "cpu_seconds": time.process_time()-cpu_start,
        "planning_seconds": planning_seconds, "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "violations": 0, "evidence_label": "development_not_confirmation", "wandb_url": None,
    }
    (path / (identifier+".json")).write_text(json.dumps(result_row, indent=2)+"\n")
    return result_row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    for relative, expected in manifest["files"].items():
        if hashlib.sha256(Path(relative).read_bytes()).hexdigest() != expected:
            raise ValueError(f"source/config hash mismatch: {relative}")
    with initialize_config_dir(config_dir=str(args.config.resolve().parent), version_base=None):
        config_object = OmegaConf.to_container(compose(config_name=args.config.stem), resolve=True)
    if not isinstance(config_object, dict):
        raise ValueError("mapping config required")
    config: dict[str, Any] = {str(k): v for k, v in config_object.items()}
    if config["evidence_label"] != "development_not_confirmation" or any(not 710000 <= s <= 710007 for s in config["seeds"]):
        raise ValueError("outside authorized development partition")
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "input_manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    (args.output / "config.yaml").write_bytes(args.config.read_bytes())
    start = time.perf_counter()
    oracles = {}
    for rho in config["refill_probabilities"]:
        model = TabularModel(config["capacity"], rho)
        values, _ = model.solve(Law(**config["law"]), config["horizon"])
        oracles[str(rho)] = float(values[-1, model.index[State(config["initial_inventory"], 1, 1)]])
    (args.output / "oracle_values.json").write_text(json.dumps(oracles, indent=2)+"\n")
    jobs = [dict(config=config, output=str(args.output), seed=seed, rho=rho, feedback=feedback, method=method, oracle_value=oracles[str(rho)])
            for seed in config["seeds"] for rho in config["refill_probabilities"] for feedback in config["feedback"] for method in config["methods"]]
    results = []
    with ProcessPoolExecutor(max_workers=config["max_workers"]) as pool:
        futures = [pool.submit(run_job, job) for job in jobs]
        for future in as_completed(futures, timeout=config["max_wall_seconds"]):
            result = future.result()
            results.append(result)
            print(json.dumps({"completed": len(results), "total": len(jobs), "id": result["id"], "wall_seconds": round(result["wall_seconds"], 2)}), flush=True)
            if sum(p.stat().st_size for p in args.output.iterdir()) > config["max_output_bytes"]:
                raise RuntimeError("output budget exceeded")
    results.sort(key=lambda r: r["id"])
    payload = {"evidence_label": "development_not_confirmation", "runs": results,
               "wall_seconds": time.perf_counter()-start, "job_cpu_seconds": sum(r["cpu_seconds"] for r in results),
               "host": os.uname().nodename, "numpy_version": np.__version__, "run_count": len(results)}
    (args.output / "results.json").write_text(json.dumps(payload, indent=2)+"\n")
    receipts = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(args.output.iterdir()) if p.is_file()}
    (args.output / "receipt_sha256.json").write_text(json.dumps(receipts, indent=2)+"\n")
    (args.output / "COMPLETE").write_text("development pilot complete\n")


if __name__ == "__main__":
    main()
