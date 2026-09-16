# Paper G: bounded review of the KA cage-sampling candidate

PRIVATE / INTERNAL. Existing candidate `g38_ka_cage_assisted_swap`; follow-up to Cycle38, not a new discovery cycle. Two already-intaken primary works were read more deeply; zero new primary works, scientific runs or outcomes. This is a bounded methods/contribution review, not a completed F2 or F3 audit.

**Decision: park nonterminally.** The two papers do not directly settle original-binary KA cage-assisted sampling. They do clarify that our present proposal still lacks a concrete mechanism for economical movement between physical structures. “Learn a larger collective proposal and apply an exact correction” remains an existing methodological direction, not an established new contribution. The underlying physical question is unresolved, not disproved.

## What the two works actually establish

**Jung, Biroli and Berthier (2024).** The main benchmark is a two-dimensional ternary liquid with 43 particles, with a larger-system appendix. An equivariant continuous flow maps high-temperature configurations toward a colder distribution, followed by importance weighting. Appendix A describes small movements within cages. Specific heat and energy are benchmarked against swap sampling; input-configuration generation is explicitly charged in their timing convention. The paper also discusses flow/MC hybrids. This is neither a demonstrated original-binary KA sampler nor a frozen-exterior, spatially bounded conditional block kernel. Its learned within-cage mapping and existing benchmark already occupy the generic cooling/correctness motivation. [Primary text: II, IV, V and Appendix A](https://arxiv.org/html/2404.09914v2).

**Parmar, Guiselin and Berthier (2020).** KA1 introduces interpolating particle types. Section III reweights its configurations toward a corresponding binary Hamiltonian, using umbrella windows to obtain overlap. The authors report that their equilibrium route encounters a near-KA equilibration bottleneck and yields no computational advantage. Section IV instead relaxes the equilibrium requirement and anneals stable configurations into binary KA glasses, comparing similar CPU effort. This is a useful preparation method, not a low-temperature equilibrium oracle for our proposal. Its result does not prove that every transport or expanded-ensemble algorithm must fail. Exact particle counts and final composition also belong in any matched comparison. [Author PDF: II–IV](https://ludovicberthier.github.io/divers/5.0020208.pdf).

| Comparison dimension | Jung flow | Parmar routes | Current candidate's unresolved requirement |
| --- | --- | --- | --- |
| Target | Two-dimensional ternary liquid | KA1 intermediates; corresponding binary endpoint | One fixed original-binary target with matched size/composition |
| Operation | High-to-low temperature flow and weighting | Equilibrium umbrella/reweighting, or nonequilibrium annealing | Valid conditional cage proposal and reverse support |
| Useful output | Equilibrium-observable estimates in tested regime | Equilibrium estimates where feasible, or stable glass preparation | Genuine physical-structure decorrelation at the declared equilibrium target |
| Missing inference | Does not establish binary-KA performance | Stable endpoint does not establish equilibrium sampling | Neither difference by itself establishes novelty or speedup |

The earlier PGMC and collective VAE-MC anchors remain direct parents, and ghost-particle relaxation remains an environmental-relaxation baseline; see the [Cycle38 record](ecomd_paper_g_topic_cycle38_2026-09-13.md). None is excluded because its parameterization differs from the proposed learner. No new broad literature neighborhood was opened.

## Two analytic controls on the claimed advantage

**R1 — physical transition rate, not accepted index motion.** Quotient out simultaneous species/coordinate relabelings as in Cycle38. Consider two distinct physical structures with equal equilibrium probability and transition matrix

\[
P_r=\begin{pmatrix}1-r&r\\r&1-r\end{pmatrix},\qquad 0<r\leq\tfrac12.
\]

For the centered structure indicator, the lag correlation is `(1−2r)^k`, hence the asymptotic variance inflation is

\[
\tau=1+2\sum_{k\geq1}(1-2r)^k=(1-r)/r.
\]

Accepted within-structure or relabeling moves can make total acceptance one while leaving `r` arbitrarily small. If useful proposals occur with probability `ε` and cross with conditional probability `p`, this example has `r=εp`. Better local fitting need not change `r`. This is a standard two-state counterexample, not a KA model or a new theorem.

**R2 — current-cost break-even.** For the same equilibrium observable and an asymptotic target of `M` effective samples, let `F_j` be setup/training/equilibration costs and `c_j` the cost per production step of sampler `j`. With finite autocorrelation factor `τ_j`, the leading cost is

\[
C_j(M)\simeq F_j+M c_j\tau_j.
\]

If the learner has extra setup cost `ΔF≥0`, it wins only if `d=c_Bτ_B−c_Lτ_L>0` and `M>ΔF/d` (strict advantage). In a hand example, baseline `r_B=0.1,c_B=1` costs 9 per effective sample. A learner with twice the crossing probability `r_L=0.2` but `c_L=4` costs 16 before setup: faster crossing per step still loses. At `c_L=1`, its production cost is 4; with extra setup 100, break-even is `M=20` and strict benefit requires more. These are illustrative unitless costs, not measurements. Nonstationary finite-run error, reference uncertainty and observable dependence still need separate checks.

These controls narrow the required evidence. They do not establish an impossibility result for learned sampling, a new efficiency metric, or a publication claim.

## Why park and what would justify returning

We now know the two closest benchmark/preparation works have different target contracts. We still have no specified proposal that demonstrably changes physical cage structure at useful cost, no learnability or rate argument beyond standard MCMC, and no qualified low-temperature reference for that claim. Merely making the block larger or replacing the flow architecture does not resolve these gaps. An empirical contribution could suffice without a new theorem, but its distinctive hypothesis and decisive comparison must be concrete first.

Return only for a contribution-changing result: an explicit reversible block construction with nontrivial physical transitions and a justified locality/cost mechanism; a directly relevant primary result exposing a matched unresolved mechanism; or a truth/control capability that actually removes a named blocker. More metadata alone is insufficient. Any scientific implementation or outcome access requires a separate current machine decision. This review creates no re-entry trigger and does not declare all learned equilibrium sampling saturated.

Stop this candidate's routine literature expansion. The next general discovery allocation should start from a different unsaturated native scientific obstruction, or the concrete trigger above. Preserve Cycle38's original F1 decision and counts: Paper G **82 formulations / 22 cycles / 0 cards**; this review adds none. The current graph status becomes parked, with no claim of empirical failure.
