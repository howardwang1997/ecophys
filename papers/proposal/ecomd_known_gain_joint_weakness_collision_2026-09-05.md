# EcoMD known-gain joint-weakness collision audit

**Date:** 2026-09-05  
**Archetype:** `measurement_method`  
**Decision:** `not_trigger`  
**Candidate harvesting:** not authorized  
**Experiment, outcome access, implementation, SSH, and GPU status:** not authorized

## 1. Frozen question

After the gain--reciprocity correction, the only plausible theoretical extension was a joint phase
diagram in which three sources of orientation information vanish together:

1. the known-gain covariance contrast \(\xi_n\);
2. the reciprocal spectral gap; and
3. the non-Gaussianity of the innovations.

The positive hypothesis was that the known column-gain algebra creates a new, additive information
geometry and a new uniform estimator. The hostile alternative was that the problem is just the
combination of a known covariance weak-design boundary and already studied weak ICA/SVAR theory.
The latter is currently the better-supported conclusion.

## 2. Boundary matching

In the exact pure-circulation submodel, common gains and an isotropic reciprocal background make the
Gaussian covariance law for \(a\) and \(-a\) identical. The preceding audit showed that a gain
contrast contributes a signed score of size \(a\xi_n\), while the quadratic magnitude signal is of
size \(a^2\). This yields the covariance-only divergence order

\[
 n(a^2\xi_n^2+a^4).
\]

Now let the independent innovations be a near-Gaussian triangular array with contamination scale
\(\beta_n\). In the common-gain pure-skew submodel, the Gaussian component is still exactly
rotation-invariant; only the contaminated component can distinguish the two signs. The resulting
weak-non-Gaussian problem therefore contains the same local experiment as near-Gaussian ICA, with
effective non-Gaussian score controlled by \(\beta_n\). A putative joint theory must at least recover
both boundary faces:

- \(\beta_n=0\): the EcoMD covariance boundary \(n(a^2\xi_n^2+a^4)\);
- \(\xi_n=0\): the established near-Gaussian ICA/SVAR boundary, where non-Gaussian separation
  disappears at the inverse-square-root scale.

The tempting expression \(n a^2(\xi_n^2+\beta_n^2)+n a^4\) is not a theorem. It requires a
specified source family, orthogonality of covariance and higher-cumulant scores, and a nuisance
projection over unknown source laws. Without those conditions a least-favourable innovation family
can make the two information channels non-additive. Writing down this sum would therefore be an
assumption, not a result.

## 3. Primary-work collision

- [Sokol, Maathuis and Falkeborg (Electronic Journal of Statistics, 2014)](https://doi.org/10.1214/14-EJS932)
  studies ICA distributions converging to Gaussianity and shows that contamination at or below the
  \(n^{-1/2}\) scale leaves only transpose-product identification asymptotically. This is already a
  local weak-identification phase boundary for the non-Gaussian component.
- [Hoesch (Quantitative Economics, 2024)](https://doi.org/10.3982/QE2274) develops locally robust
  semiparametric score inference for weakly or nonidentified non-Gaussian SVARs, with nuisance-score
  projection and coverage control. A generic “robust confidence set through weak non-Gaussianity”
  is therefore occupied.
- [Junare (2026)](https://arxiv.org/abs/2607.17275) gives a bootstrap diagnostic for extra Gaussian
  shocks, proves validity at the singular single-Gaussian boundary, localizes partial failures, and
  evaluates coverage under near-Gaussian weak identification.
- [Guay and Stevanovic (2026)](https://cirano.qc.ca/files/publications/2026s-02.pdf) quantify
  non-Gaussian identification by tensor singular-value gaps and derive nonstandard local-to-weak
  limits for SVAR inference.
- [Recke and Hansen (2026)](https://arxiv.org/abs/2603.17142) and [Recke et al. (2026)](https://arxiv.org/abs/2601.21818)
  already provide higher-cumulant identification and estimation for continuous and discrete
  Lyapunov models.

These papers do not contain the exact EcoMD gain--reciprocity formula. They do, however, occupy every
generic ingredient needed to turn that formula into the proposed joint phase-diagram method. The
remaining difference is a composition of model-specific scores, not yet an irreducible algorithmic
or scientific contribution.

## 4. Hostile decision

The joint-weakness idea is `not_trigger` for four reasons:

1. **No proved new experiment:** the additive information law is only a conjectural combination of
   two existing local experiments.
2. **No new inference primitive:** efficient-score projection, bootstrap validity, partial
   identification and local nonstandard limits already exist in the SVAR/ICA parents.
3. **No stable market estimand:** the innovation law, reciprocal background and gain assignment are
   not externally controlled in market data; arbitrary gain-conditioned shocks restore complete
   observational equivalence.
4. **No truth asset:** EcoMD's current conservative architecture has no signed circulatory ground
   truth, and the audited physical systems do not implement the same gain action.

The correct reusable result is negative: do not add a “non-Gaussian repair” or a gain-only
condition-number optimizer and call it new. No candidate, machine card or GPU authorization is
opened.

## 5. Re-entry condition

Re-enter only if a new primary disagreement or theorem proves a genuinely non-additive joint local
experiment, supplies a nuisance-efficient estimator with uniform coverage, and separates it from
weak ICA, weak SVAR, Lyapunov cumulant estimation, graphical regression and weak-GMM theory. It must
also come with two same-estimand controlled truth systems before any EcoMD or market experiment is
considered.
