# Formal cards v6 — exact fee-controller reductions

These cards preserve exact algebra and scope controls. None is currently claimed as a new theorem.

## F1 — continuous scale equivariance

Consider the continuous relaxation of the blob controller away from reflection and the EIP-7918 reserve branch,

\[
e_{t+1}=e_t+G(n_t-T),\qquad b_t=b_{\min}\exp(e_t/F).
\]

Scale target, maximum, observed blob count, excess and update fraction by the same positive factor `lambda`:

\[
(T,M,n_t,e_t,F)\mapsto
(\lambda T,\lambda M,\lambda n_t,\lambda e_t,\lambda F).
\]

Then `e'_t/F'=e_t/F` by induction and hence `b'_t=b_t`. The normalized load and fee path are invariant.

**Proof.** If `e'_t=lambda e_t`, then

\[
e'_{t+1}=\lambda e_t+G(\lambda n_t-\lambda T)=\lambda e_{t+1}.
\]

The initial condition closes the induction, and division by `F'=lambda F` gives the fee identity.

**Protocol-scale audit.** Prague/Osaka, BPO1 and BPO2 all have `M/T=1.5`. Their `F/T` values are
`834619.333333`, `834619.300000` and `834619.357143`, differing relatively by at most `3.99384e-8` from the first
schedule. At standardized integer excess states `e=G*T*s`, the exact fee is identical on the quarter grid through
`s=64`; the first integer-grid difference through `s=2000` is only at `s=74`, and the maximum relative spread is
`2.15e-5`.

**Scope.** Ethereum is integer-valued. `fake_exponential` floors intermediate terms; BPO scaling factors are
rational; blob counts have finite support; reflection, maximum utilization, the reserve branch and inherited state
break exact equivariance. The numerical protocol audit makes scale equivariance a mandatory baseline, not an
empirical law or novelty result.

## F2 — inherited-state fork defect

Let a fork change `F` to `F'=lambda F` while carrying the old excess `e` unchanged. Compare the ideal log-fee
coordinate under protocol carryover with the scale-equivariant counterfactual that also maps `e` to `lambda e`:

\[
\frac{e}{F'}-\frac{\lambda e}{F'}
=-\frac{(\lambda-1)e}{\lambda F}.
\]

Thus the first post-fork fee contains a deterministic state-carryover displacement even with identical behavior.
Any measured fork response must subtract the bit-exact protocol transition before it is labeled demand adaptation.

**Scope.** The formula uses the ideal exponential coordinate. Experiment 149 validates the actual integer
transition. This is a mechanical diagnostic directly implied by state carryover, not a new theorem.

## F3 — reserve-branch one-sided accumulation

Suppose EIP-7918's lower-bound check is false and its reserve inequality remains active over blocks `t,...,t+k-1`.
Let `alpha=(M-T)/M`. Ignoring only integer-floor notation for display,

\[
e_{t+k}=e_t+\alpha\sum_{j=0}^{k-1}u_{t+j}.
\]

With exact arithmetic, replace each increment by `u_j(M-T)//M`. Every increment is nonnegative, so the excess
state cannot decrease while this branch remains active. When the branch turns off, the ordinary target-subtraction
recurrence resumes.

**Consequence.** Execution base fee mechanically selects the blob-state update law. A cross-resource lag or
hysteresis can therefore arise inside the protocol even under a fixed demand process; it is not evidence of
substitution or learned behavior.

**Scope.** EIP-7918 itself describes the delayed, no-decrease response, and EIP-7999 generalizes multidimensional
fee coupling. The card is a required negative-control identity, not an NMI contribution.

## F4 — execution-controller coordinates

For gas limit `L`, elasticity `E`, denominator `D` and target `T=L/E`, the continuous EIP-1559 update away from
floors is

\[
\frac{b_{t+1}-b_t}{b_t}=\frac{u_t/T-1}{D}
=\frac{E(u_t/L)-1}{D}.
\]

Thus `T` sets the absolute scale, `E` sets saturation in target units and `D` sets feedback gain. A proportional
capacity change or target-preserving change tests fewer controller directions than a denominator-only or joint
non-proportional change.

**Scope.** This follows directly from the published controller and is not new. Integer division, minimum upward
increments and minimum-base-fee policies must still be evaluated by the exact oracle.

## F5 — single-regime alias and intervention-rank boundary

For

\[
y_t=Aq_t+h_t,
\quad q_{t+1}=q_t+K_0y_t,
\quad h_{t+1}=\Phi h_t+\Gamma q_t+w_t,
\]

choose any nonzero `Delta` and set

\[
A'=A-\Delta,
\quad h'_0=h_0+\Delta q_0,
\quad \Phi'=\Phi+\Delta K_0,
\quad \Gamma'=\Gamma-\Phi\Delta+\Delta(I+K_0A').
\]

Direct substitution gives `q'_t=q_t`, `h'_t=h_t+Delta q_t` and `y'_t=y_t` under `K_0`. After changing the
controller to `K_r` while holding both latent laws fixed, the alias-relation defect is

\[
h'_{t+1}-(h_{t+1}+\Delta q_{t+1})=\Delta(K_0-K_r)y_t.
\]

The controller family therefore acts on `vec(Delta)` through

\[
S=\operatorname{stack}_r((K_r-K_0)^\top\otimes I_2).
\]

A rank-deficient `S` leaves a universal nonzero alias subspace. Full column rank removes that particular
controller-invariant alias, although finite-path separation still requires excitation. If `Phi` and `Gamma` may
change freely by regime, replacing `K_0` by each `K_r` in the transformed matrices restores the alias, so the
positive conclusion requires a shared-dynamics or restricted-drift assumption.

**Generated audit.** Experiment 151 found BPO stack rank 2/minimum singular value 0 and maximum observation
divergence `3.51301e-10`. Its generated non-proportional stack had rank 4/minimum singular value `0.012`; all four
perturbations separated in 128/128 seeds. Raw SHA256 is
`6b81a0eddac2fc16697382128dff5621b75cb52d1bf8712e4a0f3193f431c649`.

**Scope.** This is an elementary coordinate-alias construction and a negative-control boundary, not a new
identifiability theorem. The generated full-rank result does not establish real cross-regime invariance or
behavioral adaptation.

## F6 — what would be irreducible

A viable new result must go beyond F1--F5 and established closed-loop identification. Examples of admissible proof
obligations, not claims, are:

1. a partially identified cross-resource response set with a sharp bound that exploits integer controller
   switching and is strictly tighter than standard IV/closed-loop bounds under the same observations;
2. a finite-sample no-refit transfer guarantee across controller parameter changes under explicitly testable
   demand drift, with a lower bound showing why ordinary closed-loop identification cannot attain it;
3. a falsifiable stochastic law for reserve-branch occupation and response that survives fixed latent-demand and
   protocol-only countermodels and transfers outside Ethereum.

No such statement survived the present audit. Experiment 151 additionally closes the current NCS design at
identification: its positive separation assumes cross-regime latent-dynamics invariance, while the available BPO
and Base topologies cannot establish that assumption prospectively or independently. These cards remain exact
oracles and negative controls only.
