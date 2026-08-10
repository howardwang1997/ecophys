"""Run the preregistered EcoMD observation-semantic contract firewall."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import subprocess
import sys
import time
from collections.abc import Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

for thread_variable in (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[thread_variable] = "1"

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from ecomd.observation.ecomd_l2_adapter import (  # noqa: E402
    EcoMDL2Adapter,
    EcoMDL2AdapterConfig,
)
from ecomd.observation.semantic_contract import (  # noqa: E402
    ClockKind,
    ClockSpec,
    ContractValidationError,
    CountLaw,
    DataScope,
    LatentAccess,
    ModelInputs,
    NegativeControl,
    ObservableLabel,
    ObservationContract,
    PriceProcess,
    SignAnchor,
    SupportLevel,
    aggregate_bin_p3_contract,
    aggregate_event_p2_contract,
    contract_from_json,
    contract_to_dict,
    contract_to_json,
    current_adapter_synthetic_contract,
    run_validated,
    validate_contract,
)

PREREG = Path(__file__).with_name("PREREG.md")
RESULT_PATH = Path(__file__).with_name("SEMANTIC_CONTRACT_RESULTS.json")
REPORT_PATH = Path(__file__).with_name("RESULTS.md")
PREREG_COMMIT = "021d0b0b"
FORMAL_ROOT_SEED = 142_202_608
SMOKE_ROOT_SEED = 142_202_609
N_PROBE_EVENTS = 256
ADAPTER_DT = 0.005

EXPECTED_MUTATION_ERRORS = {
    "N1": "EXTERNAL_EVENT_CLOCK_REQUIRES_CONDITIONAL_LAW",
    "N2": "DUAL_PRICE_PROCESS_WITHOUT_LINK",
    "N3": "AGGREGATE_BIN_REQUIRES_PHYSICAL_SECONDS",
    "N4": "EVENT_COUNTER_MUST_NOT_BE_ORDER_ID",
    "N5": "INDIVIDUAL_ORDER_CAPABILITIES_MISSING",
    "N6": "MARKET_SIZE_REQUIRES_TRAIN_ONLY_LINK",
    "N7": "LATENT_PROXY_MUST_NOT_BE_LABELED_OFI",
    "N8": "DIRECTIONAL_SIGN_CONTRADICTS_ANCHOR",
    "N9": "TEST_CONDITIONED_LATENT_FORBIDDEN",
    "N10": "LATENT_CLAIM_REQUIRES_LATENT_INPUT",
    "N11": "SIGN_FLIP_CONTROL_REQUIRED",
    "N12": "OBSERVATION_ONLY_CONTROL_REQUIRED",
}


def _git_value(*args: str) -> str:
    return subprocess.check_output(
        ("git", *args), cwd=ROOT, text=True, stderr=subprocess.DEVNULL
    ).strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _positive_contracts() -> dict[str, ObservationContract]:
    return {
        "current_adapter_synthetic": current_adapter_synthetic_contract(),
        "aggregate_bin_p3": aggregate_bin_p3_contract(),
        "aggregate_event_p2_schema": aggregate_event_p2_contract(),
    }


def _mutation_contracts() -> dict[str, ObservationContract]:
    bin_contract = aggregate_bin_p3_contract()
    event_contract = aggregate_event_p2_contract()
    return {
        "N1": replace(
            event_contract,
            clock=ClockSpec(
                kind=ClockKind.SIMULATOR_STEP,
                count_law=CountLaw.ONE_PER_TRANSITION,
                physical_seconds=ADAPTER_DT,
            ),
        ),
        "N2": replace(
            event_contract,
            price=replace(
                event_contract.price,
                scored_processes=(PriceProcess.ECOMD_INTERNAL, PriceProcess.EMITTED_BOOK),
                train_only_measurement_link=False,
            ),
        ),
        "N3": replace(
            bin_contract,
            clock=replace(bin_contract.clock, physical_seconds=None),
        ),
        "N4": replace(
            event_contract,
            identity=replace(event_contract.identity, field_name="order_id"),
        ),
        "N5": replace(event_contract, support_level=SupportLevel.INDIVIDUAL_ORDER),
        "N6": replace(
            bin_contract,
            size=replace(bin_contract.size, train_only_measurement_link=False),
        ),
        "N7": replace(
            bin_contract,
            latent=replace(bin_contract.latent, observable_label=ObservableLabel.OFI),
        ),
        "N8": replace(
            bin_contract,
            latent=replace(bin_contract.latent, sign_anchor=SignAnchor.SIGN_FLIPPED),
        ),
        "N9": replace(
            bin_contract,
            latent=replace(bin_contract.latent, access=LatentAccess.TEST_CONDITIONED),
        ),
        "N10": replace(
            bin_contract,
            latent=replace(bin_contract.latent, model_inputs=ModelInputs.OBSERVATION_ONLY),
        ),
        "N11": replace(
            bin_contract,
            latent=replace(
                bin_contract.latent,
                controls=(NegativeControl.OBSERVATION_ONLY,),
            ),
        ),
        "N12": replace(
            bin_contract,
            latent=replace(bin_contract.latent, controls=(NegativeControl.SIGN_FLIP,)),
        ),
    }


def _check_serialization(
    contracts: dict[str, ObservationContract],
) -> dict[str, Any]:
    cases: dict[str, Any] = {}
    for name, contract in contracts.items():
        encoded = contract_to_json(contract)
        decoded = contract_from_json(encoded)
        first_report = validate_contract(contract)
        second_report = validate_contract(contract)
        cases[name] = {
            "canonical_json": encoded,
            "canonical_sha256": hashlib.sha256(encoded.encode()).hexdigest(),
            "round_trip_exact": decoded == contract,
            "canonical_repeat_exact": contract_to_json(decoded) == encoded,
            "validation_repeat_exact": first_report == second_report,
        }

    unknown = contract_to_dict(aggregate_bin_p3_contract())
    unknown["unknown"] = True
    unknown_key_rejected = False
    try:
        contract_from_json(json.dumps(unknown))
    except ValueError:
        unknown_key_rejected = True

    unknown_enum = contract_to_dict(aggregate_bin_p3_contract())
    unknown_enum["support_level"] = "orderish"
    unknown_enum_rejected = False
    try:
        contract_from_json(json.dumps(unknown_enum))
    except ValueError:
        unknown_enum_rejected = True

    nonfinite = contract_to_dict(aggregate_bin_p3_contract())
    clock = nonfinite["clock"]
    if not isinstance(clock, dict):
        raise TypeError("canonical clock must be a mapping")
    clock["physical_seconds"] = float("nan")
    nonfinite_rejected = False
    try:
        contract_from_json(json.dumps(nonfinite))
    except ValueError:
        nonfinite_rejected = True

    return {
        "cases": cases,
        "unknown_key_rejected": unknown_key_rejected,
        "unknown_enum_rejected": unknown_enum_rejected,
        "nonfinite_json_rejected": nonfinite_rejected,
        "passed": bool(
            all(
                case["round_trip_exact"]
                and case["canonical_repeat_exact"]
                and case["validation_repeat_exact"]
                for case in cases.values()
            )
            and unknown_key_rejected
            and unknown_enum_rejected
            and nonfinite_rejected
        ),
    }


def _check_positive_contracts(
    positives: dict[str, ObservationContract],
) -> dict[str, Any]:
    reports = {name: validate_contract(contract) for name, contract in positives.items()}
    expected = {
        "current_adapter_synthetic": ((), ("SYNTHETIC_ORDER_ID_IS_EVENT_COUNTER",)),
        "aggregate_bin_p3": ((), ()),
        "aggregate_event_p2_schema": ((), ()),
    }
    records = {
        name: {
            "contract": contract_to_dict(positives[name]),
            "report": report.to_dict(),
            "expected_errors": list(expected[name][0]),
            "expected_warnings": list(expected[name][1]),
            "exact": report.errors == expected[name][0]
            and report.warnings == expected[name][1],
        }
        for name, report in reports.items()
    }
    return {"records": records, "passed": all(item["exact"] for item in records.values())}


def _check_mutations(mutations: dict[str, ObservationContract]) -> dict[str, Any]:
    records: dict[str, Any] = {}
    for case, contract in mutations.items():
        report = validate_contract(contract)
        expected = (EXPECTED_MUTATION_ERRORS[case],)
        records[case] = {
            "contract": contract_to_dict(contract),
            "report": report.to_dict(),
            "expected_errors": list(expected),
            "exact": report.errors == expected and not report.valid,
        }
    return {"records": records, "passed": all(item["exact"] for item in records.values())}


def _check_support_escalation() -> dict[str, Any]:
    current = current_adapter_synthetic_contract()
    records: dict[str, Any] = {}
    for support in (
        SupportLevel.AGGREGATE_BIN,
        SupportLevel.AGGREGATE_EVENT,
        SupportLevel.INDIVIDUAL_ORDER,
    ):
        contract = replace(current, support_level=support, data_scope=DataScope.EXTERNAL)
        report = validate_contract(contract)
        records[support.value] = {
            "requested_support": report.requested_support.value,
            "errors": list(report.errors),
            "preserved": report.requested_support is support,
            "rejected": not report.valid,
        }
    return {
        "records": records,
        "passed": all(item["preserved"] and item["rejected"] for item in records.values()),
    }


def _check_fit_firewall(
    positives: dict[str, ObservationContract],
    mutations: dict[str, ObservationContract],
) -> dict[str, Any]:
    invalid_records: dict[str, Any] = {}
    for case, contract in mutations.items():
        calls = 0

        def invalid_callback() -> str:
            nonlocal calls
            calls += 1
            return "invalid-sentinel"

        escaped_errors: tuple[str, ...] = ()
        callback_returned = False
        try:
            run_validated(contract, invalid_callback)
            callback_returned = True
        except ContractValidationError as error:
            escaped_errors = error.report.errors
        invalid_records[case] = {
            "callback_calls": calls,
            "returned": callback_returned,
            "escaped_errors": list(escaped_errors),
            "passed": calls == 0
            and not callback_returned
            and escaped_errors == (EXPECTED_MUTATION_ERRORS[case],),
        }

    positive_records: dict[str, Any] = {}
    for name, contract in positives.items():
        calls = 0

        def valid_callback(sentinel_name: str = name) -> str:
            nonlocal calls
            calls += 1
            return f"sentinel:{sentinel_name}"

        sentinel = run_validated(contract, valid_callback)
        positive_records[name] = {
            "callback_calls": calls,
            "returned": sentinel,
            "passed": calls == 1 and sentinel == f"sentinel:{name}",
        }

    return {
        "invalid": invalid_records,
        "positive": positive_records,
        "passed": bool(
            all(item["passed"] for item in invalid_records.values())
            and all(item["passed"] for item in positive_records.values())
        ),
    }


def _probe_adapter(root_seed: int) -> dict[str, Any]:
    latent_seed, emission_seed_sequence = np.random.SeedSequence(root_seed).spawn(2)
    latent = np.random.default_rng(latent_seed).uniform(-1.0, 1.0, N_PROBE_EVENTS)
    emission_seed = int(emission_seed_sequence.generate_state(1, dtype=np.uint64)[0])
    adapter = EcoMDL2Adapter(EcoMDL2AdapterConfig(dt=ADAPTER_DT))
    _, stream = adapter.emit(
        adapter.init_state(seed=emission_seed), latent, start_step=0
    )
    expected_time = (np.arange(N_PROBE_EVENTS, dtype=np.float64) + 1.0) * ADAPTER_DT
    expected_ids = np.arange(1, N_PROBE_EVENTS + 1, dtype=np.int64)
    lifecycle_rows = np.flatnonzero(np.isin(stream.event_type, (2, 3, 4, 5)))
    lifecycle_indices = {int(index) for index in lifecycle_rows}
    prior_ids: set[int] = set()
    prior_reference_count = 0
    for index, order_id in enumerate(stream.order_id):
        if index in lifecycle_indices and int(order_id) in prior_ids:
            prior_reference_count += 1
        prior_ids.add(int(order_id))
    increments = np.diff(stream.time)
    declaration = current_adapter_synthetic_contract()
    finite = bool(
        np.isfinite(stream.latent).all()
        and np.isfinite(stream.time).all()
        and np.isfinite(stream.size).all()
        and np.isfinite(stream.price).all()
    )
    n_emitted_rows = stream.n_events
    one_row_per_step = n_emitted_rows == latent.size
    timestamp_formula_exact = bool(np.array_equal(stream.time, expected_time))
    unique_order_id_count = int(np.unique(stream.order_id).size)
    order_ids_consecutive_exact = bool(np.array_equal(stream.order_id, expected_ids))
    removal_or_execution_rows = int(lifecycle_rows.size)
    passed = bool(
        n_emitted_rows == N_PROBE_EVENTS
        and one_row_per_step
        and timestamp_formula_exact
        and unique_order_id_count == N_PROBE_EVENTS
        and order_ids_consecutive_exact
        and removal_or_execution_rows > 0
        and prior_reference_count == 0
        and finite
    )
    facts: dict[str, Any] = {
        "root_seed": root_seed,
        "emission_seed": emission_seed,
        "n_latent_steps": int(latent.size),
        "n_emitted_rows": n_emitted_rows,
        "one_row_per_step": one_row_per_step,
        "dt": ADAPTER_DT,
        "timestamp_formula_exact": timestamp_formula_exact,
        "max_abs_increment_minus_dt": float(np.max(np.abs(increments - ADAPTER_DT))),
        "unique_order_id_count": unique_order_id_count,
        "order_ids_consecutive_exact": order_ids_consecutive_exact,
        "removal_or_execution_rows": removal_or_execution_rows,
        "removal_or_execution_rows_referencing_prior_id": prior_reference_count,
        "declared_price_processes": [item.value for item in declaration.price.scored_processes],
        "declared_observed_size_unit": declaration.size.observed_unit.value,
        "finite": finite,
        "passed": passed,
    }
    return facts


def _run_quality_checks() -> dict[str, Any]:
    commands = {
        "pytest": (
            sys.executable,
            "-m",
            "pytest",
            "tests/test_semantic_contract.py",
            "-q",
        ),
        "ruff": (
            sys.executable,
            "-m",
            "ruff",
            "check",
            "ecomd/observation/semantic_contract.py",
            "tests/test_semantic_contract.py",
            "experiments/142_observation_semantic_contract/run_contract.py",
        ),
        "mypy": (
            sys.executable,
            "-m",
            "mypy",
            "--strict",
            "ecomd/observation/semantic_contract.py",
            "experiments/142_observation_semantic_contract/run_contract.py",
        ),
    }
    records: dict[str, Any] = {}
    for name, command in commands.items():
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        records[name] = {
            "command": list(command),
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    return {"records": records, "passed": all(item["returncode"] == 0 for item in records.values())}


def _environment() -> dict[str, Any]:
    packages: dict[str, str | None] = {}
    for name in ("numpy", "pytest", "ruff", "mypy"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "executable": sys.executable,
        "conda_default_env": os.environ.get("CONDA_DEFAULT_ENV"),
        "thread_variables": {
            name: os.environ[name]
            for name in (
                "OMP_NUM_THREADS",
                "MKL_NUM_THREADS",
                "OPENBLAS_NUM_THREADS",
                "NUMEXPR_NUM_THREADS",
            )
        },
        "packages": packages,
    }


def _human_report(result: dict[str, Any]) -> str:
    gate_lines = "\n".join(
        f"- G{index}: {'PASS' if passed else 'FAIL'}"
        for index, passed in enumerate(result["gates"].values(), start=1)
    )
    probe = result["adapter_probe"]
    return f"""# Experiment 142 — results

**Decision:** **{result['decision']}**
**Implementation:** `{result['provenance']['implementation_git_sha']}`
**Protocol SHA-256:** `{result['provenance']['protocol_sha256']}`

## Gate outcomes

{gate_lines}

All three frozen positive declarations were evaluated, as were all twelve single-defect mutations. The current
adapter was accepted only as `synthetic_fixture`, with its frozen event-counter warning. The aggregate-bin P3
and structurally admissible aggregate-event P2 declarations were accepted at their declared levels.

Every invalid declaration was rejected before its callback ran. Callback counts were zero for all twelve
mutations and exactly one for each valid declaration.

## Current-adapter probe

- Rows / latent steps: {probe['n_emitted_rows']} / {probe['n_latent_steps']}
- Fixed timestamp formula exact: {probe['timestamp_formula_exact']}
- Unique consecutive IDs: {probe['unique_order_id_count']} / {probe['order_ids_consecutive_exact']}
- Removal/execution rows: {probe['removal_or_execution_rows']}
- Those rows referencing a prior ID: {probe['removal_or_execution_rows_referencing_prior_id']}
- Declared price process: {', '.join(probe['declared_price_processes'])}
- Declared size unit: {probe['declared_observed_size_unit']}

## Interpretation

This result verifies a code-enforced vocabulary and pre-fit firewall only. It does not validate real-data fit,
causal latent inference, order-level mechanics, identifiability, audit-method novelty or market physics. A
separate preregistration is required for aggregate-bin reconstruction and any later external-data experiment.
"""


def _run(root_seed: int, *, formal: bool) -> dict[str, Any]:
    started = time.perf_counter()
    dirty_before = _git_value("status", "--porcelain", "--untracked-files=all")
    implementation_sha = _git_value("rev-parse", "HEAD")
    prereg_is_ancestor = (
        subprocess.run(
            ("git", "merge-base", "--is-ancestor", PREREG_COMMIT, implementation_sha),
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )
    if formal and dirty_before:
        raise RuntimeError("formal run requires a clean implementation tree")
    if formal and (RESULT_PATH.exists() or REPORT_PATH.exists()):
        raise RuntimeError("formal result already exists; refusing a second run")

    positives = _positive_contracts()
    mutations = _mutation_contracts()
    serialization = _check_serialization({**positives, **mutations})
    positive_check = _check_positive_contracts(positives)
    mutation_check = _check_mutations(mutations)
    escalation = _check_support_escalation()
    firewall = _check_fit_firewall(positives, mutations)
    probe = _probe_adapter(root_seed)
    quality = _run_quality_checks()

    chronology_passed = bool(
        not formal
        or (
            prereg_is_ancestor
            and implementation_sha != _git_value("rev-parse", PREREG_COMMIT)
            and not dirty_before
        )
    )
    provisional_gates = {
        "chronology_provenance": chronology_passed,
        "schema_determinism": bool(serialization["passed"]),
        "positive_scope": bool(positive_check["passed"]),
        "mutation_isolation": bool(mutation_check["passed"]),
        "no_silent_support_escalation": bool(escalation["passed"]),
        "fit_firewall": bool(firewall["passed"]),
        "adapter_probe": bool(probe["passed"]),
        "code_quality": bool(quality["passed"]),
    }
    complete_reporting = bool(
        len(positive_check["records"]) == 3
        and len(mutation_check["records"]) == 12
        and len(firewall["invalid"]) == 12
        and len(firewall["positive"]) == 3
        and len(escalation["records"]) == 3
        and all(key in probe for key in ("root_seed", "emission_seed", "finite", "passed"))
    )
    gates = {**provisional_gates, "complete_reporting": complete_reporting}
    decision = "PASS" if all(gates.values()) else "FAIL"
    elapsed = time.perf_counter() - started
    result: dict[str, Any] = {
        "experiment": 142,
        "name": "observation_semantic_contract_firewall",
        "mode": "formal" if formal else "smoke",
        "decision": decision,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "provenance": {
            "preregistration_commit": PREREG_COMMIT,
            "preregistration_is_ancestor": prereg_is_ancestor,
            "protocol_path": str(PREREG.relative_to(ROOT)),
            "protocol_sha256": _sha256(PREREG),
            "implementation_git_sha": implementation_sha,
            "dirty_before_run": bool(dirty_before),
            "dirty_entries_before_run": dirty_before.splitlines(),
            "root_seed": root_seed,
        },
        "environment": _environment(),
        "serialization": serialization,
        "positive_contracts": positive_check,
        "mutations": mutation_check,
        "support_escalation": escalation,
        "fit_firewall": firewall,
        "adapter_probe": probe,
        "quality": quality,
        "gates": gates,
        "resources": {
            "wall_seconds": elapsed,
            "peak_rss_raw": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "peak_rss_unit": "bytes_on_macos_kib_on_linux",
            "gpu_used": False,
            "external_data_read": False,
        },
        "interpretation": (
            "A PASS enforces the frozen semantic vocabulary only; it does not establish external validity, "
            "identifiability, causal latent inference, novelty, order mechanics or market physics."
        ),
    }
    if formal:
        RESULT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        REPORT_PATH.write_text(_human_report(result))
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args(argv)
    result = _run(SMOKE_ROOT_SEED if args.smoke else FORMAL_ROOT_SEED, formal=not args.smoke)
    print(json.dumps({"mode": result["mode"], "decision": result["decision"], "gates": result["gates"]}, indent=2))
    return 0 if result["decision"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
