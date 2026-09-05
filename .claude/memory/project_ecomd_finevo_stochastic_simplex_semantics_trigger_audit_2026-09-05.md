# EcoMD FinEvo stochastic-simplex semantics trigger audit (2026-09-05)

## Durable decision

`not_trigger`; no candidate harvesting, outcome access, implementation, SSH or GPU work is
authorized. FinEvo is a direct 2026 collision for broad evolutionary market-ecology simulation,
but its mathematical inconsistency is an erratum-sized finding rather than an ICLR method. It
removes no blocker from the closed generic simulator-audit, population-transfer, market-native
refinement, composition-path, stochastic-semantic-conformance, measure-correct-projection, or broad
differentiable-market-simulator routes. No graph node was created.

## Exact semantic failures

For `P(x)=I-1x^T`, the paper writes heterogeneous diffusion `B=diag(x) sigma P`. Its total-mass row
is `1^T B=x^T sigma-(x^T sigma 1)x^T`, generically nonzero. At
`x=(1/2,1/2), sigma=diag(1,2)`, `d sum_i X_i=(gamma/4)(dW_2-dW_1)`. The correct noisy-logit order is
`diag(x) P sigma`; Appendix C uses that order, while the main equation and Appendix E do not.

The implemented normalized exponential update has the weak limit
`dX_i=[beta X_i(V_i-bar V)+c_i(X)]dt + gamma X_i[sigma_i dW_i-sum_j X_j sigma_j dW_j]`, where
`c_i=(X_i/2)[q_i(1-2X_i)-sum_j X_j q_j(1-2X_j)]` and
`q_j=gamma^2 sigma_j^2`. This is the classical noisy exponential-learning stochastic replicator,
including its Itô drift; it is not the SDE claimed by FinEvo. Independently resampled Dirichlet
innovation multiplied by `h` contributes fixed-horizon variance `O(h)` and vanishes as `h -> 0`.

The reported additive quantity is variance of a strategy-share increment, not market-return
volatility. Splitting a behaviorally identical strategy of mass `x_i` into `r` labels changes
entropy by `x_i log r` and HHI by `-x_i^2(1-1/r)` even when aggregate orders and prices are coupled
identically; top-one and phase-change metrics can change too.

## Collision and re-entry boundary

Mertikopoulos--Moustakas derive the exact softmax Itô correction; Mertikopoulos--Viossat distinguish
the nonequivalent stochastic-replicator semantics; Lehmann supplies the Aitchison-simplex geometry;
and stochastic modified equations occupy generic discrete-algorithm-to-SDE approximation. Automatic
local-moment checking is useful QA but does not yield a new estimator or theorem, while strategy
split/merge repair reduces to branching and Markov lumpability already closed in this repository.

Re-enter only for a constrained-update generator method with separating finite-sample upper/lower
bounds beyond local moments and SME, a market-native split/merge-invariant estimand, a theorem
linking certification to external intervention response, two independent non-EcoMD truth systems,
and untouched market confirmation. A projector fix, simplex layer, mechanism ablation, stylized-
fact table, latent population sweep, or EcoMD--FinEvo composition is not a trigger.

Formal result:
`papers/proposal/ecomd_finevo_stochastic_simplex_semantics_trigger_audit_2026-09-05.md`.
