# Paper G: shear-gain regularization and training-distribution scope

PRIVATE / INTERNAL. Ordinary outcome-blind re-entry capability audit of `g31_transient_energy_gain`, following the PI's direct continuation. **Decision: partial_capability, not a qualified trigger.** No F2 screen, new question, experiment, forecast or machine card. The single-use cycle31 exception remains consumed. This record was composed alongside paper reading and algebra; it is not a prospective prediction or registration.

The named blocker is the absence of a calibrated, distinct measurement contribution beyond known transient-growth diagnostics. We examine whether an exactly solvable population training problem supplies such a contribution. It strengthens a control, but does not remove that blocker. The [cycle31 result](ecomd_paper_g_topic_cycle31_2026-09-12.md) and its historical F1 deferral remain unchanged.

## Exact population training control

Keep cycle31's physical energy coordinates and restricted homogeneous-shear family. At a fixed physical step \(\Delta>0\), its exact propagator is

\[
M=e^{-a\Delta}\begin{pmatrix}1&S\Delta\\0&1\end{pmatrix},
\qquad a=\nu k^2>0.
\]

We fit a **linear** map \(J\) to noiseless pairs \(x\mapsto Mx\), where \(x\) is zero-mean with positive-definite second moment \(\Sigma\). The stipulated objective is

\[
\mathcal L(J)=\mathbb E\|Jx-Mx\|_2^2+\lambda\|J\|_F^2,
\qquad\lambda>0.
\]

The Hessian in each row is positive definite. Setting its gradient to zero gives the unique global optimum

\[
J_\lambda=M\Sigma(\Sigma+\lambda I)^{-1}=MC,
\qquad 0\prec C\prec I.
\]

This is elementary ridge regression. It is also exactly the risk obtained by corrupting the **input only** with independent, zero-mean noise of covariance \(\lambda I\), retaining the uncorrupted target \(Mx\). The cross term vanishes. Corrupting both input and target according to the physical dynamics is a different training contract. The exact linear equality here does not extend without remainder to arbitrary nonlinear networks.

In this noiseless, fully excited linear population problem, **unregularized least squares already recovers \(M\) exactly**, with zero prediction error, correct gain and asymptotic stability. The positive penalty is therefore a biased control by construction, not a demonstrated useful stability–accuracy trade-off. Practical benefit would require a separately specified finite-data, noise, model-class or optimization regime. This reference cannot establish superiority over an actual neural training procedure.

### Isotropic excitation: gain loss without loss of shear coupling

If \(\Sigma=\sigma^2 I\), then \(C=cI\), \(c=\sigma^2/(\sigma^2+\lambda)\), and

\[
J_\lambda^n=c^nM^n,\qquad
G_{J_\lambda}(n\Delta)=c^{2n}G_M(n\Delta).
\]

For this exact family, the effective generator is

\[
\frac{\log J_\lambda}{\Delta}
=\begin{pmatrix}-a&S\\0&-a\end{pmatrix}
+\frac{\log c}{\Delta}I.
\]

The shear coefficient \(S\) is unchanged. The fitted system has additional uniform damping \(-\log(c)/\Delta\), which can remove net energy amplification despite preserving the shear-coupling term. Thus lower raw gain alone cannot establish that the shear mechanism was erased. Within this two-dimensional family, \(G(J^n)/|\det J^n|=G(M^n)/|\det M^n|\); this is a supplementary algebraic control, not a replacement for the physically relevant energy gain or a proposed universal normalization.

The population unpenalized prediction risk satisfies

\[
R(J_\lambda)/\mathbb E\|Mx\|^2=(1-c)^2.
\]

Consequently a small relative one-step error can coexist with a substantial accumulated gain reduction over many steps. These statements concern the specified population minimizer, not an observed neural-network training result.

### Anisotropic excitation: the same penalty can produce instability

Set \(e^{-a\Delta}=1/2\), \(S\Delta=6\), and \(\lambda=1\). These are legal positive-viscosity shear controls. Fix the physical operator

\[
M=\begin{pmatrix}1/2&3\\0&1/2\end{pmatrix},\qquad\rho(M)=1/2.
\]

Choose two training second moments, with the **same eigenvalues \(3,1/3\)**, trace and conditioning:

\[
\Sigma_\pm=\begin{pmatrix}5/3&\pm4/3\\\pm4/3&5/3\end{pmatrix},\qquad
C_\pm=\begin{pmatrix}1/2&\pm1/4\\\pm1/4&1/2\end{pmatrix}.
\]

Both input distributions can have arbitrarily small bounded physical amplitudes after scaling \(\Sigma\) and \(\lambda\) by the same positive factor; their ratio and the following optimizers are unchanged. They need not introduce observation noise, omitted state or numerical error.

For the plus orientation,

\[
J_+=\begin{pmatrix}1&13/8\\1/8&1/4\end{pmatrix},\qquad
\operatorname{spec}(J_+)=\{(5+\sqrt{22})/8,(5-\sqrt{22})/8\}.
\]

The first eigenvalue exceeds one. For the minus orientation,

\[
J_-=\begin{pmatrix}-1/2&11/8\\-1/8&1/4\end{pmatrix},\qquad
\operatorname{spec}(J_-)=\{(-1+i\sqrt2)/8,(-1-i\sqrt2)/8\},
\]

whose spectral radius is \(\sqrt3/8<1\). Each one-step norm still obeys (\|MC_\pm\|_2\leq\|M\|_2\). Reducing that norm relative to the nonnormal reference does not guarantee asymptotic stability. The two cases share the underlying physical dynamics and penalty; **changing the orientation of the actual training ensemble** changes the learned operator. Rotating coordinates while transporting the physical dynamics, covariance and metrics would instead preserve predictions.

This is an estimator-conditioning control, not a new fluid instability or representation-independent physical law. It disproves a universal inference that this soft regularizer necessarily makes the learned dynamics stable or only suppresses their long-horizon amplification. It does not contradict a method with an additional verified stability constraint. No numerical fit was run; the matrix products, determinants and roots above are paper-only algebra.

## What calibration follows, and what does not

For a finite-time linear propagator \(N\), write \(G(N)=\|N\|_2^2\).

For a **linear** comparison \(D=J-M\), suppose a population prediction-risk bound \(R(J)=\operatorname{tr}(D\Sigma D^\top)\leq\epsilon^2\) is available and \(\lambda_{\min}(\Sigma)\geq m>0\). Then

\[
\|D\|_2\leq\|D\|_F\leq\epsilon/\sqrt m,
\qquad
|\sqrt{G(J)}-\sqrt{G(M)}|\leq\epsilon/\sqrt m.
\]

At a fixed integer horizon, the elementary telescoping identity gives

\[
\|J^n-M^n\|_2\leq\|J-M\|_2
\sum_{j=0}^{n-1}\|J\|_2^{n-1-j}\|M\|_2^j.
\]

These are conditional deterministic controls. A training-set error is not automatically the stipulated population bound. The covariance lower bound quantifies coverage of physical input directions; a scalar conditioning number does not determine the sign of the regularization effect. A nonlinear surrogate's state prediction risk does not by itself bound its derivative. Finite-sample confidence, nonlinear remainder, independent numerical reference error and generalization outside this two-mode family remain unqualified. No confidence level or coverage claim is assigned.

## Minimal primary-work check

- [Bishop, 1995, author-hosted paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/bishop-tikhonov-nc-95.pdf), selected §§1–3: derivative-based Tikhonov regularization and input-noise training are established parents. The nonlinear result uses a small-noise argument; our exact linear specialization is not a new noise-regularization principle.
- [Wang and Mao, arXiv:2509.18974v1](https://arxiv.org/html/2509.18974v1), abstract/introduction: a second author lineage already estimates optimal perturbations and gain from snapshots without constructing an adjoint, including multiple horizons. This rules out pitching generic adjoint-free or multi-horizon gain diagnostics as the increment. No complete algorithm, noise-calibration or independent replication audit was performed.
- [On the Surprising Effectiveness of Spectrum Clipping in Learning Stable Linear Dynamics, v1](https://arxiv.org/html/2412.01168v1), selected §§2–3: stable linear identification and eigenvalue-based corrections are existing method comparators. Spectral-radius control is different from singular-value contraction. Its numerical realization and applicability to the present defective Jordan family were not qualified here. We do not infer an observed failure or a ready implementation from this reading.

The previously registered [JAWS §3.3](https://arxiv.org/html/2603.05538v1) learns spatially varying penalty weights jointly with its predictor. The uniform, fixed-λ linear objective above is a deliberately explicit control, **not a solved model of JAWS training**. Existing Kai–Frame–Towne gain estimation remains a mandatory comparator. Neither prior author's claims nor uninspected experiments are refuted by the population control.

## Re-entry decision and stop

The gain question is better specified after this audit: a convincing measurement must distinguish ordinary damping bias, ensemble-dependent operator distortion and the true physical gain, under the actual training contract. The exact counterexample prevents assuming the answer is always downward suppression. It provides no new measurement algorithm, finite-sample result, trained-model finding or transfer evidence.

The proposed capability therefore remains **partial**. No recorded independent-contribution or calibrated-general-response blocker is removed; no qualified trigger or F2 authorization is issued. Retain the existing F1 question as provisional, without changing its original cycle disposition. Stop generic ridge, covariance-rotation and transient-growth citation variants as topic generators. Re-entry needs a concrete same-estimand residual beyond these controls and the named parents, with an outcome-blind proof or qualified truth capability; another elementary example alone is insufficient.

This session adds three primary-work records and two internal audit documents, one trigger audit and zero questions/cycles/cards. No data/model payload, scientific implementation, simulation, GPU, purchase, participant activity, outreach or delegation occurred. All controls are development paper-only assets, not public confirmatory evidence. The ICML-main/NMI/NCS objective remains unmet.

## Administrative validation

Discovery governance, route graph and protected-history validation passed against `9d90711966256bc93eadadd406a3a9651a6ec493`. Four targeted governance/graph tests passed. These are record checks, not numerical verification or scientific experiments.
