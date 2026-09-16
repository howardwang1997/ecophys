# Paper G Cycle35: lineage-resolved response and ecological interventions

PRIVATE / INTERNAL. 2026-09-13 NZ. Four source-informed F0/F1 questions under the PI's cross-domain scientific-ML scope for ICLR/ICML main.

**Retain one provisional measurement question:** does good population-distribution prediction conceal consequential errors in clone-conditional endpoint predictions under different treatments, after accounting for recovery and growth-related selection? Three generic ecological formulations close at quick screen. No full F2, F3, forecast, machine card or scientific execution occurred. These are candidate decisions, not observed model findings.

The cycle start preceded new-domain primary search. Individual questions were composed during reading, not retrospectively labelled prospective hypotheses. Seven primary works and two repository/release metadata records were retained. The primary cap is ten, with three slots remaining for a bounded follow-up. Sampling comprises two measurement and two empirical-intervention questions; no advancement quota was used.

## Four questions and decisions

| ID / archetype | Native question and rival explanations | Discriminating result; positive/null value | F1 disposition |
|---|---|---|---|
| g35_clone_conditional_response / measurement | In a barcoded cell population split across treatments, do marginally accurate response models correctly predict recoverable clones' endpoint state distributions? H1: conditional errors materially alter model choice. H0: remaining discordance is explained by capture, growth, sparse labels and ordinary conditional baselines. | Compare models at matched marginal accuracy on withheld clone-labelled outcomes, with frozen recovery rules and clone-level uncertainty. Positive: useful validation criterion for state-transition predictions. Null: delimit when marginal evaluation suffices within the observed regime. | Retain candidate; exact contribution and observation contract unqualified. |
| g35_ecological_source_fraction / measurement | Can a learned composition-only estimator recover initial donor fractions after unknown differential growth? H1: endpoint composition retains sufficient source information. H0: growth and mixture weights are confounded. | Same endpoint under different fractions/growth laws rules out generic recovery; known-growth controls restore a narrower inverse problem. Positive: identify required auxiliary measurements. Null: rule out unsupported source fractions. | Close the endpoint-only generic formulation: exact ambiguity and direct parent. |
| g35_dropout_higher_order / empirical | Does incomplete latecomer rescue after firstcomer dropout identify irreducible higher-order interactions? H1: pairwise models cannot explain residual suppression. H0: pairwise interactions with other resident strains suffice. | A pairwise cascade reproducing incomplete or reversed rescue defeats the proposed identification. Positive: a fully controlled residual could motivate higher-order modeling. Null: avoid unnecessary model complexity. | Close dropout-as-sufficient-identification; do not close predictive community modeling. |
| g35_host_history_response / empirical | Does colonization history add predictive information for host response beyond endpoint taxonomic composition and host genotype? H1: history-dependent host state matters. H0: measured endpoint composition suffices. | Controlled colonization order and host outcomes can test this fork; statistical adjustment alone does not hold all biological mediators fixed. Positive: motivate a history-aware predictor. Null: support simpler current-state predictors in a specified regime. | Close generic history-effect headline against direct experimental prior; no distinct ML result specified. |

## Retained primary neighborhood

1. [Bunne et al., CellOT, Nature Methods 2023](https://doi.org/10.1038/s41592-023-01969-x) learns perturbation maps from unpaired cell populations and evaluates multiple biological settings. Marginal accuracy versus clone-conditioned validity is a measurement question; this screen does not claim its published results are invalid or that no lineage-related evaluation exists.
2. [Schaff et al., Cell Genomics 2026](https://pubmed.ncbi.nlm.nih.gov/41916275/), [indexed author full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC13261651/), links pretreatment clone states with endpoints across six parallel treatments. Its Fig. 5 analysis already regresses initial expression programs onto endpoint programs in selected large resistant clones. Generic clone-state prediction and multi-treatment resistance are therefore established, not our novelty. The paper names GEO GSE279162 and a code archive; selected methods and resource passages were read. This is not individual-cell tracking or a randomized sequential-treatment experiment.
3. [Bonham-Carter and Schiebinger, Bioinformatics 2024](https://doi.org/10.1093/bioinformatics/btae483), [author full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11316616/), identifies growth-dependent bias in clones sampled at multiple times and examines consequences for lineage inference. Generic proliferation-bias correction is a direct parent. Its setting supplies a warning and comparator, not automatic calibration for the melanoma experiment.
4. [Wang et al., iMeta 2023](https://pubmed.ncbi.nlm.nih.gov/38868341/), DOI 10.1002/imt2.75, analyzes ecological dynamics as an obstruction to community source tracking, including experimental mixtures. The generic source-tracking concern is directly occupied. The publication year is 2023; indexing time is not the publication date.
5. [Priority effects in honeybee gut strains, 2026](https://pubmed.ncbi.nlm.nih.gov/41841794/), [selected author passages](https://pmc.ncbi.nlm.nih.gov/articles/PMC13099264/), uses sequential communities and conspecific firstcomer dropout. Partial rescue motivates contributions from both within- and between-species interactions. The authors' statement is not a claim of irreducible higher-order terms; that stronger proposed inference is what our control rejects.
6. [Blonder, Lim and Godoy, LOVE, Ecology Letters 2024](https://onlinelibrary.wiley.com/doi/full/10.1111/ele.14535), [author PDF](https://benjaminblonder.org/papers/2024_ELE_LOVE.pdf), predicts and prioritizes assembly actions from state/environment information. Generic ML prediction or action prioritization is already a baseline. Only indexed selected text was used, not a full methods audit or a claim that the exact bee intervention has been evaluated by LOVE.
7. [Leopold and Busby, Current Biology 2020](https://pubmed.ncbi.nlm.nih.gov/32679100/) varies colonization order and host genotype in a foliar-fungus experiment and reports consequences for host response beyond measured community composition. The generic history-sensitive biological claim is already present. It does not identify every possible unmeasured mediator or establish our hypothetical held-out ML result.

Each F1 question uses at most three anchor works. CoSpar, PRESCIENT, other cell-model hits and other ecology hits were intake leads, not expanded retained works in this cycle. Search silence does not establish novelty. No opposite headlines from different treatments were treated as a matched model disagreement.

## Six elementary controls

### 1. Identical marginals, opposite clone couplings

Let two equally represented pretreatment clones lead to endpoint states A and B. The joint tables

\[
J_1=\tfrac12\begin{pmatrix}1&0\\0&1\end{pmatrix},\qquad
J_2=\tfrac12\begin{pmatrix}0&1\\1&0\end{pmatrix}
\]

have identical row and column marginals. Any endpoint-distribution-only score ties them, while their clone-conditional predictions disagree completely. This establishes the need for independent conditional information when that is the target. It does not establish that actual models make such errors, or that a clone label identifies the fate of a particular destroyed cell.

### 2. Weighting alone can reverse a ranking

Suppose two clones have observed endpoint weights (0.9,0.1). A model with per-clone losses (0,1) has cell-weighted loss 0.1, better than a model with losses (0.2,0.2), whose loss is 0.2. Equal-clone weighting reverses the ranking to 0.5 versus 0.2. This is a change of estimand, not evidence of a new biological failure. A useful conditional audit must separate this bookkeeping effect from erroneous conditional predictions.

### 3. Recovery is not survival

Under independent Bernoulli capture at two times, a clone with N0 and NT cells is observed at both with probability

\[
[1-(1-p_0)^{N_0}][1-(1-p_T)^{N_T}].
\]

Thus growth and sample recovery alter the observed clone population. Zero recovered endpoint cells can occur with NT>0. Clone-level reweighting alone does not recover dead or unseen populations without a calibrated observation model and adequate support. This elementary control follows the statistical issue already addressed in the proliferation-bias parent; it is not a new theorem.

### 4. Source fraction and growth are confounded

For two source-specific taxa, an initial fraction alpha and growth rates r1,r2 produce

\[
\operatorname{logit}p_T=\operatorname{logit}\alpha+(r_1-r_2)T.
\]

For any endpoint fraction in (0,1), multiple initial fractions and growth differences give the same observation. Known rates remove this ambiguity in the toy; a generic learned estimator without such information cannot. Endpoint similarity and accurate forward prediction are not source-fraction identification.

### 5. Partial dropout rescue needs no higher-order term

Consider a resident X held at x, another resident with dynamics dz/dt=z(s-z-cx), and a latecomer with dy/dt=y(r-y-ax-bz). These per-capita laws contain only pairwise interactions. In the positive equilibrium regime,

\[
z^*=s-cx,\qquad y^*=r-bs+(bc-a)x.
\]

Changing x from 1 to 0 changes y* by a-bc. With s=2, r=4, b=c=1, all relevant equilibria remain positive. Choosing a=1.5 yields an increase of 0.5; choosing a=0.5 yields a decrease of 0.5, even though direct X-to-Y competition remains suppressive in both cases. Residual competition from Z can prevent complete rescue. This is a conditional ecological toy with X controlled, not a fit to the bee data; it refutes dropout magnitude/sign as sufficient identification of irreducible higher-order interactions.

### 6. Equal current composition need not mean equal host state

Let a host mediator satisfy dH/dt=k X(t)-lambda H and let the response depend on H(T). Different exposure histories with identical X(T) can yield different H(T). A composition-only state projection omits this mediator. This does not identify which mediator operated in an experiment, nor prove that history features improve a real learned model. It prevents relabelling an elementary hidden-state effect as a new physical mechanism.

## What the surviving candidate can actually claim at this stage

X is the pretreatment clone-associated expression distribution in one declared experimental population. A is a specified parallel treatment arm. Y is the observed endpoint state distribution conditional on a recoverable clone and a frozen capture/eligibility rule. H1 versus H0 concerns the incremental value of conditional validation for model selection after marginal accuracy, weighting and recovery controls. T consists of the analytic coupling twins and a plausible released clone/state measurement path, still requiring source-level joins and calibration.

A positive result would need robust changes in model-selection conclusions or conditional predictive performance on outcomes not used to tune the score. A null would delimit the incremental value in the qualified population; neither would establish clinical efficacy or general drug-resistance prediction. A different claim about survival requires its own validated denominator and detection model.

A suitable comparison must include simple pretreatment-to-endpoint program regression, clone-independent treated-distribution prediction, and existing lineage-informed approaches where allowed information matches. Barcode identities are evaluation links, not predictive features. Hold clone families together across splits; prevent endpoint-derived labels, feature selection or outcome-ranked clone filtering from selecting the confirmation claim. Independently replicated cultures are distinct from many cells in one culture. Treatment-held-out transfer and clone-held-out interpolation are different claims; CellOT's per-treatment parameterization cannot simply be called a zero-shot drug predictor.

The [code release metadata](https://zenodo.org/records/13935305) identifies an October 2024 first-release archive, linked to a [versioned repository tree](https://github.com/dylanschaff/Schaff_manuscript/tree/first_release). The tree lists expression, barcode and endpoint-analysis scripts. No archive, notebook outputs, sequencing payload or model weights were opened. File-level barcode joins, capture thresholds, independent replication, release rights and correspondence between this early code release and the final paper remain unqualified. The paper's GEO accession is a source-declared lead; its record contents were not verified here.

## Portfolio decision and next decisive update

The three ecological formulations have exact/direct-parent reasons to stop. The clone question survives only F1 because it has an independent conditional observation concept and an explicit candidate resource. It is distinct from the closed generic perturbation-score correction and post-treatment-proxy-as-assigned-dose formulations in Cycle32. It does not reopen either, and broad parent vocabulary does not itself veto this different target.

Next: use at most the three remaining primary slots to check the exact measurement neighborhood and inspect source/metadata joins, without executing author code or opening outcomes. Stop if the contribution reduces to existing lineage benchmarks or if the resource cannot support a calibrated independent comparison; do not repeatedly relabel a generic correction. Before any F3, freeze the exact subject and prospective full-T0 forecast.

The isotope, chemistry and quantum candidates remain parked. Paper G now has 73 formulations across 19 cycles, with zero machine cards. The broad ICLR/ICML objective remains active and incomplete. This cycle made epistemic progress through distinct target qualification and explicit exclusions; administrative validation cannot establish novelty or empirical success.
