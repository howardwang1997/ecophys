from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


def _module():
    path = Path(__file__).resolve().parents[1] / "experiments/137_free_lobster_dynamic_baselines/run_baselines.py"
    spec = importlib.util.spec_from_file_location("run_free_lobster_baselines", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _book(bid_size: int, ask_size: int) -> list[int]:
    return [10100, ask_size, 10000, bid_size, 10200, 20, 9900, 20]


def test_event_classes_and_history_are_causal() -> None:
    module = _module()
    messages = np.array(
        [
            [1.0, 1, 1, 5, 10000, 1],
            [1.1, 4, 2, 2, 10100, -1],
            [1.2, 5, 3, 1, 10000, 1],
        ],
        dtype=np.float64,
    )
    classes = module.event_classes(messages)
    assert classes.tolist() == [0, 7, 8]
    history = module.history_features(messages[:, 0], classes, [0.1, 1.0])
    assert history.shape == (3, 20)
    assert history[0, 0] > 0.0
    assert history[0, 7] == 0.0
    assert history[1, 7] > 0.0


def test_dynamic_book_audit_accepts_exact_price_level_changes() -> None:
    module = _module()
    messages = np.array(
        [
            [1.0, 1, 1, 10, 10000, 1],
            [1.1, 1, 2, 5, 10000, 1],
            [1.2, 4, 3, 3, 10100, -1],
        ],
        dtype=np.float64,
    )
    books = np.array([_book(10, 10), _book(15, 10), _book(15, 7)], dtype=np.int64)
    result = module.audit_dynamic_book(messages, books, depth=2)
    assert result["book_checks_pass"] is True
    assert result["visible_reconstruction_rate"] == 1.0
    assert result["visible_type_1_to_4_events"] == 2


def test_queue_features_have_fixed_shape_and_finite_values() -> None:
    module = _module()
    books = np.array([_book(10, 10), _book(15, 7), _book(12, 9)], dtype=np.int64)
    features = module.queue_features(books, np.array([1.0, 1.1, 1.3]), depth=2)
    assert features.shape == (3, 9)
    assert np.isfinite(features).all()
