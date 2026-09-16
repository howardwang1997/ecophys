# Paper G: synaptic history-design review

PRIVATE / INTERNAL. 2026-09-14 NZ. Bounded follow-up to Cycle43; no new question, search cycle, full F2/F3 audit, forecast, machine card or scientific execution.

**Decision: park g43_synaptic_history_coded_measurement nonterminally.** The question remains scientifically possible, but a concrete information/cost advantage attributable to a new learning or design method is unqualified. Two ordinary analytic controls delimit the proposed mechanism. Neither is a universal no-multiplexing theorem or an observed physiological failure.

## Contribution comparison

- [Rossbroich et al. (2021), Linear-nonlinear cascades capture synaptic dynamics](https://doi.org/10.1371/journal.pcbi.1008013), selected deterministic model and inference sections: SRP uses spike-history kernels, nonlinear efficacy and variability models, with likelihood fitting from naturalistic input patterns. Kernel basis timescales are not automatically biological mechanism timescales. Thus a learned history-dependent response model is an existing comparator.
- [Chen et al. (2025), High-throughput synaptic connectivity mapping using in vivo two-photon holographic optogenetics and compressive sensing](https://doi.org/10.1038/s41593-025-02024-y), selected stimulation, reconstruction and discussion: random balanced multi-target patterns and sparse reconstruction are already physical measurement tools. The mapping protocol avoids rapid repeated stimulation that might induce short-term plasticity. Its observed multi-input summation need not be exactly linear. Connectivity labels and history-dependent individual response amplitudes are different validation targets.
- [CAVIaR (2025)](https://doi.org/10.1038/s41593-025-02053-7), existing source deepened for continuous trace/demixing and timing: overlapping waveforms and stochastic presynaptic activation already enter the parent method. A static regression on commanded laser targets is an inadequate sole comparator.
- [ESB-BAL (2023)](https://doi.org/10.1371/journal.pcbi.1011342), existing batch/time sections revisited: optimizing future stimulus batches and accounting for elapsed experimental time are existing contributions. The tailored short deterministic protocol remains a required comparator.

Two new primary works plus two reading-depth records; five unique primary works for the route including Cycle43's optical observation anchor. Other search hits were intake only. Availability links were seen in articles, but no external repository manifests, outcomes, traces or model payloads were opened. The two mapping papers concern different preparations and do not constitute a matched contradiction about plasticity recovery.

## R1: records, pulses and individual-parameter information are different budgets

Assume two unknown fixed response amplitudes theta_1,theta_2, known commanded-to-arrival correspondence, exact linear summation, and independent Gaussian recording noise with known variance sigma^2 per scalar observation. There is no shared prior, unknown baseline, release noise, drift, saturation or unknown history state. For a binary design X, let n_i count pulses applied to input i and m count simultaneous observations. Then

\[
I(\theta)=\sigma^{-2}X^T X
=\sigma^{-2}\begin{pmatrix}n_1&m\\m&n_2\end{pmatrix}.
\]

If n_1 n_2>m^2, least squares attains covariance

\[
\operatorname{Cov}(\hat\theta)
=\frac{\sigma^2}{n_1n_2-m^2}
\begin{pmatrix}n_2&-m\\-m&n_1\end{pmatrix}.
\]

For fixed n_1,n_2, each diagonal variance is at least sigma^2/n_i, attained by isolated measurements (m=0). Repeating only the joint pattern gives rank one: distinct codes can restore identifiability, but that is ordinary design rank, not yet a special learning contribution. This is not a Loewner ordering of the entire information matrix: information about the sum and difference can trade off, whereas this question targets individual responses.

An exact example uses patterns (1,0),(0,1),(1,1). It spends four input-pulses in three records and gives variance 2 sigma^2/3 for each amplitude. Four isolated records, two per input, spend the same four pulses and give sigma^2/2 each: the joint design has a 4/3 variance penalty but uses fewer records. At only three records, a single-target design with counts (2,1) has total variance 3 sigma^2/2, versus 4 sigma^2/3 for the joint design, which spends an additional pulse. These are different resource allocations, not conflicting conclusions.

For known input histories in a locally differentiable additive response model, the same issue appears in block form. Write the local Fisher matrix as [[A,C],[C^T,B]], with B positive definite. Information for the first parameter block with the second unknown is A-C B^{-1} C^T, no greater than A. If isolated measurements can reproduce the same sensitivities and noise, they supply A without this nuisance subtraction. This conditional statement does not prove that identical histories can be scheduled within the same deadline, that isolated recordings have identical noise, or that a local sensitivity test establishes global identifiability. Unknown arrival/release states, parameter-dependent variance, informative priors, network effects and a different target require a separate analysis.

## R2: a recovery wait is not necessarily idle instrument time

Take two time-homogeneous, independent input systems. Each requires one pulse every Delta, and each pulse occupies an ideal nonoverlapping instrument/response window of width w. Suppose Delta>=2w. Schedule input 1 at k Delta and input 2 at k Delta+Delta/2. Both retain their own interval Delta, while a single-target instrument records alternating inputs with no overlapping windows. The second input's start is shifted by Delta/2; with suitable initial preparation, both retain the same within-input history. For L pulses per input, this changes the finite run span by a startup/end offset, not by a factor of two; the steady combined event rate is 2/Delta.

This elementary schedule refutes the necessity of waiting idly for each input to recover. It does not show that every burst schedule is packable. Dense intra-burst timing, long waveform tails, refractory instrument switching, phototoxicity, nonstationary state or common network effects can prevent the construction. The compact response window and independent time-homogeneous state are explicit toy assumptions, not measured properties of either source preparation.

A plausible surviving benefit therefore needs an actual timing or observation bottleneck, quantified under a capable schedule, plus an explanation of why the proposed learning/design method improves its cost/error frontier. Higher physical parallelism alone is already known and does not identify that method contribution.

## Scientific disposition and useful residue

The cheapest checks have not supplied a specific coded-history construction that beats a capable history model, ordinary dynamic demixing and optimized interleaved single-target design under a declared physical budget. Nor has the selected literature qualified matched multiplex/single-input dynamic truth with terminal-arrival control and untouched independent confirmation. This warrants parking the formulation, not asserting biological impossibility or requiring every empirical paper to prove a new theorem.

Reconsider if a concrete construction or primary mechanism result establishes a distinct information/cost regime, or a matched truth/control asset removes a named blocker. The construction must state its target, preparation, full input history, observation and noise model, admissible scheduling and resource frontier; empirical learning gains remain eligible. Do not reopen through a new neural architecture, renamed brain region, or an isolated availability link. This single reviewed cycle does not saturate all synaptic ML or all experimental design.

Reusable assets: the fixed-pulse versus fixed-record two-input control, local nuisance-information scope, and explicit interleaved recovery schedule. These are standard analytic controls, not new scientific findings. Cycle43's original candidate disposition remains historical; this review governs current status.

## Records and limits

No new formulation or cycle. Paper G87/27/0; detailed ledger34/171; inclusive43/227. Graph331/279/1960; evidence1225; candidate0/parked13. Original cycles, other route nodes, forecasts and re-entry decisions preserved. No outcome payload, scientific code, simulation, training, GPU, laboratory activity, outreach, purchases, delegation or publication. Broad ICLR/ICML topic-discovery goal remains incomplete. Next work should seek another unsaturated native scientific obstruction unless contribution-changing support for this candidate arrives.
