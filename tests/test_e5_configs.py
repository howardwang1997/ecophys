"""Tests for E-5: frozen Hydra configs + seed/stream manifest.

CPU spot-checks only (PI rule 2026-09-06): composing the 100 campaign
configs takes ~3 s and the manifest rebuild is instant. No GPU, no training,
no outcome access.
"""

from __future__ import annotations

import hashlib
import sys
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
for _entry in (str(REPO_ROOT / "scripts"), str(REPO_ROOT)):
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from ecomd.models.fact_surrogate import FactSurrogateConfig  # noqa: E402
from ecomd.models.l1_coordinate_heads import L1CoordinateHeadsConfig  # noqa: E402
from ecomd.reexploration import campaign as c  # noqa: E402
from ecomd.training.l1_supervised import L1SupervisedTrainConfig  # noqa: E402
from ecomd.training.train_fact_surrogate import (  # noqa: E402
    SUBSTREAM_NAMES,
    FactSurrogateTrainConfig,
    derive_substream_seeds,
)

gen = c._e2_module()  # the validated E-2 surface itself

TrainingRow = tuple[str, str, dict[str, Any]]
DeploymentRow = tuple[str, str, str, dict[str, Any]]


@pytest.fixture(scope="module")
def training() -> tuple[TrainingRow, ...]:
    return c.training_compositions()


@pytest.fixture(scope="module")
def deployment() -> tuple[DeploymentRow, ...]:
    return c.deployment_compositions()


@pytest.fixture(scope="module")
def manifest() -> dict[str, Any]:
    return c.build_seed_manifest()


# ── config tree ──────────────────────────────────────────────────────────────


def test_config_tree_validates() -> None:
    assert c.validate_config_tree() == ()


def test_composition_counts(
    training: tuple[TrainingRow, ...], deployment: tuple[DeploymentRow, ...]
) -> None:
    assert len(training) == 20  # 5 blocks x 4 arms
    assert len(deployment) == 80  # 5 blocks x 4 arms x 4 axes
    for payload in [p for _, _, p in training] + [p for _, _, _, p in deployment]:
        assert payload["schema_version"] == c.SCHEMA_VERSION


def test_hyperparameters_bind_frozen_module_defaults() -> None:
    l1 = c.load_composed_config("B1", "increment_raw", "id")["block"]["lineage"]
    assert l1["model"] == asdict(L1CoordinateHeadsConfig())
    l1_train_defaults = asdict(L1SupervisedTrainConfig())
    for key, value in l1["train"].items():
        assert l1_train_defaults[key] == value
    assert "coordinate" not in l1["train"] and "channel_scales" not in l1["train"]

    l2 = c.load_composed_config("B3", "absolute_through_m", "id")["block"]["lineage"]
    assert l2["model"] == asdict(FactSurrogateConfig())
    l2_train_defaults = asdict(FactSurrogateTrainConfig())
    for key, value in l2["train"].items():
        assert l2_train_defaults[key] == value
    for arm_level in ("coordinate", "enforcement", "estimator", "kernel", "mechanism_backend"):
        assert arm_level not in l2["train"]


def test_dgp_yaml_constructs_via_e2_axis_agreement() -> None:
    expected = replace(gen.DGPConfig(), dgp_family=gen.DgpFamily("multiscale_logvol"))
    for axis in ("id", "pop_2x", "tick_2x", "kswap"):
        payload = c.load_composed_config("B4-variantB", "increment_through_m", axis)
        parsed = gen.config_from_mapping(payload["block"]["dgp"]["config"])
        assert parsed == expected
        gen.config_for_axis(parsed, payload["axis"]["dgp_axis"])


def test_kswap_preserves_dgp_truth(deployment: tuple[DeploymentRow, ...]) -> None:
    by_key: dict[tuple[str, str], str] = {}
    for block_id, arm_id, axis_id, payload in deployment:
        fingerprint = gen.config_fingerprint(
            gen.config_from_mapping(payload["block"]["dgp"]["config"])
        )
        if axis_id == "id":
            by_key[(block_id, arm_id)] = fingerprint
    for block_id, arm_id, axis_id, payload in deployment:
        if axis_id == "kswap":
            fingerprint = gen.config_fingerprint(
                gen.config_from_mapping(payload["block"]["dgp"]["config"])
            )
            assert fingerprint == by_key[(block_id, arm_id)]
            assert payload["axis"]["raw_infer_duplicate_of"] == "id"


def test_negative_jump_iid_excluded() -> None:
    options = sorted(p.stem for p in (c.CONFIG_DIR / "dgp").glob("*.yaml"))
    assert "negative_jump_iid" not in options
    assert tuple(gen.D2_NAMED_NOT_RUN) == ("negative_jump_iid",)
    with pytest.raises(ValueError):
        gen.d2_series(gen.DgpFamily("negative_jump_iid"), n_rounds=8, seed=1, burn_in=0)


def test_composed_fingerprint_deterministic() -> None:
    first = c.load_composed_config("B2", "absolute_through_m", "pop_2x")
    second = c.load_composed_config("B2", "absolute_through_m", "pop_2x")
    assert c.composed_fingerprint(first) == c.composed_fingerprint(second)
    other = c.load_composed_config("B2", "absolute_through_m", "tick_2x")
    assert c.composed_fingerprint(other) != c.composed_fingerprint(first)


# ── C14 enumeration ──────────────────────────────────────────────────────────


def test_enumeration_matches_c14_restated() -> None:
    counts = c.validate_counts()
    assert counts.trainings_stage1 == 240
    assert counts.trainings_stage2 == 180
    assert counts.trainings_audit == 30
    assert counts.trainings_total == 450
    assert counts.per_seed_mandatory == 2048
    assert counts.mandatory_stage1 == 122880
    assert counts.mandatory_stage2 == 92160
    assert counts.mandatory_total == 215040
    assert counts.truncation_total == 76800
    assert counts.audit_records == 7680
    assert counts.confirmatory_total == 299520
    assert counts.horizon_one_probes == 420
    assert counts.per_block_mandatory == {
        "B1": 61440,
        "B3": 61440,
        "B2": 30720,
        "B4-variantA": 30720,
        "B4-variantB": 30720,
    }
    assert counts.per_block_truncation == {
        "B1": 30720,
        "B3": 15360,
        "B2": 15360,
        "B4-variantA": 7680,
        "B4-variantB": 7680,
    }
    assert counts.per_block_probes == {
        "B1": 120,
        "B3": 120,
        "B2": 60,
        "B4-variantA": 60,
        "B4-variantB": 60,
    }


def test_trainings_breakdown() -> None:
    runs = c.enumerate_trainings()
    assert len(runs) == len(set(runs))
    per_arm = {(r.block_id, r.arm_id): 0 for r in runs}
    for run in runs:
        per_arm[(run.block_id, run.arm_id)] += 1
    assert set(per_arm.values()) == {15, 30, 60}
    audit = [r for r in runs if r.audit_id == "A10"]
    assert len(audit) == 30
    assert {r.seed for r in audit} == set(range(11000, 11030))
    assert all(r.estimator_override == "perturb_and_map" for r in audit)
    assert all(r.arm_id == "increment_through_m" for r in audit)


def test_enumeration_flags_discrepancy(monkeypatch: pytest.MonkeyPatch) -> None:
    mutated = tuple(
        replace(block, seed_stop_inclusive=block.seed_stop_inclusive + 1)
        if block.block_id == "B1"
        else block
        for block in c.BLOCKS
    )
    monkeypatch.setattr(c, "BLOCKS", mutated)
    with pytest.raises(c.CampaignArithmeticError):
        c.validate_counts()


# ── seeds / manifest ─────────────────────────────────────────────────────────


def test_seed_disjointness(manifest: dict[str, Any]) -> None:
    checks = c.disjointness_checks()
    assert all(check.ok for check in checks)
    c.assert_disjointness()
    assert not (set(c.L1_TRAINING.seeds) & set(c.L2_TRAINING.seeds))
    assert manifest["disjointness"]["all_ok"] is True


def test_manifest_on_disk_is_byte_identical_to_rebuild() -> None:
    assert c.MANIFEST_PATH.exists()
    assert c.MANIFEST_PATH.read_bytes() == c.canonical_json_bytes(c.build_seed_manifest())


def test_manifest_determinism() -> None:
    assert c.canonical_json_bytes(c.build_seed_manifest()) == c.canonical_json_bytes(
        c.build_seed_manifest()
    )


def test_manifest_substreams_match_trainer_and_e2(manifest: dict[str, Any]) -> None:
    entries = {entry["seed"]: entry for entry in manifest["seed_roots"]}
    assert set(entries) == set(c.L1_TRAINING.seeds) | set(c.L2_TRAINING.seeds)
    for root in (11000, 11014, 11029, 12000, 12029):
        expected = derive_substream_seeds(root)
        assert entries[root]["substreams"] == expected
        for name in ("data", "init", "minibatch", "train_kernel"):
            assert expected[name] == gen.named_substream_seed(root, name)
        children = np.random.SeedSequence(root).spawn(len(SUBSTREAM_NAMES))
        spawned = {
            name: int(child.generate_state(1, dtype=np.uint32)[0])
            for name, child in zip(SUBSTREAM_NAMES, children, strict=True)
        }
        assert spawned == expected


def test_bootstrap_derivation(manifest: dict[str, Any]) -> None:
    expected = int(
        hashlib.sha256(
            b"ecomd_reexploration_v2_bootstrap" + b"B1" + b"signflip_mandatory"
        ).hexdigest(),
        16,
    )
    expected %= 2**63
    assert c.bootstrap_seed("B1", "signflip_mandatory") == expected
    bootstrap = manifest["derivation"]["bootstrap_seeds"]
    assert len(bootstrap) == 15
    assert len(set(bootstrap.values())) == 15
    reserved = (
        set(c.L1_TRAINING.seeds)
        | set(c.L2_TRAINING.seeds)
        | set(c.INSTRUMENT_NAMESPACE_SEEDS)
        | set(range(31000, 31100))
    )
    assert not (set(bootstrap.values()) & reserved)


def test_manifest_pins_subsets_and_posture(manifest: dict[str, Any]) -> None:
    namespaces = {ns["namespace_id"]: ns for ns in manifest["namespaces"]}
    assert namespaces["l1_training"]["stage2_subset"]["seed_stop_inclusive"] == 11014
    assert namespaces["l2_training"]["stage2_subset"]["seed_stop_inclusive"] == 12014
    assert namespaces["l1_training"]["reflexive_subset"]["seed_stop_inclusive"] == 11009
    assert namespaces["l2_training"]["reflexive_subset"]["seed_stop_inclusive"] == 12009
    posture = manifest["rank_seed_posture"]
    assert posture["world_size"] == 1
    assert 11000 + 2 * 10000 == 31000  # the latent rank-2 overlap, stated numerically
    stage2 = {e["seed"] for e in manifest["seed_roots"] if e["stage2_included"]}
    assert stage2 == set(range(11000, 11015)) | set(range(12000, 12015))
