from __future__ import annotations

from ecomd.research.aemo_nemde_rhs_tail_diagnostic import describe_equation, summarize_records


def test_descriptor_expands_generic_equations_and_reports_scada_quality() -> None:
    equation = [
        {"@SpdID": "GENERIC", "@SpdType": "X", "@Multiplier": "1", "@Operation": "ADD"},
        {"@SpdID": "UNIT", "@SpdType": "T", "@Multiplier": "1"},
    ]
    generic = {
        "GENERIC": [
            {
                "@SpdID": "SCADA",
                "@SpdType": "A",
                "@Multiplier": "1",
                "@Operation": "PUSH",
                "@Default": "0",
                "@GroupTerm": "1",
            }
        ]
    }
    scada = {
        "A": {
            "SCADA": [
                {
                    "@GoodValues": False,
                    "@EMS_Good": "False",
                    "@EMS_Replaced": "True",
                    "@Can_Use_Value": "False",
                },
                {"@GoodValues": True},
            ]
        }
    }

    descriptor = describe_equation(
        equation,
        generic,
        scada,
        unit_initial_ids={"UNIT"},
        entered_value_ids=set(),
        mnsp_from_ids=set(),
        mnsp_to_ids=set(),
    )

    assert descriptor["expanded_term_count"] == 3
    assert descriptor["generic_reference_count"] == 1
    assert descriptor["multiple_entry_scada_id_count"] == 1
    assert descriptor["scada_good_values_false_count"] == 1
    assert descriptor["scada_ems_replaced_true_count"] == 1
    assert descriptor["unresolved_input_term_count"] == 0


def _record(constraint_id: str, error: float, operation: str, spd_type: str) -> dict[str, object]:
    return {
        "constraint_id": constraint_id,
        "absolute_error": error,
        "normalized_error": error,
        "descriptor": {
            "group_term_count": 0,
            "generic_reference_count": 0,
            "default_term_count": 0,
            "branch_term_count": 0,
            "unresolved_input_term_count": 0,
            "multiple_entry_scada_id_count": 0,
            "scada_good_values_false_count": 0,
            "scada_ems_good_false_count": 0,
            "scada_ems_replaced_true_count": 0,
            "scada_can_use_value_false_count": 0,
            "expanded_operation_counts": {operation: 1},
            "expanded_spd_type_counts": {spd_type: 1},
        },
    }


def test_summary_keeps_all_records_and_orders_top_errors_deterministically() -> None:
    records = [
        _record("B", 0.2, "ADD", "A"),
        _record("A", 0.2, "ADD", "A"),
        _record("C", 1.0e-4, "PUSH", "T"),
    ]
    failures = [{"constraint_id": "D", "error_type": "IndexError"}]

    summary = summarize_records(records, failures)

    assert summary["successful_scored_equation_count"] == 3
    assert summary["failed_equation_count"] == 1
    assert [item["constraint_id"] for item in summary["top_25_errors"]] == ["A", "B", "C"]
    assert summary["threshold_exceedance"]["1e-03"]["count"] == 2
    assert summary["operation_slices"]["ADD"]["tail_count_above_1e-3"] == 2
    assert summary["spd_type_slices"]["T"]["tail_count_above_1e-3"] == 0
