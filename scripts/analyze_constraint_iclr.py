"""Select pilot cells and analyze paired confirmation records for the ICLR audit."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np
from constraint_iclr_common import bootstrap_mean_ci, holm_adjust, sha256_file
from scipy import stats

COMPARISONS = (("free", "free_res"), ("free_res", "hard"), ("free", "soft30"))
PRIMARY_CASE = {"A": "ood_flat", "B": "ood_flat", "C": "ood_rich", "H": "ood_flat", "M2": "high_imbalance"}
CONFIRMATION_SEEDS = set(range(1000, 1030))
PILOT_ALLOWED_LEARNING_RATES = {
    "B": (0.0003, 0.001),
    "C": (0.0003, 0.001),
}


def load_records(paths: Iterable[Path]) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for raw_path in paths:
        candidates = (
            sorted(raw_path.rglob("*.jsonl")) + sorted(raw_path.rglob("*.json"))
            if raw_path.is_dir()
            else [raw_path]
        )
        for path in candidates:
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".jsonl":
                payloads = [json.loads(line) for line in text.splitlines() if line.strip()]
            else:
                payload = json.loads(text)
                payloads = payload.get("records", [payload]) if isinstance(payload, dict) else payload
            for record in payloads:
                if record.get("schema_version") != "constraint-iclr-v1":
                    continue
                run_id = str(record["run_id"])
                if run_id in by_id and by_id[run_id] != record:
                    raise ValueError(f"conflicting duplicate run_id {run_id}")
                by_id[run_id] = record
    return list(by_id.values())


def system_key(record: dict[str, Any]) -> str:
    return f"{record['family']}:{record['system']}"


def cell(record: dict[str, Any]) -> dict[str, float | int | str]:
    return {
        "capacity": int(record["capacity"]),
        "epochs": int(record["epochs"]),
        "learning_rate": float(record["learning_rate"]),
        "config_id": str(record["config_id"]),
    }


def same_cell(record: dict[str, Any], selected: dict[str, Any]) -> bool:
    return (
        int(record["capacity"]) == int(selected["capacity"])
        and int(record["epochs"]) == int(selected["epochs"])
        and np.isclose(float(record["learning_rate"]), float(selected["learning_rate"]), rtol=0.0, atol=1e-15)
    )


def relative_gap(left: float, right: float) -> float:
    denominator = max((abs(left) + abs(right)) / 2.0, np.finfo(float).tiny)
    return abs(left - right) / denominator


def pilot_record_is_eligible(record: dict[str, Any]) -> bool:
    """Apply the outcome-blind B/C learning-rate correction to pilot selection."""
    if record.get("stage") != "pilot":
        return True
    allowed = PILOT_ALLOWED_LEARNING_RATES.get(str(record.get("family")))
    if allowed is None:
        return True
    learning_rate = float(record["learning_rate"])
    return any(np.isclose(learning_rate, value, rtol=0.0, atol=1e-15) for value in allowed)


def summarize_cells(records: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[(str(record["mechanism"]), str(record["config_id"]))].append(record)
    summaries: dict[tuple[str, str], dict[str, Any]] = {}
    for key, group in grouped.items():
        seed_count = len({int(record["seed"]) for record in group})
        if seed_count < 2:
            continue
        summaries[key] = {
            "cell": cell(group[0]),
            "id_rmse": float(np.mean([record["id_metrics"]["total_rmse"] for record in group])),
            "compute_proxy": float(np.mean([record["compute"]["proxy"] for record in group])),
            "seeds": sorted({int(record["seed"]) for record in group}),
        }
    return summaries


def select_pair(
    summaries: dict[tuple[str, str], dict[str, Any]],
    left_mechanism: str,
    right_mechanism: str,
    *,
    tolerance: float = 0.05,
) -> dict[str, Any]:
    left = [
        (config_id, value)
        for (mechanism, config_id), value in summaries.items()
        if mechanism == left_mechanism
    ]
    right = [
        (config_id, value)
        for (mechanism, config_id), value in summaries.items()
        if mechanism == right_mechanism
    ]
    if not left or not right:
        raise ValueError(f"missing pilot cells for {left_mechanism}--{right_mechanism}")

    candidates: list[tuple[tuple[float, float, float, str, str], dict[str, Any], dict[str, Any]]] = []
    for left_id, left_value in left:
        for right_id, right_value in right:
            compute_gap = relative_gap(left_value["compute_proxy"], right_value["compute_proxy"])
            id_gap = relative_gap(left_value["id_rmse"], right_value["id_rmse"])
            if compute_gap <= tolerance and id_gap <= tolerance:
                rank = (
                    id_gap,
                    (left_value["id_rmse"] + right_value["id_rmse"]) / 2.0,
                    (left_value["compute_proxy"] + right_value["compute_proxy"]) / 2.0,
                    left_id,
                    right_id,
                )
                candidates.append((rank, left_value, right_value))
    branch = "matched_id_compute"
    if candidates:
        _, selected_left, selected_right = min(candidates, key=lambda value: value[0])
    else:
        branch = "fixed_compute_nonoverlap"
        fixed: list[tuple[tuple[float, float, str], dict[str, Any], dict[str, Any]]] = []
        right_by_id = {config_id: value for config_id, value in right}
        for config_id, left_value in left:
            if config_id not in right_by_id:
                continue
            right_value = right_by_id[config_id]
            rank = (
                (left_value["id_rmse"] + right_value["id_rmse"]) / 2.0,
                left_value["compute_proxy"],
                config_id,
            )
            fixed.append((rank, left_value, right_value))
        if not fixed:
            raise ValueError(f"no same-cell fallback for {left_mechanism}--{right_mechanism}")
        _, selected_left, selected_right = min(fixed, key=lambda value: value[0])
    return {
        "branch": branch,
        "id_relative_gap": relative_gap(selected_left["id_rmse"], selected_right["id_rmse"]),
        "compute_relative_gap": relative_gap(selected_left["compute_proxy"], selected_right["compute_proxy"]),
        "left": {"mechanism": left_mechanism, **selected_left},
        "right": {"mechanism": right_mechanism, **selected_right},
    }


def select_pilot(records: list[dict[str, Any]]) -> dict[str, Any]:
    all_pilot = [record for record in records if record.get("stage") == "pilot"]
    pilot = [record for record in all_pilot if pilot_record_is_eligible(record)]
    excluded_by_family = {
        family: sum(
            1
            for record in all_pilot
            if str(record.get("family")) == family and not pilot_record_is_eligible(record)
        )
        for family in sorted(PILOT_ALLOWED_LEARNING_RATES)
    }
    selections: dict[str, Any] = {}
    for key in sorted({system_key(record) for record in pilot}):
        subset = [record for record in pilot if system_key(record) == key]
        summaries = summarize_cells(subset)
        comparisons = {
            f"{left}__{right}": select_pair(summaries, left, right)
            for left, right in COMPARISONS
            if any(mechanism == left for mechanism, _ in summaries)
            and any(mechanism == right for mechanism, _ in summaries)
        }
        jobs: dict[tuple[str, str], dict[str, Any]] = {}
        for comparison in comparisons.values():
            for side in ("left", "right"):
                selected = comparison[side]
                key_job = (str(selected["mechanism"]), str(selected["cell"]["config_id"]))
                jobs[key_job] = {"mechanism": selected["mechanism"], **selected["cell"]}
        selections[key] = {
            "family": subset[0]["family"],
            "system": subset[0]["system"],
            "comparisons": comparisons,
            "confirmation_jobs": sorted(
                jobs.values(), key=lambda value: (value["mechanism"], value["config_id"])
            ),
        }
    return {
        "schema_version": "constraint-iclr-lock-v1",
        "selection_uses": "pilot ID RMSE and compute proxy only",
        "pilot_record_policy": {
            "allowed_learning_rates": {
                family: list(values)
                for family, values in sorted(PILOT_ALLOWED_LEARNING_RATES.items())
            },
            "excluded_records_by_family": excluded_by_family,
        },
        "confirmation_seeds": sorted(CONFIRMATION_SEEDS),
        "systems": selections,
    }


def _records_for_arm(
    records: list[dict[str, Any]],
    key: str,
    selected: dict[str, Any],
) -> dict[int, dict[str, Any]]:
    mechanism = str(selected["mechanism"])
    chosen_cell = selected["cell"]
    return {
        int(record["seed"]): record
        for record in records
        if record.get("stage") == "confirmation"
        and system_key(record) == key
        and record["mechanism"] == mechanism
        and same_cell(record, chosen_cell)
        and int(record["seed"]) in CONFIRMATION_SEEDS
    }


def _paired_effect(
    left: dict[int, dict[str, Any]],
    right: dict[int, dict[str, Any]],
    *,
    case_name: str,
    horizon: str,
) -> dict[str, Any]:
    seeds = sorted(set(left) & set(right))
    left_values = np.array(
        [left[seed]["cases"][case_name][horizon]["conserving_rmse"] for seed in seeds], dtype=float
    )
    right_values = np.array(
        [right[seed]["cases"][case_name][horizon]["conserving_rmse"] for seed in seeds], dtype=float
    )
    differences = left_values - right_values
    result: dict[str, Any] = {
        "seeds": seeds,
        "n": len(seeds),
        "left_mean": float(left_values.mean()) if len(seeds) else None,
        "left_sd": float(left_values.std(ddof=1)) if len(seeds) > 1 else None,
        "right_mean": float(right_values.mean()) if len(seeds) else None,
        "right_sd": float(right_values.std(ddof=1)) if len(seeds) > 1 else None,
        "paired_mean_difference": float(differences.mean()) if len(seeds) else None,
    }
    if len(seeds) >= 2:
        result["ci95"] = list(bootstrap_mean_ci(differences, confidence=0.95))
        result["ci90"] = list(bootstrap_mean_ci(differences, confidence=0.90))
        result["paired_t_pvalue"] = float(stats.ttest_rel(left_values, right_values).pvalue)
    return result


def _confirmation_overlap(
    left: dict[int, dict[str, Any]], right: dict[int, dict[str, Any]]
) -> dict[str, Any]:
    seeds = sorted(set(left) & set(right))
    if not seeds:
        return {"n": 0, "passes": False}
    left_id = float(np.mean([left[seed]["id_metrics"]["total_rmse"] for seed in seeds]))
    right_id = float(np.mean([right[seed]["id_metrics"]["total_rmse"] for seed in seeds]))
    left_compute = float(np.mean([left[seed]["compute"]["proxy"] for seed in seeds]))
    right_compute = float(np.mean([right[seed]["compute"]["proxy"] for seed in seeds]))
    id_gap = relative_gap(left_id, right_id)
    compute_gap = relative_gap(left_compute, right_compute)
    return {
        "n": len(seeds),
        "left_id_rmse": left_id,
        "right_id_rmse": right_id,
        "id_relative_gap": id_gap,
        "compute_relative_gap": compute_gap,
        "passes": id_gap <= 0.05 and compute_gap <= 0.05,
    }


def analyze_confirmation(records: list[dict[str, Any]], lock: dict[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {"schema_version": "constraint-iclr-analysis-v1", "systems": {}}
    primary_sign_tests: list[tuple[str, float]] = []
    for key, system_lock in lock["systems"].items():
        comparisons: dict[str, Any] = {}
        cached_arms: dict[str, tuple[dict[int, dict[str, Any]], dict[int, dict[str, Any]]]] = {}
        for comparison_name, selection in system_lock["comparisons"].items():
            left = _records_for_arm(records, key, selection["left"])
            right = _records_for_arm(records, key, selection["right"])
            cached_arms[comparison_name] = (left, right)
            overlap = _confirmation_overlap(left, right)
            case_names = (
                sorted(
                    set.intersection(*[set(record["cases"]) for record in [*left.values(), *right.values()]])
                )
                if left and right
                else []
            )
            effects: dict[str, Any] = {}
            for case_name in case_names:
                example = next(iter(left.values()))
                horizons = sorted(example["cases"][case_name], key=int)
                effects[case_name] = {
                    horizon: _paired_effect(left, right, case_name=case_name, horizon=horizon)
                    for horizon in horizons
                }
            comparison_result = {
                "pilot_branch": selection["branch"],
                "confirmation_overlap": overlap,
                "complete_confirmation_seeds": set(left) & set(right) == CONFIRMATION_SEEDS,
                "effects": effects,
            }
            if comparison_name == "free__free_res":
                primary_case = PRIMARY_CASE[str(system_lock["family"])]
                primary = effects.get(primary_case, {}).get("1")
                if primary and "paired_t_pvalue" in primary:
                    primary_sign_tests.append((key, float(primary["paired_t_pvalue"])))
            comparisons[comparison_name] = comparison_result

        equivalence: dict[str, Any] = {}
        residual_pair = cached_arms.get("free_res__hard")
        if residual_pair:
            left, right = residual_pair
            for case_name in sorted(set(next(iter(left.values()))["cases"]) if left else set()):
                equivalence[case_name] = {}
                for horizon in sorted(next(iter(left.values()))["cases"][case_name], key=int):
                    effect = _paired_effect(left, right, case_name=case_name, horizon=horizon)
                    if effect["n"] >= 2:
                        sesoi = 0.1 * float(effect["left_mean"])
                        low, high = effect["ci90"]
                        effect["sesoi"] = sesoi
                        effect["equivalent"] = bool(low > -sesoi and high < sesoi)
                    else:
                        effect["equivalent"] = False
                    equivalence[case_name][horizon] = effect

        projection_control: dict[str, Any] = {}
        free_selection = system_lock["comparisons"].get("free__free_res", {}).get("left")
        if free_selection:
            free_records = _records_for_arm(records, key, free_selection)
            projection_selection = {**free_selection, "mechanism": "projection"}
            projection_records = _records_for_arm(records, key, projection_selection)
            for case_name in sorted(
                set(next(iter(free_records.values()))["cases"]) if free_records else set()
            ):
                projection_control[case_name] = {}
                horizons = sorted(next(iter(free_records.values()))["cases"][case_name], key=int)
                for horizon in horizons:
                    seeds = sorted(set(free_records) & set(projection_records))
                    relative_errors = []
                    absolute_errors = []
                    for seed in seeds:
                        base = free_records[seed]["cases"][case_name][horizon]["conserving_rmse"]
                        projected = projection_records[seed]["cases"][case_name][horizon]["conserving_rmse"]
                        absolute = abs(base - projected)
                        absolute_errors.append(absolute)
                        relative_errors.append(absolute / max(abs(base), np.finfo(float).tiny))
                    maximum = max(relative_errors, default=float("inf"))
                    maximum_absolute = max(absolute_errors, default=float("inf"))
                    projection_control[case_name][horizon] = {
                        "n": len(seeds),
                        "max_relative_error": maximum,
                        "max_absolute_error": maximum_absolute,
                        "algebraic_gate_applicable": horizon == "1",
                        "passes": (maximum <= 1e-5 or maximum_absolute <= 1e-8 if horizon == "1" else None),
                    }

        attribution: dict[str, Any] = {}
        parameter_result = comparisons.get("free__free_res")
        enforcement_result = comparisons.get("free_res__hard")
        if parameter_result and enforcement_result:
            common_cases = set(parameter_result["effects"]) & set(enforcement_result["effects"])
            for case_name in sorted(common_cases):
                attribution[case_name] = {}
                common_horizons = set(parameter_result["effects"][case_name]) & set(
                    enforcement_result["effects"][case_name]
                )
                for horizon in sorted(common_horizons, key=int):
                    parameter_effect = parameter_result["effects"][case_name][horizon]
                    enforcement_effect = enforcement_result["effects"][case_name][horizon]
                    if parameter_effect["n"] < 2 or enforcement_effect["n"] < 2:
                        attribution[case_name][horizon] = {"passes": False, "reason": "incomplete"}
                        continue
                    parameter_mean = float(parameter_effect["paired_mean_difference"])
                    enforcement_mean = float(enforcement_effect["paired_mean_difference"])
                    ratio = abs(parameter_mean) / max(abs(enforcement_mean), np.finfo(float).tiny)
                    parameter_ci = parameter_effect["ci95"]
                    parameter_excludes_zero = parameter_ci[0] > 0.0 or parameter_ci[1] < 0.0
                    equivalent = bool(
                        equivalence.get(case_name, {}).get(horizon, {}).get("equivalent", False)
                    )
                    overlaps = bool(
                        parameter_result["confirmation_overlap"]["passes"]
                        and enforcement_result["confirmation_overlap"]["passes"]
                    )
                    attribution[case_name][horizon] = {
                        "parameterization_mean_difference": parameter_mean,
                        "hard_enforcement_mean_difference": enforcement_mean,
                        "absolute_effect_ratio": ratio,
                        "parameterization_ci_excludes_zero": parameter_excludes_zero,
                        "hard_free_res_equivalent": equivalent,
                        "id_compute_overlap": overlaps,
                        "passes": bool(overlaps and equivalent and parameter_excludes_zero and ratio >= 2.0),
                    }

        soft_damage: dict[str, Any] = {}
        soft_result = comparisons.get("free__soft30")
        soft_pair = cached_arms.get("free__soft30")
        if soft_result and soft_pair:
            free_records, soft_records = soft_pair
            for case_name, horizons in soft_result["effects"].items():
                soft_damage[case_name] = {}
                for horizon, effect in horizons.items():
                    seeds = sorted(set(free_records) & set(soft_records))
                    free_drift = (
                        float(
                            np.mean(
                                [
                                    free_records[seed]["cases"][case_name][horizon]["invariant_drift"]
                                    for seed in seeds
                                ]
                            )
                        )
                        if seeds
                        else None
                    )
                    soft_drift = (
                        float(
                            np.mean(
                                [
                                    soft_records[seed]["cases"][case_name][horizon]["invariant_drift"]
                                    for seed in seeds
                                ]
                            )
                        )
                        if seeds
                        else None
                    )
                    ci = effect.get("ci95")
                    conserving_worse = bool(ci and ci[1] < 0.0)
                    no_drift_gain = bool(
                        free_drift is not None and soft_drift is not None and soft_drift >= free_drift
                    )
                    soft_damage[case_name][horizon] = {
                        "free_drift_mean": free_drift,
                        "soft30_drift_mean": soft_drift,
                        "soft30_conserving_worse": conserving_worse,
                        "no_invariant_drift_gain": no_drift_gain,
                        "dominated": conserving_worse and no_drift_gain,
                    }

        output["systems"][key] = {
            "family": system_lock["family"],
            "system": system_lock["system"],
            "comparisons": comparisons,
            "hard_free_res_equivalence": equivalence,
            "projection_control": projection_control,
            "attribution": attribution,
            "soft30_damage": soft_damage,
        }

    if primary_sign_tests:
        adjusted = holm_adjust([value for _, value in primary_sign_tests])
        output["primary_parameterization_holm"] = {
            key: {"raw_pvalue": raw, "holm_pvalue": corrected}
            for (key, raw), corrected in zip(primary_sign_tests, adjusted, strict=True)
        }
    return output


def validate_provenance(records: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    for record in records:
        provenance_record = record.get("provenance", {})
        required = (
            "git_head",
            "git_dirty",
            "source_sha256",
            "command",
            "resolved_config",
            "hostname",
            "python",
            "torch",
        )
        missing = [
            key
            for key in required
            if key not in provenance_record or provenance_record[key] in (None, {}, [])
        ]
        if missing:
            failures.append(f"{record.get('run_id', '<unknown>')}: missing {','.join(missing)}")
    return failures


def validate_confirmation_lock(
    records: list[dict[str, Any]], expected_sha256: str
) -> list[str]:
    """Reject confirmation records not bound to the exact analysis lock."""
    failures: list[str] = []
    for record in records:
        if record.get("stage") != "confirmation":
            continue
        run_id = str(record.get("run_id", "<unknown>"))
        observed = record.get("selection_lock_sha256")
        resolved = record.get("provenance", {}).get("resolved_config", {})
        resolved_observed = resolved.get("selection_lock_sha256")
        source_hashes = record.get("provenance", {}).get("source_sha256", {})
        if observed != expected_sha256:
            failures.append(
                f"{run_id}: record selection lock is {observed!r}, expected {expected_sha256}"
            )
        if resolved_observed != expected_sha256:
            failures.append(
                f"{run_id}: resolved-config selection lock is {resolved_observed!r}, "
                f"expected {expected_sha256}"
            )
        if expected_sha256 not in source_hashes.values():
            failures.append(f"{run_id}: selection lock is absent from provenance source hashes")
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    select_parser = subparsers.add_parser("select")
    select_parser.add_argument("--records", type=Path, nargs="+", required=True)
    select_parser.add_argument("--out", type=Path, required=True)
    confirm_parser = subparsers.add_parser("confirm")
    confirm_parser.add_argument("--records", type=Path, nargs="+", required=True)
    confirm_parser.add_argument("--lock", type=Path, required=True)
    confirm_parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    records = load_records(args.records)
    provenance_failures = validate_provenance(records)
    if provenance_failures:
        raise ValueError("invalid provenance:\n" + "\n".join(provenance_failures))
    if args.command == "select":
        result = select_pilot(records)
    else:
        lock = json.loads(args.lock.read_text(encoding="utf-8"))
        lock_sha256 = sha256_file(args.lock)
        lock_failures = validate_confirmation_lock(records, lock_sha256)
        if lock_failures:
            raise ValueError("invalid confirmation lock binding:\n" + "\n".join(lock_failures))
        result = analyze_confirmation(records, lock)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
