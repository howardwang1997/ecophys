# Paper G: physical gain, latent contraction and outer-region dissipativity

PRIVATE / INTERNAL. Bounded source/theorem scope audit of the existing F1 question g31_transient_energy_gain. **Decision: not_trigger.** No new topic or cycle, F2, forecast, card, outcome access or scientific execution. The preceding turn supplied population-regularization controls; this audit checks a different named boundary, the state and metric in which stability is imposed. This is not a prospective forecast.

## Decision-relevant primary evidence

[Li et al., NeurIPS 2022, Learning Dissipative Dynamics in Chaotic Systems](https://proceedings.neurips.cc/paper_files/paper/2022/file/6ad68277e27b42c60ac228c9859fc1a2-Paper-Conference.pdf), selected §§2–3 and equations 7–9: the regularization distribution occupies an outer shell disjoint from the attractor, and post-processing blends the learned map with a dissipative safety map farther out. The relevant property is absorption into a bounded region, not contraction of every pair of physical states. The paper's sigmoid blending is not an exact identity cutoff. Its finite-horizon approximation theorem is also not a derivative-accuracy guarantee. No model was reproduced or qualified as a shear-gain benchmark.

[Provably Stable Neural Dynamics via Koopman Operator Certificates](https://openreview.net/attachment?id=mDhyb0VGJu&name=pdf), indexed primary passages from §§3.2–3.3, assumptions 4.1–4.2, remark 4.6 and §6: the latent generator has the form \(-S+A\), with positive-definite \(S\) and skew \(A\). State-space transfer is conditional on representation quality; isometric regularization encourages a lower Lipschitz bound. The text already names transient-growth limitations of the identity metric and suggests a learned metric. An earlier anonymous version explicitly describes unit spectral normalization of encoder/decoder layers. The indexed later manuscript names Aryan Dadwal and DEMO@ICML 2026; this is a workshop designation, not ICML main. These are versions of one work, not independent evidence. Full current PDF bytes, complete implementation, actual global Lipschitz constants and the current review decision were not verified. Claims here use only inspected primary passages.

Thus neither dissipative operator learning nor stable latent dynamics implies the physical nonexpansiveness premise of cycle31's lower bound. The latter architecture's complete representation constraints need inspection before applying that bound. The generic learned-metric repair is already a named parent idea.

## Three exact scope controls

### 1. The same physical shear admits a contracting latent realization

For the established two-mode physical generator
\[
H=\begin{pmatrix}-a&S\\0&-a\end{pmatrix},\qquad a>0,
\]
direct multiplication gives
\[
P=\begin{pmatrix}
1/(2a)&S/(4a^2)\\
S/(4a^2)&1/(2a)+S^2/(4a^3)
\end{pmatrix},\qquad H^\top P+PH=-I.
\]
Its leading principal minor is positive and
\(\det P=1/(4a^2)+S^2/(16a^4)>0\), so \(P\succ0\).
The invertible encoder \(z=P^{1/2}q\) gives
\[
\dot z=Bz,\quad B=P^{1/2}HP^{-1/2},\qquad
B+B^\top=-P^{-1}\prec0.
\]
Therefore \(B\) has exactly the form negative symmetric-positive-definite plus skew-symmetric. With decoder \(q=P^{-1/2}z\), it reconstructs the same physical trajectory and transient energy gain. In particular,
\[
\|e^{Ht}\|_2^2
\leq \kappa_2(P)\exp[-t/\lambda_{\max}(P)].
\]
The condition-number factor permits physical gain above one while latent energy contracts. This is classical Lyapunov/similarity algebra, not a new architecture or theorem. The explicit encoder is generally not an isometry, and encoder/inverse cannot simultaneously satisfy unit Lipschitz bounds when their condition-number product exceeds one. This example does not assert membership in an architecture imposing those additional bounds.

### 2. The complete encoder–propagator–decoder bound is decisive

Let \(F_t=D\circ K_t\circ E\), with Lipschitz constants \(L_D,L_E\) measured against the fixed physical energy norm and the specified latent norm. If
\(\operatorname{Lip}(K_t)\leq e^{-\eta t}\), then
\[
\operatorname{Lip}(F_t)\leq L_DL_Ee^{-\eta t}.
\]
At a differentiability point, the same expression bounds the derivative norm. A physical derivative gain \(G(t)\) can be represented exactly only if
\[
L_DL_E\geq e^{\eta t}\sqrt{G(t)}.
\]
If both encoder and decoder are genuinely nonexpansive, the physical obstruction applies. A latent certificate alone does not supply that premise. Per-layer spectral normalization only entails whole-network constants under the corresponding activation, skip, scaling and composition assumptions; these were not checked in executable code.

For an approximate representation, a certified derivative error \(\delta\) would give only the necessary inequality
\(\sqrt{G(t)}\leq L_DL_Ee^{-\eta t}+\delta\).
Small reconstruction-value or forward-value errors do not automatically provide \(\delta\).
The complete-map constants and a physical reference cannot be replaced by evaluating gain in a convenient learned norm.

### 3. Outer-region dissipation is compatible with local physical gain

Let \(M=e^{H\Delta}\), and choose a smooth radial cutoff \(\chi\) equal to one for \(\|q\|\leq R\) and zero for \(\|q\|\geq2R\). Define, for \(0<\gamma<1\),
\[
F(q)=\chi(\|q\|)Mq+[1-\chi(\|q\|)]\gamma q.
\]
Near zero, \(DF(0)=M\); since zero is fixed, every fixed-horizon derivative equals \(M^n\) and retains its physical gain. Outside \(2R\), the map contracts radially by \(\gamma\). Continuity bounds the image of the compact ball of radius \(2R\); choosing a larger ball containing that image gives an invariant absorbing ball. Global dissipativity therefore coexists with the exact local transient derivative.

This is an elementary illustration of the outer-region principle, not the exact sigmoid architecture or an empirical result of Li et al. Finite-amplitude trajectories can leave the inner region; exact nonlinear gain on that larger domain does not follow.

## Consequence for the existing question

| Stated property | Does it alone forbid physical transient gain? |
| --- | --- |
| Physical complete-map nonexpansiveness | Yes, in that same physical norm |
| Latent contraction | No; encoder/decoder geometry matters |
| Negative real parts of generator eigenvalues | No; nonnormal amplification remains possible |
| An absorbing set or outer-region dissipativity | No; local pair separation can grow |
| Soft Jacobian penalty | No hard conclusion; the previous population controls separate cases |

These distinctions remove an invalid comparison, not the recorded contribution blocker. The proposed stable-models-lose-amplification narrative cannot be applied to all stable or dissipative models. Conversely, an architecture that actually bounds the complete physical map remains a legitimate restricted comparator, but its elementary expressivity limitation is not a fresh contribution.

The existing question stays provisional at F1, with no authority for a full audit or experiments. Its remaining requirement is a concrete, calibrated measurement result under the actual architecture/training contract beyond classical metric transport, prior gain estimators and the already named identity-metric limitation. No such result is established here.

Stop expanding generic Lyapunov-metric, bi-Lipschitz, outer-cutoff or Koopman-certificate variants. Re-entry requires an independently useful same-estimand residual and actual proof/truth capability removing a recorded blocker. Neither a new metric example nor a different stability label suffices. The two sources do not provide a qualified new physical assignment or independent response reference.

This audit adds two primary-work records and one nonqualified trigger entry. Paper G remains at 55 formulations, 15 cycles and zero cards. Knowledge-graph status and prior terminal decisions remain unchanged. No public scientific evidence is derived from implementation or execution incidents.

## Administrative verification

Discovery and graph validators passed; protected history passed against 9d90711966256bc93eadadd406a3a9651a6ec493. Four targeted governance/graph tests passed. Original cycle31 result/question, proposal, protocol and forecast hashes remain unchanged. These are record checks, not numerical or empirical validation of the hypotheses.
