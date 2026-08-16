from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import cast

import pytest

from ecomd.research.executable_shock_trace_ir import (
    FAIL_DECISION,
    PASS_DECISION,
    GuardRejectedError,
    Instruction,
    canonical_program_hash,
    canonicalize_program,
    execute_program,
    generate_initial_states,
    generate_instruction_library,
    instructions_independent,
    load_json,
    parse_instruction,
    parse_program,
    run_feasibility,
    sha256_file,
    validate_manifest,
    validate_parent_files,
    verify_summary,
)

MANIFEST_PATH = Path("data/manifests/executable_shock_trace_ir_feasibility_v1.json")
PROTOCOL_COMMIT = "1" * 40


def test_manifest_and_parent_evidence_are_valid_and_claim_locked() -> None:
    manifest = load_json(MANIFEST_PATH)

    assert validate_manifest(manifest) == []
    assert validate_parent_files(manifest, Path.cwd()) == []

    changed = deepcopy(manifest)
    claims = cast(dict[str, object], changed["claim_boundary"])
    claims["new_theorem_claim_authorized"] = True
    assert "claim boundary differs from the frozen non-claim" in validate_manifest(changed)


def test_strict_instruction_schemas_derive_read_and_write_sets() -> None:
    set_value = parse_instruction({"instruction_id": "set_a", "opcode": "set", "target": "a", "value": 1})
    add_value = parse_instruction({"instruction_id": "add_a", "opcode": "add", "target": "a", "value": -1})
    copy_value = parse_instruction(
        {
            "instruction_id": "copy_b",
            "opcode": "copy",
            "target": "b",
            "source": "a",
            "offset": 2,
        }
    )
    guard = parse_instruction(
        {"instruction_id": "guard_a", "opcode": "require_equal", "source": "a", "value": 0}
    )

    assert set_value.reads == frozenset()
    assert set_value.writes == {"a"}
    assert add_value.reads == add_value.writes == {"a"}
    assert copy_value.reads == {"a"}
    assert copy_value.writes == {"b"}
    assert guard.reads == {"a"}
    assert guard.writes == frozenset()

    with pytest.raises(ValueError, match="exact integer"):
        parse_instruction({"instruction_id": "bad", "opcode": "set", "target": "a", "value": True})
    with pytest.raises(ValueError, match="strict set schema"):
        parse_instruction(
            {
                "instruction_id": "bad",
                "opcode": "set",
                "target": "a",
                "value": 1,
                "reads": [],
            }
        )
    with pytest.raises(ValueError, match="not allowed"):
        Instruction("bad", "unknown")
    with pytest.raises(ValueError, match="exact integer"):
        Instruction("bad", "add", target="a", value=True)


def test_interpreter_retains_round_trip_trace_and_fails_closed() -> None:
    program = parse_program(
        [
            {"instruction_id": "lower", "opcode": "set", "target": "asset.lt", "value": 1},
            {
                "instruction_id": "restore",
                "opcode": "set",
                "target": "asset.lt",
                "value": 8_000,
            },
        ]
    )
    result = execute_program({"asset.lt": 8_000}, program)

    assert result["terminal_delta"] == {}
    trace = cast(list[dict[str, object]], result["trace"])
    assert cast(dict[str, int], trace[0]["state_after"])["asset.lt"] == 1
    assert cast(dict[str, int], trace[1]["state_after"])["asset.lt"] == 8_000
    assert result["trace_sha256"] != execute_program({"asset.lt": 8_000}, ())["trace_sha256"]

    guard = parse_program([{"instruction_id": "guard", "opcode": "require_equal", "source": "a", "value": 0}])
    with pytest.raises(GuardRejectedError):
        execute_program({"a": 1}, guard)
    with pytest.raises(ValueError, match="missing coordinate"):
        execute_program(
            {"a": 0},
            (Instruction("missing", "set", target="b", value=1),),
        )


def test_independent_swaps_canonicalize_but_dependencies_keep_order() -> None:
    set_b = Instruction("z_set_b", "set", target="b", value=1)
    add_a = Instruction("a_add_a", "add", target="a", value=1)
    independent = (set_b, add_a)

    assert instructions_independent(*independent) is True
    assert (
        execute_program({"a": 0, "b": 0}, independent)["terminal_state"]
        == execute_program({"a": 0, "b": 0}, tuple(reversed(independent)))["terminal_state"]
    )
    assert [item.instruction_id for item in canonicalize_program(independent)] == [
        "a_add_a",
        "z_set_b",
    ]
    assert canonical_program_hash(independent) == canonical_program_hash(tuple(reversed(independent)))

    set_a = Instruction("a_set", "set", target="a", value=1)
    add_same = Instruction("z_add", "add", target="a", value=1)
    dependent = (set_a, add_same)
    reversed_dependent = tuple(reversed(dependent))

    assert instructions_independent(*dependent) is False
    assert cast(dict[str, int], execute_program({"a": 0}, dependent)["terminal_state"])["a"] == 2
    assert cast(dict[str, int], execute_program({"a": 0}, reversed_dependent)["terminal_state"])["a"] == 1
    assert canonicalize_program(dependent) == dependent
    assert canonicalize_program(reversed_dependent) == reversed_dependent
    assert canonical_program_hash(dependent) != canonical_program_hash(reversed_dependent)


def test_copy_and_sparse_terminal_support_are_exact() -> None:
    program = parse_program(
        [
            {"instruction_id": "cap", "opcode": "set", "target": "cap", "value": 20},
            {
                "instruction_id": "copy",
                "opcode": "copy",
                "target": "inventory",
                "source": "cap",
                "offset": -2,
            },
        ]
    )
    result = execute_program({"inventory": 10, "cap": 12, "fee": 3}, program)

    assert result["terminal_state"] == {"cap": 20, "fee": 3, "inventory": 18}
    assert result["terminal_delta"] == {"cap": 8, "inventory": 8}
    assert set(cast(dict[str, int], result["terminal_delta"])) <= set().union(
        *(instruction.writes for instruction in program)
    )


def test_generated_grid_has_frozen_cardinality() -> None:
    manifest = load_json(MANIFEST_PATH)
    instructions = generate_instruction_library(manifest)
    states = generate_initial_states(manifest)

    assert len(instructions) == 24
    assert len({item.instruction_id for item in instructions}) == 24
    assert len(states) == 125
    assert len(instructions) ** 2 * len(states) == 72_000


@pytest.fixture(scope="module")
def sealed_summary() -> dict[str, object]:
    return run_feasibility(
        load_json(MANIFEST_PATH),
        root=Path.cwd(),
        protocol_commit=PROTOCOL_COMMIT,
        manifest_sha256=sha256_file(MANIFEST_PATH),
        source_sha256=sha256_file("ecomd/research/executable_shock_trace_ir.py"),
    )


def test_full_generated_audit_passes_all_frozen_gates(
    sealed_summary: dict[str, object],
) -> None:
    assert sealed_summary["decision"] == PASS_DECISION
    assert sealed_summary["gate_counts"] == {"pass": 10, "fail": 0}
    evaluation = cast(dict[str, object], sealed_summary["evaluation"])
    assert evaluation["generated_case_count"] == 72_000
    assert evaluation["duplicate_id_schema_rejection_count"] == 3_000
    assert evaluation["determinism_violation_count"] == 0
    assert evaluation["support_violation_count"] == 0
    assert evaluation["independence_acceptance_violation_count"] == 0
    assert evaluation["independence_terminal_violation_count"] == 0
    assert evaluation["independent_canonical_hash_violation_count"] == 0
    assert sealed_summary["resource_use"] == {
        "generated_case_count": 72_000,
        "generated_case_cap": 100_000,
        "runtime_cap_seconds": 60,
        "network_calls": 0,
        "market_or_chain_rows_read": 0,
        "cpu_workers": 1,
        "gpu_hours": 0,
        "paid_data": False,
        "h20_used": False,
        "case_rows_retained": 0,
    }


def test_independent_reconstruction_rejects_tampering(
    sealed_summary: dict[str, object],
) -> None:
    manifest = load_json(MANIFEST_PATH)

    assert verify_summary(manifest, sealed_summary, root=Path.cwd()) == []

    tampered = deepcopy(sealed_summary)
    tampered["case_ledger_sha256"] = "0" * 64
    assert verify_summary(manifest, tampered, root=Path.cwd()) == [
        "summary differs from deterministic ESTIR reconstruction"
    ]
    assert tampered["decision"] != FAIL_DECISION
