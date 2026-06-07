"""S8 — Jarzynski estimator power analysis (Paper B gate ③, pre-purchase, CPU-only).

B2 claims ⟨e^(−βW)⟩ = e^(−βΔF) with path-integral W and U_θ-derived ΔF agreeing within 15%.
The exponential average is dominated by rare negative-work events — the canonical finite-sample
bias of the Jarzynski estimator. Before committing $8–12k to high-frequency data, this script
answers: **at the realistic event budget (FOMC×3y ≈ 24, earnings ≈ 240), for which work-spread
regimes βσ_W can ΔF̂ = −(1/β)ln⟨e^(−βW)⟩ meet B2's own 15% criterion?**

Known analytic facts encoded here:
- Gaussian W ~ N(μ, σ²): ΔF = μ − βσ²/2 exactly (pipeline correctness check, S3 spirit).
- Any W with a polynomial LEFT tail (e.g. untruncated Student-t) has E[e^(−βW)] = ∞ — the
  Jarzynski average does not exist and no event count converges. Market work distributions are
  plausibly heavy-tailed ⇒ B2's pre-registration MUST include a left-tail diagnostic on W.
  We therefore test TRUNCATED Student-t (|W−μ| ≤ 10σ, physically: work bounded by event size)
  and a crash-like skewed Gaussian mixture; truth ΔF computed by quadrature.
- A GARCH(1,1)-t event-aggregate variant adds vol-clustering realism; its reference ΔF comes
  from two independent 10⁷-draw batches (disagreement ⇒ "non-convergent" verdict for that cell).

Usage: conda run -n ecophys python scripts/s8_jarzynski_power.py   (~2 min, pure numpy/scipy)
"""

from __future__ import annotations

import numpy as np
from scipy import integrate, stats

RNG = np.random.default_rng(42)
N_EVENTS = [24, 100, 240, 500, 1000, 5000]
BETA_SIGMA = [0.5, 1.0, 2.0, 4.0]
N_REPEATS = 2000
MU_OVER_SIGMA = 3.0      # W mean in σ units (keeps ΔF_true away from 0 across the β grid)
SIGMA = 1.0
CRITERION = 0.15         # B2's own 15% agreement criterion
T_TRUNC = 10.0           # truncation half-width (σ units) for the Student-t variants


def delta_f_true(logpdf, beta: float, lo: float, hi: float) -> float:
    """ΔF = −(1/β)·ln E[e^(−βW)] by quadrature on a finite support."""
    val, _ = integrate.quad(lambda w: np.exp(-beta * w + logpdf(w)), lo, hi, limit=400)
    return -np.log(val) / beta


def truncated_t_sampler(df: float, mu: float, sigma: float):
    """Student-t(df) location-scale truncated to |W−μ| ≤ T_TRUNC·σ, plus its logpdf + support."""
    lo, hi = mu - T_TRUNC * sigma, mu + T_TRUNC * sigma
    base = stats.t(df, loc=mu, scale=sigma)
    z = base.cdf(hi) - base.cdf(lo)

    def sample(size):
        out = np.empty(size)
        filled = 0
        while filled < size:
            draw = base.rvs(size=size - filled, random_state=RNG)
            keep = draw[(draw >= lo) & (draw <= hi)]
            out[filled:filled + len(keep)] = keep
            filled += len(keep)
        return out

    return sample, (lambda w: base.logpdf(w) - np.log(z)), lo, hi


def crash_mixture_sampler(mu: float, sigma: float):
    """0.9·N(μ,σ²) + 0.1·N(μ−3σ,(2σ)²) — a crash-like negative-work lump."""
    comp = [(0.9, mu, sigma), (0.1, mu - 3 * sigma, 2 * sigma)]
    lo, hi = mu - 3 * sigma - 8 * 2 * sigma, mu + 8 * sigma

    def sample(size):
        which = RNG.random(size) < 0.9
        a = RNG.normal(mu, sigma, size)
        b = RNG.normal(mu - 3 * sigma, 2 * sigma, size)
        return np.where(which, a, b)

    def logpdf(w):
        return np.log(sum(p * stats.norm.pdf(w, m, s) for p, m, s in comp))

    return sample, logpdf, lo, hi


def garch_event_sampler(mu: float, sigma: float, k: int = 26):
    """Event work = scaled sum of k consecutive GARCH(1,1)-t(df=5) returns (vol clustering).

    One long GARCH path is pre-simulated; events are random windows. Normalised to mean μ,
    std σ so the βσ_W grid applies. No closed-form ΔF — reference comes from 10⁷ draws ×2.
    """
    omega, alpha, beta_g, df = 0.05, 0.09, 0.89, 5.0
    n_path = 2_000_000
    h = np.empty(n_path)
    r = np.empty(n_path)
    h[0] = omega / (1 - alpha - beta_g)
    tdraw = RNG.standard_t(df, size=n_path) * np.sqrt((df - 2) / df)
    for i in range(1, n_path):
        h[i] = omega + alpha * r[i - 1] ** 2 + beta_g * h[i - 1]
        r[i] = np.sqrt(h[i]) * tdraw[i]
    cs = np.concatenate([[0.0], np.cumsum(r)])
    starts_max = n_path - k

    def raw(size):
        s = RNG.integers(0, starts_max, size)
        return cs[s + k] - cs[s]

    cal = raw(1_000_000)
    m0, s0 = cal.mean(), cal.std()

    def sample(size):
        return (raw(size) - m0) / s0 * sigma + mu

    return sample


def jz_hat(w: np.ndarray, beta: float) -> np.ndarray:
    """ΔF̂ per repeat: w shape (repeats, n_events). logsumexp for stability."""
    a = -beta * w
    amax = a.max(axis=1, keepdims=True)
    return -(amax[:, 0] + np.log(np.mean(np.exp(a - amax), axis=1))) / beta


def power_table(name: str, sample, df_true_fn) -> None:
    print(f"\n## {name} — hit-rate % of |ΔF̂−ΔF|/|ΔF| ≤ {CRITERION:.0%} (repeats={N_REPEATS})")
    hdr = f"{'n_events':>9} |" + "".join(f"  βσ={b:<4}" for b in BETA_SIGMA)
    print(hdr + "\n" + "-" * len(hdr))
    verdict_240 = []
    for n in N_EVENTS:
        cells = []
        for bs in BETA_SIGMA:
            beta = bs / SIGMA
            dft = df_true_fn(beta)
            if dft is None:
                cells.append("   n/a "); continue
            w = sample(N_REPEATS * n).reshape(N_REPEATS, n)
            est = jz_hat(w, beta)
            hit = float(np.mean(np.abs(est - dft) <= CRITERION * abs(dft)))
            bias = float(np.mean(est) - dft)
            cells.append(f"{100*hit:4.0f}({bias:+.2f})")
            if n == 240:
                verdict_240.append((bs, hit))
        print(f"{n:>9} |" + " ".join(f"{c:>9}" for c in cells))
    ok = [bs for bs, hit in verdict_240 if hit >= 0.8]
    print(f"   cell = hit%(mean bias in σ_W units)")
    print(f"   VERDICT n=240 (earnings budget): ≥80% power at βσ_W ∈ {ok or 'NONE'}")


def main() -> None:
    mu = MU_OVER_SIGMA * SIGMA
    print("# S8 — Jarzynski ⟨e^(−βW)⟩ estimator power analysis (B2 gate ③)")
    print(f"# W: mean={mu}, σ={SIGMA}; ΔF̂ = −(1/β)ln(mean e^(−βW)); criterion ±{CRITERION:.0%}")
    print("# NOTE: untruncated heavy LEFT tails (e.g. raw Student-t) ⇒ E[e^(−βW)] = ∞ —")
    print("#       Jarzynski formally divergent; B2 pre-registration needs a W left-tail check.")

    # (a) Gaussian + analytic pipeline check
    def g_true(beta):
        return mu - beta * SIGMA ** 2 / 2
    est_check = jz_hat(RNG.normal(mu, SIGMA, (200, 2_000_000)).reshape(200, -1), 1.0)
    rel = abs(est_check.mean() - g_true(1.0)) / abs(g_true(1.0))
    print(f"\npipeline check (Gaussian, β=1, n=2e6×200): ΔF̂={est_check.mean():.4f} "
          f"vs analytic {g_true(1.0):.4f} (rel err {rel:.2%}) → {'OK' if rel < 0.02 else 'FAIL'}")
    power_table("Gaussian", lambda size: RNG.normal(mu, SIGMA, size), g_true)

    # (b) truncated Student-t
    for df in (5.0, 3.0):
        samp, logpdf, lo, hi = truncated_t_sampler(df, mu, SIGMA)
        power_table(f"truncated Student-t df={df:g} (|W−μ|≤{T_TRUNC:g}σ)", samp,
                    lambda beta, lp=logpdf, lo=lo, hi=hi: delta_f_true(lp, beta, lo, hi))

    # (c) crash-like mixture
    samp, logpdf, lo, hi = crash_mixture_sampler(mu, SIGMA)
    power_table("crash mixture 0.9·N(μ,σ)+0.1·N(μ−3σ,2σ)", samp,
                lambda beta: delta_f_true(logpdf, beta, lo, hi))

    # (d) GARCH(1,1)-t event aggregates — reference ΔF from two independent 1e7 batches
    print("\n## GARCH(1,1)-t event-aggregate W (vol clustering realism)")
    samp = garch_event_sampler(mu, SIGMA)

    def garch_true(beta):
        refs = [jz_hat(samp(10_000_000).reshape(1, -1), beta)[0] for _ in range(2)]
        if abs(refs[0] - refs[1]) > 0.05 * max(abs(np.mean(refs)), 1e-9):
            print(f"   [βσ={beta * SIGMA:g}] reference ΔF unstable across 1e7-batches "
                  f"({refs[0]:.3f} vs {refs[1]:.3f}) → NON-CONVERGENT, cell n/a")
            return None
        return float(np.mean(refs))

    power_table("GARCH-t aggregates", samp, garch_true)

    print("\n# Interpretation: B2 is feasible only in cells with ≥80% power at the real event")
    print("# budget. If the empirical βσ_W (work spread per FOMC/earnings event, in units of")
    print("# the effective temperature) lands outside those cells, B2 must be redesigned")
    print("# (block-averaged protocols / Crooks-style bidirectional data) or dropped.")


if __name__ == "__main__":
    main()
