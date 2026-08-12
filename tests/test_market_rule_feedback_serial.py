from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
from typing import cast

import yaml

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "experiments/148_generated_market_rule_feedback_rd_serial/run_preflight.py"
EXECUTION_PATH = ROOT / "experiments/148_generated_market_rule_feedback_rd_serial/execution_config.yaml"
PARENT_CONFIG_PATH = ROOT / "experiments/147_generated_market_rule_feedback_rd/config.yaml"


def _load_runner() -> object:
    spec = importlib.util.spec_from_file_location("exp148_run_preflight", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _mapping(path: Path) -> dict[str, object]:
    raw: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    return cast(dict[str, object], raw)


def test_execution_contract_locks_all_parent_files() -> None:
    execution = _mapping(EXECUTION_PATH)
    parent_entries = [
        entry
        for key, entry in execution.items()
        if key.startswith("parent_") and isinstance(entry, dict)
    ]

    assert execution["backend"] == "serial_in_process"
    assert execution["controller_processes"] == 1
    assert execution["worker_processes"] == 0
    assert len(parent_entries) == 5
    for entry in parent_entries:
        path = ROOT / entry["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]


def test_frozen_task_counts_are_exactly_inherited() -> None:
    runner = _load_runner()
    execution = _mapping(EXECUTION_PATH)
    parent_config = _mapping(PARENT_CONFIG_PATH)

    fit_tasks, oracle_tasks = runner.count_frozen_tasks(parent_config)

    assert fit_tasks == execution["expected_fit_tasks"] == 6600
    assert oracle_tasks == execution["expected_oracle_tasks"] == 1800


def test_serial_executor_preserves_order_and_controller_pid() -> None:
    runner = _load_runner()
    controller_pid = os.getpid()
    seen: list[tuple[int, int]] = []
    tasks = [({}, {}, 10.0, 0.1, replicate) for replicate in range(4)]

    def fixture(task: tuple[dict[str, object], dict[str, object], float, float, int]) -> dict[str, object]:
        seen.append((task[-1], os.getpid()))
        return {"replicate": task[-1]}

    results = runner.execute_serial_tasks(tasks, fixture)

    assert [result["replicate"] for result in results] == [0, 1, 2, 3]
    assert seen == [(0, controller_pid), (1, controller_pid), (2, controller_pid), (3, controller_pid)]


def test_runner_source_contains_no_parallel_or_child_process_backend() -> None:
    source = RUNNER_PATH.read_text(encoding="utf-8")
    forbidden = (
        "ProcessPoolExecutor",
        "ThreadPoolExecutor",
        "multiprocessing",
        "concurrent.futures",
        "Semaphore",
        "subprocess.Popen",
    )

    assert all(symbol not in source for symbol in forbidden)
    assert "execute_serial_tasks(tasks, parent._fit_task)" in source


def test_runner_guards_network_accelerators_and_threads() -> None:
    runner = _load_runner()

    assert runner.os.environ["CUDA_VISIBLE_DEVICES"] == "-1"
    assert runner.os.environ["ROCR_VISIBLE_DEVICES"] == "-1"
    assert all(
        runner.os.environ[variable] == "1"
        for variable in (
            "OMP_NUM_THREADS",
            "OPENBLAS_NUM_THREADS",
            "MKL_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS",
            "NUMEXPR_NUM_THREADS",
        )
    )
    try:
        runner._network_audit_hook("socket.connect", ())
    except PermissionError as error:
        assert "network disabled" in str(error)
    else:
        raise AssertionError("network audit hook did not fail closed")
