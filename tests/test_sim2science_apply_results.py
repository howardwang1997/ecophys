from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest


def _module() -> ModuleType:
    root = Path(__file__).resolve().parents[1]
    path = root / "papers/paper_a_methods/workshops/sim2science/apply_learned_results.py"
    spec = importlib.util.spec_from_file_location("sim2science_apply_results", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _payload() -> dict[str, Any]:
    return {
        "primary": {
            "e1_total": 7,
            "e1_scorable": 6,
            "e1_heldout_gate_confirmed": 5,
            "effect": 0.416,
            "ci_95": [0.104, 0.793],
            "expected_positive_direction_passes": True,
            "e3_scorable": 3,
            "e3_positive_sign_count": 2,
            "e3_same_positive_sign_2_of_3": True,
        }
    }


def _robustness() -> dict[str, Any]:
    return {
        "crossed_checkpoint_seed_bootstrap": {"ci_95": [0.051, 0.811]},
        "market_balanced_sensitivity": {"leave_one_out_range": [0.221, 0.611]},
        "hill_fraction_sensitivity": {"positive_common_seed_interval_count": 2},
    }


def test_macro_values_use_paper_precision_and_fixed_denominator() -> None:
    module = _module()
    assert module.macro_values(_payload(), _robustness()) == {
        "learnedScorable": "6",
        "learnedConfirmed": "5",
        "learnedDelta": r"\ensuremath{+0.42}",
        "learnedCI": r"\ensuremath{[+0.10,\,+0.79]}",
        "variantSigns": r"\ensuremath{2/3}",
        "learnedRobustCI": r"\ensuremath{[+0.05,\,+0.81]}",
        "learnedLooRange": r"\ensuremath{[+0.22,\,+0.61]}",
        "hillFractionPasses": r"\ensuremath{2/3}",
    }


def test_synchronize_text_is_idempotent() -> None:
    module = _module()
    source = "".join(
        f"\\newcommand{{\\{name}}}{{\\pending}}\n" for name in module.MACRO_NAMES
    )
    values = module.macro_values(_payload(), _robustness())
    updated = module.synchronize_text(source, values)
    assert module.synchronize_text(updated, values) == updated
    assert r"\newcommand{\learnedScorable}{6}" in updated


def test_macro_values_reject_missing_effect() -> None:
    module = _module()
    payload = _payload()
    payload["primary"]["effect"] = None
    with pytest.raises(ValueError, match="effect and interval"):
        module.macro_values(payload, _robustness())
