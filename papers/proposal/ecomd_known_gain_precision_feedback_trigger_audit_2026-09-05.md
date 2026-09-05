# EcoMD known-gain precision feedback trigger audit

**Date:** 2026-09-05  
**Archetype:** `measurement_method`  
**Decision:** `partial_capability`  
**Candidate harvesting:** not authorized  
**Experiment, outcome access, SSH, and GPU status:** not authorized

## 1. Exact question and early truth contract

The market-native object is a vector of full-period returns or displacements \(R_t\) observed
together with disclosed channel gains \(\gamma_t\), such as leverage-rebalancing capital divided by
venue liquidity. The question is whether these outputs identify a stable cross-channel feedback
matrix \(\Phi\), even when the clean pre-clearing output and clearing-window disturbance are not
observed.

Two explanations concern the same observable, gain path, and conditioning set:

- **H1 — stable feedback modulation:** a gain-invariant innovation distribution is transmitted
  through \((I-\Phi D_{\gamma_t})^{-1}\), so changes in conditional second moments encode one stable
  coupling matrix;
- **H2 — gain-tracking shocks or omitted state:** volatility, common information, liquidity, or the
  innovation covariance changes with the disclosed gains, and the same conditional output law can
  be generated with a different or zero feedback matrix.

The cheapest discriminating population result is not a regression of a post-window return on a
full-period return. It is the exact geometry of the conditional precision matrix. A positive result
would yield a new measurement only if the gain design has enough independent support and the
gain-invariant innovation restriction survives falsification and sensitivity analysis. A null result
is useful because it forces abstention rather than turning a gain-correlated volatility episode into
a structural feedback estimate.

The early truth contract is therefore:

1. prove population identification and its necessary design boundary;
2. give an observational-equivalence theorem when gain-conditioned innovations are allowed;
3. turn the overidentifying restrictions into a calibrated finite-sample abstention procedure;
4. obtain honest partial-identification or sensitivity sets under bounded innovation drift;
5. validate on at least two independent non-EcoMD systems with genuine coupling and gain truth;
6. use a market application only when its gain construction, timing, state, and negative controls
   support the same estimand.

This audit establishes only the first two population-level pieces and an algebraic lack-of-fit
restriction. It does not satisfy the remaining contract.

## 2. The post-closure source and its unresolved observation mismatch

[Woo (2026)](https://arxiv.org/abs/2608.25844) studies
\(L_t=\Phi\operatorname{diag}(\gamma_t)\) in the fixed-point model

\[
 r_{2,t}=\Phi D_t(r_{1,t}+r_{2,t})+v_t,
 \qquad
 r_{\mathrm{on},t}=-\theta r_{2,t}+Cr_{1,t}+w_t,
\]

where \(D_t=\operatorname{diag}(\gamma_t)\). Its clean theorem needs the pre-window output \(r_1\),
gain-independent disturbances, a gain-invariant confound \(C\), a known or externally calibrated
reversal share \(\theta\), and persistent excitation. The conditional clean regression coefficient
is

\[
 B(\gamma)=C-\theta\{(I-\Phi D_\gamma)^{-1}-I\}.
\]

The paper correctly derives that replacing \(r_1\) with the full-period regressor
\(R=r_1+r_2\) contaminates this regression. Even with zero clearing-window noise, it becomes
\((C-\theta M)(I+M)^{-1}\), so the constant confound acquires gain dependence. The Korean example
has no historical pre-launch intraday bars and consequently uses close-to-close full-period returns;
the paper calls this a convention-dependent screening exercise rather than a transfer of its clean
identification theorem.

That regression failure does not by itself imply that \(\Phi\) is unidentified from full-period
outputs. Under the paper's own gain-exogeneity and invariant-second-moment restriction, a different
observable moment contains more structure.

## 3. Exact known-gain precision factorization

Let

\[
 R_t=(I-\Phi D_t)^{-1}\varepsilon_t,
 \qquad
 \mathbb E[\varepsilon_t\mid\gamma_t]=0,
 \qquad
 \operatorname{Cov}(\varepsilon_t\mid\gamma_t)=\Sigma\succ0,
\]

and assume \(I-\Phi D_t\) is invertible on the gain support. Gaussianity is unnecessary for the
second-moment statement. With \(K=\Sigma^{-1}\), the conditional precision is exactly

\[
 \Omega(\gamma)
 =\operatorname{Cov}(R\mid\gamma)^{-1}
 =(I-D_\gamma\Phi^\top)K(I-\Phi D_\gamma).
\]

Define \(H=K\Phi\) and \(J=\Phi^\top K\Phi=H^\top K^{-1}H\). Then

\[
 \Omega(\gamma)=K-D_\gamma H^\top-HD_\gamma+D_\gamma JD_\gamma,
\]

and entrywise

\[
 \Omega_{ij}(\gamma)
 =K_{ij}-\gamma_iH_{ji}-\gamma_jH_{ij}
  +\gamma_i\gamma_jJ_{ij},
\]

with

\[
 \Omega_{ii}(\gamma)=K_{ii}-2\gamma_iH_{ii}+\gamma_i^2J_{ii}.
\]

This gives a simple sufficient identification theorem. If, for every \(i\ne j\), the functions
\(1,\gamma_i,\gamma_j,\gamma_i\gamma_j\) are linearly independent on the observed support, and
\(1,\gamma_i,\gamma_i^2\) are linearly independent for every diagonal entry, then the population
coefficient functions uniquely determine \(K\), \(H\), and hence

\[
 \Phi=K^{-1}H.
\]

Equivalently, when a zero-gain baseline and independent coordinate perturbations are available,
\(K=\Omega(0)\) and

\[
 \left.\frac{\partial\Omega}{\partial\gamma_j}\right|_0
 =-E_jH^\top-HE_j.
\]

Its off-diagonal entries in column \(j\) recover \(-H_{ij}\), and its \((j,j)\) entry recovers
\(-2H_{jj}\). Unlike the reversal regression, this population result uses neither a post-window
observation nor \(\theta\).

The factorization is overidentified. An unrestricted entrywise quadratic fit must have no dependence
on irrelevant gains, and its quadratic coefficient matrix must satisfy

\[
 J=H^\top K^{-1}H.
\]

Violating either restriction rejects the joint fixed-point/invariant-innovation model. Passing them
does not prove that the restriction is causal or that innovation invariance is true.

## 4. Gain support is a hard identification condition

Time variation alone is insufficient. Suppose all channel gains co-trend as
\(\gamma_t=s_t\mathbf 1\), take \(K=I\), and let \(A^\top=-A\) be any nonzero skew-symmetric
matrix. The two feedback matrices

\[
 \Phi_+=A,
 \qquad
 \Phi_-=-A
\]

generate exactly the same conditional precision path:

\[
 (I-s\Phi_+)^\top(I-s\Phi_+)
 =I-s^2A^2
 =(I-s\Phi_-)^\top(I-s\Phi_-).
\]

For a two-channel example, choose

\[
 A=\begin{pmatrix}0&a\\-a&0\end{pmatrix}
\]

and restrict \(|s a|<1\). The models have opposite directed coefficients, zero self-loops, stable
loop gains, invariant innovations, and identical conditional distributions when the innovations are
Gaussian. Thus dense observations along one scalar gain path need not identify orientation.

More generally, for \(\gamma=s d\) with nonzero entries of \(d\), take
\(\Phi_\pm=\pm A D_d^{-1}\). This is the mechanism-modulation analogue of the intervention-ratio
condition in BackShift: independent relative movement, not merely many dates, supplies rank.

The real Korean application in Woo has only two treated complexes, strongly trending gains, and a
short post-launch window. The paper does not establish the pairwise polynomial design rank above.
No outcome reanalysis was performed in this audit.

## 5. Sharp nonidentification under gain-conditioned shocks

The invariant innovation covariance is not a convenience; it is the identifying exclusion. Let the
observed conditional covariance be \(V(\gamma)\succ0\). For any candidate feedback matrix \(\Psi\)
such that \(I-\Psi D_\gamma\) is invertible, define

\[
 \Sigma_\varepsilon^{\Psi}(\gamma)
 =(I-\Psi D_\gamma)V(\gamma)(I-D_\gamma\Psi^\top).
\]

This matrix is positive definite and the model

\[
 R=(I-\Psi D_\gamma)^{-1}\varepsilon^\Psi,
 \qquad
 \operatorname{Cov}(\varepsilon^\Psi\mid\gamma)
 =\Sigma_\varepsilon^{\Psi}(\gamma)
\]

reproduces \(V(\gamma)\) exactly. For conditional Gaussian laws the entire observed law is the same;
for general laws, define \(\varepsilon^\Psi=(I-\Psi D_\gamma)R\) to obtain the same result by
pushforward. Therefore \(\Phi\) is completely nonidentified if innovation laws may track gains
arbitrarily.

A defensible robustness target is an identified set, not a falsely robust point estimate. Given a
declared metric \(d\) and drift budget \(\delta\), define

\[
 \mathcal I_\delta
 =\left\{\Psi:
   d\!\left(\Sigma_\varepsilon^\Psi(\gamma),\Sigma_0\right)
   \le\delta\ \text{on the gain support for some }\Sigma_0\succ0
 \right\}.
\]

This set is sharp relative to the stated covariance-drift class: every included \(\Psi\) has a
constructive observationally equivalent innovation process. The present audit does not establish a
useful diameter bound, estimator, or uniform confidence set for \(\mathcal I_\delta\).

## 6. Direct-parent collision map

The exact coefficient recovery above appears to be a narrower residual, but its scientific engine is
heavily occupied.

| Proposed component | Nearest primary parent | Collision or residual |
|---|---|---|
| Recover a cyclic linear network from environment second moments | [BackShift](https://proceedings.neurips.cc/paper/2015/hash/92262bf907af914b95a0fc33c3f33bf6-Abstract.html) | BackShift already identifies a full cyclic matrix by jointly diagonalizing covariance differences under invariant coupling/noise and relatively varying diagonal shift variances. The modulation is on shocks rather than known structural columns. |
| Infer direction from covariance changes caused by connection-strength modulation | [INDUCE](https://doi.org/10.1371/journal.pone.0125777) | This is the closest conceptual collision. INDUCE derives covariance trajectories under perturbed connectivity and explicitly treats stimulus-dependent noise as the failure mode. It is qualitative, small-motif, continuous-time Langevin analysis and does not give the known-gain full-matrix factorization. |
| Use known activity interventions in cyclic equilibrium models | [Mooij and Heskes](https://arxiv.org/abs/1309.6849) | Already models interventions that change outgoing causal activity across conditions; cyclic parameters can remain nonidentified. Its changes are condition-specific and regularized rather than a known multiplicative gain law. |
| Recover cyclic direct effects from intervention experiments | [Eberhardt, Hoyer, and Scheines](https://proceedings.mlr.press/v9/eberhardt10a.html) | Supplies necessary/sufficient experiment conditions and total-to-direct-effect recovery for cyclic models with latent variables, but uses measured surgical/soft intervention effects rather than output-only gain-conditioned covariance. |
| Exploit environment covariance changes under hidden confounding | [Causal Dantzig](https://doi.org/10.1214/18-AOS1732) | Already gives identification conditions, confidence intervals, high-dimensional bounds, and predictive sets under nonidentification for additive shifts. It targets a response equation, not known column modulation of an entire cyclic matrix. |
| Learn changes in linear causal graphs from precision/regression invariance | [DCI](https://proceedings.neurips.cc/paper_files/paper/2018/hash/e1314fc026da60d837353d20aefaf054-Abstract.html) | Occupies precision-change and regression-invariance machinery for two DAGs with a shared order; it is not a cyclic full-network recovery theorem. |
| Edge intervention covariance algebra | [Yao and Evans](https://arxiv.org/abs/2205.13432) | Gives covariance effects and identification conditions for adding/removing edges in linear SEMs; assumes acyclic graphical structure and usually identifiable baseline coefficients. |
| Known scheduling and closed-loop parameter variation | [Cox and Tóth](https://doi.org/10.1016/j.automatica.2020.109296) | LPV subspace identification is a mature parent with known schedules, likelihood/realization estimators, and open/closed-loop data equations, normally with measured inputs. |
| Blind identification using known modulation and output second-order statistics | [Serpedin and Giannakis](https://doi.org/10.1109/78.700965) | Already proves necessary/sufficient blind-channel identification from modulation-induced cyclic second-order statistics. It is feedforward FIR rather than an algebraic feedback fixed point. |
| Simultaneous-equation identification from covariance regimes | [Rigobon](https://doi.org/10.1162/003465303772815727) | Establishes the econometric covariance-regime parent; weak identification and maintained shock restrictions are mature concerns. |
| Full graph recovery from a few environments | [Montagna, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/171ffe2c4231b96db4d203ffdce49cde-Abstract-Conference.html) | Occupies the broad multi-environment identification headline for arbitrary nonlinear acyclic SCMs with changing Gaussian noise statistics. |
| Context-dependent structure and edge-local interventions | [Orujlu et al., UAI 2026](https://proceedings.mlr.press/v337/orujlu26a.html) | Gives positive and negative identification results under partially observed context and edge mechanisms, but explicitly retains acyclic ordered generation and leaves cyclic semantics open. |

Consequently, “use varying gains,” “use covariance/precision changes,” “identify a cyclic network
from environments,” “add an abstention test,” or “apply the method to finance” is not an adequate
novelty sentence. The unoccupied-looking residue is the exact known-column-gain precision
factorization together with sharp support and innovation-drift boundaries. That algebra is too small
by itself for an ICLR paper.

## 7. What a genuinely non-incremental method paper would still need

A credible ICLR formulation would have to contribute a package whose hard part is not already in
the parent literature:

1. necessary and sufficient identification conditions for arbitrary continuous or discrete gain
   support, not only the sufficient entrywise polynomial rank condition;
2. a minimax lower bound showing how error diverges near the co-trending ambiguity and an estimator
   attaining the rate under temporal dependence and one observation per continuous gain vector;
3. a finite-sample, multiplicity-controlled test of the zero irrelevant-gain coefficients and
   \(J=H^\top K^{-1}H\), with calibrated abstention under weak gain excitation;
4. sharp, computationally tractable partial-identification and confidence sets under a declared
   amount of gain-conditioned covariance drift;
5. comparisons against BackShift, Causal Dantzig, conditional precision estimation, LPV likelihood,
   and the clean/reversal estimator under equal information and compute;
6. two independently governed physical, biological, or engineered systems where the gain schedule,
   coupling truth, and innovations are externally controlled rather than produced by the fitted
   simulator.

EcoMD could later be one adversarial synthetic benchmark, especially for misspecification and
partial observation, but it cannot be the truth source that validates a claim about real market
feedback. Fitting and inverting the same EcoMD mechanism would be an inverse crime.

## 8. Market bridge audit

The leveraged-fund setting does supply a meaningful, disclosed gain formula, and the Woo papers are
a genuine post-closure source change. It does not currently supply the needed identification
contract:

- \(\gamma=K/\mathrm{ADV}\) contains lagged NAV/assets and liquidity, both of which co-move with
  volatility, attention, and time;
- products launch together, so channel gains can be nearly one-dimensional rather than independently
  excited;
- full-period daily outputs merge pre-window news, intraday discovery, the closing feedback window,
  and post-close correction;
- the Korean sample reported in the source has roughly two months after launch and no clean
  pre-launch intraday observation for the treated products;
- the source reports a strong treated pre-period loading and one opposite-signed unexplained cell;
- U.S. examples in the same paper are null after multiplicity, and no independent market implements
  the same gain, clearing, observation, and intervention grammar with known \(\Phi\).

These facts make H2 scientifically live. A polynomial residual can reject H1, but passing it on one
short episode cannot establish invariant innovations or causal feedback. No historical returns,
fund files, or stored outcomes were opened in this audit.

## 9. Gate decision

| Gate | Result |
|---|---|
| Genuine post-closure source change | Pass: the output-only and loop-gain papers appeared in August 2026 |
| Exact theorem-shaped residual | Partial pass: the full-period precision factorization recovers \(\Phi\) under invariant innovations and sufficient gain support |
| Hard identification boundary | Pass: co-trending gains and gain-conditioned innovations yield explicit observational equivalences |
| Irreducible novelty beyond direct parents | Fail: covariance modulation, cyclic multi-environment recovery, intervention algebra, LPV scheduling, and blind second-order identification are established parents; the remaining identity is too small alone |
| Finite-sample truth contract | Fail: no rate-optimal estimator, calibrated residual test, confidence set, or bounded-drift guarantee exists here |
| Market design rank and exclusion | Fail: independent gain support and innovation invariance are not established |
| Two independent same-estimand truth systems | Fail |
| Recorded same-target blocker removed | Fail: this does not solve the global-drift, field-assignment, funding-controller, or cross-impact targets of the linked closed routes |
| Prospectively frozen full-T0 forecast | Fail: the exact subject and forecast were not frozen before this neighborhood expanded; no retrospective number may enter calibration history |

**Decision:** `partial_capability`, with `removed_blockers: []` and
`candidate_harvest_authorized: false`. The factorization and counterexamples are reusable theory
assets, not a topic card or experiment authorization. No route node, data pull, model implementation,
EcoMD integration, SSH connection, or GPU job is created.

## 10. Exact re-entry boundary

Re-audit a narrowly frozen child only after one of the following is available before further
candidate harvesting:

1. a theorem/algorithm package gives necessary-and-sufficient arbitrary-support identification,
   minimax weak-design behavior, uniformly calibrated model checking, and sharp tractable confidence
   sets under bounded gain-conditioned innovation drift beyond BackShift, INDUCE, Causal Dantzig,
   LPV, and modulation-induced blind identification; or
2. a lawful controlled system exposes independently varied known channel gains, complete outputs,
   coupling truth, and an untouched independent replication, thereby turning the algebra into a
   falsifiable cross-system measurement contribution.

Any child must freeze its exact subject node and full-T0 forecast before opening a fresh full
primary-work neighborhood. A market application additionally needs a gain-exogeneity or negative-
control design strong enough to separate mechanical feedback from gain-tracking volatility and
liquidity. Until then all three authorized compute workers remain idle for EcoMD discovery.
