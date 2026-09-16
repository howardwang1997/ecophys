# Paper G: bounded adjudication of the transient-gain measurement formulation

PRIVATE / INTERNAL. Outcome-blind F2 adjudication of the existing g31_transient_energy_gain question. Opened at 2026-09-12T06:51:02Z under the [one-use PI decision](../../research/discovery/decisions/pi_paper_g_bounded_f2_exception_20260912.yaml), following the direct user instruction “继续”. This is one follow-up adjudication, not a new search cycle, an experiment, or a full fifteen-work audit.

**Decision: failed_closed at the distinct calibrated contribution gate.** The supplied generic measurement formulation does not provide an increment beyond existing transient-growth analysis and elementary error propagation. This closes this formulation; it does not establish absence of response distortion in trained models or rule out a future substantive physical-response result.

## Frozen question and competing explanations

For the previously defined homogeneous-shear system, fix the physical perturbation family, kinetic-energy norm, shear S, viscosity, wavenumber, base state and horizon t. The proposed comparison is whether a named stabilization procedure changes physical finite-time gain beyond calibrated uncertainty at matched information and total cost.

The rival explanations remain: a procedure introduces extra damping or otherwise changes the physical response; alternatively, the apparent difference is accounted for by the estimator, excitation coverage, representation geometry or unmatched training information. A positive result would need a specific mechanism and meaningful regime. A null would need a predeclared distortion bound strong enough to affect model selection. Neither is supplied by an arbitrary bad surrogate or an uncalibrated gain comparison.

## Direct prior-work comparison

Six already registered works anchor the adjudication; three texts were revisited or expanded this session. No new primary work was added. The last three rows use the previously recorded selected-text scope, not a fresh full-text audit.

| Primary work | Relevant contribution or contract | Consequence for this formulation |
| --- | --- | --- |
| [Kai, Frame and Towne, v1, §§2–3](https://arxiv.org/html/2507.02525v1) | Estimates energy-weighted optimal gain and input/output modes from paired states; its optimization is restricted to the input-data span and includes a noise regularizer | The central diagnostic and its subspace boundary are already explicit |
| [Wang and Mao, v1, §3.2](https://arxiv.org/html/2509.18974v1) | Constructs a reduced propagator from evolved snapshot pairs, with a transported energy metric; collecting intermediate outputs supports multiple horizons | A second author lineage already supplies a data-driven operator/gain comparator; reduced-space coverage remains an assumption |
| [JAWS, v1, §3.3, Eq.6](https://arxiv.org/html/2603.05538v1) | Uses learned spatial tolerances in a soft Jacobian-Frobenius penalty | A hard complete-map contraction premise is not established by this objective; a sign of shear-gain bias cannot be deduced from the method label |
| [Bishop, 1995](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/bishop-tikhonov-nc-95.pdf) | Derivative regularization and small-input-noise connection | The earlier exact linear noise/ridge specialization does not create a new regularization principle |
| [Li et al., NeurIPS 2022, §§2–3](https://proceedings.neurips.cc/paper_files/paper/2022/file/6ad68277e27b42c60ac228c9859fc1a2-Paper-Conference.pdf) | Outer-region dissipativity and an absorbing-region construction | Stability need not remove local physical amplification |
| [Koopman certificates, selected indexed manuscript passages](https://openreview.net/attachment?id=mDhyb0VGJu&name=pdf) | Latent contraction with conditional representation transfer; a metric limitation is already discussed | Latent contraction alone is not the proposed physical obstruction; workshop/version and full-text limitations from the prior audit remain |

These works need not have tested the same trained shear surrogate for the generic method contribution to fail. Their existence does not settle the actual empirical comparison. The decision is that the supplied formulation has not specified a substantive increment in theorem, estimator or calibrated physical result.

## Paper-only check 1: the entire supplied truth family is recovered by the paired-data baseline

In the existing two-mode family, write q=(A,B) and
\[
q_t=M(t)q_0,\qquad
M(t)=e^{-at}\begin{pmatrix}1&St\\0&1\end{pmatrix},
\qquad E(q)=\tfrac14\|q\|_2^2.
\]
Choose two linearly independent admitted initial perturbations as columns of an invertible 2-by-2 matrix X. The exact paired responses are Y=M(t)X. Then
\[
YX^{-1}=M(t),\qquad
\max_{c\ne0}\frac{\|Yc\|_2^2}{\|Xc\|_2^2}
=\|M(t)\|_2^2=G(t).
\]
The proof is substitution, with Xc ranging over the complete admitted family. This is the full-span specialization of existing paired-data identification and gain optimization. It recovers both gain and maximizing disturbances, with no stabilization penalty required in the noiseless reference.

If the input span is smaller, the optimization answers a restricted question. If an estimator uses a positive denominator regularizer, that changes its finite-data objective. Neither is a physical suppression result. All compared methods must receive the same admissible response information, and its acquisition cost must be included; two exact pairs do not describe the training cost of an arbitrary neural surrogate.

**Implication:** the available exact truth is useful as a regression/reference asset, but the noiseless full-span measurement problem within this family is already solved by the baseline. There is no deduction here about general PDE perturbations, finite-sample learning, or nonlinear neural response.

## Paper-only check 2: conditional calibration reduces to ordinary operator perturbation

Continue with this real, finite-dimensional, fixed-energy coordinate system. Suppose the observed matrices are
\[
\widetilde X=X+E_X,\qquad \widetilde Y=MX+E_Y,
\qquad \widehat M=\widetilde Y\widetilde X^{-1}.
\]
Let s be the smallest singular value of X and assume
\(\|E_X\|_2\le\epsilon_X<s\), \(\|E_Y\|_2\le\epsilon_Y\).
Then
\[
\widehat M-M=(E_Y-ME_X)\widetilde X^{-1},\qquad
\|\widehat M-M\|_2
\le\frac{\epsilon_Y+\|M\|_2\epsilon_X}{s-\epsilon_X}
 \equiv\delta.
\]
This follows from the reverse triangle inequality for the smallest singular value and submultiplicativity. If X is exact, it reduces to \(\delta=\epsilon_Y/s\). With input uncertainty, a usable numerical certificate also needs known bounds on s and \(\|M\|_2\); a fitted residual does not supply them.

For any independently certified operator bound \(\|\widehat M-M\|_2\le\delta\),
\[
|\sqrt{\widehat G}-\sqrt G|\le\delta,\qquad
|\widehat G-G|\le\delta(2\|M\|_2+\delta).
\]
An achieved-energy decision can also be bounded without identifying a unique singular vector. Let \(\widehat v\) be any unit maximizer for \(\widehat M\). Define
\(\eta=\delta(2\|M\|_2+\delta)\). Since
\(\|\widehat M^\top\widehat M-M^\top M\|_2\le\eta\),
comparison of the two quadratic objectives at their respective maximizers gives
\[
0\le G-\|M\widehat v\|_2^2\le2\eta.
\]
The intermediate predicted-objective difference is nonpositive by optimality of \(\widehat v\); each of the other two differences is at most \(\eta\). This controls achieved energy, not the angle of a particular mode in a degenerate singular subspace.

These are deterministic elementary controls, not a new confidence procedure or theorem contribution. Statistical coverage requires an independently justified error event; nonlinear use requires a derivative and truncation-error contract. Those capabilities are absent here. Extending the formula without providing them does not remove the calibration blocker.

## Four required decisions

| Gate | Result | Reason |
| --- | --- | --- |
| Specific independent contribution | Fail for supplied formulation | Applying a known gain diagnostic to stable surrogates does not yet identify a new result; the exact family is already fully handled by the baseline |
| Precise prior-art difference | Fail for generic estimator/bound claim | Paired-data gain analysis, metric transport and the above perturbation controls cover the supplied method ingredients |
| Separation from rival explanations | Necessary controls specified; not empirically established | Preserve exact unregularized recovery, ordinary damping, covariance orientation, physical versus latent norm, and outer dissipation controls; no matched trained-model effect has been observed |
| Calibrated correct answer | Pass only for restricted noiseless two-mode truth; broader claim unqualified | General nonlinear derivative coverage, measurement uncertainty and external truth are not supplied by this family |

Stop at these hard contribution failures. The unused allowance for additional papers is not a reason to continue the citation chain. No second new question, F3 forecast or machine card follows.

## Preservation, scope and reopening

Retain the exact shear reference, population damping/covariance controls, Lyapunov transport and outer-dissipation examples, full-span baseline identity, and conditional perturbation/achieved-energy bounds as private reusable analysis assets. They are not independent confirmations or novel physical findings.

The current closure does not answer whether a particular trained neural architecture distorts physical response. It also does not reject every empirical paper using established diagnostics: a consequential and well-controlled empirical finding could be substantive. No such finding or currently qualified truth/control asset is established in this adjudication.

Reopening requires a concrete same-estimand result or new truth/control capability that removes a named contribution or calibration blocker, followed by a validated re-entry decision. Merely changing the regularizer, metric, flow name, horizon or target venue is insufficient. The one-use process exception is consumed. Scientific implementation, outcomes, compute, delegation and publication remain unauthorized.

The structured [resolution receipt](../../research/paper_g/gain_f2_resolution_20260912.yaml) records the exact historical hashes, selected evidence scope and budget. The original cycle31 report, question screen, approval proposals and decisions are preserved. A separate follow-up pointer in the search ledger leaves original cycle-stage counts intact; the route graph records the terminal status. Paper G remains 55 recorded formulations over 15 cycles, with zero cards. No publication probability or field-exhaustion claim is inferred.

Administrative verification completed at 2026-09-12T07:00:01Z, within nine conservative wall minutes of the 45-minute allowance. Discovery and graph validators, protected history, four targeted tests, original-artifact hashes and the scoped whitespace check passed. These checks validate the records; they are not scientific or empirical confirmation.
