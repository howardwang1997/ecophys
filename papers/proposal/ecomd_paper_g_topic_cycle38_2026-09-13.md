# Paper G Cycle 38: learned cage-assisted sampling in a binary glass

PRIVATE / INTERNAL — exploratory topic screen, not a manuscript or an empirical result. Started 2026-09-13; completed after resumption on 2026-09-14 NZ. The filename retains the immutable start record's reference.

Decision: retain **one F1 candidate**, `g38_ka_cage_assisted_swap`, with novelty and feasibility unresolved. No F2, F3, forecast, machine card or scientific execution. The scientific question concerns equilibrium sampling in the original binary Kob–Andersen (KA) mixture; it does not concern physical-time glass kinetics.

## Native question and competing explanations

At fixed KA interaction parameters, composition, density, temperature and target ensemble, does a learned proposal that rearranges a bounded surrounding cage along with a proposed A/B exchange improve **label-invariant structural decorrelation per total computational cost** beyond current sampling baselines?

- H1: useful exchange pathways require cooperative but spatially bounded cage motion. A conditional collective proposal can learn those pathways economically; the benefit persists after exact acceptance correction and current training/inference costs.
- H0: bounded proposals mainly relabel particles, remain trapped in the same physical structures, or require sufficiently extensive/expensive relaxation that their apparent advantage disappears against matched baselines. Restricted-cage free-energy differences can also persist after perfect coordinate relaxation.

These explanations can hold in different regimes. They are proposed alternatives, not a claim that two published papers give contradictory predictions. The discriminator is a matched comparison of pair-only, surrounding-cage and existing enhanced moves, with declared block support, common equilibrium observables and total cost. A positive answer would identify a useful spatial scope for learned moves. A null answer would delimit when local learned proposals are insufficient and when extended/expanded-ensemble moves are preferable. A null at one architecture or temperature cannot refute all collective sampling.

Archetype: `simulator_method`. Source lane: `market_native_action_or_constraint`, interpreted in the actual scientific domain under the PI's cross-domain authorization. Algorithmic interventions are not physical empirical interventions.

## Three F1 anchors and occupied claims

1. **Galliano, Rende and Coslovich, PGMC (2024).** Their soft swap displaces the two exchanged particles before acceptance. In binary KA, biased and soft swaps provide little improvement; biased displacement is a necessary baseline. They already evaluate structural relaxation and move costs, and explicitly discuss learned collective proposals as future work. Thus neither cost-aware evaluation nor “use a neural collective move” is our innovation. [Primary paper, III.4–III.6 and IV](https://arxiv.org/html/2407.03275v2).
2. **Monroe and Shen (2022).** VAE-based collective proposals with an exact acceptance construction are an existing parent; correlated dense-fluid generation motivates autoregressive decoding. Exact learned equilibrium sampling is occupied territory. Selected abstract/introduction/theory were read; a complete collision map remains pending. [Author PDF](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=932532).
3. **Turci, Royall and Speck (2017), Appendix A.** A staged capped interaction for one ghost particle is interleaved with local MC moves; uncapped configurations are recorded. The stated purpose is local cage-barrier reduction. This is a direct environmental-relaxation baseline, not evidence that pair-plus-cage proposals are unprecedented. Its described algorithm must not be rewritten as an explicit two-particle swap kernel. The separate trajectory-biased method is not automatically a same-estimand equilibrium comparator. [Author PDF, Appendix A](https://francescoturci.wordpress.com/wp-content/uploads/2013/10/physrevx-7-031028.pdf).

## Three hand-derived controls

These are standard analytic controls, not new theorems and not observations of KA trajectories.

**C1: conditional refresh does not remove all restricted free-energy odds.** Let `b` be frozen outside coordinates, `u` the proposed coordinates and `s` their species assignment. On a declared, state-independent domain `D`, define

\[
Z_s(b)=\int_D e^{-\beta U_s(u,b)}du,\qquad
q_s(u\mid b)=e^{-\beta U_s(u,b)}/Z_s(b).
\]

For an exact conditional refresh after selecting `s → s′`, the MH acceptance is

\[
\alpha=\min\{1,[Z_{s'}(b)/Z_s(b)]\,[p_{\rm reverse}/p_{\rm forward}]\}.
\]

This follows by cancelling the coordinate Boltzmann factors. It describes this conditional-refresh subfamily, not an upper bound over every correlated transport kernel. An exact conditional is an oracle here; its availability and cost have not been established.

**C2: unit acceptance can mean zero physical progress.** If `D` is invariant under permuting the two exchanged coordinate labels and contains both particles, then `Z_s′(b)=Z_s(b)` by that coordinate permutation. This holds even for a finite block with frozen outside coordinates. A symmetric involution exchanging both the species labels and their coordinates has acceptance one while every species-density field

\[
\rho_a(r)=\sum_i\mathbf1[s_i=a]\delta(r-r_i)
\]

is unchanged. It produces no decorrelation of physical configurations. Particle-index displacement can nevertheless change. Therefore neither high acceptance nor an identity-sensitive displacement score alone can certify useful sampling for this enlarged move class. This is not a criticism of PGMC's reported experiments. Require species-resolved collective correlations, structural overlap or equilibrium observable autocorrelation in addition to any conventional self-scattering diagnostic.

**C3: relaxation and free-energy offset are distinct.** For a restricted-site toy `U_s(u)=k(u-a_s)^2/2+c_s`, `k>0`, integration over the real line gives `Z_s=√(2π/(βk)) exp(-βc_s)`. Different centers with equal offsets can incur a large frozen-coordinate exchange penalty, yet exact conditional refresh accepts with probability one for symmetric selection. An uphill offset `c_s′−c_s=Δ>0` instead leaves acceptance `exp(-βΔ)`. These are two limits of one toy, not two KA results. Applying the offset interpretation to particle cages requires explicit site restrictions or another non-permutation-invariant support; unrestricted coordinate labels fall under C2.

## Minimal truth and contribution boundary

A putative sampler needs evaluable forward/reverse probabilities and a full-target acceptance correction. A geometric neighborhood selected from the starting coordinates can change under reversal: either use fixed auxiliary block choices with proved reverse support, or retain the complete selection factors. A fixed set of particle indices alone does not confine their proposed positions to a spatial cage. Restricted domains must remain proposals within the declared global target, not silently change that target. Combine with an irreducible base kernel and freeze trained policies for production; stationarity alone is not a finite-run convergence certificate.

The cheap analytic controls supply correctness tests, not low-temperature equilibrium truth. Before execution, require a same-target reference in a tractable regime, independent starts and convergence diagnostics, and explicit handling of amorphous metastability versus true equilibrium. No inaccessible low-temperature target can be declared equilibrated solely because a move accepts or energy falls.

The comparison must include biased displacement, PGMC pair/soft swaps, staged ghost relaxation, and relevant learned collective samplers. Match actual training, tuning, energy/force evaluations, sampling and acceptance-correction cost. Report first-use and amortized costs with an explicit reuse count. Cavity radius is an algorithm parameter; no monotone speedup or thermodynamic length interpretation follows automatically.

The possible contribution is a demonstrated bounded cooperative mechanism with a useful cost frontier, not a generic flow-plus-MH recipe. Existing data access would not establish it. For ICLR/ICML main, transfer across declared conditions and a substantive learning result remain unresolved; no publication probability is assigned.

## Intake accounting and public metadata

Eight distinct primary works consumed the frozen cap, at unequal reading depth: the three anchors above, plus five context/intake records below. This is **not eight full reviews** or a completed F2 screen.

| Context work | Read scope and disposition |
| --- | --- |
| [Parmar et al., stable KA configurations (2020)](https://arxiv.org/abs/2006.10377) | Abstract/selected introductory material. Added-species routes require separate reweighting/annealing contracts; priority for follow-up. |
| [Ghimenti et al., irreversible hard-disk sampling (2024)](https://arxiv.org/abs/2402.06585) | Abstract. Two-dimensional polydisperse hard disks; no same-KA disagreement inferred. |
| [Berthier et al., beyond Metropolis (2024)](https://arxiv.org/abs/2406.19704) | Abstract. Three-dimensional polydisperse hard spheres; context, not a KA result. |
| [Scalable flow mitigation of topological freezing (2026)](https://arxiv.org/abs/2601.20708) | Selected methods/conclusion. Gauge-sampling intake; no raw question formed. Underlying longer study not separately reviewed or counted. |
| [Jung et al., flows for supercooled liquids (2024)](https://arxiv.org/abs/2404.09914) | Search/abstract intake only; exact model and comparison contract remain a follow-up priority. |

The [PGMC Zenodo metadata](https://zenodo.org/records/11396665) describes a figure-reproduction workflow and processed simulation products, with CC BY 4.0 metadata and a 281,442,770-byte archive. Metadata explicitly distinguishes that workflow from the complete PGMC code needed for its Figure 3. No archive or outcome payload was accessed, and complete runnable baseline availability is unqualified. This is capability documentation, not scientific support for a speedup.

Only one raw question was formed and quick-screened. The scoped algorithmic intake did not supply qualifying physical interventions; manufacturing generic measurement questions would repeat the saturated calibration template. Record this bounded source/allocation exception to the archetype sampling targets; it is not a claim of scarcity across science. No quota filler, terminal sibling or new re-entry authorization is created.

## Record and next decisive update

The graph duplicate check found no existing KA cage formulation. Preserve every old node, edge, cycle, forecast and re-entry entry. Counts after this screen: Paper G **82 formulations / 22 cycles / 0 cards**; detailed ledger **29 cycles / 166 questions**; inclusive history **38 cycles / 222 questions**. Candidate status authorizes no experiments.

Next bounded step: read the already-identified Jung and Parmar methods for the exact target and proposal support, then determine whether a cage-conditioned kernel has a concrete distinction from existing collective/expanded-ensemble constructions. Stop or park if only the published suggestion “learn larger collective moves” remains. Do not collect another broad neighborhood merely to postpone that decision.
