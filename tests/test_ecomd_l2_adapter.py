from __future__ import annotations

import numpy as np
import pytest

from ecomd.observation.ecomd_l2_adapter import (
    EcoMDL2Adapter,
    EcoMDL2AdapterConfig,
    EcoMDL2AdapterState,
)
from ecomd.observation.l2_emission import reconstruct_aggregate_book


def _concatenate(streams, field: str) -> np.ndarray:
    return np.concatenate([getattr(stream, field) for stream in streams], axis=0)


def test_adapter_chunks_and_checkpoint_are_bit_exact() -> None:
    adapter = EcoMDL2Adapter(EcoMDL2AdapterConfig(dt=0.005))
    latent = np.random.default_rng(136).standard_normal(120)
    initial = adapter.init_state(seed=6136, start_step=500)
    full_state, full = adapter.emit(initial.clone(), latent, start_step=500)

    state = initial.clone()
    streams = []
    offset = 0
    for length in (17, 31, 72):
        state, stream = adapter.emit(
            state, latent[offset : offset + length], start_step=500 + offset
        )
        streams.append(stream)
        offset += length
        if offset == 48:
            state = EcoMDL2AdapterState.from_checkpoint(state.to_checkpoint())

    for field in (
        "latent",
        "time",
        "event_type",
        "order_id",
        "size",
        "price",
        "direction",
        "snapshots",
    ):
        np.testing.assert_array_equal(getattr(full, field), _concatenate(streams, field))
    np.testing.assert_array_equal(full_state.current_book, state.current_book)
    assert full_state.next_step == state.next_step
    assert full_state.next_order_id == state.next_order_id
    assert full_state.rng_state == state.rng_state
    np.testing.assert_array_equal(reconstruct_aggregate_book(full), full.snapshots)


def test_adapter_clock_and_anchor_validation() -> None:
    with pytest.raises(ValueError, match="positive"):
        EcoMDL2AdapterConfig(dt=0.005, beta_emit=0.0)
    adapter = EcoMDL2Adapter(EcoMDL2AdapterConfig(dt=0.005))
    state = adapter.init_state(seed=1, start_step=10)
    with pytest.raises(ValueError, match="clock mismatch"):
        adapter.emit(state, np.ones(2), start_step=9)


def test_positive_alignment_maps_to_positive_visible_flow() -> None:
    adapter = EcoMDL2Adapter(EcoMDL2AdapterConfig(dt=0.005, beta_emit=2.0))
    latent = np.concatenate((np.full(10_000, -1.0), np.full(10_000, 1.0)))
    _, stream = adapter.emit(
        adapter.init_state(seed=2), latent, start_step=0
    )
    visible = stream.event_type != 5
    action = np.where(stream.event_type == 1, 1, -1)
    signed_flow = stream.direction * action
    negative_rate = float(np.mean(signed_flow[:10_000][visible[:10_000]] == 1))
    positive_rate = float(np.mean(signed_flow[10_000:][visible[10_000:]] == 1))
    assert negative_rate < 0.05
    assert positive_rate > 0.95
