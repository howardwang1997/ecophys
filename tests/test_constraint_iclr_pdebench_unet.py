from __future__ import annotations

import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_constraint_iclr_pdebench_fno import build_model  # noqa: E402


def _cfg() -> dict[str, int | str]:
    return {"architecture": "unet1d", "history": 10, "channels": 8}


def test_unet_replication_supports_all_registered_resolutions() -> None:
    model = build_model(_cfg(), "free")
    for resolution in (256, 512, 1024):
        history = torch.randn(2, resolution, 10)
        grid = torch.linspace(0.0, 1.0, resolution)
        assert model(history, grid).shape == (2, resolution)


def test_unet_hard_arms_conserve_previous_mass() -> None:
    history = torch.randn(3, 256, 10)
    grid = torch.linspace(0.0, 1.0, 256)
    for mechanism in ("hard_abs", "hard"):
        prediction = build_model(_cfg(), mechanism)(history, grid)
        torch.testing.assert_close(prediction.mean(dim=-1), history[..., -1].mean(dim=-1), atol=1e-6, rtol=0)
