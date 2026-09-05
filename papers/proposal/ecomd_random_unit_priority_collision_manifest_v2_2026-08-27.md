# Collision manifest v2: random-unit priority, speed investment and market quality

Date: 2026-08-27

Status: **bounded primary-work re-audit; paper-only**

## Exact subject node

Human participants are assigned by independent market session to FIFO or uniform random-unit
allocation at an equal price. The primary outcome is costly latency investment before own fill
feedback; a full induced-value CDA supplies secondary market-quality and simulator-response
outcomes.

A direct collision must contain human market participants, an assigned FIFO-versus-random
within-price allocation contrast, and either latency investment/arrival effort or the same
replay-complete CDA response. Proposal, theory, field rule changes, fixed-order-flow simulations
and alternative priority rules occupy adjacent claims but are not direct collisions.

## Primary neighborhood

| Work | Evidence lane | What is already occupied | Direct collision? |
|---|---|---|---|
| [Lim (2026), Random Queue Priority](https://doi.org/10.2139/ssrn.6574208) | Controlled dual-engine simulation + theory | FIFO versus randomized priority on identical order flow; fast/slow execution redistribution; arms-race theory | No human decisions or assigned human market |
| [Lim companion engine](https://github.com/boonchuan/delta-exchange) | Public implementation | Random queue mechanisms and simulated exchange tooling | No human causal response; public implementation samples/reorders orders rather than freezing our anti-splitting unit kernel |
| [Yang et al. (2026)](https://www.sciencedirect.com/science/article/pii/S0957417426003672) | Heterogeneous-agent artificial market | Time, pro-rata and equal-sharing effects on liquidity, efficiency and volatility | Agents; no random-unit human arm |
| [Khapko & Zoican (2021)](https://doi.org/10.1016/j.finmar.2020.100601) | Human laboratory market | Costly low-latency investment under deterministic/random and symmetric/asymmetric speed bumps | Time priority remains fixed; no allocation-rule treatment |
| [Angel & Weaver (1998/1999)](https://doi.org/10.2139/ssrn.169274) | Toronto field change + model | Time priority fosters price competition; pro-rata fosters size competition | Observational rule change, not random allocation |
| [Aspris et al. (2015)](https://doi.org/10.1002/fut.21708) | LIFFE field change | Pure pro-rata to time-pro-rata adaptation and child-order behavior | Different hybrid mechanisms and no assignment |
| [Haynes & Onur (2020)](https://doi.org/10.1016/j.jcomm.2019.100109) | Matching-rule field study | FIFO versus a more pro-rata algorithm; size and cancellation responses | Different deterministic rule change |
| [Frino, Hill & Jarnecic (2000)](https://doi.org/10.3905/jod.2000.319139) | Screen-market comparison | Price/time versus pro-rata execution outcomes | Field comparison, not random or human assignment |
| [Battalio, Jennings & McDonald (2021)](https://doi.org/10.1016/j.finmar.2020.100567) | NYSE parity field evidence | Cost of deviations from time priority under parity | Different hybrid allocation and selection environment |
| [Degryse & Karagiannis (2022)](https://doi.org/10.2139/ssrn.3186009) | Priority-rule theory | Price-broker-time versus price-time execution and welfare | Theory; different rules |
| [Yueshen (2025)](https://doi.org/10.1287/mnsc.2023.03371) | Queue-position equilibrium | Random initial queue uncertainty, revision and excessive/fleeting depth | Queue realization, not an exchange random-allocation treatment |
| [Daures, Moinas & Boussetta (2026)](https://doi.org/10.1287/mnsc.2023.03998) | Euronext field behavior | Early submission to gain time priority in the preopen | Observational call-auction setting |
| [Roşu (2009)](https://doi.org/10.1093/rfs/hhp011) | Dynamic LOB theory | Strategic limit/market choice and waiting costs | FIFO theory only |
| [Gao & Xu (2022)](https://doi.org/10.1016/j.jedc.2021.104287) | Queue score + learning | Queue-position value, cancellation and bandit adaptation | No priority intervention |
| [Huang, Lehalle & Rosenbaum (2015)](https://doi.org/10.1080/01621459.2014.982278) | Queue-reactive simulator | Anonymous aggregate-state Markov baseline | No identity allocation response |
| [Gode & Sunder (1993)](https://doi.org/10.1086/261868) | Human/ZI laboratory benchmark | Institution plus private-value/no-loss constraints can generate aggregate efficiency | Not an identity-free M0 theorem and no priority arm |
| [Avellaneda & Stoikov (2008)](https://doi.org/10.1080/14697680701381228) | Market-making control | Inventory-aware optimal quote distance with intensity depending on distance to midprice | Not a queue-ahead model; removed as strategic anchor |
| [Hersch (2023)](https://doi.org/10.1007/s10551-022-05315-7) | Procedural-fairness proposal | Random selection for service in exchange matching | Normative/design analysis; no market response |
| Haeringer & Melton (2020), High Frequency Fairness | Mechanism proposal | Random serial processing and access fairness | No human market response |
| [Mavroudis et al. (2019)](https://arxiv.org/abs/1910.00321) | Fair matching design | Temporal-fairness limits and matching mechanisms | No causal human experiment |
| [Budish, Cramton & Shim (2015)](https://doi.org/10.1093/qje/qjv027) | Market-design theory | Latency-rent removal by frequent batch auctions | Different institution |
| [Aldrich & López Vargas (2019)](https://doi.org/10.1007/s10683-019-09605-2) | Human lab institution comparison | Continuous versus frequent batch markets | Different treatment; cannot supply same-design variance automatically |

## Corrections to v1

- Lim is a direct simulation/theory neighbor, not merely a proposal. Its full SSRN PDF remained
  inaccessible during this audit, but the current abstract and public companion repository both
  establish a nonhuman lane. This uncertainty forbids strong claims about details not in those
  sources.
- Yang et al., Khapko--Zoican, Angel--Weaver, Haynes--Onur, Battalio et al., Yueshen and Daures et
  al. materially narrow the novelty story and are now load-bearing citations.
- Avellaneda--Stoikov's intensity is a function of quote distance, not queue-ahead. Gode--Sunder
  includes private-value/no-loss constraints and is not the pure M0 invariance model. Their DOIs
  are corrected to `10.1080/14697680701381228` and `10.1086/261868`.
- The public Lim implementation makes an anti-splitting semantic distinction important: this
  project uses uniform resting-unit sampling, not a uniform lottery over variable-size orders.

## Verdict

No exact human FIFO-versus-random-unit allocation experiment with costly speed choice was found in
this bounded neighborhood. The direct-collision gate **provisionally survives**.

Claims that do not survive are: first randomized-priority mechanism, first simulation, first human
speed-investment market, first secondary-priority analysis, and any universal liquidity sign.
Permitted wording is: “To our preregistered bounded search, this is the first human laboratory test
combining FIFO-versus-uniform-random-unit allocation with a pre-feedback costly-speed endpoint.”

Re-audit triggers are an exact human treatment surfaced later, the inaccessible Lim full text
containing human data, or a publication appearing before manuscript freeze. No participant work is
authorized by this verdict.
