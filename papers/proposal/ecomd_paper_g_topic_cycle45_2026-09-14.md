# Paper G Cycle45: mutation-level kinetic selectivity

PRIVATE / INTERNAL — 2026-09-14. One provisional F1 empirical-intervention question; no execution authority or publication-ready result.

Question: do representations trained on equilibrium affinity retain information that predicts mutation-induced changes in binding speed when affinity changes are small, beyond parent identity and affinity-correlated effects?

The native intervention is a registered sequence substitution relative to a parent, with the binding partner, construct, assay conditions and observation model held explicit. The response is the pair a=log(kon_mut/kon_parent), b=log(koff_mut/koff_parent). Under one consistent 1:1 model, the affinity change is d=b-a. The target is protocol-conditioned mutation kinetics, not therapeutic efficacy or an inferred microscopic transition mechanism.

H1 predicts that affinity-pretrained representations retain useful information about common rate shifts a approximately b within a parent lineage. H0 predicts that their apparent kinetic performance is explained by affinity and between-parent variation, with existing mutation predictors or ordinary representations sufficient for the remaining task. These are testable predictive explanations, not claims that a particular molecular pathway has been identified.

Positive value: determine when equilibrium training supports kinetic-selective screening. Null value: delimit that transfer and distinguish mutation-level ability from pooled correlation. Neither outcome automatically meets the ICLR/ICML bar; a distinct scientific conclusion beyond ordinary stratified evaluation remains to be established.

Existing work and plausible truth

| Source | Scope of selected reading |
| --- | --- |
| [AbAgKer, 2026](https://doi.org/10.1093/bioinformatics/btag606) | Affinity-trained frozen representations feed a kinetic MLP; its kinetic subset contains 272 pairs. Selected methods and discussion provide the direct transfer comparator. A full code/split audit has not been performed. |
| [Agius et al., 2013](https://doi.org/10.1371/journal.pcbi.1003216) | Molecular and hotspot descriptors already predict mutation-induced off-rate changes. Selected abstract/introduction/approach establishes a mandatory comparator and rules out first-mutant-kinetics claims. |
| [AIntibody, 2026](https://doi.org/10.1038/s41587-026-03238-6) | Selected assay and availability sections document sequence-to-result mapping, parent controls and SPR kinetic parameters. There is a fitted off-rate floor; independent equilibrium measurements cover selected subsets. Published cluster-level kinetic comparisons are already part of the parent work. |
| [MAXTIA, 2026](https://doi.org/10.1002/pro.70769) | Additional assay documentation describes an antigen alanine panel and a supplementary kinetic table. Nonbinding placeholders are not measured kinetic rates. This is not independent replication of antibody-design behavior. |

The first three works are the F1 anchors; MAXTIA was inspected during source intake for assay scope. Four works total, below the six-work intake cap. No supplementary outcome files, model weights or source implementation were accessed. These sources establish plausible measurement paths, not a complete matched-reference contract.

Two standard controls

1. Scale both kon and koff by c>0 in a two-state 1:1 system. KD is unchanged, but the relaxation rate at fixed concentration C, kon*C+koff, scales by c. Thus a=b=log(c), d=0 is an independent kinetic direction. This identity does not prove that a particular sequence mutation realizes it or that a model can predict it.
2. Let the true log-rate be y_gm=mu_g+epsilon_gm for parent g and mutant m, with independent centered parent and mutation terms. A predictor that outputs only mu_g has pooled correlation sqrt(Var(mu)/(Var(mu)+Var(epsilon))). It can approach one while predicting zero mutation changes after within-parent centering. This illustrates a possible null; it is not an empirical diagnosis of AbAgKer or any other published model.

Evaluation that would discriminate

Freeze parent/family and mutation holdouts before any payload access. Give all deployable methods the same sequence/structure information, available parent kinetic reference and training-label budget. Compare frozen affinity-pretrained representations with raw PLM features, fine-tuning, a joint rate regressor and the direct hotspot/molecular baseline. Use mutation rate-change errors and sign/ranking performance as primary readouts; pooled absolute correlation is secondary.

Near-isoaffinity analysis requires a prespecified uncertainty-aware tolerance and an independent selection measurement or a justified joint error model. KD computed from the same fitted kon and koff is algebraically coupled to both target errors, so simply filtering that ratio and treating it as exact is inadequate. An oracle-affinity diagnostic can ask what affinity alone explains, but is separate from sequence-only deployment evaluation. Never supply test mutant kinetic labels to a deployment predictor.

Assay uncertainty, censoring, valency, mass transport, construct folding and measurement windows remain explicit. Technical replicates do not create new mutants or independent studies. The already published prospective challenge cannot confer prospective status on our new post-hoc analysis. A separate untouched confirmation partition is still needed for a confirmation claim.

Decision and next gate

Retain one provisional F1 candidate. The scientific contribution is unresolved, particularly against prior mutation-rate prediction and existing antibody benchmarks. No new architecture, residual score or two-head identity is claimed as an invention. This differs from the closed generic latent-phenotype/readout route and does not reopen conditional-calibration transfer or learned-MC families.

Next conduct a bounded, outcome-blind contribution/support review of existing mutation-rate evaluations and source metadata/code interfaces. Establish whether independent affinity selection and kinetic evaluation, sufficient within-parent variation, and defensible lineage splits are possible. Park the route if only ordinary residual reporting remains, or if valid matched kinetic support is inadequate. No full fifteen-work review or forecast is authorized by this F1 record.

This source-led cycle has one raw question and one quick screen; diversity targets are unmet, not waived for a future twelve-program cycle. Counts: Paper G89 formulations/29 cycles/0 cards; detailed36 cycles/173 raw; inclusive45 cycles/229 raw; graph333 nodes/279 edges/1972 locators; evidence1243; candidate1/parked13. No F2/F3, forecast, outcome payload, scientific code, simulation, training, hardware, outreach, delegation or publication. Administrative validation is documented separately.
