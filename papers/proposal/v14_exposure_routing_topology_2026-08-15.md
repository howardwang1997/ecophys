# V14 exposure-routing topology after U1R

**Status:** architectural hypothesis from post-hoc pre-treatment description; not yet a validated method

## Revised multiscale decomposition

```mermaid
flowchart LR
    G[Governance authorization] --> C[Adapter configuration]
    C --> M[Exact contract transition M2]
    M --> R[Learned exposure router]
    R --> S[Swap-intensity channel]
    R --> P[Position-action channel]
    S --> A[Participant adaptation M3]
    P --> A
    A --> E[Entry exit and share dynamics M4]
    E --> O[Aggregate observables]

    U0[U0: exact 1000 transitions] -.supports.-> M
    U1A[U1a: activation != activity] -.motivates.-> R
    U1R[U1R: sparse concentrated counts] -.constrains.-> R
```

The exact event mechanism should remain non-learned when its code, authority and transition are observable. What
must be learned is the state-dependent routing from a technical intervention to economically active units and
channels. This resolves the earlier false choice between a fixed event layer and a fully learned mechanism: keep
the executable rule fixed, but learn exposure incidence and behavioral response separately.

## Mathematical object

For channel-specific event counts `a_i^(c)`, define exposure weights
`p_i^(c) = a_i^(c) / sum_j a_j^(c)`. The router is not merely a binary mask; it must predict both support and mass,
and may differ between swap and position channels. A later response aggregate under this measure is
`sum_i p_i^(c) r_i`, not the uniform contract average.

With `u_i=1/N` and `g_i=N p_i`, the exact identity

`E_p[r] - E_u[r] = Cov_u(g,r)`

locates the aggregation error. The exposure distribution alone does not identify the error's sign because the
response covariance is unopened. Its HHI fixes `Var_u(g)=N HHI-1`, which controls a Cauchy upper bound. This is an
elementary diagnostic identity, not a claimed new theorem.

## Evidence and missing links

| Link | Current evidence | Status |
|---|---|---|
| governance to configuration | exact Proposal 94 execution | observed |
| configuration to contract transition | 1,000 ordered U0 transitions | validated development M2 |
| contract transition to preperiod event incidence | U1a plus complete U1R prefix | observed, post-hoc routing analysis pending |
| incidence to causal response | no valid controls or post-treatment access | blocked |
| public key/NPM owner to beneficiary | incomplete identity ontology | blocked |
| adaptation to entry/exit ecology | no M4 panel | blocked |

## Consequence for source selection

The next M3/M4 domain must expose more than exact rules. Before response access it needs a defensible exposure
denominator, multiple action channels, stable participant identifiers and an untreated/not-yet-treated comparison
with overlap. Uniswap remains useful as the exact-M2 anchor, but U1R forbids treating its current propagation
prefix as the behavioral panel.

NMI would require a method showing that an explicit router improves intervention prediction across systems and
beats simpler activity-weighted baselines. NCS would additionally require the router to transfer across domains,
connect exact mechanisms to validated observations and yield frozen real-data prediction. The current identity
and one Uniswap census satisfy neither bar; they only make the missing operator explicit.
