"""Outcome-free g42 engine checks: certification identities, move invariants,
MH mechanics and replay determinism. No campaign units and no confirmation
material are touched."""

from __future__ import annotations

import math
from fractions import Fraction

import pytest

from research.paper_g.g42_fixed_knot_moves import model
from research.paper_g.g42_fixed_knot_moves.model import PCG64, EngineError


def _folded_ring() -> list[model.Vertex]:
    return [
        (0, 0, 0),
        (1, 0, 0),
        (2, 0, 0),
        (2, 1, 0),
        (1, 1, 0),
        (1, 2, 0),
        (0, 2, 0),
        (0, 1, 0),
    ]


def test_pcg64_reproducible_and_bounded() -> None:
    a = PCG64(12345, 67)
    b = PCG64(12345, 67)
    c = PCG64(12346, 67)
    seq_a = [a.next_uint64() for _ in range(200)]
    seq_b = [b.next_uint64() for _ in range(200)]
    seq_c = [c.next_uint64() for _ in range(200)]
    assert seq_a == seq_b
    assert seq_a != seq_c
    assert all(0 <= value < 2**64 for value in seq_a)
    d = PCG64(999, 7)
    assert all(d.below(13) < 13 for _ in range(500))
    seen = {d.below(5) for _ in range(200)}
    assert seen == {0, 1, 2, 3, 4}
    e = PCG64(4242, 9)
    values = [e.uniform() for _ in range(500)]
    assert all(0.0 <= value < 1.0 for value in values)
    assert sum(value < 0.5 for value in values) > 200


def test_pcg64_seed_range_enforced() -> None:
    with pytest.raises(EngineError):
        PCG64(1 << 128, 1)
    with pytest.raises(EngineError):
        PCG64(1, 1 << 64)


@pytest.mark.parametrize(
    "word,strands,expected",
    [
        (((0, 1),), 2, 1),
        (((0, 1),) * 3, 2, 3),
        (((0, -1),) * 3, 2, 3),
        (((0, 1), (1, -1), (0, 1), (1, -1)), 3, 5),
        (((0, 1), (1, 1)), 3, 1),
        (((0, 1), (1, 1)) * 2, 3, 3),
        (((0, 1),) * 5, 2, 5),
    ],
)
def test_braid_closures_match_known_knot_determinants(
    word: tuple[tuple[int, int], ...], strands: int, expected: int
) -> None:
    ring = model._braid_closure(word, strands)
    model.validate_ring(ring)
    assert model.certify(ring) == expected
    assert set(model.certify_all_directions(ring).values()) == {expected}


def test_identity_braid_closure_rejected_as_multi_component() -> None:
    with pytest.raises(EngineError):
        model._braid_closure((), 2)


def test_seeds_hit_target_size_and_class() -> None:
    for knot, n in (("0_1", 64), ("0_1", 96), ("0_1", 128), ("3_1", 160), ("4_1", 256)):
        ring = model.seed_ring(knot, n)
        assert len(ring) == n
        assert model.certify(ring) == model.KNOT_DETERMINANTS[knot]


def test_corner_flips_preserve_class_over_long_run() -> None:
    ring = model.seed_ring("3_1", 160)
    rng = PCG64(20260916, 5)
    occupancy = set(ring)
    flipped = 0
    for _ in range(3000):
        candidate = model._corner_flip(rng, ring, occupancy)
        if candidate is None:
            continue
        ring = candidate
        occupancy = set(ring)
        flipped += 1
        if flipped % 128 == 0:
            model.validate_ring(ring)
            assert model.certify(ring) == 3
        if flipped >= 500:
            break
    assert flipped >= 500
    model.validate_ring(ring)
    assert model.certify(ring) == 3


def test_padding_preserves_class_and_exact_length() -> None:
    base = model._braid_closure(model._BRAID_WORDS["4_1"], 3)
    ring = model.pad_to_length(base, len(base) + 20)
    assert len(ring) == len(base) + 20
    model.validate_ring(ring)
    assert model.certify(ring) == 5
    with pytest.raises(EngineError):
        model.pad_to_length(base, len(base) + 1)
    with pytest.raises(EngineError):
        model.pad_to_length(base, len(base) - 2)


def test_contacts_hand_checks() -> None:
    assert model.contacts(model.planar_rectangle(16)) == 0
    assert model.contacts(_folded_ring()) == 2


def test_policy_ratio_is_exact_fraction() -> None:
    policy = model.Policy(
        {
            "kind": "table",
            "weights": {"corner": 3, "pivot": 2, "self_loop": 1},
            "context": {
                "observable": "rg2_bucket",
                "thresholds": [10.0, 50.0],
                "multipliers": {"corner": [1, 2, 3], "pivot": [3, 2, 1], "self_loop": [2, 2, 2]},
            },
        }
    )
    assert policy.bucket(5.0) == 0
    assert policy.bucket(10.0) == 1
    assert policy.bucket(50.0) == 2
    assert policy.total(0) == 3 * 1 + 2 * 3 + 1 * 2
    # w(corner,2)*total(0) / (w(corner,0)*total(2)) = (3*3)*(3+6+2) / ((3*1)*(9+2+2))
    assert policy.ratio("corner", 0, 2) == Fraction(9 * 11, 3 * 13)
    rng = PCG64(7, 11)
    counts = {family: 0 for family in model.FAMILIES}
    for _ in range(6000):
        counts[policy.draw_family(rng, 0)] += 1
    assert counts["pivot"] > counts["corner"] > counts["self_loop"]
    assert sum(counts.values()) == 6000


def test_policy_table_zero_weight_blocks_family() -> None:
    policy = model.Policy(
        {"kind": "table", "weights": {"corner": 0, "pivot": 0, "self_loop": 4}}
    )
    rng = PCG64(3, 3)
    assert all(policy.draw_family(rng, 0) == "self_loop" for _ in range(100))
    with pytest.raises(EngineError):
        model.Policy({"kind": "table", "weights": {"corner": 0, "pivot": 0, "self_loop": 0}})
    with pytest.raises(EngineError):
        model.Policy({"kind": "geometric"})


def _config(**overrides: object) -> dict[str, object]:
    config: dict[str, object] = {
        "branch_id": "g42_engine_test_branch",
        "epistemic_class": "sandbox_exploratory_tainted",
        "unit_id": "g42_engine_test_0001",
        "mode": "normal",
        "system": {"n_vertices": 32, "knot": "0_1"},
        "ensemble": {"temperature": 1.5},
        "policy": {"kind": "uniform"},
        "budget": {"proposals": 240, "cpu_seconds": 120.0, "thin": 6},
    }
    config.update(overrides)
    return config


def test_run_unit_replays_bit_exactly_minus_timing() -> None:
    first = model.run_unit(dict(_config()))  # type: ignore[arg-type]
    second = model.run_unit(dict(_config()))  # type: ignore[arg-type]
    assert first["engine_version"] == model.ENGINE_VERSION
    first.pop("timing")
    second.pop("timing")
    assert first == second
    assert first["final"]["determinant"] == 1
    assert first["completed_reason"] == "proposal_budget"
    assert sum(first["proposals"]["proposed"].values()) == 240
    assert all(first["proposals"][key][family] >= 0 for key in ("proposed", "accepted", "invalid") for family in model.FAMILIES)


def test_run_unit_knotted_seed_rejects_class_changing_pivots() -> None:
    config = _config(
        system={"n_vertices": 160, "knot": "3_1"},
        unit_id="g42_engine_test_trefoil",
        policy={"kind": "table", "weights": {"corner": 1, "pivot": 4, "self_loop": 1}},
        budget={"proposals": 240, "cpu_seconds": 300.0, "thin": 12},
    )
    report = model.run_unit(dict(config))  # type: ignore[arg-type]
    assert report["final"]["determinant"] == 3
    assert report["proposals"]["proposed"]["pivot"] > 0
    assert report["proposals"]["executed"] == 240


def test_cpu_budget_reason() -> None:
    config = _config(budget={"proposals": 10_000_000, "cpu_seconds": 0.001, "thin": 1000})
    report = model.run_unit(dict(config))  # type: ignore[arg-type]
    assert report["completed_reason"] == "cpu_budget"
    assert report["proposals"]["executed"] < 10_000_000


def test_tau_int_initial_positive_sequence() -> None:
    assert model._integral_time([]) is None
    assert model._integral_time([1.0] * 6) is None
    constant = model._integral_time([2.0] * 50)
    assert constant == 0.5
    alternating = model._integral_time([(-1.0) ** k * 1.0 for k in range(200)])
    assert alternating == 0.5
    # Sawtooth k % 8 has negative lag-2 autocovariance, so the initial
    # positive sequence must truncate after lag 1: tau = 0.5 + rho_1 = 5/6.
    sawtooth = model._integral_time([float(k % 8) for k in range(512)])
    assert sawtooth is not None and 0.5 < sawtooth < 1.0
    # A smooth sinusoid keeps several lag covariances positive.
    slow = model._integral_time([math.sin(0.25 * k) for k in range(512)])
    assert slow is not None and slow > 1.0


@pytest.mark.parametrize(
    "mutator",
    [
        lambda c: c.update(epistemic_class="clean"),
        lambda c: c.update(mode="fast"),
        lambda c: c.update(unit_id="g38_wrong_prefix"),
        lambda c: c.update(system={"n_vertices": 31, "knot": "0_1"}),
        lambda c: c.update(system={"n_vertices": 32, "knot": "5_2"}),
        lambda c: c.update(ensemble={"temperature": 0.0}),
        lambda c: c.update(policy={"kind": "adaptive"}),
        lambda c: c.update(budget={"proposals": 0, "cpu_seconds": 10.0, "thin": 1}),
        lambda c: c.update(budget={"proposals": 10, "cpu_seconds": 10.0, "thin": 0}),
        lambda c: c.update(extra_key=None),
        lambda c: c.pop("branch_id"),
    ],
)
def test_config_validation_rejects_mutations(mutator: object) -> None:
    config = _config()
    mutator(config)  # type: ignore[operator]
    with pytest.raises(EngineError):
        model.run_unit(dict(config))  # type: ignore[arg-type]


def test_certify_current_delegates_and_returns_none_on_ambiguity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    unknot = model.seed_ring("0_1", 32)
    trefoil = model.seed_ring("3_1", 160)
    assert model.certify_current(unknot) == model.certify(unknot) == 1
    assert model.certify_current(trefoil) == model.certify(trefoil) == 3
    real_alexander = model._alexander_determinant

    def always_ambiguous(
        vertices: list[model.Vertex], d: tuple[int, int, int]
    ) -> int:
        raise model.CertificationAmbiguityError("forced for test")

    monkeypatch.setattr(model, "_alexander_determinant", always_ambiguous)
    assert model.certify_current(unknot) is None
    with pytest.raises(EngineError):
        model.certify(unknot)
    monkeypatch.setattr(model, "_alexander_determinant", real_alexander)


def test_runtime_ambiguity_is_graceful_terminal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(model, "certify_current", lambda vertices: None)
    report = model.run_unit(dict(_config()))  # type: ignore[arg-type]
    assert report["engine_version"] == model.ENGINE_VERSION
    assert report["completed_reason"] == "certification_ambiguous"
    assert report["final"]["determinant"] is None
    assert report["samples"]["count"] > 0
    assert report["samples"]["rg2_mean"] > 0.0
    assert report["corner_certification_checks"] >= 0


def test_runtime_wrong_determinant_remains_fatal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(model, "certify_current", lambda vertices: 3)
    with pytest.raises(EngineError, match="class"):
        model.run_unit(dict(_config()))  # type: ignore[arg-type]


def test_tail_statistics_present_and_finite() -> None:
    report = model.run_unit(dict(_config()))  # type: ignore[arg-type]
    samples = report["samples"]
    assert samples["rg2_tau_int_tail"] is not None
    assert math.isfinite(samples["rg2_tau_int_tail"])
    assert samples["rg2_tau_int_tail"] >= 0.5
    assert samples["rg2_ess_tail"] is not None
    assert math.isfinite(samples["rg2_ess_tail"])
    assert samples["rg2_ess_tail"] > 0.0


def _branch_envelope(
    unit_ids: list[str], *, branch_id: str = "g42_engine_test_branch"
) -> dict[str, object]:
    return {
        "branch_id": branch_id,
        "epistemic_class": "sandbox_exploratory_tainted",
        "unit_ids": unit_ids,
        "units": {
            unit_id: _config(unit_id=unit_id, branch_id=branch_id)  # type: ignore[call-arg]
            for unit_id in unit_ids
        },
    }


def test_runner_executes_branch_envelope_in_frozen_order() -> None:
    from research.paper_g.g42_fixed_knot_moves import runner

    envelope = _branch_envelope(
        ["g42_engine_test_0001", "g42_engine_test_0002"]
    )
    report = runner.execute(envelope)  # type: ignore[arg-type]
    assert report["branch_id"] == "g42_engine_test_branch"
    assert report["epistemic_class"] == "sandbox_exploratory_tainted"
    assert list(report["units"]) == [
        "g42_engine_test_0001",
        "g42_engine_test_0002",
    ]
    for unit_id, unit_report in report["units"].items():
        assert unit_report["unit_id"] == unit_id
        assert unit_report["final"]["determinant"] == 1


def test_runner_rejects_envelope_mismatches() -> None:
    from research.paper_g.g42_fixed_knot_moves import runner

    envelope = _branch_envelope(["g42_engine_test_0001"])
    envelope["unit_ids"] = ["g42_engine_test_0001", "g42_engine_test_9999"]
    with pytest.raises(ValueError, match="membership"):
        runner.execute(envelope)  # type: ignore[arg-type]

    envelope = _branch_envelope(["g42_engine_test_0001"])
    envelope["units"]["g42_engine_test_0001"]["branch_id"] = "g42_other_branch"
    with pytest.raises(ValueError, match="identity"):
        runner.execute(envelope)  # type: ignore[arg-type]

    envelope = _branch_envelope(["g42_engine_test_0001"])
    envelope["epistemic_class"] = "clean"
    with pytest.raises(ValueError, match="exploratory"):
        runner.execute(envelope)  # type: ignore[arg-type]


def test_runner_tar_member_is_deterministic_snapshot() -> None:
    import io
    import json
    import tarfile

    report = model.run_unit(dict(_config()))  # type: ignore[arg-type]
    data = json.dumps(report, sort_keys=True, allow_nan=False).encode()
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        member = tarfile.TarInfo("exploratory_response.json")
        member.size = len(data)
        member.mode = 0o444
        member.mtime = 0
        archive.addfile(member, io.BytesIO(data))
    buffer.seek(0)
    with tarfile.open(fileobj=buffer, mode="r:") as archive:
        extracted = archive.getmember("exploratory_response.json")
        assert extracted.mode == 0o444
        assert extracted.mtime == 0
        payload = archive.extractfile("exploratory_response.json")
        assert payload is not None
        parsed = json.loads(payload.read().decode())
    timing = parsed.pop("timing")
    report_copy = dict(report)
    report_copy.pop("timing")
    assert parsed == report_copy
    assert set(timing) == {"cpu_seconds"}


def test_context_policy_zero_bucket_rejected() -> None:
    with pytest.raises(EngineError, match="bucket total"):
        model.Policy(
            {
                "kind": "table",
                "weights": {"corner": 1, "pivot": 1, "self_loop": 1},
                "context": {
                    "observable": "rg2_bucket",
                    "thresholds": [10.0, 20.0],
                    "multipliers": {
                        "corner": [1, 1, 0],
                        "pivot": [1, 1, 0],
                        "self_loop": [1, 1, 0],
                    },
                },
            }
        )


def test_low_temperature_acceptance_does_not_overflow() -> None:
    config = _config(
        ensemble={"temperature": 0.0005},
        budget={"proposals": 240, "cpu_seconds": 120.0, "thin": 6},
    )
    report = model.run_unit(dict(config))  # type: ignore[arg-type]
    assert report["completed_reason"] in {
        "proposal_budget",
        "certification_ambiguous",
    }


def test_tail_variance_marker_present_and_finite() -> None:
    report = model.run_unit(dict(_config()))  # type: ignore[arg-type]
    tail_var = report["samples"]["rg2_var_tail"]
    assert isinstance(tail_var, float)
    assert math.isfinite(tail_var)
    assert tail_var >= 0.0


def test_runner_rejects_swapped_inner_unit_id() -> None:
    from research.paper_g.g42_fixed_knot_moves import runner

    envelope = _branch_envelope(["g42_engine_test_0001", "g42_engine_test_0002"])
    envelope["units"]["g42_engine_test_0001"]["unit_id"] = "g42_engine_test_0002"
    with pytest.raises(ValueError, match="unit_id"):
        runner.execute(envelope)  # type: ignore[arg-type]


def test_runner_main_emits_envelope_tar(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: object,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    import io
    import json
    import tarfile
    from pathlib import Path

    from research.paper_g.g42_fixed_knot_moves import runner

    config_path = Path(str(tmp_path)) / "config.json"
    config_path.write_text(json.dumps(_branch_envelope(["g42_engine_test_0001"])))
    monkeypatch.setenv("ECOMD_DX_SANDBOX_ID", "g42_engine_test_sandbox")
    monkeypatch.setenv("ECOMD_DX_BRANCH_ID", "g42_engine_test_branch")
    monkeypatch.setenv("ECOMD_DX_CONFIG", str(config_path))
    runner.main()
    captured = capsysbinary.readouterr().out
    with tarfile.open(fileobj=io.BytesIO(captured), mode="r:") as archive:
        member = archive.getmember("exploratory_response.json")
        assert member.mode == 0o444
        assert member.mtime == 0
        payload = archive.extractfile("exploratory_response.json")
        assert payload is not None
        parsed = json.loads(payload.read().decode())
    assert parsed["branch_id"] == "g42_engine_test_branch"
    unit = parsed["units"]["g42_engine_test_0001"]
    assert unit["unit_id"] == "g42_engine_test_0001"
    assert unit["final"]["determinant"] == 1


def test_runner_main_rejects_branch_mismatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: object,
) -> None:
    import json
    from pathlib import Path

    from research.paper_g.g42_fixed_knot_moves import runner

    config_path = Path(str(tmp_path)) / "config.json"
    config_path.write_text(json.dumps(_branch_envelope(["g42_engine_test_0001"])))
    monkeypatch.setenv("ECOMD_DX_SANDBOX_ID", "g42_engine_test_sandbox")
    monkeypatch.setenv("ECOMD_DX_BRANCH_ID", "g42_someone_elses_branch")
    monkeypatch.setenv("ECOMD_DX_CONFIG", str(config_path))
    with pytest.raises(ValueError, match="branch identity"):
        runner.main()
