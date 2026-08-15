"""Rejected NEMDE group-tree candidate retained for reproducible negative evidence.

The consumed-case development run showed severe tail regressions. Do not use this adapter as a validated AEMO
evaluator; see the experiment result before importing it into any replay path.
"""

from __future__ import annotations

import copy
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, cast

GroupFreeEvaluator = Callable[[list[dict[str, Any]]], float]


class GroupStructureError(ValueError):
    """Raised when RPN group identifiers do not form an evaluable tree."""


@dataclass
class RpnGroupRepairStats:
    """Aggregate structural telemetry without term values."""

    rpn_call_count: int = 0
    grouped_rpn_call_count: int = 0
    group_evaluation_count: int = 0
    self_marked_anchor_count: int = 0
    maximum_group_depth: int = 0
    structure_error_count: int = 0

    def as_dict(self) -> dict[str, int]:
        """Return stable JSON-ready counters."""

        return {
            "rpn_call_count": self.rpn_call_count,
            "grouped_rpn_call_count": self.grouped_rpn_call_count,
            "group_evaluation_count": self.group_evaluation_count,
            "self_marked_anchor_count": self.self_marked_anchor_count,
            "maximum_group_depth": self.maximum_group_depth,
            "structure_error_count": self.structure_error_count,
        }


def _identifier(term: Mapping[str, Any], field: str) -> str | None:
    value = term.get(field)
    return str(value) if value is not None else None


class RpnGroupRepair:
    """Resolve `TermID`/`GroupTerm` hierarchy before calling Nempy's operators."""

    def __init__(self, group_free_evaluator: GroupFreeEvaluator) -> None:
        self._group_free_evaluator = group_free_evaluator
        self.stats = RpnGroupRepairStats()

    def __call__(self, equation: Sequence[Mapping[str, Any]]) -> float:
        """Evaluate one equation while preserving upstream non-group operations."""

        self.stats.rpn_call_count += 1
        terms = [copy.deepcopy(dict(term)) for term in equation]
        if not any("@GroupTerm" in term for term in terms):
            return float(self._group_free_evaluator(terms))
        self.stats.grouped_rpn_call_count += 1
        try:
            return self._evaluate_grouped(terms)
        except GroupStructureError:
            self.stats.structure_error_count += 1
            raise

    def _evaluate_grouped(self, terms: list[dict[str, Any]]) -> float:
        anchors: dict[str, int] = {}
        for index, term in enumerate(terms):
            if term.get("@SpdType") != "G":
                continue
            term_id = _identifier(term, "@TermID")
            if term_id is None:
                raise GroupStructureError("G term is missing @TermID")
            if term_id in anchors:
                raise GroupStructureError(f"duplicate G anchor TermID {term_id}")
            anchors[term_id] = index

        children: defaultdict[str, list[int]] = defaultdict(list)
        effective_parent: dict[int, str] = {}
        for index, term in enumerate(terms):
            group_id = _identifier(term, "@GroupTerm")
            if group_id is None:
                continue
            term_id = _identifier(term, "@TermID")
            self_marked = term.get("@SpdType") == "G" and term_id == group_id
            if self_marked:
                self.stats.self_marked_anchor_count += 1
                continue
            children[group_id].append(index)
            effective_parent[index] = group_id

        missing_anchors = sorted(group_id for group_id in children if group_id not in anchors)
        if missing_anchors:
            raise GroupStructureError("groups without G anchors: " + ",".join(missing_anchors))

        resolved_anchor_values: dict[str, float] = {}
        visiting: set[str] = set()
        visited_terms: set[int] = set()

        def resolve_term(index: int, depth: int) -> dict[str, Any]:
            term = copy.deepcopy(terms[index])
            term_id = _identifier(term, "@TermID")
            if term.get("@SpdType") == "G" and term_id in children:
                term["@Value"] = resolve_group(cast(str, term_id), depth + 1)
                term["@SpdType"] = "C"
            elif term.get("@SpdType") == "G" and "@Value" not in term:
                raise GroupStructureError(f"G anchor {term_id} has no group members")
            term.pop("@GroupTerm", None)
            visited_terms.add(index)
            return term

        def resolve_group(group_id: str, depth: int) -> float:
            if group_id in resolved_anchor_values:
                return resolved_anchor_values[group_id]
            if group_id in visiting:
                raise GroupStructureError(f"group cycle at {group_id}")
            visiting.add(group_id)
            self.stats.maximum_group_depth = max(self.stats.maximum_group_depth, depth)
            group_terms = [resolve_term(index, depth) for index in children[group_id]]
            if not group_terms:
                raise GroupStructureError(f"group {group_id} has no direct members")
            value = float(self._group_free_evaluator(group_terms))
            visiting.remove(group_id)
            resolved_anchor_values[group_id] = value
            self.stats.group_evaluation_count += 1
            return value

        root_indexes = [index for index in range(len(terms)) if index not in effective_parent]
        root_terms = [resolve_term(index, 0) for index in root_indexes]
        if len(visited_terms) != len(terms):
            unresolved = sorted(set(range(len(terms))) - visited_terms)
            unresolved_ids = [str(terms[index].get("@TermID", index)) for index in unresolved]
            raise GroupStructureError("unreachable group terms: " + ",".join(unresolved_ids))
        return float(self._group_free_evaluator(root_terms))


def install_rpn_group_repair(rhs_module: Any) -> RpnGroupRepair:
    """Replace only a loaded Nempy module's `_rpn_calc` entry point."""

    original = getattr(rhs_module, "_rpn_calc", None)
    if not callable(original):
        raise TypeError("rhs_module._rpn_calc is not callable")
    if isinstance(original, RpnGroupRepair):
        raise RuntimeError("RPN group repair is already installed")
    repair = RpnGroupRepair(cast(GroupFreeEvaluator, original))
    rhs_module._rpn_calc = repair
    return repair


def compare_repair_arms(
    references: Mapping[str, float],
    baseline: Sequence[Mapping[str, object]],
    repaired: Sequence[Mapping[str, object]],
    *,
    threshold: float = 1.0e-3,
) -> dict[str, object]:
    """Describe paired arm changes without retaining predicted or reference RHS values."""

    baseline_by_id = {str(item["constraint_id"]): item for item in baseline}
    repaired_by_id = {str(item["constraint_id"]): item for item in repaired}
    equation_ids = sorted(set(baseline_by_id) | set(repaired_by_id))
    recovered: list[str] = []
    new_failures: list[str] = []
    improved: list[tuple[float, str, float, float]] = []
    worsened: list[tuple[float, str, float, float]] = []
    ties = 0
    crossed_below: list[str] = []
    crossed_above: list[str] = []
    changed_prediction_count = 0
    for constraint_id in equation_ids:
        before = baseline_by_id.get(constraint_id)
        after = repaired_by_id.get(constraint_id)
        before_ok = before is not None and before.get("status") == "ok"
        after_ok = after is not None and after.get("status") == "ok"
        if not before_ok and after_ok:
            recovered.append(constraint_id)
        if before_ok and not after_ok:
            new_failures.append(constraint_id)
        if (
            before is None
            or after is None
            or before.get("status") != "ok"
            or after.get("status") != "ok"
            or constraint_id not in references
        ):
            continue
        if before.get("value_hex") != after.get("value_hex"):
            changed_prediction_count += 1
        reference = references[constraint_id]
        denominator = max(1.0, abs(reference))
        before_error = abs(float(cast(float, before["value"])) - reference) / denominator
        after_error = abs(float(cast(float, after["value"])) - reference) / denominator
        delta = before_error - after_error
        if delta > 0.0:
            improved.append((delta, constraint_id, before_error, after_error))
        elif delta < 0.0:
            worsened.append((-delta, constraint_id, before_error, after_error))
        else:
            ties += 1
        if before_error > threshold and after_error <= threshold:
            crossed_below.append(constraint_id)
        if before_error <= threshold and after_error > threshold:
            crossed_above.append(constraint_id)

    def top_changes(items: list[tuple[float, str, float, float]]) -> list[dict[str, object]]:
        ordered = sorted(items, key=lambda item: (-item[0], item[1]))[:25]
        return [
            {
                "constraint_id": constraint_id,
                "normalized_error_change": change,
                "baseline_normalized_error": before_error,
                "repaired_normalized_error": after_error,
            }
            for change, constraint_id, before_error, after_error in ordered
        ]

    return {
        "paired_equation_count": len(equation_ids),
        "recovered_error_count": len(recovered),
        "recovered_constraint_ids": recovered,
        "new_failure_count": len(new_failures),
        "new_failure_constraint_ids": new_failures,
        "changed_prediction_count_among_joint_successes": changed_prediction_count,
        "strict_improvement_count": len(improved),
        "strict_worsening_count": len(worsened),
        "exact_error_tie_count": ties,
        "crossed_below_1e-3_count": len(crossed_below),
        "crossed_below_1e-3_constraint_ids": crossed_below,
        "crossed_above_1e-3_count": len(crossed_above),
        "crossed_above_1e-3_constraint_ids": crossed_above,
        "top_25_improvements": top_changes(improved),
        "top_25_worsenings": top_changes(worsened),
    }
