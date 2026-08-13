# V6 identifiability closure — exact fee controllers and latent demand

**Closed:** 2026-08-13

**Outcome access:** none; generated paths and public mechanism/intervention metadata only

**Decision:** `V6_NO_SURVIVOR_IDENTIFIABILITY`

The current NCS candidate `V6-NCS-1` is retired as `RETIRED_IDENTIFIABILITY`. The NMI candidate was already
retired as prior art. No real response outcome, remote worker or GPU is unlocked.

## 1. Evidence chain

The decision combines four distinct results rather than treating one simulation as decisive:

1. Experiment 149 establishes bit-exact local implementation of the selected EIP-1559/EIP-4844/EIP-7918
   controller cases. It removes a software ambiguity but contains no behavioral information.
2. The scale audit shows that Prague/Osaka, BPO1 and BPO2 form an almost exact normalized scale family. BPO-only
   transfer can be solved by a mechanical scale oracle and does not provide a scientifically useful second
   controller direction.
3. The Base registry supplies non-proportional controller directions, but only as historical operations on one
   chain and one administrator; several are bundled or locally confounded, and no future task is available.
4. Experiment 151 confirms an exact single-regime latent-state alias and the intervention-rank boundary. A
   generated full-rank intervention separates the frozen aliases only after imposing shared latent dynamics
   across regimes. That invariance is the very behavioral assumption the real study would need to establish.

Experiment 150 is not part of the scientific evidence. It is permanently
`VOID_PREMATURE_FORMAL_CELL_EXECUTION`; Experiment 151 is the disclosed, disjoint-seed process repair.

## 2. Exact boundary exposed by Experiment 151

Consider the declared linear witness

\[
y_t=Aq_t+h_t,
\qquad q_{t+1}=q_t+K_0y_t,
\qquad h_{t+1}=\Phi h_t+\Gamma q_t+w_t.
\]

For any nonzero matrix `Delta`, define

\[
A'=A-\Delta,
\quad h'_0=h_0+\Delta q_0,
\quad \Phi'=\Phi+\Delta K_0,
\quad \Gamma'=\Gamma-\Phi\Delta+\Delta(I+K_0A').
\]

With shared innovations, induction gives `q'_t=q_t`, `h'_t=h_t+Delta q_t` and `y'_t=y_t` throughout the
development regime. Thus a single closed-loop regime does not identify `A` from `(q,y)` when the latent update is
unrestricted within this class.

If the two fitted systems are then held fixed while the controller changes to `K_r`, the one-step failure of the
alias relation is

\[
h'_{t+1}-(h_{t+1}+\Delta q_{t+1})
=\Delta(K_0-K_r)y_t.
\]

Across interventions, the controller-only map on `vec(Delta)` has stack

\[
S=\operatorname{stack}_r\left((K_r-K_0)^\top\otimes I_2\right).
\]

If `S` is rank deficient, a nonzero controller-invariant alias subspace remains. If it has full column rank, that
universal alias is removed, but observable separation additionally needs response excitation. This is standard
linear identifiability algebra and is not claimed as a new theorem.

For the BPO topology, `rank(S)=2` and the minimum singular value is zero because only the blob-gain direction
changes; the maximum generated path divergence was `3.51301e-10`. For the deliberately non-proportional topology,
`rank(S)=4`, the minimum singular value is `0.012`, and all four perturbations separated in all 128 formal seeds.

The constructive escape is equally important. If the latent dynamics may be regime specific, define for each new
gain

\[
\Phi'_r=\Phi_r+\Delta K_r,
\qquad
\Gamma'_r=\Gamma_r-\Phi_r\Delta+\Delta(I+K_rA').
\]

The alias is restored in every regime. Therefore intervention diversity identifies the response only under a
shared-dynamics or otherwise restricted-drift contract. A generated experiment can impose that contract; the
available market topology cannot validate it before the claimed transfer.

## 3. Gate decision

| Gate | Final state | Reason |
|---|---|---|
| G0 exact mechanism | `PASS_EXP149` | 97 official cases, 107 blocks and zero mismatch |
| N0 NMI novelty | `FAIL_NO_SURVIVOR` | closed-loop identification, IV and multi-resource control cover the proposed composition |
| N0 NCS phenomenon | `CONDITIONAL_ONLY` | a prospective response law would be meaningful, but no identified instance is available |
| D0 free reconstruction | `CONDITIONAL_FIELDS_ONLY` | free canonical fields exist; untouched future and independent cells do not |
| I0 behavioral identification | `FAIL_LATENT_INVARIANCE` | the response is aliased unless cross-regime latent dynamics are restricted; the restriction is not testably supplied |
| P0 generated attack | `PASS_NEGATIVE_BOUNDARY` | Exp151 confirms the alias/rank distinction, not a market estimator |
| prospective intervention | `FAIL_EMPTY` | BPO3 is unset; Base has no frozen active future operation |
| independent replication | `FAIL_EMPTY` | no separately administered finalized event was sealed |

Passing G0 and the generated negative control cannot compensate for the indispensable I0 and replication failures.
Under the frozen anti-rescue rule, opening historical outcomes now would turn the project into post-hoc exploration
without a route to its declared NCS claim.

## 4. Why no further current experiment is justified

- More seeds repeat exact algebra and cannot test real latent-dynamics invariance.
- BPO1/2 add essentially no controller direction and their outcomes are already public.
- Base outcomes could support exploratory same-chain diagnostics, but cannot fill either the prospective or
  independent cell and several operations carry explicit confounders.
- A larger neural estimator cannot create an instrument, an intervention or an invariant latent law.
- GPU scale-up changes precision or throughput, not identification.

The two V100 32 GB hosts and the RTX2060 therefore remain idle and unqueued. Current V6 compute consumed only
small local CPU runs; no H20 is assumed or permitted.

## 5. Reopen contract

V6 may be reopened only as a new preregistered design after all of the following exist before outcome access:

1. a finalized, genuinely non-proportional controller intervention with timestamp and parameters frozen before
   activation;
2. a separately administered compatible-system intervention or later untouched replication, also frozen before
   outcomes;
3. a falsifiable invariance or partial-identification contract that remains informative under declared latent
   workload drift and bundled changes;
4. observable negative controls, anticipation windows and exclusion rules capable of rejecting that contract;
5. a pre-change estimator and full-vector scoring rule frozen against the exact controller and scale oracle.

A newly announced BPO scale increase alone does not satisfy items 1 or 3. A historical Base download alone does
not satisfy items 2 or 3. A new architecture or more compute satisfies none of them.

## 6. Preserved contribution

V6 remains useful as a rigorous negative research package: a verified exact-controller oracle, a normalized-scale
audit, a provenance-checked intervention topology, an explicit observational-equivalence construction and an
intervention-rank diagnostic. These are reusable baselines and design filters. They are not, separately or
together, a complete NCS or NMI paper.
