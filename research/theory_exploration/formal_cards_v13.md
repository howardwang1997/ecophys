# Formal cards v13 — observability of algorithmic-market mechanism transitions

These cards close the frozen V13 latency/information/concentration program at the observation-contract gate. They
are identification controls, not novelty claims. No auction outcome was queried in constructing them.

## O1 — a relay feed is a selected clocked projection

Let `B_t` denote all builder submissions for opportunity `t`. A relay-location `r` records

\[
 O_{rt}=S_r(B_t;G_{rt},Q_{rt},F_{rt},C_{rt}),
\]

where `G` is geographical/network routing, `Q` is relay admission and rate limiting, `F` is bid forwarding and
sharing policy, and `C` is the relay clock/sequencing convention. The recorded latency statistic is therefore a
functional of both agent behavior and the observation system.

Ultra Sound's global data view aggregates its own regional instances; it is not the union of every MEV-Boost
relay. Its documentation states that bids are sequenced by relay `received_at` unless the builder supplies a
monotone sequence, and that cross-region forwarding depends on a sharing rule. Consequently,

\[
 \Delta L_{\rm observed}
 \ne \Delta L_{\rm agent}
\]

without invariance or calibration of `S_r` and `C_r`. A post-ePBS global P2P bid topic changes the observation
operator itself. The pre/post contrast cannot be interpreted as a behavioral latency effect merely by adding relay
or builder fixed effects.

## O2 — losing payload absence blocks the information-rent channel

For builder `i`, let `V_{it}` be its private valuation, `b_{it}` its bid and `P_{it}` its proposed payload. In
MEV-Boost public data, a relay may expose `b_{it}` for submissions it received, but losing payloads `P_{it}` are not
generally disclosed. An exclusive-order-flow proxy computed from the winning on-chain payload is therefore
post-selection:

\[
 X_{it}^{\rm observed}=X(P_{it})\mathbf 1\{i=W_t\}.
\]

It cannot identify the relationship between private information and winning over all bidders without a model for
the missing losing payloads. Public-mempool nonappearance is also not proof of exclusivity because mempool
observation has incomplete geographical and peer coverage. H2 is therefore not operational under the current
frozen free-data contract.

## O3 — strategic withholding and correlated failure are observationally equivalent

Let `E_t=1` indicate that an ePBS slot is empty after a committed builder bid. Let `Z_t` be public covariates such
as external price movement, volatility and builder identity. Consider two latent mechanisms:

\[
 E_t=A_t\lor N_t,
\]

where `A_t` is strategic free-option exercise and `N_t` is nonstrategic propagation, implementation or network
failure. If only `(E_t,Z_t)` is observed, then for any law

\[
 p(z)=\Pr(E_t=1\mid Z_t=z)
\]

there is a pure-strategy model with `Pr(A=1|Z=z)=p(z), N=0` and a pure-failure model with
`A=0, Pr(N=1|Z=z)=p(z)`. They induce the same observed distribution.

Thus a correlation between empty slots and adverse price moves, even with the theoretically predicted sign, does
not identify strategic exercise. Builder identity and ordinary network controls do not repair the equivalence if
unmeasured failure probability also depends on load, volatility or geography.

## O4 — evidence that would reopen the free-option mechanism

At least one source of separation is required:

1. authenticated multi-vantage capture of bid, payload and blob propagation showing preparation followed by
   selective withholding;
2. a protocol-randomized or externally assigned penalty/window treatment that changes strategic incentives but
   not physical propagation;
3. a negative-control payload class with the same size/routing load but no external-price option value, together
   with assumptions sufficient to bound differential failures; or
4. an independently measured failure process yielding informative upper bounds on `Pr(N=1|Z)`.

For example, if a validated external monitor supplies
`0<=n_-(z)<=Pr(N=1|Z=z)<=n_+(z)`, with the coherent lower bound `n_-(z)<=p(z)`, and strategic and
nonstrategic causes cannot occur simultaneously, then

\[
 \max\{0,p(z)-n_+(z)\}
 \le \Pr(A=1\mid Z=z)
 \le p(z)-n_-(z).
\]

These elementary bounds become informative only when the failure monitor is independently calibrated. Deriving a
general sharp-bound estimator without such evidence would be another relabeling of standard partial
identification.

## O5 — V13 disposition

The frozen three-part claim does not survive:

- H1 lacks a common pre/post latency clock and complete auction support;
- H2 lacks losing payloads and a direct private-information proxy; and
- H3's qualitative persistence/centralization mechanism is already predicted in direct MEV-Boost/ePBS work.

EIP-7732 remains in Review and the Gloas fork epoch is TBD, so there is also no sealable primary transition time.
CoW CIP-85/Consistency v2 and Jito BAM are useful development systems but do not supply a prospectively sealed,
independently governed replication of the frozen relay-removal channel.

The only retained lead is the broader question of **self-concealing mechanism actions**: an agent can suppress the
outcome that would reveal why it acted, so the action and its nonstrategic physical failure mode become
observationally equivalent. This is a possible V14 equation/prior-art audit, not a V13 survivor or experiment
authorization.
