# Paper G: clone-conditional response contribution review

PRIVATE / INTERNAL — exploratory analysis and allocation decision; excluded from public builds.
2026-09-13 NZ. Route: `g35_clone_conditional_response`.

## Decision and scope

Park this candidate nonterminally. Its narrower empirical question remains open: does clone-conditional endpoint validation improve model selection for unseen treatment/culture settings beyond matched marginal and growth-aware baselines? The review establishes neither an empirical failure nor a publishable new method. Generic lineage validation and growth correction already have direct parents; a distinct economical comparison and independently qualified observation contract remain missing. Do not expand this generic citation chain or begin experiments.

This is a follow-up to Cycle35, not another search cycle. The frozen allocation allowed three additional primary works, bringing the original cycle from seven to its cap of ten. The exact candidate neighborhood contains six works: CellOT, Schaff et al., the proliferation-bias study, CoSpar, PRESCIENT and moslin. This is a targeted contribution screen, not a completed full F2 truth contract or an F3 audit. No forecast, machine card or scientific execution is issued.

## Direct contribution collisions

| Primary work | Relevant existing contribution | Boundary for this candidate |
|---|---|---|
| [PRESCIENT (2021)](https://www.nature.com/articles/s41467-021-23518-w), selected Results and Fig. 2 | Evaluates both held-out marginal distributions and clonal fate bias. Compares proliferation-aware and unweighted models, including lineage-derived and expression-derived growth estimates. | Neither the marginal/clone distinction nor adding growth correction is new. Its hematopoietic setting does not resolve drug-specific transfer in the proposed melanoma resource. Privileged lineage-derived growth must not be silently equated with expression-only inputs. |
| [CoSpar (2022)](https://www.shouwenwang-lab.com/pdfs/cospar.pdf), selected benchmark sections and Figs. 4–5 | Combines expression and lineage information; compares state-only and endpoint-clone inputs against clonal fate references, including sparse lineage settings. | Sparse clone information and lineage-assisted fate validation are occupied. Holding clone labels out for evaluation is a protocol distinction to qualify, not by itself a new method. |
| [moslin (2024)](https://link.springer.com/article/10.1186/s13059-024-03422-4), selected Results/methods | Combines expression and lineage distances using fused Gromov–Wasserstein transport, with growth/death handling. In synthetic evaluation it withholds cross-time ancestry while using within-time lineage for inference. | Independent ancestry scoring is an existing strategy. Static clone labels are weaker than resolved lineage trees; moslin is not automatically a comparator with equal information in this resource. |

The earlier three parents and their read-scope limitations remain in the [Cycle35 report](ecomd_paper_g_topic_cycle35_2026-09-13.md). No claim is made to have reproduced any published numerical result or exhaustively audited every method.

## What the public author source establishes

Four files from the `first_release` author repository were read without execution or opening data/output objects. Hashes and precise read scopes are recorded in the structured record.

- [Workflow README](https://raw.githubusercontent.com/dylanschaff/Schaff_manuscript/first_release/How_to_run_code_README.txt) declares gene-expression preprocessing before cDNA and gDNA barcode preprocessing.
- [Gene-expression source](https://raw.githubusercontent.com/dylanschaff/Schaff_manuscript/first_release/preprocess_GEX.Rmd) constructs RNA and custom lineage assays from corresponding 10X inputs. Merging prefixes cell IDs with condition/sample names. `OG_condition` comes from those prefixes and pools `naive1`, `naive2`, `naive3` into `naive`. These names alone do not establish independent biological replicates.
- [cDNA barcode source](https://raw.githubusercontent.com/dylanschaff/Schaff_manuscript/first_release/preprocess_cDNA_BCs.Rmd) clusters correlated barcodes, assigns a best lineage using a posterior margin of at least 0.2, and filters assignments below a maximum posterior of 0.5. Default clustering settings include a cell lower limit of 100 and correlation threshold 0.55. Thresholds specify the observation procedure; they do not establish empirical assignment calibration or state-independent recovery.
- [Endpoint source](https://raw.githubusercontent.com/dylanschaff/Schaff_manuscript/first_release/Endstate_clonal_differences.Rmd) loads the lineage-annotated object, groups by `OG_condition`, and joins lineage counts across conditions. Its selected differential-expression section analyzes top-ranked clones. This inspection does not qualify the complete final-paper Figure 5 prediction pipeline or establish correspondence between every release file and the final publication.

Thus a source-level cell/condition/assigned-clone path is present. Actual release joins, independent culture identities, state-dependent capture, assignment accuracy, relevant growth denominators, reuse rights and untouched confirmation partitions remain unqualified. No absence in this bounded inspection is asserted to prove absence from all author resources. gDNA replicate arms cannot simply be counted as independent scRNA endpoint replicates.

## Observation operator and exact ambiguity

This is a hand-derived identification control, not a new theorem, simulation or observed biological finding. Assume correct clone labels and a baseline distribution `mu_c(dx)` within clone c. Let `g_a(x)` denote expected endpoint descendants per initial cell, `K_a(dy|x)` the normalized descendant-state kernel, and `r_a(c,y)` the endpoint recovery probability. Under this simplified factorization, the observed endpoint probability is proportional to

`nu_obs(a,c,dy) ∝ r_a(c,y) integral g_a(x) K_a(dy|x) mu_c(dx)`.

Baseline sampling may also distort `mu_c`. Misassignment would require an additional mixing operator; the expression above grants correct labels to expose an ambiguity that already exists in that easier case. Total clone growth `G = integral g_a(x) mu_c(dx)` supplies one moment, not the state-dependent function `g_a`.

With ideal capture, take baseline states A and B in equal proportions:

| Explanation | Descendant weights | State kernel | Endpoint proportions | Total expected growth |
|---|---|---|---|---|
| Selection only | g(A)=1.5, g(B)=0.5 | Identity | A=0.75, B=0.25 | 1 |
| State change only | g(A)=g(B)=1 | Both rows are (0.75, 0.25) | A=0.75, B=0.25 | 1 |

The same static clone identity, normalized endpoint law and total expected growth admit different mechanisms. This statement concerns endpoint mixtures/first moments, not equality of every possible branching or longitudinal count distribution. State-resolved proliferation or finer live ancestry can add identifying information. Unweighted averaging of a predicted per-cell state kernel generally misses the descendant-weighted target when growth varies within a clone.

The measurable endpoint target remains valid in principle: predict the distribution of recovered descendants conditional on a declared clone/sample protocol. It must not be described as identifying how each original cell changed, or as separating selection from transition. These stronger claims are unnecessary for testing predictive usefulness.

## Minimum distinct empirical fork if revisited

Rival explanations: (A) clone-conditional validation detects response errors that ordinary marginal validation misses and selects models that transfer better; (B) its apparent advantage is explained by clone weighting, growth/capture selection, noise or extra information and disappears in matched comparisons.

The discriminating quantity is selection regret on an independently held-out target among the same fixed models: target risk of the model chosen using marginal validation minus target risk of the model chosen using clone-conditional validation. A positive difference would support incremental selection value; a null would limit the expense and scope of this validation. The independent target must match the scientific claim: another qualified endpoint dataset supports predictive transfer, while mechanism claims need stronger truth.

Before allocation, qualify biological units and grouping, observation/calibration uncertainty, a fixed feature representation and scoring rule, treatment/culture transfer, source permissions, and a confirmation partition independent of tuning. Keep related clone samples together when claiming generalization to unseen clones. If using endpoint labels or lineage-derived growth during training, name that extra-information regime and compare like with like. Compare clone-conditional scoring to matched weighting/growth baselines and simple clone/program predictors, not merely to an uncorrected aggregate score. Resampling cells alone does not create independent cultures or treatments.

These are requirements for a future proposal, not an approved experiment or a preregistered outcome claim. Resume only on a contribution-changing primary result or a qualified economical truth/comparison asset, with a new bounded allocation and any required re-entry review. Next authorized work is an unsaturated cross-domain scientific-ML screen; do not relabel this generic lineage question to restart it.

## Record

Paper G remains 73 formulations / 19 cycles / 0 cards; detailed ledger 26 cycles / 157 raw questions, historical inclusive 35 / 213. This review adds three primary and four source records. Broad ICLR/ICML objective remains active and incomplete. Administrative registry checks are separate from scientific evidence.
