from __future__ import annotations

from dataclasses import fields, replace
from typing import Any

import numpy as np

from ecomd.observation.dynamic_l2 import (
    DynamicL2Config,
    DynamicL2Generator,
    DynamicL2State,
    DynamicL2Stream,
    reconstruct_dynamic_l2,
)
from ecomd.observation.l2_emission import simulate_latent_ar1


def _tree_equal(left: Any, right: Any) -> bool:
    if isinstance(left, np.ndarray) and isinstance(right, np.ndarray):
        return bool(np.array_equal(left, right))
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(
            _tree_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, (list, tuple)) and isinstance(right, type(left)):
        return len(left) == len(right) and all(
            _tree_equal(a, b) for a, b in zip(left, right, strict=True)
        )
    return bool(left == right)


def _concatenate(parts: list[DynamicL2Stream]) -> DynamicL2Stream:
    values = {
        field.name: np.concatenate(
            [getattr(part, field.name) for part in parts], axis=0
        )
        for field in fields(DynamicL2Stream)
    }
    return DynamicL2Stream(**values)


def test_dynamic_book_chunk_resume_and_reconstruction() -> None:
    config = DynamicL2Config()
    latent = simulate_latent_ar1(5_000, 0.6, np.random.default_rng(13701))
    operator = DynamicL2Generator(config, "latent_incremental", censor_rate=0.2)
    initial = operator.init_state(seed=13702)
    full_state, full = operator.emit(initial.clone(), latent, start_event=0)

    chunk_state = initial.clone()
    parts: list[DynamicL2Stream] = []
    offset = 0
    for length in (137, 499, 61, 803, 1_500, 2_000):
        chunk_state, part = operator.emit(
            chunk_state, latent[offset : offset + length], start_event=offset
        )
        parts.append(part)
        offset += length
        if offset == 1_500:
            chunk_state = DynamicL2State.from_checkpoint(
                chunk_state.to_checkpoint()
            )
    chunked = _concatenate(parts)

    assert offset == latent.size
    for field in fields(DynamicL2Stream):
        assert np.array_equal(getattr(full, field.name), getattr(chunked, field.name))
    assert _tree_equal(full_state.to_checkpoint(), chunk_state.to_checkpoint())

    books, mids, moves = reconstruct_dynamic_l2(full, config)
    assert np.array_equal(books, full.snapshots)
    assert np.array_equal(mids, full.mid_tick)
    assert np.array_equal(moves, full.price_move)
    assert np.all(full.snapshots[:, 1::4] > 0)
    assert np.all(full.snapshots[:, 3::4] > 0)
    moving = full.price_move != 0
    assert np.array_equal(full.price_move[moving], full.signed_flow[moving])
    assert set(full.price_move[moving]) == {-1, 1}


def test_observation_only_flow_is_invariant_to_latent_sign() -> None:
    config = DynamicL2Config()
    latent = simulate_latent_ar1(2_000, 0.95, np.random.default_rng(13703))
    operator = DynamicL2Generator(config, "observation_only", censor_rate=0.0)
    initial = operator.init_state(seed=13704)
    _, positive = operator.emit(initial.clone(), latent, start_event=0)
    _, negative = operator.emit(initial.clone(), -latent, start_event=0)

    for field in fields(DynamicL2Stream):
        if field.name == "latent":
            continue
        assert np.array_equal(
            getattr(positive, field.name), getattr(negative, field.name)
        )


def test_dynamic_book_rejects_clock_state_and_tampered_price() -> None:
    config = DynamicL2Config()
    latent = np.linspace(-1.0, 1.0, 100, dtype=np.float64)
    operator = DynamicL2Generator(config, "latent_incremental", censor_rate=0.0)
    state = operator.init_state(seed=13705)

    try:
        operator.emit(state.clone(), latent, start_event=1)
    except ValueError as error:
        assert "clock mismatch" in str(error)
    else:
        raise AssertionError("clock mismatch must fail")

    broken = state.clone()
    broken.current_book[1] = 0
    try:
        operator.emit(broken, latent, start_event=0)
    except ValueError as error:
        assert "queues must be positive" in str(error)
    else:
        raise AssertionError("non-positive queue must fail")

    _, stream = operator.emit(state, latent, start_event=0)
    price = stream.price.copy()
    visible = int(np.flatnonzero(stream.event_type != 5)[0])
    price[visible] += 100
    tampered = replace(stream, price=price)
    try:
        reconstruct_dynamic_l2(tampered, config)
    except ValueError as error:
        assert "outside the displayed" in str(error)
    else:
        raise AssertionError("tampered price must fail")


def test_dynamic_book_validates_configuration_and_truth() -> None:
    for kwargs in (
        {"initial_queue": 1},
        {"p_hidden": 1.0},
        {"p_add": 0.0},
        {"removal_probabilities": (0.2, 0.2, 0.2)},
    ):
        try:
            DynamicL2Config(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid configuration accepted: {kwargs}")

    try:
        DynamicL2Generator(DynamicL2Config(), "unknown", censor_rate=0.0)  # type: ignore[arg-type]
    except ValueError as error:
        assert "unknown truth" in str(error)
    else:
        raise AssertionError("unknown truth must fail")
