"""Tests for canonical band scoring."""

from __future__ import annotations

import pytest

from ecomd.eval.canonical_bands import (
    CANONICAL_FACT_BANDS,
    normalized_band_distance,
    score_against_canonical_bands,
)


def test_normalized_band_distance() -> None:
    assert normalized_band_distance(3.0, 2.0, 4.0) == 0.0
    assert normalized_band_distance(1.0, 2.0, 4.0) == pytest.approx(0.5)
    assert normalized_band_distance(5.0, 2.0, 4.0) == pytest.approx(0.5)


def test_score_all_band_midpoints_pass() -> None:
    estimates = {name: (lower + upper) / 2.0 for name, (lower, upper) in CANONICAL_FACT_BANDS.items()}
    score = score_against_canonical_bands(estimates)
    assert score.pass_count == 11
    assert score.mean_normalized_distance == 0.0


def test_score_requires_all_facts() -> None:
    with pytest.raises(ValueError, match="missing canonical facts"):
        score_against_canonical_bands({"hill_tail_index": 3.0})
