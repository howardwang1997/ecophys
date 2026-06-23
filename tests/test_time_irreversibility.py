"""Tests for the DHVG model-free time-irreversibility estimator (Paper A C-a)."""
import numpy as np

from ecomd.eval.time_irreversibility import dhvg_irreversibility, hvg_degrees, windowed_dhvg


def test_hvg_degrees_monotone():
    # strictly increasing: each point sees only its immediate neighbours horizontally
    out_deg, in_deg = hvg_degrees(np.arange(6, dtype=float))
    # total directed edges = sum(out) == sum(in); a path graph has n-1 edges
    assert out_deg.sum() == in_deg.sum() == 5


def test_dhvg_reversible_series_near_zero():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(4000)            # iid → statistically time-reversible
    d = dhvg_irreversibility(x)
    assert d < 0.02, f"iid series should be ~reversible, got {d}"


def test_dhvg_irreversible_sawtooth_positive_and_asymmetric():
    # slow linear ramp, sharp drop — a canonical time-irreversible signal
    tooth = np.concatenate([np.linspace(0, 1, 20), [0.0]])
    x = np.tile(tooth, 80)
    d_fwd = dhvg_irreversibility(x)
    d_rev = dhvg_irreversibility(x[::-1])
    assert d_fwd > 0.01, f"sawtooth should be irreversible, got {d_fwd}"
    # time-reversal must change the (asymmetric) KL divergence
    assert abs(d_fwd - d_rev) > 1e-6


def test_windowed_shapes():
    x = np.random.default_rng(1).standard_normal(2000)
    c, v = windowed_dhvg(x, W=500, stride=100)
    assert c.shape == v.shape and c.size > 0 and np.all(np.isfinite(v))
