"""Tests for paper-a-solidify additions: yfinance loaders, period split,
sign_mode, volume_mode."""

from __future__ import annotations

from pathlib import Path

import pytest
import torch

from ecomd.models.price_formation import ExcessDemandParams, ExcessDemandPrice
from ecomd.training.train_distributed import (
    _YFINANCE_DAILY_SYMBOL,
    _parse_period,
    load_real_returns,
)

REPO = Path(__file__).resolve().parents[1]


# ─── Period parser ─────────────────────────────────────────────────────


def test_parse_period_full():
    assert _parse_period("2015-2026_daily") == (None, None)


def test_parse_period_subrange():
    assert _parse_period("2015-2019_daily") == (2015, 2019)


def test_parse_period_invalid_falls_back():
    assert _parse_period("garbage") == (None, None)


# ─── yfinance loader registry ─────────────────────────────────────────


def test_yfinance_dataset_keys_include_new_tickers():
    for ds in ("dax", "stoxx50", "hsi", "nikkei", "qqq", "iwm", "gold"):
        assert ds in _YFINANCE_DAILY_SYMBOL


def test_load_real_returns_spx_full_period():
    """SPX backwards-compat: full range gives all data."""
    r = load_real_returns(REPO, "spx", "2015-2026_daily")
    assert len(r) > 2000


def test_load_real_returns_spx_subrange_smaller():
    """Subrange should give strictly fewer returns."""
    r_full = load_real_returns(REPO, "spx", "2015-2026_daily")
    r_sub = load_real_returns(REPO, "spx", "2015-2019_daily")
    assert len(r_sub) < len(r_full)


def test_load_real_returns_unknown_dataset_hard_fails():
    with pytest.raises(ValueError, match="unsupported target dataset"):
        load_real_returns(REPO, "typo_market", "2015-2026_daily")


def test_load_real_returns_invalid_period_hard_fails():
    with pytest.raises(ValueError, match="unsupported period"):
        load_real_returns(REPO, "spx", "typo_period")


# ─── Hawkes sign_mode ──────────────────────────────────────────────────


def test_hawkes_sign_modes_diverge():
    """Three sign modes produce different log_price after several steps."""
    final_prices = {}
    for mode in ("coherent", "flipping", "none"):
        torch.manual_seed(0)
        p = ExcessDemandParams(hawkes_alpha=0.2, hawkes_kappa=0.5,
                               hawkes_sign_mode=mode)
        pf = ExcessDemandPrice(p)
        state = pf.init_state(torch.device("cpu"), torch.float32)
        s = torch.randn(20, 3) * 0.1
        gen = torch.Generator().manual_seed(2)
        for _ in range(10):
            sn = s + torch.randn(20, 3) * 0.05
            out = pf.step(state, s, sn, generator=gen)
            state = out.state
            s = sn
        final_prices[mode] = float(state.log_price)

    # All three should be different
    vals = list(final_prices.values())
    assert vals[0] != vals[1]
    assert vals[1] != vals[2]


def test_hawkes_default_is_coherent_backward_compat():
    """Without hawkes_sign_mode, behavior matches old 'coherent' default."""
    p = ExcessDemandParams(hawkes_alpha=0.1, hawkes_kappa=0.3)
    assert p.hawkes_sign_mode == "coherent"


# ─── volume_mode ────────────────────────────────────────────────────


def test_volume_mode_default_is_delta_pos():
    p = ExcessDemandParams()
    assert p.volume_mode == "delta_pos"


def test_volume_mode_price_driven_differs_from_delta_pos():
    """volume_mode='price_driven' produces a different volume from default."""
    s = torch.randn(20, 3) * 0.1
    sn = s + torch.randn_like(s) * 0.05
    g = torch.Generator().manual_seed(0)

    p_def = ExcessDemandParams()
    p_pr = ExcessDemandParams(volume_mode="price_driven")
    out_def = ExcessDemandPrice(p_def).step(
        ExcessDemandPrice(p_def).init_state(torch.device("cpu"), torch.float32),
        s, sn, generator=g,
    )
    out_pr = ExcessDemandPrice(p_pr).step(
        ExcessDemandPrice(p_pr).init_state(torch.device("cpu"), torch.float32),
        s, sn, generator=g,
    )
    assert float(out_def.aux["volume"]) != float(out_pr.aux["volume"])
