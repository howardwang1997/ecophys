"""Tests for the D1_06 DGP-only K-variance preflight (experiments/reexploration/k_preflight_20260906).

Covers: generator determinism and episode-shape constraints, engine-grounded replay
invariants (FIFO payload identity, request-boundary aggregate-hash identity across arms
and draw replays, null-statistic zero draw variance, plan/tape walk agreement),
variance-decomposition math on a synthetic matrix, and byte-identical pipeline
determinism across two independent runs.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
KP_DIR = REPO_ROOT / "experiments" / "reexploration" / "k_preflight_20260906"


def _load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, KP_DIR / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


dgp_stream = _load_module("dgp_stream")
run_preflight = _load_module("run_preflight")


def _config() -> dict:
    cfg = json.loads((KP_DIR / "preflight_config.json").read_text())
    cfg["n_seeds"] = 3
    cfg["episodes_per_seed"] = 2
    cfg["bootstrap"]["draws"] = 200
    return cfg


def test_episode_stream_deterministic_and_shaped() -> None:
    cfg = _config()["generator"]
    first = dgp_stream.build_episode(31000, 0, cfg)
    second = dgp_stream.build_episode(31000, 0, cfg)
    assert first == second

    lo, hi = first.price_bands
    for order in first.initial_book:
        assert lo <= order.price <= hi
        assert order.quantity > 0
        assert 0 <= order.arrival_clock <= int(cfg["initial_clock_max"])
    prices = [order.price for order in first.initial_book if order.side.value == "S"]
    assert len(set(prices)) == 3, "three initial ask levels"

    window = first.latency_window
    for plan in first.walk_plans:
        pool_total = sum(quantity for _, quantity, _ in plan.pool)
        assert 1 <= plan.v_star <= pool_total - 2, "interior rationing with remainder >= 2"
        clocks = [clock for _, _, clock in plan.pool]
        assert any(c <= window for c in clocks) and any(c > window for c in clocks)
    ticks = [int(spec["match_ts"]) for spec in first.requests if spec["kind"] == "submit"]
    assert ticks == sorted(ticks) and ticks[0] >= int(cfg["request_tick_start"])
    assert first.requests[-1]["kind"] == "finish"


def test_engine_replay_invariants_and_null_draw_variance() -> None:
    cfg = _config()["generator"]
    stream = dgp_stream.build_episode(31005, 1, cfg)
    outcome = run_preflight.run_episode_evaluations(stream, k_max=4)
    for name, ok in outcome["invariants"].items():
        assert ok, f"invariant {name} failed"
    evaluations = outcome["evaluations"]
    varying = [
        stat
        for stat in run_preflight.DRAW_STATS
        if len(
            {
                float(evaluations[("random_unit_within_price", k)]["stats"][stat])
                for k in range(1, 5)
            }
        )
        > 1
    ]
    assert varying, "at least one draw-dependent statistic must vary across replays"
    for arm in run_preflight.ARM_LABELS:
        for stat in run_preflight.NULL_STATS:
            values = [
                float(evaluations[(arm, k)]["stats"][stat]) for k in range(1, 5)
            ]
            assert len(set(values)) == 1, f"null statistic {stat} moved under {arm}"


def test_variance_decomposition_on_synthetic_matrix() -> None:
    matrix = [[float(s) + 0.5 * float(k % 3) for k in range(16)] for s in range(8)]
    result = run_preflight.decompose_variance(matrix, [4, 8, 16], 200, 12345)
    within = run_preflight._variance(matrix[0])
    assert result["w_hat_within_seed_draw_variance"] == run_preflight._mean(
        [run_preflight._variance(row) for row in matrix]
    )
    for k in (4, 8, 16):
        per_k = result["per_k"][str(k)]
        assert per_k["draw_contribution"] == result["w_hat_within_seed_draw_variance"] / k
        assert per_k["ratio_vs_between"] == per_k["draw_contribution"] / result["v_between"]
    assert (
        result["per_k"]["4"]["ratio_vs_between"]
        > result["per_k"]["8"]["ratio_vs_between"]
        > result["per_k"]["16"]["ratio_vs_between"]
    )
    ci = result["ci95_ratio_vs_between"]["8"]
    assert ci is not None and ci[0] <= ci[1]

    constant = [[float(s) for _ in range(16)] for s in range(8)]
    degenerate = run_preflight.decompose_variance(constant, [4, 8, 16], 50, 7)
    assert degenerate["w_hat_within_seed_draw_variance"] == 0.0
    for k in (4, 8, 16):
        assert degenerate["per_k"][str(k)]["ratio_vs_between"] == 0.0


def test_min_k_rule() -> None:
    per_k = {
        "4": {"ratio_vs_between": 0.20},
        "8": {"ratio_vs_between": 0.09},
        "16": {"ratio_vs_between": 0.05},
    }
    ci = {"4": [0.1, 0.3], "8": [0.05, 0.12], "16": [0.02, 0.06]}
    decomposition = {"per_k": per_k, "ci95_ratio_vs_between": ci}
    assert run_preflight._min_k_at_threshold(decomposition, 0.10, use_ci_upper=False) == "8"
    assert run_preflight._min_k_at_threshold(decomposition, 0.10, use_ci_upper=True) == "16"
    assert run_preflight._min_k_at_threshold(decomposition, 0.05, use_ci_upper=False) == "16"
    per_k_none = {k: {"ratio_vs_between": 0.5} for k in ("4", "8", "16")}
    ci_none = {k: [0.4, 0.6] for k in ("4", "8", "16")}
    none = {"per_k": per_k_none, "ci95_ratio_vs_between": ci_none}
    assert run_preflight._min_k_at_threshold(none, 0.10, use_ci_upper=False) == "none_in_set"


def test_full_pipeline_deterministic_bytes(tmp_path: Path) -> None:
    cfg = _config()
    first = run_preflight.run_pipeline(cfg)
    second = run_preflight.run_pipeline(cfg)
    first_bytes = json.dumps(first, indent=2, sort_keys=True)
    second_bytes = json.dumps(second, indent=2, sort_keys=True)
    assert first_bytes == second_bytes

    results = first
    assert all(value == 0 for key, value in results["invariants"].items() if key != "note")
    ru = results["variance_decomposition"]["random_unit_within_price"]
    for stat in run_preflight.DRAW_STATS:
        assert ru[stat]["w_hat_within_seed_draw_variance"] > 0.0, f"{stat} shows no draw variance"
    for stat in run_preflight.NULL_STATS:
        assert ru[stat]["w_hat_within_seed_draw_variance"] == 0.0
    fifo = results["variance_decomposition"]["fifo"]
    for stat in run_preflight.ALL_STATS:
        assert fifo[stat]["w_hat_within_seed_draw_variance"] == 0.0
    assert results["recommendation"]["k_recommended"] in (4, 8, 16)
