"""DGP-only, zero-GPU K-variance preflight (PI decision D1_06).

Measures, on DGP-native consumer statistics, how much of the variance of a per-seed
K-draw mean is attributable to allocation-draw replay versus between-seed stream
variance, so K in {4, 8, 16} can be frozen on evidence before D0 (immutable after).

Variance identity (contract C2/2a.4): for per-seed value = mean over K replays of the
allocation draws, with the request stream fixed per seed,
    E[B(K)] = V_between + W/K,
where B(K) is the across-seed variance of the realized K-draw means, V_between the
between-seed variance of the infinite-draw mean, and W the expected within-seed draw
variance. Estimators: B(K) = unbiased across-seed variance; W = mean over seeds of the
unbiased 16-replay within-seed variance; V_between = B(16) - W/16 (method of moments).
Reported per statistic and K: draw contribution W/K, ratio vs between-seed variance
W(K)/V_between, ratio vs total W(K)/(V_between + W(K)), and a seeded seed-level
bootstrap 95% CI for the between ratio.

Legality: CPU-only engine execution for instrument calibration (D1_06). No GPU, no
trained models, no cell endpoints, no outcome access, no market data, and no writes
anywhere under the frozen a2_exit_20260905 bundle.

Determinism: the results JSON is a pure function of (config, code); no timestamps, no
absolute paths. Re-running to any directory reproduces byte-identical bytes.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import random
import statistics
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

KP_DIR = Path(__file__).resolve().parent
REPO_ROOT = KP_DIR.parents[2]
for entry in (str(KP_DIR), str(REPO_ROOT / "scripts")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

import dgp_stream  # noqa: E402
from lab_asset.matching import ReferenceEngine  # noqa: E402
from lab_asset.schema import (  # noqa: E402
    AllocationRule,
    EventType,
    SessionPrestate,
    TapeRecord,
)  # noqa: E402

ARM_LABELS = ("fifo", "random_unit_within_price")
NULL_STATS = (
    "c_risk_rawflow",
    "c_lat_rawflow",
    "cleared_volume_units",
    "clearing_notional",
)
DRAW_STATS = (
    "c_lat_exec",
    "alloc_hhi_mean",
    "alloc_l2_mean",
    "alloc_proprata_dev_mean",
    "n_maker_orders_filled",
)
ALL_STATS = NULL_STATS + DRAW_STATS

BOUNDARY_EVENTS = frozenset(
    {
        EventType.SESSION_START,
        EventType.ORDER_ACCEPTED,
        EventType.ORDER_REJECTED,
        EventType.ORDER_CANCELLED,
        EventType.CANCEL_REJECTED,
        EventType.ORDER_REPLACED,
        EventType.REPLACE_REJECTED,
        EventType.SESSION_END,
    }
)
_VOLATILE_PAYLOAD_KEYS = frozenset({"session_id", "prestate_hash"})


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mean(xs: Sequence[float]) -> float:
    return statistics.fmean(xs)


def _variance(xs: Sequence[float]) -> float:
    return statistics.variance(xs)


def _percentile(sorted_xs: Sequence[float], q: float) -> float:
    position = (len(sorted_xs) - 1) * q / 100.0
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_xs[lower]
    weight = position - lower
    return sorted_xs[lower] * (1.0 - weight) + sorted_xs[upper] * weight


def _json_default(obj: object) -> object:
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dict(vars(obj))
    return str(obj)


def _canonical_payload(payload: Mapping[str, object]) -> str:
    trimmed = {k: v for k, v in payload.items() if k not in _VOLATILE_PAYLOAD_KEYS}
    return json.dumps(trimmed, sort_keys=True, separators=(",", ":"), default=_json_default)


def _run_engine(prestate: SessionPrestate, requests: Sequence[object]) -> list[TapeRecord]:
    engine = ReferenceEngine(prestate)
    for request in requests:
        engine.submit(request)
    engine.finish()
    return engine.tape


def analyze_tape(tape: Sequence[TapeRecord], stream: dgp_stream.EpisodeStream) -> dict[str, object]:
    """DGP-native consumer statistics and replay-invariant projections of one tape."""

    window = stream.latency_window
    order_clocks = {order.order_id: order.arrival_clock for order in stream.initial_book}
    request_notional = 0.0
    request_notional_in_window = 0.0
    accepted_ids: list[str] = []
    rejection_count = 0
    for record in tape:
        if record.event_type == EventType.ORDER_REQUEST:
            payload = record.payload
            notional = int(payload["price"]) * int(payload["quantity"])
            request_notional += notional
            if int(payload["clocks"]["match_ts"]) <= window:
                request_notional_in_window += notional
        elif record.event_type == EventType.ORDER_ACCEPTED:
            payload = record.payload
            accepted_ids.append(str(payload["order_id"]))
            order_clocks[str(payload["order_id"])] = int(payload["clocks"]["match_ts"])
        elif record.event_type in (EventType.ORDER_REJECTED, EventType.CANCEL_REJECTED):
            rejection_count += 1

    executions = [
        record.payload["execution"]
        for record in tape
        if record.event_type == EventType.EXECUTION
    ]

    walks: list[dict[str, object]] = []
    for execution in executions:
        aggressor = str(execution["aggressor_order_id"])
        if not walks or walks[-1]["aggressor"] != aggressor:
            if any(walk["aggressor"] == aggressor for walk in walks):
                raise AssertionError("aggressive walks interleave; grouping is ambiguous")
            walks.append({"aggressor": aggressor, "executions": []})
        walks[-1]["executions"].append(execution)

    if len(walks) != len(stream.walk_plans):
        raise AssertionError(
            f"walk count {len(walks)} != plan count {len(stream.walk_plans)}"
        )

    hhi_values: list[float] = []
    l2_values: list[float] = []
    proprata_dev_values: list[float] = []
    realized_terminals: list[dict[str, object]] = []
    for walk, plan in zip(walks, stream.walk_plans, strict=True):
        walk_execs = walk["executions"]
        assert isinstance(walk_execs, list)
        terminal_price = int(walk_execs[-1]["price"])
        terminal_units = sum(
            int(item["quantity"]) for item in walk_execs if int(item["price"]) == terminal_price
        )
        counts: dict[str, int] = {}
        for item in walk_execs:
            if int(item["price"]) == terminal_price:
                maker = str(item["maker_order_id"])
                counts[maker] = counts.get(maker, 0) + int(item["quantity"])
        if terminal_price != plan.target_price or terminal_units != plan.v_star:
            raise AssertionError(
                f"realized walk terminal ({terminal_price}, {terminal_units}) != plan "
                f"({plan.target_price}, {plan.v_star})"
            )
        pool_total = sum(quantity for _, quantity, _ in plan.pool)
        hhi_values.append(sum((c / terminal_units) ** 2 for c in counts.values()))
        l2_values.append(math.sqrt(sum(c * c for c in counts.values())))
        deviation = math.sqrt(
            sum(
                (counts.get(order_id, 0) - plan.v_star * quantity / pool_total) ** 2
                for order_id, quantity, _ in plan.pool
            )
        )
        proprata_dev_values.append(deviation)
        realized_terminals.append(
            {
                "aggressor": str(plan.aggressor_actor),
                "target_price": terminal_price,
                "swept_units": int(plan.swept_units),
                "v_star": int(plan.v_star),
                "r_star": int(pool_total),
                "maker_counts": dict(sorted(counts.items())),
            }
        )

    initial_notional = sum(
        order.price * order.quantity for order in stream.initial_book
    )
    initial_notional_in_window = sum(
        order.price * order.quantity
        for order in stream.initial_book
        if order.arrival_clock <= window
    )
    cleared_volume = sum(int(item["quantity"]) for item in executions)
    clearing_notional = sum(
        int(item["price"]) * int(item["quantity"]) for item in executions
    )
    c_lat_exec = sum(
        int(item["price"]) * int(item["quantity"])
        for item in executions
        if order_clocks[str(item["maker_order_id"])] <= window
    )
    distinct_makers_filled = {str(item["maker_order_id"]) for item in executions}

    stats = {
        "c_risk_rawflow": float(initial_notional + request_notional),
        "c_lat_rawflow": float(initial_notional_in_window + request_notional_in_window),
        "cleared_volume_units": float(cleared_volume),
        "clearing_notional": float(clearing_notional),
        "c_lat_exec": float(c_lat_exec),
        "alloc_hhi_mean": _mean(hhi_values),
        "alloc_l2_mean": _mean(l2_values),
        "alloc_proprata_dev_mean": _mean(proprata_dev_values),
        "n_maker_orders_filled": float(len(distinct_makers_filled)),
    }

    boundary = [
        (record.event_type.value, record.post_aggregate_state_hash)
        for record in tape
        if record.event_type in BOUNDARY_EVENTS
    ]
    payload_projection = [
        (record.sequence, record.event_type.value, _canonical_payload(record.payload))
        for record in tape
    ]
    return {
        "stats": stats,
        "boundary": boundary,
        "payload_projection": payload_projection,
        "accepted_ids": accepted_ids,
        "rejection_count": rejection_count,
        "cleared_volume": cleared_volume,
        "realized_terminals": realized_terminals,
    }


def run_episode_evaluations(
    stream: dgp_stream.EpisodeStream, k_max: int
) -> dict[str, object]:
    """Run both arms x k_max draw replays of one episode and enforce invariants."""

    requests = dgp_stream.order_requests(stream)
    evaluations: dict[tuple[str, int], dict[str, object]] = {}
    for arm in ARM_LABELS:
        rule = AllocationRule(arm)
        for k in range(1, k_max + 1):
            draw_seed = dgp_stream.derive_seed(stream.seed_root, "draw", k, stream.episode_index)
            tape = _run_engine(dgp_stream.build_prestate(stream, rule, draw_seed), requests)
            evaluations[(arm, k)] = analyze_tape(tape, stream)

    fifo_projections = [evaluations[("fifo", k)]["payload_projection"] for k in range(1, k_max + 1)]
    fifo_identity = all(projection == fifo_projections[0] for projection in fifo_projections)

    boundaries = [evaluations[(arm, k)]["boundary"] for arm in ARM_LABELS for k in range(1, k_max + 1)]
    boundary_identity = all(boundary == boundaries[0] for boundary in boundaries)

    ru_accepted = [evaluations[("random_unit_within_price", k)]["accepted_ids"] for k in range(1, k_max + 1)]
    ru_accepted_identity = all(ids == ru_accepted[0] for ids in ru_accepted)

    cleared_matches_plan = all(
        evaluation["cleared_volume"] == stream.predicted_cleared_volume
        for evaluation in evaluations.values()
    )
    zero_rejections = all(
        evaluation["rejection_count"] == 0 for evaluation in evaluations.values()
    )
    ru_null_draw_variance_zero = all(
        _variance(
            [
                float(evaluations[("random_unit_within_price", k)]["stats"][stat])
                for k in range(1, k_max + 1)
            ]
        )
        == 0.0
        for stat in NULL_STATS
    )

    return {
        "evaluations": evaluations,
        "invariants": {
            "fifo_payload_projection_identity": fifo_identity,
            "request_boundary_aggregate_hash_identity": boundary_identity,
            "ru_accepted_stream_identity": ru_accepted_identity,
            "cleared_volume_matches_plan": cleared_matches_plan,
            "zero_rejections": zero_rejections,
            "ru_null_stat_draw_variance_zero": ru_null_draw_variance_zero,
        },
    }


def decompose_variance(
    matrix: Sequence[Sequence[float]],
    k_grid: Sequence[int],
    bootstrap_draws: int,
    bootstrap_seed: int,
) -> dict[str, object]:
    """Variance decomposition of the per-seed K-draw mean from an S x k_max matrix."""

    k_max = len(matrix[0])
    seed_count = len(matrix)
    within = [_variance(row) for row in matrix]
    w_hat = _mean(within)
    means_full = [_mean(row) for row in matrix]
    b_16 = _variance(means_full)
    v_between = b_16 - w_hat / k_max

    per_k: dict[str, dict[str, object]] = {}
    for k in k_grid:
        means_k = [_mean(row[:k]) for row in matrix]
        b_k = _variance(means_k)
        draw_contribution = w_hat / k
        ratio_between = draw_contribution / v_between if v_between > 0 else None
        ratio_total = (
            draw_contribution / (v_between + draw_contribution)
            if v_between + draw_contribution > 0
            else None
        )
        per_k[str(k)] = {
            "between_var_of_k_draw_mean": b_k,
            "draw_contribution": draw_contribution,
            "ratio_vs_between": ratio_between,
            "ratio_vs_total": ratio_total,
        }

    rng = random.Random(bootstrap_seed)
    bootstrap: dict[int, list[float]] = {k: [] for k in k_grid}
    degenerate = 0
    for _ in range(bootstrap_draws):
        indices = [rng.randrange(seed_count) for _ in range(seed_count)]
        b_star = _variance([means_full[i] for i in indices])
        w_star = _mean([within[i] for i in indices])
        v_star = b_star - w_star / k_max
        if v_star <= 0:
            degenerate += 1
            continue
        for k in k_grid:
            bootstrap[k].append((w_star / k) / v_star)
    ci: dict[str, list[float] | None] = {}
    for k in k_grid:
        sample = sorted(bootstrap[k])
        ci[str(k)] = (
            [_percentile(sample, 2.5), _percentile(sample, 97.5)] if sample else None
        )

    return {
        "n_seeds": seed_count,
        "k_max": k_max,
        "w_hat_within_seed_draw_variance": w_hat,
        "v_between": v_between,
        "b_at_k_max": b_16,
        "per_k": per_k,
        "ci95_ratio_vs_between": ci,
        "bootstrap_degenerate_resamples": degenerate,
    }


def _min_k_at_threshold(
    decomposition: Mapping[str, object], threshold: float, use_ci_upper: bool
) -> str:
    per_k = decomposition["per_k"]
    assert isinstance(per_k, dict)
    key = "ratio_vs_between"
    if use_ci_upper:
        ci = decomposition["ci95_ratio_vs_between"]
        assert isinstance(ci, dict)
        for k in (4, 8, 16):
            interval = ci[str(k)]
            if interval is not None and interval[1] <= threshold:
                return str(k)
        return "none_in_set"
    for k in (4, 8, 16):
        ratio = per_k[str(k)][key]
        if ratio is not None and ratio <= threshold:
            return str(k)
    return "none_in_set"


def run_pipeline(cfg: Mapping[str, object]) -> dict[str, object]:
    """Execute the full preflight; returns the results payload (pure function)."""

    generator_cfg = cfg["generator"]
    assert isinstance(generator_cfg, dict)
    seed_base = int(cfg["seed_base"])
    seed_count = int(cfg["n_seeds"])
    episodes_per_seed = int(cfg["episodes_per_seed"])
    k_grid = [int(k) for k in cfg["k_grid"]]
    k_max = max(k_grid)
    bootstrap_cfg = cfg["bootstrap"]
    assert isinstance(bootstrap_cfg, dict)
    thresholds = [float(t) for t in cfg["thresholds"]]
    seed_roots = [seed_base + i for i in range(seed_count)]

    invariant_failures: dict[str, int] = {name: 0 for name in (
        "fifo_payload_projection_identity",
        "request_boundary_aggregate_hash_identity",
        "ru_accepted_stream_identity",
        "cleared_volume_matches_plan",
        "zero_rejections",
        "ru_null_stat_draw_variance_zero",
    )}
    episode_records: list[dict[str, object]] = []
    matrices: dict[str, dict[str, list[list[float]]]] = {
        arm: {stat: [] for stat in ALL_STATS} for arm in ARM_LABELS
    }
    terminal_examples: dict[str, object] = {}

    for seed_root in seed_roots:
        replay_values: dict[str, dict[str, list[list[float]]]] = {
            arm: {stat: [[] for _ in range(k_max)] for stat in ALL_STATS}
            for arm in ARM_LABELS
        }
        for episode_index in range(episodes_per_seed):
            stream = dgp_stream.build_episode(seed_root, episode_index, generator_cfg)
            outcome = run_episode_evaluations(stream, k_max)
            for name, ok in outcome["invariants"].items():
                assert isinstance(ok, bool)
                if not ok:
                    invariant_failures[name] += 1
            evaluations = outcome["evaluations"]
            assert isinstance(evaluations, dict)
            for arm in ARM_LABELS:
                for stat in ALL_STATS:
                    for k in range(1, k_max + 1):
                        replay_values[arm][stat][k - 1].append(
                            float(evaluations[(arm, k)]["stats"][stat])
                        )
                    if episode_index == 0 and seed_root == seed_roots[0]:
                        terminal_examples.setdefault(arm, {})[stat] = [
                            float(evaluations[(arm, k)]["stats"][stat])
                            for k in range(1, k_max + 1)
                        ]

            ru_first = evaluations[("random_unit_within_price", 1)]
            assert isinstance(ru_first, dict)
            episode_records.append(
                {
                    "seed_root": seed_root,
                    "episode_index": episode_index,
                    "walks": ru_first["realized_terminals"],
                    "pool_straddles_window": [
                        any(clock <= stream.latency_window for _, _, clock in plan.pool)
                        and any(clock > stream.latency_window for _, _, clock in plan.pool)
                        for plan in stream.walk_plans
                    ],
                    "predicted_cleared_volume": stream.predicted_cleared_volume,
                }
            )
        for arm in ARM_LABELS:
            for stat in ALL_STATS:
                matrices[arm][stat].append(
                    [_mean(values) for values in replay_values[arm][stat]]
                )

    decompositions: dict[str, dict[str, object]] = {}
    for arm in ARM_LABELS:
        decompositions[arm] = {}
        for stat in ALL_STATS:
            decompositions[arm][stat] = decompose_variance(
                matrices[arm][stat],
                k_grid,
                int(bootstrap_cfg["draws"]),
                dgp_stream.derive_seed(int(bootstrap_cfg["seed"]), arm, stat),
            )

    k_table: dict[str, object] = {
        "thresholds": thresholds,
        "rule": (
            "recommended K = smallest K in {4,8,16} such that EVERY random_unit-arm "
            "draw-dependent statistic has bootstrap 95% upper bound of "
            "ratio_vs_between(K) <= 0.10 (conservative); point-estimate variant reported "
            "alongside"
        ),
        "per_stat_min_k": {},
        "min_k_draw_stats": {},
    }
    per_stat = {}
    for arm in ARM_LABELS:
        for stat in ALL_STATS:
            entry = {}
            for threshold in thresholds:
                entry[f"threshold_{threshold:g}"] = {
                    "point": _min_k_at_threshold(
                        decompositions[arm][stat], threshold, use_ci_upper=False
                    ),
                    "ci_upper": _min_k_at_threshold(
                        decompositions[arm][stat], threshold, use_ci_upper=True
                    ),
                }
            per_stat[f"{arm}:{stat}"] = entry
    k_table["per_stat_min_k"] = per_stat

    def _max_min_k(arm: str, stats: Sequence[str], threshold: float, ci: bool) -> str:
        chosen = [per_stat[f"{arm}:{stat}"][f"threshold_{threshold:g}"]["ci_upper" if ci else "point"] for stat in stats]
        if "none_in_set" in chosen:
            return "none_in_set"
        return str(max(int(k) for k in chosen))

    summary = {}
    for threshold in thresholds:
        summary[f"threshold_{threshold:g}"] = {
            "point": _max_min_k("random_unit_within_price", DRAW_STATS, threshold, ci=False),
            "ci_upper": _max_min_k("random_unit_within_price", DRAW_STATS, threshold, ci=True),
        }
    k_table["min_k_draw_stats"] = summary

    conservative = summary["threshold_0.1"]["ci_upper"]
    if conservative == "none_in_set":
        k_recommended = 16
        recommendation_notes = [
            "K=16 is the largest authorized value and still fails the 10% conservative "
            "criterion for at least one random_unit draw-dependent statistic; the D0 "
            "freeze must either accept the residual draw noise at K=16 or revisit the "
            "statistic set with the PI."
        ]
    else:
        k_recommended = int(conservative)
        recommendation_notes = []
    recommendation_notes.append(
        "FIFO arm: all statistics have exactly zero draw variance (deterministic "
        "kernel); any K satisfies the criterion and the extra K-1 evaluations serve "
        "only the G8 byte-identity determinism gate."
    )

    v_star_counts: dict[str, int] = {}
    straddle_all_count = 0
    for record in episode_records:
        walks = record["walks"]
        assert isinstance(walks, list)
        for walk in walks:
            assert isinstance(walk, dict)
            key = f"v_star={int(walk['v_star'])}"
            v_star_counts[key] = v_star_counts.get(key, 0) + 1
        straddles = record["pool_straddles_window"]
        assert isinstance(straddles, list)
        if all(straddles):
            straddle_all_count += 1

    results = {
        "schema_version": "k-preflight-v1",
        "component": "d1_06_dgp_only_k_variance_preflight",
        "authorization": "pi_reexploration_d1_authorization_20260906 (item D1_06)",
        "policy_class_note": (
            "M0 (zero tape feedback), the strongest-lumpability point of the "
            "M0/M1-lumpable class of contract C2(a); calibration-grade generator, NOT "
            "the D0-frozen corpus generator. Re-run this preflight against the D0 "
            "corpus generator before the K freeze if it adds feedback channels."
        ),
        "config": dict(cfg),
        "seed_roots": seed_roots,
        "statistics_definitions": {
            "c_risk_rawflow": "sum of price*quantity over initial book + submitted order requests (theory-appendix C_risk raw-flow notional; stream-null)",
            "c_lat_rawflow": "c_risk_rawflow restricted to orders with arrival clock <= W (C_lat^W raw-flow; stream-null)",
            "cleared_volume_units": "total executed units (aggregate tape; null under resource slack)",
            "clearing_notional": "sum of price*quantity over executions (aggregate tape; null)",
            "c_lat_exec": "executed notional attributable to makers with arrival clock <= W (realized-allocation latency consumer, Theorem 1(e)(ii) direction; draw-dependent)",
            "alloc_hhi_mean": "mean over aggressive walks of sum_i (c_i/V*)^2 at the terminal rationed level (allocation concentration; draw-dependent)",
            "alloc_l2_mean": "mean over walks of ||c||_2 at the terminal rationed level (allocation-vector scale; draw-dependent)",
            "alloc_proprata_dev_mean": "mean over walks of ||c - V* q/R*||_2 vs the pro-rata expectation using DGP ground-truth pool snapshots (draw-dependent)",
            "n_maker_orders_filled": "distinct maker orders with >= 1 fill (granularity fingerprint direction; draw-dependent)",
        },
        "arm_semantics": {
            "fifo": "deterministic kernel; engine RNG never consumed; draw replays must be payload-identical",
            "random_unit_within_price": "draws uniformly without replacement from remaining resting units; engine RNG seeded by prestate.seed = per-(seed,k,episode) derived draw stream",
        },
        "invariants": {
            **invariant_failures,
            "note": "counts are failure counts; all must be 0",
        },
        "episode_descriptives": {
            "episodes_total": len(episode_records),
            "walks_total": sum(v_star_counts.values()),
            "v_star_counts": dict(sorted(v_star_counts.items())),
            "episodes_with_all_pools_straddling_window": straddle_all_count,
        },
        "spot_check_first_episode_replay_values": terminal_examples,
        "variance_decomposition": decompositions,
        "k_table": k_table,
        "recommendation": {
            "k_recommended": k_recommended,
            "k_default_per_decision_text": 8,
            "notes": recommendation_notes,
        },
        "provenance": {
            "dgp_stream_sha256": sha256_file(KP_DIR / "dgp_stream.py"),
            "run_preflight_sha256": sha256_file(Path(__file__).resolve()),
            "engine_matching_sha256": sha256_file(REPO_ROOT / "scripts/lab_asset/matching.py"),
            "engine_schema_sha256": sha256_file(REPO_ROOT / "scripts/lab_asset/schema.py"),
            "python_version": sys.version.split()[0],
        },
        "caveats": [
            "This preflight bounds ONLY the DGP-side draw-replay component of per-seed "
            "variance. Stage-1 endpoint channels additionally carry training noise, "
            "neural decode error and horizon-rollout divergence that no zero-GPU, "
            "no-trained-model preflight can see; the K freeze therefore conditions on "
            "the DGP-side component alone.",
            "Between-seed variance here is calibration-generator design variance; the "
            "frozen D0 corpus generator may differ.",
            "Contract CRN replays the same K draw streams across the cells within a "
            "seed, so paired-contrast draw variance is at most the single-arm draw "
            "variance measured here; the reported ratios are conservative (upper "
            "bounds) for the contract's paired contrasts.",
            "The training-time kernel stream (one draw consumer per through-M arm) is "
            "outside this preflight's scope.",
        ],
    }
    return results


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    output_dir = Path(argv[0]).resolve() if argv else KP_DIR
    cfg = json.loads((KP_DIR / "preflight_config.json").read_text())
    results = run_pipeline(cfg)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n"
    )
    recommendation = results["recommendation"]
    assert isinstance(recommendation, dict)
    print(
        f"k-preflight written to {output_dir / 'results.json'}: "
        f"K_recommended={recommendation['k_recommended']}"
    )


if __name__ == "__main__":
    main()
