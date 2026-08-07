from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest


def _load_module() -> ModuleType:
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts/exp127_v100_orchestrator.py"
    spec = importlib.util.spec_from_file_location("exp127_v100_orchestrator", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_machine_inventory_requires_two_distinct_nodes(tmp_path: Path) -> None:
    module = _load_module()
    inventory = tmp_path / "machines.json"
    inventory.write_text(
        json.dumps(
            {
                "v100_a": {"host": "node-a", "user": "root"},
                "v100_b": {"host": "node-b", "user": "root"},
            }
        )
    )
    nodes = module.load_nodes(inventory)
    assert nodes["v100_a"].target == "root@node-a"

    inventory.write_text(
        json.dumps(
            {
                "v100_a": {"host": "same", "user": "root"},
                "v100_b": {"host": "same", "user": "root"},
            }
        )
    )
    with pytest.raises(ValueError, match="duplicate"):
        module.load_nodes(inventory)


def test_rollout_service_names_are_stable() -> None:
    module = _load_module()
    assert module.rollout_service_name("calibration", "v100_a") == (
        "ecophys-exp127-calibration-a.service"
    )
    assert module.rollout_service_name("heldout", "v100_b") == "ecophys-exp127-heldout-b.service"


def test_write_json_is_atomic_and_hashable(tmp_path: Path) -> None:
    module = _load_module()
    path = tmp_path / "status.json"
    module.write_json(path, {"complete": True})
    assert json.loads(path.read_text()) == {"complete": True}
    assert len(module.sha256_file(path)) == 64


def test_wait_tolerates_collected_service_before_final_status_visibility(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    node = module.Node(name="v100_a", host="node-a", user="root")
    observations = iter([None, {"complete": True, "jobs": []}])
    monkeypatch.setattr(module, "remote_json", lambda _node, _path: next(observations))
    monkeypatch.setattr(module, "service_state", lambda _node, _service: "unknown")
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)

    result = module.wait_for_stage(
        {"v100_a": node},
        {"v100_a": Path("/tmp/status.json")},
        {"v100_a": "collected.service"},
        poll_seconds=60,
    )

    assert result["v100_a"]["complete"] is True
