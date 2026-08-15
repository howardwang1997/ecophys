from __future__ import annotations

from types import SimpleNamespace

import pytest

from ecomd.research.aemo_nemde_rpn_group_repair import (
    GroupStructureError,
    RpnGroupRepair,
    compare_repair_arms,
    install_rpn_group_repair,
)


def _linear_evaluator(equation: list[dict[str, object]]) -> float:
    total = 0.0
    for term in equation:
        assert "@GroupTerm" not in term
        assert term["@SpdType"] != "G"
        total += float(term["@Value"]) * float(term["@Multiplier"])
    return total


def test_official_page_38_group_known_answer() -> None:
    equation = [
        {"@TermID": "1", "@GroupTerm": "5", "@SpdType": "E", "@Multiplier": "1", "@Value": "1000"},
        {"@TermID": "2", "@GroupTerm": "5", "@SpdType": "A", "@Multiplier": "-1", "@Value": "400"},
        {"@TermID": "3", "@GroupTerm": "5", "@SpdType": "A", "@Multiplier": "-0.498", "@Value": "500"},
        {"@TermID": "4", "@GroupTerm": "5", "@SpdType": "C", "@Multiplier": "-25", "@Value": "1"},
        {"@TermID": "5", "@SpdType": "G", "@Multiplier": "4.197"},
        {"@TermID": "6", "@SpdType": "T", "@Multiplier": "-1", "@Value": "250"},
    ]

    assert RpnGroupRepair(_linear_evaluator)(equation) == pytest.approx(1118.222)


def test_nested_sibling_groups_use_ids_not_adjacency() -> None:
    equation = [
        {"@TermID": "10", "@GroupTerm": "30", "@SpdType": "G", "@Multiplier": "1"},
        {"@TermID": "1", "@GroupTerm": "10", "@SpdType": "C", "@Multiplier": "1", "@Value": "1"},
        {"@TermID": "20", "@GroupTerm": "30", "@SpdType": "G", "@Multiplier": "1"},
        {"@TermID": "2", "@GroupTerm": "10", "@SpdType": "C", "@Multiplier": "1", "@Value": "2"},
        {"@TermID": "3", "@GroupTerm": "20", "@SpdType": "C", "@Multiplier": "1", "@Value": "3"},
        {"@TermID": "4", "@GroupTerm": "20", "@SpdType": "C", "@Multiplier": "1", "@Value": "4"},
        {"@TermID": "30", "@SpdType": "G", "@Multiplier": "2"},
    ]
    repair = RpnGroupRepair(_linear_evaluator)

    assert repair(equation) == 20.0
    assert repair.stats.group_evaluation_count == 3
    assert repair.stats.maximum_group_depth == 2


def test_leading_self_marked_anchor_is_not_its_own_child() -> None:
    equation = [
        {"@TermID": "5", "@GroupTerm": "5", "@SpdType": "G", "@Multiplier": "3"},
        {"@TermID": "1", "@GroupTerm": "5", "@SpdType": "C", "@Multiplier": "1", "@Value": "1"},
        {"@TermID": "2", "@GroupTerm": "5", "@SpdType": "C", "@Multiplier": "1", "@Value": "2"},
    ]
    repair = RpnGroupRepair(_linear_evaluator)

    assert repair(equation) == 9.0
    assert repair.stats.self_marked_anchor_count == 1


def test_unknown_group_anchor_is_retained_as_structure_error() -> None:
    equation = [{"@TermID": "1", "@GroupTerm": "99", "@SpdType": "C", "@Multiplier": "1", "@Value": "1"}]
    repair = RpnGroupRepair(_linear_evaluator)

    with pytest.raises(GroupStructureError, match="groups without G anchors: 99"):
        repair(equation)
    assert repair.stats.structure_error_count == 1


def test_install_is_switchable_and_rejects_double_install() -> None:
    module = SimpleNamespace(_rpn_calc=_linear_evaluator)

    installed = install_rpn_group_repair(module)

    assert isinstance(installed, RpnGroupRepair)
    with pytest.raises(RuntimeError, match="already installed"):
        install_rpn_group_repair(module)


def test_paired_comparison_keeps_recoveries_and_regressions() -> None:
    baseline = [
        {"constraint_id": "A", "status": "error"},
        {"constraint_id": "B", "status": "ok", "value": 2.0, "value_hex": (2.0).hex()},
        {"constraint_id": "C", "status": "ok", "value": 10.0, "value_hex": (10.0).hex()},
    ]
    repaired = [
        {"constraint_id": "A", "status": "ok", "value": 1.0, "value_hex": (1.0).hex()},
        {"constraint_id": "B", "status": "error"},
        {"constraint_id": "C", "status": "ok", "value": 0.0, "value_hex": (0.0).hex()},
    ]

    comparison = compare_repair_arms({"A": 1.0, "B": 2.0, "C": 0.0}, baseline, repaired)

    assert comparison["recovered_constraint_ids"] == ["A"]
    assert comparison["new_failure_constraint_ids"] == ["B"]
    assert comparison["strict_improvement_count"] == 1
    assert comparison["crossed_below_1e-3_constraint_ids"] == ["C"]
