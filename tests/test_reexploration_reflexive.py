"""Tests for the reflexive deployment cell (pre-freeze build item 10).

Mac-legal seconds-scale spot checks only (PI compute rule 2026-09-19): the
full-suite run and the N<=500 smoke execute remotely. Engine-path tests
avoid torch entirely (the module imports it lazily); model-path tests use
throwaway untrained instances and check internal consistency against
direct head/forward calls, never scientific behavior.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ecomd.reexploration.reflexive import (
    CELLS,
    REFLEXIVE_LABEL,
    REFLEXIVE_SEEDS,
    RUN_ID_PREFIX,
    AdaptiveExecutionPolicy,
    DgpFeedback,
    Observation,
    PolicyAction,
    PolicyConfig,
    StubFeedback,
    assert_seed_disjointness,
    build_model_feedback,
    reflexive_seed,
    run_reflexive_session,
    summarize,
    validate_cell_vocabulary,
    validate_namespace,
)

TINY = PolicyConfig(q_total=6, n_rounds=12, warmup_rounds=5)


# ── seeds ────────────────────────────────────────────────────────────────────


def test_reflexive_seed_is_the_e2_sha256_idiom() -> None:
    payload = "|".join(("11000", "reflexive", "background"))
    expected = int(hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8], 16)
    assert reflexive_seed(11000, "background") == expected
    assert reflexive_seed(11000, "background") != reflexive_seed(11000, "other")
    assert reflexive_seed(11000, "background") != reflexive_seed(11001, "background")


def test_seed_disjointness_assertion_fires_on_collision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ecomd.training.train_fact_surrogate as tfs

    colliding = reflexive_seed(11000, "background")
    monkeypatch.setattr(
        tfs, "derive_substream_seeds", lambda root: {"data": colliding}
    )
    with pytest.raises(RuntimeError, match="collides"):
        assert_seed_disjointness(11000)


def test_seed_disjointness_holds_for_reflexive_subset() -> None:
    for seed in REFLEXIVE_SEEDS["l1"][:3] + REFLEXIVE_SEEDS["l2"][:3]:
        assert_seed_disjointness(seed)


def test_cell_vocabulary_matches_campaign() -> None:
    validate_cell_vocabulary()


# ── policy ───────────────────────────────────────────────────────────────────


def test_policy_config_validation() -> None:
    with pytest.raises(ValueError, match="behind-schedule"):
        PolicyConfig(urgency_cross=1.0)
    with pytest.raises(ValueError, match="participation"):
        PolicyConfig(participation=0.0)
    with pytest.raises(ValueError, match="ewma_alpha"):
        PolicyConfig(ewma_alpha=1.5)


def _obs(**kwargs: object) -> Observation:
    defaults: dict[str, object] = {
        "round_index": 0,
        "rounds_left": 100,
        "remaining": 50,
        "ewma_volume": 10.0,
        "streak": 0,
        "best_bid": 99,
        "best_ask": 101,
        "working_price": None,
        "working_qty": None,
    }
    defaults.update(kwargs)
    return Observation(**defaults)  # type: ignore[arg-type]


def test_policy_urgency_semantics() -> None:
    policy = AdaptiveExecutionPolicy(PolicyConfig(q_total=100, n_rounds=200))
    # On schedule: half the quantity left at half the time -> u = 1.
    assert policy.urgency(_obs(remaining=50, rounds_left=100)) == pytest.approx(1.0)
    # Behind schedule: everything left at quarter time -> u = 4.
    assert policy.urgency(_obs(remaining=100, rounds_left=50)) == pytest.approx(4.0)
    # Last round -> infinity (deadline).
    assert policy.urgency(_obs(rounds_left=0)) == float("inf")


def test_policy_decision_table() -> None:
    policy = AdaptiveExecutionPolicy(PolicyConfig(q_total=100, n_rounds=200))
    # On schedule, spread 2 -> improve one tick inside the ask, chunk floor 1.
    action = policy.decide(_obs(remaining=50, rounds_left=100, ewma_volume=0.0))
    assert action == PolicyAction("place", 100, 1)
    # Tight spread -> join the ask.
    action = policy.decide(
        _obs(remaining=50, rounds_left=100, best_bid=100, best_ask=101)
    )
    assert action.price == 101
    # Chunk = round(participation * ewma), capped by chunk_max and remaining.
    action = policy.decide(
        _obs(remaining=50, rounds_left=100, ewma_volume=1000.0)
    )
    assert action.quantity == 16
    action = policy.decide(_obs(remaining=3, rounds_left=100, ewma_volume=1000.0))
    assert action.quantity == 3
    # Behind schedule escalates to marketable at the bid.
    action = policy.decide(_obs(remaining=100, rounds_left=50))
    assert action == PolicyAction("place", 99, 1)
    # Streak escalation.
    action = policy.decide(_obs(remaining=50, rounds_left=100, streak=3))
    assert action.price == 99
    # Working order present -> reprice, not place.
    action = policy.decide(_obs(remaining=50, rounds_left=100, working_qty=4))
    assert action.kind == "reprice"
    # Unchanged target price -> hold the working order (queue priority).
    action = policy.decide(
        _obs(remaining=50, rounds_left=100, working_price=100, working_qty=4)
    )
    assert action.kind == "idle"
    # Done -> cancel the leftover working order, then idle.
    assert policy.decide(_obs(remaining=0, working_qty=4)).kind == "cancel"
    assert policy.decide(_obs(remaining=0)).kind == "idle"


def test_policy_ewma_and_streak_update() -> None:
    policy = AdaptiveExecutionPolicy(PolicyConfig(q_total=10, n_rounds=10))
    policy.update(4.0, 0)
    assert policy.state.ewma_volume == pytest.approx(1.0)
    assert policy.state.streak == 1
    policy.update(4.0, 0, count_streak=False)
    assert policy.state.streak == 1  # warmup mode does not accrue
    policy.update(4.0, 3)
    assert policy.state.streak == 0
    assert policy.state.filled_units == 3
    assert policy.state.remaining == 7
    assert policy.state.ewma_volume == pytest.approx(0.75 * 1.75 + 0.25 * 4.0)


def test_stub_feedback_multiplier() -> None:
    base = DgpFeedback()
    stub = StubFeedback(base, 8.0)
    stub.consume_round(None, (0, 0), 3)
    assert stub.latest() == 24
    assert StubFeedback(base, 0.0).latest() == 0


# ── sessions (engine-only paths; no torch) ──────────────────────────────────


def test_dgp_smoke_session_contract() -> None:
    record = run_reflexive_session(
        seed=11000, lineage="l1", cell_id="R00", arm="dgp",
        config=TINY, smoke=True,
    )
    assert record["run_id"] == "RFX-l1-R00-dgp-11000-SMOKE"
    assert record["exploratory"] is True and record["reflexive"] is True
    assert record["label"] == REFLEXIVE_LABEL
    assert record["smoke"] is True
    assert record["replay_ok"] is True
    metrics = record["metrics"]
    assert metrics["filled_units"] + metrics["unfilled_units"] == TINY.q_total
    assert metrics["filled_units"] == (
        metrics["passive_fill_units"] + metrics["aggressive_fill_units"]
    )
    assert len(record["tape_sha256"]) == 64
    assert record["cell"] == {
        "r_label": "R00", "arm_id": "absolute_raw",
        "inference_enforcement": "raw", "coordinate": "absolute",
    }
    assert record["feedback"]["channel"] == "volume_increment"
    validate_namespace([record])


def test_dgp_session_determinism() -> None:
    kwargs = dict(
        seed=12003, lineage="l2", cell_id="R11", arm="dgp",
        config=TINY, smoke=True,
    )
    first = run_reflexive_session(**kwargs)
    second = run_reflexive_session(**kwargs)
    assert first["tape_sha256"] == second["tape_sha256"]
    assert first["metrics"] == second["metrics"]
    assert first["tape_length"] == second["tape_length"]


def test_stub_feedback_diverges_from_dgp() -> None:
    config = PolicyConfig(
        q_total=40, n_rounds=20, warmup_rounds=6, participation=0.5, chunk_max=16
    )
    dgp = run_reflexive_session(
        seed=11001, lineage="l1", cell_id="R00", arm="dgp",
        config=config, smoke=True,
    )
    stub = run_reflexive_session(
        seed=11001, lineage="l1", cell_id="R00", arm="sim",
        feedback=StubFeedback(DgpFeedback(), 8.0),
        config=config, smoke=True,
    )
    assert stub["arm"] == "sim"
    assert stub["tape_sha256"] != dgp["tape_sha256"]


def test_session_guards() -> None:
    # Seed outside the Annex B(d) subset.
    with pytest.raises(SystemExit, match="Annex B"):
        run_reflexive_session(
            seed=11010, lineage="l1", cell_id="R00", arm="dgp",
            config=TINY, smoke=True,
        )
    # Unknown cell.
    with pytest.raises(SystemExit, match="unknown cell"):
        run_reflexive_session(
            seed=11000, lineage="l1", cell_id="R01", arm="dgp",
            config=TINY, smoke=True,
        )
    # Smoke cannot carry a checkpoint reference.
    with pytest.raises(SystemExit, match="checkpoints"):
        run_reflexive_session(
            seed=11000, lineage="l1", cell_id="R00", arm="dgp",
            config=TINY, smoke=True, checkpoint_ref="ckpt.pt",
        )
    # Sim arm needs a feedback provider.
    with pytest.raises(SystemExit, match="feedback"):
        run_reflexive_session(
            seed=11000, lineage="l1", cell_id="R00", arm="sim",
            config=TINY, smoke=True,
        )


def test_unlock_gate() -> None:
    base = dict(
        seed=11000, lineage="l1", cell_id="R00", arm="dgp", config=TINY
    )
    # Non-smoke without an unlock file: refused.
    with pytest.raises(SystemExit, match="unlock"):
        run_reflexive_session(**base)
    # Three hashes: refused.
    bad = Path("/tmp/rfx_bad_unlock.txt")
    bad.write_text("\n".join("a" * 64 for _ in range(3)) + "\n")
    with pytest.raises(SystemExit, match="sha256"):
        run_reflexive_session(**base, unlock_file=bad)
    # Four valid hex lines: runs, and the record is non-smoke.
    good = Path("/tmp/rfx_good_unlock.txt")
    good.write_text("\n".join(f"{i:064x}" for i in range(4)) + "\n")
    record = run_reflexive_session(**base, unlock_file=good)
    assert record["smoke"] is False
    assert record["run_id"] == "RFX-l1-R00-dgp-11000"
    bad.unlink()
    good.unlink()


def test_out_dir_guards(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="firewall 1"):
        run_reflexive_session(
            seed=11000, lineage="l1", cell_id="R00", arm="dgp",
            config=TINY, smoke=True, out_dir=tmp_path / "plain",
        )
    with pytest.raises(SystemExit, match="smoke"):
        run_reflexive_session(
            seed=11000, lineage="l1", cell_id="R00", arm="dgp",
            config=TINY, smoke=True, out_dir=tmp_path / "reflexive" / "runs",
        )
    out_dir = tmp_path / "reflexive" / "smoke"
    record = run_reflexive_session(
        seed=11000, lineage="l1", cell_id="R00", arm="dgp",
        config=TINY, smoke=True, out_dir=out_dir,
    )
    written = out_dir / f"{record['run_id']}.json"
    assert written.exists()
    assert json.loads(written.read_text())["tape_sha256"] == record["tape_sha256"]


def test_namespace_validation_refuses_tampered_records() -> None:
    record = run_reflexive_session(
        seed=11002, lineage="l1", cell_id="R00", arm="dgp",
        config=TINY, smoke=True,
    )
    tampered = dict(record)
    tampered["run_id"] = record["run_id"].replace(RUN_ID_PREFIX, "CFG-")
    with pytest.raises(SystemExit, match="prefix"):
        validate_namespace([tampered])
    tampered = dict(record)
    del tampered["label"]
    with pytest.raises(SystemExit, match="label"):
        validate_namespace([tampered])


def test_summarize_gap_arithmetic() -> None:
    def rec(seed: int, arm: str, shortfall: float, smoke: bool = False) -> dict:
        return {
            "run_id": f"{RUN_ID_PREFIX}l1-R00-{arm}-{seed}",
            "exploratory": True,
            "reflexive": True,
            "smoke": smoke,
            "label": REFLEXIVE_LABEL,
            "lineage": "l1",
            "cell": {"r_label": "R00"},
            "seed": seed,
            "arm": arm,
            "metrics": {
                "implementation_shortfall_ticks": shortfall,
                "unfilled_marked_shortfall_ticks": 0.0,
                "avg_fill_price": 100.0,
                "cash_received": 100,
                "filled_units": 1,
                "unfilled_units": 0,
                "passive_fill_units": 1,
                "aggressive_fill_units": 0,
                "rounds_to_complete": 5,
            },
        }

    records = [
        rec(11000, "dgp", 10.0), rec(11000, "sim", 13.0),   # gap +3
        rec(11001, "dgp", 10.0), rec(11001, "sim", 8.0),    # gap -2
        rec(11005, "dgp", 99.0),                             # unpaired: excluded
        rec(11006, "dgp", 1.0, smoke=True),                  # smoke: excluded
    ]
    summary = summarize(records)
    assert summary["label"] == REFLEXIVE_LABEL
    group = summary["groups"]["l1|R00"]
    assert group["paired_seeds"] == 2
    gaps = group["gap_sim_minus_dgp"]["implementation_shortfall_ticks"]
    assert gaps["mean"] == pytest.approx(0.5)
    assert gaps["min"] == pytest.approx(-2.0)
    assert gaps["max"] == pytest.approx(3.0)


# ── model feedback (torch; throwaway instances; consistency only) ───────────


def test_model_feedback_l1_raw_matches_forward() -> None:
    import torch

    from ecomd.models.fact_surrogate import FactSurrogateBatch
    from ecomd.models.l1_coordinate_heads import L1CoordinateHeads

    torch.manual_seed(0)
    model = L1CoordinateHeads()
    model.eval()
    features = torch.randn(14)  # d_features = len(FEXEC_ROUND_FEATURES)
    x_pre = (3, 1500)
    provider = build_model_feedback(
        model, coordinate="increment", inference_enforcement="raw", seed_root=11000
    )
    provider.consume_round(features, x_pre, 5)
    with torch.no_grad():
        batch = FactSurrogateBatch(
            features=features.view(1, 1, -1),
            channels=torch.tensor([[[x_pre[0], x_pre[1]]]], dtype=torch.float32),
            slot_prices=torch.zeros(1, 1, model.cfg.n_slots),
            channels_init=torch.tensor([[x_pre[0], x_pre[1]]], dtype=torch.float32),
        )
        expected = float(model(batch).inc_channels[0, 0, 0])
    assert provider.latest() == max(0, round(expected))


def test_model_feedback_l1_absolute_coordinate() -> None:
    import torch

    from ecomd.models.fact_surrogate import FactSurrogateBatch
    from ecomd.models.l1_coordinate_heads import L1CoordinateHeads

    torch.manual_seed(1)
    model = L1CoordinateHeads()
    model.eval()
    features = torch.randn(14)
    x_pre = (7, 2100)
    provider = build_model_feedback(
        model, coordinate="absolute", inference_enforcement="raw", seed_root=11000
    )
    provider.consume_round(features, x_pre, 2)
    with torch.no_grad():
        batch = FactSurrogateBatch(
            features=features.view(1, 1, -1),
            channels=torch.tensor([[[x_pre[0], x_pre[1]]]], dtype=torch.float32),
            slot_prices=torch.zeros(1, 1, model.cfg.n_slots),
            channels_init=torch.tensor([[x_pre[0], x_pre[1]]], dtype=torch.float32),
        )
        expected = float(model(batch).abs_channels[0, 0, 0]) - x_pre[0]
    assert provider.latest() == max(0, round(expected))


def test_model_feedback_through_m_volume_lattice() -> None:
    import torch

    from ecomd.models.l1_coordinate_heads import L1CoordinateHeads

    torch.manual_seed(2)
    model = L1CoordinateHeads()
    model.eval()
    provider = build_model_feedback(
        model,
        coordinate=CELLS["R11"].coordinate,
        inference_enforcement=CELLS["R11"].inference_enforcement,
        seed_root=11003,
    )
    features = torch.randn(14)
    provider.consume_round(features, (0, 0), 1)
    first = provider.latest()
    assert first >= 0
    twin = build_model_feedback(
        L1CoordinateHeads(),  # different weights, same grammar
        coordinate="increment",
        inference_enforcement="through_m",
        seed_root=11003,
    )
    twin.consume_round(features, (0, 0), 1)
    assert twin.latest() >= 0


def test_model_feedback_l2_pre_round_timing() -> None:
    import torch

    from ecomd.models.fact_surrogate import RecurrentFactSurrogate

    torch.manual_seed(3)
    model = RecurrentFactSurrogate()
    model.eval()
    features_0 = torch.randn(14)
    features_1 = torch.randn(14)
    provider = build_model_feedback(
        model, coordinate="increment", inference_enforcement="raw", seed_root=12000
    )
    with torch.no_grad():
        h0 = model.init_hidden(1)
        decode_round_0 = float(model.inc_head(h0)[0, 0])
    provider.consume_round(features_0, (0, 0), 1)
    # The decode for round 0 was made from h_0 BEFORE consuming features_0.
    assert provider.latest() == max(0, round(decode_round_0))
    with torch.no_grad():
        h1 = model.cell(features_0.view(1, -1), h0)
        decode_round_1 = float(model.inc_head(h1)[0, 0])
    provider.consume_round(features_1, (0, 0), 1)
    assert provider.latest() == max(0, round(decode_round_1))
