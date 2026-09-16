# Paper G Cycle43: history-coded multiplex synaptic measurement

PRIVATE / INTERNAL. 2026-09-14 NZ. F0/F1 research screening only; not a public result, execution protocol, prospective forecast or completed novelty audit.

One provisional **measurement_method** question survives: can input-specific stimulus histories make multiplexed short-term synaptic response measurement more economical than capable single-target scheduling? Main-track scientific and methodological contributions remain unqualified.

## Native question and competing explanations

Subject: a declared set of presynaptic inputs to one recorded postsynaptic cell, with fixed preparation, cell types, expression method, opsin, illumination geometry, clamp conditions, pulse power and initial recovery history. The primary target is each input's **protocol-conditioned evoked-current response curve** over a frozen set of pulse histories. Release probability, vesicle number and an intrinsic replenishment constant are additional mechanistic targets requiring stronger assumptions and observations.

Action: assign different burst/recovery histories to labelled inputs, allowing concurrent pulses, then infer individual history-dependent responses from their overlapping current trace. A tentative construction jointly chooses target subsets and per-input timing, using a declared dynamic observation model. Merely adjoining a static compressed-sensing model to an existing active-learning controller is not a contribution.

- H1: history assignment creates distinguishable response signatures and useful joint measurements, improving held-out per-input response estimation at fixed total experimental and computational cost.
- H0: spike-arrival uncertainty, release variability and waveform overlap exhaust the apparent multiplex benefit; appropriate ordinary scheduling, demixing and priors explain any gain.
- Discriminator: response error and interval coverage on untouched single-input history probes, comparing optimized multiplex schedules with optimized single-target schedules under the same permissible actions, observations, priors and total budget. Compare a cost frontier rather than claiming simultaneously equal time and equal pulse number when infeasible.
- Positive value: a validated regime where many-input dynamic measurements become practical, with an explicit mechanism for the efficiency gain.
- Null value: identify when separate measurements suffice and specify the extra observation needed before a mechanistic plasticity claim is identifiable. A null alone does not guarantee a publishable ML paper.

No opposite-sign literature conflict is asserted: the source lane is the domain-native timing/measurement constraint. Existing calibration-transfer and learned-MC guards are unrelated and remain intact.

## Three primary anchors, bounded reading

1. [Triplett et al., CAVIaR, Nature Neuroscience (2025)](https://www.nature.com/articles/s41593-025-02053-7): selected methods and discussion. Models latent presynaptic spikes and power dependence; explicitly identifies short-term plasticity as a future problem and suggests connectivity mapping followed by single-target refinement. Its mean re-stimulation interval is N/(Rf). This is a direct parent, not a demonstrated failure.
2. [Gontier et al., ESB-BAL, PLOS Computational Biology (2023)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1011342): selected model, controller and batch sections. A depletion/replenishment IO-HMM estimates N, p, q, noise and recovery time; active timing includes time penalties and batch design. In the reported comparison, batch learning did not outperform the tailored short deterministic protocol. Both belong in the baseline set.
3. [Jackman et al., J. Neurosci. (2014)](https://doi.org/10.1523/JNEUROSCI.4694-13.2014): indexed primary abstract and selected discussion, not a full PDF review. Optical/electrical response agreement depends on synapse, expression and illumination conditions. This motivates a physical observation contract; it does not establish a deficit in modern holographic systems.

Availability links in the first two articles were seen, but repository contents, metadata manifests, traces and model payloads were not accessed. Those links do not qualify a matched truth asset. Search hits outside these three works remain intake, not additional reviewed questions.

## C1: current-only drive/release ambiguity

This is a standard restricted identifiability counterexample, not a new theorem or an observed biological result. Let the current at pulse j be Y_j=q S_j R_j, where S_j is a Bernoulli terminal-arrival event with probability a_j and R_j an independent Bernoulli release event with probability b_j. Fix q and use independence across the two pulses.

Both alternatives have (a_1,b_1)=(0.8,0.5). Alternative A has (a_2,b_2)=(0.4,0.5); alternative B has (a_2,b_2)=(0.8,0.25). Their observable event probabilities are identically (0.4,0.2). Hence the entire joint distribution of (Y_1,Y_2) is identical, including after adding the same independent recording noise. A decline in evoked response therefore does not by itself distinguish reduced terminal drive from reduced conditional release in this model class.

Observing the relevant S events distinguishes these alternatives. Somatic spikes require a separate propagation contract before serving as terminal-arrival truth. Real release dynamics can introduce informative correlations; this toy does not prove universal nonidentifiability. The narrower optical-protocol response remains a different target from intrinsic release parameters.

## C2: full histories matter even at a fixed mean interval

Assume each global trial independently selects R of N targets uniformly, at trial frequency f. For one neuron, selection probability is p=R/N and the positive waiting count J is geometric: Pr(J=j)=p(1-p)^(j-1). Therefore E[Delta]=1/(pf), where Delta=J/f.

For the illustrative exponential recovery factor, summing the geometric series gives

\[
\mathbb E[e^{-\Delta/\tau}]
=\frac{p e^{-1/(f\tau)}}{1-(1-p)e^{-1/(f\tau)}}
\geq e^{-1/(pf\tau)}.
\]

The inequality is Jensen's and is strict for 0<p<1 and finite positive f,tau. Thus two schedules with the same mean interval need not have the same mean nonlinear recovery factor. Interpreting this as a resource state additionally assumes a unit depletion reset at each relevant event; it is not a full stochastic synapse model. Target selection is not guaranteed spike arrival or depletion. This is not a criticism of the parent's stated mean-interval formula.

Retain the complete assigned and observed event histories. Neither global frequency nor mean per-input frequency alone is the matched control. This calculation establishes no advantage for history coding.

## Early truth, cost and stopping contract

Begin conceptually with a declared additive current model and known input identity. Mechanistic parameter recovery needs analytic or synthetic truth; optical response recovery needs matched single-input references. Neither benchmark is implemented or authorized here. Extra imaging/reference measurements must be offered equally to comparators and included in cost. Preparation-specific nonlinear summation, polysynaptic recruitment, drift, release variability and arrival uncertainty delimit transfer.

Required comparisons are: optimized short deterministic single-target trains; an ESB-BAL-style active timing/batch baseline; ordinary demixing with full history covariates; and history-aware multiplex design. **Single-target scheduling may interleave different inputs during recovery waits.** It must not be forced to wait idly or repeat connectivity mapping for each method. Common mapping costs are handled consistently; new mapping, calibration, optimization, training, recording, energy and reference costs are counted when incurred.

The cheapest next discriminating step is a bounded analytic design/collision review: freeze a small two-input response model and its admissible timing/observation budget; determine whether coded histories provide independent sensitivity to the target beyond optimized interleaved single-target and ordinary dynamic demixing. A local Jacobian check is a diagnostic for first-order information, not a global identifiability theorem. A successful example must explain an advantage beyond a generic active-learning composition and specify a plausible independent reference.

Park if the only benefit is avoiding artificial idle time, a weaker static comparator, extra information/priors, or generic design optimization; stop escalation if the scientific target remains ambiguous. Retaining this F1 question is not evidence of main-track readiness. Exact pulse/reference joins, rights, animal/protocol scope, untouched preparation-level confirmation, independent replication and full cost remain unqualified.

## Accounting

One source-led raw program, one quick screen, three primary works, two standard analytic controls; one provisional F1 survivor and zero F2/F3 audits, forecasts or machine cards. The two-measurement/two-intervention sampling targets are unmet in this one-question allocation; it is not a twelve-program cycle or a global source-scarcity claim.

Paper G: 87 formulations across 27 cycles, zero cards. Detailed ledger: 34 cycles/171 raw questions; inclusive history: 43 cycles/227 raw questions. Graph: 331 nodes/279 edges/1952 locators. Evidence registry: 1221 records. Candidate 1; parked 12. Prior forecasts and re-entry records are preserved. All work is internal literature/analytic screening; no scientific implementation, outcomes, simulation, training, GPU, laboratory activity, outreach, delegation or publication.
