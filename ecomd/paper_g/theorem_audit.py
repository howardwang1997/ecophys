"""Deterministic checks of executable imitation and persistent access rights."""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path
import time
from typing import Any

from hydra import compose, initialize_config_dir
import numpy as np
from numpy.typing import NDArray
from omegaconf import OmegaConf

from .model import ACTIONS, Action, Law, Market, State, TabularModel


def distance(left: State, right: State) -> int:
    return abs(left.inventory-right.inventory)+abs(left.bid_depth-right.bid_depth)+abs(left.ask_depth-right.ask_depth)


def imitate(state: State, virtual: Action, capacity: int) -> Action:
    h = virtual.hedge
    if (h == 1 and (not state.ask_depth or state.inventory == capacity)) or (h == -1 and (not state.bid_depth or state.inventory == 0)):
        h = 0
    after = state.inventory+h
    return Action(h, virtual.bid if after < capacity else 0, virtual.ask if after > 0 else 0)


def geometric_wait(horizon: int, probability: float) -> float:
    if horizon < 0 or not 0 <= probability <= 1:
        raise ValueError("invalid geometric-wait parameters")
    if probability == 0:
        return float(horizon)
    if probability == 1:
        return float(min(horizon, 1))
    return float(-np.expm1(horizon*np.log1p(-probability))/probability)


def check_coupling(capacity: int) -> dict[str, int]:
    model = TabularModel(capacity, .5)
    count, tight = 0, 0
    types = ((True, 101), (True, 102), (False, 98), (False, 99))
    for real, virtual in product(model.states, repeat=2):
        for j, action in enumerate(ACTIONS):
            if not model.legal[model.index[virtual], j]:
                continue
            copied = imitate(real, action, capacity)
            for (buy, value), rb, ra in product(types, (False, True), (False, True)):
                left, right = Market(capacity, 1, real.inventory), Market(capacity, 1, virtual.inventory)
                left.state, right.state = real, virtual
                actual = left.step(copied, buy, value, rb, ra, False)
                target = right.step(action, buy, value, rb, ra, False)
                before, after = distance(real, virtual), distance(actual.state, target.state)
                slack = 2*(before-after)-(target.reward-actual.reward)
                if slack < 0 or after > before:
                    raise AssertionError((real, virtual, action, copied, buy, value, rb, ra, slack))
                count += 1
                tight += int(slack == 0)
    return {"capacity": capacity, "event_cases": count, "tight_cases": tight, "violations": 0}


def gate_values(capacity: int, law: Law, restore: float, horizon: int) -> NDArray[np.float64]:
    if not 0 <= restore <= 1:
        raise ValueError("invalid restoration probability")
    size = capacity+1
    reward = np.zeros((2*size, len(ACTIONS)))
    legal = np.zeros_like(reward, dtype=bool)
    transition = np.zeros((2*size, len(ACTIONS), 2*size))
    for access in (0, 1):
        base = TabularModel(capacity, float(access))
        p, r = base.kernel(law)
        indices = [base.index[State(q, access, access)] for q in range(size)]
        rows = slice(access*size, (access+1)*size)
        legal[rows] = base.legal[indices]
        reward[rows] = r[indices]
        reduced = p[indices][:, :, indices]
        if access:
            transition[rows, :, size:] = reduced
        else:
            transition[rows, :, :size] = (1-restore)*reduced
            transition[rows, :, size:] = restore*reduced
    values = np.zeros((horizon+1, 2*size))
    for h in range(1, horizon+1):
        scores = reward+np.einsum("sak,k->sa", transition, values[h-1], optimize=False)
        scores[~legal] = -np.inf
        values[h] = scores.max(axis=1)
    return values


def audit(config: dict[str, Any]) -> dict[str, Any]:
    start = time.perf_counter()
    coupling = [check_coupling(q) for q in config["coupling_capacities"]]
    span_rows = []
    for q, p, pair, rho in product(config["capacities"], config["buy_probabilities"], config["willingness_pairs"], config["refill_probabilities"]):
        law = Law(p, *pair)
        model = TabularModel(q, rho)
        values, _ = model.solve(law, config["horizon"])
        adjacent = [(i, j) for i, s in enumerate(model.states) for j, t in enumerate(model.states) if i < j and distance(s, t) == 1]
        differences = [float(np.max(np.abs(values[:, i]-values[:, j]))) for i, j in adjacent]
        spans = np.ptp(values, axis=1)
        if max(differences) > 2+config["tolerance"] or float(spans.max()) > 2*(q+2)+config["tolerance"]:
            raise AssertionError("M0 value bound failed")
        span_rows.append({"capacity": q, "buy_probability": p, "buyer_high_probability": pair[0], "seller_low_probability": pair[1], "rho": rho,
                          "max_adjacent_value_difference": max(differences), "max_span": float(spans.max()),
                          "span_bound": 2*(q+2), "horizon": config["horizon"], "adjacent_pairs": len(adjacent)})
    gate_rows = []
    law = Law(**config["gate_law"])
    for q, probability in product(config["capacities"], config["gate_restore_probabilities"]):
        values = gate_values(q, law, probability, config["horizon"])
        i = config["initial_inventory"]
        for h in config["report_horizons"]:
            gap = float(values[h, q+1+i]-values[h, i])
            expected_wait = geometric_wait(h, probability)
            bound = .2*expected_wait-6*q
            if gap < bound-config["tolerance"]:
                raise AssertionError("access-gate bound failed")
            gate_rows.append({"capacity": q, "lambda": probability, "horizon": h,
                              "eligible_value": float(values[h, q+1+i]), "suspended_value": float(values[h, i]),
                              "value_gap": gap, "truncated_wait": expected_wait, "proved_gap_lower_bound": bound,
                              "old_inventory_depth_span_bound": 2*(q+2)})
    return {"evidence_label": config["evidence_label"], "seed_use": config["seed_use"],
            "coupling": coupling, "m0_span_cells": span_rows, "gate_cells": gate_rows,
            "wall_seconds": time.perf_counter()-start, "violations": 0,
            "scope": "Finite deterministic checks support implementation; uniform claims depend on the analytic proof, not this grid."}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    for name, digest in manifest["files"].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"source mismatch: {name}")
    with initialize_config_dir(config_dir=str(args.config.resolve().parent), version_base=None):
        obj = OmegaConf.to_container(compose(config_name=args.config.stem), resolve=True)
    if not isinstance(obj, dict):
        raise ValueError("mapping required")
    config: dict[str, Any] = {str(k): v for k, v in obj.items()}
    args.output.mkdir(parents=True, exist_ok=False)
    result = audit(config)
    (args.output / "result.json").write_text(json.dumps(result, indent=2)+"\n")
    (args.output / "input_manifest.json").write_bytes(args.manifest.read_bytes())
    (args.output / "config.yaml").write_bytes(args.config.read_bytes())
    files = list(args.output.iterdir())
    if sum(p.stat().st_size for p in files) > config["max_output_bytes"] or result["wall_seconds"] > config["max_wall_seconds"]:
        raise RuntimeError("budget exceeded")
    receipts = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (args.output / "receipt_sha256.json").write_text(json.dumps(receipts, indent=2)+"\n")
    (args.output / "COMPLETE").write_text("deterministic audit complete\n")
    print(json.dumps({"coupling": result["coupling"], "span_cells": len(result["m0_span_cells"]),
                      "gate_rows": len(result["gate_cells"]), "wall_seconds": result["wall_seconds"]}), flush=True)


if __name__ == "__main__":
    main()
