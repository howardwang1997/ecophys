"""Exact two-world first-success search benchmark; no inventory-market claim."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import time
from typing import Any

from hydra import compose, initialize_config_dir
import numpy as np
from omegaconf import OmegaConf
from scipy.optimize import linprog


def validate(horizon: int, restore: float, separation: float, reward: float) -> None:
    if horizon < 0 or not all(math.isfinite(x) for x in (restore, separation, reward)):
        raise ValueError("finite nonnegative horizon and parameters required")
    if restore < 0 or not 0 <= separation < 1 or restore*(1+separation) >= 1 or reward < 0:
        raise ValueError("invalid two-channel law")


def expected_wait(horizon: int, probability: float) -> float:
    if probability == 0:
        return float(horizon)
    return -math.expm1(horizon*math.log1p(-probability))/probability


def balanced_wait(horizon: int, restore: float, separation: float) -> float:
    validate(horizon, restore, separation, 1)
    if restore == 0:
        return float(horizon)
    pairs, odd = divmod(horizon, 2)
    log_pair = math.log1p(-restore*(1+separation))+math.log1p(-restore*(1-separation))
    pair_sum = math.expm1(pairs*log_pair)/math.expm1(log_pair)
    return (2-restore)*pair_sum + odd*math.exp(pairs*log_pair)


def minimax_regret(horizon: int, restore: float, separation: float, reward: float = 1) -> float:
    validate(horizon, restore, separation, reward)
    if restore == 0 or separation == 0:
        return 0.0
    return reward*(balanced_wait(horizon, restore, separation)-expected_wait(horizon, restore*(1+separation)))


def scaling_limit(c: float, separation: float, reward: float = 1) -> float:
    if not math.isfinite(c) or c <= 0:
        raise ValueError("positive finite c required")
    validate(0, 0, separation, reward)
    first = -math.expm1(-c)/c
    second = -math.expm1(-c*(1+separation))/(c*(1+separation))
    return reward*(first-second)


def saturation_limit(restore: float, separation: float, reward: float = 1) -> float:
    validate(0, restore, separation, reward)
    if restore == 0 or separation == 0:
        return 0.0
    return reward*((2-restore)/(2*restore-restore**2*(1-separation**2))-1/(restore*(1+separation)))


def bayesian_value(horizon: int, restore: float, separation: float, reward: float = 1) -> float:
    """Backward reward DP with the posterior determined by observed failures."""
    validate(horizon, restore, separation, reward)
    high, low = restore*(1+separation), restore*(1-separation)
    log_ratio = math.log1p(-high)-math.log1p(-low)
    continuation = np.zeros(horizon+1)
    for elapsed in range(horizon-1, -1, -1):
        counts_a = np.arange(elapsed+1)
        odds = (2*counts_a-elapsed)*log_ratio
        posterior_a = np.exp(-np.logaddexp(0, -odds))
        success_a = posterior_a*high+(1-posterior_a)*low
        success_b = posterior_a*low+(1-posterior_a)*high
        eligible_value = reward*(horizon-elapsed-1)
        choose_a = success_a*eligible_value+(1-success_a)*continuation[1:elapsed+2]
        choose_b = success_b*eligible_value+(1-success_b)*continuation[:elapsed+1]
        continuation = np.maximum(choose_a, choose_b)
    return float(continuation[0])


def sequence_values(actions: tuple[int, ...], high: Fraction, low: Fraction) -> tuple[Fraction, Fraction]:
    """Exact rewards accumulated from first-success probabilities in each world."""
    horizon = len(actions)+1
    result = []
    for world in (0, 1):
        survival, value = Fraction(1), Fraction(0)
        for index, action in enumerate(actions):
            probability = high if action == world else low
            value += survival*probability*(horizon-index-1)
            survival *= 1-probability
        result.append(value)
    return result[0], result[1]


def rational_audit(config: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    tolerance = float(config["tolerance"])
    for law in config["rational_laws"]:
        restore, separation = Fraction(law["lambda"]), Fraction(law["alpha"])
        high, low = restore*(1+separation), restore*(1-separation)
        u, v = 1-high, 1-low
        for horizon in range(1, config["enumeration_max_horizon"]+1):
            values = [sequence_values(sequence, high, low) for sequence in product((0, 1), repeat=horizon-1)]
            best_bayes_value = max((a+b)/2 for a, b in values)
            oracle = sum((u**n*high*(horizon-n-1) for n in range(horizon-1)), Fraction(0))
            survival_sum = sum(((u*v)**(n//2)*(1 if n % 2 == 0 else (u+v)/2) for n in range(horizon)), Fraction(0))
            formula_value = horizon-survival_sum
            if best_bayes_value != formula_value:
                raise AssertionError("exact rational Bayes equality failed")
            expected_regret = oracle-best_bayes_value
            sequence = tuple(index % 2 for index in range(horizon-1))
            swapped = tuple(1-action for action in sequence)
            left, right = sequence_values(sequence, high, low), sequence_values(swapped, high, low)
            risks = tuple(oracle-(left[world]+right[world])/2 for world in (0, 1))
            if risks != (expected_regret, expected_regret):
                raise AssertionError("symmetric policy does not attain both world risks")
            row: dict[str, Any] = {"lambda": str(restore), "alpha": str(separation), "horizon": horizon,
                                   "deterministic_policies": len(values), "exact_minimax_regret": str(expected_regret),
                                   "regret": float(expected_regret), "rational_equalities": True}
            if horizon <= config["lp_max_horizon"]:
                losses = np.array([[float(oracle-a), float(oracle-b)] for a, b in values])
                objective = np.zeros(len(values)+1)
                objective[-1] = 1
                inequalities = np.column_stack((losses.T, -np.ones(2)))
                equality = np.zeros((1, len(values)+1))
                equality[0, :-1] = 1
                solution = linprog(objective, A_ub=inequalities, b_ub=np.zeros(2), A_eq=equality,
                                   b_eq=np.ones(1), bounds=[(0, None)]*len(values)+[(None, None)], method="highs")
                if not solution.success:
                    raise AssertionError("minimax linear program not solved")
                error = abs(float(solution.fun)-float(expected_regret))
                if error > tolerance:
                    raise AssertionError("minimax LP equality failed")
                row.update({"lp_regret": float(solution.fun), "lp_absolute_error": error})
            rows.append(row)
    return rows


def audit(config: dict[str, Any]) -> dict[str, Any]:
    start = time.perf_counter()
    rational = rational_audit(config)
    reward, tolerance = float(config["reward_per_eligible_round"]), float(config["tolerance"])
    dp_rows = []
    for restore, separation, horizon in product(config["dp_lambdas"], config["dp_alphas"], config["dp_horizons"]):
        value = bayesian_value(horizon, restore, separation, reward)
        formula_value = reward*(horizon-balanced_wait(horizon, restore, separation))
        error = abs(value-formula_value)
        if error > tolerance:
            raise AssertionError("independent reward DP equality failed")
        dp_rows.append({"lambda": restore, "alpha": separation, "horizon": horizon,
                        "bayesian_dp_value": value, "formula_value": formula_value, "absolute_error": error})
    scaling_rows = []
    for regime, values in (("fixed_lambda", config["fixed_lambdas"]), ("lambda_c_over_T", config["scaling_c"])):
        for parameter, separation, horizon in product(values, config["scaling_alphas"], config["report_horizons"]):
            restore = parameter if regime == "fixed_lambda" else parameter/horizon
            regret = minimax_regret(horizon, restore, separation, reward)
            scaling_rows.append({"regime": regime, "lambda": restore, "c": restore*horizon, "alpha": separation,
                                 "horizon": horizon, "regret": regret, "regret_per_round": regret/horizon,
                                 "fixed_lambda_regret_limit": saturation_limit(restore, separation, reward) if regime == "fixed_lambda" else None,
                                 "normalized_limit": scaling_limit(parameter, separation, reward) if regime == "lambda_c_over_T" else 0.0})
    return {"evidence_label": config["evidence_label"], "seed_use": config["seed_use"],
            "rational_cells": rational, "bayesian_dp_cells": dp_rows, "scaling_cells": scaling_rows,
            "violations": 0, "wall_seconds": time.perf_counter()-start,
            "scope": "Exact synthetic development checks; proof establishes minimax identity, not the finite grid. No coupled inventory claim."}


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
    (args.output/"result.json").write_text(json.dumps(result, indent=2)+"\n")
    (args.output/"input_manifest.json").write_bytes(args.manifest.read_bytes())
    (args.output/"config.yaml").write_bytes(args.config.read_bytes())
    files = list(args.output.iterdir())
    if sum(p.stat().st_size for p in files) > config["max_output_bytes"] or result["wall_seconds"] > config["max_wall_seconds"]:
        raise RuntimeError("budget exceeded")
    (args.output/"receipt_sha256.json").write_text(json.dumps({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}, indent=2)+"\n")
    (args.output/"COMPLETE").write_text("deterministic audit complete\n")
    print(json.dumps({"rational_cells": len(result["rational_cells"]), "dp_cells": len(result["bayesian_dp_cells"]),
                      "scaling_cells": len(result["scaling_cells"]), "wall_seconds": result["wall_seconds"]}), flush=True)


if __name__ == "__main__":
    main()
