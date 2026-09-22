"""Production record identity and decision checks; run on a remote worker."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "reexploration"))
import eval_draws_d0s4 as driver


def test_full_b1_record_ids_and_resume(tmp_path: Path) -> None:
    records = []
    for seed in range(11000, 11030):
        for arm_id in driver.ARM_IDS:
            coordinate, training = arm_id.split("_", 1)
            for inference in driver.INFERENCE_ENFORCEMENTS:
                cell = f"{coordinate}-{training}-{inference}"
                for record_class, condition, axis in (
                    *(("RC1", "id", axis) for axis in driver.AXES_BY_ID),
                    *(("RC2", condition, "id") for condition in driver.RC2_W),
                ):
                    duplicate = record_class == "RC1" and axis == "kswap" and inference == "raw"
                    scope = ("id" if duplicate else axis) if record_class == "RC1" else condition
                    for horizon in driver.HORIZONS:
                        for draw in range(1, 17):
                            record = driver.make_record(
                                record_key=driver.record_key("B1", record_class, condition, axis, horizon, cell, seed, draw),
                                record_class=record_class, block_id="B1", condition=condition,
                                axis=axis, horizon=horizon, cell_id=cell, seed=seed, draw_index=draw,
                                run_id=f"B1.eval.{arm_id}.{scope}.{cell}.{seed:05d}.{draw:02d}",
                            )
                            if duplicate:
                                record["run_id"] += ".kswap"
                            records.append(record)
        for axis in driver.AXES_BY_ID:
            records.append(driver.make_record(
                record_key=driver.record_key("B1", "RC4", "id", axis, 1, "engine-replay-probe", seed, 0),
                record_class="RC4", block_id="B1", condition="id", axis=axis, horizon=1,
                cell_id="engine-replay-probe", seed=seed, draw_index=0, run_id=f"B1.probe.{axis}.{seed}",
            ))
    assert len(records) == len({r["record_key"] for r in records}) == len({r["run_id"] for r in records}) == 92280
    representatives = [next(r for r in records if r["record_class"] == kind) for kind in ("RC1", "RC2", "RC4")]
    representatives.append(next(r for r in records if r["axis"] == "kswap" and r["cell_id"].endswith("-raw")))
    for record in representatives:
        driver.write_record(tmp_path, record)
    driver.validate_existing_record_ids(tmp_path)
    legacy = dict(representatives[0])
    legacy["run_id"] = legacy["run_id"].removesuffix(".h01")
    driver.write_record(tmp_path, legacy)
    with pytest.raises(RuntimeError, match="horizon binding"):
        driver.validate_existing_record_ids(tmp_path)


def test_production_requires_ratified_decision(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="production requires"):
        driver.require_run_id_decision(tmp_path, "pi_d0s4_eval_constants_20260922")
    decision = tmp_path / "research" / "discovery" / "decisions" / f"{driver.RUN_ID_DECISION}.yaml"
    decision.parent.mkdir(parents=True)
    payload = {"decision_id": driver.RUN_ID_DECISION, "authorized_by": "PI", "status": "proposed"}
    decision.write_text(json.dumps(payload))
    with pytest.raises(RuntimeError, match="not PI-ratified"):
        driver.require_run_id_decision(tmp_path, driver.RUN_ID_DECISION)
    payload["status"] = "ratified"
    decision.write_text(json.dumps(payload))
    assert driver.require_run_id_decision(tmp_path, driver.RUN_ID_DECISION) == driver.sha256_file(decision)
