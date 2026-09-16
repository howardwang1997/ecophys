# Paper G: reward design, achieved policies and physical attribution

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

Decision: `not_trigger`. This follows the named SHAP-control result, not a new
candidate-harvesting cycle. Connection to the repository is the neural-PDE
response/control branch: separate the benefit of a training intervention from
identification of a physical mechanism. No Paper D outcome is used.

## Exact scope diagnostic

Fix a physical evaluation environment E, initial-state distribution, horizon,
objective return J_E and admissible policy class Pi. Pi includes observation,
memory, action, boundary and deployment constraints. Let pi_D and pi_S be the
achieved direct-reward and SHAP-reward policies in Pi. Assume all objective
values are finite and J_E^* = sup_{pi in Pi} J_E(pi) is finite. Define
R_E(pi) = J_E^* - J_E(pi). Then

\[
g_E = J_E(\pi_S)-J_E(\pi_D)
    = R_E(\pi_D)-R_E(\pi_S) \le R_E(\pi_D).
\]

Proof: subtract the two definitions and use nonnegative regret. The supremum
need not be attained. This holds for decentralized or history-dependent
controllers too, provided the comparison uses the same Pi; no local observation
is assumed to be Markov. A positive true gap excludes global optimality of the
achieved direct-reward policy for this evaluation objective. It does not
identify why learning that policy was difficult or what the alternative reward
has physically identified. Estimated sample gaps additionally need uncertainty.

For a training environment T and evaluation environment E, use a common
deployable policy class and define d(pi)=J_E(pi)-J_T(pi). Exactly,

\[
g_E=g_T+d(\pi_S)-d(\pi_D).
\]

If R_T(pi_D) <= epsilon and |d(pi_D)|, |d(pi_S)| <= delta, then
g_E <= epsilon + 2 delta. The bounds are assumptions, not measured quantities
for the published controllers. All returns here use the same physical objective;
SHAP reward values are not subtracted from drag returns. Different channel
geometries require an explicit policy-deployment mapping before applying this
notation. No ranking reversal or training defect is asserted for the source.

## Prior and inference

[Sorg et al., NeurIPS 2010](https://proceedings.neurips.cc/paper_files/paper/2010/hash/168908dd3227b8358eababa07fcaf091-Abstract.html)
already formulates reward design for agents with limitations: a training reward
different from the designer's objective can improve achieved objective return.
Scope: official abstract and indexed introduction; its convergence proof was
not audited. This establishes a generic parent, not the cause of the turbulence
result.

[Beneitez et al., arXiv2504.02354v2](https://arxiv.org/html/2504.02354v2)
compares learned policies and transfers from a small to a large channel. Those
are achieved-policy results, not a global-optimum comparison. Read with the
preceding IND–SHAP scope record. No new source outcome was generated or accessed.

## Decision and next evidence

The standard identities and generic reward-design interpretation remove no
novelty blocker. Better control and better identification of a specific mechanism
are separate claims; reward learning can exploit physical structure, so they
are not mutually exclusive explanations. More training seeds or matched budget
alone would not establish a mechanism either.

Stop this generic claim chain. Re-entry requires a specified physical response
prediction that differs between substantive explanations after reward-design
baselines, or a nonstandard theorem eliminating a recorded reduction. Any future
method claim needs a budget accounting for reward-model training and policy
selection as well as control training. No experiment is authorized here. The
overall Paper G goal remains unmet.
