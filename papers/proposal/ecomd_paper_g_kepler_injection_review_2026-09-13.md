# Paper G: Kepler injection calibration, source and cost review

PRIVATE / INTERNAL. 2026-09-13. Bounded paper/metadata follow-up to Cycle37;
not a new search cycle or an experimental result. Previous goal turn: progress.

## Decision

**Park g37_kepler_injection_rank_transfer nonterminally.** The public validation
resource is more concrete than at F1, but neither a distinct calibration method
nor the claimed cheap-versus-expensive evaluation cost separation is qualified.
Empirical injection-stage sensitivity could still matter; it has not been tested
or disproved. No completed F2, F3, forecast, machine card or execution authority.

The decisive new allocation consideration is **current marginal cost**. Kepler
already supplies light curves after pixel injection and upstream processing.
For a new downstream detector, its inference is needed on both archived pixel-
derived curves and newly constructed flux-injected curves. We cannot count
the mission's historical pixel processing as a cost that our comparison must
incur again. A cost advantage may exist in a separately specified setting, but
has not been established for this one.

## Closest method parent

The single new retained primary work is Eyre and Madras,
[Regression for the Mean, ICML 2025](https://proceedings.mlr.press/v267/eyre25a.html).
We read the official paper's first four pages, including the binary mean target,
prediction-powered estimator, regression interpretation, ridge and sigmoid
corrections. It directly occupies the generic claim that a small gold panel can
correct many proxy labels, including learning the correction in the few-label
regime. Regularization or a nonlinear calibration map alone is therefore not a
new method here. The paper also separates fixed-coefficient reasoning from
estimating that coefficient on a small panel.

PPI, PPI++ and other papers surfaced during search intake; we did not conduct
separate full reviews of them. The retained work's discussion of those parents
is not substituted for an independent review. Original Cycle37 cap10 is now
consumed: nine previous works plus this one. The focused comparison uses four
direct works: this method paper, the FLTI report, Kepler recovery IV and the
DR25 catalog. This is not a completed six-work/full F2 audit.

## Four analytic controls

These are ordinary statistical applicability checks and a cost counterexample,
not new theorems, measurements or empirical failures of prior methods. Let Z
contain a star, injection parameters and the frozen observation/protocol state.
For a fixed detector m and threshold, Y_m is pixel-derived injection recovery
and L_m is flux-derived proxy recovery, both in {0,1}. Unless otherwise stated,
the following derivations assume independent identically distributed samples
from the same declared distribution Q, n paired observations and N additional
proxy observations. That sampling model is not automatically the fixed archive
or the full population of planets.

### 1. Correction and finite proxy-sample variance

For a fixed coefficient lambda, the standard estimator is

    mu_hat = mean(Y)_n + lambda [mean(L)_N - mean(L)_n].

Its expectation is mu_Y. With v_Y=Var(Y), v_L=Var(L)>0 and c=Cov(Y,L),

    Var(mu_hat) = v_Y/n + lambda^2 v_L(1/n + 1/N) - 2 lambda c/n.
    lambda_star = c / [v_L(1+n/N)].
    Var_min = (v_Y/n) [1 - rho^2 N/(n+N)].

For a constant proxy, its correction vanishes. The variance expressions require
fixed coefficients, or suitable conditioning on independent fitting data; they
cannot simply be reused after tuning lambda on the same labels. Flexible
calibrators also need separated fitting/evaluation or a justified cross-fitting
analysis. No finite-panel coverage guarantee is inferred from the existence of
the estimator.

### 2. Distribution mismatch is not removed by a mean correction

If paired data follow Q_H and the additional proxy data follow Q_L, the bias
relative to E_QH[Y] is

    lambda (E_QL[L] - E_QH[L]).

More cheap samples do not eliminate this term. Native strata and injected-
parameter distributions must match, or a justified support/weighting contract
must replace this derivation. In particular, a stratum with zero high-fidelity
sampling probability cannot be validated there by importance weighting. The
archive's M-dwarf injection-period restriction makes this a concrete support
check, not evidence that any existing published estimator failed.

### 3. Model selection requires joint error control

Suppose M detectors and their thresholds are frozen, and simultaneously
|mu_hat_m-mu_m| <= epsilon for every m. Choosing the largest estimated recovery
then gives regret at most 2 epsilon. Individual pointwise intervals do not imply
this simultaneous event after selecting the winner. For bounded Y,L, fixed
coefficients and the independent sampling model above, one conservative route
is a union bound over the two sample means for each of the M detectors. It is
standard concentration, not a new selection theorem. Threshold selection at a
false-alarm budget additionally needs its own untouched negative-control split.

### 4. Equal marginal cost removes the automatic efficiency story

Consider a legal counterexample budget model with v_Y>0: every new Y evaluation costs c_H,
every L evaluation costs c_L >= c_H, and sufficient independent high-fidelity
samples are available. The paired-plus-proxy estimator costs

    B = n c_H + (n+N)c_L.

Even its oracle coefficient satisfies Var_min >= v_Y/(n+N), since rho^2<=1.
At the same budget, direct Y sampling can afford at least 2n+N observations and
has variance at most v_Y/(2n+N). Thus this estimator cannot obtain an automatic
variance-per-cost advantage in that model, even with perfect correlation.

This is not a universal impossibility for multifidelity inference or a measured
Kepler timing result. Reusable free proxies, shared computation, a genuinely
cheaper surrogate, restricted high-fidelity sample supply, or another estimand
change the cost problem. They must be named and costed. For the actual archive,
charge download/staging, reconstruction and detector evaluation; treat already
released upstream products as available inputs. If new pixel injections outside
the archive are required, the truth and execution contract changes as well.

## Source qualification gained

The [official injection schema](https://exoplanetarchive.ipac.caltech.edu/docs/KSCI-19110-001.pdf)
documents KIC_ID, injected period/epoch/depth/duration and geometric parameters,
source-offset/group indicators, and distinct recovery/fitted-parameter columns.
Injected truth fields must be separated from recovery-derived fields. Its epoch
and depth conventions require explicit handling; a 25-column table alone is not
a pinned reconstruction of all cadence, aperture and photometric processing.
The documented injection distribution depends on stellar properties, with a
different period/radius design for the M-dwarf subset. This technical report is
the already-counted Kepler recovery work's earlier documentation, not a second
independent scientific lineage. We read methods/schema text, not result rows.

The [nominal time-series schema](https://exoplanetarchive.ipac.caltech.edu/docs/API_keplertimeseries_columns.html)
provides star identifiers, temporal coverage, file format and data-release
metadata. The [product overview](https://exoplanetarchive.ipac.caltech.edu/docs/Kepler_Data_Products_Overview.html)
separately documents nominal and injected light-curve products. These strengthen
the expected join design; they do not verify one-to-one actual file joins,
cadence masks, per-quarter dilution, rights or an untouched confirmation split.
No light curve, result table, model weight or archive-manifest payload was read.

## Allocation and retained value

The retained assets are a specific source-field map, target/support restrictions,
an information-matched comparator, and a current-cost counterexample. They
prevent a misleading proposal built from historical generation costs and a
generic mean correction. A substantive empirical benchmark remains possible in
principle, but its detector-family comparison, selection benefit and main-track
contribution are unresolved. No theorem is demanded as a substitute for useful
empirical evidence.

Resume only after a contribution-changing result or an economical, fully
specified comparison removes these blockers, with a new bounded allocation and
any required re-entry review. Do not spend another cycle merely moving the same
generic calibration-transfer proposal into a different domain. Before further
harvesting, compare the recent zero-card cycles by failure family and apply the
existing saturation/re-entry rule. This review itself authorizes no harvesting.

The broad scientific-ML publication objective remains active and incomplete.
