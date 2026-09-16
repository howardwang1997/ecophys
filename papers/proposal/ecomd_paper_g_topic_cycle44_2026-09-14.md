# Paper G Cycle44: isotope-only catalytic pathway discrimination

PRIVATE / INTERNAL. 2026-09-14 NZ. One bounded F0/F1 measurement-method screen. **Close the exact isotope-only topology-discrimination formulation** by an explicit positive, mass-conserving counterexample. No new theorem, observed catalytic failure, full review or experimental execution is claimed.

## Question and scope

Native object: a catalyst at fixed chemical steady state, temperature, potential where applicable, feed composition and flow. A carbon-isotope label changes without altering rates or total chemical populations. The observed response is the product's labelled-carbon flux, optionally supplemented by calibrated total labelled surface inventory.

Intervention: change the temporal isotope fraction u(t), including pulse trains and adaptive schedules, while retaining this chemical state. H1 proposes that a learned schedule can separate a slow productive parallel pathway from reversible storage outside the direct product-forming step despite matching conventional transients. H0 says some positive networks remain observationally equivalent for every such schedule.

Discriminator: an admissible waveform with unequal predicted observation laws, or an exact equivalent pair ruling out identification on the proposed model class. A positive result would justify a cheaper pathway-measurement strategy; a negative result identifies which extra state observation or rate-changing intervention is necessary. Neither outcome automatically establishes an ICLR/ICML contribution.

The source lane is a native control restriction, not contradictory claims across different catalysts. Earlier formate search hits concern different supports, reactions and conditions; they are not a matched scientific fork. A reversible holding pool can eventually contribute labelled carbon to product and is not a chemically disconnected, inert spectator.

## Two primary anchors

- [Elucidating the Origins of Electrocatalytic Phenomena Using Steady State Isotopic Transient Kinetic Analysis, ACS Catalysis (2026)](https://doi.org/10.1021/acscatal.6c00526): indexed primary method/interpretation excerpts only. Electrochemical SSITKA on methanol oxidation over Pt uses transient product signals and pool models. It is a physical measurement anchor, not evidence that the counterexample below describes that experiment. The full article/supplement and outcome payloads were not reviewed.
- [Yonge et al., model-based TAP experiment design, arXiv v2 (2023)](https://arxiv.org/html/2309.15786v2): selected methodology and discrimination discussion, corresponding to a 2024 publication. Pulse intensity, timing and temperature are existing design variables; comparing mechanisms must allow their parameters to be refitted. TAP's chemically perturbing, low-pressure experiments differ from the isotope-only intervention here. The final published supplement was not reconciled; no first active kinetic-design claim is available.

The hard failure below stops further source expansion. No repository metadata, source data, fitted model or scientific implementation was accessed.

## C1: parallel productive pools and a reversible holding pool can be equivalent

Use label amounts measured in a common carbon unit. Set the constant total incoming carbon flux to F>0; u(t) is its labelled fraction. Initial labelled amounts are zero, while the unlabelled chemical populations are already at steady state. All rate constants below are positive; the isotope has no kinetic effect. Product flux means the labelled product flux y(t).

Parallel model P:

\[
\dot x=wFu-a x,\qquad
\dot z=(1-w)Fu-b z,\qquad y=a x+b z,
\]

where a>b>0 and 0<w<1. Both pools directly produce product. Its normalized input-output transfer function is

\[
G_P(s)=\frac{y(s)}{F u(s)}
=\frac{wa}{s+a}+\frac{(1-w)b}{s+b}
=\frac{c s+ab}{(s+a)(s+b)},\quad c=wa+(1-w)b.
\]

Reversible-storage model R:

\[
\dot X=Fu-(k+e)X+rZ,\qquad
\dot Z=eX-rZ,\qquad y=kX.
\]

Only X directly produces product; Z returns material to X. Choose

\[
k=c,\qquad r=ab/c,\qquad
e=a+b-c-ab/c=\frac{(a-c)(c-b)}{c}>0.
\]

Then k+e+r=a+b and kr=ab, so

\[
G_R(s)=\frac{k(s+r)}{s^2+(k+e+r)s+kr}
=\frac{c s+ab}{(s+a)(s+b)}=G_P(s).
\]

Both systems are stable positive compartment models, with the same steady product flux F and the same complete product response for every permissible u(t). For example a=2, b=1, w=1/2 gives c=k=3/2, r=4/3, e=1/6, in consistent inverse-time units. The product transfer function is (1.5s+2)/((s+2)(s+1)) in both cases.

Adding the same exogenous observation-noise law yields identical observation distributions. Any randomized adaptive isotope policy based only on those observations therefore also has the same history distribution under both models, by induction over decisions. A neural model or richer waveform cannot recover the hidden topology on this class. This statement assumes the declared mean-response plus common-noise observation model; chemically specific fluctuation statistics are not proven equivalent. Unknown transport is unnecessary for the counterexample, and a common linear transport convolution preserves it.

This is an elementary linear compartment realization equivalence, not a newly established theory or a diagnosis of a published catalyst mechanism. Distinct networks elsewhere in the model class may be identifiable; predictive transfer-function estimation remains useful.

## C2: total labelled inventory is still insufficient, but a selective channel can separate the pair

Let T_P=x+z and T_R=X+Z. In either model,

\[
\dot T=Fu-y.
\]

With equal initial labelled inventory, equal product responses imply equal total labelled inventory for every u. Equivalently, T(s)/(Fu(s))=(1-G(s))/s. A perfectly calibrated nonselective total-label observation thus adds no distinguishing mean response for this pair. Total chemical surface population is also equal at steady state: F[w/a+(1-w)/b]. This is stronger than merely matching product residence times.

A genuinely selective observation of the second compartment would distinguish them. Normalize each second-pool labelled amount by its own steady chemical amount. For the numerical example, the transfer from isotope fraction to this normalized amount is 1/(s+1) for P and 2/((s+2)(s+1)) for R. Following a unit step, the initial slope is respectively 1 and 0. This comparison assumes an independently justified chemical assignment, selective response and adequate temporal observation; an unassigned spectral component cannot be presumed to supply that channel.

A potential, reactant-concentration or temperature intervention might also distinguish the networks, but it changes the allowed rate family. Its rate effects, catalyst state and transport must be constrained independently; arbitrary refitting of every condition can preserve ambiguity. No such intervention asset has been qualified here, and no second raw question is created from this escape condition.

## Disposition and next step

One quick closure, zero survivors. The exact claim that isotope-only learned scheduling can distinguish these unrestricted positive pathway alternatives at fixed chemical state fails C1, even when total inventory is added in C2. Closing it does not close catalytic ML, isotope-response prediction, restricted identifiable model classes or multi-observable experimental design.

Retain the positive-rate equivalent-network pair and the total-inventory/selective-observation contract. Re-entry requires an explicit model restriction or newly usable selective observation/rate-control asset that excludes the counterexample, with a distinct scientific ML contribution beyond existing kinetic design. Do not revive it by changing the neural architecture, catalyst label or isotope pulse pattern alone. Another unrelated native scientific question remains eligible.

## Accounting and authorization

One source-led measurement-method program, one quick screen, two bounded primary readings, two standard analytic controls. The two-measurement/two-intervention targets are unmet; no twelve-program cycle, global source-scarcity assertion or quota filler. No F2/F3, forecast, machine card, outcome access, implementation, simulation, training, GPU, laboratory work, outreach, delegation or publication.

Paper G88 formulations/28 cycles/0 cards; detailed ledger35/172; inclusive44/228. Graph332 nodes/279 edges/1965 locators; evidence1227; candidate0/parked13. Earlier histories and decisions preserved. Broad ICLR/ICML goal remains incomplete.
