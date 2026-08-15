"""Descriptive post-hoc diagnostics for the frozen NEMDE RHS error tail."""

from __future__ import annotations

import copy
import math
import tempfile
import traceback
from collections import Counter
from collections.abc import Callable, Mapping, Sequence, Set
from typing import Any, cast

TAIL_THRESHOLD = 1.0e-3
REPORT_THRESHOLDS = (1.0e-8, 1.0e-6, 1.0e-4, 1.0e-3, 1.0e-2, 1.0e-1)
TOP_K = 25


def _quantile(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * probability
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    weight = index - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _expanded_terms(
    equation: Sequence[Mapping[str, Any]],
    generic_equations: Mapping[str, Sequence[Mapping[str, Any]]],
    visited: frozenset[str] = frozenset(),
) -> list[Mapping[str, Any]]:
    expanded: list[Mapping[str, Any]] = []
    for term in equation:
        expanded.append(term)
        spd_id = term.get("@SpdID")
        if (
            term.get("@SpdType") == "X"
            and isinstance(spd_id, str)
            and spd_id in generic_equations
            and spd_id not in visited
        ):
            expanded.extend(_expanded_terms(generic_equations[spd_id], generic_equations, visited | {spd_id}))
    return expanded


def _counter(values: Sequence[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def describe_equation(
    equation: Sequence[Mapping[str, Any]],
    generic_equations: Mapping[str, Sequence[Mapping[str, Any]]],
    scada_data: Mapping[str, Mapping[str, Sequence[Mapping[str, Any]]]],
    *,
    unit_initial_ids: Set[str],
    entered_value_ids: Set[str],
    mnsp_from_ids: Set[str],
    mnsp_to_ids: Set[str],
) -> dict[str, object]:
    """Describe expression structure and input-resolution/SCADA-quality features without values."""

    direct = list(equation)
    expanded = _expanded_terms(direct, generic_equations)
    direct_operations = [cast(str, term.get("@Operation", "NONE")) for term in direct]
    expanded_operations = [cast(str, term.get("@Operation", "NONE")) for term in expanded]
    direct_types = [cast(str, term.get("@SpdType", "MISSING")) for term in direct]
    expanded_types = [cast(str, term.get("@SpdType", "MISSING")) for term in expanded]
    generic_refs = {
        cast(str, term["@SpdID"])
        for term in expanded
        if term.get("@SpdType") == "X"
        and isinstance(term.get("@SpdID"), str)
        and term["@SpdID"] in generic_equations
    }
    unresolved = 0
    scada_refs: set[tuple[str, str]] = set()
    for term in expanded:
        spd_type = term.get("@SpdType")
        spd_id = term.get("@SpdID")
        resolved = spd_type in {"C", "U", "G", "B"}
        if isinstance(spd_type, str) and isinstance(spd_id, str):
            if spd_type in {"A", "S", "R", "I", "W"}:
                rows = scada_data.get(spd_type, {}).get(spd_id, ())
                resolved = len(rows) > 0
                if rows:
                    scada_refs.add((spd_type, spd_id))
            elif spd_type == "T":
                resolved = spd_id in unit_initial_ids
            elif spd_type == "E":
                resolved = spd_id in entered_value_ids
            elif spd_type == "X":
                resolved = spd_id in generic_equations
            elif spd_type == "M":
                resolved = spd_id in mnsp_from_ids
            elif spd_type == "N":
                resolved = spd_id in mnsp_to_ids
        if not resolved:
            unresolved += 1

    scada_entries: list[Mapping[str, Any]] = []
    multiple_scada_ids = 0
    for spd_type, spd_id in sorted(scada_refs):
        rows = list(scada_data[spd_type][spd_id])
        scada_entries.extend(rows)
        if len(rows) > 1:
            multiple_scada_ids += 1

    def flag_count(key: str, expected: str | bool) -> int:
        return sum(row.get(key) == expected for row in scada_entries)

    return {
        "direct_term_count": len(direct),
        "expanded_term_count": len(expanded),
        "direct_operation_counts": _counter(direct_operations),
        "expanded_operation_counts": _counter(expanded_operations),
        "direct_spd_type_counts": _counter(direct_types),
        "expanded_spd_type_counts": _counter(expanded_types),
        "group_term_count": sum("@GroupTerm" in term for term in expanded),
        "default_term_count": sum("@Default" in term for term in expanded),
        "generic_reference_count": len(generic_refs),
        "branch_term_count": sum(term.get("@SpdType") == "B" for term in expanded),
        "unresolved_input_term_count": unresolved,
        "referenced_scada_id_count": len(scada_refs),
        "referenced_scada_entry_count": len(scada_entries),
        "multiple_entry_scada_id_count": multiple_scada_ids,
        "scada_good_values_false_count": flag_count("@GoodValues", False),
        "scada_ems_good_false_count": flag_count("@EMS_Good", "False"),
        "scada_ems_replaced_true_count": flag_count("@EMS_Replaced", "True"),
        "scada_can_use_value_false_count": flag_count("@Can_Use_Value", "False"),
    }


def _error_summary(values: list[float]) -> dict[str, float | None]:
    return {
        "median": _quantile(values, 0.5),
        "p95": _quantile(values, 0.95),
        "maximum": max(values) if values else None,
    }


def _slice(records: list[dict[str, object]]) -> dict[str, object]:
    values = [cast(float, record["normalized_error"]) for record in records]
    tail_count = sum(value > TAIL_THRESHOLD for value in values)
    return {
        "equation_count": len(records),
        "tail_count_above_1e-3": tail_count,
        "tail_fraction_above_1e-3": tail_count / len(records) if records else 0.0,
        "normalized_error": _error_summary(values),
    }


def _descriptor(record: Mapping[str, object]) -> Mapping[str, object]:
    descriptor = record.get("descriptor")
    if not isinstance(descriptor, Mapping):
        raise TypeError("diagnostic record descriptor is not a mapping")
    return cast(Mapping[str, object], descriptor)


def _count_names(record: Mapping[str, object], key: str) -> set[str]:
    counts = _descriptor(record).get(key)
    if not isinstance(counts, Mapping):
        raise TypeError(f"diagnostic descriptor {key} is not a mapping")
    return {str(name) for name in counts}


def summarize_records(
    records: list[dict[str, object]], failures: list[dict[str, object]]
) -> dict[str, object]:
    """Build the fixed threshold, top-error and feature/operation/type slices."""

    ordered = sorted(
        records,
        key=lambda record: (-cast(float, record["normalized_error"]), cast(str, record["constraint_id"])),
    )
    values = [cast(float, record["normalized_error"]) for record in records]
    exceedance = {
        f"{threshold:.0e}": {
            "count": sum(value > threshold for value in values),
            "fraction": sum(value > threshold for value in values) / len(values) if values else 0.0,
        }
        for threshold in REPORT_THRESHOLDS
    }
    feature_tests: dict[str, Callable[[Mapping[str, object]], bool]] = {
        "uses_group_terms": lambda item: cast(int, item["group_term_count"]) > 0,
        "uses_generic_equation": lambda item: cast(int, item["generic_reference_count"]) > 0,
        "uses_defaults": lambda item: cast(int, item["default_term_count"]) > 0,
        "uses_branch_term": lambda item: cast(int, item["branch_term_count"]) > 0,
        "has_unresolved_input": lambda item: cast(int, item["unresolved_input_term_count"]) > 0,
        "uses_multiple_scada_entries": lambda item: cast(int, item["multiple_entry_scada_id_count"]) > 0,
        "uses_good_values_false_scada": lambda item: cast(int, item["scada_good_values_false_count"]) > 0,
        "uses_ems_good_false_scada": lambda item: cast(int, item["scada_ems_good_false_count"]) > 0,
        "uses_replaced_scada": lambda item: cast(int, item["scada_ems_replaced_true_count"]) > 0,
        "uses_can_use_value_false_scada": lambda item: cast(int, item["scada_can_use_value_false_count"]) > 0,
    }
    feature_slices = {
        name: _slice([record for record in records if test(_descriptor(record))])
        for name, test in feature_tests.items()
    }
    operation_names = sorted(
        {operation for record in records for operation in _count_names(record, "expanded_operation_counts")}
    )
    operation_slices = {
        operation: _slice(
            [record for record in records if operation in _count_names(record, "expanded_operation_counts")]
        )
        for operation in operation_names
    }
    spd_types = sorted(
        {spd_type for record in records for spd_type in _count_names(record, "expanded_spd_type_counts")}
    )
    spd_type_slices = {
        spd_type: _slice(
            [record for record in records if spd_type in _count_names(record, "expanded_spd_type_counts")]
        )
        for spd_type in spd_types
    }
    return {
        "successful_scored_equation_count": len(records),
        "failed_equation_count": len(failures),
        "normalized_error": _error_summary(values),
        "threshold_exceedance": exceedance,
        "top_25_errors": ordered[:TOP_K],
        "failures": failures,
        "feature_slices": feature_slices,
        "operation_slices": operation_slices,
        "spd_type_slices": spd_type_slices,
    }


def diagnose_case(
    document: Mapping[str, Any],
    references: Mapping[str, float],
    xml_cache_class: type[Any],
    rhs_calculator_class: type[Any],
) -> dict[str, object]:
    """Evaluate one sentinel document and produce only the fixed derived diagnostic."""

    with tempfile.TemporaryDirectory(prefix="ecophys-nempy-rhs-diagnostic-") as cache:
        manager = xml_cache_class(cache)
        manager.xml = document
        engine = rhs_calculator_class(manager)
        generic_equations = cast(Mapping[str, Sequence[Mapping[str, Any]]], engine.generic_equations)
        raw_equations = cast(Mapping[str, Sequence[Mapping[str, Any]]], engine.rhs_constraint_equations)
        scada_data = cast(Mapping[str, Mapping[str, Sequence[Mapping[str, Any]]]], engine.scada_data)
        records: list[dict[str, object]] = []
        failures: list[dict[str, object]] = []
        for constraint_id in sorted(raw_equations):
            raw_equation = copy.deepcopy(raw_equations[constraint_id])
            descriptor = describe_equation(
                raw_equation,
                generic_equations,
                scada_data,
                unit_initial_ids=set(engine.unit_initial_mw),
                entered_value_ids=set(engine.entered_values),
                mnsp_from_ids=set(engine.msnsp_from_availbility),
                mnsp_to_ids=set(engine.msnsp_to_availbility),
            )
            try:
                prediction = float(engine.compute_constraint_rhs(constraint_id))
                if not math.isfinite(prediction):
                    raise ValueError("computed RHS is nonfinite")
                if constraint_id not in references:
                    raise KeyError("production reference absent")
                reference = references[constraint_id]
                absolute_error = abs(prediction - reference)
                records.append(
                    {
                        "constraint_id": constraint_id,
                        "absolute_error": absolute_error,
                        "normalized_error": absolute_error / max(1.0, abs(reference)),
                        "descriptor": descriptor,
                    }
                )
            except Exception as error:
                frames = traceback.extract_tb(error.__traceback__)
                terminal = frames[-1] if frames else None
                failures.append(
                    {
                        "constraint_id": constraint_id,
                        "error_type": type(error).__name__,
                        "error_message": str(error)[:500],
                        "terminal_function": terminal.name if terminal else None,
                        "terminal_line": terminal.lineno if terminal else None,
                        "descriptor": descriptor,
                    }
                )
    return summarize_records(records, failures)
