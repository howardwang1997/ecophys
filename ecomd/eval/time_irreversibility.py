"""Model-free time-irreversibility estimators for EcoMD / market series.

The sign-level (Δp, OFI) entropy-production proxy in ``scripts/analyze_ofi_entropy.py`` was *flat* at
the shock (it only sees the 2×2 sign-transition table). This module provides a stronger, model-free
estimator that sees the full amplitude structure: the **directed horizontal visibility graph (DHVG)**
irreversibility of Lacasa et al. (2012) / Flanagan & Lacasa (2016).

A real-valued series is mapped to a graph (nodes = samples; horizontal-visibility edges), made
*directed* by time. Its forward (out-degree) and backward (in-degree) degree distributions are equal
iff the series is statistically time-reversible; their Kullback–Leibler divergence

    D = KL( P_out || P_in )

is a single scalar that is 0 for a reversible process and >0 under irreversible (non-equilibrium)
driving. Unlike a Hill tail index it does not saturate at a floor, so it is a censoring-free probe of
the driven transient (Paper A §5 "Mechanism", the C-a strengthening of the entropy reading).

References
----------
- Lacasa, Nunez, Roldan, Parrondo, Luque, *Eur. Phys. J. B* 85, 217 (2012).
- Flanagan & Lacasa, *Phys. Lett. A* 380, 1457 (2016).
- Zumbach, *Quant. Finance* 9, 505 (2009) — the volatility time-reversal asymmetry (second estimator).
"""

from __future__ import annotations

import numpy as np


def hvg_degrees(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Out- and in-degree of every node of the horizontal visibility graph of ``x``.

    Two samples t_a < t_b are connected iff every sample strictly between them is strictly lower than
    ``min(x[t_a], x[t_b])``. The edge is directed forward in time, so it adds to ``out_deg[t_a]`` and
    ``in_deg[t_b]``. O(n) amortized via a monotonic stack.

    Returns ``(out_deg, in_deg)``, each ``(n,)`` int64.
    """
    x = np.asarray(x, dtype=float)
    n = x.size
    out_deg = np.zeros(n, dtype=np.int64)
    in_deg = np.zeros(n, dtype=np.int64)
    stack: list[int] = []  # indices, non-increasing in height
    for i in range(n):
        while stack and x[stack[-1]] < x[i]:
            j = stack.pop()
            out_deg[j] += 1
            in_deg[i] += 1
        if stack:
            j = stack[-1]
            out_deg[j] += 1
            in_deg[i] += 1
            if x[j] == x[i]:        # equal heights block each other (ties: measure-zero for floats)
                stack.pop()
        stack.append(i)
    return out_deg, in_deg


def _deg_hist(deg: np.ndarray, kmax: int) -> np.ndarray:
    h = np.bincount(deg, minlength=kmax + 1)[: kmax + 1].astype(float)
    return h


def dhvg_irreversibility(x: np.ndarray) -> float:
    """KL divergence between the DHVG out-degree and in-degree distributions.

    0 for a time-reversible series; >0 under irreversible driving. Laplace-smoothed so it is finite on
    short windows.
    """
    x = np.asarray(x, dtype=float)
    if x.size < 4:
        return float("nan")
    out_deg, in_deg = hvg_degrees(x)
    kmax = int(max(out_deg.max(), in_deg.max()))
    po = _deg_hist(out_deg, kmax) + 1e-6
    pi = _deg_hist(in_deg, kmax) + 1e-6
    po /= po.sum()
    pi /= pi.sum()
    return float(np.sum(po * np.log(po / pi)))


def windowed_dhvg(x: np.ndarray, W: int, stride: int) -> tuple[np.ndarray, np.ndarray]:
    """Sliding-window DHVG irreversibility. Returns (window_centers, irreversibility)."""
    x = np.asarray(x, dtype=float)
    centers, vals = [], []
    i = 0
    while i + W <= x.size:
        vals.append(dhvg_irreversibility(x[i : i + W]))
        centers.append(i + W // 2)
        i += stride
    return np.asarray(centers), np.asarray(vals)


def zumbach_asymmetry(r: np.ndarray, tau: int = 5) -> float:
    """Zumbach (2009) volatility time-reversal asymmetry.

    Correlation of past realized volatility with future squared return minus the time-reversed version;
    >0 means historical vol predicts future vol better than the reverse (an irreversibility signature).
    A cheap second estimator alongside the DHVG.
    """
    r = np.asarray(r, dtype=float)
    a = r * r
    sig_past = np.array([a[max(0, t - tau) : t].mean() if t > 0 else 0.0 for t in range(a.size)])
    sig_fut = np.array([a[t + 1 : t + 1 + tau].mean() if t + 1 < a.size else 0.0 for t in range(a.size)])

    def _corr(u: np.ndarray, v: np.ndarray) -> float:
        u = u - u.mean()
        v = v - v.mean()
        d = np.sqrt((u * u).sum() * (v * v).sum())
        return float((u * v).sum() / d) if d > 0 else 0.0

    return _corr(sig_past, a) - _corr(a, sig_fut)
