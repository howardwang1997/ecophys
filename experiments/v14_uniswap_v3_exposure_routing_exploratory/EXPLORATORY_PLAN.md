# Exploratory plan — mechanism activation to event-exposure routing

**Frozen for computation:** 2026-08-15 11:41 UTC

**Status:** explicitly post hoc; the U1R failure is binding and there is no pass/fail gate

## Motivation

U1R activated no new scientific route, but its already consumed counts expose an architectural distinction worth
quantifying. A technical mechanism can be applied to 1,000 contracts while observable economic events occupy a
much smaller and non-uniform measure over those contracts. Swap and position actions may also define different
measures. Treating “contract activated” as “one equal economic unit treated” is therefore an observation-model
assumption, not a consequence of exact mechanism execution.

This analysis cannot repair U1R. It uses only its committed per-pool pre-treatment counts and has no inferential
threshold. Metrics and identities are fixed here before the metric script is run, but the source result and its
headline concentration are already known; the output remains post hoc.

## Frozen outputs

For swap, position-action and combined event counts over all 1,000 pools, report:

- active/inactive counts and fractions;
- top-1/3/5/10/20 event-count shares;
- HHI, inverse-HHI effective count and entropy effective count;
- Gini over the full population and over active pools;
- total variation from a uniform contract measure;
- variance and standard deviation of the exposure multiplier `g_i = N p_i`.

Compare swap and position channels by support intersection/Jaccard, conditional support coverage, total variation,
Jensen-Shannon divergence and cosine similarity. Report the same total/active counts and representation ratios for
packed fee classes and the two exact 500-pool propagation batches. Retain the top ten public pool addresses per
channel only to make concentration auditable; do not resolve tokens, wallets or beneficiaries.

## Exact aggregation identity

For non-negative event counts `a_i`, define the uniform contract measure `u_i = 1/N`, normalized exposure measure
`p_i = a_i / sum_j a_j` and exposure multiplier `g_i = N p_i`. For any later pool response `r_i`,

`E_p[r] - E_u[r] = Cov_u(g, r)`.

This follows because `E_u[g] = 1` and `E_u[g r] = E_p[r]`. Also
`Var_u(g) = N HHI(p) - 1`, giving the Cauchy bound

`|E_p[r] - E_u[r]| <= sqrt((N HHI(p)-1) Var_u(r))`.

For a bounded response, the alternative bound is total variation times its range. These are elementary algebraic
identities, not a novel theorem and not evidence about an unobserved response. Their role is to specify why a
multiscale model needs a learned exposure router between an exact event mechanism and participant dynamics.

## Claim and access locks

- no new RPC, API, chain, control, post-treatment, identity or economic-amount data;
- no reweighting is used to change the U1R decision;
- event counts are not called volume, liquidity, capital or welfare;
- the U0 propagation prefix is not generalized to all Uniswap;
- no causal, predictive or universal-scaling claim;
- local CPU only, no paid data, remote worker or GPU.
