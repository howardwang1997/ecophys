# Random-clock free-flight / hard-collision dynamics — T0 result

**Date:** 2026-08-24

**Frozen config:** `configs/empirical_physics/ecomd_random_clock_collision_t0_v1.yaml`

**Frozen implementation/data boundary:** zero market outcomes, paid data, benchmark runs, EcoMD and GPU

## Formal decision

**FAIL/RED at D-1; stop the route.** None of the three frozen protocol candidates satisfies every required
schema condition, and the contract requires at least two independently governed qualifying clocks. AlphaX US
has the cleanest random clock in its rule but no passive event stream exposing empty Match Events or the hidden
book. Xetra is the closest data-ready near-miss: its live EOBI state messages and visible auction book are useful,
but the public rule/schema does not identify the randomization unit or cross-instrument dependence, its historical
order-by-order product does not promise the synchronized state-message stream, and hidden AVD orders affect the
post-price execution. HKEX supplies one market-segment clock per day, not one draw per security, and its status
and auction-order observations cannot be synchronized into the required pre/collision/post record.

The frozen `stop_at_first_failure` rule makes this terminal. G0--G3, the 40-work minimum, finite toys,
implementation and outcome analysis are not authorized after this result.

## Protocol gate matrix

`PASS` means that an official rule and an accessible schema jointly establish the field. `PARTIAL` and `UNKNOWN`
fail an `all_required` gate; they are not invitations to impute the field from trades.

| Frozen requirement | AlphaX US | Xetra T7 14.1 | HKEX CAS |
|---|---|---|---|
| Realized clock draw or exact phase transition | **FAIL:** the filing defines independently randomized security-specific Match Events, but no passive public heartbeat or event identifier reveals each realized event | **PASS prospectively:** EOBI publishes an Instrument State Change when an instrument leaves an auction | **PARTIAL:** market-segment status marks Random Close/Order Matching, but its time fields are nearest-second and carried separately from order/trade data |
| Independent unit and shared-clock clusters | **PASS in rule, unusable in data:** events are security-specific, but unobservable empty events prevent a panel | **UNKNOWN:** the documents expose per-instrument state messages but do not certify independent random-end draws rather than shared schedule/group clocks | **PASS only as one market-segment/day:** all CAS securities share the close; securities are not replications |
| Pre-collision state or sufficient projection | **FAIL:** non-displayed global book and participant parameters are hidden | **PARTIAL:** EOBI 14.1 exposes the visible auction book at full depth, but AVD orders remain hidden and the historical product does not promise a synchronized state stream | **FAIL:** real-time CAS data withhold individual auction orders; IEP/volume is only an aggregate projection |
| Post-collision state | **FAIL:** public TRF records executions, not the full post-event book | **PARTIAL:** post-auction public book/trades are visible, but cannot be paired with a sufficient pre-state | **PARTIAL:** auction trades/closing price are visible, but cannot be paired with the hidden pre-state on a synchronized channel |
| Collision rule and hidden parameters resolved | **FAIL:** price/time rules are public, while counterparty selection and minimum-quantity participant parameters remain private | **FAIL:** regular price formation is public, but hidden AVD orders form a post-price execution layer at the auction timestamp | **FAIL:** price/matching rules are public, but the order state needed to apply them is not disseminated during the auction |
| Empty collision events observable | **FAIL:** no execution means no public TRF marker | **PASS:** leaving the auction generates a state message even without an auction trade | **PASS at market-segment level:** the session changes even if an individual security has no auction trade |
| Timing precise relative to clock and state | **FAIL:** execution time is not the hidden event time | **PASS for the state transition; insufficient overall because the unit is unresolved** | **FAIL for the joint record:** status is nearest-second and officially asynchronous to order/trade channels |
| Compatible reproducible access contract | **FAIL:** no passive public/event-level product was identified; participant connectivity exposes own messages, not the global hidden book | **UNKNOWN:** commercial live/historical order-by-order access exists, but the public contract does not promise synchronized historical state messages or publication rights and cannot resolve the clock unit | **FAIL for the joined schema:** paid Historical Full Book exists, but its public description does not include the session-status record needed to recover the realized close without proxy inference |
| Protocol verdict | **NOT QUALIFIED** | **NOT QUALIFIED — best near-miss** | **NOT QUALIFIED** |

Qualified independently governed protocols: **0/2 required**.

## Evidence by protocol

### AlphaX US

The live SEC Form ATS-N states that Match Events are automatic, calibrated security by security, and separated
by a 40 ms base interval with a random increment up to 20% on either side. It also states that the venue is
non-displayed, that matching is constrained by participant parameters, and that the venue reports executions to
the Nasdaq TRF. An execution report therefore cannot identify an empty Match Event, and the absence of a print
cannot be interpreted as an event marker. The official FAQ only offers participant order entry through private
FIX/BIN connectivity; no public market-event feed or global-book schema was found.

- [Live AlphaX Form ATS-N](https://www.sec.gov/Archives/edgar/data/2000464/000200046426000006/xslATS-N_X01/primary_doc.xml)
- [AlphaX US FAQ](https://www.tmxalphaus.com/faq/)

An active Auction-or-Cancel probe would at most reveal the next event affecting the researcher's own order. It
would perturb the book, would not reveal other orders or participant parameters, and would require broker-dealer
participant access. It is not a passive substitute for the frozen schema.

### Xetra

T7 Release 14.1 activated enhanced Xetra auction transparency on 2026-06-01. EOBI can disseminate the visible
auction book at full depth, and its unchanged Instrument State Change schema marks an instrument leaving the
auction even when no auction trade occurs. Release 14.1 did not create a new random-clock message; it expanded
auction-book transparency. AVD orders remain explicitly absent from call-phase order-book information, activate
only after the regular auction price is determined, and can trade with the regular-auction surplus at the same
execution timestamp. Thus the visible book is richer than an aggregate quote but is still not sufficient for the
declared full pre/collision/post map.

- [T7 Release 14.1 page and activation dates](https://www.cashmarket.deutsche-boerse.com/cash-en/Data-Tech/Initiatives-Releases/release14-1)
- [T7 14.1 EOBI manual](https://www.cashmarket.deutsche-boerse.com/resource/blob/4942838/30c75bbdf69443bb111c89107f776767/data/T7_R.14.1_%20EOBI_Manual_Version_1.pdf)
- [T7 14.1 Xetra market model](https://www.cashmarket.deutsche-boerse.com/resource/blob/4942824/7f80f5406aab402eb2e5e2436ce0821a/data/T7_Release_14.1_-_Market_Model%20_Xetra.pdf)
- [A7 historical order-by-order product](https://www.mds.deutsche-boerse.com/mds-en/analytics/A7-Analytics-Platform/A7-Analytics-Platform-2082116)

Most importantly, a per-instrument status field is not evidence that random draws are independent per instrument.
The official material inspected does not define that clustering unit, and the commercial historical product page
does not promise that Template 13301 state messages accompany the order-by-order history. Counting securities as
clock replications or assuming a historical join would therefore violate the frozen gate.

### HKEX

HKEX's CAS rule has one Random Closing period from 16:08 to 16:10 on a full day, after which all CAS securities
are matched. The OMD-C Trading Session Status message is a market-segment message. Its start/end fields have
nearest-second precision, and the interface specification warns that session status can travel on a separate
multicast channel and is not synchronized with order and trade data. HKEX additionally states that even its
FullTick feed does not disseminate individual orders during an auction.

- [HKEX Closing Auction Session rule](https://www.hkex.com.hk/Global/Exchange/FAQ/Securities-Market/Trading/CAS?sc_lang=en)
- [OMD-C binary interface specification](https://www.hkex.com.hk/-/media/HKEX-Market/Services/Market-Data-Services/Infrastructure/HKEX-Orion-Market-Data-Platform-Securities-Market-OMD-C/HKEX_OMDC_Binary_Interface_Specifications_v1%2C-d-%2C39b.pdf)
- [OMD-C auction-order disclosure FAQ](https://www.hkex.com.hk/Global/Exchange/FAQ/Market-Data/Getting-Market-Data/Orion-Market-Data-Platform-Securities-Market-OMDC?sc_lang=en)
- [Historical Full Book product](https://data.hkex.com.hk/catalog/dataset/bb801552763111efb0542ed09cd1001d?lang=en)

Historical Full Book is a paid order/trade product, but its public product schema does not promise the session
status messages required to join every book transition to the realized system close. Buying it would not be a
permitted D-1 experiment and would not by itself cure the schema failure.

## Theoretical collision warning, not a completed G1

The first failed gate stops the formal prior-art audit, so no E1--E3 novelty claim is adjudicated here. The
limited reduction check nevertheless supplies a strong reopen warning:

- with full state and random observation intervals, transition/generator estimation starts from established
  random-time continuous-time Markov inference, including Duffie--Glynn;
- under a fixed many-to-one observation, collision-erased directions start from standard observability and
  projected-process equivalence classes;
- deterministic flow punctuated by random jumps/collisions is a standard PDMP or hybrid-process object;
- an in-support change of the clock distribution starts from conditional-response integration or importance
  reweighting and needs a collision-specific lower bound or guarantee to survive.

The frozen 40-primary-work minimum was deliberately not completed after D-1 failed. These reductions cannot be
presented as a theorem or literature-complete novelty result.

- Duffie and Glynn, [*Estimation of Continuous-Time Markov Processes Sampled at Random Time Intervals*](https://web.stanford.edu/~glynn/papers/2004/DuffieG04.html)
- Metzner et al., [*Estimation of transition rates from single-molecule time series*](https://publications.imp.fu-berlin.de/35/1/MeDiJaSc07.pdf),
  and Metzner, Horenko and Schütte,
  [*Generator estimation of Markov jump processes from incomplete observations nonequidistant in time*](https://publications.imp.fu-berlin.de/36/1/MeHoSc07.pdf)
- [Koopman representations from irregular intervals](https://doi.org/10.1016/j.physd.2025.135062)
- Mesbahi et al., [*Nonlinear observability via Koopman analysis: Characterizing the role of symmetry*](https://doi.org/10.1016/j.automatica.2020.109353)
- Bertazzi, Bierkens and Dobson,
  [*Approximations of piecewise deterministic Markov processes and their convergence properties*](https://doi.org/10.1016/j.spa.2022.09.004)
- Kennedy et al., [*Non-parametric methods for doubly robust estimation of continuous treatment effects*](https://doi.org/10.1111/rssb.12212)
- Mastrolia and Xu, [*Randomized auction closing time*](https://arxiv.org/abs/2405.09764)

## Binding closure and reopen condition

This route is closed before outcomes and implementation. Do not:

- infer AlphaX empty Match Events or random draws from public trade prints;
- count HKEX securities as independent clock draws;
- count Xetra instruments as independent clocks without an official clustering/randomization declaration;
- replace the two-protocol gate with one protocol plus a synthetic or non-financial toy;
- purchase data, fit a conditional outcome model, implement EcoMD or run a GPU under this T0; or
- relabel generic irregular-time regression as hard-collision tomography.

Reopening requires a new preregistration backed by **two** independently governed, versioned access contracts
that explicitly expose event/phase identifiers including empty events, the shared-clock unit, synchronized
pre/post observations sufficient for the declared collision map, all hidden matching parameters relevant to
that map, timestamp precision and reproducible publication licensing. It must also state a candidate theorem or
finite-sample boundary that does not reduce to random-time Markov estimation, semigroup embedding, irregular-time
Koopman learning, PDMP/hybrid modeling or the already closed observation quotient. A vendor's generic “full book”
description or an offer to buy data is not enough.

No market outcome, event-window statistic, paid or bulk dataset, synthetic benchmark, EcoMD fit/training or GPU
was accessed for this decision.
