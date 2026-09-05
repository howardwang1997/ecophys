# EcoMD price-clock refinement and nonlinear-impact re-entry audit

**Date:** 2026-09-05 NZST. **Literature cutoff:** 2026-09-05 02:22 NZST.
**Mode:** outcome-blind blocker-specific re-entry audit; this is not a new Discovery cycle.

## 1. Decision

No executable ICLR topic is activated.

The audit found a real claim-scope and implementation issue, but not an irreducible research method:

1. If every Langevin integrator step of width `h` is also treated as a price-observation step while
   `beta`, `sigma_price` and the concave-impact parameters are held fixed, the price path has no
   tight fixed-physical-horizon refinement limit. Fixed per-step price noise already makes its
   variance grow as `1/h`; with price noise removed, a memoryless signed-power impact with exponent
   `delta < 1` makes the variance grow as `h^(delta-1)`.
2. The implemented numerical offset in the signed-power map makes the map discontinuous at zero.
   This is a source-level QA defect, although this audit does not establish that any historical
   trajectory entered the offset-dominated regime.
3. EcoMD already exposes a legitimate two-clock construction: reduce `dt`, increase
   `inner_steps_per_price` so their product remains the fixed market-clearing bucket, and call the
   price head once on the aggregate displacement. The fixed `sigma_price` is then a per-bucket
   parameter. The missing item is a frozen convergence test and unit contract, not a new model.
4. Exact aggregation consistency for a continuous memoryless impact map forces linear impact by
   the Cauchy functional equation. Nonlinear impact across scales needs state, history or an
   explicitly fixed aggregation clock. Neural differential-equation models and stateful latent
   order-book impact theories already supply the obvious constructions.

The result is therefore `not_trigger`. It is useful simulator QA and prevents an invalid physical
continuum claim. It does not rescue the failed stationary cube-law route and does not justify an
ICLR submission, EcoMD modification, outcome access, SSH or GPU work.

## 2. Frozen question contract

**Archetype:** `simulator_method`.

**Market-native object.** The distribution of a log-price change over a fixed market observation
interval `Delta`, when the latent agent integrator is refined while continuous agent dynamics,
market-clearing times and price units are held fixed.

**Rival explanations.** (A) EcoMD's nonlinear impact and return law describe one physical process
whose fixed-`Delta` distribution is invariant to the latent solver step. (B) the apparent law is a
property of one discrete transition kernel because the solver clock, clearing clock and price-noise
units have been conflated.

**Discriminating result.** A lawful refinement varies the latent step `h` while holding `Delta`, the
market-clearing schedule and per-`Delta` price parameters fixed. It must compare the same path
functional after aggregation. A positive result would certify numerical semantics; a null result
would restrict EcoMD to an explicitly discrete clock. Neither answer is a paper contribution
without a new theorem or algorithm beyond standard weak convergence, power variation, continuous-
time neural models and simulator semigroup diagnostics.

## 3. Exact zero-force witness

Take the valid EcoMD subsystem with no deterministic force, no memory, no jump and independent
Gaussian Langevin innovations. For the first agent coordinate,

\[
  \Delta s_{i,k}=\sqrt{2Th/\gamma}\,\epsilon_{i,k}.
\]

With `N` agents, the excess demand entering the price head is

\[
  E_{h,k}=\kappa\sum_{i=1}^N\Delta s_{i,k}
         =a\sqrt{h}\,Z_k,
  \qquad a=\kappa\sqrt{2TN/\gamma},
\]

where `Z_k` are iid standard normal. The implemented price core reduces to

\[
  R_{h,k}=\beta\phi_{\delta,e}(E_{h,k})-	frac12\sigma^2+\sigma\eta_k,
\]

where

\[
  \phi_{\delta,e}(x)=\operatorname{sign}(x)s
     \left(\frac{|x|}{s}+e\right)^\delta,
  \qquad e=10^{-8}.
\]

For a fixed physical horizon `H`, let `m=floor(H/h)` price steps occur.

### 3.1 Fixed per-step price noise

For every fixed `sigma > 0`, symmetry makes the impact contribution mean zero and

\[
  \mathbb E\!\left[\sum_{k=1}^{m}R_{h,k}\right]
    =-\frac{m\sigma^2}{2}\to-\infty,
  \qquad
  \operatorname{Var}\!\left(\sum_{k=1}^{m}R_{h,k}\right)
    \ge m\sigma^2\to\infty.
\]

Thus the fixed-parameter price process is not tight under the interpretation "one price update per
shrinking physical step." The usual continuous-time scaling would instead use a diffusion
coefficient `sigma_bar`, per-step noise `sigma_bar*sqrt(h)`, and drift
`-sigma_bar^2*h/2`.

### 3.2 Offset-dominated signed power

Set `sigma=0`. Because `Z_k` is almost surely nonzero,

\[
  \phi_{\delta,e}(a\sqrt h Z_k)
    \xrightarrow[h\downarrow0]{a.s.}
    s e^\delta\operatorname{sign}(Z_k).
\]

The one-step variance tends to the positive constant `s^2 e^(2 delta)`, so the fixed-horizon
variance again grows as `1/h`. This follows from the source expression itself: at `x=0` the map is
zero, but its right and left limits are `+s e^delta` and `-s e^delta`. The offset prevents a zero
gradient singularity by creating a jump discontinuity.

### 3.3 Ideal homogeneous signed power

Even after replacing the offset map by the continuous homogeneous map

\[
  \phi_{\delta,0}(x)=s^{1-\delta}\operatorname{sign}(x)|x|^\delta,
\]

the accumulated variance is

\[
  m\beta^2s^{2(1-\delta)}a^{2\delta}h^\delta
    \mathbb E|Z|^{2\delta}
  \asymp Hh^{\delta-1}.
\]

It diverges for every concave exponent `0 < delta < 1`. Scaling
`beta_h = beta_bar*h^((1-delta)/2)` restores order-`h` one-step variance, but the iid triangular
array then has a Gaussian fixed-horizon limit under ordinary Lindeberg conditions. The signed-power
one-step shape does not supply a persistent heavy-tail continuum mechanism.

This is a special case of established realized-power-variation asymptotics, not a new limit theorem.

## 4. Exact aggregation obstruction

Suppose a memoryless price map `psi` is required to commute exactly with splitting any bucket flow
`q=q_1+q_2`:

\[
  \psi(q_1+q_2)=\psi(q_1)+\psi(q_2)
  \quad\text{for all }q_1,q_2.
\]

Any continuous, measurable, or locally bounded solution is `psi(q)=c q`. Therefore no continuous
memoryless square-root map can simultaneously be the exact fine-step and coarse-bucket impact law.
This elementary Cauchy-equation result does not forbid nonlinear market impact. It says that
nonlinearity must be attached to a declared execution horizon, or realized through a stateful
liquidity/history model whose state composes across substeps.

The market literature already makes that distinction. Donier et al. obtain nonlinear impact from a
dynamic latent order book, and Sato and Kanazawa obtain diffusive prices by combining persistent
metaorder flow with nonlinear impact. Applying a square-root map independently to Brownian-scale
agent displacements is not the same object as either model.

## 5. The repository already contains the lawful refinement axis

The code separates the clocks sufficiently for a future QA check:

- `LangevinIntegrator.step` scales agent noise by `sqrt(dt)`;
- `EcoMDSimulator` performs `inner_steps_per_price` latent steps while the slow price state is
  frozen, then calls `price_formation.step` once using the total outer displacement;
- `ExcessDemandPrice.step` applies impact and `sigma_price` only at that outer price step.

A legitimate solver-refinement sequence therefore fixes a clearing interval `Delta`, uses
`dt=Delta/m` and `inner_steps_per_price=m`, freezes the same slow-state splitting convention, and
holds the per-clearing price parameters fixed. That sequence tests ordinary numerical convergence
of the declared hybrid process. Changing `dt` while leaving `inner_steps_per_price=1` changes the
market-clearing clock and is a different model.

Historical concave-impact configurations inspected here use one fixed `dt=0.01`; they do not claim
or test a refinement sequence. This audit therefore narrows the allowable interpretation but does
not retrospectively assign their observed statistics to the discontinuity or prove a corrected
configuration would pass any market target.

## 6. Novelty collision

The obvious paper formulations are occupied:

- Jacod's semimartingale power-variation theory already characterizes normalized sums of nonlinear
  functions of fine increments.
- Neural SDEs define flexible generative models directly on path space; Neural RDEs/CDEs provide a
  stateful continuous-time response to an input path; stochastic-process diffusion models generate
  continuous functions under irregular observation. Replacing the current price head by one of
  these is an application, not a new architecture.
- Zhu et al. already show that numerical integration can determine the learned modified equation
  rather than the intended continuous dynamics.
- Shikhman already proposes semigroup consistency as a model-agnostic learned-simulator diagnostic
  and reports mixed value for semigroup regularization.
- Dynamic latent-order-book and persistent-order-flow theories already produce stateful nonlinear
  impact with diffusive prices. A market-specific restatement of the aggregation obstruction has no
  independent mechanism theorem.

An ICLR contribution would need more than a clock-aware test suite or a continuous-time head. No
new estimator, architecture, generalization bound, impossibility boundary beyond the elementary
additivity result, or two-system validation contract was constructed. Diagnostic ICLR survival is
`1--3%`; this is a retrospective audit label, not a preregistered forecast.

## 7. Compute decision

No experiment plan is authorized because the route failed before implementation:

- no simulator, stored outcome or benchmark result was executed or opened;
- no source, loss, test or experiment configuration was changed;
- no SSH session was opened to `100.113.230.38`, `100.80.236.112` or `100.123.220.57`;
- the A800 and both V100 workers received zero jobs.

The two reusable QA checks are a zero-continuity unit test for every nonlinear impact map and a
joint `(dt, inner_steps_per_price)` convergence test at fixed clearing interval. They require a
separate implementation decision; they are not an experiment plan or paper activation.

## 8. Re-entry condition

Re-audit only if all of the following are written before candidate harvesting:

1. a stateful resolution-equivariant impact operator with a non-vacuous theorem strictly beyond
   CDE/RDE path modeling, standard weak/power-variation limits and semigroup-error diagnostics;
2. a market-native prediction invariant under a jointly frozen solver step, clearing clock,
   aggregation rule and price-unit transformation, not a desired exponent inserted by scaling a
   parameter;
3. analytic or gold-standard truth on two independently maintained non-EcoMD dynamic systems and a
   legal untouched market confirmation partition; and
4. a new current machine decision authorizing implementation and compute.

Until then, do not vary `dt` alone and call the result physical robustness, do not apply a concave
impact independently at every refined solver substep and compare it with fixed-bucket impact, and do
not present a continuous odd smoothing patch as an ICLR method.
