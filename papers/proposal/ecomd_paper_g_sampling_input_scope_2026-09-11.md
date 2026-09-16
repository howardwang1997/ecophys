# Paper G: sampling rate, known inputs and response identification

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

Decision: retain a conditional response-estimation baseline; no qualified
re-entry. This source comparison refines the observation contract of the
closed physical-history-response route, connected to the repository's learned
PDE and stochastic-dynamics work. It creates no new question program or method.

## Selected primary results

[Yue, Thunberg and Goncalves, arXiv1605.06973v1](https://arxiv.org/pdf/1605.06973),
May 23, 2016: selected extracted text, Definition 5 and Section III-A/Theorem 4.
The previous registry record covered only the abstract. Their system-aliasing
problem concerns recovering a continuous-time matrix from its exponential.
The principal-logarithm argument requires its spectral-strip and branch
conditions. A safely interior strip is
`|Im(lambda(A))| < pi/h`. The statement is conditional on the candidate class
and available matrix information; it is not a universal impossibility theorem
for every experiment performed at interval `h`. No full proof audit or visual
PDF verification is claimed here.

[Gonzalez, van Haren, Oomen and Rojas, arXiv2410.19629v1](https://arxiv.org/html/2410.19629v1),
October 25, 2024: selected Sections II–III, Theorems III.1–III.2 and Remark III.1.
They study stable SISO linear systems with perfectly known continuous multisine
input, no intervening hold device, settled transients, and iid zero-mean output
noise. With at least `2M+1` samples for `M` positive excitation frequencies,
distinct sampled frequency lines give an unbiased least-squares response estimate,
including above Nyquist. Its covariance is `sigma^2 Z^(-1)`, with `Z` the
input-regressor Gram matrix. Their stronger diagonal-covariance simplification
also requires the specified no-leakage condition. This is a driven-experiment
result, not recovery of unknown input histories from passive trajectories.

## What changes in the selection contract

The two results concern different available information. Known continuous input
adds information absent from a single autonomous transition matrix. Their
conclusions are therefore compatible; they supply no matched primary-model
disagreement for a new Paper G.

Retain four distinctions when evaluating a future physical response question:

1. Exact uniqueness depends on the input and model class, not just an output
   sampling interval. Do not apply the passive alias control as a blanket veto.
2. A commanded waveform is usable here only when its actual action and timing
   are established. A sampled command list does not establish its intersample
   waveform or remove a hold device.
3. Invertibility of `Z` is not a precision guarantee. Its conditioning, input
   amplitudes and output-noise assumptions determine the reported covariance.
4. Compare both sample count and elapsed physical time. Holding sample count
   fixed while increasing the interval changes the experiment duration. The
   no-leakage result does not establish a universal cost-free sampling benefit.

These are source-based comparison requirements and elementary consequences,
not new theorems. No timing-jitter estimator, minimax rate, new counterexample
or learned-model failure is claimed. No nonlinear, partially observed,
state-dependent-noise or arbitrary PDE extension has been qualified.

The existing generic-sensitivity and generic-forced-response contribution
blockers remain. Changing the observation clock or naming an above-Nyquist
response task is insufficient novelty. Stop generic sampling remedies from
this source chain; any future re-entry needs a substantive native result or
truth/control asset that removes a recorded blocker. The ICML/NMI/NCS Paper G
selection objective is still unmet.

Related records:
[history-response closure](ecomd_paper_g_history_response_resolution_2026-09-09.md),
[Koopman/actuation scope](ecomd_paper_g_koopman_actuation_scope_2026-09-11.md).
