"""Exact-integer executable shock trace IR feasibility audit."""

from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import re
import subprocess
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import cast

SCHEMA_VERSION = "ecophys-executable-shock-trace-ir-feasibility/v1"
ARTIFACT_SCHEMA_VERSION = "ecophys-executable-shock-trace-ir-summary/v1"
AUDIT_ID = "executable_shock_trace_ir_feasibility_v1"
MANIFEST_RELATIVE_PATH = Path("data/manifests/executable_shock_trace_ir_feasibility_v1.json")
SOURCE_RELATIVE_PATH = Path("ecomd/research/executable_shock_trace_ir.py")
PASS_DECISION = "PASS_ESTIR_SOFTWARE_FEASIBILITY_AUTHORIZE_COMPILER_FIXTURES_ONLY"
FAIL_DECISION = "FAIL_ESTIR_UNDERSPECIFIED_KEEP_EMPIRICAL_COMPILER_AND_GPU_LOCKED"
HEX_SHA_PATTERN = re.compile(r"[0-9a-f]{64}")
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
ALLOWED_OPCODES = ("set", "add", "copy", "require_equal")
REQUIRED_GATES = (
    "manifest_and_parent_integrity",
    "instruction_schema_fail_closed",
    "interpreter_determinism",
    "certified_independence_commutation",
    "dependency_witness_nonzero_commutator",
    "canonical_hash_independent_swap_invariance",
    "terminal_collision_trace_separation",
    "sparse_support_containment",
    "two_fixture_families",
    "access_and_claim_boundary",
)

EXPECTED_PARENTS: dict[str, object] = {
    "bundle_manifest_path": "data/manifests/aave_v3_bundle_structure_feasibility_v1.yaml",
    "bundle_manifest_sha256": "e8cf60b2577bdf9e46f68f15c0c7e21931a3d705357420a907b75d74838a65e0",
    "bundle_result_path": "experiments/v14_aave_v3_bundle_structure_feasibility/RESULTS.md",
    "bundle_result_sha256": "08383a129202f720f12920644cb05399ddc402e05b9687a9ff73f1ecebea68f2",
    "bundle_summary_path": ("experiments/v14_aave_v3_bundle_structure_feasibility/artifacts/summary.json"),
    "bundle_summary_sha256": "922312a9c75a64cfe66a1ef828140df938929e4bc6fbac9200a3a1f6fa9d9db9",
    "transport_repair_result_path": ("experiments/v14_aave_v3_b0_transport_canary_repair/RESULTS.md"),
    "transport_repair_result_sha256": ("7acdc245a33355c70c22e04ada738155e05c37ee6c11aa814e1677c0a508450e"),
    "transport_repair_summary_path": (
        "experiments/v14_aave_v3_b0_transport_canary_repair/artifacts/summary.json"
    ),
    "transport_repair_summary_sha256": ("4cd70d0ef198a88f8e2e6014cbb4de10c24a2f357259432212bdc2a57fe4df33"),
    "expected_bundle_decision": (
        "COMPLETE_DEVELOPMENT_BUNDLE_STRUCTURE_AUTHORIZE_VECTOR_COMPILER_PROTOCOL_DESIGN_ONLY"
    ),
    "expected_transport_decision": ("FAIL_TARGET_ROW_FREE_TRANSPORT_REPAIR_KEEP_B0_V2_B1_G1_GPU_LOCKED"),
}


class DuplicateKeyError(ValueError):
    """Raised when a JSON object repeats a key."""


class GuardRejectedError(ValueError):
    """Raised when an exact program guard rejects its input state."""


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def load_json(path: str | Path) -> dict[str, object]:
    """Load a JSON mapping while rejecting duplicate keys."""

    value: object = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return cast(dict[str, object], value)


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 digest of one file."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _sequence(value: object) -> Sequence[object] | None:
    if isinstance(value, str) or not isinstance(value, Sequence):
        return None
    return cast(Sequence[object], value)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _exact_int(value: object, *, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{path} must be an exact integer")
    return value


def _name(value: object, *, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{path} must be a nonempty string")
    return value


def validate_manifest(manifest: Mapping[str, object]) -> list[str]:
    """Validate the complete frozen ESTIR feasibility contract."""

    errors: list[str] = []
    expected_keys = {
        "schema_version",
        "audit_id",
        "as_of",
        "stage",
        "parents",
        "claim_boundary",
        "state_domain",
        "instruction_contract",
        "canonicalization",
        "evaluation",
        "frozen_witnesses",
        "gates",
        "resources",
        "decision_policy",
    }
    if set(manifest) != expected_keys:
        errors.append("manifest root keys differ from the frozen ESTIR contract")
    if manifest.get("schema_version") != SCHEMA_VERSION or manifest.get("audit_id") != AUDIT_ID:
        errors.append("schema or audit ID differs from the frozen ESTIR contract")
    if manifest.get("as_of") != "2026-08-17" or manifest.get("stage") != (
        "generated_zero_network_exact_integer_ir_feasibility"
    ):
        errors.append("date or stage differs from the frozen ESTIR contract")
    if manifest.get("parents") != EXPECTED_PARENTS:
        errors.append("parent evidence differs from the frozen values")
    expected_claims = {
        "development_only": True,
        "new_theorem_claim_authorized": False,
        "full_evm_semantics_claim_authorized": False,
        "empirical_aave_compiler_claim_authorized": False,
        "b0_v2_authorized": False,
        "b1_empirical_compiler_authorized": False,
        "account_or_outcome_access_authorized": False,
        "g1_or_gpu_authorized": False,
    }
    if manifest.get("claim_boundary") != expected_claims:
        errors.append("claim boundary differs from the frozen non-claim")
    expected_domain = {
        "exhaustive_coordinate_names": ["a", "b", "c"],
        "initial_values": [-2, -1, 0, 1, 2],
        "exact_integer_only": True,
        "booleans_rejected_as_integers": True,
        "missing_coordinate_action": "fail",
    }
    if manifest.get("state_domain") != expected_domain:
        errors.append("state domain differs from the frozen exact-integer grid")
    expected_instruction = {
        "allowed_opcodes": list(ALLOWED_OPCODES),
        "read_write_sets_derived_from_opcode": True,
        "unique_instruction_ids_required": True,
        "unknown_fields_forbidden": True,
        "set_values": [-1, 0, 1],
        "add_values": [-1, 1],
        "copy_offsets": [0],
        "require_equal_values": [0],
        "expected_generated_instruction_count": 24,
    }
    if manifest.get("instruction_contract") != expected_instruction:
        errors.append("instruction contract differs from the frozen primitive library")
    expected_canonicalization = {
        "independence_rule": ("Wi_intersect_Rj_union_Wj_and_Wj_intersect_Ri_union_Wi_are_both_empty"),
        "dependency_edges_preserve_original_conflicting_order": True,
        "topological_tie_breaker": "instruction_id_lexicographic",
        "canonical_hash_encoding": "sorted_key_compact_json_sha256",
        "guards_must_preserve_acceptance_under_certified_swaps": True,
    }
    if manifest.get("canonicalization") != expected_canonicalization:
        errors.append("canonicalization contract differs from the frozen dependency rule")
    expected_evaluation = {
        "ordered_instruction_pairs": True,
        "all_initial_state_cartesian_products": True,
        "expected_initial_state_count": 125,
        "maximum_generated_cases": 100_000,
        "repeat_each_successful_execution": 2,
        "retain_case_rows": False,
        "retain_case_ledger_sha256": True,
    }
    if manifest.get("evaluation") != expected_evaluation:
        errors.append("evaluation grid differs from the frozen exhaustive contract")
    if manifest.get("frozen_witnesses") != _expected_witnesses():
        errors.append("frozen witnesses differ from the preregistered values")
    if manifest.get("gates") != list(REQUIRED_GATES):
        errors.append("gates differ from the ten conjunctive requirements")
    expected_resources = {
        "network_calls": 0,
        "market_or_chain_rows_read": 0,
        "maximum_runtime_seconds": 60,
        "maximum_output_bytes": 1_048_576,
        "cpu_workers": 1,
        "gpu_hours": 0,
        "paid_data": False,
        "h20_used": False,
    }
    if manifest.get("resources") != expected_resources:
        errors.append("resource boundary differs from the frozen zero-network budget")
    expected_decision = {
        "all_gates_required": True,
        "pass": PASS_DECISION,
        "fail": FAIL_DECISION,
        "authorized_next_stage": "compiler_fixture_and_specification_extension_only",
    }
    if manifest.get("decision_policy") != expected_decision:
        errors.append("decision policy differs from the frozen values")
    return errors


def _expected_witnesses() -> dict[str, object]:
    return {
        "independent_swap": {
            "initial_state": {"a": 0, "b": 0, "c": 0},
            "instructions": [
                {"instruction_id": "z_set_b", "opcode": "set", "target": "b", "value": 1},
                {"instruction_id": "a_add_a", "opcode": "add", "target": "a", "value": 1},
            ],
        },
        "dependent_noncommuting": {
            "initial_state": {"a": 0, "b": 0, "c": 0},
            "instructions": [
                {"instruction_id": "a_set", "opcode": "set", "target": "a", "value": 1},
                {"instruction_id": "z_add", "opcode": "add", "target": "a", "value": 1},
            ],
            "expected_forward_a": 2,
            "expected_reverse_a": 1,
        },
        "aave_like_terminal_collision": {
            "initial_state": {"asset.lt": 8_000},
            "round_trip_program": [
                {
                    "instruction_id": "lower",
                    "opcode": "set",
                    "target": "asset.lt",
                    "value": 1,
                },
                {
                    "instruction_id": "restore",
                    "opcode": "set",
                    "target": "asset.lt",
                    "value": 8_000,
                },
            ],
            "no_op_program": [],
            "expected_terminal_delta": {},
            "expected_transient_value": 1,
        },
        "generic_inventory_order": {
            "initial_state": {"inventory": 10, "cap": 12},
            "instructions": [
                {
                    "instruction_id": "set_cap",
                    "opcode": "set",
                    "target": "cap",
                    "value": 20,
                },
                {
                    "instruction_id": "copy_cap",
                    "opcode": "copy",
                    "target": "inventory",
                    "source": "cap",
                    "offset": 0,
                },
            ],
            "expected_forward_inventory": 20,
            "expected_reverse_inventory": 12,
        },
    }


def validate_parent_files(manifest: Mapping[str, object], root: str | Path) -> list[str]:
    """Verify every immutable result used to motivate this generated audit."""

    parents = _mapping(manifest.get("parents"))
    if parents is None:
        return ["parents must be a mapping"]
    errors: list[str] = []
    root_path = Path(root)
    pairs = (
        ("bundle_manifest_path", "bundle_manifest_sha256"),
        ("bundle_result_path", "bundle_result_sha256"),
        ("bundle_summary_path", "bundle_summary_sha256"),
        ("transport_repair_result_path", "transport_repair_result_sha256"),
        ("transport_repair_summary_path", "transport_repair_summary_sha256"),
    )
    for path_key, hash_key in pairs:
        relative = parents.get(path_key)
        expected_hash = parents.get(hash_key)
        if not isinstance(relative, str) or not isinstance(expected_hash, str):
            errors.append(f"invalid parent identity fields: {path_key}/{hash_key}")
            continue
        target = root_path / relative
        if not target.is_file():
            errors.append(f"missing parent file: {relative}")
        elif sha256_file(target) != expected_hash:
            errors.append(f"parent hash mismatch: {relative}")
    if errors:
        return errors
    bundle_summary = load_json(root_path / cast(str, parents["bundle_summary_path"]))
    transport_summary = load_json(root_path / cast(str, parents["transport_repair_summary_path"]))
    if bundle_summary.get("decision") != parents.get("expected_bundle_decision"):
        errors.append("bundle parent decision differs from the frozen development result")
    if (
        transport_summary.get("decision") != parents.get("expected_transport_decision")
        or transport_summary.get("validation_errors") != []
        or transport_summary.get("selected_host") is not None
        or transport_summary.get("target_row_count_retained") != 0
        or transport_summary.get("gpu_used") is not False
    ):
        errors.append("transport parent differs from the frozen zero-row failure")
    for result_key, decision_key in (
        ("bundle_result_path", "expected_bundle_decision"),
        ("transport_repair_result_path", "expected_transport_decision"),
    ):
        text = (root_path / cast(str, parents[result_key])).read_text(encoding="utf-8")
        if cast(str, parents[decision_key]) not in text:
            errors.append(f"{result_key} does not contain its frozen decision")
    return errors


@dataclass(frozen=True)
class Instruction:
    """One strict exact-integer ESTIR primitive."""

    instruction_id: str
    opcode: str
    target: str | None = None
    source: str | None = None
    value: int | None = None
    offset: int | None = None

    def __post_init__(self) -> None:
        _name(self.instruction_id, path="instruction.instruction_id")
        if self.opcode not in ALLOWED_OPCODES:
            raise ValueError(f"instruction.opcode is not allowed: {self.opcode}")
        if self.opcode in {"set", "add"}:
            _name(self.target, path="instruction.target")
            _exact_int(self.value, path="instruction.value")
            if self.source is not None or self.offset is not None:
                raise ValueError(f"{self.opcode} contains fields from another opcode")
        elif self.opcode == "copy":
            _name(self.target, path="instruction.target")
            _name(self.source, path="instruction.source")
            _exact_int(self.offset, path="instruction.offset")
            if self.value is not None:
                raise ValueError("copy contains fields from another opcode")
        else:
            _name(self.source, path="instruction.source")
            _exact_int(self.value, path="instruction.value")
            if self.target is not None or self.offset is not None:
                raise ValueError("require_equal contains fields from another opcode")

    @property
    def reads(self) -> frozenset[str]:
        if self.opcode == "add":
            return frozenset((cast(str, self.target),))
        if self.opcode in {"copy", "require_equal"}:
            return frozenset((cast(str, self.source),))
        return frozenset()

    @property
    def writes(self) -> frozenset[str]:
        if self.opcode in {"set", "add", "copy"}:
            return frozenset((cast(str, self.target),))
        return frozenset()

    def to_mapping(self) -> dict[str, object]:
        if self.opcode in {"set", "add"}:
            return {
                "instruction_id": self.instruction_id,
                "opcode": self.opcode,
                "target": self.target,
                "value": self.value,
            }
        if self.opcode == "copy":
            return {
                "instruction_id": self.instruction_id,
                "opcode": self.opcode,
                "target": self.target,
                "source": self.source,
                "offset": self.offset,
            }
        return {
            "instruction_id": self.instruction_id,
            "opcode": self.opcode,
            "source": self.source,
            "value": self.value,
        }


def parse_instruction(value: Mapping[str, object], *, path: str = "instruction") -> Instruction:
    """Parse one opcode with exact per-opcode keys."""

    instruction_id = _name(value.get("instruction_id"), path=f"{path}.instruction_id")
    opcode = _name(value.get("opcode"), path=f"{path}.opcode")
    if opcode not in ALLOWED_OPCODES:
        raise ValueError(f"{path}.opcode is not allowed: {opcode}")
    if opcode in {"set", "add"}:
        expected_keys = {"instruction_id", "opcode", "target", "value"}
        if set(value) != expected_keys:
            raise ValueError(f"{path} keys differ from the strict {opcode} schema")
        return Instruction(
            instruction_id=instruction_id,
            opcode=opcode,
            target=_name(value["target"], path=f"{path}.target"),
            value=_exact_int(value["value"], path=f"{path}.value"),
        )
    if opcode == "copy":
        expected_keys = {"instruction_id", "opcode", "target", "source", "offset"}
        if set(value) != expected_keys:
            raise ValueError(f"{path} keys differ from the strict copy schema")
        return Instruction(
            instruction_id=instruction_id,
            opcode=opcode,
            target=_name(value["target"], path=f"{path}.target"),
            source=_name(value["source"], path=f"{path}.source"),
            offset=_exact_int(value["offset"], path=f"{path}.offset"),
        )
    expected_keys = {"instruction_id", "opcode", "source", "value"}
    if set(value) != expected_keys:
        raise ValueError(f"{path} keys differ from the strict require_equal schema")
    return Instruction(
        instruction_id=instruction_id,
        opcode=opcode,
        source=_name(value["source"], path=f"{path}.source"),
        value=_exact_int(value["value"], path=f"{path}.value"),
    )


def parse_program(values: Sequence[object], *, path: str = "program") -> tuple[Instruction, ...]:
    """Parse an ordered program and reject duplicate instruction IDs."""

    instructions: list[Instruction] = []
    for index, value in enumerate(values):
        item = _mapping(value)
        if item is None:
            raise ValueError(f"{path}[{index}] must be a mapping")
        instructions.append(parse_instruction(item, path=f"{path}[{index}]"))
    ids = [item.instruction_id for item in instructions]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{path} contains duplicate instruction IDs")
    return tuple(instructions)


def _validate_state(initial_state: Mapping[str, object]) -> dict[str, int]:
    state: dict[str, int] = {}
    for coordinate, value in initial_state.items():
        name = _name(coordinate, path="state coordinate")
        state[name] = _exact_int(value, path=f"state.{name}")
    if not state:
        raise ValueError("state must contain at least one coordinate")
    return state


def _require_coordinates(state: Mapping[str, int], instruction: Instruction) -> None:
    for coordinate in instruction.reads | instruction.writes:
        if coordinate not in state:
            raise ValueError(
                f"instruction {instruction.instruction_id} references missing coordinate {coordinate}"
            )


def execute_program(
    initial_state: Mapping[str, object], instructions: Sequence[Instruction]
) -> dict[str, object]:
    """Execute one ordered atomic program and retain its normalized trace."""

    ids = [item.instruction_id for item in instructions]
    if len(ids) != len(set(ids)):
        raise ValueError("program contains duplicate instruction IDs")
    original = _validate_state(initial_state)
    state = dict(original)
    trace: list[dict[str, object]] = []
    for index, instruction in enumerate(instructions):
        _require_coordinates(state, instruction)
        read_values = {name: state[name] for name in sorted(instruction.reads)}
        write_values_before = {name: state[name] for name in sorted(instruction.writes)}
        if instruction.opcode == "require_equal":
            source = cast(str, instruction.source)
            if state[source] != instruction.value:
                raise GuardRejectedError(
                    f"guard {instruction.instruction_id} rejected {source}={state[source]}"
                )
        elif instruction.opcode == "set":
            state[cast(str, instruction.target)] = cast(int, instruction.value)
        elif instruction.opcode == "add":
            target = cast(str, instruction.target)
            state[target] += cast(int, instruction.value)
        elif instruction.opcode == "copy":
            state[cast(str, instruction.target)] = state[cast(str, instruction.source)] + cast(
                int, instruction.offset
            )
        else:
            raise AssertionError(f"unreachable opcode: {instruction.opcode}")
        write_values_after = {name: state[name] for name in sorted(instruction.writes)}
        trace.append(
            {
                "step": index,
                "instruction": instruction.to_mapping(),
                "read_values": read_values,
                "write_values_before": write_values_before,
                "write_values_after": write_values_after,
                "changed_coordinates": sorted(
                    name
                    for name in instruction.writes
                    if write_values_before[name] != write_values_after[name]
                ),
                "state_after": dict(sorted(state.items())),
            }
        )
    terminal_delta = {
        name: state[name] - original[name] for name in sorted(original) if state[name] != original[name]
    }
    return {
        "terminal_state": dict(sorted(state.items())),
        "terminal_delta": terminal_delta,
        "trace": trace,
        "trace_sha256": hashlib.sha256(_canonical_bytes(trace)).hexdigest(),
    }


def instructions_independent(left: Instruction, right: Instruction) -> bool:
    """Apply the frozen symmetric read/write conflict criterion."""

    return not (left.writes & (right.reads | right.writes) or right.writes & (left.reads | left.writes))


def canonicalize_program(instructions: Sequence[Instruction]) -> tuple[Instruction, ...]:
    """Canonicalize only orders not constrained by a read/write dependency edge."""

    ids = [item.instruction_id for item in instructions]
    if len(ids) != len(set(ids)):
        raise ValueError("program contains duplicate instruction IDs")
    successors: list[list[int]] = [[] for _ in instructions]
    indegree = [0 for _ in instructions]
    for left_index, left in enumerate(instructions):
        for right_index in range(left_index + 1, len(instructions)):
            if not instructions_independent(left, instructions[right_index]):
                successors[left_index].append(right_index)
                indegree[right_index] += 1
    ready = [
        (instruction.instruction_id, index)
        for index, instruction in enumerate(instructions)
        if indegree[index] == 0
    ]
    heapq.heapify(ready)
    ordered: list[Instruction] = []
    while ready:
        _, index = heapq.heappop(ready)
        ordered.append(instructions[index])
        for successor in successors[index]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                instruction = instructions[successor]
                heapq.heappush(ready, (instruction.instruction_id, successor))
    if len(ordered) != len(instructions):
        raise AssertionError("forward-only dependency graph unexpectedly contains a cycle")
    return tuple(ordered)


def canonical_program_hash(instructions: Sequence[Instruction]) -> str:
    """Hash the deterministic dependency-preserving program order."""

    canonical = [item.to_mapping() for item in canonicalize_program(instructions)]
    return hashlib.sha256(_canonical_bytes(canonical)).hexdigest()


def _integer_token(value: int) -> str:
    if value < 0:
        return f"m{abs(value)}"
    if value > 0:
        return f"p{value}"
    return "z0"


def generate_instruction_library(manifest: Mapping[str, object]) -> tuple[Instruction, ...]:
    """Generate the exact 24-instruction exhaustive library."""

    domain = cast(Mapping[str, object], manifest["state_domain"])
    contract = cast(Mapping[str, object], manifest["instruction_contract"])
    coordinates = cast(Sequence[str], domain["exhaustive_coordinate_names"])
    result: list[Instruction] = []
    for coordinate in coordinates:
        for value in cast(Sequence[int], contract["set_values"]):
            result.append(
                Instruction(
                    instruction_id=f"set_{coordinate}_{_integer_token(value)}",
                    opcode="set",
                    target=coordinate,
                    value=value,
                )
            )
    for coordinate in coordinates:
        for value in cast(Sequence[int], contract["add_values"]):
            result.append(
                Instruction(
                    instruction_id=f"add_{coordinate}_{_integer_token(value)}",
                    opcode="add",
                    target=coordinate,
                    value=value,
                )
            )
    for target in coordinates:
        for source in coordinates:
            if target == source:
                continue
            for offset in cast(Sequence[int], contract["copy_offsets"]):
                result.append(
                    Instruction(
                        instruction_id=f"copy_{source}_to_{target}_{_integer_token(offset)}",
                        opcode="copy",
                        target=target,
                        source=source,
                        offset=offset,
                    )
                )
    for source in coordinates:
        for value in cast(Sequence[int], contract["require_equal_values"]):
            result.append(
                Instruction(
                    instruction_id=f"require_{source}_{_integer_token(value)}",
                    opcode="require_equal",
                    source=source,
                    value=value,
                )
            )
    expected = cast(int, contract["expected_generated_instruction_count"])
    if len(result) != expected or len({item.instruction_id for item in result}) != expected:
        raise AssertionError("generated instruction library differs from the frozen cardinality")
    return tuple(result)


def generate_initial_states(manifest: Mapping[str, object]) -> tuple[dict[str, int], ...]:
    """Generate the exact 125-state Cartesian grid."""

    domain = cast(Mapping[str, object], manifest["state_domain"])
    coordinates = cast(Sequence[str], domain["exhaustive_coordinate_names"])
    values = cast(Sequence[int], domain["initial_values"])
    states = tuple(
        dict(zip(coordinates, combination, strict=True)) for combination in product(values, repeat=3)
    )
    if len(states) != cast(Mapping[str, object], manifest["evaluation"])["expected_initial_state_count"]:
        raise AssertionError("generated state grid differs from the frozen cardinality")
    return states


def _execution_status(
    initial_state: Mapping[str, object], instructions: Sequence[Instruction]
) -> tuple[str, dict[str, object] | None]:
    try:
        return "success", execute_program(initial_state, instructions)
    except GuardRejectedError:
        return "guard_rejected", None


def _schema_rejection_checks() -> dict[str, bool]:
    checks: dict[str, bool] = {}

    def rejects(action: Callable[[], object]) -> bool:
        try:
            action()
        except ValueError:
            return True
        return False

    checks["unknown_opcode"] = rejects(
        lambda: parse_instruction({"instruction_id": "x", "opcode": "unknown"})
    )
    checks["unknown_field"] = rejects(
        lambda: parse_instruction(
            {"instruction_id": "x", "opcode": "set", "target": "a", "value": 1, "extra": 0}
        )
    )
    checks["boolean_integer"] = rejects(
        lambda: parse_instruction({"instruction_id": "x", "opcode": "set", "target": "a", "value": True})
    )
    checks["duplicate_instruction_id"] = rejects(
        lambda: parse_program(
            [
                {"instruction_id": "x", "opcode": "set", "target": "a", "value": 1},
                {"instruction_id": "x", "opcode": "set", "target": "b", "value": 1},
            ]
        )
    )
    missing = parse_program([{"instruction_id": "x", "opcode": "set", "target": "missing", "value": 1}])
    checks["missing_coordinate"] = rejects(lambda: execute_program({"a": 0}, missing))
    return checks


def _run_exhaustive_grid(
    manifest: Mapping[str, object],
) -> tuple[dict[str, object], str]:
    library = generate_instruction_library(manifest)
    states = generate_initial_states(manifest)
    evaluation = cast(Mapping[str, object], manifest["evaluation"])
    maximum_cases = cast(int, evaluation["maximum_generated_cases"])
    ledger_hash = hashlib.sha256()
    counts = {
        "generated_case_count": 0,
        "duplicate_id_schema_rejection_count": 0,
        "successful_forward_case_count": 0,
        "guard_rejected_forward_case_count": 0,
        "determinism_violation_count": 0,
        "support_violation_count": 0,
        "certified_independent_case_count": 0,
        "independence_acceptance_violation_count": 0,
        "independence_terminal_violation_count": 0,
        "independent_canonical_hash_violation_count": 0,
    }
    for left in library:
        for right in library:
            for state in states:
                counts["generated_case_count"] += 1
                if counts["generated_case_count"] > maximum_cases:
                    raise RuntimeError("generated-case cap exceeded")
                case: dict[str, object] = {
                    "state": state,
                    "instruction_ids": [left.instruction_id, right.instruction_id],
                }
                if left.instruction_id == right.instruction_id:
                    counts["duplicate_id_schema_rejection_count"] += 1
                    case["status"] = "duplicate_id_schema_rejected"
                    ledger_hash.update(_canonical_bytes(case) + b"\n")
                    continue
                program = (left, right)
                forward_status, forward = _execution_status(state, program)
                repeated_status, repeated = _execution_status(state, program)
                case["forward_status"] = forward_status
                if forward_status != repeated_status or forward != repeated:
                    counts["determinism_violation_count"] += 1
                if forward_status == "success":
                    counts["successful_forward_case_count"] += 1
                    assert forward is not None
                    support = set(cast(Mapping[str, object], forward["terminal_delta"]))
                    if not support <= (left.writes | right.writes):
                        counts["support_violation_count"] += 1
                    case["forward_terminal_state"] = forward["terminal_state"]
                    case["forward_trace_sha256"] = forward["trace_sha256"]
                else:
                    counts["guard_rejected_forward_case_count"] += 1
                independent = instructions_independent(left, right)
                case["certified_independent"] = independent
                if independent:
                    counts["certified_independent_case_count"] += 1
                    reverse_status, reverse = _execution_status(state, (right, left))
                    case["reverse_status"] = reverse_status
                    if forward_status != reverse_status:
                        counts["independence_acceptance_violation_count"] += 1
                    elif forward_status == "success":
                        assert forward is not None and reverse is not None
                        if forward["terminal_state"] != reverse["terminal_state"]:
                            counts["independence_terminal_violation_count"] += 1
                        case["reverse_terminal_state"] = reverse["terminal_state"]
                    if canonical_program_hash(program) != canonical_program_hash((right, left)):
                        counts["independent_canonical_hash_violation_count"] += 1
                ledger_hash.update(_canonical_bytes(case) + b"\n")
    return {"instruction_count": len(library), "state_count": len(states), **counts}, ledger_hash.hexdigest()


def _witness_result(value: object, *, path: str) -> tuple[dict[str, int], tuple[Instruction, ...]]:
    witness = _mapping(value)
    if witness is None:
        raise ValueError(f"{path} must be a mapping")
    state_value = _mapping(witness.get("initial_state"))
    instructions_value = _sequence(witness.get("instructions"))
    if state_value is None or instructions_value is None:
        raise ValueError(f"{path} lacks state or instructions")
    return _validate_state(state_value), parse_program(instructions_value, path=f"{path}.instructions")


def _run_witnesses(manifest: Mapping[str, object]) -> dict[str, object]:
    values = cast(Mapping[str, object], manifest["frozen_witnesses"])
    independent_value = cast(Mapping[str, object], values["independent_swap"])
    independent_state, independent_program = _witness_result(
        independent_value, path="frozen_witnesses.independent_swap"
    )
    independent_forward = execute_program(independent_state, independent_program)
    independent_reverse = execute_program(independent_state, tuple(reversed(independent_program)))
    independent_result = {
        "certified_independent": instructions_independent(*independent_program),
        "terminal_states_equal": (
            independent_forward["terminal_state"] == independent_reverse["terminal_state"]
        ),
        "canonical_hashes_equal": (
            canonical_program_hash(independent_program)
            == canonical_program_hash(tuple(reversed(independent_program)))
        ),
        "canonical_instruction_ids": [
            item.instruction_id for item in canonicalize_program(independent_program)
        ],
    }

    dependent_value = cast(Mapping[str, object], values["dependent_noncommuting"])
    dependent_state, dependent_program = _witness_result(
        dependent_value, path="frozen_witnesses.dependent_noncommuting"
    )
    dependent_forward = execute_program(dependent_state, dependent_program)
    dependent_reverse = execute_program(dependent_state, tuple(reversed(dependent_program)))
    dependent_forward_a = cast(Mapping[str, object], dependent_forward["terminal_state"])["a"]
    dependent_reverse_a = cast(Mapping[str, object], dependent_reverse["terminal_state"])["a"]
    dependent_result = {
        "certified_independent": instructions_independent(*dependent_program),
        "forward_a": dependent_forward_a,
        "reverse_a": dependent_reverse_a,
        "matches_expected": (
            dependent_forward_a == dependent_value["expected_forward_a"]
            and dependent_reverse_a == dependent_value["expected_reverse_a"]
        ),
        "canonical_forward_ids": [item.instruction_id for item in canonicalize_program(dependent_program)],
        "canonical_reverse_ids": [
            item.instruction_id for item in canonicalize_program(tuple(reversed(dependent_program)))
        ],
    }

    collision_value = cast(Mapping[str, object], values["aave_like_terminal_collision"])
    collision_state = _validate_state(cast(Mapping[str, object], collision_value["initial_state"]))
    round_trip = parse_program(
        cast(Sequence[object], collision_value["round_trip_program"]),
        path="frozen_witnesses.aave_like_terminal_collision.round_trip_program",
    )
    no_op = parse_program(
        cast(Sequence[object], collision_value["no_op_program"]),
        path="frozen_witnesses.aave_like_terminal_collision.no_op_program",
    )
    round_trip_result = execute_program(collision_state, round_trip)
    no_op_result = execute_program(collision_state, no_op)
    trace = cast(Sequence[Mapping[str, object]], round_trip_result["trace"])
    transient_values = [cast(Mapping[str, object], item["state_after"])["asset.lt"] for item in trace]
    collision_result = {
        "terminal_deltas_equal": (
            round_trip_result["terminal_delta"]
            == no_op_result["terminal_delta"]
            == collision_value["expected_terminal_delta"]
        ),
        "trace_signatures_differ": (round_trip_result["trace_sha256"] != no_op_result["trace_sha256"]),
        "transient_value_observed": collision_value["expected_transient_value"] in transient_values,
        "round_trip_trace_sha256": round_trip_result["trace_sha256"],
        "no_op_trace_sha256": no_op_result["trace_sha256"],
    }

    inventory_value = cast(Mapping[str, object], values["generic_inventory_order"])
    inventory_state, inventory_program = _witness_result(
        inventory_value, path="frozen_witnesses.generic_inventory_order"
    )
    inventory_forward = execute_program(inventory_state, inventory_program)
    inventory_reverse = execute_program(inventory_state, tuple(reversed(inventory_program)))
    forward_inventory = cast(Mapping[str, object], inventory_forward["terminal_state"])["inventory"]
    reverse_inventory = cast(Mapping[str, object], inventory_reverse["terminal_state"])["inventory"]
    inventory_result = {
        "certified_independent": instructions_independent(*inventory_program),
        "forward_inventory": forward_inventory,
        "reverse_inventory": reverse_inventory,
        "matches_expected": (
            forward_inventory == inventory_value["expected_forward_inventory"]
            and reverse_inventory == inventory_value["expected_reverse_inventory"]
        ),
    }
    return {
        "independent_swap": independent_result,
        "dependent_noncommuting": dependent_result,
        "aave_like_terminal_collision": collision_result,
        "generic_inventory_order": inventory_result,
    }


def run_feasibility(
    manifest: Mapping[str, object],
    *,
    root: str | Path,
    protocol_commit: str,
    manifest_sha256: str,
    source_sha256: str,
) -> dict[str, object]:
    """Run the complete deterministic generated ESTIR feasibility audit."""

    manifest_errors = validate_manifest(manifest)
    parent_errors = validate_parent_files(manifest, root)
    if manifest_errors or parent_errors:
        raise ValueError("invalid ESTIR contract: " + "; ".join(manifest_errors + parent_errors))
    if COMMIT_PATTERN.fullmatch(protocol_commit) is None:
        raise ValueError("protocol commit must be a lowercase 40-hex Git SHA")
    if HEX_SHA_PATTERN.fullmatch(manifest_sha256) is None or HEX_SHA_PATTERN.fullmatch(source_sha256) is None:
        raise ValueError("manifest and source hashes must be lowercase SHA-256 values")
    started = time.perf_counter()
    schema_checks = _schema_rejection_checks()
    evaluation, case_ledger_sha256 = _run_exhaustive_grid(manifest)
    witnesses = _run_witnesses(manifest)
    elapsed = time.perf_counter() - started
    resources = cast(Mapping[str, object], manifest["resources"])
    if elapsed > cast(int, resources["maximum_runtime_seconds"]):
        raise RuntimeError("ESTIR execution exceeded the frozen runtime cap")
    claims = manifest["claim_boundary"]
    independent = cast(Mapping[str, object], witnesses["independent_swap"])
    dependent = cast(Mapping[str, object], witnesses["dependent_noncommuting"])
    collision = cast(Mapping[str, object], witnesses["aave_like_terminal_collision"])
    inventory = cast(Mapping[str, object], witnesses["generic_inventory_order"])
    gates = {
        "manifest_and_parent_integrity": not manifest_errors and not parent_errors,
        "instruction_schema_fail_closed": bool(schema_checks) and all(schema_checks.values()),
        "interpreter_determinism": evaluation["determinism_violation_count"] == 0,
        "certified_independence_commutation": (
            cast(int, evaluation["certified_independent_case_count"]) > 0
            and evaluation["independence_acceptance_violation_count"] == 0
            and evaluation["independence_terminal_violation_count"] == 0
        ),
        "dependency_witness_nonzero_commutator": (
            dependent["certified_independent"] is False
            and dependent["matches_expected"] is True
            and dependent["forward_a"] != dependent["reverse_a"]
            and dependent["canonical_forward_ids"] != dependent["canonical_reverse_ids"]
        ),
        "canonical_hash_independent_swap_invariance": (
            independent["certified_independent"] is True
            and independent["terminal_states_equal"] is True
            and independent["canonical_hashes_equal"] is True
            and evaluation["independent_canonical_hash_violation_count"] == 0
        ),
        "terminal_collision_trace_separation": (
            collision["terminal_deltas_equal"] is True
            and collision["trace_signatures_differ"] is True
            and collision["transient_value_observed"] is True
        ),
        "sparse_support_containment": evaluation["support_violation_count"] == 0,
        "two_fixture_families": (
            dependent["matches_expected"] is True
            and collision["terminal_deltas_equal"] is True
            and inventory["matches_expected"] is True
            and inventory["certified_independent"] is False
        ),
        "access_and_claim_boundary": (
            claims
            == {
                "development_only": True,
                "new_theorem_claim_authorized": False,
                "full_evm_semantics_claim_authorized": False,
                "empirical_aave_compiler_claim_authorized": False,
                "b0_v2_authorized": False,
                "b1_empirical_compiler_authorized": False,
                "account_or_outcome_access_authorized": False,
                "g1_or_gpu_authorized": False,
            }
            and cast(int, evaluation["generated_case_count"])
            <= cast(
                int,
                cast(Mapping[str, object], manifest["evaluation"])["maximum_generated_cases"],
            )
        ),
    }
    if tuple(gates) != REQUIRED_GATES:
        raise AssertionError("runtime gate ordering differs from the frozen manifest")
    passed = all(gates.values())
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "protocol_commit": protocol_commit,
        "manifest_sha256": manifest_sha256,
        "source_sha256": source_sha256,
        "parent_validation_errors": parent_errors,
        "schema_rejection_checks": schema_checks,
        "evaluation": evaluation,
        "case_ledger_sha256": case_ledger_sha256,
        "witnesses": witnesses,
        "gates": gates,
        "gate_counts": {
            "pass": sum(gates.values()),
            "fail": len(gates) - sum(gates.values()),
        },
        "resource_use": {
            "generated_case_count": evaluation["generated_case_count"],
            "generated_case_cap": cast(Mapping[str, object], manifest["evaluation"])[
                "maximum_generated_cases"
            ],
            "runtime_cap_seconds": resources["maximum_runtime_seconds"],
            "network_calls": 0,
            "market_or_chain_rows_read": 0,
            "cpu_workers": 1,
            "gpu_hours": 0,
            "paid_data": False,
            "h20_used": False,
            "case_rows_retained": 0,
        },
        "claim_boundary": claims,
        "decision": PASS_DECISION if passed else FAIL_DECISION,
        "authorized_next_stage": ("compiler_fixture_and_specification_extension_only" if passed else None),
    }


def verify_summary(
    manifest: Mapping[str, object], summary: Mapping[str, object], *, root: str | Path
) -> list[str]:
    """Recompute the deterministic audit and compare the complete normalized artifact."""

    root_path = Path(root)
    protocol_commit = summary.get("protocol_commit")
    manifest_hash = summary.get("manifest_sha256")
    source_hash = summary.get("source_sha256")
    if (
        not isinstance(protocol_commit, str)
        or not isinstance(manifest_hash, str)
        or not isinstance(source_hash, str)
    ):
        return ["summary lacks protocol/source/manifest identities"]
    actual_manifest_hash = sha256_file(root_path / MANIFEST_RELATIVE_PATH)
    actual_source_hash = sha256_file(root_path / SOURCE_RELATIVE_PATH)
    identity_errors: list[str] = []
    if manifest_hash != actual_manifest_hash:
        identity_errors.append("summary manifest hash differs from the repository file")
    if source_hash != actual_source_hash:
        identity_errors.append("summary source hash differs from the repository file")
    if identity_errors:
        return identity_errors
    expected = run_feasibility(
        manifest,
        root=root_path,
        protocol_commit=protocol_commit,
        manifest_sha256=actual_manifest_hash,
        source_sha256=actual_source_hash,
    )
    return [] if expected == summary else ["summary differs from deterministic ESTIR reconstruction"]


def _write_json(path: Path, value: object, *, maximum_bytes: int) -> int:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    encoded = json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    if len(encoded) > maximum_bytes:
        raise RuntimeError("serialized ESTIR artifact exceeds the frozen output cap")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    return len(encoded)


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run")
    run.add_argument("manifest", type=Path)
    run.add_argument("--root", type=Path, default=Path.cwd())
    run.add_argument("--protocol-commit", required=True)
    run.add_argument("--output", type=Path, required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("manifest", type=Path)
    verify.add_argument("summary", type=Path)
    verify.add_argument("--root", type=Path, default=Path.cwd())
    return parser


def main() -> None:
    """Run or independently reconstruct the generated ESTIR audit."""

    args = _build_parser().parse_args()
    root = cast(Path, args.root).resolve()
    manifest_path = cast(Path, args.manifest).resolve()
    manifest = load_json(manifest_path)
    if args.command == "verify":
        summary = load_json(cast(Path, args.summary))
        errors = verify_summary(manifest, summary, root=root)
        if errors:
            raise ValueError("ESTIR verification failed: " + "; ".join(errors))
        print(json.dumps({"verified": True, "decision": summary["decision"]}))
        return
    protocol_commit = cast(str, args.protocol_commit)
    if _git(root, "rev-parse", "HEAD") != protocol_commit:
        raise RuntimeError("worktree HEAD differs from the sealed protocol commit")
    if _git(root, "status", "--porcelain"):
        raise RuntimeError("ESTIR worktree must be clean before execution")
    source_hash = sha256_file(Path(__file__))
    result = run_feasibility(
        manifest,
        root=root,
        protocol_commit=protocol_commit,
        manifest_sha256=sha256_file(manifest_path),
        source_sha256=source_hash,
    )
    resources = cast(Mapping[str, object], manifest["resources"])
    byte_count = _write_json(
        cast(Path, args.output), result, maximum_bytes=cast(int, resources["maximum_output_bytes"])
    )
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "generated_cases": cast(Mapping[str, object], result["evaluation"])["generated_case_count"],
                "output_bytes": byte_count,
            }
        )
    )


if __name__ == "__main__":
    main()
